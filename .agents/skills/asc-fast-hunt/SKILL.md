---
name: asc-fast-hunt
description: 当需要在不对 APK 全量反编译的前提下秒级定位硬编码密钥/签名函数/隐藏接口/调试后门，或 APK 过大（>100MB）JADX 全量反编译过慢、内存吃紧，或脱壳产物（裸 dex）需要快速检索，或只想先读一下 Manifest 组件面/权限清单时调用。负责基于 Droid ASC 的零预处理快速定位（findrefs 全局交叉引用搜索 + getclass 按需反编译 + Manifest 秒读），是 android-security-audit「密钥追踪→未授权接口」链的快速前置引擎，也是 apk-reversing 全量还原前的 triage 快筛。命中场景：大包快速 triage、搜 appkey/secret/sign/Authorization/RSA、按类名秒看实现逻辑、追字符串/方法/字段引用链、脱壳 dex 快速检索、Dex 分片全局搜索。注意本技能**不能替代 JADX**：它无资源层（res/ 全解不出）、DAD 输出类型不可信、无法搜共现模式，因此精读/数据流推理/资源审计/报告取证仍须走 apk-reversing 全量产物。加固壳识别与脱壳见 apk-reversing；组件安全深挖与漏洞验证见 android-security-audit；正式报告见 report。
---

# asc-fast-hunt — APK 零预处理快速定位（Droid ASC）

> **定位**：本技能是**秒级定位引擎**，解决"先全量反编译再搜索"的等待问题——把 APK 当只读数据库直接查询，不建全局索引、不落全量产物，命中即按需反编译单个类。它**只负责快速定位与读实现**，不负责脱壳、不负责漏洞定级与成稿。
>
> **三段式分工**：`asc-fast-hunt`（秒级快筛定位）→ `apk-reversing`（加固壳脱壳 + 全量还原，仅当快筛命中值得深挖时）→ `android-security-audit`（组件安全/密钥追踪深挖 + 动态验证）→ `report`（DOCX 成稿）。

## 出处声明（必须保留）

- 工具仓库：**https://github.com/MG1937/ASC**（Droid ASC，Black Hat Europe Arsenal 议题）
- 本 SKILL 只是对该工具的**封装与工作流编排**，工具算法与实现版权归原作者所有，未做任何代码修改
- 原仓库**无 LICENSE 文件**（默认保留所有权利）：仅限本机自用与授权测试，**不得对外分发、不得打包发布、不得声称自有**
- 本机已装位置：`/Users/apple/Desktop/武器库/5.逆向/ASC/`（与 jadx、ida-mcp-server 并列）；如需重建见本文「环境安装与自检」

## 何时调用（触发条件）

- 拿到 APK 想知道"有没有硬编码密钥/隐藏接口/调试后门"，**不想等 JADX 全量反编译**（大包动辄几十分钟 + 数 GB 内存）
- APK > 100MB（系统应用、游戏、大厂 App），全量反编译成本过高
- 已有脱壳产物（裸 dex / dex 分片），需要快速检索而不是重新全量反编译
- 只想先看 Manifest 的 exported 组件、权限、scheme 清单，再决定挖不挖
- `android-security-audit` 一、密钥追踪专项需要**快速找到签名类/密钥常量位置**时（本技能负责定位，它负责还原算法与验证接口）
- 不确定某个 APK 值不值得投入全量还原成本，需要先 triage

**不适用**：加固壳脱壳（→ `apk-reversing`）、漏洞定级与验证（→ `android-security-audit`）、需要跨类数据流/完整工程视图的静态审计（→ 全量反编译产物 + `source-code-audit`）

---

## 一、环境安装与自检

**硬门槛：Python ≥ 3.11**（工具用了原子分组正则 `(?>(?:...))`，3.9/3.10 会直接报 `unknown extension ?>`）。唯一第三方依赖 `androguard`（本机实测 4.1.4）。

