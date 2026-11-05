# 三、Native/内存安全深挖（IDA 9.5 无头 + MCP）

> 来源：CkSKILLS v1 `android-security-audit` §三、Native/内存安全深挖（IDA 9.5 无头 + MCP）（迁移至 v2 知识块）

> **进入条件（命中任一才进本章，否则别碰 IDA）**：
> ① JADX 产物 grep 到 `native ` 声明或 `System.loadLibrary/System.load`；② `lib/arm64-v8a/` 下有业务 so（非壳）；③ 字符串/密钥/命令执行命中点落在 native 方法参数上；④ 需要还原算法但 Java 层只是 JNI 壳。
> **反例（不进本章）**：纯 Java 无 so；只有壳 so 且未脱壳（先 `apk-reversing`）；Java 层已能定论且不需要 native 证据。
> **抄近路**：大包只想确认 native 算法、JADX 全量成本过高时，先用 `asc-fast-hunt` 定位 Java 调用点，**直接进本章**（见 `../../../../AGENTS.md` 3.1）。

> **本章定位**：Java 层审完（二）之后，对 `lib/arm64-v8a/*.so` 做**证据级**漏洞挖掘，重点产出 **RCE / 提权 / 沙箱逃逸 / 溢出 / DoS**。
> **操作手册（必读）**：[references/IDA95-native-audit.md](references/IDA95-native-audit.md) —— 含已验证环境路径、完整 IDAPython 脚本模板、六步工作流、判定分级表。
> **工具唯一路径**：**IDA 9.5 无头模式（idalib）+ 官方 IDA MCP**。不用 Ghidra / GhidraMCP。

### 3.0 开工前置：环境自检 + 缓解措施摸底

**第一步永远是环境自检**（三条全过再开工，失败先修环境，不要降级换工具）：

```bash
python3.11 -c "import idapro; print(idapro.get_library_version())"   # 期望 (9, 5, 261001)
<你的 Agent> mcp doctor | grep -A3 "ida (stdio"                                        # 期望 ✓ handshake OK ✓ 6 tools
ls -la /tmp/apktool_out/lib/arm64-v8a/                                                 # so 目标就位
```

**第二步摸底缓解措施**——这一条直接决定溢出类发现能不能定级：

```bash
readelf -hW libxxx.so | grep Type                            # DYN = PIE
readelf -lW libxxx.so | grep -i stack                        # GNU_STACK: RWE = 可执行栈（严重）
readelf -sW libxxx.so | grep -iE "stack_chk|fortify"         # 有 __stack_chk_fail = 有 canary
readelf -dW libxxx.so | grep -iE "bind_now|relro"            # BIND_NOW + GNU_RELRO = Full RELRO
```

| 现象 | 对评级的影响 |
|---|---|
| `GNU_STACK` = `RWE` | 栈溢出可直接劫持执行流 → **严重** |
| 无 `__stack_chk_fail` | 无栈保护，溢出可利用性大增 |
| 有 canary + Full RELRO | **纯栈溢出通常打不通** → 转攻堆溢出/整数溢出/越界读/逻辑缺陷 |
| 无 `__*_chk` 符号 | 无 FORTIFY，`strcpy`/`sprintf` 等未加固 |

> ⚠️ **反幻觉要点**：现代 NDK 默认开 canary + FORTIFY，**"看到 strcpy 就报栈溢出"是典型误报**。
> 必须先证明「长度可控 + 缓冲区固定 + 无边界校验 + 缓解措施允许」，缺一项只能定中危或不定级。
> 系统 App（`/system/priv-app/`）常编译于更宽松的时代，**优先审计这些**。

### 3.1 JNI 攻击面建模（先画地图，再逆向）

`.so` 动辄几万函数，**不要盲目全量逆向**。先用 JADX 侧拿到「Java 调了哪些 native 方法」这张地图：

```bash
grep -rn "native " /tmp/jadx_out/sources/ | grep -v "^.*://"    # Java 侧 native 声明
grep -rn "System.loadLibrary\|System.load" /tmp/jadx_out/sources/  # 加载了哪些 so
```

再进 IDA 无头枚举导出，把 Java 方法与 native 函数一一对应：

- **静态注册**：导出表里 `Java_包名_类名_方法名` → 直接对应
- **动态注册**：so 里**搜不到** `Java_` 前缀 → 必须找 `JNI_OnLoad` 追 `RegisterNatives`，
  那里的 `JNINativeMethod{name, signature, fnPtr}` 数组才是真正的方法映射表

> 完整枚举脚本（`ida_entry` / `ida_name` / `ida_xref` 三路覆盖）见操作手册 **二、Step 3**。

**这一步产出的是攻击面清单**：每个「外部可达的 JNI 函数 + 其参数」都是后续审计的候选点。

### 3.2 逐项深挖清单

