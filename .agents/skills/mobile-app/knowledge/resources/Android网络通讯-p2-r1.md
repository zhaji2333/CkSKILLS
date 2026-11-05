# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 2 · part 1

> 分段 1/2。索引见 `Android网络通讯-p2.md`。

# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 2

> 分段 2/3。索引见 `Android网络通讯.md`。

## 承接

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
