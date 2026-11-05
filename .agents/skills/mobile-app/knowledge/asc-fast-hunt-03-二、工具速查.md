# 二、工具速查

> 来源：CkSKILLS v1 `asc-fast-hunt` §二、工具速查（迁移至 v2 知识块）

### 2.1 五个官方子命令

```bash
ASC=$HOME/tools/ASC

$ASC/asc getmanifest <apk>
$ASC/asc getmanifest <apk> | grep -B2 -A6 'exported="true"'   # 导出组件
$ASC/asc getmanifest <apk> | grep 'android:scheme'            # Deep Link scheme
$ASC/asc getmanifest <apk> -o /tmp/AndroidManifest.xml >/dev/null

$ASC/asc listclass <apk> --prefix com.x.y
$ASC/asc listclass <apk> -o /tmp/classes.txt >/dev/null

$ASC/asc findrefs <apk> string <关键词>                        # 模糊
$ASC/asc findrefs <apk> type com.x.Y                          # 模糊
$ASC/asc findrefs <apk> method <方法名> [--class <类>] [--fuzzy-class]
$ASC/asc findrefs <apk> field <字段名> [--class <类>] [--fuzzy-class]
$ASC/asc findrefs <apk> extends <类>                          # 0.1.2 新增：找子类
$ASC/asc findrefs <apk> impl <接口>                           # 0.1.2 新增：找接口实现
$ASC/asc findrefs --debug <apk> string token                  # --debug/--threads 写在 apk 前
$ASC/asc findrefs --threads 16 <apk> string token             # 默认 8

$ASC/asc getclass <apk> 'Lcom/x/Y;' -o Y.java                 # Dalvik 格式
$ASC/asc getclass <apk> com.x.Y -o Y.java                     # 点分格式（自动转换）

$ASC/asc disassemble <apk> com.x.Y -o Y.smali                 # 基本反汇编
$ASC/asc disassemble <apk> com.x.Y --debuginfo                # 带 .line/局部变量指令
$ASC/asc disassemble <apk> com.x.Y --method 'run(I)V'         # 只出精确签名的方法
```

`-o` 是**额外写文件**，标准输出照样打。批量搜索只要文件时把 stdout 丢掉（`>/dev/null`），再读那个文件。

**0.1.2 修了定位类 bug，旧树的命中不要沿用，用本版重跑：**

- non-BMP 字符串/类名（emoji、生僻字）此前可能漏检或错位：`findrefs string/type`、`getclass`、`listclass` 都在本版重跑。
- `findrefs string` 改为按匹配项自身 `string_data_item` 解析；精确成员扫描限定在 DEX 表边界内。旧的 `findrefs field/method` 位置可能偏。
- 无代码方法（abstract/native）现在保留参数信息；DEX builder 的 UTF-16 计数修复。
- 代码扫描走 `byte.translate`（0.1.1 起，约快 30%）。耗时表里的 0.3s 是旧版实测，只作数量级。

### 2.2 输出格式与语义（Agent 必读）

**findrefs 输出**（一行一个命中点）：

```
classes3.dex | LA8/m$a;->b | matched=(appkey)
   ↑ dex 名    ↑ 类->方法     ↑ 命中内容
```

- **搜的是"引用点"不是"定义"**：`findrefs method onCreate` 返回的是**调用了 onCreate 的位置**。看某个方法/字段**自身的实现**要配合 `getclass`。
- **命中按"调用方方法"去重聚合**：同一方法内多次调用同名 API 只输出一行，多个命中合并显示在 `matched=(a; b; c)` 里。所以本技能命中数**少于** `grep` 的行计数（实测同一 4.4MB 包：`exec` 39 vs 95、`startActivity` 18 vs 23、`getStringExtra` 4 vs 9）——**不是漏检，是聚合**；`grep` 这边还会同时匹配方法定义、JADX 注释与子串，噪音更大。两者数字不可直接对比。
- `string` / `type` 是**模糊匹配**（substring）；`method` / `field` 的 `--class` 默认精确匹配，加 `--fuzzy-class` 才模糊（如 `--class miui --fuzzy-class` 匹配所有 miui 命名空间）。
- 一个关键词常命中几十~几百行。`-o` 不会关掉 stdout，批量时 `>/dev/null` 再读文件，不要把整份命中打进上下文。
- 搜索**跨全部 dex 分片**（classes.dex / classes2.dex / …），无需先合并。

**上游官方基准（10 线程，四档 Ascending APK；图表见 `docs/benchmark_all_en.png`）**

