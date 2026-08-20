# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview)

本章从架构的角度介绍Android平台。讨论了以下五个关键领域：

1. Android架构
2. Android 安全：纵深防御方法
3. Android应用结构
4. Android应用发布
5. Android 应用程序攻击面

有关 Android 平台的更多详细信息，请访问官方[Android 开发人员文档网站](https://developer.android.com/index.html)。

## Android架构[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-architecture)

[Android是由](https://en.wikipedia.org/wiki/Android_(operating_system))[开放手机联盟](https://www.openhandsetalliance.com/)（由 Google 牵头的联盟）开发的基于 Linux 的开源平台，用作移动操作系统 (OS)。今天，该平台是各种现代技术的基础，例如手机、平板电脑、可穿戴技术、电视和其他智能设备。典型的 Android 构建附带一系列预安装（“库存”）应用程序，并支持通过 Google Play 商店和其他市场安装第三方应用程序。

Android 的软件堆栈由几个不同的层组成。每一层定义接口并提供特定服务。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/android_software_stack.png)

**内核(Kernel)：**在最低级别，Android 基于[Linux 内核的变体，](https://source.android.com/devices/architecture/kernel)其中包含一些重要的附加功能，包括[Low Memory Killer](https://source.android.com/devices/tech/perf/lmkd)、唤醒锁、[Binder IPC](https://source.android.com/devices/architecture/hidl/binder-ipc)驱动程序等。为了 MASTG 的目的，我们将重点关注操作系统的用户模式部分，其中 Android 与典型的 Linux 发行版有很大不同。对我们来说最重要的两个组件是应用程序使用的托管Runtime(运行时) (ART/Dalvik) 和[Bionic](https://en.wikipedia.org/wiki/Bionic_(software))，Android 版本的 glibc，GNU C 库。

**HAL：**在内核之上，硬件抽象层 (HAL) 定义了一个标准接口，用于与内置硬件组件进行交互。多个 HAL 实现被打包到 Android 系统在需要时调用的共享库模块中。这是允许应用程序与设备硬件交互的基础。例如，它允许普通电话应用程序使用设备的麦克风和扬声器。

**Runtime(运行时)环境(Runtime Environment)：** Android 应用程序是用 Java 和 Kotlin 编写的，然后编译为[Dalvik 字节码](https://source.android.com/devices/tech/dalvik/dalvik-bytecode)，然后可以使用解释字节码指令并在目标设备上执行它们的Runtime(运行时)来执行。对于 Android，这是[Android Runtime (ART)](https://source.android.com/devices/tech/dalvik/configure#how_art_works)。这类似于用于 Java 应用程序的[JVM（Java 虚拟机）](https://en.wikipedia.org/wiki/Java_virtual_machine)或用于 .NET 应用程序的 Mono Runtime。

Dalvik 字节码是 Java 字节码的优化版本。它是通过首先将 Java 或 Kotlin 代码编译为 Java 字节码来创建的，分别使用 javac 和 kotlinc 编译器生成 .class 文件。最后，使用 d8 工具将 Java 字节码转换为 Dalvik 字节码。Dalvik 字节码以 .dex 文件的形式打包在 APK 和 AAB 文件中，并由 Android 上的托管Runtime(运行时)使用以在设备上执行它。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/java_vs_dalvik.png)

在 Android 5.0（API 级别 21）之前，Android 在 Dalvik 虚拟机 (DVM) 上执行字节码，并在执行时将其转换为机器代码，这一过程称为*即时*(JIT) 编译。这使Runtime(运行时)能够受益于编译代码的速度，同时保持代码解释的灵活性。

从 Android 5.0（API 级别 21）开始，Android 在 Android Runtime (ART) 上执行字节码，它是 DVM 的后继者。ART 通过包含 Java 和Native堆栈信息，在应用程序Native崩溃报告中提供改进的性能和上下文信息。它使用相同的 Dalvik 字节码输入来保持向后兼容性。然而，ART 以不同的方式执行 Dalvik 字节码，它使用*提前*(AOT)、*即时*(JIT) 和配置文件引导编译的混合组合。

- **AOT**将 Dalvik 字节码预编译为Native代码，生成的代码将以 .oat 扩展名（ELF 二进制文件）保存在磁盘上。dex2oat 工具可用于执行编译，可在 Android 设备上的 /system/bin/dex2oat 中找到。AOT 编译是在应用程序安装过程中执行的。这使得应用程序启动更快，因为不再需要编译。但是，这也意味着与 JIT 编译相比安装时间增加了。此外，由于应用程序总是针对当前版本的操作系统进行优化，这意味着软件更新将重新编译所有以前编译的应用程序，从而导致系统更新时间显着增加。最后，AOT 编译将编译整个应用程序，即使某些部分从未被用户使用过。
- **JIT**发生在Runtime(运行时)。
- **Profile-guided compilation**是 Android 7（API 级别 24）中引入的一种混合方法，用于克服 AOT 的缺点。起初，应用程序将使用 JIT 编译，Android 会跟踪应用程序中所有经常使用的部分。此信息存储在应用程序配置文件中，当设备空闲时，编译 (dex2oat) 守护程序运行，AOT 编译配置文件中识别出的频繁代码路径。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/java2oat.png)

来源：[https ://lief-project.github.io/doc/latest/tutorials/10_android_formats.html](https://lief-project.github.io/doc/latest/tutorials/10_android_formats.html)

**沙盒(Sandboxing)：**Android 应用程序无法直接访问硬件资源，每个应用程序都在自己的虚拟机或沙箱中运行。这使操作系统能够精确控制设备上的资源和内存访问。例如，崩溃的应用程序不会影响同一设备上运行的其他应用程序。Android 控制分配给应用程序的最大系统资源数量，防止任何一个应用程序独占过多资源。同时，这种沙盒设计也可以认为是Android全局纵深防御策略中的众多原则之一。具有低权限的恶意第三方应用程序不应该能够逃脱自己的Runtime(运行时)并读取同一设备上受害应用程序的内存。在下一节中，我们将仔细研究 Android 操作系统中的不同防御层。[“软件隔离”](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#software-isolation)。

[您可以在 Google Source 文章“Android Runtime (ART)”](https://source.android.com/devices/tech/dalvik/configure#how_art_works)、[Jonathan Levin 的“Android Internals”](http://newandroidbook.com/)和[@_qaz_qaz 的博文“Android 101”](https://secrary.com/android-reversing/android101/)中找到更多详细信息。

## Android 安全：纵深防御方法[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-security-defense-in-depth-approach)

Android 架构实现了不同的安全层，这些安全层共同支持纵深防御方法。这意味着敏感用户数据或应用程序的机密性、完整性或可用性并不取决于单一的安全措施。本节概述了 Android 系统提供的不同防御层。安全策略可以粗略地分为四个不同的领域，每个领域都侧重于防止某些攻击模型。

- 系统级安全(System-wide security)
- 软件隔离(Software isolation)
- 网络安全(Network security)
- 反剥削(Anti-exploitation)

### 系统级安全[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#system-wide-security)

#### 设备加密[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#device-encryption)

Android 从 Android 2.3.4（API 级别 10）开始支持设备加密，并且从那时起它经历了一些重大变化。谷歌强制要求所有运行 Android 6.0（API 级别 23）或更高版本的设备都必须支持存储加密，尽管一些低端设备被豁免，因为这会显着影响它们的性能。

- [全盘加密 (FDE)](https://source.android.com/security/encryption/full-disk)：Android 5.0（API 级别 21）及更高版本支持全盘加密。此加密使用受用户设备密码保护的单个密钥来加密和解密用户数据分区。这种加密现在被认为已弃用，应尽可能使用基于文件的加密。全盘加密有缺点，如不输入密码解锁无法接听电话或重启后无操作报警。
- [基于文件的加密 (FBE)](https://source.android.com/security/encryption/file-based)：Android 7.0（API 级别 24）支持基于文件的加密。基于文件的加密允许使用不同的密钥对不同的文件进行加密，以便它们可以独立解密。支持此类加密的设备也支持直接启动。直接启动使设备能够访问警报或无障碍服务等功能，即使用户没有解锁设备也是如此。

> 注意：您可能听说过[Adiantum](https://github.com/google/adiantum)，这是一种加密方法，专为运行 Android 9（API 级别 28）及更高版本且 CPU 缺少 AES 指令的设备而设计。**Adiantum 仅与 ROM 开发人员或设备供应商相关**，Android 不提供 API 供开发人员从应用程序使用 Adiantum。根据 Google 的建议，在运送带有 ARMv8 加密扩展的基于 ARM 的设备或带有 AES-NI 的基于 x86 的设备时，不应使用 Adiantum。AES 在这些平台上更快。
>
> [Android 文档](https://source.android.com/security/encryption/adiantum)中提供了更多信息。

#### 可信执行环境 (TEE)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#trusted-execution-environment-tee)

为了让 Android 系统执行加密，它需要一种方法来安全地生成、导入和存储加密密钥。我们实质上是将保持敏感数据安全的问题转移到保持加密密钥安全上。如果攻击者可以转储或猜测加密密钥，则可以检索敏感的加密数据。

Android 在专用硬件中提供可信执行环境，以解决安全生成和保护密钥的问题。这意味着 Android 系统中的专用硬件组件负责处理加密密钥材料。三个主要模块负责：

- [硬件支持的密钥库](https://source.android.com/security/keystore)：该模块为 Android 操作系统和第三方应用程序提供加密服务。它使应用程序能够在 TEE 中执行加密敏感操作，而不会暴露加密密钥材料。
- [StrongBox](https://developer.android.com/training/articles/keystore#HardwareSecurityModule)：在 Android 9 (Pie) 中，引入了 StrongBox，这是另一种实现硬件支持的 KeyStore 的方法。在 Android 9 Pie 之前，硬件支持的 KeyStore 可以是位于 Android 操作系统内核之外的任何 TEE 实现。StrongBox是一个真正完整的独立硬件芯片，添加到实现KeyStore的设备上，在Android文档中有明确的定义。您可以通过编程方式检查密钥是否驻留在 StrongBox 中，如果存在，您可以确定它受到硬件安全模块的保护，该模块具有自己的 CPU、安全存储和真随机数生成器 (TRNG)。所有敏感的加密操作都发生在这个芯片上，在 StrongBox 的安全边界内。
- [GateKeeper](https://source.android.com/security/authentication/gatekeeper)：GateKeeper 模块启用设备模式和密码身份验证。身份验证过程中的安全敏感操作发生在设备上可用的 TEE 内。GateKeeper 由三个主要组件组成，(1)`gatekeeperd`它是公开 GateKeeper 的服务，(2) GateKeeper HAL，它是硬件接口，(3) TEE 实现，它是在 TEE 中实现 GateKeeper 功能的实际软件。

#### 验证启动[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#verified-boot)

我们需要有一种方法来确保在 Android 设备上执行的代码来自可信源并且其完整性不会受到损害。为了实现这一点，Android 引入了验证启动的概念。验证启动的目标是在硬件和在该硬件上执行的实际代码之间建立信任关系。在经过验证的引导序列中，建立了一条完整的信任链，从受硬件保护的信任根 (RoT) 开始，直到运行的最终系统，通过并验证所有必需的引导阶段。当Android系统最终启动时，您可以放心，系统没有被篡改。您有密码证明正在运行的代码是 OEM 预期的代码，而不是被恶意或意外更改的代码。

[Android 文档](https://source.android.com/security/verifiedboot)中提供了更多信息。

### 软件隔离[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#software-isolation)

#### Android 用户和群组[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-users-and-groups)

尽管 Android 操作系统基于 Linux，但它并不像其他类 Unix 系统那样实现用户帐户。在 Android 中，Linux 内核的多用户支持用于沙盒应用程序：除了少数例外，每个应用程序都像在一个单独的 Linux 用户下运行一样，与其他应用程序和操作系统的其余部分有效隔离。

文件[系统/core/include/private/android_filesystem_config.h](http://androidxref.com/9.0.0_r3/xref/system/core/include/private/android_filesystem_config.h)包含系统进程分配给的预定义用户和组的列表。其他应用程序的 UID（用户 ID）在安装时添加。有关详细信息，请查看 Bin Chen关于 Android 沙盒的[博客文章。](https://pierrchen.blogspot.mk/2016/09/an-walk-through-of-android-uidgid-based.html)

例如，Android 9.0（API 级别 28）定义了以下系统用户：

```
    #define AID_ROOT             0  /* traditional unix root user */
    #...
    #define AID_SYSTEM        1000  /* system server */
    #...
    #define AID_SHELL         2000  /* adb and debug shell user */
    #...
    #define AID_APP_START          10000  /* first app user */
    ...
```

#### SELinux[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#selinux)

Security-Enhanced Linux (SELinux) 使用强制访问控制 (MAC) 系统进一步锁定哪些进程应该访问哪些资源。每个资源都被赋予一个标签，标签的形式`user:role:type:mls_level`定义了哪些用户能够对其执行哪些类型的操作。例如，一个进程可能只能读取一个文件，而另一个进程可能能够编辑或删除该文件。这样，通过遵循最小特权原则，易受攻击的进程更难以通过特权升级或横向移动进行利用。

[Android 文档](https://source.android.com/security/selinux)中提供了更多信息。

#### 权限[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#permissions)

Android 实现了一个广泛的权限系统，用作访问控制机制。它确保对敏感用户数据和设备资源的访问受控。Android 将权限分为不同的[类型](https://developer.android.com/guide/topics/permissions/overview#types)，提供不同的保护级别。

> 在 Android 6.0（API 级别 23）之前，应用请求的所有权限都是在安装时授予的（安装时权限）。从 API 级别 23 开始，用户必须在Runtime(运行时)批准一些权限请求（Runtime(运行时)权限）。

[Android 文档](https://developer.android.com/guide/topics/permissions/overview)中提供了更多信息，包括一些[注意事项](https://developer.android.com/training/permissions/evaluating)和[最佳实践](https://developer.android.com/training/permissions/usage-notes)。

要了解如何测试应用程序权限，请参阅“Android 平台 API”一章中的[测试应用程序权限](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-app-permissions-mstg-platform-1)部分。

### 网络安全[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#network-security)

#### 默认 TLS[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#tls-by-default)

默认情况下，自 Android 9（API 级别 28）起，所有网络活动都被视为在敌对环境中执行。这意味着 Android 系统将只允许应用程序通过使用传输层安全 (TLS) 协议建立的网络通道进行通信。该协议有效地加密所有网络流量并创建到服务器的安全通道。出于遗留原因，您可能希望使用畅通的交通连接。这可以通过调整`res/xml/network_security_config.xml`应用程序中的文件来实现。

[Android 文档](https://developer.android.com/training/articles/security-config.html)中提供了更多信息。

#### 通过 TLS 的 DNS[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#dns-over-tls)

自 Android 9（API 级别 28）以来，系统范围的 DNS over TLS 支持已被引入。它允许您使用 TLS 协议对 DNS 服务器执行查询。与发送 DNS 查询的 DNS 服务器建立安全通道。这可确保在 DNS 查找期间不会暴露任何敏感数据。

[Android 开发者博客](https://android-developers.googleblog.com/2018/04/dns-over-tls-support-in-android-p.html)上提供了更多信息。

### 反剥削[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#anti-exploitation)

#### ASLR、KASLR、PIE 和 DEP[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#aslr-kaslr-pie-and-dep)

地址空间布局随机化 (ASLR) 自 Android 4.1（API 级别 15）以来一直是 Android 的一部分，是针对缓冲区溢出攻击的标准保护，它确保应用程序和操作系统都加载到随机内存地址，从而很难获得特定内存区域或库的正确地址。在 Android 8.0（API 级别 26）中，这种保护也针对内核（KASLR）实现了。只有当应用程序可以加载到内存中的随机位置时，ASLR 保护才有可能，这由应用程序的位置独立可执行文件 (PIE) 标志指示。自 Android 5.0（API 级别 21）起，不再支持未启用 PIE 的Native库(NATIVE LIBRARIES)。最后，数据执行保护 (DEP) 可防止堆栈和堆上的代码执行，这也用于打击缓冲区溢出攻击。

[Android 开发者博客](https://android-developers.googleblog.com/2016/07/protecting-android-with-more-linux.html)上提供了更多信息。

#### SECCOMP过滤器[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#seccomp-filter)

Android 应用程序可以包含用 C 或 C++ 编写的Native代码。这些已编译的二进制文件既可以通过 Java Native接口 (JNI) 绑定与 Android Runtime(运行时)通信，也可以通过系统调用与操作系统通信。一些系统调用要么没有实现，要么不应该被普通应用程序调用。由于这些系统调用直接与内核通信，因此它们是漏洞开发人员的主要目标。在 Android 8（API 级别 26）中，Android 为所有基于 Zygote 的进程（即用户应用程序）引入了对安全计算 (SECCOMP) 过滤器的支持。这些过滤器将可用的系统调用限制为通过Bionic公开的系统调用。

[Android 开发者博客](https://android-developers.googleblog.com/2017/07/seccomp-filter-in-android-o.html)上提供了更多信息。

## Android应用结构[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-application-structure)

### 与操作系统的通信[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#communication-with-the-operating-system)

Android 应用程序通过 Android Framework 与系统服务交互，Android Framework 是一个提供高级 Java API 的抽象层。这些服务中的大部分是通过普通的 Java 方法调用调用的，并被转换为对在后台运行的系统服务的 IPC 调用。系统服务的例子包括：

- 连接性（Wi-Fi、蓝牙、NFC 等）
- 文件
- 相机
- 地理定位 (GPS)
- 麦克风

该框架还提供常见的安全功能，例如密码学。

API 规范随每个新的 Android 版本而变化。关键错误修复和安全补丁通常也适用于早期版本。

值得注意的 API 版本：

- 2012 年 11 月 Android 4.2（API 级别 16）（引入 SELinux）
- 2013 年 7 月的 Android 4.3（API 级别 18）（默认启用 SELinux）
- 2013 年 10 月的 Android 4.4（API 级别 19）（引入了几个新的 API 和 ART）
- 2014 年 11 月的 Android 5.0（API 级别 21）（默认使用 ART 并添加了许多其他功能）
- 2015 年 10 月的 Android 6.0（API 级别 23）（许多新功能和改进，包括授予；在Runtime(运行时)详细设置权限，而不是在安装期间设置全部或全部）
- 2016 年 8 月的 Android 7.0（API 级别 24-25）（ART 上的新 JIT 编译器）
- 2017 年 8 月的 Android 8.0（API 级别 26-27）（大量安全改进）
- 2018 年 8 月 Android 9（API 级别 28）（限制后台使用麦克风或摄像头，引入锁定模式，所有应用程序默认 HTTPS）
- **2019 年 9 月的Android 10（API 级别 29）**（“仅在使用应用程序时”访问位置、防止设备跟踪、改进安全外部存储、）
- 隐私（[概述](https://developer.android.com/about/versions/10/highlights#privacy_for_users)，[细节 1](https://developer.android.com/about/versions/10/privacy)，[细节 2](https://developer.android.com/about/versions/10/privacy/changes)）
- 安全性（[概述](https://developer.android.com/about/versions/10/highlights#security)，[细节](https://developer.android.com/about/versions/10/behavior-changes-all#security)）
- **2020 年 9 月的Android 11（API 级别 30）**（范围存储实施、权限自动重置、[降低包可见性](https://developer.android.com/training/package-visibility)、APK 签名方案 v4）
- 隐私（[概述](https://developer.android.com/about/versions/11/privacy)）
- [隐私行为更改（所有应用程序）](https://developer.android.com/about/versions/11/behavior-changes-all)
- [安全行为更改（所有应用程序）](https://developer.android.com/about/versions/11/behavior-changes-all#security)
- [隐私行为变化（应用定位版本）](https://developer.android.com/about/versions/11/behavior-changes-11#privacy)
- [安全行为更改（应用程序定位版本）](https://developer.android.com/about/versions/11/behavior-changes-11#security)
- **2021 年 8 月的Android 12（API 级别 31-32）**（Material You、Web 意图解析、隐私仪表板）
- [安全和隐私](https://developer.android.com/about/versions/12/features#security-privacy)
- [行为改变（所有应用）](https://developer.android.com/about/versions/12/behavior-changes-all#security-privacy)
- [行为变化（应用定位版本）](https://developer.android.com/about/versions/12/behavior-changes-12#security-privacy)
- [BETA] 2022 年的**Android 13（API 级别 33）**（更安全地导出上下文注册的接收器，新的照片选择器）
- [安全和隐私](https://developer.android.com/about/versions/13/features#privacy-security)
- [隐私行为更改（所有应用程序）](https://developer.android.com/about/versions/13/behavior-changes-all#privacy)
- [安全行为更改（所有应用程序）](https://developer.android.com/about/versions/13/behavior-changes-all#security)
- [隐私行为变化（应用定位版本）](https://developer.android.com/about/versions/13/behavior-changes-13#privacy)
- [安全行为更改（应用程序定位版本）](https://developer.android.com/about/versions/13/behavior-changes-13#security)

### 应用程序沙箱[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#the-app-sandbox)

应用程序在 Android 应用程序沙箱中执行，它将应用程序数据和代码执行与设备上的其他应用程序分开。如前所述，这种分离增加了第一层防御。

安装新应用程序会创建一个以应用程序包命名的新目录，其路径如下：`/data/data/[package-name]`. 该目录保存应用程序的数据。设置 Linux 目录权限，以便只能使用应用程序的唯一 UID 读取和写入目录。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/Selection_003.png)

我们可以通过查看文件`/data/data`夹中的文件系统权限来确认这一点。例如，我们可以看到 Google Chrome 和 Calendar 各自分配了一个目录，并在不同的用户帐户下运行：

```
drwx------  4 u0_a97              u0_a97              4096 2017-01-18 14:27 com.android.calendar
drwx------  6 u0_a120             u0_a120             4096 2017-01-19 12:54 com.android.chrome
```

希望他们的应用程序共享一个公共沙箱的开发人员可以避开沙箱。当两个应用程序使用相同的证书签名并明确共享相同的用户 ID（在其*AndroidManifest.xml文件中具有**sharedUserId*）时，每个应用程序都可以访问对方的数据目录。请参阅以下示例以在 NFC 应用程序中实现此目的：

```
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
  package="com.android.nfc"
  android:sharedUserId="android.uid.nfc">
```

#### Linux 用户管理[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#linux-user-management)

Android 利用 Linux 用户管理来隔离应用程序。这种方法不同于传统 Linux 环境中的用户管理用法，在传统 Linux 环境中，多个应用程序通常由同一用户运行。Android 为每个 Android 应用程序创建一个唯一的 UID，并在单独的进程中运行该应用程序。因此，每个应用程序只能访问自己的资源。这种保护由 Linux 内核强制执行。

通常，为应用分配的 UID 范围为 10000 到 99999。Android 应用根据其 UID 接收用户名。例如，UID 为 10188 的应用收到用户名`u0_a188`。如果应用程序请求的权限被授予，则相应的组 ID 将添加到应用程序的进程中。比如下面这个app的用户ID是10188，属于组ID 3003（inet）。该组与 android.permission.INTERNET 权限相关。命令的输出`id`如下所示。

```
$ id
uid=10188(u0_a188) gid=10188(u0_a188) groups=10188(u0_a188),3003(inet),
9997(everybody),50188(all_a188) context=u:r:untrusted_app:s0:c512,c768
```

组 ID 和权限之间的关系定义在以下文件中：

[框架/基础/数据/etc/platform.xml](http://androidxref.com/9.0.0_r3/xref/frameworks/base/data/etc/platform.xml)

```
<permission name="android.permission.INTERNET" >
    <group gid="inet" />
</permission>

<permission name="android.permission.READ_LOGS" >
    <group gid="log" />
</permission>

<permission name="android.permission.WRITE_MEDIA_STORAGE" >
    <group gid="media_rw" />
    <group gid="sdcard_rw" />
</permission>
```

#### Zygote[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#zygote)

该进程在[Android 初始化](https://github.com/dogriffiths/HeadFirstAndroid/wiki/How-Android-Apps-are-Built-and-Run)`Zygote`期间启动。Zygote 是用于启动应用程序的系统服务。Zygote 进程是一个“基础”进程，包含应用程序所需的所有核心库。启动后，Zygote 打开套接字并侦听来自本地客户端的连接。当它接收到连接时，它会派生一个新进程，然后加载并执行特定于应用程序的代码。`/dev/socket/zygote`

#### 应用生命周期(App Lifecycle¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#app-lifecycle)

在 Android 中，应用程序进程的生命周期由操作系统控制。当一个应用程序组件启动并且同一应用程序还没有任何其他组件在Runtime(运行时)，将创建一个新的 Linux 进程。当不再需要后者或需要回收内存以运行更重要的应用程序时，Android 可能会终止此进程。终止进程的决定主要与用户与进程交互的状态有关。通常，进程可以处于四种状态之一。

- 前台进程（例如，在屏幕顶部运行的活动或正在运行的 BroadcastReceiver）
- 可见进程是用户知道的进程，因此杀死它会对用户体验产生明显的负面影响。一个示例是运行一项用户在屏幕上可见但在前台不可见的活动。
- 服务进程是托管已使用该`startService`方法启动的服务的进程。这些进程虽然用户不直接可见，但一般都是用户关心的事情（比如后台网络数据上传或下载），所以系统会一直保持这些进程运行，除非内存不足以保留所有前台和可见的过程。
- 缓存的进程是当前不需要的进程，因此系统可以在需要内存时随意终止它。应用程序必须实现对许多事件做出反应的回调方法；例如，`onCreate`首次创建应用程序进程时会调用处理程序。其他回调方法包括`onLowMemory`,`onTrimMemory`和`onConfigurationChanged`。

### 应用程序包(App Bundles)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#app-bundles)

Android 应用程序可以以两种形式发布：Android Package Kit (APK) 文件或[Android App Bundle](https://developer.android.com/guide/app-bundle) (.aab)。Android App Bundle 提供应用程序所需的所有资源，但将 APK 的生成及其签名推迟到 Google Play。App Bundle 是经过签名的二进制文件，其中包含多个模块中的应用程序代码。基本模块包含应用程序的核心。基本模块可以使用各种模块进行扩展，这些模块包含应用程序的新丰富/功能，如[应用程序包的开发人员文档中](https://developer.android.com/guide/app-bundle)进一步解释的那样。如果您有 Android App Bundle，最好使用[bundletool](https://developer.android.com/studio/command-line/bundletool)来自 Google 的命令行工具，用于构建未签名的 APK，以便使用 APK 上的现有工具。您可以通过运行以下命令从 AAB 文件创建 APK：

```
bundletool build-apks --bundle=/MyApp/my_app.aab --output=/MyApp/my_app.apks
```

如果您想创建已签名的 APK 以准备部署到测试设备，请使用：

```
$ bundletool build-apks --bundle=/MyApp/my_app.aab --output=/MyApp/my_app.apks
--ks=/MyApp/keystore.jks
--ks-pass=file:/MyApp/keystore.pwd
--ks-key-alias=MyKeyAlias
--key-pass=file:/MyApp/key.pwd
```

我们建议您测试带有和不带有附加模块的 APK，以便清楚附加模块是否引入和/或修复基本模块的安全问题。

### Android清单(Android Manifest)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-manifest)

每个应用程序都有一个 Android 清单文件，它以二进制 XML 格式嵌入内容。该文件的标准名称是 AndroidManifest.xml。它位于应用程序的 Android Package Kit (APK) 文件的根目录中。

清单文件描述应用程序结构、其组件（活动、服务、Content Provider(内容提供者)和意图接收者）以及请求的权限。它还包含一般的应用元数据，例如应用的图标、版本号和主题。该文件可能会列出其他信息，例如兼容的 API（最小、目标和最大 SDK 版本）以及[它可以安装的存储类型（外部或内部）](https://developer.android.com/guide/topics/data/install-location.html)。

这是清单文件的示例，包括包名称（约定是反向 URL，但可以接受任何字符串）。它还列出了应用程序版本、相关 SDK、所需权限、公开的Content Provider(内容提供者)、与意图过滤器一起使用的广播接收器以及应用程序及其活动的描述：

```
<manifest
    package="com.owasp.myapplication"
    android:versionCode="0.1" >

    <uses-sdk android:minSdkVersion="12"
        android:targetSdkVersion="22"
        android:maxSdkVersion="25" />

    <uses-permission android:name="android.permission.INTERNET" />

    <provider
        android:name="com.owasp.myapplication.MyProvider"
        android:exported="false" />

    <receiver android:name=".MyReceiver" >
        <intent-filter>
            <action android:name="com.owasp.myapplication.myaction" />
        </intent-filter>
    </receiver>

    <application
        android:icon="@drawable/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.Material.Light" >
        <activity
            android:name="com.owasp.myapplication.MainActivity" >
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

可用清单选项的完整列表在官方[Android 清单文件文档](https://developer.android.com/guide/topics/manifest/manifest-intro.html)中。

### 应用组件(App Components¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#app-components)

Android 应用程序由多个高级组件组成。主要组成部分是：

- Activities
- Fragments
- Intents
- Broadcast receivers
- Content providers and services

所有这些元素均由 Android 操作系统以可通过 API 提供的预定义类的形式提供。

#### 活动(Activities)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#activities)

活动构成了任何应用程序的可见部分。每个屏幕有一个 Activity，因此具有三个不同屏幕的应用会实现三个不同的 Activity。活动通过扩展 Activity 类来声明。它们包含所有用户界面元素：片段、视图和布局。

每个活动都需要使用以下语法在 Android Manifest 中声明：

```
<activity android:name="ActivityName">
</activity>
```

无法显示未在清单中声明的活动，尝试启动它们将引发异常。

像应用程序一样，活动有自己的生命周期，需要监控系统变化来处理它们。活动可以处于以下状态：活动、暂停、停止和非活动。这些状态由 Android 操作系统管理。因此，活动可以实现以下事件管理器：

- 创建时
- onSaveInstanceState
- 启动时
- 恢复时
- onRestoreInstanceState
- 暂停
- 停止
- 重新启动
- 销毁时

- onCreate
- onSaveInstanceState
- onStart
- onResume
- onRestoreInstanceState
- onPause
- onStop
- onRestart
- onDestroy

应用程序可能不会显式实现所有事件管理器，在这种情况下会采取默认操作。通常，至少`onCreate`管理器会被应用程序开发人员覆盖。大多数用户界面组件都是这样声明和初始化的。`onDestroy`当必须显式释放资源（如网络连接或数据库连接）或应用程序关闭时必须执行特定操作时，可能会被覆盖。

#### 碎片(Fragments¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#fragments)

片段表示活动中的行为或用户界面的一部分。Fragments 是在 Android 版本 Honeycomb 3.0（API 级别 11）中引入的。

片段旨在封装界面的各个部分，以促进可重用性和适应不同的屏幕尺寸。片段是自治实体，因为它们包含所有必需的组件（它们有自己的布局、按钮等）。但是，它们必须与活动集成在一起才能发挥作用：片段不能单独存在。它们有自己的生命周期，与实现它们的活动的生命周期相关联。

因为片段有自己的生命周期，所以片段类包含可以重新定义和扩展的事件管理器。这些事件管理器包括 onAttach、onCreate、onStart、onDestroy 和 onDetach。其他几个存在；读者应参考[Android Fragment 规范](https://developer.android.com/guide/components/fragments)了解更多详细信息。

Fragments可以通过扩展Android提供的Fragment类来轻松实现：

Java 中的示例：

```
public class MyFragment extends Fragment {
    ...
}
```

Kotlin 中的示例：

```
class MyFragment : Fragment() {
    ...
}
```

片段不需要在清单文件中声明，因为它们依赖于活动。

要管理其片段，活动可以使用片段管理器（FragmentManager 类）。此类使查找、添加、删除和替换关联片段变得容易。

可以通过以下方式创建片段管理器：

Java 中的示例：

```
FragmentManager fm = getFragmentManager();
```

Kotlin 中的示例：

```
var fm = fragmentManager
```

片段不一定有用户界面；它们可以是管理与应用程序用户界面相关的后台操作的一种方便有效的方式。一个片段可以被声明为持久的，这样即使它的 Activity 被销毁，系统也会保留它的状态。

#### Content Provider(内容提供者)(Content Providers¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#content-providers)

Android 使用 SQLite 永久存储数据：与 Linux 一样，数据存储在文件中。SQLite 是一种轻量、高效、开源的关系数据存储技术，不需要太多的处理能力，这使得它非常适合移动使用。具有特定类（Cursor、ContentValues、SQLiteOpenHelper、ContentProvider、ContentResolver 等）的完整 API 可用。SQLite 不作为单独的进程运行；它是应用程序的一部分。默认情况下，属于给定应用程序的数据库只能由该应用程序访问。然而，Content Provider(内容提供者)提供了一个很好的抽象数据源的机制（包括数据库和平面文件）；它们还提供了一种标准且高效的机制来在应用程序（包括Native应用程序）之间共享数据。为了让其他应用程序可以访问，Content Provider(内容提供者)需要在将共享它的应用程序的清单文件中明确声明。只要未声明Content Provider(内容提供者)，它们就不会被导出，只能由创建它们的应用程序调用。

Content Provider(内容提供者)是通过 URI 寻址方案实现的：它们都使用 content:// 模型。无论源的类型如何（SQLite 数据库、平面文件等），寻址方案总是相同的，从而将源抽象化并为开发人员提供独特的方案。Content Provider(内容提供者)提供所有常规数据库操作：创建、读取、更新、删除。这意味着任何在其清单文件中拥有适当权限的应用程序都可以操纵来自其他应用程序的数据。

#### 服务(Services)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#services)

服务是在后台执行任务（数据处理、启动意图和通知等）而不显示用户界面的 Android 操作系统组件（基于 Service 类）。服务旨在长期运行流程。它们的系统优先级低于活动应用程序的系统优先级，高于非活动应用程序的系统优先级。因此，它们不太可能在系统需要资源时被杀死，并且可以将它们配置为在有足够的资源可用时自动重启。这使得服务成为运行后台任务的理想选择。请注意，服务，如活动，在主应用程序线程中执行。服务不会创建自己的线程，也不会在单独的进程中运行，除非您另有指定。

### 进程间通信(Inter-Process Communication)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#inter-process-communication)

正如我们已经了解到的，每个 Android 进程都有自己的沙盒地址空间。进程间通信设施允许应用程序安全地交换信号和数据。Android 的 IPC 不是依赖于默认的 Linux IPC 工具，而是基于 Binder，这是 OpenBinder 的自定义实现。大多数 Android 系统服务和所有高级 IPC 服务都依赖于 Binder。

术语*Binder*代表许多不同的事物，包括：

- Binder Driver：内核级驱动
- Binder 协议：用于与 Binder 驱动程序通信的低级基于 ioctl 的协议
- IBinder 接口：Binder 对象实现的定义明确的行为
- Binder对象：IBinder接口的通用实现
- Binder服务：Binder对象的实现；例如，位置服务和传感器服务
- Binder客户端：使用Binder服务的对象

Binder 框架包括一个客户端-服务器通信模型。要使用 IPC，应用程序会调用代理对象中的 IPC 方法。代理对象透明地将调用参数*编组*到一个*包裹*中，并将事务发送到作为字符驱动程序 (/dev/binder) 实现的 Binder 服务器。服务器拥有一个线程池，用于处理传入的请求并将消息传递到目标对象。从客户端应用程序的角度来看，所有这些似乎都是常规方法调用，所有繁重的工作都由 Binder 框架完成。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/binder.jpg)

- *Binder 概述 - 图片来源：[Thorsten Schreiber 的 Android Binder](https://1library.net/document/z33dd47z-android-android-interprocess-communication-thorsten-schreiber-somorovsky-bussmeyer.html)*

允许其他应用程序绑定到它们的服务称为*绑定服务*。这些服务必须向客户端提供 IBinder 接口。开发人员使用 Android 接口描述语言 (AIDL) 为远程服务编写接口。

ServiceManager 是一个系统守护进程，负责管理系统服务的注册和查找。它为所有已注册的服务维护一个名称/绑定器对列表。`addService`使用以下静态`getService`方法按名称添加和检索服务`android.os.ServiceManager`：

Java 中的示例：

```
public static IBinder getService(String name) {
        try {
            IBinder service = sCache.get(name);
            if (service != null) {
                return service;
            } else {
                return getIServiceManager().getService(name);
            }
        } catch (RemoteException e) {
            Log.e(TAG, "error in getService", e);
        }
        return null;
    }
```

Kotlin 中的示例：

```
companion object {
        private val sCache: Map<String, IBinder> = ArrayMap()
        fun getService(name: String): IBinder? {
            try {
                val service = sCache[name]
                return service ?: getIServiceManager().getService(name)
            } catch (e: RemoteException) {
                Log.e(FragmentActivity.TAG, "error in getService", e)
            }
            return null
        }
    }
```

您可以使用`service list`命令查询系统服务列表。

```
$ adb shell service list
Found 99 services:
0 carrier_config: [com.android.internal.telephony.ICarrierConfigLoader]
1 phone: [com.android.internal.telephony.ITelephony]
2 isms: [com.android.internal.telephony.ISms]
3 iphonesubinfo: [com.android.internal.telephony.IPhoneSubInfo]
```

#### 意图(Intents)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#intents)

*Intent 消息传递*是构建在 Binder 之上的异步通信框架。该框架允许点对点和发布-订阅消息传递。*Intent*是一个消息传递对象，可用于从另一个应用程序组件请求操作。尽管意图以多种方式促进组件间通信，但有三个基本用例：

- 开始一项活动
- 一个活动代表应用程序中的单个屏幕。您可以通过将意图传递给 来启动活动的新实例`startActivity`。意图描述活动并携带必要的数据。
- 启动服务
- 服务是在后台执行操作的组件，没有用户界面。在 Android 5.0（API 级别 21）及更高版本中，您可以使用 JobScheduler 启动服务。
- 进行广播
- 广播是任何应用程序都可以接收的消息。系统为系统事件发送广播，包括系统启动和充电初始化。您可以通过将意图传递给`sendBroadcast`或来向其他应用程序发送广播`sendOrderedBroadcast`。

有两种类型的意图。显式意图命名将要启动的组件（完全限定的类名）。例如：

Java 中的示例：

```
Intent intent = new Intent(this, myActivity.myClass);
```

Kotlin 中的示例：

```
var intent = Intent(this, myActivity.myClass)
```

隐式意图被发送到操作系统以对给定的数据集执行给定的操作（我们下面示例中的 OWASP 网站的 URL）。由系统决定哪个应用程序或类将执行相应的服务。例如：

Java 中的示例：

```
Intent intent = new Intent(Intent.MY_ACTION, Uri.parse("https://www.owasp.org"));
```

Kotlin 中的示例：

```
var intent = Intent(Intent.MY_ACTION, Uri.parse("https://www.owasp.org"))
```

*Intent 过滤器*是 Android Manifest 文件中的一个表达式，它指定组件想要接收的 Intent 类型。例如，通过为 Activity 声明一个 Intent 过滤器，您可以让其他应用程序以某种 Intent 直接启动您的 Activity。同样，如果您没有为它声明任何意图过滤器，则您的活动只能以明确的意图开始。

Android 使用 Intent 向应用程序广播消息（例如来电或短信）、重要的电源信息（例如电池电量不足）和网络变化（例如连接丢失）。可以将额外数据添加到意图（通过`putExtra`/ `getExtras`）。

这是操作系统发送的意图的简短列表。所有常量都在 Intent 类中定义，整个列表在官方 Android 文档中：

- ACTION_CAMERA_BUTTON 按钮
- ACTION_MEDIA_EJECT
- ACTION_NEW_OUTGOING_CALL
- ACTION_TIMEZONE_CHANGED

为了提高安全性和隐私性，本地广播管理器用于在应用程序内发送和接收意图，而无需将它们发送到操作系统的其余部分。这对于确保敏感和私有数据不会离开应用边界（例如地理位置数据）非常有用。

#### 广播接收器(Broadcast Receivers)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#broadcast-receivers)

广播接收器是允许应用程序从其他应用程序和系统本身接收通知的组件。有了它们，应用程序可以对事件（内部的、由其他应用程序发起的或由操作系统发起的）做出反应。它们通常用于更新用户界面、启动服务、更新内容和创建用户通知。

有两种方法可以让系统知道广播接收器。一种方法是在 Android Manifest 文件中声明它。清单应指定广播接收器和意图过滤器之间的关联，以指示接收器要侦听的操作。

清单中带有意图过滤器的广播接收器声明示例：

```
<receiver android:name=".MyReceiver" >
    <intent-filter>
        <action android:name="com.owasp.myapplication.MY_ACTION" />
    </intent-filter>
</receiver>
```

请注意，在此示例中，广播接收器不包含该[`android:exported`](https://developer.android.com/guide/topics/manifest/receiver-element)属性。由于至少定义了一个过滤器，因此默认值将设置为“true”。在没有任何过滤器的情况下，它将被设置为“false”。

另一种方法是在代码中动态创建接收器。然后接收方可以使用该方法进行注册[`Context.registerReceiver`](https://developer.android.com/reference/android/content/Context.html#registerReceiver(android.content.BroadcastReceiver,%20android.content.IntentFilter))。

动态注册广播接收器的示例：

Java 中的示例：

```
// Define a broadcast receiver
BroadcastReceiver myReceiver = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "Intent received by myReceiver");
    }
};
// Define an intent filter with actions that the broadcast receiver listens for
IntentFilter intentFilter = new IntentFilter();
intentFilter.addAction("com.owasp.myapplication.MY_ACTION");
// To register the broadcast receiver
registerReceiver(myReceiver, intentFilter);
// To un-register the broadcast receiver
unregisterReceiver(myReceiver);
```

Kotlin 中的示例：

```
// Define a broadcast receiver
val myReceiver: BroadcastReceiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Log.d(FragmentActivity.TAG, "Intent received by myReceiver")
    }
}
// Define an intent filter with actions that the broadcast receiver listens for
val intentFilter = IntentFilter()
intentFilter.addAction("com.owasp.myapplication.MY_ACTION")
// To register the broadcast receiver
registerReceiver(myReceiver, intentFilter)
// To un-register the broadcast receiver
unregisterReceiver(myReceiver)
```

请注意，当引发相关意图时，系统会自动启动带有已注册接收器的应用程序。

根据[Broadcasts Overview](https://developer.android.com/guide/components/broadcasts)，如果广播不专门针对应用程序，则广播被视为“隐式”。收到隐式广播后，Android 将列出所有已在其过滤器中注册给定操作的应用程序。如果有多个应用程序注册了同一操作，Android 将提示用户从可用应用程序列表中进行选择。

Broadcast Receiver 的一个有趣特性是它们可以被优先化；这样，一个意图将根据他们的优先级传递给所有授权的接收者。`android:priority`可以通过属性以及通过方法以编程方式将优先级分配给清单中的意图过滤器[`IntentFilter.setPriority`](https://developer.android.com/reference/android/content/IntentFilter#setPriority(int))。但是，请注意具有相同优先级的接收器将以[任意顺序运行](https://developer.android.com/guide/components/broadcasts.html#sending-broadcasts)。

如果您的应用不应跨应用发送广播，请使用本地广播管理器 ( [`LocalBroadcastManager`](https://developer.android.com/reference/androidx/localbroadcastmanager/content/LocalBroadcastManager.html))。它们可用于确保仅从内部应用程序接收意图，并且将丢弃来自任何其他应用程序的任何意图。这对于提高应用程序的安全性和效率非常有用，因为不涉及进程间通信。但是，请注意`LocalBroadcastManager`该类已被[弃用](https://developer.android.com/reference/androidx/localbroadcastmanager/content/LocalBroadcastManager.html)，Google 建议使用替代方法，例如[`LiveData`](https://developer.android.com/reference/androidx/lifecycle/LiveData.html).

有关广播接收器的更多安全注意事项，请参阅[安全注意事项和最佳实践](https://developer.android.com/guide/components/broadcasts.html#security-and-best-practices)。

#### 隐式广播接收器限制[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#implicit-broadcast-receiver-limitation)

根据[Background Optimizations](https://developer.android.com/topic/performance/background-optimization)，针对 Android 7.0（API 级别 24）或更高版本的应用程序不再接收`CONNECTIVITY_ACTION`广播，除非他们向`Context.registerReceiver()`. 系统也不发送`ACTION_NEW_PICTURE`和`ACTION_NEW_VIDEO`广播。

根据[Background Execution Limits ，针对 Android 8.0（API 级别 26）或更高版本的应用程序不能再在其清单中为隐式广播注册广播接收器，隐](https://developer.android.com/about/versions/oreo/background.html#broadcasts)[式广播异常](https://developer.android.com/guide/components/broadcast-exceptions)中列出的除外。在Runtime(运行时)通过调用创建的广播接收器`Context.registerReceiver`不受此限制的影响。

根据[Changes to System Broadcasts](https://developer.android.com/guide/components/broadcasts#changes-system-broadcasts)，从 Android 9（API 级别 28）开始，`NETWORK_STATE_CHANGED_ACTION`广播不会接收有关用户位置或个人身份数据的信息。

## Android应用发布[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-application-publishing)

应用程序开发成功后，下一步就是发布并与他人共享。然而，应用程序不能简单地添加到商店并共享，它们必须先被签名。加密签名用作应用程序开发人员放置的可验证标记。它识别应用程序的作者，并确保应用程序自最初分发以来未被修改。

### 签名流程(Signing Process)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#signing-process)

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
- [通过 IPC 测试敏感功能暴露](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-sensitive-functionality-exposure-through-ipc-mstg-platform-4)
- [测试深层链接](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links-mstg-platform-3)
- 验证用户在输入字段中的所有输入。
- 验证加载到 WebView 中的内容，另请参阅：
- [在 WebView 中测试 JavaScript 执行](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)
- [测试 WebView 协议处理程序](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webview-protocol-handlers-mstg-platform-6)
- [判断 Java 对象是否通过 WebView 暴露](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#determining-whether-java-objects-are-exposed-through-webviews-mstg-platform-7)
- 与后端服务器安全通信或容易受到服务器和移动应用程序之间的中间人攻击，另请参阅：
- [测试网络通信](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#testing-network-communication)
- [Android网络通讯](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/)
- 安全地存储所有本地数据，或从存储中加载不受信任的数据，另请参阅：
- [Android 上的数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)
- 保护自己免受受损环境、重新打包或其他本地攻击，另请参阅：
- [Android 反逆向防御](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/)
