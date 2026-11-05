# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 1 · part 1

> 分段 1/2。索引见 `Android加密API-p1.md`。

# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 1

> 分段 1/2。索引见 `Android加密API.md`。

# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis)

在[“移动应用密码学”](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/)一章中，我们介绍了一般的密码学最佳实践，并描述了密码学使用不当时可能出现的典型问题。在本章中，我们将更详细地介绍 Android 的加密 API。我们将展示如何识别源代码中这些 API 的使用以及如何解释加密配置。在审查代码时，确保将使用的加密参数与本指南中链接的当前最佳实践进行比较。

我们可以识别 Android 中密码系统的关键组件：

- [Security Provider](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#security-provider)
- KeyStore - 请参阅“测试数据存储”一章中的[KeyStore部分](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#keystore)
- KeyChain - 请参阅“测试数据存储”一章中的[KeyChain部分](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#keychain)

Android 加密 API 基于 Java 加密架构 (JCA)。JCA 将接口和实现分开，使得包含多个可以实现加密算法集的[security providers成为可能。](https://developer.android.com/reference/java/security/Provider.html)大多数 JCA 接口和类都在`java.security.*`和`javax.crypto.*`包中定义。此外，还有 Android 特定的包`android.security.*`和`android.security.keystore.*`.

KeyStore 和 KeyChain 提供了用于存储和使用密钥的 API（在后台，KeyChain API 使用 KeyStore 系统）。这些系统允许管理加密密钥的整个生命周期。可以在[密钥管理备忘单](https://cheatsheetseries.owasp.org/cheatsheets/Key_Management_Cheat_Sheet.html)中找到实施加密密钥管理的要求和指南。我们可以确定以下阶段：

- 生成密钥
- 使用钥匙
- 存储密钥
- 归档密钥
- 删除密钥

> 请注意，密钥的存储在“[测试数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)”一章中进行了分析。

这些阶段由 Keystore/KeyChain 系统管理。然而，系统如何工作取决于应用程序开发人员如何实现它。对于分析过程，您应该关注应用程序开发人员使用的功能。您应该识别并验证以下功能：

- [密钥生成](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#key-generation)
- [随机数生成](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#random-number-generation)
- 密钥轮换

针对现代 API 级别的应用经历了以下变化：

- 对于 Android 7.0（API 级别 24）及更高[版本，Android 开发者博客显示](https://android-developers.googleblog.com/2016/06/security-crypto-provider-deprecated-in.html)：
- 建议停止指定security providers。相反，始终使用[打过补丁的security providers](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#updating-provider)。
- 对提供者的支持`Crypto`已经下降，提供者已被弃用。这同样适用于它`SHA1PRNG`的安全随机数。
- 对于 Android 8.1（API 级别 27）及更高版本，[开发者文档](https://developer.android.com/about/versions/oreo/android-8.1)显示：
- Conscrypt，称为`AndroidOpenSSL`，比使用 Bouncy Castle 更受欢迎，它有新的实现：`AlgorithmParameters:GCM`, `KeyGenerator:AES`, `KeyGenerator:DESEDE`, `KeyGenerator:HMACMD5`, `KeyGenerator:HMACSHA1`, `KeyGenerator:HMACSHA224`, `KeyGenerator:HMACSHA256`, `KeyGenerator:HMACSHA384`, `KeyGenerator:HMACSHA512`, `SecretKeyFactory:DESEDE`, 和`Signature:NONEWITHECDSA`.
- 您不应`IvParameterSpec.class`再对 GCM 使用 the，而应使用 the `GCMParameterSpec.class`。
- 套接字已从`OpenSSLSocketImpl`变为`ConscryptFileDescriptorSocket`和`ConscryptEngineSocket`。
- `SSLSession`使用 null 参数给出一个`NullPointerException`.
- 您需要有足够大的数组作为输入字节以生成密钥，否则将`InvalidKeySpecException`抛出 an。
- 如果 Socket 读取被中断，你会得到一个`SocketException`.
- 对于 Android 9（API 级别 28）及更高版本，[Android 开发者博客](https://android-developers.googleblog.com/2018/03/cryptography-changes-in-android-p.html)显示了更多变化：
- 如果您仍然使用该`getInstance`方法指定security providers并且您将任何低于 28 的 API 作为目标，您将收到警告。如果您将目标设为 Android 9（API 级别 28）或更高版本，则会收到错误消息。
- 安全提供`Crypto`程序现已删除。调用它会产生一个`NoSuchProviderException`.
- 对于 Android 10（API 级别 29），[开发者文档](https://developer.android.com/about/versions/10/behavior-changes-all#security)列出了所有网络安全更改。

## 建议[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#recommendations)

在应用检查期间应考虑以下建议列表：

- 您应该确保遵循“[移动应用程序加密](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/)”一章中概述的最佳实践。
- 您应该确保security providers具有最新的更新 -[更新security providers](https://developer.android.com/training/articles/security-gms-provider)。
- 您应该停止指定security providers并使用默认实现（AndroidOpenSSL、Conscrypt）。
- 您应该停止使用加密security providers及其`SHA1PRNG`已弃用的内容。
- 您应该仅为 Android Keystore 系统指定security providers。
- 您应该停止使用没有 IV 的基于密码的加密密码。
- 您应该使用 KeyGenParameterSpec 而不是 KeyPairGeneratorSpec。

### Security Provider[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#security-provider)

Android 依赖于`provider`实现 Java 安全服务。这对于确保安全的网络通信和保护依赖于密码学的其他功能至关重要。

Android 中包含的security providers列表因 Android 版本和特定于 OEM 的构建而异。现在已知旧版本中的某些security providers实现不太安全或易受攻击。因此，Android 应用程序不仅应该选择正确的算法并提供良好的配置，在某些情况下，它们还应该注意遗留security providers中实现的强度。

您可以使用以下代码列出现有security providers集：

```
StringBuilder builder = new StringBuilder();
for (Provider provider : Security.getProviders()) {
    builder.append("provider: ")
            .append(provider.getName())
            .append(" ")
            .append(provider.getVersion())
            .append("(")
            .append(provider.getInfo())
            .append(")\n");
}
String providers = builder.toString();
//now display the string on the screen or in the logs for debugging.
```

您可以在下面找到在带有 Google Play API 的模拟器中运行 Android 4.4（API 级别 19）的输出，security providers已修补后：

```
provider: GmsCore_OpenSSL1.0 (Android's OpenSSL-backed security provider)
provider: AndroidOpenSSL1.0 (Android's OpenSSL-backed security provider)
provider: DRLCertFactory1.0 (ASN.1, DER, PkiPath, PKCS7)
provider: BC1.49 (BouncyCastle Security Provider v1.49)
provider: Crypto1.0 (HARMONY (SHA1 digest; SecureRandom; SHA1withDSA signature))
provider: HarmonyJSSE1.0 (Harmony JSSE Provider)
provider: AndroidKeyStore1.0 (Android AndroidKeyStore security provider)
```

您可以在下面找到在带有 Google Play API 的模拟器中运行 Android 9（API 级别 28）的输出：

```
provider: AndroidNSSP 1.0(Android Network Security Policy Provider)
provider: AndroidOpenSSL 1.0(Android's OpenSSL-backed security provider)
provider: CertPathProvider 1.0(Provider of CertPathBuilder and CertPathVerifier)
provider: AndroidKeyStoreBCWorkaround 1.0(Android KeyStore security provider to work around Bouncy Castle)
provider: BC 1.57(BouncyCastle Security Provider v1.57)
provider: HarmonyJSSE 1.0(Harmony JSSE Provider)
provider: AndroidKeyStore 1.0(Android KeyStore security provider)
```

#### 更新security providers[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#updating-security-provider)

保持最新和打补丁的组件是安全原则之一。这同样适用于`provider`. 应用程序应检查使用的security providers是否是最新的，如果不是，则[更新它](https://developer.android.com/training/articles/security-gms-provider)。它与[检查第三方库中的弱点 (MSTG-CODE-5) 有关](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#checking-for-weaknesses-in-third-party-libraries)。

#### 较旧的 Android 版本[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#older-android-versions)

对于某些支持旧版本 Android 的应用程序（例如：仅使用低于 Android 7.0（API 级别 24）的版本），捆绑最新的库可能是唯一的选择。Spongy Castle（Bouncy Castle 的重新打包版本）是这些情况下的常见选择。重新打包是必要的，因为 Bouncy Castle 包含在 Android SDK 中。最新版本的[Spongy Castle](https://rtyley.github.io/spongycastle/)可能修复了 Android 中包含的早期版本的[Bouncy Castle](https://www.cvedetails.com/vulnerability-list/vendor_id-7637/Bouncycastle.html)中遇到的问题。请注意，Android 附带的 Bouncy Castle 库通常不如来自[Bouncy Castle 军团的](https://www.bouncycastle.org/java.html)对应库那么完整。最后：请记住，打包像 Spongy Castle 这样的大型库通常会导致多索引的 Android 应用程序。

### 密钥生成[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#key-generation)

Android SDK 提供了指定安全密钥生成和使用的机制。Android 6.0（API 级别 23）引入了`KeyGenParameterSpec`可用于确保应用程序中正确使用密钥的类。

下面是在 API 23+ 上使用 AES/CBC/PKCS7Padding 的示例：

```
String keyAlias = "MySecretKey";

KeyGenParameterSpec keyGenParameterSpec = new KeyGenParameterSpec.Builder(keyAlias,
        KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
        .setRandomizedEncryptionRequired(true)
        .build();

KeyGenerator keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore");
keyGenerator.init(keyGenParameterSpec);

SecretKey secretKey = keyGenerator.generateKey();
```