```bash
# 已装好（本机）：直接自检
ASC=/Users/apple/Desktop/武器库/5.逆向/ASC
$ASC/asc 2>&1 | head -5                    # 打印用法 = 环境正常
$ASC/asc_manifest <任意.apk> | head -3     # Manifest 解析 = androguard 正常

# 从零重建（换机/环境损坏时）
git clone --depth 1 https://github.com/MG1937/ASC $ASC
cd $ASC && python3.11 -m venv .venv && ./.venv/bin/pip install androguard==4.1.4 loguru
```

**自检三连**（开工前 10 秒确认）：

```bash
$ASC/asc findrefs <target.apk> string token | head -3      # 有无命中都要无报错
$ASC/asc_manifest <target.apk> | grep -c "uses-permission" # 权限条数 > 0 即解析成功
```

---

## 二、工具速查

### 2.1 四个核心命令

```bash
ASC=/Users/apple/Desktop/武器库/5.逆向/ASC

# ① Manifest 秒读（组件面/权限/scheme 清单，零反编译）
$ASC/asc_manifest <apk>                                  # 约 0.3s
$ASC/asc_manifest <apk> | grep -B2 -A6 'exported="true"' # 导出组件
$ASC/asc_manifest <apk> | grep 'android:scheme'          # Deep Link scheme

# ② 全局交叉引用搜索（findrefs，四个维度）
$ASC/asc findrefs <apk> string <关键词>                   # 模糊搜字符串使用点
$ASC/asc findrefs <apk> type com.x.Y                     # 模糊搜类型引用点
$ASC/asc findrefs <apk> method <方法名> [--class <类>] [--fuzzy-class]
$ASC/asc findrefs <apk> field <字段名> [--class <类>] [--fuzzy-class]
$ASC/asc findrefs <apk> string appkey -o refs.txt        # 输出存盘（便于通读）
$ASC/asc findrefs --debug <apk> string token             # 耗时统计（--debug 必须在子命令前）

# ③ 按需反编译单个类（getclass）
$ASC/asc getclass <apk> Lcom/x/Y; -o Y.java              # Dalvik 格式
$ASC/asc getclass <apk> com.x.Y -o Y.java                # 点分格式（自动转换）
```

### 2.2 输出格式与语义（Agent 必读）

**findrefs 输出**（一行一个命中点）：

```
classes3.dex | LA8/m$a;->b | matched=(appkey)
   ↑ dex 名    ↑ 类->方法     ↑ 命中内容
```

- **搜的是"引用点"不是"定义"**：`findrefs method onCreate` 返回的是**调用了 onCreate 的位置**。看某个方法/字段**自身的实现**要配合 `getclass`。
- **命中按"调用方方法"去重聚合**：同一方法内多次调用同名 API 只输出一行，多个命中合并显示在 `matched=(a; b; c)` 里。所以本技能命中数**少于** `grep` 的行计数（实测同一 4.4MB 包：`exec` 39 vs 95、`startActivity` 18 vs 23、`getStringExtra` 4 vs 9）——**不是漏检，是聚合**；`grep` 这边还会同时匹配方法定义、JADX 注释与子串，噪音更大。两者数字不可直接对比。
- `string` / `type` 是**模糊匹配**（substring）；`method` / `field` 的 `--class` 默认精确匹配，加 `--fuzzy-class` 才模糊（如 `--class miui --fuzzy-class` 匹配所有 miui 命名空间）。
- 一个关键词常命中几十~几百行，**用 `-o` 存盘后 grep/分页通读**，不要一次性打印刷屏。
- 搜索**跨全部 dex 分片**（classes.dex / classes2.dex / …），无需先合并。

| 命令 | 输出 | 耗时（实测） | 峰值内存 |
|---|---|---|---|
| `asc_manifest`（68MB 包） | 可读 XML 全量权限/组件 | ~0.3s | ~110MB |
| `findrefs string/type`（68MB） | 命中行列表 | ~0.32s | ~108MB |
| `findrefs string`（175MB） | 命中行列表 | ~0.33s | — |
| `getclass`（单类） | DAD 风格 Java | ~0.12s | — |
| **对照**：JADX 全量反编译（68MB） | 17613 类 → 12677 java + 1629 res XML | **39.2s** | **6.96GB** |
| **对照**：JADX 全量反编译（4.4MB） | 2753 类 | 5.87s | — |

