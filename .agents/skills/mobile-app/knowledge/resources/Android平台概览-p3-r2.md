# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 3 · part 2

> 分段 2/2。索引见 `Android平台概览-p3.md`。

在开发过程中，应用程序使用自动生成的证书进行签名。此证书本质上是不安全的，仅用于调试。大多数商店不接受此类证书发布；因此，必须创建具有更安全特性的证书。当应用程序安装在 Android 设备上时，包管理器会确保它已使用相应 APK 中包含的证书进行签名。如果证书的公钥与用于签署设备上任何其他 APK 的密钥匹配，则新 APK 可能会与预先存在的 APK 共享一个 UID。这促进了来自单个供应商的应用程序之间的交互。或者，可以为签名保护级别指定安全权限；这将限制对使用相同密钥签名的应用程序的访问。

### APK 签名方案[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#apk-signing-schemes)

Android 支持三种应用程序签名方案。从 Android 9（API 级别 28）开始，可以使用 APK 签名方案 v3（v3 方案）、APK 签名方案 v2（v2 方案）或 JAR 签名（v1 方案）验证 APK。对于 Android 7.0（API 级别 24）及更高版本，可以使用 APK 签名方案 v2（v2 方案）或 JAR 签名（v1 方案）验证 APK。为了向后兼容，可以使用多个签名方案对 APK 进行签名，以使应用程序在新旧 SDK 版本上运行。[旧平台忽略 v2 签名并仅验证 v1 签名](https://source.android.com/security/apksigning/)。

#### JAR 签名（v1 方案）[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#jar-signing-v1-scheme)

应用签名的原始版本将签名的 APK 作为标准签名的 JAR 实现，它必须包含`META-INF/MANIFEST.MF`. 所有文件都必须使用通用证书进行签名。此方案不保护 APK 的某些部分，例如 ZIP 元数据。该方案的缺点是APK验证者在应用签名之前需要处理不可信的数据结构，验证者丢弃数据结构不覆盖的数据。此外，APK 验证程序必须解压缩所有压缩文件，这会占用大量时间和内存。

#### APK签名方案（v2方案）[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#apk-signature-scheme-v2-scheme)

使用 APK 签名方案，对完整的 APK 进行哈希处理和签名，然后创建 APK 签名块并将其插入到 APK 中。在验证期间，v2 方案会检查整个 APK 文件的签名。这种形式的 APK 验证速度更快，并提供更全面的修改保护。下面可以看到[v2 Scheme的APK签名验证过程](https://source.android.com/security/apksigning/v2#verification)。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/apk-validation-process.png)

#### APK 签名方案（v3 方案）[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#apk-signature-scheme-v3-scheme)

v3 APK 签名块格式与 v2 相同。V3 将有关受支持的 SDK 版本的信息和旋转证明结构添加到 APK 签名块。在 Android 9（API 级别 28）及更高版本中，可以根据 APK 签名方案 v3、v2 或 v1 方案验证 APK。旧平台忽略 v3 签名并尝试验证 v2 然后 v1 签名。

签名块的签名数据中的 proof-of-rotation 属性由一个单链表组成，每个节点包含一个签名证书，用于签署应用程序的先前版本。为了使向后兼容工作，旧的签名证书签署新的证书集，从而为每个新密钥提供证据表明它应该与旧密钥一样受信任。不再可能独立地签署 APK，因为旋转证明结构必须让旧的签名证书签署新的证书集，而不是一个一个地签署它们。下面可以看到[APK签名v3方案验证过程](https://source.android.com/security/apksigning/v3)。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/apk-validation-process-v3-scheme.png)

#### APK 签名方案（v4 方案）[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#apk-signature-scheme-v4-scheme)

APK 签名方案 v4 与 Android 11（API 级别 30）一起引入，并要求所有搭载 Android 11 及更高版本的设备默认启用[fs-verity 。](https://www.kernel.org/doc/html/latest/filesystems/fsverity.html)fs-verity 是一项 Linux 内核功能，由于其极其高效的文件哈希计算，主要用于文件身份验证（检测恶意修改）。如果内容根据在引导期间加载到内核密钥环的受信任数字证书进行验证，则只读请求将成功。

v4 签名需要一个互补的 v2 或 v3 签名，与以前的签名方案相比，v4 签名存储在一个单独的文件`<apk name>.apk.idsig`中。`--v4-signature-file`请记住在使用验证 v4 签名的 APK 时使用标志指定它`apksigner verify`。

[您可以在Android 开发人员文档](https://source.android.com/security/apksigning/v4)中找到更多详细信息。

#### 创建您的证书[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#creating-your-certificate)

Android 使用公共/私有证书来签署 Android 应用程序（.apk 文件）。证书是信息包；就安全性而言，密钥是该捆绑包中最重要的部分。公用证书包含用户的公钥，私用证书包含用户的私钥。公共证书和私有证书是链接在一起的。证书是唯一的，不能重新生成。请注意，如果证书丢失，则无法恢复，因此无法更新任何使用该证书签名的应用程序。应用程序创建者可以重复使用可用密钥库中的现有私钥/公钥对，也可以生成新的一对。在 Android SDK 中，生成了一个新的密钥对`keytool`命令。以下命令创建一个 RSA 密钥对，密钥长度为 2048 位，到期时间为 7300 天 = 20 年。生成的密钥对存储在文件“myKeyStore.jks”中，该文件位于当前目录中：

```
keytool -genkey -alias myDomain -keyalg RSA -keysize 2048 -validity 7300 -keystore myKeyStore.jks -storepass myStrongPassword
```

安全地存储您的密钥并确保它在其整个生命周期中保持秘密是至关重要的。任何获得密钥访问权限的人都可以使用您无法控制的内容发布您的应用程序更新（从而添加不安全的功能或使用基于签名的权限访问共享内容）。用户对应用程序及其开发者的信任完全基于此类证书；因此，证书保护和安全管理对于声誉和客户保留至关重要，绝不能与其他人共享密钥。密钥存储在可以用密码保护的二进制文件中；此类文件称为*KeyStore*. KeyStore 密码应该是强密码并且只有密钥创建者知道。因此，密钥通常存储在开发人员访问权限有限的专用构建机器上。Android 证书的有效期必须长于关联应用（包括应用的更新版本）的有效期。例如，Google Play 将要求证书至少在 2033 年 10 月 22 日之前保持有效。

#### 签署申请[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#signing-an-application)

签名过程的目标是将应用程序文件 (.apk) 与开发人员的公钥相关联。为此，开发人员计算 APK 文件的哈希值并使用他们自己的私钥对其进行加密。然后，第三方可以通过使用作者的公钥解密加密的哈希值并验证它与 APK 文件的实际哈希值匹配来验证应用程序的真实性（例如，应用程序确实来自声称是发起者的用户的事实） .

许多集成开发环境 (IDE) 集成了应用程序签名过程，以方便用户使用。请注意，某些 IDE 在配置文件中以明文形式存储私钥；仔细检查以防其他人能够访问此类文件并在必要时删除这些信息。可以使用 Android SDK（API 级别 24 及更高）提供的“apksigner”工具从命令行对应用程序进行签名。它位于`[SDK-Path]/build-tools/[version]`。对于 API 24.0.2 及更低版本，您可以使用“jarsigner”，它是 Java JDK 的一部分。整个过程的细节可以参考Android官方文档；但是，下面给出了一个例子来说明这一点。

```
apksigner sign --out mySignedApp.apk --ks myKeyStore.jks myUnsignedApp.apk
```

在此示例中，未签名的应用程序（“myUnsignedApp.apk”）将使用来自开发人员密钥库“myKeyStore.jks”（位于当前目录）的私钥进行签名。该应用程序将成为名为“mySignedApp.apk”的签名应用程序，并准备好发布到商店。

##### ZIPALIGN[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#zipalign)

该`zipalign`工具应始终用于在分发前对齐 APK 文件。此工具对齐 APK 内的所有未压缩数据（例如图像、原始文件和 4 字节边界），这有助于改进应用Runtime(运行时)的内存管理。

> 在使用 apksigner 对 APK 文件进行签名之前，必须使用 Zipalign。

### 发布过程[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#publishing-process)

由于 Android 生态系统是开放的，因此可以从任何地方（您自己的站点、任何商店等）分发应用程序。然而，Google Play 是最知名、最受信任和最受欢迎的商店，并且由 Google 自己提供。Amazon Appstore 是 Kindle 设备值得信赖的默认商店。如果用户想要从不受信任的来源安装第三方应用程序，他们必须在他们的设备安全设置中明确允许这样做。

应用程序可以通过多种来源安装到 Android 设备上：通过 USB 在本地安装、通过 Google 的官方应用程序商店 (Google Play Store) 或从其他商店安装。

其他供应商可能会在实际发布应用程序之前对其进行审查和批准，而谷歌只会扫描已知的恶意软件签名；这最大限度地减少了发布过程开始和公共应用程序可用之间的时间。

发布应用程序非常简单；主要操作是使已签名的 APK 文件可下载。在 Google Play 上，发布从创建帐户开始，然后是通过专用界面交付应用程序。详细信息可在[官方 Android 文档](https://play.google.com/console/about/guides/releasewithconfidence/)中找到。

## Android 应用程序攻击面[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-application-attack-surface)

Android 应用程序攻击面由应用程序的所有组件组成，包括发布应用程序和支持其功能所需的支持材料。如果 Android 应用程序不满足以下条件，则它可能容易受到攻击：

- 通过 IPC 通信或 URL 方案验证所有输入，另请参阅：
