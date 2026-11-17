---
name: internal-network
description: 内网/域渗透专项。当目标处于域环境（systeminfo 显示 Domain 非 WORKGROUP、88/389/636/445 开放）、拿到边界立足点需要内网侦察、持有凭据/哈希/票据需要横向移动、需要搭隧道跨网段、或做域内提权（Kerberos/委派/ACL/ADCS/NTLM 中继）时调用。
---

# internal-network — 内网/域渗透专项

## 何时调用

- `systeminfo` 显示 Domain ≠ WORKGROUP，或 88/389/636/445 在内网可达
- 已从 Web/RCE/云主机拿到立足点，需要内网侦察与横向
- 持有凭据（明文 / NTLM hash / 票据），要验证可复用范围
- 需要跨网段：DMZ→内网、多层防火墙后面、只能靠代理进出
- 域内提权：Kerberoasting / AS-REP / 委派 / ACL / ADCS / DCSync / NTLM 中继
- 内网基础设施：Exchange / SCCM / 国产 OA / 数据库 / 中间件 / CI 平台

## 30 秒分诊

1. **先判身份与环境**：`whoami /all`、`systeminfo`、`ipconfig /all`（DNS 是否指向域控）、`net user /domain` 是否可用
2. 无凭据 → 侦察面（`internal-01`）：存活、端口、SMB/LDAP 匿名、域控定位
3. 有域用户 → 枚举面（`internal-01`/`internal-02`）：BloodHound、SPN、ACL、委派
4. 有本地管理员 → 凭据提取 → hash/票据 → 横向（`internal-04`/`internal-05`）
5. 跨网段 → 隧道（`internal-06`）；已控制主机 → 后渗透（`internal-07`/`internal-08`）
6. 每条结论（含否定证据）写线索板，协议见 `rules/60`、`rules/66`

## 首枪顺序

- 域定位：`nltest /dclist:<domain>` / `nslookup -type=SRV _ldap._tcp.dc._msdcs.<domain>`
- 无凭据枚举：`netexec smb <cidr> -u '' -p '' --shares`、`enum4linux-ng -A <dc>`
- 有域用户：`bloodhound-python -u <user> -p <pass> -ns <dc> -c All`
- SPN 票据：`impacket-GetUserSPNs <domain>/<user>:<pass> -dc-ip <dc> -request`
- AS-REP：`impacket-GetNPUsers <domain>/ -dc-ip <dc> -no-pass -usersfile users.txt`
- 委派 / ACL / ADCS：`certipy`、`bloodyAD`、`ldeep`（见 `internal-03`）
- 横向：`impacket-psexec|wmiexec|smbexec`、`netexec -H`（见 `internal-05`）
- 隧道：`chisel` / `frp` / `ssh -D` + proxychains（见 `internal-06`）

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/internal-01-域侦察与决策树.md` | 域环境确认、枚举、攻击决策树 | 5.2KB |
| `knowledge/internal-02-Kerberos与票据攻击.md` | Kerberoasting / AS-REP / 票据滥用 | 7.6KB |
| `knowledge/internal-03-委派-ACL-ADCS.md` | 委派、ACL 滥用、ADCS ESC1–ESC11 | 7.5KB |
| `knowledge/internal-04-凭据-中继-投毒.md` | 凭据提取、NTLM 中继、协议投毒、喷洒 | 6.2KB |
| `knowledge/internal-05-横向移动.md` | PTH/PTT、WMI/PSExec/DCOM、跨库横向 | 5.5KB |
| `knowledge/internal-06-隧道与多层网络.md` | frp/chisel/SSH 多跳、SOCKS、端口转发 | 6.5KB |
| `knowledge/internal-07-后渗透与提权.md` | Linux/Windows 后渗透、本地提权 | 8.1KB |
| `knowledge/internal-08-持久化与痕迹.md` | 域/主机持久化、痕迹处理 | 8.7KB |
| `knowledge/internal-09-内网基础设施打法.md` | Exchange/SCCM/OA/数据库/中间件的默认弱点表 | 11.4KB |
| `knowledge/internal-10-工具投递与规避.md` | 往目标投工具、免杀与落地路径 | 8.8KB |

## 相关

- `ck-router` 的 `../ck-router/knowledge/战法索引-08-内网与域.md`（首枪表）
- `web-auth-access`（拿到初始凭据）、`cloud-infra`（云上内网/元数据）、`binary-re` / `mobile-app`（立足点获取）