> 同一 68MB 包上的对照实测：本技能 **0.34s / 108MB** vs JADX 全量 **39.2s / 6.96GB** —— 快约 **115 倍**、省约 **66 倍**内存。

### 2.3 输出质量边界（决定何时必须转全量反编译）

`getclass` 后端是 Androguard DAD：**寄存器级变量名（v0_2、p9）、无类型推断、控制流较朴素**。够做的事：读方法逻辑、看字符串常量、识别加密调用（`MessageDigest.getInstance("MD5")`、`Cipher.getInstance("AES/...")`）、看调用关系与参数来源。

**⚠️ 类型不可信（实测，最危险的边界）**：DAD 会给出**错误类型**。同一个类、同一个方法，两个工具的输出：

```java
// JADX 1.5.5（正确）
ByteBuffer outputBuffer = this.f2295b.getOutputBuffer(i3);

// ASC / DAD（错误：该方法真实返回 ByteBuffer，却被声明成 String）
String v0_1 = this.b.getOutputBuffer(p6);
```

因此本技能的输出**不可用于数据流/污染推理**（"这个参数可不可控、会不会流到危险点"），**也不适合作为报告取证截图**。它只用于快速读懂大致逻辑、认出加密调用与字符串常量——一旦要做可达性推理或写报告，必须换 JADX 产物。

**资源层为零**：本技能只有 Manifest 解析（借 androguard），`res/` 下的 `file_paths.xml`（FileProvider 路径暴露）、`network_security_config.xml`、`strings.xml`（硬编码密钥高发地）、layout（UI 注入点）**一律看不到**——同一 4.4MB 包 JADX 解出 **1629 个 res/ XML**。组件审计、Provider 审计必须走 `apk-reversing` 的 apktool/JADX 产物。

**做不到的搜索形态**：`findrefs` 查的是 DEX 引用表，**无法表达"同一行两个 API 共现"的模式**——`android-security-audit` Step 2 里的 `grep -rE "startActivity.*getParcelable"`（Intent 重定向）、`grep -rE "setTitle.*getIntent"`（弹窗欺骗）这类模式，本技能只能逐个 API 分别查再自己交叉。也没有项目级通读视图。

不够做的事：精读复杂混淆逻辑、跨类数据流追踪、函数调用图、写报告级源码引用、资源层分析、共现模式搜索。**当需要这些时，转 `apk-reversing` 全量反编译用 JADX 读。**

---

## 三、标准工作流（快筛循环）

### Step 0：壳预检（30 秒，决定要不要转 apk-reversing）

```bash
# 看 lib/ 壳特征 so 与入口类
unzip -l <apk> | grep -iE "libshella|libjiagu|libSecShell|libexec|libtprt|com/stub"
$ASC/asc_manifest <apk> | grep -oE 'android:name="[A-Za-z0-9._]*Application[A-Za-z0-9._]*"'
$ASC/asc getclass <apk> <上一步的入口类> | head -30     # 是 stub 包装类 = 有壳
```

- **判定**：`lib/` 有壳 so、或入口类是 stub（`com.stub.StubApp` 等）、或 getclass 读到的 Application 是空壳 → **有壳，转 `apk-reversing` 脱壳**，脱壳产物再回到本技能快筛
- **无壳** → 直接进 Step 1，全程不需要全量反编译

### Step 1：Manifest 秒读（攻击面清单）

```bash
$ASC/asc_manifest <apk> > /tmp/manifest.xml
grep -B3 -A8 'exported="true"' /tmp/manifest.xml                     # 导出组件
grep -oE 'android:scheme="[^"]+"' /tmp/manifest.xml | sort -u        # Deep Link scheme
grep -oE 'android:name="android.permission.[^"]+"' /tmp/manifest.xml | sort -u  # 权限面
grep -iE 'android:process|sharedUserId|allowBackup|debuggable' /tmp/manifest.xml
```

