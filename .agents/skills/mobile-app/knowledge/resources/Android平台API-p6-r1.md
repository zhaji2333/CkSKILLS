# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 6 · part 1

> 分段 1/2。索引见 `Android平台API-p6.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 6

> 分段 6/8。索引见 `Android平台API.md`。

## 承接

        String newpass = intent.getStringExtra("newpass");
        if (phn != null) {
            try {
                SharedPreferences settings = context.getSharedPreferences("mySharedPreferences", 1);
                this.usernameBase64ByteString = new String(Base64.decode(settings.getString("EncryptedUsername", (String) null), 0), "UTF-8");
                String decryptedPassword = new CryptoClass().aesDeccryptedString(settings.getString("superSecurePassword", (String) null));
                String textPhoneno = phn.toString();
                String textMessage = "Updated Password from: " + decryptedPassword + " to: " + newpass;
                SmsManager smsManager = SmsManager.getDefault();
                System.out.println("For the changepassword - phonenumber: " + textPhoneno + " password is: " + textMessage);
                smsManager.sendTextMessage(textPhoneno, (String) null, textMessage, (PendingIntent) null, (PendingIntent) null);
            } catch (Exception e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("Phone number is null");
        }
    }
}
```

正如您在源代码中所见，此广播接收器需要两个名为`phonenumber`和的参数`newpass`。有了这些信息，您现在可以尝试通过使用自定义值向它发送事件来利用这个广播接收器：

```
# Send an event with the following properties:
# Action is set to "theBroadcast"
# Parameter "phonenumber" is set to the string "07123456789"
# Parameter "newpass" is set to the string "12345"
$ adb shell am broadcast -a theBroadcast --es phonenumber "07123456789" --es newpass "12345"
Broadcasting: Intent { act=theBroadcast flg=0x400000 (has extras) }
Broadcast completed: result=0
```

这会生成以下 SMS：

```
Updated Password from: SecretPassword@ to: 12345
```

##### 嗅探意图[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#sniffing-intents)

如果 Android 应用程序在未设置所需权限或指定目标包的情况下广播意图，则该意图可以被设备上运行的任何应用程序监视。

要注册广播接收器以嗅探意图，请使用 Drozer 模块`app.broadcast.sniff`并使用参数指定要监视的操作`--action`：

