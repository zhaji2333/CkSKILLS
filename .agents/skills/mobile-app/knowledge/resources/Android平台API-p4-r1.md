# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 4 · part 1

> 分段 1/2。索引见 `Android平台API-p4.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 4

> 分段 4/8。索引见 `Android平台API.md`。

## 承接


如果意图过滤器列出了具有不同子域的多个主机，则每个域上都必须有一个有效的数字资产链接文件。例如，以下意向过滤器包括`www.example.com`和`mobile.example.com`作为接受的意向 URL 主机。

```
<application>
  <activity android:name=”MainActivity”>
    <intent-filter android:autoVerify="true">
      <action android:name="android.intent.action.VIEW" />
      <category android:name="android.intent.category.DEFAULT" />
      <category android:name="android.intent.category.BROWSABLE" />
      <data android:scheme="https" />
      <data android:scheme="https" />
      <data android:host="www.example.com" />
      <data android:host="mobile.example.com" />
    </intent-filter>
  </activity>
</application>
```

为了正确注册深层链接，必须在`https://www.example.com/.well-known/assetlinks.json`和上发布有效的数字资产链接文件`https://mobile.example.com/.well-known/assetlinks.json`。

**检查通配符：**

如果主机名包含通配符（例如`*.example.com`），您应该能够在根主机名处找到有效的数字资产链接文件：`https://example.com/.well-known/assetlinks.json`。

#### 检查处理程序方法[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-the-handler-method)

即使正确验证了深层链接，也应该仔细分析处理程序方法的逻辑。特别注意**用于传输数据的深层链接**（由用户或任何其他应用程序在外部控制）。

