# 二、工具链

> 来源：CkSKILLS v1 `windows-reverse-engineering` §二、工具链（迁移至 v2 知识块）

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
