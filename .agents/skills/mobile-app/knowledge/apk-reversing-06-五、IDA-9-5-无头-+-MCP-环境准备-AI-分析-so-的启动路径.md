# 五、IDA 9.5 无头 + MCP 环境准备（AI 分析 so 的启动路径）

> 来源：CkSKILLS v1 `apk-reversing` §五、IDA 9.5 无头 + MCP 环境准备（AI 分析 so 的启动路径）（迁移至 v2 知识块）

> 目标：让 Agent 能自主驱动 IDA 分析 .so（定位 JNI 导出 → 反编译伪 C → 读算法重写 → 挖内存安全漏洞）。
> **IDA 9.5 的 idalib 是真无头**——不导入、不建工程、不开 GUI，`open_database` 直接分析。
> **只用 IDA 9.5 无头 + 官方 IDA MCP，不用 Ghidra / GhidraMCP。**

### 5.1 环境自检（开工前必做）

```bash
python3.11 -c "import idapro; print(idapro.get_library_version())"

<你的 Agent> mcp doctor | grep -A3 "ida (stdio"

ls -la apktool_out/lib/arm64-v8a/
```

三条全过再开工。任一条失败**先修环境**，不要降级换工具。

### 5.2 MCP 暴露的 6 个工具（代码模式架构）

| 工具 | 用途 | 关键点 |
|---|---|---|
| `open_database` | 打开 .so / .i64 | 返回 `instance_id`；`backend: "idalib"` = 真无头。**会在样本同目录生成 `.i64`** |
| `execute_python` | 执行 IDAPython | 主力工具，有 `timeout` 参数，大函数要调大 |
| `reference` | 查 ida-domain API 用法 | **先查再写**，别猜 API 名浪费轮次 |
| `list_databases` | 列出已打开库 | 多 so 并行时确认状态 |
| `save_database` | 落盘 .i64（持久化重命名/注释） | 分析成果要留存时才调 |
| `close_database` | 释放会话租约 | 分析完必须调，否则残留 worker 占内存 |

### 5.3 ✅ Domain API 优先（已装好）+ 两个注意点

**`ida_domain` 已安装可用**（0.5.1，2026-10-04 修复了 9.5 不自带的问题）：

```bash
python3.11 -m pip install ida-domain
```

`execute_python` 里两个全局开箱可用：`db`（Domain API 句柄，**别自己再 `Database.open()`**）、`ida_domain`。

```python
for f in db.functions:
    print(hex(f.start_ea), f.name)
txt = str(db.pseudocode.decompile(f.start_ea))   # 必须 str()
callers = list(db.xrefs.get_callers(f.start_ea)) # 可达性回溯
```

**注意点 1：地址属性是 `f.start_ea`**，写 `f.address` 会报 `AttributeError`；反编译返回值要 `str()`。
**注意点 2：`getn_func()` 在 9.5 已弃用**（`ida_domain` 包内部也在用它，有 DeprecationWarning 可忽略）：

```python
ida_funcs.getn_func(i)          # ⚠️ DeprecationWarning
ida_funcs.get_func_ea_by_num(i) # ✅ 改用这个
```

**降级**：若 `ida_domain` 缺失或 API 不兼容，回退标准 IDAPython
（`ida_funcs`/`ida_bytes`/`ida_name`/`ida_xref`/`ida_hexrays`/`ida_segment`/`ida_entry`/`ida_nalt`，实测全部可用）——**不要因为 Domain API 报错就换工具**。
完整 schema 与两种写法对照 → `references/IDA95-native-audit.md` 1.3

**注意点 3：别拿 `/bin/ls` 之类自测**

macOS 上 `/bin/ls` 是 dyld 缓存桩，`open_database` 返回 `2`、0 函数——**假失败**。
测试一律用 APK 里真实提取的 `.so`。

### 5.4 打开 so 并枚举 JNI 导出

```
open_database("apktool_out/lib/arm64-v8a/libxxx.so")
```

```python
import ida_entry
for i in range(ida_entry.get_entry_qty()):
    ord_ = ida_entry.get_entry_ordinal(i)
    nm = ida_entry.get_entry_name(ord_) or ""
    if nm.startswith(("Java_", "JNI_")):
        print(hex(ida_entry.get_entry(ord_)), nm)

import ida_name, ida_xref
ea = ida_name.get_name_ea(0, "RegisterNatives")
xb = ida_xref.xrefblk_t()
ok = xb.first_to(ea, ida_xref.XREF_ALL)
while ok:
    print("RegisterNatives called from:", hex(xb.frm)); ok = xb.next_to()
```

### 5.5 AI 驱动分析路径（工具调用序列）

```
1. open_database              → 打开 so（或已有 .i64 直接开，省重复分析）
2. execute_python             → 枚举 Java_* 导出 / 追 JNI_OnLoad+RegisterNatives
3. references / xrefs 回溯    → 确认哪些函数从 JNI 入口可达（决定评级）
4. decompile                  → 拿伪 C → 识别算法（MD5/SHA/AES）与拼接顺序 → Python 重写
5. 危险函数交叉引用总扫        → strcpy/system/memcpy/open 等 Sink（见 android-security-audit 三）
6. readelf 摸底缓解措施        → canary/RELRO/NX 决定溢出类能否定级
7. save_database + close_database
```

- 伪 C 读不动（ollvm 控制流平坦化 / VMP / 字符串加密）→ 记录「需动态路径」，回落 `android-security-audit` 1.3 抓包兜底
- 完整脚本模板（JNI 枚举、危险函数总扫、字符串回溯、批量伪代码导出、假阳过滤）→ **references/IDA95-native-audit.md**

### 5.6 注意事项

- 分析对象是从 APK 提取的**具体 .so**（`lib/arm64-v8a/`），不是整个 APK
- `arm64-v8a` 原生支持；x86/x86_64 模拟器 so 也可分析
- 大 so 首次自动分析要几十秒到几分钟，**等 `open_database` 返回再调后续工具**
- `.i64` 会生成在样本同目录，归档到 `hunts/<目标>/ida/`；**旧格式库一旦被 9.5 保存，低版本可能打不开**，需要回退能力就先 `cp` 副本
- **不做**的事：不用 Ghidra/GhidraMCP、不用 Radare2 做替代、不因 idalib 报错就换工具（先修环境）
