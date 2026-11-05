# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 3 · part 2

> 分段 2/2。索引见 `Android平台API-p3.md`。

- 在 Android 12（API 级别 31）之前，如果应用程序有任何[不可验证的链接](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)，可能会导致系统无法验证该应用程序的所有 Android 应用程序链接。
- 从 Android 12（API 级别 31）开始，应用程序受益于[减少的攻击面](https://developer.android.com/training/app-links/deep-linking)。通用网络意图解析为用户的默认浏览器应用程序，除非目标应用程序已获准用于该网络意图中包含的特定域。

必须枚举和验证所有深层链接以确保正确的网站关联。他们执行的操作必须经过良好测试，尤其是所有输入数据，这些数据应被视为不可信，因此应始终进行验证。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_3)

#### 枚举深层链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#enumerate-deep-links)

**检查 Android 清单：**

[您可以通过使用 apktool 解码应用程序](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)并检查 Android Manifest 文件以查找[``元素](https://developer.android.com/guide/components/intents-filters.html#DataTest)来轻松确定是否定义了深层链接（有或没有自定义 URL 方案）。

- **自定义 Url 方案**：以下示例指定了一个深度链接，其中包含名为 的自定义 URL 方案`myapp://`。

```
<activity android:name=".MyUriActivity">
  <intent-filter>
      <action android:name="android.intent.action.VIEW" />
      <category android:name="android.intent.category.DEFAULT" />
      <category android:name="android.intent.category.BROWSABLE" />
      <data android:scheme="myapp" android:host="path" />
  </intent-filter>
</activity>
```

- **深层链接**：以下示例指定了一个同时使用`http://`和`https://`方案的深层链接，以及将激活它的主机和路径（在本例中，完整的 URL 为`https://www.myapp.com/my/app/path`）：

```
<intent-filter>
  ...
  <data android:scheme="http" android:host="www.myapp.com" android:path="/my/app/path" />
  <data android:scheme="https" android:host="www.myapp.com" android:path="/my/app/path" />
</intent-filter>
```

- **App Links**：如果`<intent-filter>`包含该标志`android:autoVerify="true"`，这会导致 Android 系统接触声明`android:host`以尝试访问[Digital Asset Links 文件](https://developers.google.com/digital-asset-links/v1/getting-started)以[验证 App Links](https://developer.android.com/training/app-links/verify-site-associations)。**只有验证成功才能将深度链接视为 App Link。**

```
<intent-filter android:autoVerify="true">
```

列出深层链接时，请记住，`<data>`同一元素中的元素`<intent-filter>`实际上合并在一起，以说明其组合属性的所有变化。

```
<intent-filter>
  ...
  <data android:scheme="https" android:host="www.example.com" />
  <data android:scheme="app" android:host="open.my.app" />
</intent-filter>
```

看起来这似乎只支持`https://www.example.com`和`app://open.my.app`。但是，它实际上支持：

- `https://www.example.com`
- `app://open.my.app`
- `app://www.example.com`
- `https://open.my.app`

**使用 Dumpsys：**

使用[adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)运行以下将显示所有方案的命令：

```
adb shell dumpsys package com.example.package
```

**使用Android“App Link Verification”测试仪：**

使用[Android“App Link Verification”Tester](https://github.com/inesmartins/Android-App-Link-Verification-Tester)脚本列出所有深层链接 ( `list-all`) 或仅列出应用程序链接 ( `list-applinks`)：

```
python3 deeplink_analyser.py -op list-all -apk ~/Downloads/example.apk

.MainActivity

app://open.my.app
app://www.example.com
https://open.my.app
https://www.example.com
```

#### 检查正确的网站关联[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-for-correct-website-association)

即使深层链接包含该`android:autoVerify="true"`属性，它们也必须经过*实际*验证才能被视为应用链接。您应该测试任何可能阻止完整验证的错误配置。

##### 自动验证[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#automatic-verification)

使用[Android“App Link Verification”Tester](https://github.com/inesmartins/Android-App-Link-Verification-Tester)脚本获取所有应用程序链接的验证状态 ( `verify-applinks`)。[请在此处](https://github.com/inesmartins/Android-App-Link-Verification-Tester#use-an-apk-to-check-for-dals-for-all-app-links)查看示例。

**仅适用于 Android 12（API 级别 31）或更高版本：**

无论应用程序是否针对 Android 12（API 级别 31），您都可以使用[adb来测试验证逻辑。](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)此功能允许您：

- [手动调用验证过程](https://developer.android.com/training/app-links/verify-site-associations#manual-verification)。
- [在您的设备上重置目标应用的 Android 应用链接的状态](https://developer.android.com/training/app-links/verify-site-associations#reset-state)。
- [调用域验证过程](https://developer.android.com/training/app-links/verify-site-associations#invoke-domain-verification)。

您还可以[查看验证结果](https://developer.android.com/training/app-links/verify-site-associations#review-results)。例如：

```
adb shell pm get-app-links com.example.package

com.example.package:
    ID: 01234567-89ab-cdef-0123-456789abcdef
    Signatures: [***]
    Domain verification state:
      example.com: verified
      sub.example.com: legacy_failure
      example.net: verified
      example.org: 1026
```

> `adb shell dumpsys package com.example.package`通过运行（仅适用于 Android 12（API 级别 31）或更高版本）可以找到相同的信息。

##### 人工验证[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#manual-verification)

本节详细介绍了验证过程失败或未实际触发的几个（可能有很多）原因。请参阅[Android 开发人员文档](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)和白皮书[“衡量 Android 移动深度链接的不安全性”](https://people.cs.vt.edu/gangwang/deep17.pdf)中的更多信息。

**检查[数字资产链接文件](https://developers.google.com/digital-asset-links/v1/getting-started)：**

- 检查**丢失**的数字资产链接文件：
- 尝试在域的`/.well-known/`路径中找到它。例子：`https://www.example.com/.well-known/assetlinks.json`
- 或尝试`https://digitalassetlinks.googleapis.com/v1/statements:list?source.web.site=www.example.com`
- 检查**通过 HTTP**提供的有效数字资产链接文件。
- 检查通过 HTTPS 提供的**无效**数字资产链接文件。例如：
- 该文件包含无效的 JSON。
- 该文件不包含目标应用程序的包。

**检查重定向：**

为了增强应用程序的安全性，如果服务器设置了诸如to或to之类的重定向，系统[不会验证应用程序的任何 Android 应用程序链接](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)。`http://example.com``https://example.com``example.com``www.example.com`

**检查子域：**
