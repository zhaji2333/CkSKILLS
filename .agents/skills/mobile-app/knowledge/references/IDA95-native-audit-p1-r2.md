# IDA 9.5 无头模式 Native 安全审计手册 · part 1 · part 2

> 分段 2/2。索引见 `IDA95-native-audit-p1.md`。

alloca(n)                                          ← n 可控则栈破坏
```

**脚本：一次性扫出所有危险调用点**

```python
import ida_name, ida_xref, ida_funcs, ida_hexrays

DANGEROUS = ["strcpy", "strcat", "sprintf", "vsprintf", "gets", "memcpy",
             "memmove", "sscanf", "__isoc99_sscanf", "alloca", "strncpy"]

for fn in DANGEROUS:
    ea = ida_name.get_name_ea(0, fn)
    if ea == 0xFFFFFFFFFFFFFFFF:
        continue
    xb = ida_xref.xrefblk_t()
    ok = xb.first_to(ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f:
            print(f"{fn:20s} <- {hex(xb.frm)} {ida_funcs.get_func_name(f.start_ea)}")
        ok = xb.next_to()
```

**判定要点**：
- 长度参数是否来自 `JNIEnv->GetStringUTFChars` / `GetArrayLength` / `GetStringUTFLength`（= Java 侧可控）
- 若长度来自 Java 传入的 `jstring`，且**未做 `< sizeof(buf)` 校验** → 可触发
- 有 canary 时：能覆写**返回地址之外**的东西（如函数指针、堆上的回调结构）仍是漏洞
- **越界读**（`memcpy(dst, src, len)` 里 len 超读）→ 信息泄露，可配合绕过 ASLR → 中高危

### 3.2 堆溢出 / UAF / 双重释放

**找什么**：堆分配 + 越界写 + 释放后使用。

**spot-list**：`malloc` / `calloc` / `realloc` / `free` / `new` / `delete` / `operator new[]`

**检查模式**：
- `malloc(len)` 后 `memcpy(buf, src, len2)` 且 **`len2 > len`**
- `realloc` 返回值未检查、原指针未更新 → UAF
- `free(p)` 后继续 `p->field` 使用 → UAF
- 异常路径下重复 `free` → double free
- C++ 容器（`std::vector` / `std::string`）的 `resize` / `reserve` 与实际写入不一致

**脚本：枚举内存操作调用链**

```python
import ida_name, ida_xref, ida_funcs

for fn in ["malloc", "calloc", "realloc", "free", "_Znwm", "_Znam", "_ZdlPv"]:
    ea = ida_name.get_name_ea(0, fn)
    if ea == 0xFFFFFFFFFFFFFFFF:
        continue
    xb = ida_xref.xrefblk_t(); ok = xb.first_to(ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f: print(f"{fn:12s} <- {ida_funcs.get_func_name(f.start_ea)}")
        ok = xb.next_to()
```

**判定**：能在**同一函数内**同时看到分配、越界写、可控长度 → 优先深读该函数。

### 3.3 整数溢出 → 短分配长拷贝

Android native 里最经典的**真实可利用**形态：

```c
// 危险模式：len 相乘/相加溢出后变成小值
int total = width * height;          // width/height 来自 Java，可溢出为小值或负数
char *buf = malloc(total);           // 分配过小
memcpy(buf, src, width * height * 4); // 拷贝时又按未截断的算式 → 堆溢出
```

**检查**：`malloc` 参数是否与后续 `memcpy` 长度**算式不一致**；是否缺少 `if (a > INT_MAX / b)` 类校验。
**符号性**：`size_t` 与 `int` 混用、负数长度传给 `malloc` → 转成巨大 `size_t`。

### 3.4 格式化字符串

**找什么**：`printf` 家族的第一个参数可控（不是字面量）。

```
printf  fprintf  sprintf  snprintf  vprintf  __android_log_print
syslog  vsnprintf
```

**关键判据**：格式串来自 `GetStringUTFChars` 或拼接结果，而非硬编码常量。

```python
import ida_hexrays, ida_funcs

# 反编译后人工确认：格式串是字面量还是变量
# 伪 C 里形如 printf(v12) 而非 printf("fmt", v12) → 命中
```

**危害**：`%n` 任意写（可劫持控制流）+ `%s`/`%p` 泄露内存（绕过 ASLR、泄露密钥、泄露沙箱外内存）。
`__android_log_print` 是 Android 上最常见的命中点（日志函数被滥用）。

### 3.5 命令注入 / 危险执行

**这是 RCE 最直接的路径**，优先级最高。

**spot-list**：`system` / `popen` / `execve` / `execl` / `execlp` / `execvp` / `fork`+`exec`
以及 Android 的 `__system_property_set` / `property_set`（可改 `persist.*` 造成持久化）

**检查**：
- 命令字符串是否拼接了 Java 传入的字符串（绕过 Java 层 `Runtime.exec` 的审计）
- 是否调用 `setuid` / `setgid` / `setresuid` 后仍执行外部命令（提权链）
- `system()` 内部走 `/bin/sh -c` → `;` `|` `&&` `` ` `` `$()` 全部可注入

```python
import ida_name, ida_xref, ida_funcs
for fn in ["system", "popen", "execve", "execl", "execlp", "execvp",
           "__system_property_set", "property_set"]:
    ea = ida_name.get_name_ea(0, fn)
    if ea == 0xFFFFFFFFFFFFFFFF: continue
    xb = ida_xref.xrefblk_t(); ok = xb.first_to(ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f: print(f"{fn:22s} <- {ida_funcs.get_func_name(f.start_ea)}")
        ok = xb.next_to()
```

**判定**：命令串可外部控制 → **严重**（RCE）；命令串来自本地配置/常量 → 不报。

### 3.6 提权（Privilege Escalation）

Native 提权的三个方向：

**(a) so 本身运行在特权进程**
系统 App（`system_app` / `platform_app` / `priv_app`）加载的 so 跑在 UID 1000 或 system_server。
此时 so 里的任意代码执行 = **系统权限**。

```bash
# 确认目标 App 的 SELinux domain 与 UID
adb shell ps -Z | grep <package>
adb shell dumpsys package <package> | grep -E "userId|sharedUser"
```

**(b) Binder 服务 / 系统能力暴露**
so 里若实现或调用了 Binder 接口，检查是否有 `checkCallingPermission` / `checkCallingUid` 校验：

```python
# 搜 Binder 相关符号
import ida_name
for i in range(ida_name.get_nlist_size()):
    nm = ida_name.get_nlist_name(i) or ""
    if any(k in nm for k in ("Binder", "binder", "IPCThreadState", "Parcel",
                             "checkCalling", "getCallingUid", "permission")):
        print(hex(ida_name.get_nlist_ea(i)), nm)
