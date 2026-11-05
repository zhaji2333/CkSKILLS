# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 2 · part 2

> 分段 2/2。索引见 `Android数据存储-p2.md`。

每次应用程序需要执行加密操作时，都需要用户的密码。要么每次都提示用户输入它，这不是理想的用户体验，要么只要用户通过身份验证，密码就会保存在内存中。将密码短语保存在内存中并不是最佳做法，因为任何加密材料只能在使用时保存在内存中。[如“清理密钥材料”](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cleaning-out-key-material)中所述，将密钥清零通常是一项非常具有挑战性的任务。

此外，请考虑从密码派生的密钥有其自身的弱点。例如，密码或密码短语可能会被用户重复使用或容易被猜到。请参阅[测试密码学章节](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#weak-key-generation-functions)以获取更多信息。

##### 清理密钥材料[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cleaning-out-key-material)

一旦不再需要密钥材料，就应将其从内存中清除。在使用垃圾收集器 (Java) 和不可变字符串（Swift、Objective-C、Kotlin）的语言中，真正清理秘密数据存在一定的局限性。[Java Cryptography Architecture Reference Guide](https://docs.oracle.com/en/java/javase/16/security/java-cryptography-architecture-jca-reference-guide.html#GUID-C9F76AFB-6B20-45A7-B84F-96756C8A94B4)建议使用`char[]`instead of`String`来存储敏感数据，并在使用后使数组无效。

请注意，某些密码没有正确清理其字节数组。例如，BouncyCastle 中的 AES 密码并不总是清理其最新的工作密钥，在内存中留下一些字节数组的副本。接下来，如果不付出额外的努力，就无法将基于 BigInteger 的密钥（例如私钥）从堆中移除或清零。清除字节数组可以通过编写一个实现[Destroyable](https://docs.oracle.com/javase/8/docs/api/javax/security/auth/Destroyable.html#destroy--)的包装器来实现。

##### 使用 ANDROID KEYSTORE API 存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-using-android-keystore-api)

更人性化和推荐的方法是使用[Android KeyStore API](https://developer.android.com/reference/java/security/KeyStore.html)系统（本身或通过 KeyChain）来存储密钥材料。如果可能，应使用硬件支持的存储。否则，它应该回退到 Android Keystore 的软件实现。但是，请注意，`AndroidKeyStore`在不同版本的 Android 中，API 已发生重大变化。在早期版本中，`AndroidKeyStore`API 仅支持存储公钥/私钥对（例如，RSA）。自 Android 6.0（API 级别 23）起才添加对称密钥支持。因此，开发人员需要处理不同的 Android API 级别以安全地存储对称密钥。

##### 通过使用其他密钥加密来存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-by-encrypting-them-with-other-keys)

为了在运行 Android 5.1（API 级别 22）或更低版本的设备上安全地存储对称密钥，我们需要生成一个公钥/私钥对。我们使用公钥加密对称密钥并将私钥存储在`AndroidKeyStore`. 加密的对称密钥可以使用 base64 编码并存储在`SharedPreferences`. 每当我们需要对称密钥时，应用程序都会从中检索私钥`AndroidKeyStore`并解密对称密钥。

信封加密或密钥包装是一种类似的方法，它使用对称加密来封装密钥材料。数据加密密钥 (DEK) 可以使用安全存储的密钥加密密钥 (KEK) 进行加密。加密的 DEK 可以存储在文件中`SharedPreferences`或写入文件。需要时，应用程序读取 KEK，然后解密 DEK。请参阅[OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html#encrypting-stored-keys)以了解有关加密密钥的更多信息。

此外，作为此方法的说明，请参阅[androidx.security.crypto 包中的 EncryptedSharedPreferences](https://developer.android.com/jetpack/androidx/releases/security)。

##### 存储密钥的不安全选项[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#insecure-options-to-store-keys)

存储加密密钥的安全性较低的方法是在 Android 的 SharedPreferences 中。使用[SharedPreferences](https://developer.android.com/reference/android/content/SharedPreferences.html)时，文件只能由创建它的应用程序读取。但是，在有Root设备上，任何其他具有根访问权限的应用程序都可以简单地读取其他应用程序的 SharedPreference 文件。AndroidKeyStore 不是这种情况。由于 AndroidKeyStore 访问是在内核级别管理的，因此需要相当多的工作和技巧才能在 AndroidKeyStore 不清除或破坏密钥的情况下绕过。

最后三个选项是在源代码中使用硬编码的加密密钥，具有可预测的混淆功能或基于稳定属性的密钥派生功能，并将生成的密钥存储在公共场所，如`/sdcard/`. 硬编码加密密钥是一个问题，因为这意味着应用程序的每个实例都使用相同的加密密钥。攻击者可以对应用程序的本地副本进行逆向工程以提取加密密钥，并使用该密钥解密任何设备上应用程序加密的任何数据。

接下来，当您具有基于标识符的可预测密钥派生函数时，其他应用程序可以访问该函数，攻击者只需找到 KDF 并将其应用于设备即可找到密钥。最后，公开存储加密密钥也是非常不鼓励的，因为其他应用程序可能有权读取公共分区并窃取密钥。

#### 第三方库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-libraries)

有几个不同的开源库提供特定于 Android 平台的加密功能。

- **[Java AES Crypto](https://github.com/tozny/java-aes-crypto)** - 一个简单的 Android 类，用于加密和解密字符串。
- **[SQL Cipher](https://www.zetetic.net/sqlcipher/sqlcipher-for-android/)** - SQLCipher 是 SQLite 的开源扩展，提供透明的 256 位 AES 数据库文件加密。
- **[Secure Preferences](https://github.com/scottyab/secure-preferences)** - Android Shared preference wrapper 比加密 Shared Preferences 的键和值。
- **[Themis](https://github.com/cossacklabs/themis)** - 一个跨平台的高级加密库，它在许多平台上提供相同的 API，用于在身份验证、存储、消息传递等过程中保护数据。

> 请记住，只要密钥未存储在 KeyStore 中，就始终可以轻松地在获得 root 权限的设备上检索密钥，然后解密您试图保护的值。

### 日志[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#logs)

在移动设备上创建日志文件有很多正当理由，例如跟踪崩溃、错误和使用情况统计信息。当应用程序离线时，日志文件可以存储在本地，并在应用程序在线时发送到端点。但是，记录敏感数据可能会将数据暴露给攻击者或恶意应用程序，并且还可能侵犯用户机密。您可以通过多种方式创建日志文件。以下列表包括两个可用于 Android 的类：

- [日志类](https://developer.android.com/reference/android/util/Log.html)
- [记录器类](https://developer.android.com/reference/java/util/logging/Logger.html)

### 备份[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#backups)

Android 为用户提供了自动备份功能。备份通常包括所有已安装应用程序的数据和设置副本。鉴于其多样化的生态系统，Android 支持许多备份选项：

- Stock Android 具有内置的 USB 备份功能。启用USB调试后，您可以使用该`adb backup`命令创建完整数据备份和应用程序数据目录的备份。
- Google 提供了“备份我的数据”功能，可以将所有应用程序数据备份到 Google 的服务器。
- 应用程序开发人员可以使用两个备份 API：
- [键/值备份](https://developer.android.com/guide/topics/data/keyvaluebackup.html)（备份 API 或 Android 备份服务）上传到 Android 备份服务云。
- [应用程序自动备份](https://developer.android.com/guide/topics/data/autobackup.html)：在 Android 6.0（API 级别 23）及更高版本中，Google 添加了“应用程序自动备份”功能。此功能会自动将最多 25MB 的应用程序数据与用户的 Google Drive 帐户同步。
- OEM 可能会提供其他选项。例如，HTC 设备有一个“HTC 备份”选项，激活后可以每天备份到云端。

应用程序必须小心确保敏感的用户数据不会在这些备份中结束，因为这可能允许攻击者提取它。

### 进程内存[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#process-memory)

Android 上的所有应用程序都使用内存来执行正常的计算操作，就像任何普通的现代计算机一样。因此，有时会在进程内存中执行敏感操作也就不足为奇了。出于这个原因，重要的是一旦处理了相关的敏感数据，就应该尽快将其从进程内存中清除。

可以通过内存转储和通过调试器实时分析内存来调查应用程序的内存。

这在“测试敏感数据的内存”部分中有进一步解释。

## 测试敏感数据的本地存储（MSTG-STORAGE-1 和 MSTG-STORAGE-2）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-local-storage-for-sensitive-data-mstg-storage-1-and-mstg-storage-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview)

此测试用例侧重于识别应用程序存储的潜在敏感数据并验证它是否安全存储。应执行以下检查：

- 分析源代码中的数据存储。
- 确保触发应用程序中所有可能的功能（例如，通过单击所有可能的地方）以确保数据生成。
- 检查所有应用程序生成和修改的文件，并确保存储方法足够安全。
- 这包括 SharedPreferences、SQL 数据库、Realm Databases、内部存储、外部存储等。

一般来说，存储在设备本地的敏感数据至少应该加密，并且任何用于加密方法的密钥都应该安全地存储在 Android Keystore 中。这些文件也应该存储在应用程序沙箱中。如果应用程序可以实现，敏感数据应该存储在设备之外，或者更好的是，根本不存储。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis)

首先，尝试确定 Android 应用程序使用的存储类型，并找出该应用程序是否以不安全的方式处理敏感数据。

- 检查`AndroidManifest.xml`读/写外部存储权限，例如，`uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"`.
- 检查用于存储数据的关键字和 API 调用的源代码：
- 文件权限，例如：
