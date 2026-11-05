# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 5 · part 2

> 分段 2/2。索引见 `Android数据存储-p5.md`。

## 测试内存中的敏感数据 (MSTG-STORAGE-10)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-memory-for-sensitive-data-mstg-storage-10)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_9)

分析内存可以帮助开发人员确定几个问题的根本原因，例如应用程序崩溃。但是，它也可用于访问敏感数据。本节介绍如何通过进程内存检查数据泄露。

首先识别存储在内存中的敏感信息。敏感资产可能已在某个时候加载到内存中。目的是验证此信息是否已尽可能简短地公开。

要调查应用程序的内存，您必须首先创建内存转储。您还可以实时分析内存，例如，通过调试器。无论采用何种方法，内存转储在验证方面都是一个非常容易出错的过程，因为每个转储都包含已执行函数的输出。您可能会错过执行关键场景。此外，除非您知道数据的足迹（确切值或数据格式），否则在分析过程中很可能会忽略数据。例如，如果应用程序使用随机生成的对称密钥进行加密，您可能无法在内存中发现它，除非您可以在另一个上下文中识别密钥的值。

因此，您最好从静态分析开始。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_9)

有关可能的数据泄露来源的概述，请在检查源代码之前查看文档并确定应用程序组件。例如，来自后端的敏感数据可能在 HTTP 客户端、XML 解析器等中。您希望尽快从内存中删除所有这些副本。

此外，了解应用程序的体系结构和体系结构在系统中的作用将帮助您识别根本不必暴露在内存中的敏感信息。例如，假设您的应用程序从一台服务器接收数据并在不进行任何处理的情况下将其传输到另一台服务器。该数据可以以加密格式处理，从而防止暴露在内存中。

但是，如果您需要公开内存中的敏感数据，则应确保您的应用程序设计为尽可能短地公开尽可能少的数据副本。换句话说，您希望集中处理敏感数据（即使用尽可能少的组件）并基于原始的、可变的数据结构。

后一个要求为开发人员提供了直接的内存访问权限。确保他们使用此访问权限用虚拟数据（通常为零）覆盖敏感数据。首选数据类型的示例包括`byte []`and `char []`，但不包括`String`or `BigInteger`。每当您尝试修改不可变对象（如`String`）时，您都会创建并更改该对象的副本。

`StringBuffer`使用像和这样的非原始可变类型`StringBuilder`可能是可以接受的，但它是指示性的，需要小心。类型 like`StringBuffer`用于修改内容（这是你想要做的）。但是，要访问此类类型的值，您将使用该`toString`方法，该方法将创建数据的不可变副本。有几种方法可以在不创建不可变副本的情况下使用这些数据类型，但它们比简单地使用原始数组需要更多的努力。安全内存管理是使用类似类型的好处之一`StringBuffer`，但这可能是一把两刃剑。如果您尝试修改其中一种类型的内容并且副本超出缓冲区容量，缓冲区大小将自动增加。缓冲区内容可能会被复制到不同的位置，使旧内容没有可用于覆盖它的引用。

不幸的是，很少有库和框架旨在允许覆盖敏感数据。例如，销毁一个密钥，如下所示，并没有真正从内存中删除该密钥：

Java 中的示例：

```
SecretKey secretKey = new SecretKeySpec("key".getBytes(), "AES");
secretKey.destroy();
```

Kotlin 中的示例：

```
val secretKey: SecretKey = SecretKeySpec("key".toByteArray(), "AES")
secretKey.destroy()
```

覆盖来自的支持字节数组`secretKey.getEncoded`也不会删除密钥；基于 SecretKeySpec 的密钥返回支持字节数组的副本。请参阅以下部分了解`SecretKey`从内存中删除 a 的正确方法。

RSA 密钥对基于`BigInteger`类型，因此在首次在`AndroidKeyStore`. 一些密码（例如 中的 AES `Cipher`）`BouncyCastle`没有正确清理它们的字节数组。

用户提供的数据（凭证、社会安全号码、信用卡信息等）是另一种可能暴露在内存中的数据。无论您是否将其标记为密码字段，都会通过界面`EditText`将内容传送到应用程序。`Editable`如果您的应用不提供`Editable.Factory`，用户提供的数据可能会在内存中暴露的时间超过必要的时间。默认`Editable`实现 ,导致与 Java和cause`SpannableStringBuilder`相同的问题（上面讨论过）。`StringBuilder``StringBuffer`

总之，在执行静态分析以识别暴露在内存中的敏感数据时，您应该：