产出：导出 Activity/Service/Receiver/Provider 清单 + scheme 清单 → **交棒 `android-security-audit` 二、静态分析**（组件安全部分）；本技能继续做密钥/接口定位。

### Step 2：关键词矩阵搜索（核心，一波流）

按组批量搜索，每组存盘通读：

```bash
ASC=/Users/apple/Desktop/武器库/5.逆向/ASC
APK=<target.apk>

# A 组｜凭证与密钥（最高价值）
for kw in appkey appKey app_secret appSecret secret_key access_key api_key ak_sk client_secret; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

# B 组｜签名与加密
for kw in sign signature signKey md5 sha1 sha256 hmac RSA AES PUBLIC.CRYPTO_PUBLIC; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

# C 组｜网络与接口（拿出接口域名/路径）
for kw in https:// http:// /api/ /v1/ /v2/ Authorization Bearer Cookie userToken; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw -o /tmp/refs_$(echo $kw|tr -d '/:.').txt
done

# D 组｜后门与调试（隐藏功能）
for kw in debug test internal backdoor admin bypass __dev__ mock; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

# E 组｜云服务与第三方（appid/key 泄露高发区）
for kw in appId appid AK SK push_key map_key accessKeyId endpoint bucket; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done
```

**关键技巧**：
- 命中收敛不了（如 `secret` 几百条）→ 换更长的特征串（`app_secret`、`client_secret`）或加限定词（`secret_key`）
- 关注**方法名异常**的命中：`LA8/m$a;->b` 这种混淆单字母类 + 命中 `appkey` = 签名工具类，直接进 Step 3
- **URL 类命中最有价值**：拿到接口域名/路径清单后，`recon-js-analysis` 测绘资产、`api-protocol-security` 打接口
- 命中即存档：`-o /tmp/refs_xxx.txt`，后续可反复通读，避免重复搜索

### Step 3：按需读实现（getclass）

```bash
# 对 Step 2 命中的类逐个读（一个类约 0.1s，可放心多读）
$ASC/asc getclass $APK LA8/m\$a\; -o /tmp/A8_m_a.java
```

读的时候盯四件事：
1. **加密调用**：`MessageDigest.getInstance("MD5"/"SHA-1")`、`Cipher.getInstance("AES/ECB"...)`、`java.security.Signature`、`KeyGenerator`
2. **拼接顺序**：`md5(appId + appKey + ts)` 这类参数拼接 → 直接决定能否 Python 重写
3. **常量来源**：密钥是硬编码字符串常量、还是从 `Build`/`SharedPreferences`/`native` 取（后者要转 SO 层追踪）
4. **参数来源**：是否为外部可控（Intent extra / Deep Link 参数 / 网络响应）

> ⚠️ 第 4 点要克制：DAD 会给出错误类型（见 2.3），**别拿这里的类型声明确认"这个值是什么、从哪来"**。此步只建立"疑似外部可控"的假设，确认可达性与数据流必须用 JADX 产物复核。

⚠️ **shell 转义**：Dalvik 类名含 `$`（内部类）时必须转义或加引号——`LA8/m\$a\;` 或 `'LA8/m$a;'`。

### Step 4：追引用链（找调用方与数据流）

```bash
# 谁调用了这个签名方法 → 定位业务接口调用点
$ASC/asc findrefs $APK method <方法名> --class <类> --fuzzy-class

# 谁使用了这个密钥字段 → 定位全部加密场景
$ASC/asc findrefs $APK field <字段名>

# 哪些地方引用了这个类（如 Retrofit 接口定义）→ 定位完整 API 面
$ASC/asc findrefs $APK type com.x.net.ApiService
```

沿"密钥常量 → 签名方法 → 业务接口调用"三跳走完，就能拼出**完整攻击链**。每一跳都记录 `dex | 类->方法`，这是后续复现与报告的证据。

### Step 5：出链归档与交棒

