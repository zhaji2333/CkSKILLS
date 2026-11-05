# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 1 · part 1

> 分段 1/2。索引见 `Android平台概览-p1.md`。

# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 1

> 分段 1/4。索引见 `Android平台概览.md`。

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