```
dz> run app.broadcast.sniff  --action theBroadcast
[*] Broadcast receiver registered to sniff matching intents
[*] Output is updated once a second. Press Control+C to exit.

Action: theBroadcast
Raw: Intent { act=theBroadcast flg=0x10 (has extras) }
Extra: phonenumber=07123456789 (java.lang.String)
Extra: newpass=12345 (java.lang.String)`
```

您还可以使用以下命令来嗅探意图。但是不会显示extras传递的内容：

```
$ adb shell dumpsys activity broadcasts | grep "theBroadcast"
BroadcastRecord{fc2f46f u0 theBroadcast} to user 0
Intent { act=theBroadcast flg=0x400010 (has extras) }
BroadcastRecord{7d4f24d u0 theBroadcast} to user 0
Intent { act=theBroadcast flg=0x400010 (has extras) }
45: act=theBroadcast flg=0x400010 (has extras)
46: act=theBroadcast flg=0x400010 (has extras)
121: act=theBroadcast flg=0x400010 (has extras)
144: act=theBroadcast flg=0x400010 (has extras)
```

## 在 WebView 中测试 JavaScript 执行 (MSTG-PLATFORM-5)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_6)

JavaScript 可以通过反射、存储或基于 DOM 的跨站点脚本 (XSS) 注入 Web 应用程序。移动应用程序在沙盒环境中执行，在Native实现时不存在此漏洞。然而，WebViews 可能是本地应用程序的一部分，以允许查看网页。每个应用程序都有自己的 WebView 缓存，不会与Native浏览器或其他应用程序共享。在 Android 上，WebViews 使用 WebKit 渲染引擎来显示网页，但页面被精简到最少的功能，例如，页面没有地址栏。如果 WebView 实现过于松散并允许使用 JavaScript，则 JavaScript 可用于攻击应用程序并获取对其数据的访问权限。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_5)

必须检查源代码以了解 WebView 类的用法和实现。要创建和使用 WebView，您必须创建 WebView 类的实例。

```
WebView webview = new WebView(this);
setContentView(webview);
webview.loadUrl("https://www.owasp.org/");
```

可以对 WebView 应用各种设置（激活/停用 JavaScript 就是一个例子）。WebView 默认禁用 JavaScript，必须明确启用。寻找[`setJavaScriptEnabled`](https://developer.android.com/reference/android/webkit/WebSettings#setJavaScriptEnabled(boolean))检查 JavaScript 激活的方法。

```
webview.getSettings().setJavaScriptEnabled(true);
```

这允许 WebView 解释 JavaScript。只有在必要时才应启用它以减少应用程序的攻击面。如果需要 JavaScript，您应该确保

- 与端点的通信始终依赖 HTTPS（或其他允许加密的协议）来保护 HTML 和 JavaScript 在传输过程中不被篡改。
- JavaScript 和 HTML 在本地加载，从应用程序数据目录内或仅从受信任的 Web 服务器加载。
- 用户无法通过基于用户提供的输入加载不同的资源来定义加载哪些源。

要删除所有 JavaScript 源代码和本地存储的数据，请[`clearCache`](https://developer.android.com/reference/android/webkit/WebView#clearCache(boolean))在应用关闭时清除 WebView 的缓存。

运行早于 Android 4.4（API 级别 19）的平台的设备使用存在多个安全问题的 WebKit 版本。作为解决方法，如果应用程序在这些设备上运行，则应用程序必须确认 WebView 对象[仅显示受信任的内容。](https://developer.android.com/training/articles/security-tips.html#WebView)

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_5)

动态分析取决于操作条件。有几种方法可以将 JavaScript 注入到应用程序的 WebView 中：

- 端点中存储的跨站点脚本漏洞；当用户导航到易受攻击的功能时，漏洞将被发送到移动应用程序的 WebView。
- 攻击者占据中间人 (MITM) 位置并通过注入 JavaScript 篡改响应。
- 恶意软件篡改由 WebView 加载的本地文件。

要解决这些攻击向量，请检查以下内容：

- 端点提供的所有功能都应该没有[存储的 XSS](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting)。
- 只有应用程序数据目录中的文件应该在 WebView 中呈现（请参阅测试用例“测试本地文件包含在 WebView 中”）。
- 必须根据最佳实践实施 HTTPS 通信以避免 MITM 攻击。这表示：
- 所有通信都通过 TLS 加密（请参阅测试用例“测试网络上未加密的敏感数据”），
- 证书被正确检查（参见测试用例“测试端点识别验证”），和/或
- 应该固定证书（请参阅“测试自定义证书存储和证书固定”）。

## 测试 WebView 协议处理程序 (MSTG-PLATFORM-6)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webview-protocol-handlers-mstg-platform-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_7)

Android URL 有几种默认[架构。](https://developer.android.com/guide/appendix/g-app-intents.html)它们可以在 WebView 中通过以下方式触发：

- http(s)://
- 文件：//
- 电话：//

WebView 可以从端点加载远程内容，但它们也可以从应用程序数据目录或外部存储加载本地内容。如果加载本地内容，用户不应该能够影响文件名或用于加载文件的路径，并且用户不应该能够编辑加载的文件。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_6)

检查 WebView 使用的源代码。以下[WebView 设置](https://developer.android.com/reference/android/webkit/WebSettings.html)控制资源访问：

- `setAllowContentAccess`: 内容 URL 访问允许 WebViews 从系统上安装的内容提供程序加载内容，默认情况下启用。
- `setAllowFileAccess`：启用和禁用 WebView 中的文件访问。默认值是`true`针对 Android 10（API 级别 29）及更低版本以及`false`Android 11（API 级别 30）及更高版本。请注意，这仅启用和禁用[文件系统访问](https://developer.android.com/reference/android/webkit/WebSettings.html#setAllowFileAccess(boolean))。资产和资源访问不受影响，可通过`file:///android_asset`和访问`file:///android_res`。
- `setAllowFileAccessFromFileURLs`：是否允许在文件方案 URL 的上下文中运行的 JavaScript 访问来自其他文件方案 URL 的内容。默认值适用`true`于 Android 4.0.3 - 4.0.4（API 级别 15）及更低版本以及`false`Android 4.1（API 级别 16）及更高版本。
- `setAllowUniversalAccessFromFileURLs`：是否允许在文件方案 URL 上下文中运行的 JavaScript 访问来自任何来源的内容。默认值适用`true`于 Android 4.0.3 - 4.0.4（API 级别 15）及更低版本以及`false`Android 4.1（API 级别 16）及更高版本。

如果激活了上述一种或多种方法，您应该确定这些方法是否真的是应用程序正常运行所必需的。

如果能识别到WebView实例，则通过该方法判断是否加载了本地文件[`loadURL`](https://developer.android.com/reference/android/webkit/WebView.html#loadUrl(java.lang.String))。

```
WebView = new WebView(this);
webView.loadUrl("file:///android_asset/filename.html");
```

必须验证加载 HTML 文件的位置。例如，如果文件是从外部存储加载的，则该文件对每个人都是可读可写的。这被认为是一种不好的做法。相反，该文件应放在应用程序的资产目录中。

```
webview.loadUrl("file:///" +
Environment.getExternalStorageDirectory().getPath() +
"filename.html");
```

应检查中指定的 URL`loadURL`是否有可操作的动态参数；他们的操作可能会导致包含本地文件。

使用以下[代码片段和最佳实践](https://github.com/nowsecure/secure-mobile-development/blob/master/en/android/webview-best-practices.md#remediation)来停用协议处理程序（如果适用）：

```
