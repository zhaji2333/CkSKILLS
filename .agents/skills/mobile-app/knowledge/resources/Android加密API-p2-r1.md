# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 2 · part 1

> 分段 1/2。索引见 `Android加密API-p2.md`。

# Android 加密 API[¶](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#android-cryptographic-apis) · part 2

> 分段 2/2。索引见 `Android加密API.md`。

## 承接

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

