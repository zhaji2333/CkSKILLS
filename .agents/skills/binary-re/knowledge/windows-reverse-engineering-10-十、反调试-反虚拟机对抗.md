# 十、反调试 / 反虚拟机对抗

> 来源：CkSKILLS v1 `windows-reverse-engineering` §十、反调试 / 反虚拟机对抗（迁移至 v2 知识块）

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