> 每项都配套**可复制的 IDAPython 脚本**，见操作手册 **三、Native 漏洞挖掘清单** 与 **四、常用片段**。
> 统一判定原则：**能证明可达 + 可触发 = 高危；仅可疑 = 中危；纯理论 = 不报。**

| # | 漏洞类型 | 搜索重点 | 判定要点 |
|---|---|---|---|
| 1 | **栈/缓冲区溢出** | `strcpy` `strcat` `sprintf` `gets` `memcpy` `alloca`；`strncpy(dst,src,strlen(src))` | 长度来自 `GetStringUTFChars`/`GetArrayLength` 且无 `< sizeof(buf)` 校验 |
| 2 | **堆溢出 / UAF / double free** | `malloc`/`realloc`/`free`；异常路径重复释放；`free` 后继续解引用 | 分配、越界写、可控长度**同函数内同时出现** |
| 3 | **整数溢出→短分配长拷贝** | `malloc(a*b)` 与随后 `memcpy(..., a*b*4)` 算式不一致；`int`/`size_t` 混用 | native 里**最真实可利用**的形态 |
| 4 | **格式化字符串** | `printf` 家族首个参数非字面量；**`__android_log_print`** 是 Android 高发点 | `printf(v12)` 而非 `printf("fmt", v12)` |
| 5 | **命令注入（RCE 最直接）** | `system` `popen` `execve` `execlp`；`property_set` | 命令串拼接了 Java 传入值 → **严重** |
| 6 | **提权** | `setuid`/`setgid`/`capset`；Binder 接口缺 `checkCallingPermission`；写 `/data/local/tmp` 后被特权进程加载 | 先 `adb shell ps -Z` 确认目标 domain（`system_app`/`platform_app`） |
| 7 | **沙箱逃逸** | `open`/`openat`/`fopen` 路径含 `..`；读写 `/data/data/<其他包>/`、`/data/system/` | ⚠️ 仅指 **Android App 沙箱/SELinux 域逃逸**；云端容器逃逸走 `agent-sandbox-takeover` |
| 8 | **DoS** | 可控超大 `malloc`、无限递归、native 解析器畸形输入 | ⚠️ 厂商忽略清单**不收录**「App 崩溃可重启」；只有**系统级服务崩溃**或**不可自恢复**才报 |
| 9 | **Native 层证书校验绕过** | so 里直接 `socket`/`libcurl`/`openssl` 发包 | 绕过已配置的 pinning + 明文传敏感数据 → 中危 |
| 10 | **硬编码密钥/算法还原** | 字符串表搜 `key`/`secret`/`sign`/`iv`/`salt` | 回到 一、1.3 密钥追踪链 → 打未授权接口 |

### 3.3 可达性回溯（决定评级的关键一步）

**IDA 里看到危险 Sink ≠ 漏洞。** 必须从 JNI 入口反向确认这条链能被外部触发：

```
Java 导出组件 / Deep Link / WebView JSBridge  ← 外部输入（远程 or 本地）
        ↓
Java native 方法声明                           ← JADX 确认
        ↓
JNI 导出函数（Java_xxx / RegisterNatives 表）  ← IDA 确认
        ↓
危险 Sink（strcpy / system / open / ...）      ← IDA 确认
```

用 `ida_xref.xrefblk_t()` 递归回溯调用者（脚本见操作手册 **二、Step 5**）。
**链上任何一环断裂（参数不可控 / 有边界校验 / 不可达）→ 降级或不定级。**

### 3.4 动态验证

- **ADB 触发**：通过导出组件 / Deep Link 把畸形参数喂进 native（配合四、动态验证）
- **crash 取证**：`adb logcat | grep -E "DEBUG|SIGSEGV|backtrace"`，tombstone 里确认崩溃地址落在目标 so
- **信息泄露验证**：越界读类漏洞要能实际打印出沙箱外内存内容
- ⚠️ **Frida 边界不变**：Frida 只作**取证**，最终 PoC 用提取的密钥/构造的输入直接触发（见 一、1.3 的 Frida 边界规则）

### 3.5 证据链与成稿（缺一项不许定级）

| # | 证据 | 获取方式 |
|---|---|---|
| 1 | Java 侧入口 | JADX 源码 + 行号（哪个导出组件/native 方法） |
| 2 | so 路径与架构 | `lib/arm64-v8a/libxxx.so` |
| 3 | 函数地址 + 伪代码 | IDA 反编译片段（**贴伪代码，不贴汇编**） |
| 4 | 可达性链 | 3.3 的四环完整链路 |
| 5 | 缓解措施现状 | `readelf` 的 canary/RELRO/NX 结论 |
| 6 | 触发验证 | ADB / PoC App 实际触发（crash log / 返回值 / 读到的内容） |
| 7 | 评级依据 | 对照 3.2 判定要点 |

**报告口径**：✅ 写「native 层缺少边界校验导致堆溢出，可远程触发」；❌ 不写工具名；❌ 不报「so 未混淆/可重打包」（忽略清单）。

---