- 尝试识别应用程序组件并映射数据的使用位置。
- 确保敏感数据由尽可能少的组件处理。
- 一旦不再需要包含敏感数据的对象，请确保正确删除对象引用。
- 确保在删除引用后请求垃圾回收。
- 确保敏感数据在不再需要时立即被覆盖。
- 不要用不可变数据类型（例如`String`和`BigInteger`）表示此类数据。
- 避免使用非原始数据类型（例如`StringBuilder`）。
- 在方法外部删除引用之前覆盖引用`finalize`。
- 注意第三方组件（库和框架）。公共 API 是很好的指标。确定公共 API 是否按照本章所述处理敏感数据。

**以下部分描述了内存中数据泄漏的陷阱以及避免它们的最佳实践。**

不要使用不可变结构（例如，`String`和`BigInteger`）来表示秘密。使这些结构无效：垃圾收集器可能会收集它们，但它们可能会在垃圾收集后保留在堆上。然而，您应该在每个关键操作（例如，加密、解析包含敏感信息的服务器响应）之后请求垃圾收集。当信息的副本没有被正确清理（如下所述）时，您的请求将有助于减少这些副本在内存中可用的时间长度。

要从内存中正确清除敏感信息，请将其存储在原始数据类型中，例如字节数组 ( `byte[]`) 和字符数组 ( `char[]`)。如上面“静态分析”部分所述，您应该避免将信息存储在可变的非原始数据类型中。

一旦不再需要对象，请确保覆盖关键对象的内容。用零覆盖内容是一种简单且非常流行的方法：

Java 中的示例：

```
byte[] secret = null;
try{
    //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        Arrays.fill(secret, (byte) 0);
    }
}
```

Kotlin 中的示例：

```
val secret: ByteArray? = null
try {
     //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        Arrays.fill(secret, 0.toByte())
    }
}
```

但是，这并不能保证内容会在Runtime(运行时)被覆盖。为了优化字节码，编译器会分析并决定不覆盖数据，因为它以后不会被使用（即，这是一个不必要的操作）。即使代码在已编译的 DEX 中，优化也可能发生在 VM 中的即时或提前编译期间。

这个问题没有灵丹妙药，因为不同的解决方案会产生不同的后果。例如，您可能会执行额外的计算（例如，将数据异或到虚拟缓冲区），但您无法知道编译器优化分析的范围。另一方面，在编译器范围之外使用被覆盖的数据（例如，在临时文件中序列化它）保证它会被覆盖，但显然会影响性能和维护。

然后，使用`Arrays.fill`覆盖数据是一个坏主意，因为该方法是一个明显的Hook目标（有关更多详细信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章）。

上述示例的最后一个问题是内容仅被零覆盖。您应该尝试用随机数据或非关键对象的内容覆盖关键对象。这将使构建能够根据其管理识别敏感数据的扫描仪变得非常困难。

下面是前面例子的改进版本：

Java 中的示例：

```
byte[] nonSecret = somePublicString.getBytes("ISO-8859-1");
byte[] secret = null;
try{
    //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        for (int i = 0; i < secret.length; i++) {
            secret[i] = nonSecret[i % nonSecret.length];
        }

        FileOutputStream out = new FileOutputStream("/dev/null");
        out.write(secret);
        out.flush();
        out.close();
    }
}
```

Kotlin 中的示例：

```
val nonSecret: ByteArray = somePublicString.getBytes("ISO-8859-1")
val secret: ByteArray? = null
try {
     //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        for (i in secret.indices) {
            secret[i] = nonSecret[i % nonSecret.size]
        }

        val out = FileOutputStream("/dev/null")
        out.write(secret)
        out.flush()
        out.close()
        }
}
```

有关详细信息，请查看[在 RAM 中安全存储敏感数据](https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/securely-store-sensitive-data-in-ram/)。

在“静态分析”部分中，我们提到了在使用`AndroidKeyStore`or时处理加密密钥的正确方法`SecretKey`。

为了更好地实现`SecretKey`，请查看`SecureSecretKey`下面的类。尽管该实现可能缺少一些使类与 兼容的样板代码`SecretKey`，但它解决了主要的安全问题：

- 不对敏感数据进行跨上下文处理。密钥的每个副本都可以从创建它的范围内清除。
- 根据上面给出的建议清除本地副本。

Java 中的示例：

```
  public class SecureSecretKey implements javax.crypto.SecretKey, Destroyable {
      private byte[] key;
      private final String algorithm;

      /** Constructs SecureSecretKey instance out of a copy of the provided key bytes.
        * The caller is responsible of clearing the key array provided as input.
        * The internal copy of the key can be cleared by calling the destroy() method.
        */
