# IDA 9.5 无头模式 Native 安全审计手册 · part 1 · part 1

> 分段 1/2。索引见 `IDA95-native-audit-p1.md`。

# IDA 9.5 无头模式 Native 安全审计手册 · part 1

> 分段 1/2。索引见 `IDA95-native-audit.md`。

# IDA 9.5 无头模式 Native 安全审计手册

> 本文件是 `android-security-audit` 的**操作手册**，不是可选参考。
> 做 SO/Native 深挖前必须读完「一、环境与工具」和「二、工作流」两节。
> 目标：用 IDA 9.5 无头模式（idalib）+ 官方 MCP，对 APK 的 `.so` 做**可复现证据级**的漏洞挖掘。

---

## 一、环境与工具（参考配置）

### 1.1 参考路径（按你的环境替换）

| 项目 | 值 |
|---|---|
| IDA | IDA 9.5+（macOS 通常在 `/Applications/IDA Professional 9.5.app`） |
| idalib 引擎 | `(9, 5, 261001)` |
| **必须用的 Python** | Python 3.11+（idalib 只挂在 3.11 解释器上；Homebrew 安装通常在 `/opt/homebrew/bin/python3.11`） |
| JADX CLI | `$JADX_HOME/jadx`（如 `~/tools/jadx/bin/jadx`） |
| MCP server | `uvx --exclude-newer=1s ida-mcp stdio --agent=<name>` |
| 授权文件 | 安装目录下的 `ida.hexlic`（随授权方式不同） |

### 1.2 官方 IDA MCP 的 6 个工具（代码模式架构）

| 工具 | 用途 | 关键点 |
|---|---|---|
| `open_database` | 打开 .so / .i64 | 返回 `instance_id`；`backend: "idalib"` = 真无头。**每开一个 so 都会在样本同目录生成 `.i64`** |
| `execute_python` | 执行 IDAPython | 这是主力。有 `timeout` 参数，大函数反编译要调大 |
| `reference` | 查 ida-domain API 用法 | **先查再写**，避免猜 API 名浪费轮次 |
| `list_databases` | 列出已打开的库 | 多 so 并行分析时确认状态 |
| `save_database` | 落盘 .i64（持久化重命名/注释/类型） | 分析成果要留存时才调 |
| `close_database` | 释放会话租约 | 分析完必须调，否则残留 idalib worker 占内存 |

### 1.3 ✅ Domain API 已可用（已实测通过）

**结论：`ida_domain` 现已安装，推荐优先使用 Domain API。**

背景：MCP 的 `open_database` 返回提示写着「`db` and `ida_domain` are available globally」，
但 9.5 安装时**并不自带**该包（首次实测报 `ModuleNotFoundError`）。现已通过 PyPI 安装修复：

```bash
python3.11 -m pip install ida-domain
# 实测版本: 0.5.1  (requires-python >=3.10, 要求 IDA 9.1+)
```

**`execute_python` 里两个全局开箱可用**（已实测）：

| 全局名 | 类型 | 说明 |
|---|---|---|
| `db` | `ida_domain.database.Database` | 当前已打开的数据库句柄，**不要自己再 `Database.open()`** |
| `ida_domain` | module | 模块本身 |

**Domain API 正确用法（实测通过的 schema，别猜属性名）**：

```python
# 基本信息
db.architecture, db.bitness, db.format        # 'ARM' 64 'ELF64 for ARM64 (Shared object)'

# 函数枚举 —— 地址属性是 start_ea（不是 address！）
funcs = list(db.functions)
for f in funcs:
    f.start_ea, f.end_ea, f.name, f.size
    f.is_lib, f.is_thunk                       # 库函数/跳转桩过滤

# 反编译（返回 PseudocodeFunction，需 str() 转文本）
txt = db.pseudocode.decompile(f.start_ea)
print(str(txt))
db.pseudocode.decompile_many, db.pseudocode.get_text   # 批量/取文本

# 字符串
db.strings.get_all()                           # 迭代所有字符串
db.strings.get_at(ea), db.strings.get_between(a, b)

# 交叉引用（可达性回溯就用它）
db.xrefs.get_callers(ea)                       # ⭐ 回溯调用者
db.xrefs.calls_to_ea(ea), db.xrefs.calls_from_ea(ea)
db.xrefs.code_refs_to_ea(ea), db.xrefs.data_refs_to_ea(ea)
db.xrefs.reads_of_ea(ea), db.xrefs.writes_to_ea(ea)
```

