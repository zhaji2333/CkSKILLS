# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 2 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p2.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 2

> 分段 2/10。索引见 `Android篡改和逆向工程.md`。

## 承接

> 习惯于[IDA](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#ida-pro-commercial-tool)或[Hopper](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#hopper-commercial-tool)的人只是加载二进制文件，出去泡杯咖啡，然后在分析完成后，他们开始进行手动分析以了解程序在做什么。确实，这些工具在后台执行分析，并且 GUI 未被阻止。但这会占用大量 CPU 时间，而且 r2 的目标是在更多平台上运行，而不仅仅是高端台式计算机。

这就是说，请参阅“[审查反汇编Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)”部分以了解更多关于 radare2 如何帮助我们更快地执行逆向任务的信息。例如，获取特定函数的反汇编是一项可以在一个命令中执行的微不足道的任务。

##### IDA专业版[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#ida-pro)

如果您拥有[IDA Pro](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#ida-pro-commercial-tool)Licenses（许可证），请打开文件，然后在“加载新文件”对话框中，选择“ELF for ARM（共享对象）”作为文件类型（IDA 应该会自动检测到这一点），然后选择“ARM Little-Endian” " 作为处理器类型。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/IDA_open_file.jpg)

> 不幸的是，IDA Pro 的免费版本不支持 ARM 处理器类型。

## 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#static-analysis)

对于白盒源代码测试，您需要一个类似于开发人员设置的设置，包括一个包含 Android SDK 和 IDE 的测试环境。建议访问物理设备或模拟器（用于调试应用程序）。

在**黑盒测试**期间，您将无法访问源代码的原始形式。您通常会有[Android APK 格式](https://en.wikipedia.org/wiki/Android_application_package)的应用程序包，可以将其安装在 Android 设备上或按照“反汇编和反编译”部分中的说明进行逆向工程。

### 基本信息收集[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#basic-information-gathering)

如前几节所述，Android 应用程序可以同时包含 Java/Kotlin 字节码和Native代码。在本节中，我们将学习一些使用静态分析收集基本信息的方法和工具。

#### 检索字符串[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#retrieving-strings)

在执行任何类型的二进制分析时，字符串可以被视为最有价值的起点之一，因为它们提供了上下文。例如，类似“数据加密失败”的错误日志字符串。给我们一个提示，相邻的代码可能负责执行某种加密操作。

##### JAVA 和 KOTLIN 字节码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#java-and-kotlin-bytecode)

我们已经知道，Android 应用程序的所有 Java 和 Kotlin 字节码都被编译成一个 DEX 文件。每个 DEX 文件都包含一个[字符串标识符列表](https://source.android.com/devices/tech/dalvik/dex-format#file-layout)(strings_ids)，其中包含每当引用字符串时二进制文件中使用的所有字符串标识符，包括内部命名（例如，类型描述符）或代码引用的常量对象（例如，硬编码字符串） . [您可以使用 Ghidra（基于 GUI）或Dextra](http://newandroidbook.com/tools/dextra.html)（基于 CLI）等工具简单地转储此列表。

使用 Ghidra，只需加载 DEX 文件并在菜单中选择**Window -> Defined strings即可获取字符串。**

> 将 APK 文件直接加载到 Ghidra 中可能会导致不一致。因此，建议通过解压缩 APK 文件来提取 DEX 文件，然后将其加载到 Ghidra 中。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/ghidra_dex_strings.png)

使用 Dextra，您可以使用以下命令转储所有字符串：

```
dextra -S classes.dex
```

Dextra 的输出可以使用标准的 Linux 命令进行操作，例如，`grep`用于搜索某些关键字。

重要的是要知道，使用上述工具获得的字符串列表可能非常大，因为它还包括应用程序中使用的各种类和包名称。浏览完整列表，特别是对于大型二进制文件，可能会非常麻烦。因此，建议从基于关键字的搜索开始，仅在关键字搜索无济于事时才浏览列表。一些可以作为良好起点的通用关键字是 - password、key 和 secret。当您使用应用程序本身时，可以获得特定于应用程序上下文的其他有用关键字。例如，假设应用程序具有登录表单，您可以记下显示的占位符或输入字段的标题文本，并将其用作静态分析的入口点。

##### Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#native-code)

为了从 Android 应用程序中使用的Native代码中提取字符串，您可以使用 Ghidra 或 Cutter 等 GUI 工具，或者依赖基于 CLI 的工具，例如*字符串*Unix 实用程序 ( `strings <path_to_binary>`) 或 radare2 的 rabin2 ( `rabin2 -zz <path_to_binary>`)。使用基于 CLI 的工具时，您可以利用 grep 等其他工具（例如结合正则表达式）进一步过滤和分析结果。

#### 交叉引用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#cross-references)

##### JAVA 和Kotlin[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#java-and-kotlin)

有许多 RE 工具支持检索 Java 交叉引用。对于许多基于 GUI 的函数，这通常是通过右键单击所需函数并选择相应的选项来完成的，例如在 Ghidra 中**显示对**的引用或在 jadx中[查找](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)[**用法**](https://github.com/skylot/jadx/wiki/jadx-gui-features-overview#find-usage)。

##### Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#native-code_1)

与 Java 分析类似，您也可以使用 Ghidra 分析原生库并通过右键单击所需函数并选择**Show References to 来**获取交叉引用。

#### 接口使用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#api-usage)

Android 平台为应用程序中的常用功能提供了许多内置库，例如加密、蓝牙、NFC、网络或位置库。确定这些库在应用程序中的存在可以为我们提供有关其性质的宝贵信息。

例如，如果应用程序正在导入`javax.crypto.Cipher`，则表明该应用程序将执行某种加密操作。幸运的是，密码调用本质上是非常标准的，即它们需要以特定顺序调用才能正常工作，这一知识在分析密码 API 时会很有帮助。例如，通过查找`Cipher.getInstance`函数，我们可以确定所使用的加密算法。通过这种方法，我们可以直接转向分析加密资产，这在应用程序中通常非常关键。有关如何分析 Android 加密 API 的更多信息，请参阅“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”部分。

同样，上述方法可用于确定应用程序在何处以及如何使用 NFC。例如，使用基于主机的卡仿真来执行数字支付的应用程序必须使用该`android.nfc`包。因此，NFC API 分析的一个很好的陈述点是查阅[Android 开发者文档](https://developer.android.com/guide/topics/connectivity/nfc/hce)以获得一些想法并开始搜索关键函数，例如`processCommandApdu`来自`android.nfc.cardemulation.HostApduService`类的函数。

#### 网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#network-communication)

您可能遇到的大多数应用程序都连接到远程端点。即使在您执行任何动态分析（例如流量捕获和分析）之前，您也可以通过枚举应用程序应该与之通信的域来获得一些初始输入或入口点。

通常，这些域将作为字符串出现在应用程序的二进制文件中。实现这一目标的一种方法是使用自动化工具，例如[APKEnum](https://github.com/shivsahni/APKEnum)或[MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF)。或者，您可以使用正则表达式对域名进行*grep 。*为此，您可以直接以应用程序二进制文件为目标或对其进行反向工程并以反汇编或反编译代码为目标。后一种选择有一个明显的优势：它可以为您提供**context**，因为您将能够看到每个域在哪个上下文中被使用（例如类和方法）。``

从这里开始，您可以使用此信息获得更多见解，这些见解可能会在稍后的分析过程中使用，例如，您可以将域与固定证书或[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)文件进行匹配，或者对域名执行进一步侦察以了解更多信息目标环境。在评估应用程序时，检查网络安全配置文件很重要，因为通常（安全性较低）调试配置可能会被错误地推送到最终版本中。

安全连接的实施和验证可能是一个复杂的过程，需要考虑许多方面。例如，许多应用程序使用除 HTTP 之外的其他协议，例如 XMPP 或纯 TCP 数据包，或执行证书固定以试图阻止 MITM 攻击，但不幸的是在其实现中存在严重的逻辑错误或固有错误的安全网络配置。

请记住，在大多数情况下，仅使用静态分析是不够的，与可以获得更可靠结果的动态替代方案（例如使用拦截器代理）相比，甚至可能变得极其低效。在本节中，我们只是略微触及了表面，请参阅“Android 基本安全测试”一章中的“[基本网络监控/嗅探”部分，并查看“ ](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#basic-network-monitoringsniffing)[Android 网络通信](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/)”一章中的测试用例。

### 手动（反向）代码审查[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#manual-reversed-code-review)

#### 查看反编译的 Java 代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)

