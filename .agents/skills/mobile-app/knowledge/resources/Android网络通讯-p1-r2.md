# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 1 · part 2

> 分段 2/2。索引见 `Android网络通讯-p1.md`。

以 Android 7.0（API 级别 24）或更高版本为目标的应用程序将使用**不信任任何用户提供的 CA 的默认网络安全配置**，从而通过引诱用户安装恶意 CA 来减少 MITM 攻击的可能性。

[使用 apktool 解码应用程序](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)并验证`targetSdkVersion`apktool.yml 中的 等于或高于`24`。

```
grep targetSdkVersion UnCrackable-Level3/apktool.yml
  targetSdkVersion: '28'
```

但是，即使`targetSdkVersion >=24`，开发人员也可以通过使用定义自定义信任锚的自定义网络安全配置来禁用默认保护，**强制应用程序信任用户提供的**CA。请参阅[“分析自定义信任锚”](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#analyzing-custom-trust-anchors)。

#### 分析自定义信任锚[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#analyzing-custom-trust-anchors)

搜索[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)文件并检查任何自`<trust-anchors>`定义定义`<certificates src="user">`（应避免）。

您应该仔细分析[条目的优先级](https://developer.android.com/training/articles/security-config#ConfigInheritance)：

- 如果未在`<domain-config>`条目或父项中设置值`<domain-config>`，则现有配置将基于`<base-config>`
- 如果未在此条目中定义，将使用[默认配置。](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#default-configurations)

查看针对 Android 9（API 级别 28）的应用的网络安全配置示例：

```
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        <domain includeSubdomains="false">owasp.org</domain>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </domain-config>
</network-security-config>
```

一些观察：

- 没有`<base-config>`，这意味着 Android 9（API 级别 28）或更高版本的[默认配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#default-configurations)将用于所有其他连接（`system`原则上只信任 CA）。
- 但是，它`<domain-config>`会覆盖默认配置，允许应用程序信任指定的(owasp.org)`system`和`user`CA。`<domain>`
- 这不会影响子域，因为`includeSubdomains="false"`.

综上所述，我们可以*将*上述网络安全配置翻译为：“应用程序信任 owasp.org 域的系统和用户 CA，不包括其子域。对于任何其他域，应用程序将仅信任系统 CA”。

#### 验证服务器证书[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#verifying-the-server-certificate)

`TrustManager`是一种验证在 Android 中建立可信连接所必需的条件的方法。此时应检查以下条件：

- 证书是否由受信任的 CA 签署？
- 证书是否过期？
- 证书是自签名的吗？

以下代码片段有时会在开发过程中使用，并且会接受任何证书，覆盖函数`checkClientTrusted`、`checkServerTrusted`和`getAcceptedIssuers`。应该避免这样的实现，如果有必要，应该将它们与生产构建明确分开，以避免内置的安全漏洞。

```
TrustManager[] trustAllCerts = new TrustManager[] {
    new X509TrustManager() {
        @Override
        public X509Certificate[] getAcceptedIssuers() {
            return new java.security.cert.X509Certificate[] {};
        }

        @Override
        public void checkClientTrusted(X509Certificate[] chain, String authType)
            throws CertificateException {
        }

        @Override
        public void checkServerTrusted(X509Certificate[] chain, String authType)
            throws CertificateException {
        }
    }
 };

// SSLContext context
context.init(null, trustAllCerts, new SecureRandom());
```

#### WebView 服务器证书验证[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#webview-server-certificate-verification)

有时应用程序使用 WebView 来呈现与应用程序关联的网站。基于 HTML/JavaScript 的框架就是如此，例如 Apache Cordova，它使用内部 WebView 进行应用程序交互。使用 WebView 时，移动浏览器会执行服务器证书验证。忽略 WebView 尝试连接到远程网站时发生的任何 TLS 错误是一种不好的做法。

以下代码将忽略 TLS 问题，就像提供给 WebView 的 WebViewClient 自定义实现一样：

```
WebView myWebView = (WebView) findViewById(R.id.webview);
myWebView.setWebViewClient(new WebViewClient(){
    @Override
    public void onReceivedSslError(WebView view, SslErrorHandler handler, SslError error) {
        //Ignore TLS certificate errors and instruct the WebViewClient to load the website
        handler.proceed();
    }
});
```

#### Apache Cordova 证书验证[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#apache-cordova-certificate-verification)

如果在应用程序清单中启用了标志，则 Apache Cordova 框架的内部 WebView 使用的实现将忽略方法中的[TLS 错误。](https://github.com/apache/cordova-android/blob/master/framework/src/org/apache/cordova/engine/SystemWebViewClient.java)因此，请确保该应用程序不可调试。请参阅测试用例“测试应用程序是否可调试”。`onReceivedSslError``android:debuggable`

#### 主机名验证[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#hostname-verification)

客户端 TLS 实现中的另一个安全缺陷是缺乏主机名验证。开发环境通常使用内部地址而不是有效域名，因此开发人员经常禁用主机名验证（或强制应用程序允许任何主机名）并且在他们的应用程序投入生产时忘记更改它。以下代码禁用主机名验证：

```
final static HostnameVerifier NO_VERIFY = new HostnameVerifier() {
    public boolean verify(String hostname, SSLSession session) {
        return true;
    }
};
```

使用内置的`HostnameVerifier`，可以接受任何主机名：

```
HostnameVerifier NO_VERIFY = org.apache.http.conn.ssl.SSLSocketFactory
                             .ALLOW_ALL_HOSTNAME_VERIFIER;
```

确保您的应用程序在设置可信连接之前验证主机名。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis_1)

在测试针对 Android 7.0（API 级别 24）或更高版本的应用程序时，它应该有效地应用网络安全配置，您一开始应该看不到解密的 HTTPS 流量。但是，如果该应用的目标 API 级别低于 24，则该应用将自动接受已安装的用户证书。

