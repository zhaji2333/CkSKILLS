# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 1 · part 1

> 分段 1/2。索引见 `Android网络通讯-p1.md`。

# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 1

> 分段 1/3。索引见 `Android网络通讯.md`。

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

