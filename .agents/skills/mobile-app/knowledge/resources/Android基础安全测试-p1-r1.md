# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 1 · part 1

> 分段 1/2。索引见 `Android基础安全测试-p1.md`。

# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 1

> 分段 1/5。索引见 `Android基础安全测试.md`。

# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing)

在上一章中，我们概述了 Android 平台并描述了其应用程序的结构。在本章中，我们将讨论如何设置安全测试环境，并介绍可用于测试 Android 应用程序是否存在安全漏洞的基本流程和技术。这些基本过程是以下章节中概述的测试用例的基础。

## Android测试设置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-testing-setup)

您几乎可以在任何运行 Windows、Linux 或 macOS 的机器上设置功能齐全的测试环境。

### 主机设备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#host-device)

至少，您需要[Android Studio](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#android-studio)（随[Android SDK](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#android-sdk)一起提供）平台工具、模拟器和应用程序来管理各种 SDK 版本和框架组件。Android Studio 还附带了一个用于创建模拟器图像的 Android 虚拟设备 (AVD) 管理器应用程序。确保您的系统上安装了最新的[SDK 工具](https://developer.android.com/studio/releases/sdk-tools)和[平台工具](https://developer.android.com/studio/releases/platform-tools)包。

此外，如果您打算使用包含Native库(NATIVE LIBRARIES)的应用程序，您可能希望通过安装[Android NDK来完成主机设置（这也与“ ](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#android-ndk)[Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章相关）。

有时从计算机显示或控制设备可能很有用。为此，您可以使用[Scrcpy](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#scrcpy)。

### 检测装置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#testing-device)

对于动态分析，您需要一个 Android 设备来运行目标应用程序。原则上，您可以在没有真实 Android 设备的情况下仅使用模拟器进行测试。但是，应用程序在模拟器上的执行速度非常慢，而且模拟器可能无法提供真实的结果。在真实设备上进行测试可以使过程更顺畅，环境更逼真。另一方面，模拟器允许您轻松更改 SDK 版本或创建多个设备。下表列出了每种方法的优缺点的完整概述。

| 资产       | 真机                                                                                   | 仿真器/模拟器                                                |
|:---------|:-------------------------------------------------------------------------------------| :----------------------------------------------------------- |
| 恢复能力     | Softbricks 总是可行的，但新固件通常仍然可以被刷新。硬砖非常罕见。                                               | 模拟器可能会崩溃或损坏，但可以创建新模拟器或恢复快照。       |
| 重置       | 可以恢复出厂设置或刷新。                                                                         | 可以删除和重新创建模拟器。                                   |
| 快照       | 不可能。                                                                                 | 支持，非常适合恶意软件分析。                                 |
| 速度       | 比模拟器快多了。                                                                             | 通常很慢，但正在改进。                                       |
| 成本       | 可用设备的起价通常为 200 美元。您可能需要不同的设备，例如带有或不带生物识别传感器的设备。                                      | 存在免费和商业解决方案。                                     |
| 易于root   | 高度依赖设备。                                                                              | 通常默认为 root。                                            |
| 易于检测模拟器  | 它不是模拟器，因此模拟器检查不适用。                                                                   | 将存在许多人工制品，从而很容易检测到该应用程序正在模拟器中运行。 |
| 易于root检测 | 更容易隐藏Root，因为许多Root检测算法会检查模拟器属性。使用 Magisk Systemless root 几乎不可能检测到。                         | 模拟器几乎总是会触发Root检测算法，因为它们是为使用可以找到的许多人工制品进行测试而构建的。 |
| 硬件交互     | 通过蓝牙、NFC、4G、Wi-Fi、生物识别、摄像头、GPS、陀螺仪等轻松交互                                              | 通常相当有限，具有模拟硬件输入（例如随机 GPS 坐标）          |
| API 级别支持 | 取决于设备和社区。活跃的社区将不断分发更新版本（例如 LineageOS），而不太受欢迎的设备可能只会收到一些更新。在版本之间切换需要刷新设备，这是一个繁琐的过程。   | 始终支持最新版本，包括测试版。可以轻松下载和启动包含特定 API 级别的模拟器。 |
| Native库(NATIVE LIBRARIES)支持    | Native库(NATIVE LIBRARIES)通常是为 ARM 设备构建的，因此它们可以在物理设备上运行。                                                    | 某些模拟器在 x86 CPU 上运行，因此它们可能无法运行打包的Native库(NATIVE LIBRARIES)。 |
| 恶意软件危险   | 恶意软件样本可以感染设备，但如果您可以清除设备存储空间并刷新一个干净的固件，从而将其恢复为出厂设置，这应该不是问题。请注意，存在试图利用 USB 桥接器的恶意软件样本。 | 恶意软件样本可以感染模拟器，但可以简单地删除并重新创建模拟器。还可以创建快照并比较不同的快照以帮助进行恶意软件分析。请注意，存在试图攻击管理程序的恶意软件概念证明。 |

#### 在真实设备上测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#testing-on-a-real-device)

几乎任何物理设备都可用于测试，但有一些注意事项需要考虑。首先，设备需要可root。这通常是通过漏洞利用或通过解锁的引导加载程序完成的。漏洞利用并不总是可用，引导加载程序可能会被永久锁定，或者只有在运营商合同终止后才能解锁。

最佳候选者是专为开发人员打造的旗舰 Google Pixel 设备。这些设备通常带有可解锁的引导加载程序、开源固件、内核、在线收音机和官方操作系统源代码。开发者社区更喜欢谷歌设备，因为操作系统最接近 android 开源项目。这些设备通常具有最长的支持窗口，包括 2 年的操作系统更新和 1 年的安全更新。

或者，谷歌的[Android One](https://www.android.com/one/)项目包含的设备将获得相同的支持窗口（2 年的操作系统更新，1 年的安全更新）并具有接近库存的体验。虽然它最初是作为一个针对低端设备的项目开始的，但该计划已经发展到包括中端和高端智能手机，其中许多都得到了改装社区的积极支持。

[LineageOS](https://lineageos.org/)项目支持的设备也是非常好的测试设备候选者。他们有一个活跃的社区，易于遵循闪烁和Root说明，并且最新的 Android 版本通常可以作为 Lineage 安装快速获得。在 OEM 停止分发更新后很长一段时间内，LineageOS 还继续支持新的 Android 版本。

使用 Android 物理设备时，您需要在设备上启用开发人员模式和 USB 调试，以便使用[ADB](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)调试界面。自 Android 4.2（API 级别 16）起， “设置”应用中的“**开发者选项**”子菜单默认隐藏。要激活它，请点击**关于手机视图的****版本号**部分七次。请注意，内部版本号字段的位置因设备而略有不同。例如，在 LG 手机上，它位于**About phone** -> **Software information**下。完成此操作后，**开发人员选项**将显示在“设置”菜单的底部。激活开发人员选项后，您可以使用**USB调试**开关。

#### 在模拟器上测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#testing-on-an-emulator)

存在多个仿真器，同样各有优缺点：

免费模拟器：

- [Android 虚拟设备 (AVD)](https://developer.android.com/studio/run/managing-avds.html) - 官方 android 模拟器，随 Android Studio 一起分发。
- [Android X86](https://www.android-x86.org/) - Android 代码库的 x86 端口

商业模拟器：

- [Genymotion](https://www.genymotion.com/download/) - 具有许多功能的成熟模拟器，既可以作为本地解决方案，也可以作为基于云的解决方案。免费版本可用于非商业用途。
- [Corellium](https://corellium.com/) - 通过基于云或内部部署的解决方案提供自定义设备虚拟化。

尽管存在多种免费的 Android 模拟器，但我们建议使用 AVD，因为与其他模拟器相比，它提供了适合测试您的应用程序的增强功能。在本指南的其余部分，我们将使用官方 AVD 来执行测试。

AVD 通过其所谓的[扩展控件](https://developer.android.com/studio/run/advanced-emulator-usage#extended)以及[运动传感器](https://developer.android.com/guide/topics/sensors/sensors_overview#test-with-the-android-emulator)支持某些硬件仿真，例如 GPS 或 SMS 。

您可以使用 Android Studio 中的 AVD 管理器启动 Android 虚拟设备 (AVD)，也可以使用以下命令从命令行启动 AVD 管理器，该命令`android`位于 Android SDK 的工具目录中：

```
./android avd
```

可用于在模拟器环境中测试应用程序的多种工具和 VM 可用：

- [MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF)
- [Nathan](https://github.com/mseclab/nathan)（自 2016 年以来未更新）

还请验证本书末尾的“[测试工具”一章。](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/)

#### 获得Root权限[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#getting-privileged-access)

*建议在真实设备上进行Root*（即修改操作系统，以便您可以以 root 用户身份运行命令）进行测试。这使您可以完全控制操作系统，并允许您绕过应用程序沙盒等限制。这些权限反过来允许您更轻松地使用代码注入和函数Hook等技术。