> ⚠️ **两个易错点**：
> 1. **地址属性是 `f.start_ea` / `f.end_ea`**，写 `f.address` 会报
>    `AttributeError: 'func_t' object has no attribute 'address'`。
> 2. `db.pseudocode.decompile()` 返回对象不是字符串，**要 `str()`** 才能当文本处理/写文件。

**降级策略**：若某台机器上 `ida_domain` 缺失或 API 不兼容，**回退标准 IDAPython**
（`ida_funcs` / `ida_bytes` / `ida_name` / `ida_xref` / `ida_hexrays` / `ida_segment` /
`ida_entry` / `ida_nalt`，实测全部可用）——本手册第四章片段两种写法都给了，不会卡住。
**不要因为 Domain API 报错就换工具。**

**坑 2：`getn_func()` 已弃用**（注意：`ida_domain` 包内部自己也在用它，会有 DeprecationWarning，可忽略）

```python
ida_funcs.getn_func(i)                  # ⚠️ DeprecationWarning（9.5）
ida_funcs.get_func_ea_by_num(i)         # ✅ 取第 i 个函数的地址
ida_funcs.get_func_entry_info_by_num(i) # ✅ 取入口信息
```

按数量遍历函数一律用 `get_func_qty()` + `get_func_ea_by_num(i)`。

**坑 3：别拿 `/bin/ls` 之类自测**

macOS 上 `/bin/ls` 是 dyld 缓存桩，`open_database` 会返回 `2`、0 函数。**这是假失败**。
测试用 APK 里真实提取的 `.so`。

### 1.4 无 MCP 时的等价脚本用法

```python
import idapro          # 必须第一个 import，且在任何 IDA 模块之前
import ida_auto, ida_funcs, ida_hexrays

r = idapro.open_database("/path/to/libxxx.so", True)   # 0 = 成功
ida_auto.auto_wait()
ida_hexrays.init_hexrays_plugin()

for i in range(ida_funcs.get_func_qty()):
    ea = ida_funcs.get_func_ea_by_num(i)
    print(hex(ea), ida_funcs.get_func_name(ea))

idapro.close_database(False)
```

运行：`python3.11 script.py`

---

## 二、工作流（六步，按序执行）

### Step 1：DEX 侧先定位 JNI 入口（不要一上来就全量逆向 so）

```bash
# 1) Java 侧声明了哪些 native 方法
grep -rn "native " /tmp/jadx_out/sources/ | grep -v "//"

# 2) 加载了哪些 so
grep -rn "System.loadLibrary\|System.load" /tmp/jadx_out/sources/

# 3) so 清单（arm64-v8a 优先）
ls -la /tmp/apktool_out/lib/arm64-v8a/
```

理由：`.so` 动辄几万个函数，**先拿到「Java 调了哪些 native 方法」这张地图**，
再带着目标进 IDA，比盲目全量逆向快一个数量级。

### Step 2：用 IDA MCP 打开 so

```
open_database("/tmp/apktool_out/lib/arm64-v8a/libxxx.so")
```

若已有 `.i64`（之前分析过）可直接开 `.i64`，省去重复分析。

### Step 3：枚举 JNI 导出，定位真正的攻击面

```python
import ida_entry, ida_name, ida_funcs

# 静态注册：导出表里的 Java_* / JNI_*
n = ida_entry.get_entry_qty()
for i in range(n):
    ea = ida_entry.get_entry_ordinal(i)
    addr = ida_entry.get_entry(ea)
    nm = ida_entry.get_entry_name(ea) or ""
    if nm.startswith("Java_") or nm.startswith("JNI_"):
        print(hex(addr), nm)

# 补充：名字表里搜（有些不在导出表但被 RegisterNatives 引用）
for ea, nm in [ (ida_name.get_nlist_ea(i), ida_name.get_nlist_name(i))
                for i in range(ida_name.get_nlist_size()) ]:
    if nm and (nm.startswith("Java_") or nm.startswith("JNI_")):
        print(hex(ea), nm)
```

**静态注册**：函数名形如 `Java_com_example_app_NativeLib_sign` → 直接对应 Java 方法。
**动态注册**：so 里搜不到 `Java_` 前缀 → 必须找 `JNI_OnLoad` 追 `RegisterNatives`：

