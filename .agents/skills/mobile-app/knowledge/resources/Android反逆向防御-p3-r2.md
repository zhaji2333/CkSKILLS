# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 3 · part 2

> 分段 2/2。索引见 `Android反逆向防御-p3.md`。

| **检查相关工件的环境**         | 工件可以是包文件、二进制文件、库、进程和临时文件。对于 Frida，这可能是在目标（有根）系统中运行的 frida-server（负责通过 TCP 公开 Frida 的守护进程）。检查正在运行的服务 ( [`getRunningServices`](https://developer.android.com/reference/android/app/ActivityManager.html#getRunningServices(int))) 和进程 ( `ps`)，搜索名称为“frida-server”的服务。您还可以遍历已加载库的列表并检查是否存在可疑库（例如名称中包含“frida”的库）。 | 从 Android 7.0（API 级别 24）开始，检查正在运行的服务/进程不会向您显示像 frida-server 这样的守护进程，因为它不是由应用程序本身启动的。即使有可能，绕过这个也很容易，只需重命名相应的 Frida 工件 (frida-server/frida-gadget/frida-agent)。 |
| **检查打开的 TCP 端口**        | frida-server 进程默认绑定到 TCP 端口 27042。检查此端口是否打开是检测守护进程的另一种方法。 | 此方法在其默认模式下检测 frida-server，但可以通过命令行参数更改监听端口，因此绕过它有点太简单了。 |
| **检查响应 D-Bus Auth 的端口** | `frida-server`使用 D-Bus 协议进行通信，因此您可以期望它响应 D-Bus AUTH。向每个打开的端口发送一条 D-Bus AUTH 消息并检查答案，希望它`frida-server`会自己显示出来。 | 这是一种相当可靠的检测方法`frida-server`，但 Frida 提供了不需要 frida-server 的替代操作模式。 |
| **扫描进程内存以查找已知工件** | 扫描内存以查找在 Frida 库中发现的工件，例如所有版本的 frida-gadget 和 frida-agent 中都存在字符串“LIBFRIDA”。例如，使用`Runtime.getRuntime().exec`并遍历在`/proc/self/maps`或`/proc/<pid>/maps`（取决于 Android 版本）搜索字符串中列出的内存映射。 | 这种方法更有效一些，仅使用 Frida 很难绕过，尤其是在添加了一些混淆并且正在扫描多个工件的情况下。但是，所选工件可能会在 Frida 二进制文件中进行修补。[在Berdhard Mueller 的 GitHub](https://github.com/muellerberndt/frida-detection-demo/blob/master/AntiFrida/app/src/main/cpp/native-lib.cpp)上找到源代码。 |

请记住，这张表远非详尽无遗。我们可以开始讨论[命名管道](https://en.wikipedia.org/wiki/Named_pipe)（由 frida-server 用于外部通信）、检测[蹦床](https://en.wikipedia.org/wiki/Trampoline_(computing))（在函数序言处插入的间接跳转向量），这将有助于检测 Substrate 或 Frida 的拦截器，但例如，不会有效对抗Frida的追猎者；以及许多其他或多或少有效的检测方法。它们中的每一个都将取决于您是否使用有Root设备、Root方法的特定版本和/或工具本身的版本。此外，该应用程序可以尝试通过使用各种混淆技术来使其更难检测已实施的保护机制，如下面“[针对逆向工程的测试弹性”部分所述](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-obfuscation-mstg-resilience-9)”。最后，这是保护在不受信任的环境（在用户设备中运行的应用程序）上处理的数据的猫捉老鼠游戏的一部分。

> 重要的是要注意，这些控制只会增加逆向工程过程的复杂性。如果使用，最好的方法是巧妙地组合控件而不是单独使用它们。然而，它们都不能保证 100% 的有效性，因为逆向工程师总是可以完全访问设备，因此总是会赢！您还必须考虑将某些控件集成到您的应用程序中可能会增加应用程序的复杂性，甚至会影响其性能。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_3)

使用测试设备中安装的各种逆向工程工具和框架启动应用程序。至少包括以下内容：Frida、Xposed、Android 的 Substrate、RootCloak、Android SSL Trust Killer。

该应用程序应以某种方式响应这些工具的存在。例如：

- 提醒用户并要求承担责任。
- 通过优雅终止来防止执行。
- 安全擦除存储在设备上的任何敏感数据。
- 向后端服务器报告，例如，用于欺诈检测。

接下来，绕过逆向工程工具的检测并回答以下问题：

- 是否可以轻松绕过这些机制（例如，通过Hook单个 API 函数）？
- 通过静态和动态分析识别反逆向工程代码有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您如何评估绕过这些机制的难度？

绕过逆向工程工具的检测时，应遵循以下步骤：

1. 修补反逆向工程功能。通过简单地用 NOP 指令覆盖相关的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed 在 Java 和Native层上Hook文件系统 API。返回原始文件的句柄，而不是修改后的文件。
3. 使用内核模块拦截与文件相关的系统调用。当进程尝试打开修改后的文件时，返回文件未修改版本的文件描述符。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

## 测试仿真器检测 (MSTG-RESILIENCE-5)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-emulator-detection-mstg-resilience-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_4)

在反逆向的背景下，模拟器检测的目标是增加应用程序在模拟设备上运行的难度，这阻碍了逆向工程师喜欢使用的一些工具和技术。这种增加的难度迫使逆向工程师击败仿真器检查或利用物理设备，从而禁止进行大规模设备分析所需的访问。

### 模拟器检测示例[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#emulator-detection-examples)

有几个指标表明正在模拟有问题的设备。尽管所有这些 API 调用都可以Hook，但这些指标提供了适度的第一道防线。

第一组指标在文件中`build.prop`。

```
API Method          Value           Meaning
Build.ABI           armeabi         possibly emulator
BUILD.ABI2          unknown         possibly emulator
Build.BOARD         unknown         emulator
Build.Brand         generic         emulator
Build.DEVICE        generic         emulator
Build.FINGERPRINT   generic         emulator
Build.Hardware      goldfish        emulator
Build.Host          android-test    possibly emulator
Build.ID            FRF91           emulator
Build.MANUFACTURER  unknown         emulator
Build.MODEL         sdk             emulator
Build.PRODUCT       sdk             emulator
Build.RADIO         unknown         possibly emulator
Build.SERIAL        null            emulator
Build.USER          android-build   emulator
```

您可以在已获得 root 权限的 Android 设备上编辑该文件`build.prop`，或在从源代码编译 AOSP 时对其进行修改。这两种技术都可以让您绕过上面的静态字符串检查。

下一组静态指示器使用电话管理器。所有 Android 模拟器都有此 API 可以查询的固定值。

```
API                                                     Value                   Meaning
TelephonyManager.getDeviceId()                          0's                     emulator
TelephonyManager.getLine1 Number()                      155552155               emulator
TelephonyManager.getNetworkCountryIso()                 us                      possibly emulator
TelephonyManager.getNetworkType()                       3                       possibly emulator
TelephonyManager.getNetworkOperator().substring(0,3)    310                     possibly emulator
