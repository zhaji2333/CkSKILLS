# 二、静态分析 · part 1 · part 1

> 分段 1/2。索引见 `android-security-audit-06-二、静态分析-r1.md`。

# 二、静态分析 · part 1

> 分段 1/2。索引见 `android-security-audit-06-二、静态分析.md`。

# 二、静态分析

> 来源：CkSKILLS v1 `android-security-audit` §二、静态分析（迁移至 v2 知识块）

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
adb shell am start -n com.victim/.ExportedActivity --es intent "com.victim/.PrivateActivity"
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
find /tmp/jadx_out/sources -name "*.aidl"
```