```python
import ida_name, ida_funcs, ida_xref, ida_bytes

for target in ("JNI_OnLoad", "RegisterNatives"):
    ea = ida_name.get_name_ea(0, target)
    print(f"{target} @ {hex(ea) if ea != 0xFFFFFFFFFFFFFFFF else 'NOT FOUND'}")

# 找所有调用 RegisterNatives 的位置 → 那里的 JNINativeMethod 数组就是方法映射表
rn = ida_name.get_name_ea(0, "RegisterNatives")
if rn != 0xFFFFFFFFFFFFFFFF:
    xb = ida_xref.xrefblk_t()
    ok = xb.first_to(rn, ida_xref.XREF_ALL)
    while ok:
        print("called from:", hex(xb.frm))
        ok = xb.next_to()
```

拿到 `JNINativeMethod` 数组后，`{name, signature, fnPtr}` 三元组把 Java 方法与 native 函数一一对应。

### Step 4：按危险面逐项审计（见第三章清单）

对每个可达的 JNI 函数：
1. 反编译拿伪 C
2. 追参数来源：JNI 参数（`JNIEnv*` / `jobject` / `jstring`）→ 是否来自 Java 侧外部输入
3. 检查 Sink：危险函数、无边界的内存操作、路径拼接
4. 记录证据（函数名 + 地址 + 伪代码片段）

```python
import ida_hexrays
cf = ida_hexrays.decompile(ea)
print(cf)
```

### Step 5：交叉引用回溯可达性（判断"能不能被外部触发"）

**这一步决定漏洞评级**——不可达的 Sink 不是漏洞。

```python
import ida_xref, ida_funcs

def callers_of(ea, depth=2, seen=None):
    """递归取调用者，用于回溯 JNI 入口"""
    seen = seen or set()
    xb = ida_xref.xrefblk_t()
    ok = xb.first_to(ea, ida_xref.XREF_ALL)
    while ok:
        f = ida_funcs.get_func(xb.frm)
        if f and f.start_ea not in seen:
            seen.add(f.start_ea)
            print("  " * (2 - depth), "←", hex(f.start_ea), ida_funcs.get_func_name(f.start_ea))
            if depth > 1:
                callers_of(f.start_ea, depth - 1, seen)
        ok = xb.next_to()

callers_of(suspect_func_ea)
```

### Step 6：收尾

- 有价值的重命名/注释 → `save_database` 落盘
- `close_database` 释放会话
- 分析产物 `.i64` 归档到 `hunts/<目标>/ida/`

---

## 三、Native 漏洞挖掘清单

> 每项都给出：**找什么 → 怎么找（脚本/命令）→ 怎么判定**。
> 判定分级统一遵循：**能证明可达 + 可触发 = 高危；仅可疑 = 中危；纯理论 = 不报**。

### 3.0 先判断"能不能溢出"——看编译期缓解措施

**这一步必须先做**：ASLR/DEP/Canary/FORTIFY 决定了栈溢出到底是不是漏洞。
Android 官方 NDK 默认开启 canary 与 FORTIFY，**现代 App 的"栈溢出"多数不可利用**。

```bash
# 用 readelf 看符号与段
readelf -hW  libxxx.so     | grep Type        # DYN = PIE
readelf -lW  libxxx.so     | grep -i stack    # GNU_STACK: RW = 无 NX（可执行栈，极罕见）
readelf -sW  libxxx.so     | grep -iE "stack_chk|fortify"   # 有 __stack_chk_fail = 有 canary
readelf -dW  libxxx.so     | grep -iE "bind_now|relro"      # BIND_NOW + GNU_RELRO = Full RELRO
```

判定速查：

| 现象 | 含义 | 对评级的影响 |
|---|---|---|
| `GNU_STACK` 为 `RWE` | 栈可执行 | 栈溢出可直接劫持执行流 → **严重** |
| 无 `__stack_chk_fail` 符号 | 无栈保护 | 栈溢出可利用性大增 |
| 有 `__stack_chk_fail` | 有 canary | 纯栈溢出通常打不通 → 转看**堆溢出/整数溢出/越界读** |
| `BIND_NOW` 缺失 | 非 Full RELRO | GOT 覆写可行（需配合任意写） |
| 无 `__*_chk` 符号 | 无 FORTIFY | `strcpy`/`sprintf` 等未加固 |

> 系统 App（`/system/priv-app/`）常编译于更宽松的时代，**优先审计这些**。

### 3.1 栈溢出 / 缓冲区溢出

**找什么**：不定长写入固定栈缓冲。

**spot-list（反编译里搜这些调用）**：

```
strcpy  strcat  sprintf  vsprintf  gets
memcpy  memmove  strncpy(dst, src, strlen(src))   ← 长度用错也是溢出
sscanf  scanf  __isoc99_sscanf