| 指标 | TelegramX 59MB | WhatsApp 130MB | Grab 228MB | Lark 352MB |
|---|---|---|---|---|
| 全局字符串 xref（ASC） | **322ms** | **418ms** | **806ms** | **1.597s** |
| 全局字符串 xref（JADX） | 20s | 32s | 2m14s | 8m2s（**OOM，仅搜 49%**） |
| 单类反编译（ASC） | **157ms** | **141ms** | **165ms** | **303ms** |
| 单类反编译（JADX） | 6s | 15s | 37s | 1m32s |
| CLI 内存（ASC） | 36MB | 36MB | 58MB | 141MB |
| CLI 内存（JADX） | 1,016MB | 2.1GB | 7.1GB | 13.2GB（GUI 最高 22GB+） |
| 磁盘缓存（ASC / JADX） | 0MB / 119MB | 0MB / 30MB | 0MB / 127MB | 0MB / 322MB |

> 加速比：搜索 **62×–302×**、单类反编译 **38×–304×**、内存 **28×–96×**；**磁盘缓存恒为 0**（全程内存操作，不在目标机留产物）。越大包优势越大——JADX 在 352MB 包上搜索直接 OOM，ASC 全档完成。上游明确：可配 Agent 同时分析**几十~上百个 APK**，弱机器也可行。

> 本地旧版补充实测（68MB 包，0.1.1 时代）：`getmanifest` ~0.3s / ~110MB、`findrefs string` ~0.32s / ~108MB、`getclass` ~0.12s；JADX 全量 39.2s / 6.96GB（17613 类）。耗时只作数量级参照，新版只会更快。

### 2.3 输出质量边界（决定何时必须转全量反编译）

`getclass`/`disassemble` 后端是内置 `dadguard`（从 Androguard DAD 抽离的版本）：**寄存器级变量名（v0_2、p9）、无类型推断、控制流较朴素**。够做的事：读方法逻辑、看字符串常量、识别加密调用（`MessageDigest.getInstance("MD5")`、`Cipher.getInstance("AES/...")`）、看调用关系与参数来源。

**⚠️ 类型不可信（实测，最危险的边界）**：DAD 会给出**错误类型**。同一个类、同一个方法，两个工具的输出：

```java
// JADX 1.5.5（正确）
ByteBuffer outputBuffer = this.f2295b.getOutputBuffer(i3);

// ASC / DAD（错误：该方法真实返回 ByteBuffer，却被声明成 String）
String v0_1 = this.b.getOutputBuffer(p6);
```

因此本技能的输出**不可用于数据流/污染推理**（"这个参数可不可控、会不会流到危险点"），**也不适合作为报告取证截图**。它只用于快速读懂大致逻辑、认出加密调用与字符串常量——一旦要做可达性推理或写报告，必须换 JADX 产物。

**资源层为零**：本技能只有 Manifest 解析（0.1.2 起内置 `axml`），`res/` 下的 `file_paths.xml`（FileProvider 路径暴露）、`network_security_config.xml`、`strings.xml`（硬编码密钥高发地）、layout（UI 注入点）**一律看不到**——同一 4.4MB 包 JADX 解出 **1629 个 res/ XML**。组件审计、Provider 审计必须走 `apk-reversing` 的 apktool/JADX 产物。

**做不到的搜索形态**：`findrefs` 查的是 DEX 引用表，**无法表达"同一行两个 API 共现"的模式**——`android-security-audit` Step 2 里的 `grep -rE "startActivity.*getParcelable"`（Intent 重定向）、`grep -rE "setTitle.*getIntent"`（弹窗欺骗）这类模式，本技能只能逐个 API 分别查再自己交叉。也没有项目级通读视图。

不够做的事：精读复杂混淆逻辑、跨类数据流追踪、函数调用图、写报告级源码引用、资源层分析、共现模式搜索。**当需要这些时，转 `apk-reversing` 全量反编译用 JADX 读。**

### 2.4 批量多 APK triage（Agent 编排）

上游基准强调：ASC 可在弱机器上同时分析**几十~上百个 APK**（单命令常驻 36–141MB、0 磁盘缓存）。资产测绘常一次拿到一批包（分片/兄弟应用/历史版本/多厂商），逐包开 JADX 不现实——用 shell 层并行把 ASC 排成流水线：

```bash
ASC=$HOME/tools/ASC
OUT=/tmp/asc_batch; mkdir -p "$OUT"

ls /path/to/apks/*.apk | xargs -P 4 -I{} sh -c \
  '"$0/asc" findrefs "$1" string appkey -o '"$OUT"'/$(basename "$1").appkey.txt >/dev/null' \
  "$ASC" {}

grep -l . "$OUT"/*.appkey.txt

```

- **线程与内存**：`--threads` 是**单 APK 内**线程；多包并行用 `xargs -P`（或 GNU parallel）。总内存 ≈ N × 单包峰值（大包 ~141MB，小包 ~36MB）。
- **先清单再批量**：`listclass --prefix` 每包落一份类清单；同厂商多 App 类名高度相似，关键词矩阵可复用。
- **落盘策略**：每包每关键词一文件，先 `grep -l` 筛有命中的包，再按需读文件——别把整批命中灌进上下文。
- **适用边界**：批量 triage 只做"有没有/在哪"；命中后仍按单包工作流 Step 3–5 精读与交棒。

---
