# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 1 · part 2

> 分段 2/2。索引见 `Android平台概览-p1.md`。

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
