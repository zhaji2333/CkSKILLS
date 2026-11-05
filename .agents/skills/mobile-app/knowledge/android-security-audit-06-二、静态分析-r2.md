# 二、静态分析 · part 2

> 分段 2/2。索引见 `android-security-audit-06-二、静态分析.md`。

grep -rn "shouldOverrideUrlLoading\|@JavascriptInterface\|jsbridge\|evaluateJavascript" /tmp/jadx_out/sources/
```

**自定义 JSBridge**
- `shouldOverrideUrlLoading()` 中对自定义 scheme（如 `jsbridge://`）的拦截处理；检查 method 白名单是否完整、param 是否有校验。
- 若 WebView 加载的 URL 可控（见 2.4），攻击者可通过注入 JS 调用 JSBridge 任意方法。

**验证步骤**
```bash
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

### 2.13 Fragment Injection 扩展

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

### 2.14 命令执行（可产出高危~严重）

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

### 2.15 权限/合规越权（HyperOS 重点）

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

### 2.16 推送/通知越权（业务逻辑重点）

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
