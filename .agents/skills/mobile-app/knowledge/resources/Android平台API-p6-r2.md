# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 6 · part 2

> 分段 2/2。索引见 `Android平台API-p6.md`。

//If attackers can inject script into a WebView, they could access local resources. This can be prevented by disabling local file system access, which is enabled by default. You can use the Android WebSettings class to disable local file system access via the public method `setAllowFileAccess`.
webView.getSettings().setAllowFileAccess(false);

webView.getSettings().setAllowFileAccessFromFileURLs(false);

webView.getSettings().setAllowUniversalAccessFromFileURLs(false);

webView.getSettings().setAllowContentAccess(false);
```

- 创建一个列表，定义允许加载的本地和远程网页和协议。
- 创建本地 HTML/JavaScript 文件的校验和，并在应用程序启动时检查它们。缩小 JavaScript 文件以使其更难阅读。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_6)

要确定协议处理程序的使用情况，请寻找在您使用该应用程序时触发电话呼叫的方法以及从文件系统访问文件的方法。

## 确定是否通过 WebView 公开 Java 对象 (MSTG-PLATFORM-7)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#determining-whether-java-objects-are-exposed-through-webviews-mstg-platform-7)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_8)

Android 为在 WebView 中执行的 JavaScript 提供了一种调用和使用 Android 应用程序（注释为`@JavascriptInterface`）的原生功能的[`addJavascriptInterface`](https://developer.android.com/reference/android/webkit/WebView.html#addJavascriptInterface(java.lang.Object, java.lang.String))方法。这称为*WebView JavaScript 桥*或*Native桥*。

请注意，**当您使用 时`addJavascriptInterface`，您是在明确授予该 WebView 中加载的所有页面访问已注册的 JavaScript 接口对象的权限**。这意味着，如果用户在您的应用程序或域之外导航，所有其他外部页面也将可以访问那些 JavaScript 接口对象，如果通过这些接口暴露任何敏感数据，这可能会带来潜在的安全风险。

> 警告：特别注意针对 Android 4.2（API 级别 17）以下 Android 版本的应用程序，因为它们在执行时[容易受到缺陷](https://labs.mwrinfosecurity.com/blog/webview-addjavascriptinterface-remote-code-execution/)`addJavascriptInterface`的攻击：一种滥用反射的攻击，当恶意 JavaScript 注入到网络视图。这是因为默认情况下可以访问所有 Java Object 方法（而不仅仅是那些注释的方法）。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_7)

您需要确定该方法是否`addJavascriptInterface`被使用，如何使用，以及攻击者是否可以注入恶意 JavaScript。

以下示例显示了如何`addJavascriptInterface`在 WebView 中桥接 Java 对象和 JavaScript：

```
WebView webview = new WebView(this);
WebSettings webSettings = webview.getSettings();
webSettings.setJavaScriptEnabled(true);

MSTG_ENV_008_JS_Interface jsInterface = new MSTG_ENV_008_JS_Interface(this);

myWebView.addJavascriptInterface(jsInterface, "Android");
myWebView.loadURL("http://example.com/file.html");
setContentView(myWebView);
```

在 Android 4.2（API 级别 17）及更高版本中，注解`@JavascriptInterface`明确允许 JavaScript 访问 Java 方法。

```
public class MSTG_ENV_008_JS_Interface {

        Context mContext;

        /** Instantiate the interface and set the context */
        MSTG_ENV_005_JS_Interface(Context c) {
            mContext = c;
        }

        @JavascriptInterface
        public String returnString () {
            return "Secret String";
        }

        /** Show a toast from the web page */
        @JavascriptInterface
        public void showToast(String toast) {
            Toast.makeText(mContext, toast, Toast.LENGTH_SHORT).show();
        }
}
```

这是`returnString`从 JavaScript 调用方法的方法，字符串“Secret String”将存储在变量中`result`：

```
var result = window.Android.returnString();
```

通过访问 JavaScript 代码，例如通过存储的 XSS 或 MITM 攻击，攻击者可以直接调用暴露的 Java 方法。

如有`addJavascriptInterface`必要，请考虑以下事项：

- 只应允许 APK 提供的 JavaScript 使用桥接器，例如，通过验证每个桥接 Java 方法上的 URL（通过`WebView.getUrl`）。
- 不应从远程端点加载任何 JavaScript，例如，通过将页面导航保持在应用程序的域内并在默认浏览器（例如 Chrome、Firefox）上打开所有其他域。
- 如果出于遗留原因（例如，必须支持旧设备）有必要，请至少在应用程序的清单文件 ( `<uses-sdk android:minSdkVersion="17" />`) 中将最低 API 级别设置为 17。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_7)

应用程序的动态分析可以向您显示加载了哪些 HTML 或 JavaScript 文件以及存在哪些漏洞。利用该漏洞的过程从生成 JavaScript 负载并将其注入到应用程序请求的文件中开始。如果文件存储在外部存储中，则可以通过 MITM 攻击或直接修改文件来完成注入。整个过程可以通过 Drozer 和 weasel（MWR 的高级利用有效载荷）来完成，它们可以安装完整代理，将有限代理注入正在运行的进程或连接反向 shell 作为远程访问工具 (RAT)。

攻击的完整描述包含在[MWR 的博客文章中](https://labs.mwrinfosecurity.com/blog/webview-addjavascriptinterface-remote-code-execution/)。

## 测试对象持久性 (MSTG-PLATFORM-8)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-object-persistence-mstg-platform-8)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_9)

有几种方法可以在 Android 上持久化一个对象：

#### 对象序列化[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#object-serialization)

对象及其数据可以表示为字节序列。这是在 Java 中通过[对象序列化](https://developer.android.com/reference/java/io/Serializable.html)完成的。序列化本身并不安全。它只是一种二进制格式（或表示形式），用于将数据本地存储在 .ser 文件中。只要密钥安全存储，就可以对 HMAC 序列化数据进行加密和签名。反序列化一个对象需要一个与用于序列化该对象的类版本相同的类。更改类后，`ObjectInputStream`无法从旧的 .ser 文件创建对象。`Serializable`下面的示例显示了如何通过实现`Serializable`接口来创建类。

```
import java.io.Serializable;

public class Person implements Serializable {
  private String firstName;
  private String lastName;

  public Person(String firstName, String lastName) {
    this.firstName = firstName;
    this.lastName = lastName;
    }
  //..