```
1. 线索写入 CLUEBOARD：hunts/<目标>/CLUEBOARD.md（调用 hunt-clueboard）
   - 记录: APK 路径与版本、包名、命中类/方法、命中关键词、dex 分片名
   - 否定证据也要写（"搜 appkey 无硬编码命中，疑为动态下发"）
2. 拿到「密钥 + 签名算法 + 接口」→ 交棒 android-security-audit 一、密钥追踪专项：
   - Python 重写签名 → curl 未授权调接口 → 拉真实业务数据 = 成洞
3. 拿到「接口域名清单」→ 交棒 recon-js-analysis（资产测绘）+ api-protocol-security（接口测试）
4. 命中「命令执行/文件读取/JSBridge」类字符串与类 → 交棒 android-security-audit 二/三 深挖验证
5. 需要精读混淆逻辑或跨类数据流 → 交棒 apk-reversing 全量反编译
```

---

## 四、分工矩阵（什么时候用哪个）

| 场景 | 用什么 | 原因 |
|---|---|---|
| 大包想知道有没有硬编码密钥/接口 | **本技能** `findrefs` | 秒级，零预处理 |
| 只想看组件面/权限/scheme | **本技能** `asc_manifest` | 0.3s 出全量 XML |
| 已知类名，想看实现 | **本技能** `getclass` | 0.1s，够读逻辑 |
| **小包（<20MB）任何环节** | **直接 JADX 全量** | 4.4MB 包 JADX 仅 5.87s，本技能省不下时间，白折腾 |
| 加固壳（stub/壳 so） | `apk-reversing` | 真代码不在 DEX，本技能搜不到 |
| 脱壳后的 dex 要检索 | **本技能**（打包成 zip 后） | 见"坑"第 2 条 |
| 混淆严重、需跨类数据流/调用图 | `apk-reversing` 全量反编译 + JADX | DAD 类型不可信，推理会歪 |
| **要查 res/（file_paths.xml、network_security_config、strings.xml）** | `apk-reversing` apktool/JADX | 本技能资源层为零 |
| **共现模式搜索**（`startActivity.*getParcelable` 等） | JADX 产物 + `grep -rE` | 引用表查询无法表达 |
| **报告取证截图** | `apk-reversing` JADX 产物 | DAD 输出寄存器级 + 类型错误，不能当证据 |
| 组件安全深挖 + 动态验证 + PoC | `android-security-audit` | 本技能只定位不验证 |
| 漏洞定级与 DOCX 成稿 | `report` | — |

**成本对比（同一 68MB 包实测）**：本技能 `findrefs` **0.34s / 108MB**；JADX 全量反编译 **39.2s / 6.96GB**（17613 个类）——快约 **115 倍**、省约 **66 倍**内存。本技能全流程（Manifest + 5 组关键词 + 读 10 个类）通常 **1 分钟内**跑完。

**但这不是"替代 JADX"**：本技能回答**"在哪里"**，JADX 回答**"是什么、怎么流、能不能用"**。实用阈值——

- **小包（<20MB）**：直接 JADX 全量，快筛没有收益（4.4MB 只要 5.87s）
- **大包（>100MB）**：先本技能秒级定位，命中后再让 JADX 只精读相关部分——68MB 就要 39s + 7GB，175MB 级极易 OOM
- **任何需要资源层/数据流/报告取证的环节**：无论包大小都回 `apk-reversing` 全量产物

---

## 五、边界与坑（实测记录）

1. **Python ≥ 3.11 硬门槛**：报 `unknown extension ?>` 就是 Python 版本不够（原子分组正则），换 3.11+ 重建 venv。
2. **裸 `.dex` 不能直接喂**：报 `EOCD not found`（只认 zip/APK 容器）。脱壳产物（frida-dexdump 出的 dex）先打包：
   ```bash
   cd <dex目录> && zip -q dumped.zip classes*.dex && cp dumped.zip dumped.zip.apk
   $ASC/asc findrefs dumped.zip.apk string appkey
   ```