`<activity>`首先，从定义目标的 Android Manifest 元素中获取 Activity 的名称`<intent-filter>`并搜索 和 的[`getIntent`](https://developer.android.com/reference/android/content/Intent#getIntent(java.lang.String))用法[`getData`](https://developer.android.com/reference/android/content/Intent#getData())。在执行逆向工程时，这种定位这些方法的一般方法可以在大多数应用程序中使用，并且在尝试了解应用程序如何使用深度链接和处理任何外部提供的输入数据以及它是否可能受到任何类型的滥用时是关键。

以下示例是[使用 jadx 反编译](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#decompiling-java-code)的示例性 Kotlin 应用程序的片段。从[静态分析](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#enumerate-deep-links)我们知道它支持深度链接`deeplinkdemo://load.html/`作为`com.mstg.deeplinkdemo.WebViewActivity`.

```
// snippet edited for simplicity
public final class WebViewActivity extends AppCompatActivity {
    private ActivityWebViewBinding binding;

    public void onCreate(Bundle savedInstanceState) {
        Uri data = getIntent().getData();
        String html = data == null ? null : data.getQueryParameter("html");
        Uri data2 = getIntent().getData();
        String deeplink_url = data2 == null ? null : data2.getQueryParameter("url");
        View findViewById = findViewById(R.id.webView);
        if (findViewById != null) {
            WebView wv = (WebView) findViewById;
            wv.getSettings().setJavaScriptEnabled(true);
            if (deeplink_url != null) {
                wv.loadUrl(deeplink_url);
            ...
```

您可以简单地跟随`deeplink_url`String 变量并查看`wv.loadUrl`调用的结果。这意味着攻击者可以完全控制加载到 WebView 的 URL（如上所示启用了[JavaScript](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)。

同一个 WebView 也可能呈现攻击者控制的参数。在这种情况下，以下深层链接有效负载将在 WebView 的上下文中触发[反射跨站点脚本 (XSS) ：](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#cross-site-scripting-flaws-mstg-platform-2)

```
deeplinkdemo://load.html?attacker_controlled=<svg onload=alert(1)>
```

但是还有很多其他的可能性。请务必查看以下部分，以了解有关预期结果以及如何测试不同场景的更多信息：

- [“跨站点脚本缺陷 (MSTG-PLATFORM-2)”](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#cross-site-scripting-flaws-mstg-platform-2)。
- [“注入缺陷（MSTG-ARCH-2 和 MSTG-PLATFORM-2）”](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#injection-flaws-mstg-arch-2-and-mstg-platform-2)。
- [“测试对象持久性 (MSTG-PLATFORM-8)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-object-persistence-mstg-platform-8)。
- [“在 WebView 中测试 URL 加载 (MSTG-PLATFORM-2)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-url-loading-in-webviews-mstg-platform-2)
- [“在 WebView 中测试 JavaScript 执行 (MSTG-PLATFORM-5)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)
- [“测试 WebView 协议处理程序 (MSTG-PLATFORM-6)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webview-protocol-handlers-mstg-platform-6)

此外，我们建议搜索和阅读公开报告（搜索词：）`"deep link*"|"deeplink*" site:https://hackerone.com/reports/`。例如：

- [“[HackerOne#1372667\] 能够从深层链接窃取不记名令牌”](https://hackerone.com/reports/1372667)
- [“[HackerOne#401793\] 不安全的深层链接导致敏感信息泄露”](https://hackerone.com/reports/401793)
- [“[HackerOne#583987\] Android 应用深层链接在后续操作中导致 CSRF”](https://hackerone.com/reports/583987)
- [“[HackerOne#637194\] 在 Android 应用程序中可以绕过生物识别安全功能”](https://hackerone.com/reports/637194)
- [“[HackerOne#341908\] XSS 通过直接消息深度链接”](https://hackerone.com/reports/341908)

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_3)

在这里，您将使用来自静态分析的深层链接列表来迭代和确定每个处理程序方法和处理的数据（如果有）。您将首先启动[Frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#frida)Hook，然后开始调用深层链接。

以下示例假定目标应用程序接受此深层链接：`deeplinkdemo://load.html`。但是，我们还不知道相应的处理程序方法，也不知道它可能接受的参数。

**[第一步] Frida Hooking：**

您可以使用[Frida CodeShare中的脚本](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#frida-codeshare)[“Android Deep Link Observer”](https://codeshare.frida.re/@leolashkevych/android-deep-link-observer/)来监控所有触发对. 您还可以使用该脚本作为基础，根据手头的用例包含您自己的修改。在这种情况下，我们在脚本中[包含堆栈跟踪](https://github.com/FrenchYeti/frida-trick/blob/master/README.md)，因为我们对调用.`Intent.getData``Intent.getData`

**[步骤 2] 调用深层链接：**

[现在，您可以使用adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)和[活动管理器 (am)](https://developer.android.com/training/app-links/deep-linking#testing-filters)调用任何深层链接，这将在 Android 设备内发送意图。例如：

```
adb shell am start -W -a android.intent.action.VIEW -d "deeplinkdemo://load.html/?message=ok#part1"

Starting: Intent { act=android.intent.action.VIEW dat=deeplinkdemo://load.html/?message=ok }
Status: ok
LaunchState: WARM
Activity: com.mstg.deeplinkdemo/.WebViewActivity
TotalTime: 210
WaitTime: 217
Complete
```

> 这可能会在使用“http/https”架构时或其他已安装的应用程序支持相同的自定义 URL 架构时触发消歧对话框。您可以包含包名称以使其成为明确的意图。

此调用将记录以下内容：

```
[*] Intent.getData() was called
[*] Activity: com.mstg.deeplinkdemo.WebViewActivity
[*] Action: android.intent.action.VIEW

[*] Data
- Scheme: deeplinkdemo://
- Host: /load.html
- Params: message=ok
- Fragment: part1

[*] Stacktrace:

android.content.Intent.getData(Intent.java)
com.mstg.deeplinkdemo.WebViewActivity.onCreate(WebViewActivity.kt)
android.app.Activity.performCreate(Activity.java)
...
com.android.internal.os.ZygoteInit.main(ZygoteInit.java)
```

在这种情况下，我们制作了包含任意参数 ( `?message=ok`) 和片段 ( `#part1`) 的深层链接。我们仍然不知道它们是否被使用。上面的信息揭示了您现在可以用来对应用程序进行逆向工程的有用信息。请参阅[“检查处理程序方法”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-the-handler-method)部分以了解您应该考虑的事项。

- 文件：`WebViewActivity.kt`
- 班级：`com.mstg.deeplinkdemo.WebViewActivity`
- 方法：`onCreate`

> 有时您甚至可以利用您知道与目标应用程序交互的其他应用程序。您可以对应用程序进行反向工程（例如，提取所有字符串并过滤那些包含目标深层链接的字符串，`deeplinkdemo:///load.html`在之前的案例中），或者将它们用作触发器，同时如前所述Hook应用程序。

## 通过 IPC 测试敏感功能暴露 (MSTG-PLATFORM-4)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-sensitive-functionality-exposure-through-ipc-mstg-platform-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_5)

在移动应用程序的实现过程中，开发人员可能会应用传统的 IPC 技术（例如使用共享文件或网络套接字）。应该使用移动应用平台提供的IPC系统功能，因为它比传统技术成熟得多。在没有考虑安全性的情况下使用 IPC 机制可能会导致应用程序泄漏或暴露敏感数据。

以下是可能暴露敏感数据的 Android IPC 机制列表：

- [粘合剂](https://developer.android.com/reference/android/os/Binder.html)
- [服务](https://developer.android.com/guide/components/services.html)
- [绑定服务](https://developer.android.com/guide/components/bound-services.html)
- [AIDL](https://developer.android.com/guide/components/aidl.html)
- [意图](https://developer.android.com/reference/android/content/Intent.html)
- [Content Provider(内容提供者)](https://developer.android.com/reference/android/content/ContentProvider.html)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_4)

