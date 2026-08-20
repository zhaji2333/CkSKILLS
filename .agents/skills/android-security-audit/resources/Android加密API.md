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

表示该`KeyGenParameterSpec`密钥可用于加密和解密，但不能用于其他目的，如签名或验证。它进一步指定块模式 (CBC)、填充 (PKCS #7)，并明确指定需要随机加密（这是默认设置）。`"AndroidKeyStore"`是本示例中使用的security providers的名称。这将自动确保密钥存储在`AndroidKeyStore`保护密钥的受益人中。

GCM 是另一种 AES 块模式，与其他较旧的模式相比，它提供了额外的安全优势。除了在密码学上更安全之外，它还提供身份验证。使用 CBC（和其他模式）时，需要使用 HMAC 单独执行身份验证（请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章）。请注意，GCM 是唯一[不支持填充](https://developer.android.com/training/articles/keystore.html#SupportedCiphers)的 AES 模式。

尝试违反上述规范使用生成的密钥将导致安全异常。

下面是使用该密钥进行加密的示例：

```
String AES_MODE = KeyProperties.KEY_ALGORITHM_AES
        + "/" + KeyProperties.BLOCK_MODE_CBC
        + "/" + KeyProperties.ENCRYPTION_PADDING_PKCS7;
KeyStore AndroidKeyStore = AndroidKeyStore.getInstance("AndroidKeyStore");

// byte[] input
Key key = AndroidKeyStore.getKey(keyAlias, null);

Cipher cipher = Cipher.getInstance(AES_MODE);
cipher.init(Cipher.ENCRYPT_MODE, key);

byte[] encryptedBytes = cipher.doFinal(input);
byte[] iv = cipher.getIV();
// save both the IV and the encryptedBytes
```

IV（初始化向量）和加密后的字节都需要存储；否则无法解密。

下面是密文的解密方式。是加密的`input`字节数组，`iv`是加密步骤的初始化向量：

```
// byte[] input
// byte[] iv
Key key = AndroidKeyStore.getKey(AES_KEY_ALIAS, null);

Cipher cipher = Cipher.getInstance(AES_MODE);
IvParameterSpec params = new IvParameterSpec(iv);
cipher.init(Cipher.DECRYPT_MODE, key, params);

byte[] result = cipher.doFinal(input);
```

由于 IV 每次都是随机生成的，因此应将其与密文 ( `encryptedBytes`) 一起保存，以便稍后解密。

在 Android 6.0（API 级别 23）之前，不支持 AES 密钥生成。因此，许多实现选择使用 RSA 并生成用于非对称加密的公私密钥对，使用`KeyPairGeneratorSpec`或用于`SecureRandom`生成 AES 密钥。

这是用于创建 RSA 密钥对`KeyPairGenerator`的示例：`KeyPairGeneratorSpec`

```
Date startDate = Calendar.getInstance().getTime();
Calendar endCalendar = Calendar.getInstance();
endCalendar.add(Calendar.YEAR, 1);
Date endDate = endCalendar.getTime();
KeyPairGeneratorSpec keyPairGeneratorSpec = new KeyPairGeneratorSpec.Builder(context)
        .setAlias(RSA_KEY_ALIAS)
        .setKeySize(4096)
        .setSubject(new X500Principal("CN=" + RSA_KEY_ALIAS))
        .setSerialNumber(BigInteger.ONE)
        .setStartDate(startDate)
        .setEndDate(endDate)
        .build();

KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance("RSA",
        "AndroidKeyStore");
keyPairGenerator.initialize(keyPairGeneratorSpec);

KeyPair keyPair = keyPairGenerator.generateKeyPair();
```

此示例创建密钥大小为 4096 位（即模数大小）的 RSA 密钥对。也可以用类似的方式生成椭圆曲线 (EC) 密钥。但是，从 Android 11（API 级别 30）开始，[AndroidKeyStore 不支持使用 EC 密钥进行加密或解密](https://developer.android.com/guide/topics/security/cryptography#SupportedCipher)。它们只能用于签名。

可以使用基于密码的密钥派生函数版本 2 (PBKDF2) 从密码生成对称加密密钥。该加密协议旨在生成可用于加密目的的加密密钥。算法的输入参数根据[弱密钥生成函数](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#weak-key-generation-functions)部分进行调整。下面的代码清单说明了如何根据密码生成强加密密钥。

```
public static SecretKey generateStrongAESKey(char[] password, int keyLength)
{
    //Initialize objects and variables for later use
    int iterationCount = 10000;
    int saltLength     = keyLength / 8;
    SecureRandom random = new SecureRandom();
    //Generate the salt
    byte[] salt = new byte[saltLength];
    random.nextBytes(salt);
    KeySpec keySpec = new PBEKeySpec(password.toCharArray(), salt, iterationCount, keyLength);
    SecretKeyFactory keyFactory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1");
    byte[] keyBytes = keyFactory.generateSecret(keySpec).getEncoded();
    return new SecretKeySpec(keyBytes, "AES");
}
```

上述方法需要一个包含密码和所需密钥长度（以位为单位）的字符数组，例如 128 或 256 位 AES 密钥。我们定义了 PBKDF2 算法将使用的 10,000 轮迭代计数。增加迭代次数会显着增加对密码进行暴力攻击的工作量，但它会影响性能，因为密钥派生需要更多的计算能力。我们将 salt 大小定义为等于密钥长度，我们除以 8 以处理位到字节的转换。我们使用`SecureRandom`该类随机生成盐。显然，盐是您想要保持不变的东西，以确保为相同提供的密码一次又一次地生成相同的加密密钥。请注意，您可以将盐私下存储在`SharedPreferences`. 建议将 salt 从 Android 备份机制中排除，以防止在较高风险数据的情况下同步。

> 请注意，如果您将获得 root 权限的设备或打过补丁（例如重新打包）的应用程序视为对数据的威胁，最好使用放置在`AndroidKeystore`. 基于密码的加密 (PBE) 密钥是使用推荐的`PBKDF2WithHmacSHA1`算法生成的，直到 Android 8.0（API 级别 26）。对于更高的 API 级别，最好使用`PBKDF2withHmacSHA256`，这将以更长的哈希值结束。

注意：人们普遍错误地认为 NDK 应该用于隐藏加密操作和硬编码密钥。然而，使用这种机制并不有效。攻击者仍然可以使用工具找到所使用的机制并将密钥转储到内存中。接下来，可以使用例如 radare2 分析控制流，并借助 Frida 或两者的组合提取密钥：[r2frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#r2frida)（参见“[反汇编Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#disassembling-native-code)”、“[内存转储](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-dump)”和“[内存中搜索”部分](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#in-memory-search)”在“Android 上的篡改和逆向工程”一章了解更多详情）。从 Android 7.0（API 级别 24）开始，不允许使用私有 API，而是：需要调用公共 API，这进一步影响了有效性按照[Android 开发者博客](https://android-developers.googleblog.com/2016/06/android-changes-for-ndk-developers.html)中的描述将其隐藏起来

### 随机数生成[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#random-number-generation)

密码学需要安全的伪随机数生成 (PRNG)。标准 Java 类`java.util.Random`不提供足够的随机性，实际上可能使攻击者猜测将生成的下一个值，并使用此猜测来冒充其他用户或访问敏感信息。

一般来说，`SecureRandom`应该使用。但是，如果支持低于 Android 4.4（API 级别 19）的 Android 版本，则需要额外注意以解决 Android 4.1-4.3（API 级别 16-18）版本中[无法正确初始化 PRNG](https://android-developers.googleblog.com/2013/08/some-securerandom-thoughts.html)的错误.

大多数开发人员应该`SecureRandom`通过不带任何参数的默认构造函数进行实例化。其他构造函数用于更高级的用途，如果使用不当，可能会导致随机性和安全性降低。PRNG 提供程序支持`SecureRandom`使用`SHA1PRNG`from `AndroidOpenSSL`(Conscrypt) 提供程序。

## 测试对称加密 (MSTG-CRYPTO-1)[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-symmetric-cryptography-mstg-crypto-1)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#overview)

此测试用例侧重于将硬编码对称密码术作为唯一的加密方法。应执行以下检查：

- 识别对称加密的所有实例
- 对于每个已识别的实例，验证是否有任何硬编码的对称密钥
- 验证硬编码对称加密是否未用作唯一的加密方法

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#static-analysis)

识别代码中对称密钥加密的所有实例，并寻找加载或提供对称密钥的任何机制。您可以寻找：

- 对称算法（例如`DES`,`AES`等）
- 密钥生成器的规范（例如`KeyGenParameterSpec`, `KeyPairGeneratorSpec`, `KeyPairGenerator`, `KeyGenerator`,`KeyProperties`等）
- 类导入`java.security.*`, `javax.crypto.*`, `android.security.*`,`android.security.keystore.*`

对于每个已识别的实例，验证是否使用了对称密钥：

- 不是应用程序资源的一部分
- 不能从已知值导出
- 没有硬编码在代码中

对于每个硬编码的对称密钥，验证它没有在安全敏感的上下文中用作唯一的加密方法。

作为示例，我们说明了如何定位硬编码加密密钥的使用。首先[反汇编和反编译](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#disassembling-and-decompiling)应用程序以获取Java代码，例如使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)。

现在在文件中搜索`SecretKeySpec`该类的用法，例如通过简单地递归 grepping 或使用 jadx 搜索功能：

```
grep -r "SecretKeySpec"
```

这将返回所有使用该类的`SecretKeySpec`类。现在检查这些文件并跟踪哪些变量用于传递密钥材料。下图显示了对生产就绪应用程序执行此评估的结果。我们可以很清楚地定位到静态字节数组中硬编码和初始化的静态加密密钥的使用`Encrypt.keyBytes`。

![img](https://mas.owasp.org/assets/Images/Chapters/0x5e/static_encryption_key.png)

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#dynamic-analysis)

您可以对加密方法使用[方法跟踪](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)来确定输入/输出值，例如正在使用的密钥。在执行加密操作时监控文件系统访问，以评估密钥材料写入或读取的位置。例如，使用[RMS - Runtime Mobile Security](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#RMS-Runtime-Mobile-Security)的[API监控器](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security#8-api-monitor---android-only)监控文件系统。

## 测试加密标准算法的配置（MSTG-CRYPTO-2、MSTG-CRYPTO-3 和 MSTG-CRYPTO-4）[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-the-configuration-of-cryptographic-standard-algorithms-mstg-crypto-2-mstg-crypto-3-and-mstg-crypto-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#overview_1)

这些测试用例侧重于加密原语的实现和使用。应执行以下检查：

- 识别密码学原语的所有实例及其实现（库或自定义实现）
- 验证密码原语的使用方式和配置方式
- 验证是否出于安全目的不推荐使用加密协议和算法。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#static-analysis_1)

识别代码中加密原语的所有实例。识别所有自定义加密实现。您可以寻找：

- 类`Cipher`, `Mac`, `MessageDigest`,`Signature`
- 接口`Key`, `PrivateKey`, `PublicKey`,`SecretKey`
- 功能`getInstance`，`generateKey`
- 异常`KeyStoreException`，，`CertificateException`_`NoSuchAlgorithmException`
- 使用`java.security.*`、`javax.crypto.*`和包的`android.security.*`类。`android.security.keystore.*`

通过不指定它来识别对 getInstance 的所有调用都使用默认`provider`的安全服务（这意味着 AndroidOpenSSL aka Conscrypt）。`Provider`只能在`KeyStore`相关代码中指定（在那种情况下`KeyStore`应提供为`provider`）。如果`provider`指定了其他，则应根据情况和业务案例（即 Android API 版本）进行验证，并`provider`应对潜在漏洞进行检查。

确保遵循“[移动应用程序加密](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/)”一章中概述的最佳实践。查看[不安全和过时的算法](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#identifying-insecure-and/or-deprecated-cryptographic-algorithms)以及[常见的配置问题](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#common-configuration-issues)。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#dynamic-analysis_1)

您可以对加密方法使用[方法跟踪](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)来确定输入/输出值，例如正在使用的密钥。在执行加密操作时监控文件系统访问，以评估密钥材料写入或读取的位置。例如，使用[RMS - Runtime Mobile Security](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#RMS-Runtime-Mobile-Security)的[API监控器](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security#8-api-monitor---android-only)监控文件系统。

## 测试密钥的用途 (MSTG-CRYPTO-5)[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-the-purposes-of-keys-mstg-crypto-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#overview_2)

此测试用例侧重于验证目的和重复使用相同的加密密钥。应执行以下检查：

- 识别所有使用密码学的实例
- 确定加密材料的用途（保护使用中、传输中或静止的数据）
- 识别密码类型
- 验证是否根据其目的使用了密码学

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#static-analysis_2)

识别所有使用密码术的实例。您可以寻找：

- 类`Cipher`, `Mac`, `MessageDigest`,`Signature`
- 接口`Key`, `PrivateKey`, `PublicKey`,`SecretKey`
- 功能`getInstance`，`generateKey`
- 异常`KeyStoreException`，，`CertificateException`_`NoSuchAlgorithmException`
- 类导入`java.security.*`, `javax.crypto.*`, `android.security.*`,`android.security.keystore.*`

对于每个已识别的实例，确定其用途和类型。它可以用于：

- 用于加密/解密 - 确保数据机密性
- 用于签名/验证——确保数据的完整性（以及某些情况下的问责制）
- 维护 - 在某些敏感操作期间保护密钥（例如导入到 KeyStore）

此外，您应该确定使用已识别的加密实例的业务逻辑。

在验证期间，应执行以下检查：

- 是否根据创建时定义的目的使用所有密钥？（它与 KeyStore 密钥相关，可以定义 KeyProperties）
- 对于非对称密钥，私钥是否专门用于签名和公钥加密？
- 对称密钥用于多种用途吗？如果在不同的上下文中使用它，则应生成一个新的对称密钥。
- 是否根据其业务目的使用密码学？

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#dynamic-analysis_2)

您可以对加密方法使用[方法跟踪](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)来确定输入/输出值，例如正在使用的密钥。在执行加密操作时监控文件系统访问，以评估密钥材料写入或读取的位置。例如，使用[RMS - Runtime Mobile Security](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#RMS-Runtime-Mobile-Security)的[API监控器](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security#8-api-monitor---android-only)监控文件系统。

## 测试随机数生成 (MSTG-CRYPTO-6)[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-random-number-generation-mstg-crypto-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#overview_3)

此测试用例侧重于应用程序使用的随机值。应执行以下检查：

- 识别使用随机值的所有实例
- 验证随机数生成器是否不被认为是加密安全的
- 验证如何使用随机数生成器
- 验证生成的随机值的随机性

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#static-analysis_3)

识别随机数生成器的所有实例并查找自定义或众所周知的不安全类。例如，`java.util.Random`为每个给定的种子值生成相同的数字序列；因此，数字的顺序是可以预测的。相反，应该选择一个经过严格审查的算法，该算法当前被该领域的专家认为是强大的，并且应该使用经过充分测试的具有足够长度种子的实现。

`SecureRandom`标识不是使用默认构造函数创建的所有实例。指定种子值可能会降低随机性。更喜欢它的[无参数构造函数，`SecureRandom`](https://www.securecoding.cert.org/confluence/display/java/MSC02-J.+Generate+strong+random+numbers)它使用系统指定的种子值来生成一个 128 字节长的随机数。

一般来说，如果 PRNG 没有被宣传为密码安全（例如`java.util.Random`），那么它可能是统计 PRNG，不应在安全敏感的上下文中使用。如果生成器已知并且可以猜到种子，伪随机数生成器[可以生成可预测的数字。](https://www.securecoding.cert.org/confluence/display/java/MSC63-J.+Ensure+that+SecureRandom+is+properly+seeded)128 位种子是生成“足够随机”数字的良好起点。

一旦攻击者知道使用哪种类型的弱伪随机数生成器 (PRNG)，编写概念验证以根据先前观察到的随机值生成下一个随机值就很容易了，就像[对 Java Random 所做的那样](https://franklinta.com/2014/08/31/predicting-the-next-math-random-in-java/). 在非常弱的自定义随机生成器的情况下，可以从统计上观察模式。尽管推荐的方法无论如何都是反编译 APK 并检查算法（请参阅静态分析）。

如果你想测试随机性，你可以尝试捕获大量数字并使用 Burp 的[排序器](https://portswigger.net/burp/documentation/desktop/tools/sequencer)检查随机性的质量有多好。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#dynamic-analysis_3)

您可以对上述类和方法使用[方法跟踪来确定正在使用的输入/输出值。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#references)

- [#nelenkov] - N. Elenkov，Android Security Internals，No Starch Press，2014 年，第 5 章。

### 密码学参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#cryptography-references)

- Android 开发者博客：NDK 开发者的变化 - https://android-developers.googleblog.com/2016/06/android-changes-for-ndk-developers.html
- Android 开发者博客：不推荐使用加密提供程序 - https://android-developers.googleblog.com/2016/06/security-crypto-provider-deprecated-in.html
- Android 开发者博客：Android P 中的密码学变化 - https://android-developers.googleblog.com/2018/03/cryptography-changes-in-android-p.html
- Android 开发者博客：一些 SecureRandom 想法 - https://android-developers.googleblog.com/2013/08/some-securerandom-thoughts.html
- Android 开发者文档 - https://developer.android.com/guide
- BSI 建议 - https://www.keylength.com/en/8/
- Ida Pro - https://www.hex-rays.com/products/ida/
- 充气城堡军团 - https://www.bouncycastle.org/java.html
- NIST 密钥长度建议 - https://www.keylength.com/en/4/
- 安全提供商 - https://developer.android.com/reference/java/security/Provider.html
- 海绵城堡 - https://rtyley.github.io/spongycastle/

### 安全随机引用[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#securerandom-references)

- BurpProxy 定序器 - https://portswigger.net/burp/documentation/desktop/tools/sequencer
- SecureRandom 的正确播种 - https://www.securecoding.cert.org/confluence/display/java/MSC63-J.+Ensure+that+SecureRandom+is+properly+seeded

### 测试密钥管理参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-key-management-references)

- Android 钥匙串 API - https://developer.android.com/reference/android/security/KeyChain
- Android 密钥库 API - https://developer.android.com/reference/java/security/KeyStore.html
- Android Keystore 系统 - https://developer.android.com/training/articles/keystore#java
- Android Pie 功能和 API - https://developer.android.com/about/versions/pie/android-9.0#secure-key-import
- KeyInfo 文档 - https://developer.android.com/reference/android/security/keystore/KeyInfo
- SharedPreferences - https://developer.android.com/reference/android/content/SharedPreferences.html

### 关键认证参考[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#key-attestation-references)

- Android 密钥证明 - https://developer.android.com/training/articles/security-key-attestation
- 证明和断言 - https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API/Attestation_and_Assertion
- FIDO 联盟技术说明 - https://fidoalliance.org/fido-technotes-the-truth-about-attestation/
- FIDO 联盟白皮书 - https://fidoalliance.org/wp-content/uploads/Hardware-backed_Keystore_White_Paper_June2018.pdf
- 谷歌示例代码 - https://github.com/googlesamples/android-key-attestation/tree/master/server
- 验证 Android 密钥证明 - https://medium.com/@herrjemand/webauthn-fido2-verifying-android-keystore-attestation-4a8835b33e9d
- W3C Android 密钥证明 - https://www.w3.org/TR/webauthn/#android-key-attestation

#### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#owasp-masvs)

- MSTG-STORAGE-1：“需要使用系统凭证存储设施来存储敏感数据，例如 PII、用户凭证或加密密钥。”
- MSTG-CRYPTO-1：“该应用程序不依赖使用硬编码密钥的对称加密作为唯一的加密方法。”
- MSTG-CRYPTO-2：“该应用程序使用经过验证的加密原语实现。”
- MSTG-CRYPTO-3：“该应用程序使用适合特定用例的加密原语，并配置了符合行业最佳实践的参数。”
- MSTG-CRYPTO-4：“该应用程序不使用出于安全目的而被广泛认为已弃用的加密协议或算法。”
- MSTG-CRYPTO-5：“该应用程序不会出于多种目的重复使用相同的加密密钥。”
- MSTG-CRYPTO-6：“所有随机值都是使用足够安全的随机数生成器生成的。”