3. **split APK / XAPK**：工具按 zip 内的 `.dex` 条目扫描，`split_config.*.apk` 这类分片需先用 apkeditor 合并，或用 base.apk（业务 dex 通常在 base）。
4. **加固壳包搜不到东西是正常现象**：DEX 里只有壳的 stub 类，命中无意义 → 转 `apk-reversing` 脱壳，不要误判为"没有密钥"。
5. **`--debug` 位置**：属于 findrefs 层，必须写在子命令前（`findrefs --debug <apk> string kw`），写在末尾会报 `unrecognized arguments`。
6. **`$` 转义**：Dalvik 内部类名 `LA8/m$a;` 在 shell 里要转义或用单引号包裹。
7. **findrefs 搜引用点非定义**（见 2.2），别把它当"方法列表"用。
8. **别猜类名**：R8 会重命名/裁剪类，猜 `com.x.y.R` 这类名字大概率报 `Class ... not found in APK.`（报错本身是正常信号）。正确姿势永远是 **findrefs 反查命中类名 → 再 getclass**；类名不存在即说明该类被裁剪（常是资源类/构建期类）。
9. **无 LICENSE，不可分发**：详见「出处声明」。工具更新用 `cd $ASC && git pull`（本机保留 .git）。
10. **GUI 用不上**：工具自带 tkinter GUI，Agent 工作流一律走 CLI，不要启动 GUI。

---

## 六、证据纪律（防幻觉，强制）

- **命中 ≠ 漏洞**：`findrefs` 返回的字符串命中只是**入口线索**，必须 `getclass` 读到真实代码，才能说"这是密钥/这是签名函数"。
- **⚠️ `getclass` 只能确认"逻辑与常量"，不能确认"类型与可达性"**：DAD 输出有类型错误（见 2.3 的 `ByteBuffer`→`String` 实证）。所以用本技能读加密调用、字符串常量、分支逻辑是可靠的；**一旦要推理"这个参数可不可控、会不会流到危险点"，必须换 JADX 产物**，不要拿 DAD 的类型下结论。
- **输出不可直接作报告证据**：报告里的代码截图与行号引用一律取自 `apk-reversing` 的 JADX 产物；本技能的行只用于线索板上的"定位记录"。
- **不编造类名、方法名、dex 名**：报告与线索板里写的每个 `dex | 类->方法` 都必须来自实际命令输出，禁止推测补全。
- **否定证据同样要写**：搜过什么关键词、没命中，是判断"密钥是否动态下发"的关键依据，必须如实入板。
- **区分静态位置与可执行性**：类里存在 MD5 调用 ≠ 该路径被调用；要沿 Step 4 的引用链确认可达，或交棒 `android-security-audit` 动态验证。
- **不越权定级**：本技能只输出"定位结论 + 证据行"，漏洞等级由 `android-security-audit` 的验证门与 `report` 的分层验证门裁定。

---

## 七、验证要点

- [ ] 自检三连通过（`asc` 打印用法、`asc_manifest` 出权限条数、`findrefs` 无报错）
- [ ] 壳预检已做：无壳 or 已脱壳（有壳时确认已转 `apk-reversing`，不硬编结论）
- [ ] 关键词矩阵 A~E 五组**全部跑过**，未命中的组也在线索板记录
- [ ] 每个"发现"都有 `getclass` 读到的代码佐证（方法名 + 关键调用行）
- [ ] 引用链至少追一跳（谁调用/谁引用），不只停在命中行
- [ ] 线索（含否定证据）已写入 `hunts/<目标>/CLUEBOARD.md`
- [ ] 命中密钥/接口/命令执行点**已交棒**对应技能，未在本技能内直接定级

---

## 联动

- 上游输入：APK 获取与壳识别/脱壳 → `apk-reversing`（有壳必走）
- 下游挖洞：密钥追踪→未授权接口、组件安全深挖、动态验证 → `android-security-audit`
- 接口域名清单 → `recon-js-analysis`（资产测绘）、`api-protocol-security`（API 测试）
- 云服务凭证（AK/SK/bucket）→ `cloud-infra-supply-chain`
- SO 层密钥（native 取密钥时）→ `apk-reversing` 五、Ghidra 路径 + `android-security-audit` 1.3
- 跨轮线索留存 → `hunt-clueboard`（`hunts/<目标>/CLUEBOARD.md`）
- 正式报告 → `report`
