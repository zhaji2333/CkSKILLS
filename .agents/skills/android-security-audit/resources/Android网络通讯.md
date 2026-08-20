# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication)

几乎每个 Android 应用程序都充当一个或多个远程服务的客户端。由于这种网络通信通常发生在公共 Wi-Fi 等不受信任的网络上，因此基于经典网络的攻击成为一个潜在问题。

大多数现代移动应用程序都使用基于 HTTP 的 Web 服务的变体，因为这些协议已得到充分记录和支持。

## 概述[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#overview)

### Android网络安全配置[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)

从 Android 7.0（API 级别 24）开始，Android 应用程序可以使用所谓的[网络安全配置](https://developer.android.com/training/articles/security-config)功能自定义其网络安全设置，该功能提供以下主要功能：

- **明文流量**：防止应用意外使用明文流量（或启用它）。
- **自定义信任锚**：为应用程序的安全连接自定义哪些证书颁发机构 (CA) 是可信的。例如，信任特定的自签名证书或限制应用信任的公共 CA 集。
- **证书固定**：限制应用程序与特定证书的安全连接。
- **仅调试覆盖**：安全地调试应用程序中的安全连接，而不会给已安装的基础增加风险。

`android:networkSecurityConfig`如果应用程序定义了自定义网络安全配置，您可以通过在 AndroidManifest.xml 文件中搜索来获取其位置。

```
<application android:networkSecurityConfig="@xml/network_security_config"
```

在这种情况下，文件位于`@xml`（相当于 /res/xml）并且名称为“network_security_config”（可能有所不同）。您应该能够找到它作为“res/xml/network_security_config.xml”。[如果存在配置，则系统日志](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#monitoring-system-logs)中应显示以下事件：

```
D/NetworkSecurityConfig: Using Network Security Config from resource network_security_config
```

网络安全配置是[基于 XML 的](https://developer.android.com/training/articles/security-config#FileFormat)，可用于配置应用程序范围和特定于域的设置：

- `base-config`适用于应用程序尝试建立的所有连接。
- `domain-config`覆盖`base-config`特定域（它可以包含多个`domain`条目）。

例如，以下配置使用`base-config`来防止所有域的明文流量。但它使用 覆盖该规则`domain-config`，明确允许`localhost`.

```
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
    <domain-config cleartextTrafficPermitted="true">
        <domain>localhost</domain>
    </domain-config>
</network-security-config>
```

学到更多：

- [《Android P 网络安全配置安全分析师指南》](https://www.nowsecure.com/blog/2018/08/15/a-security-analysts-guide-to-network-security-configuration-in-android-p/)
- [Android开发者-网络安全配置](https://developer.android.com/training/articles/security-config)
- [Android Codelab - 网络安全配置](https://developer.android.com/codelabs/android-network-security-config)

#### 默认配置[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#default-configurations)

针对 Android 9（API 级别 28）及更高版本的应用的默认配置如下：

```
<base-config cleartextTrafficPermitted="false">
    <trust-anchors>
        <certificates src="system" />
    </trust-anchors>
</base-config>
```

针对 Android 7.0（API 级别 24）到 Android 8.1（API 级别 27）的应用程序的默认配置如下：

```
<base-config cleartextTrafficPermitted="true">
    <trust-anchors>
        <certificates src="system" />
    </trust-anchors>
</base-config>
```

针对 Android 6.0（API 级别 23）及更低版本的应用的默认配置如下：

```
<base-config cleartextTrafficPermitted="true">
    <trust-anchors>
        <certificates src="system" />
        <certificates src="user" />
    </trust-anchors>
</base-config>
```

## 在网络上测试数据加密 (MSTG-NETWORK-1)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-data-encryption-on-the-network-mstg-network-1)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#static-analysis)

#### 通过安全协议测试网络请求[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-network-requests-over-secure-protocols)

首先，您应该识别源代码中的所有网络请求，并确保没有使用纯 HTTP URL。确保使用[`HttpsURLConnection`](https://developer.android.com/reference/javax/net/ssl/HttpsURLConnection.html)或[`SSLSocket`](https://developer.android.com/reference/javax/net/ssl/SSLSocket.html)（对于使用 TLS 的套接字级通信）通过安全通道发送敏感信息。

#### 测试网络 API 使用[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-network-api-usage)

接下来，即使使用应该建立安全连接的低级 API（例如`SSLSocket`），也要注意它必须安全地实现。例如，`SSLSocket` **不**验证主机名。用于`getDefaultHostnameVerifier`验证主机名。Android 开发人员文档包括一个[代码示例](https://developer.android.com/training/articles/security-ssl.html#WarningsSslSocket)。

#### 测试明文流量[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-for-cleartext-traffic)

接下来，您应该确保该应用不允许明文 HTTP 流量。由于 Android 9（API 级别 28）默认情况下会阻止明文 HTTP 流量（由于[默认的网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#default-configurations)），但应用程序仍然可以通过多种方式发送它：

- 在 AndroidManifest.xml 文件中设置标签的[`android:usesCleartextTraffic`](https://developer.android.com/guide/topics/manifest/application-element#usesCleartextTraffic)属性。`<application>`请注意，如果配置了网络安全配置，则忽略此标志。
- 通过在元素`cleartextTrafficPermitted`上将属性设置为 true，将网络安全配置配置为启用明文流量。`<domain-config>`
- 使用低级 API（例如[`Socket`](https://developer.android.com/reference/java/net/Socket)）来设置自定义 HTTP 连接。
- 使用跨平台框架（例如 Flutter、Xamarin 等），因为它们通常有自己的 HTTP 库实现。

上述所有案例都必须作为一个整体仔细分析。例如，即使应用程序在其 Android 清单或网络安全配置中不允许明文流量，它实际上可能仍在发送 HTTP 流量。如果它使用的是低级 API（忽略网络安全配置）或配置不当的跨平台框架，则可能会出现这种情况。

有关更多信息，请参阅文章[“HTTPS 和 SSL 的安全性”](https://developer.android.com/training/articles/security-ssl.html)。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis)

拦截测试应用程序的传入和传出网络流量，并确保此流量已加密。您可以通过以下任一方式拦截网络流量：

- [使用OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)或[Burp Suite](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#burp-suite)等拦截代理捕获所有 HTTP(S) 和 Websocket 流量，并确保所有请求都是通过 HTTPS 而不是 HTTP 发出的。
- Burp 和 OWASP ZAP 等拦截代理将仅显示 HTTP(S) 流量。但是，您可以使用 Burp 插件（例如[Burp-non-HTTP-Extension）](https://github.com/summitt/Burp-Non-HTTP-Extension)或工具[mitm-relay](https://github.com/jrmdev/mitm_relay)来解码和可视化通过 XMPP 和其他协议进行的通信。

> 由于证书固定，某些应用程序可能无法与 Burp 和 OWASP ZAP 等代理一起使用。在这种情况下，请检查[“测试自定义证书存储和证书固定”](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-custom-certificate-stores-and-certificate-pinning-mstg-network-4)。

有关更多详细信息，请参阅：

- “移动应用程序网络通信”一章[中的“网络层拦截流量”](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#intercepting-traffic-on-the-network-layer)
- “ Android 基本安全测试”一章中[的“设置网络测试环境”](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-a-network-testing-environment)

## 测试 TLS 设置 (MSTG-NETWORK-2)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-the-tls-settings-mstg-network-2)

详见“移动应用网络通信”一章中[的“验证TLS设置”部分。](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#verifying-the-tls-settings-mstg-network-2)

## 测试端点识别验证 (MSTG-NETWORK-3)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-endpoint-identify-verification-mstg-network-3)

使用 TLS 通过网络传输敏感信息对于安全至关重要。然而，加密移动应用程序与其后端 API 之间的通信并非易事。开发人员通常决定采用更简单但安全性较低的解决方案（例如，那些接受任何证书的解决方案）来促进开发过程，有时这些薄弱的解决方案[会进入生产版本](https://saschafahl.de/static/paper/androidssl2012.pdf)，从而可能使用户面临[中间人攻击](https://cwe.mitre.org/data/definitions/295.html)。

应解决两个关键问题：

- 验证证书是否来自受信任的来源，即受信任的 CA（证书颁发机构）。
- 确定端点服务器是否提供正确的证书。

确保主机名和证书本身得到正确验证。[官方 Android 文档](https://developer.android.com/training/articles/security-ssl.html)中提供了示例和常见陷阱。在代码中搜索示例`TrustManager`和`HostnameVerifier`用法。在下面的部分中，您可以找到您应该寻找的不安全用法的示例。

> 请注意，从 Android 8.0（API 级别 26）开始，不再支持 SSLv3，并且`HttpsURLConnection`将不再执行回退到不安全的 TLS/SSL 协议。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#static-analysis_1)

#### 验证目标 SDK 版本[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#verifying-the-target-sdk-version)

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

要测试不正确的证书验证，请使用 Burp 等拦截代理发起 MITM 攻击。尝试以下选项：

- **自签名证书：**
- 在 Burp 中，转到“**代理**”选项卡并选择“**选项**”选项卡。
- 转到**Proxy Listeners**部分，突出显示您的侦听器，然后单击**Edit**。
- 转到**Certificate**选项卡，选中**Use a self-signed certificate**，然后单击**Ok**。
- 运行您的应用程序。如果您能够看到 HTTPS 流量，则您的应用程序正在接受自签名证书。
- **接受具有不受信任的 CA 的证书：**
- 在 Burp 中，转到“**代理**”选项卡并选择“**选项**”选项卡。
- 转到**Proxy Listeners**部分，突出显示您的侦听器，然后单击**Edit**。
- 转到**Certificate**选项卡，选中**Generate a CA-signed certificate with a specific hostname**，然后输入后端服务器的主机名。
- 运行您的应用程序。如果您能够看到 HTTPS 流量，则您的应用程序正在接受来自不受信任的 CA 的证书。
- **接受不正确的主机名：**
- 在 Burp 中，转到“**代理**”选项卡并选择“**选项**”选项卡。
- 转到**Proxy Listeners**部分，突出显示您的侦听器，然后单击**Edit**。
- 转到**Certificate**选项卡，选中**Generate a CA-signed certificate with a specific hostname**，然后输入无效的主机名，例如 example.org。
- 运行您的应用程序。如果您能够看到 HTTPS 流量，则您的应用程序正在接受所有主机名。

如果您仍然看不到任何解密的 HTTPS 流量，您的应用程序可能正在实施[证书固定](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-custom-certificate-stores-and-certificate-pinning-mstg-network-4)。

## 测试自定义证书存储和证书固定 (MSTG-NETWORK-4)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-custom-certificate-stores-and-certificate-pinning-mstg-network-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#overview_1)

此测试验证应用程序是否正确实施身份锁定（证书或公钥锁定）。

有关详细信息，请参阅一般章节“移动应用程序网络通信”中的[“身份固定”部分。](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#identity-pinning)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#static-analysis_2)

#### 网络安全配置中的证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#certificate-pinning-in-the-network-security-configuration)

[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)还可用于将声明[性证书](https://developer.android.com/training/articles/security-config.html#CertificatePinning)固定到特定域。这是通过在网络安全配置中提供一个来完成的，它是相应 X.509 证书的`<pin-set>`公钥 ( ) 的一组摘要（散列） 。`SubjectPublicKeyInfo`

尝试建立与远程端点的连接时，系统将：

- 获取并验证传入的证书。
- 提取公钥。
- 计算提取的公钥的摘要。
- 将摘要与本地引脚集进行比较。

如果至少有一个固定摘要匹配，则证书链将被视为有效并且连接将继续。

```
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config>
        Use certificate pinning for OWASP website access including sub domains
        <domain includeSubdomains="true">owasp.org</domain>
        <pin-set expiration="2018/8/10">
            <!-- Hash of the public key (SubjectPublicKeyInfo of the X.509 certificate) of
            the Intermediate CA of the OWASP website server certificate -->
            <pin digest="SHA-256">YLh1dUR9y6Kja30RrAn7JKnbQG/uEtLMkBgFF2Fuihg=</pin>
            <!-- Hash of the public key (SubjectPublicKeyInfo of the X.509 certificate) of
            the Root CA of the OWASP website server certificate -->
            <pin digest="SHA-256">Vjs8r4z+80wjNcr1YKepWQboSIRi63WsWXhIMN+eWys=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

检查`<pin-set>`任何`expiration`日期的元素。如果过期，受影响域的证书固定将被禁用。

> **测试提示：如果证书固定验证检查失败，**[系统日志](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#monitoring-system-logs)中应记录以下事件：

```
I/X509Util: Failed to validate the certificate chain, error: Pin verification failed
```

#### TrustManager[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#trustmanager)

实施证书固定涉及三个主要步骤：

- 获取所需主机的证书。
- 确保证书采用 .bks 格式。
- 将证书固定到默认 Apache Httpclient 的实例。

要分析证书固定的正确实现，HTTP 客户端应加载 KeyStore：

```
InputStream in = resources.openRawResource(certificateRawResource);
keyStore = KeyStore.getInstance("BKS");
keyStore.load(resourceStream, password);
```

加载 KeyStore 后，我们可以使用信任 KeyStore 中的 CA 的 TrustManager：

```
String tmfAlgorithm = TrustManagerFactory.getDefaultAlgorithm();
TrustManagerFactory tmf = TrustManagerFactory.getInstance(tmfAlgorithm);
tmf.init(keyStore);
// Create an SSLContext that uses the TrustManager
// SSLContext context = SSLContext.getInstance("TLS");
sslContext.init(null, tmf.getTrustManagers(), null);
```

应用程序的实现可能不同，仅固定证书的公钥、整个证书或整个证书链。

#### 网络库和 WebView[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#network-libraries-and-webviews)

使用第三方网络库的应用程序可以利用库的证书固定功能。例如[okhttp](https://github.com/square/okhttp/wiki/HTTPS)可以这样设置`CertificatePinner`：

```
OkHttpClient client = new OkHttpClient.Builder()
        .certificatePinner(new CertificatePinner.Builder()
            .add("example.com", "sha256/UwQAapahrjCOjYI3oLUx5AQxPBR02Jz6/E2pt0IeLXA=")
            .build())
        .build();
```

使用 WebView 组件的应用程序可以利用 WebViewClient 的事件处理程序在加载目标资源之前对每个请求进行某种“证书固定”。以下代码显示了一个示例验证：

```
WebView myWebView = (WebView) findViewById(R.id.webview);
myWebView.setWebViewClient(new WebViewClient(){
    private String expectedIssuerDN = "CN=Let's Encrypt Authority X3,O=Let's Encrypt,C=US;";

    @Override
    public void onLoadResource(WebView view, String url)  {
        //From Android API documentation about "WebView.getCertificate()":
        //Gets the SSL certificate for the main top-level page
        //or null if there is no certificate (the site is not secure).
        //
        //Available information on SslCertificate class are "Issuer DN", "Subject DN" and validity date helpers
        SslCertificate serverCert = view.getCertificate();
        if(serverCert != null){
            //apply either certificate or public key pinning comparison here
                //Throw exception to cancel resource loading...
            }
        }
    }
});
```

或者，最好使用带有已配置引脚的 OkHttpClient，并让它充当代理覆盖`shouldInterceptRequest`.`WebViewClient`

#### Xamarin 应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#xamarin-applications)

在 Xamarin 中开发的应用程序通常会使用 ServicePointManager 来实现固定。

通常会创建一个函数来检查证书并将布尔值返回给 ServerCertificateValidationCallback 方法：

```
[Activity(Label = "XamarinPinning", MainLauncher = true)]
    public class MainActivity : Activity
    {
        // SupportedPublicKey - Hexadecimal value of the public key.
        // Use GetPublicKeyString() method to determine the public key of the certificate we want to pin. Uncomment the debug code in the ValidateServerCertificate function a first time to determine the value to pin.
        private const string SupportedPublicKey = "3082010A02820101009CD30CF05AE52E47B7725D3783B..."; // Shortened for readability

        private static bool ValidateServerCertificate(
                object sender,
                X509Certificate certificate,
                X509Chain chain,
                SslPolicyErrors sslPolicyErrors
            )
        {
            //Log.Debug("Xamarin Pinning",chain.ChainElements[X].Certificate.GetPublicKeyString());
            //return true;
            return SupportedPublicKey == chain.ChainElements[1].Certificate.GetPublicKeyString();
        }

        protected override void OnCreate(Bundle savedInstanceState)
        {
            System.Net.ServicePointManager.ServerCertificateValidationCallback += ValidateServerCertificate;
            base.OnCreate(savedInstanceState);
            SetContentView(Resource.Layout.Main);
            TesteAsync("https://security.claudio.pt");

        }
```

在此特定示例中，我们固定了证书链的中间 CA。HTTP 响应的输出将在系统日志中可用。

可以在[MSTG 存储库上获取带有前面示例的示例 Xamarin 应用程序](https://github.com/OWASP/owasp-mastg/raw/master/Samples/Android/02_CertificatePinning/certificatePinningXamarin.apk)

解压 APK 文件后，使用 dotPeak、ILSpy 或 dnSpy 等 .NET 反编译器反编译存储在“Assemblies”文件夹中的应用程序 dll，并确认 ServicePointManager 的使用。

#### 科尔多瓦应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#cordova-applications)

基于 Cordova 的混合应用程序本身不支持 Certificate Pinning，因此需要使用插件来实现。最常见的是 PhoneGap SSL Certificate Checker。该`check`方法用于确认指纹，回调将确定下一步。

```
  // Endpoint to verify against certificate pinning.
  var server = "https://www.owasp.org";
  // SHA256 Fingerprint (Can be obtained via "openssl s_client -connect hostname:443 | openssl x509 -noout -fingerprint -sha256"
  var fingerprint = "D8 EF 3C DF 7E F6 44 BA 04 EC D5 97 14 BB 00 4A 7A F5 26 63 53 87 4E 76 67 77 F0 F4 CC ED 67 B9";

  window.plugins.sslCertificateChecker.check(
          successCallback,
          errorCallback,
          server,
          fingerprint);

   function successCallback(message) {
     alert(message);
     // Message is always: CONNECTION_SECURE.
     // Now do something with the trusted server.
   }

   function errorCallback(message) {
     alert(message);
     if (message === "CONNECTION_NOT_SECURE") {
       // There is likely a man in the middle attack going on, be careful!
     } else if (message.indexOf("CONNECTION_FAILED") >- 1) {
       // There was no connection (yet). Internet may be down. Try again (a few times) after a little timeout.
     }
   }
```

解压 APK 文件后，Cordova/Phonegap 文件将位于 /assets/www 文件夹中。'plugins' 文件夹会让您看到所使用的插件。我们需要在应用程序的 JavaScript 代码中搜索此方法以确认其用法。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis_2)

按照[“测试端点识别验证 > 动态分析”](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-endpoint-identify-verification-mstg-network-3)中的说明进行操作。如果这样做不会导致流量被代理，则可能意味着实际上已实施证书固定并且所有安全措施都已到位。所有域都会发生同样的情况吗？

作为快速冒烟测试，您可以尝试使用[objection](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)绕过证书固定，如[“绕过证书固定”](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-certificate-pinning)中所述。被objectionHook的固定相关 API 应该出现在objection的输出中。

![反对 Android SSL Pinning 绕过](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/Images/Chapters/0x05b/android_ssl_pinning_bypass.png)

但是，请记住：

- API 可能不完整。
- 如果没有任何东西被钩住，那并不一定意味着该应用程序没有实现固定。

[在这两种情况下，应用程序或其某些组件可能会以 objection 支持](https://github.com/sensepost/objection/blob/master/agent/src/android/pinning.ts)的方式实现自定义固定。请查看静态分析部分以了解具体的固定指标和更深入的测试。

## 测试security providers (MSTG-NETWORK-6)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-the-security-provider-mstg-network-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#overview_2)

Android 依靠security providers来提供基于 SSL/TLS 的连接。设备附带的这种security providers（一个例子是[OpenSSL](https://www.openssl.org/news/vulnerabilities.html)）的问题是它经常有错误和/或漏洞。为避免已知漏洞，开发人员需要确保应用程序将安装适当的security providers。自 2016 年 7 月 11 日起，谷歌[一直拒绝](https://support.google.com/faqs/answer/6376725?hl=en)使用易受攻击的 OpenSSL 版本的 Play 商店应用程序提交（包括新应用程序和更新）。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#static-analysis_3)

基于Android SDK 的应用程序应该依赖于GooglePlayServices。例如，在 gradle 构建文件中，您会`compile 'com.google.android.gms:play-services-gcm:x.x.x'`在 dependencies 块中找到。您需要确保使用或`ProviderInstaller`调用该类。需要由应用程序的组件尽早调用。这些方法抛出的异常应该被正确捕获和处理。如果应用程序无法修补其security providers，它可以通知 API 其安全性较低的状态或限制用户操作（因为在这种情况下所有 HTTPS 流量都应被视为风险更高）。`installIfNeeded``installIfNeededAsync``ProviderInstaller`

[以下是Android 开发人员文档](https://developer.android.com/training/articles/security-gms-provider.html)中的两个示例，展示了如何更新security providers以防止 SSL 攻击。在这两种情况下，开发人员都需要正确处理异常，并且在应用程序使用未打补丁的security providers时向后端报告可能是明智的。

同步修补：

```
//this is a sync adapter that runs in the background, so you can run the synchronous patching.
public class SyncAdapter extends AbstractThreadedSyncAdapter {

  ...

  // This is called each time a sync is attempted; this is okay, since the
  // overhead is negligible if the security provider is up-to-date.
  @Override
  public void onPerformSync(Account account, Bundle extras, String authority,
      ContentProviderClient provider, SyncResult syncResult) {
    try {
      ProviderInstaller.installIfNeeded(getContext());
    } catch (GooglePlayServicesRepairableException e) {

      // Indicates that Google Play services is out of date, disabled, etc.

      // Prompt the user to install/update/enable Google Play services.
      GooglePlayServicesUtil.showErrorNotification(
          e.getConnectionStatusCode(), getContext());

      // Notify the SyncManager that a soft error occurred.
      syncResult.stats.numIOExceptions++;
      return;

    } catch (GooglePlayServicesNotAvailableException e) {
      // Indicates a non-recoverable error; the ProviderInstaller is not able
      // to install an up-to-date Provider.

      // Notify the SyncManager that a hard error occurred.
      //in this case: make sure that you inform your API of it.
      syncResult.stats.numAuthExceptions++;
      return;
    }

    // If this is reached, you know that the provider was already up-to-date,
    // or was successfully updated.
  }
}
```

异步修补：

```
//This is the mainactivity/first activity of the application that's there long enough to make the async installing of the securityprovider work.
public class MainActivity extends Activity
    implements ProviderInstaller.ProviderInstallListener {

  private static final int ERROR_DIALOG_REQUEST_CODE = 1;

  private boolean mRetryProviderInstall;

  //Update the security provider when the activity is created.
  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    ProviderInstaller.installIfNeededAsync(this, this);
  }

  /**
   * This method is only called if the provider is successfully updated
   * (or is already up-to-date).
   */
  @Override
  protected void onProviderInstalled() {
    // Provider is up-to-date, app can make secure network calls.
  }

  /**
   * This method is called if updating fails; the error code indicates
   * whether the error is recoverable.
   */
  @Override
  protected void onProviderInstallFailed(int errorCode, Intent recoveryIntent) {
    if (GooglePlayServicesUtil.isUserRecoverableError(errorCode)) {
      // Recoverable error. Show a dialog prompting the user to
      // install/update/enable Google Play services.
      GooglePlayServicesUtil.showErrorDialogFragment(
          errorCode,
          this,
          ERROR_DIALOG_REQUEST_CODE,
          new DialogInterface.OnCancelListener() {
            @Override
            public void onCancel(DialogInterface dialog) {
              // The user chose not to take the recovery action
              onProviderInstallerNotAvailable();
            }
          });
    } else {
      // Google Play services is not available.
      onProviderInstallerNotAvailable();
    }
  }

  @Override
  protected void onActivityResult(int requestCode, int resultCode,
      Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode == ERROR_DIALOG_REQUEST_CODE) {
      // Adding a fragment via GooglePlayServicesUtil.showErrorDialogFragment
      // before the instance state is restored throws an error. So instead,
      // set a flag here, which will cause the fragment to delay until
      // onPostResume.
      mRetryProviderInstall = true;
    }
  }

  /**
   * On resume, check to see if we flagged that we need to reinstall the
   * provider.
   */
  @Override
  protected void onPostResume() {
    super.onPostResult();
    if (mRetryProviderInstall) {
      // We can now safely retry installation.
      ProviderInstall.installIfNeededAsync(this, this);
    }
    mRetryProviderInstall = false;
  }

  private void onProviderInstallerNotAvailable() {
    // This is reached if the provider cannot be updated for some reason.
    // App should consider all HTTP communication to be vulnerable, and take
    // appropriate action (e.g. inform backend, block certain high-risk actions, etc.).
  }
}
```

确保基于 NDK 的应用程序仅绑定到最新且已正确修补的库，该库提供 SSL/TLS 功能。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis_3)

当你有源代码时：

- 在调试模式下运行应用程序，然后在应用程序将首先联系端点的位置创建一个断点。
- 右键单击突出显示的代码并选择`Evaluate Expression`。
- 键入`Security.getProviders()`并按回车键。
- 检查提供商并尝试查找`GmsCore_OpenSSL`，这应该是新的排名靠前的提供商。

当您没有源代码时：

- 使用 Xposed Hook到`java.security`包中，然后`java.security.Security`使用方法Hook`getProviders`（不带参数）。返回值将是一个数组`Provider`。
- 确定第一个提供者是否是`GmsCore_OpenSSL`。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#owasp-masvs)

- MSTG-NETWORK-1：“数据在网络上使用 TLS 加密。整个应用程序始终使用安全通道。”
- MSTG-NETWORK-2：“TLS 设置符合当前最佳实践，或者如果移动操作系统不支持推荐标准，则尽可能接近。”
- MSTG-NETWORK-3：“应用程序在建立安全通道时验证远程端点的 X.509 证书。只接受由受信任的 CA 签名的证书。”
- MSTG-NETWORK-4：“该应用程序要么使用自己的证书存储，要么固定端点证书或公钥，随后不会与提供不同证书或密钥的端点建立连接，即使由受信任的 CA 签名也是如此。”
- MSTG-NETWORK-6：“该应用程序仅依赖于最新的连接和安全库。”

### Android开发者文档[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-developer-documentation)

- 网络安全配置 - https://developer.android.com/training/articles/security-config
- 网络安全配置（缓存替代）- [https://webcache.googleusercontent.com/search?q=cache:hOONLxvMTwYJ:https://developer.android.com/training/articles/security-config+&cd=10&hl=nl&ct= clnk&gl=nl](https://webcache.googleusercontent.com/search?q=cache:hOONLxvMTwYJ:https://developer.android.com/training/articles/security-config+&cd=10&hl=nl&ct=clnk&gl=nl)

### Xamarin 证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#xamarin-certificate-pinning)

- 使用 Xamarin 固定证书和公钥 - https://thomasbandt.com/certificate-and-public-key-pinning-with-xamarin
- ServicePointManager - https://msdn.microsoft.com/en-us/library/system.net.servicepointmanager(v=vs.110).aspx

### Cordova 证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#cordova-certificate-pinning)

- PhoneGap SSL 证书检查器插件 - https://github.com/EddyVerbruggen/SSLCertificateChecker-PhoneGap-Plugin
