# IDA 9.5 无头模式 Native 安全审计手册 · part 2

> 分段 2/2。索引见 `IDA95-native-audit.md`。

## 承接

```

**(c) setuid / 能力提升调用**
搜 `setuid` / `setgid` / `setresuid` / `capset` / `prctl(PR_SET_KEEPCAPS)`，
以及读取 `/proc/self/status` 判断权限后走特权分支的逻辑。

**(d) 文件权限 / 路径**
- 写入 `/data/local/tmp/`、`/sdcard/` 后由特权进程加载 → **提权链**
- `chmod` 0777 / `chown` system 的调用是否可被外部触发
- 硬编码路径穿越到 `/data/system/`、`/system/` 等特权目录

**判定**：
- 特权进程内可执行任意命令 → **严重**
- 从普通 App 提升到 system/root → **严重**
- 仅能读写本 App 沙箱 → 不报

### 3.7 沙箱逃逸（Sandbox Escape）

> ⚠️ **口径纪律**：Android 的"沙箱"与云端 Agent 沙箱是**两回事**。
> 本技能只做 **Android App 沙箱 / SELinux 域逃逸**；
> 云端 Agent 容器逃逸走 `agent-sandbox-takeover`，不要混为一谈。

**找什么**：
- 读取本 App 沙箱之外的路径：`/data/data/<其他包名>/`、`/data/system/`、`/system/`、`/proc/<其他pid>/`
- 通过特权代理进程/服务间接访问（Confused Deputy）
- `ContentProvider` / Binder 代理未做调用方校验 → 以受害 App 权限读写
- so 里的 `open()` 路径是否经过 `..` 过滤

```python
import ida_name, ida_xref, ida_funcs
for fn in ["open", "openat", "fopen", "access", "stat", "opendir",
           "rename", "unlink", "chmod", "chown"]:
    ea = ida_name.get_name_ea(0, fn)
    if ea == 0xFFFFFFFFFFFFFFFF: continue
    xb = ida_xref.xrefblk_t(); ok = xb.first_to(ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f: print(f"{fn:10s} <- {ida_funcs.get_func_name(f.start_ea)}")
        ok = xb.next_to()
```

**再配合 strings 找特权路径常量**：

```bash
strings -a libxxx.so | grep -E "/data/(system|data|local)|/system/|\.\./|/proc/|/dev/"
```

**判定**：
- 能读写其他 App 沙箱 / 系统目录 → **高危**
- 能以特权身份执行操作 → **严重**
- 仅能访问自己沙箱内文件 → 不报

### 3.8 DoS（拒绝服务）

> ⚠️ **厂商忽略清单明确不收录**：畸形 Intent 导致崩溃、用户重启即恢复的本地 DoS。
> 只有满足以下条件才报：**影响面大（系统级服务不可用）** 或 **不可自恢复（持久化崩溃）**。

**有价值的 DoS 形态**：
- so 被**系统服务**加载，崩溃导致系统服务反复重启（如 SystemUI、telephony、bluetooth）
- native 层死循环 / 无限递归 → ANR 且无法通过重启 App 恢复
- 内存耗尽（可控超大 `malloc`）导致系统级 OOM
- 畸形输入导致 **native crash 且被 Sink 到持久化状态**（下次启动即崩 → bootloop）

```python
# 递归调用检测：函数调用自己的情况
import ida_funcs, ida_xref
def self_recursive(ea):
    xb = ida_xref.xrefblk_t(); ok = xb.first_to(ea, ida_xref.XREF_ALL)
    f = ida_funcs.get_func(ea)
    while ok:
        cf = ida_funcs.get_func(xb.frm)
        if f and cf and cf.start_ea == f.start_ea:
            return True
        ok = xb.next_to()
    return False
```

**判定**：
- 系统级服务崩溃且可远程/本地稳定触发 → **中危**（需说明影响面）
- 仅目标 App 崩溃可重启 → **不报**（忽略清单）

### 3.9 Native 层证书校验绕过 / 网络直连

**找什么**：so 里直接用 `socket` / `libcurl` / `openssl` 发包，绕过 Java 层 `network_security_config.xml`。

```bash
strings -a libxxx.so | grep -iE "curl|openssl|SSL_|TLS_|socket" | head -20
```

**判定**：绕过证书固定 + 明文传输敏感数据 → **中危**（厂商清单里"缺少证书绑定"本身忽略，
但**绕过已配置的校验**可报）。

### 3.10 硬编码密钥 / 算法还原（联动 1.3）

so 里常藏签名密钥与加密算法。IDA 无头是**离线还原**的最佳工具：

```python
# 搜密钥/加密常量
import ida_bytes, ida_strlist
ida_strlist.build_strlist()
for i in range(ida_strlist.get_strlist_qty()):
    si = ida_strlist.string_info_t()
    if ida_strlist.get_strlist_item(si, i):
        s = ida_bytes.get_strlit_contents(si.ea, si.length, si.type)
        if s and any(k in s.lower() for k in
                     (b"key", b"secret", b"sign", b"aes", b"md5", b"iv", b"salt")):
            print(hex(si.ea), s[:120])
```

拿到加密函数后 → Python 重写 → 离线构造签名 → 打未授权接口（回到 `android-security-audit` 一、密钥追踪专项）。

---

## 四、常用 IDAPython 片段（可直接复制进 `execute_python`）

### 4.1 总览：函数数量与关键统计

```python
import ida_funcs, ida_segment, ida_entry
print("functions:", ida_funcs.get_func_qty())
print("exports:", ida_entry.get_entry_qty())
print("segments:", [ (ida_segment.get_segm_name(ida_segment.getnseg(i)),) for i in range(ida_segment.get_segm_qty()) if ida_segment.getnseg(i) ])
```

### 4.2 按名字找函数并反编译

```python
import ida_name, ida_funcs, ida_hexrays
ea = ida_name.get_name_ea(0, "JNI_OnLoad")
print("found:", hex(ea))
if ea != 0xFFFFFFFFFFFFFFFF:
    print(ida_hexrays.decompile(ea))
```

### 4.3 批量导出反编译伪代码（供离线通读）

```python
import ida_funcs, ida_hexrays, os
out = "/tmp/pseudo"
os.makedirs(out, exist_ok=True)
ida_hexrays.init_hexrays_plugin()
n = 0
for i in range(ida_funcs.get_func_qty()):
    ea = ida_funcs.get_func_ea_by_num(i)
    nm = ida_funcs.get_func_name(ea) or f"sub_{ea:x}"
    try:
        cf = ida_hexrays.decompile(ea)
        if cf:
            open(os.path.join(out, f"{ea:x}_{nm}.c"), "w").write(str(cf))
            n += 1
    except Exception:
        pass
print("exported:", n)
```

> 大 so 上很慢。**先筛函数再导出**（例如只导 JNI 导出 + 其被调用者）。

### 4.4 搜字符串并回溯引用者

```python
import ida_bytes, ida_strlist, ida_xref, ida_funcs
KEYWORDS = (b"key", b"secret", b"sign", b"http", b"/data/", b"su")
ida_strlist.build_strlist()
for i in range(ida_strlist.get_strlist_qty()):
    si = ida_strlist.string_info_t()
    if not ida_strlist.get_strlist_item(si, i): continue
    s = ida_bytes.get_strlit_contents(si.ea, si.length, si.type)
    if not s or not any(k in s.lower() for k in KEYWORDS): continue
    print(f"\n[{hex(si.ea)}] {s[:100]}")
    xb = ida_xref.xrefblk_t(); ok = xb.first_to(si.ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f: print("   used in:", hex(f.start_ea), ida_funcs.get_func_name(f.start_ea))
        ok = xb.next_to()
```

### 4.5 危险函数交叉引用总扫（3.1~3.5 的合并版）

```python
import ida_name, ida_xref, ida_funcs

BUCKETS = {
    "溢出": ["strcpy","strcat","sprintf","vsprintf","gets","memcpy","memmove",
             "sscanf","__isoc99_sscanf","alloca","strncpy"],
    "内存": ["malloc","calloc","realloc","free","_Znwm","_Znam","_ZdlPv"],
    "执行": ["system","popen","execve","execl","execlp","execvp",
             "__system_property_set","property_set"],
    "格式串": ["printf","fprintf","snprintf","__android_log_print","syslog","vsnprintf"],
    "文件": ["open","openat","fopen","access","stat","unlink","chmod","chown","opendir"],
}

for bucket, fns in BUCKETS.items():
    print(f"\n===== {bucket} =====")
    for fn in fns:
        ea = ida_name.get_name_ea(0, fn)
        if ea == 0xFFFFFFFFFFFFFFFF: continue
        hits = set()
        xb = ida_xref.xrefblk_t(); ok = xb.first_to(ea, ida_xref.XREF_ALL)
        while ok:
            f = ida_funcs.get_func(xb.frm)
            if f: hits.add((f.start_ea, ida_funcs.get_func_name(f.start_ea)))
            ok = xb.next_to()
        for a, nm in sorted(hits):
            print(f"  {fn:22s} <- {hex(a)} {nm}")
```

### 4.6 假阳过滤：区分"字面量"与"可控输入"

反编译后看调用点：`printf("literal: %d", v)` 是安全的；`printf(v)` 才是格式串漏洞。
写脚本自动粗筛：

```python
import ida_hexrays, ida_funcs
# 对每个候选函数反编译后，人工/正则判断首个参数是否为字符串字面量
# 伪 C 中字面量会带引号，变量则为标识符
cf = ida_hexrays.decompile(ea)
import re
for line in str(cf).splitlines():
    m = re.search(r'\b(printf|sprintf|snprintf|__android_log_print)\s*\(\s*([^,)]+)', line)
    if m:
        first_arg = m.group(2).strip()
        kind = "字面量(安全)" if first_arg.startswith('"') else "变量(需审查)"
        print(f"{kind}: {line.strip()}")
```

---

## 五、证据与成稿要求

每个 native 漏洞必须凑齐这条链，缺一项不许定级：

| # | 证据 | 获取方式 |
|---|---|---|
| 1 | Java 侧入口 | JADX 源码 + 行号：哪个导出组件/native 方法 |
| 2 | .so 清单与架构 | `lib/arm64-v8a/` 路径 + so 名 |
| 3 | 函数地址与伪代码 | IDA 反编译片段（**贴伪代码，不贴汇编**） |
| 4 | 参数可达性 | 从 Java 外部输入 → JNI 参数 → Sink 的完整调用链 |
| 5 | 缓解措施现状 | `readelf` 输出的 canary/RELRO/NX 结论 |
| 6 | 触发验证 | ADB / PoC App 实际触发（crash log / 返回值 / 读取到的内容） |
| 7 | 评级依据 | 对照本手册第三章的判定标准 |

**报告口径**（厂商忽略清单约束）：
- ✅ 写「native 层缺少边界校验导致堆溢出，可远程触发」
- ❌ 不写「用 IDA 无头分析发现」——**工具名不进报告**，只写漏洞本身
- ❌ 「so 未做混淆/加固」「可被重打包」属忽略清单，不报

---

## 六、快速自检

开工前 30 秒确认环境：

```bash
# 1) idalib 可用
python3.11 -c "import idapro; print(idapro.get_library_version())"
#    期望: (9, 5, 261001)

# 2) MCP 连通（换成你的 Agent 自带的 MCP 自检命令）
<你的 Agent> mcp doctor | grep -A3 "ida (stdio"
#    期望: ✓ handshake OK   ✓ 6 tools discovered

# 3) so 目标就位
ls -la /tmp/apktool_out/lib/arm64-v8a/
```

三条全过再开工。任一条失败，先修环境，不要用降级工具硬上。
