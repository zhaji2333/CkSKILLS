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

请注意，Root是有风险的，在继续之前需要弄清三个主要后果。Root可能会产生以下负面影响：

- 使设备保修失效（在采取任何行动之前务必检查制造商的政策）
- “变砖”设备，即使其无法操作和无法使用
- 造成额外的安全风险（因为内置的漏洞利用缓解措施经常被删除）

您不应该对存储您的私人信息的个人设备进行 root。我们建议改用便宜的专用测试设备。许多旧设备，例如 Google 的 Nexus 系列，可以运行最新的 Android 版本并且非常适合测试。

**您需要了解，对您的设备进行 root 操作最终是您的决定，OWASP 对任何损坏概不负责。如果您不确定，请在开始Root过程之前寻求专家建议。**

##### 哪些手机可以ROOT[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#which-mobiles-can-be-rooted)

几乎所有Android手机都可以root。Android 操作系统的商业版本（在内核级别是 Linux 操作系统的演变）针对移动世界进行了优化。这些版本的某些功能已被删除或禁用，例如，非特权用户能够成为“root”用户（具有提升的特权）。Root 手机意味着允许用户成为 root 用户，例如，添加一个名为 的标准 Linux 可执行文件`su`，用于更改为另一个用户帐户。

要对移动设备进行 root，首先要解锁其引导加载程序。解锁过程取决于设备制造商。然而，出于实际原因，对某些移动设备进行 root 操作比对其他移动设备进行 root 操作更受欢迎，特别是在安全测试方面：由谷歌创建并由三星、LG 和摩托罗拉等公司制造的设备是最受欢迎的，特别是因为它们是许多开发人员使用。解锁引导加载程序后，设备保修不会失效，并且 Google 提供了许多工具来支持 root 本身。[XDA 论坛上](https://www.xda-developers.com/root/)发布了所有主要品牌设备的 root 指南精选列表。

##### 用 MAGISK 刷机[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#rooting-with-magisk)

Magisk（“Magic Mask”）是一种 root Android 设备的方法。它的专长在于对系统进行修改的方式。虽然其他Root工具会更改系统分区上的实际数据，但 Magisk 不会（称为“无系统”）。这提供了一种方法来隐藏对 root 敏感的应用程序（例如银行或游戏）的修改，并允许使用官方 Android OTA 升级，而无需事先取消对设备的 root 权限。

[您可以阅读GitHub 上的官方文档](https://topjohnwu.github.io/Magisk/)来熟悉 Magisk 。如果您没有安装 Magisk，您可以在[文档](https://topjohnwu.github.io/Magisk/)中找到安装说明。如果你使用的是Android官方版本并打算升级，Magisk[在 GitHub 上提供了教程](https://topjohnwu.github.io/Magisk/ota.html)。

此外，开发人员可以使用 Magisk 的强大功能来创建自定义模块并将它们[提交](https://github.com/Magisk-Modules-Repo/submission)到官方[Magisk 模块存储库](https://github.com/Magisk-Modules-Repo)。然后可以在 Magisk Manager 应用程序中安装提交的模块。这些可安装模块之一是著名的[Xposed Framework](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#xposed)的无系统版本（适用于最高 27 的 SDK 版本）。

##### Root检测[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#root-detection)

“在 Android 上测试反逆向防御”一章中提供了一个广泛的Root检测方法列表。

对于典型的移动应用程序安全构建，您通常需要在禁用Root检测的情况下测试调试构建。如果此类构建不可用于测试，您可以通过本书稍后介绍的多种方式禁用Root检测。

## 基本测试操作[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#basic-testing-operations)

### 访问设备Shell[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#accessing-the-device-shell)

测试应用程序时最常做的事情之一是访问设备Shell。在本节中，我们将了解如何使用/不使用 USB 电缆从您的主机远程访问 Android shell，以及如何从设备本身本地访问 Android shell。

#### 远程Shell[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#remote-shell)

为了从您的主机连接到 Android 设备的Shell，[adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)通常是您选择的工具（除非您更喜欢使用远程 SSH 访问，例如[通过 Termux](https://wiki.termux.com/wiki/Remote_Access#Using_the_SSH_server)）。

对于本节，我们假设您已正确启用开发人员模式和 USB 调试，如“在真实设备上测试”中所述。通过 USB 连接 Android 设备后，您可以通过运行以下命令访问远程设备的 shell：

```
adb shell
```

> 按 Control + D 或键入`exit`退出

进入远程 shell 后，如果您的设备已获得 root 权限或您正在使用模拟器，则可以通过运行以下命令获得 root 访问权限`su`：

```
bullhead:/ $ su
bullhead:/ # id
uid=0(root) gid=0(root) groups=0(root) context=u:r:su:s0
```

> 仅当您使用模拟器时，您才可以使用命令以 root 权限重新启动 adb，`adb root`这样下次您输入`adb shell`时就已经拥有 root 访问权限了。这也允许在您的主机和 Android 文件系统之间双向传输数据，即使可以访问只有 root 用户可以访问的位置（通过`adb push/pull`）。[在下面的“主机设备数据传输](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#host-device-data-transfer)”部分中查看有关数据传输的更多信息。

##### 连接到多个设备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#connect-to-multiple-devices)

如果您有多个设备，请记住在您的所有命令（例如或）中包含`-s`后跟设备序列号的标志。您可以使用以下命令获取所有已连接设备及其序列号的列表：`adb``adb -s emulator-5554 shell``adb -s 00b604081540b7c6 shell`

```
adb devices
List of devices attached
00c907098530a82c    device
emulator-5554    device
```

##### 通过 WI-FI 连接到设备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#connect-to-a-device-over-wi-fi)

您也可以在不使用 USB 数据线的情况下访问您的 Android 设备。为此，您必须将主机和 Android 设备连接到同一个 Wi-Fi 网络，然后执行以下步骤：

- 使用 USB 电缆将设备连接到主机，并将目标设备设置为在端口 5555 上侦听 TCP/IP 连接：`adb tcpip 5555`。
- 从目标设备断开 USB 电缆并运行`adb connect <device_ip_address>`。通过运行检查设备现在是否可用`adb devices`。
- 用 . 打开Shell`adb shell`。

但是，请注意，这样做会使您的设备对同一网络中的任何人开放，并且知道您设备的 IP 地址。您可能更喜欢使用 USB 连接。

> 例如，在 Nexus 设备上，您可以在**“设置”** -> “**系统**” -> “**关于手机**” -> **“状态”** -> “ **IP**地址”中找到 IP 地址，或者转到**Wi-Fi**菜单并在您连接的网络上点击一次.

[请参阅Android 开发人员文档](https://developer.android.com/studio/command-line/adb#wireless)中的完整说明和注意事项。

##### 通过 SSH 连接到设备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#connect-to-a-device-via-ssh)

如果愿意，您还可以启用 SSH 访问。一个方便的选择是使用[Termux](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#termux)，您可以轻松地将其[配置为提供 SSH 访问](https://wiki.termux.com/wiki/Remote_Access#Using_the_SSH_server)（使用密码或公钥身份验证）并使用命令启动它`sshd`（默认在端口 8022 上启动）。为了通过 SSH 连接到 Termux，您可以简单地运行命令`ssh -p 8022 <ip_address>`（`ip_address`实际的远程设备 IP 在哪里）。这个选项有一些额外的好处，因为它允许通过 SFTP 也可以在端口 8022 上访问文件系统。

#### 设备上的Shell应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#on-device-shell-app)

虽然与远程 shell 相比，通常使用设备上的 shell（终端仿真器）（如[Termux](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#termux) ）可能非常乏味，但事实证明，在出现网络问题或检查某些配置等情况下，它可以方便地进行调试。

### 主机设备数据传输[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#host-device-data-transfer)

#### 使用ADB[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#using-adb)

您可以使用[adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)命令`adb pull <remote> <local>`和`adb push <local> <remote>` [命令](https://developer.android.com/studio/command-line/adb#copyfiles)将文件复制到设备或从设备复制文件。它们的用法非常简单。例如，以下`foo.txt`将从您当前目录（本地）复制到`sdcard`文件夹（远程）：

```
adb push foo.txt /sdcard/foo.txt
```

当您确切地知道要复制什么以及从/复制到哪里并且还支持批量文件传输时，通常使用这种方法，例如，您可以将整个目录从 Android 设备拉（复制）到您的主机。

```
$ adb pull /sdcard
/sdcard/: 1190 files pulled. 14.1 MB/s (304526427 bytes in 20.566s)
```

#### 使用 Android Studio 设备文件资源管理器[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#using-android-studio-device-file-explorer)

Android Studio 有一个[内置的 Device File Explorer](https://developer.android.com/studio/debug/device-file-explorer)，您可以通过转到**View** -> **Tool Windows** -> **Device File Explorer**打开它。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/android-studio-file-device-explorer.png)

如果您使用的是有Root设备，您现在可以开始探索整个文件系统。但是，当使用非 root 设备访问应用程序沙箱时，除非该应用程序是可调试的，否则您将被“囚禁”在应用程序沙箱中。

#### 使用objection[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#using-objection)

当您在特定应用程序上工作并想要复制您可能在其沙箱中遇到的文件时，此选项很有用（请注意，您将只能访问目标应用程序有权访问的文件）。这种方法无需将应用程序设置为可调试即可工作，否则在使用 Android Studio 的设备文件资源管理器时需要将其设置为可调试。

[首先，按照“推荐工具 - 反对](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)”中的说明，使用 Objection 连接到应用程序。然后，像往常一样在终端上使用`ls`和来浏览可用文件：`cd`

```
$ frida-ps -U | grep -i owasp
21228  sg.vp.owasp_mobile.omtg_android

$ objection -g sg.vp.owasp_mobile.omtg_android explore

...g.vp.owasp_mobile.omtg_android on (google: 8.1.0) [usb] # cd ..
/data/user/0/sg.vp.owasp_mobile.omtg_android

...g.vp.owasp_mobile.omtg_android on (google: 8.1.0)  [usb] # ls
Type       ...  Name
---------  ...  -------------------
Directory  ...  cache
Directory  ...  code_cache
Directory  ...  lib
Directory  ...  shared_prefs
Directory  ...  files
Directory  ...  app_ACRA-approved
Directory  ...  app_ACRA-unapproved
Directory  ...  databases

Readable: True  Writable: True
```

一个你有一个你想要下载的文件，你可以直接运行`file download <some_file>`。这会将文件下载到您的工作目录。与您可以使用上传文件的方式相同`file upload`。

```
...[usb] # ls
Type    ...  Name
------  ...  -----------------------------------------------
File    ...  sg.vp.owasp_mobile.omtg_android_preferences.xml

Readable: True  Writable: True
...[usb] # file download sg.vp.owasp_mobile.omtg_android_preferences.xml
Downloading ...
Streaming file from device...
Writing bytes to destination...
Successfully downloaded ... to sg.vp.owasp_mobile.omtg_android_preferences.xml
```

缺点是，在撰写本文时，objection 尚不支持批量文件传输，因此您只能复制单个文件。不过，在某些情况下，如果您已经使用 objection 探索应用程序并找到一些有趣的文件，这仍然会派上用场。例如`adb pull <path_to_some_file>`，您可能不想记下该文件的完整路径并从单独的终端使用，而是直接执行`file download <some_file>`.

#### 使用 Termux[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#using-termux)

如果你有一个 root 设备，安装了[Termux](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#termux)并[正确配置了 SSH 访问](https://wiki.termux.com/wiki/Remote_Access#Using_the_SSH_server)，你应该有一个 SFTP（SSH 文件传输协议）服务器已经在端口 8022 上运行。你可以从你的终端访问它：

```
$ sftp -P 8022 root@localhost
...
sftp> cd /data/data
sftp> ls -1
...
sg.vantagepoint.helloworldjni
sg.vantagepoint.uncrackable1
sg.vp.owasp_mobile.omtg_android
```

或者简单地使用像[FileZilla](https://filezilla-project.org/download.php)这样的支持 SFTP 的客户端：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/sftp-with-filezilla.png)

查看[Termux Wiki](https://wiki.termux.com/wiki/Remote_Access)以了解有关远程文件访问方法的更多信息。

### 获取和提取应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#obtaining-and-extracting-apps)

有多种方法可以从设备中提取 APK 文件。您需要Root据应用程序是公开的还是私有的来决定哪一种是最简单的方法。

#### 替代应用商店[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#alternative-app-stores)

最简单的选择之一是从镜像 Google Play 商店公共应用程序的网站下载 APK。但是，请记住，这些网站不是官方网站，无法保证应用程序未被重新打包或未包含恶意软件。一些托管 APK 且不以修改应用程序甚至列出应用程序的 SHA-1 和 SHA-256 校验和而闻名的知名网站是：

- [APKMirror](https://apkmirror.com/)
- [APKPure](https://apkpure.com/)

请注意，您无法控制这些站点，并且您无法保证它们将来会做什么。仅当这是您唯一的选择时才使用它们。

#### 使用 gplaycli[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#using-gplaycli)

您可以使用[gplaycli](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#gplaycli)`-d`通过指定其 AppID来下载 ( ) 选定的 APK（添加`-p`以显示进度条和`-v`冗长）：

```
$ gplaycli -p -v -d com.google.android.keep
[INFO] GPlayCli version 3.26 [Python3.7.4]
[INFO] Configuration file is ~/.config/gplaycli/gplaycli.conf
[INFO] Device is bacon
[INFO] Using cached token.
[INFO] Using auto retrieved token to connect to API
[INFO] 1 / 1 com.google.android.keep
[################################] 15.78MB/15.78MB - 00:00:02 6.57MB/s/s
[INFO] Download complete
```

该`com.google.android.keep.apk`文件将位于您的当前目录中。正如您想象的那样，这种方法是一种非常方便的下载 APK 的方式，尤其是在自动化方面。

> 您可以使用自己的 Google Play 凭据或令牌。默认情况下，gplaycli 将使用[内部提供的令牌](https://github.com/matlink/gplaycli/blob/3.26/gplaycli/gplaycli.py#L106)。

#### 从设备中提取应用程序包[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#extracting-the-app-package-from-the-device)

从设备上获取应用包是推荐的方法，因为我们可以保证应用没有被第三方修改过。要从root或非root设备获取应用程序，您可以使用以下方法：

用于`adb pull`检索 APK。如果您不知道包名称，第一步是列出设备上安装的所有应用程序：

```
adb shell pm list packages
```

找到应用程序的包名称后，您需要它在系统上存储的完整路径才能下载它。

```
adb shell pm path <package name>
```

有了 APK 的完整路径，您现在可以简单地使用`adb pull`来提取它。

```
adb pull <apk path>
```

APK 将下载到您的工作目录中。

或者，还有像[APK Extractor](https://play.google.com/store/apps/details?id=com.ext.ui)这样不需要 root 的应用程序，甚至可以通过您喜欢的方法共享提取的 APK。如果您不想通过网络连接设备或设置 adb 来传输文件，这会很有用。

#### 测试即时应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#testing-instant-apps)

借助[Google Play Instant](https://developer.android.com/topic/google-play-instant/overview)，您可以创建即时应用程序，这些应用程序可以从浏览器或 Android 5.0（API 级别 21）及更高版本的应用程序商店中的“立即试用”按钮立即启动。它们不需要任何形式的安装。即时应用程序存在一些挑战：

- 免安装应用程序的大小有限。
- 只能使用较少数量的权限，这些权限记录在[Android Instant app 文档](https://developer.android.com/topic/google-play-instant/getting-started/instant-enabled-app-bundle?tenant=irina#request-supported-permissions)中。

这些因素的结合可能会导致不安全的决策，例如：从应用程序中剥离过多的授权/身份验证/机密性逻辑，从而导致信息泄露。

注意：即时应用程序需要一个 App Bundle。App Bundle 在“Android 平台概述”一章的“ [App Bundle](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#app-bundles) ”部分进行了描述。

**静态分析注意事项：**

静态分析可以在对下载的即时应用程序进行逆向工程后完成，也可以通过分析 App Bundle 来完成。当您分析 App Bundle 时，检查 Android Manifest 以查看是否`dist:module dist:instant="true"`为给定模块设置了（基础模块或特定模块`dist:module`）。接下来，检查各种入口点，设置了哪些入口点（通过`<data android:path="</PATH/HERE>" />`）。

现在跟随入口点，就像您对任何 Activity 所做的那样并检查：

- 应用程序检索到的任何数据是否需要对该数据进行隐私保护？如果是这样，是否所有必需的控制措施都到位了？
- 所有通信都安全吗？
- 当您需要更多功能时，是否也下载了正确的安全控制？

**动态分析注意事项：**

有多种方法可以开始对您的免安装应用程序进行动态分析。在所有情况下，您首先必须安装对即时应用程序的支持并将`ia`可执行文件添加到您的`$PATH`.

通过以下命令安装即时应用程序支持：

```
cd path/to/android/sdk/tools/bin && ./sdkmanager 'extras;google;instantapps'
```

接下来，您必须添加`path/to/android/sdk/extras/google/instantapps/ia`到您的`$PATH`.

准备工作完成后，您可以在运行 Android 8.1（API 级别 27）或更高版本的设备上本地测试免安装应用程序。该应用程序可以通过不同的方式进行测试：

- 在本地测试应用程序：通过 Android Studio 部署应用程序（并启用`Deploy as instant app`运行/配置对话框中的复选框）或使用以下命令部署应用程序：

```
ia run output-from-build-command <app-artifact>
```

- 使用 Play 控制台测试应用：
- 将您的 App Bundle 上传到 Google Play 管理中心
- 准备上传的包以发布到内部测试轨道。
- 在设备上登录内部测试员帐户，然后从外部准备好的链接或通过`try now`测试员帐户中 App 商店中的按钮启动您的即时体验。

现在您可以测试该应用程序，检查是否：

- 是否有任何数据需要隐私控制以及这些控制是否到位。
- 所有通信都足够安全。
- 当您需要更多功能时，是否也为这些功能下载了正确的安全控制？

### 重新打包应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#repackaging-apps)

如果您需要在未越狱的设备上进行测试，您应该学习如何重新打包应用程序以在其上启用动态测试。

使用计算机执行反对 Wiki中的文章[“修补 Android 应用程序”中指示的所有步骤。](https://github.com/sensepost/objection/wiki/Patching-Android-Applications)完成后，您将能够通过调用反对命令来修补 APK：

```
objection patchapk --source app-release.apk
```

然后需要使用 adb 安装已打补丁的应用程序，如[“安装应用程序”](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#installing-apps)中所述。

> 这种重新打包方法足以满足大多数用例。对于更高级的重新打包，请参阅[“Android 篡改和逆向工程 - 修补、重新打包和重新签名”](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-repackaging-and-re-signing)。

### 安装应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#installing-apps)

用于`adb install`在模拟器或连接的设备上安装 APK。

```
adb install path_to_apk
```

请注意，如果您拥有原始源代码并使用 Android Studio，则无需执行此操作，因为 Android Studio 会为您处理应用程序的打包和安装。

### 信息收集[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#information-gathering)

分析应用程序的一个基本步骤是信息收集。这可以通过检查主机上的应用程序包或通过访问设备上的应用程序数据来远程完成。您将在后续章节中找到更多高级技术，但目前我们将重点关注基础知识：获取所有已安装应用程序的列表、浏览应用程序包以及访问设备本身的应用程序数据目录。这应该让您对应用程序的全部内容有一些了解，甚至不必对其进行逆向工程或执行更高级的分析。我们将回答以下问题：

- 包中包含哪些文件？
- 该应用程序使用哪些Native库(NATIVE LIBRARIES)？
- 应用程序定义了哪些应用程序组件？任何服务或Content Provider(内容提供者)？
- 应用程序是否可调试？
- 该应用程序是否包含网络安全策略？
- 该应用程序在安装时是否会创建任何新文件？

#### 列出已安装的应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#listing-installed-apps)

当定位安装在设备上的应用程序时，您首先必须找出要分析的应用程序的正确包名称。您可以使用`pm`(Android Package Manager) 或使用以下方法检索已安装的应用程序`frida-ps`：

```
$ adb shell pm list packages
package:sg.vantagepoint.helloworldjni
package:eu.chainfire.supersu
package:org.teamsik.apps.hackingchallenge.easy
package:org.teamsik.apps.hackingchallenge.hard
package:sg.vp.owasp_mobile.omtg_android
```

您可以包含标志以仅显示第三方应用程序 ( `-3`) 及其 APK 文件的位置 ( `-f`)，之后您可以使用它们通过以下方式下载它`adb pull`：

```
$ adb shell pm list packages -3 -f
package:/data/app/sg.vantagepoint.helloworldjni-1/base.apk=sg.vantagepoint.helloworldjni
package:/data/app/eu.chainfire.supersu-1/base.apk=eu.chainfire.supersu
package:/data/app/org.teamsik.apps.hackingchallenge.easy-1/base.apk=org.teamsik.apps.hackingchallenge.easy
package:/data/app/org.teamsik.apps.hackingchallenge.hard-1/base.apk=org.teamsik.apps.hackingchallenge.hard
package:/data/app/sg.vp.owasp_mobile.omtg_android-kR0ovWl9eoU_yh0jPJ9caQ==/base.apk=sg.vp.owasp_mobile.omtg_android
```

`adb shell pm path <app_package_id>`这与在应用程序包 ID 上运行相同：

```
$ adb shell pm path sg.vp.owasp_mobile.omtg_android
package:/data/app/sg.vp.owasp_mobile.omtg_android-kR0ovWl9eoU_yh0jPJ9caQ==/base.apk
```

用于`frida-ps -Uai`获取连接的 USB 设备 ( ) 上`-a`当前安装 ( ) 的所有应用程序 ( )：`-i``-U`

```
$ frida-ps -Uai
  PID  Name                                      Identifier
-----  ----------------------------------------  ---------------------------------------
  766  Android System                            android
21228  Attack me if u can                        sg.vp.owasp_mobile.omtg_android
 4281  Termux                                    com.termux
    -  Uncrackable1                              sg.vantagepoint.uncrackable1
```

请注意，这还会显示当前正在运行的应用程序的 PID。记下“标识符”和 PID（如果有的话），因为之后您将需要它们。

#### 探索应用程序包[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)

一旦您收集了您想要作为目标的应用程序的包名称，您将要开始收集有关它的信息。[首先，按照“基本测试操作 - 获取和提取应用程序”](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#obtaining-and-extracting-apps)中的说明检索 APK 。

APK 文件实际上是 ZIP 文件，可以使用标准解压缩实用程序（例如`unzip`. 但是，我们建议使用[apktool](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apktool)，它额外解码 AndroidManifest.xml 并将应用程序二进制文件 (classes.dex) 反汇编为 smali 代码：

```
$ apktool d UnCrackable-Level3.apk
$ tree
.
├── AndroidManifest.xml
├── apktool.yml
├── lib
├── original
│   ├── AndroidManifest.xml
│   └── META-INF
│       ├── CERT.RSA
│       ├── CERT.SF
│       └── MANIFEST.MF
├── res
...
└── smali
```

解压以下文件：

- AndroidManifest.xml：包含应用的包名、目标和最低[API级别](https://developer.android.com/guide/topics/manifest/uses-sdk-element#ApiLevels)、应用配置、应用组件、权限等的定义。
- original/META-INF：包含应用程序的元数据
- MANIFEST.MF：存储应用程序资源的哈希值
- CERT.RSA：应用程序的证书
- CERT.SF：资源列表和 MANIFEST.MF 文件中相应行的 SHA-1 摘要
- assets：包含应用程序资产（Android 应用程序中使用的文件，例如 XML 文件、JavaScript 文件和图片）的目录，[AssetManager](https://developer.android.com/reference/android/content/res/AssetManager)可以检索这些资产
- classes.dex：以DEX文件格式编译的类，Dalvik虚拟机/Android Runtime可以处理。DEX 是 Dalvik 虚拟机的 Java 字节码。它针对小型设备进行了优化
- lib：包含作为 APK 一部分的第 3 方库的目录
- res：包含尚未编译到 resources.arsc 中的资源的目录
- resources.arsc：包含预编译资源的文件，例如用于布局的 XML 文件

由于使用标准`unzip`实用程序解压缩会留下一些`AndroidManifest.xml`不可读的文件，因此最好使用[apktool](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apktool)解压缩 APK 。

```
$ ls -alh
total 32
drwxr-xr-x    9 sven  staff   306B Dec  5 16:29 .
drwxr-xr-x    5 sven  staff   170B Dec  5 16:29 ..
-rw-r--r--    1 sven  staff    10K Dec  5 16:29 AndroidManifest.xml
-rw-r--r--    1 sven  staff   401B Dec  5 16:29 apktool.yml
drwxr-xr-x    6 sven  staff   204B Dec  5 16:29 assets
drwxr-xr-x    3 sven  staff   102B Dec  5 16:29 lib
drwxr-xr-x    4 sven  staff   136B Dec  5 16:29 original
drwxr-xr-x  131 sven  staff   4.3K Dec  5 16:29 res
drwxr-xr-x    9 sven  staff   306B Dec  5 16:29 smali
```

##### Android Manifest[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#the-android-manifest)

Android Manifest 是主要的信息来源，它包括很多有趣的信息，例如包名、权限、应用程序组件等。

这是一些信息和相应关键字的非详尽列表，您可以通过检查文件或使用以下内容轻松地在 Android Manifest 中搜索它们`grep -i <keyword> AndroidManifest.xml`：

- 应用权限：（`permission`参见“ [Android Platform APIs](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/) ”）
- 备份津贴：（`android:allowBackup`请参阅“ [Android 上的数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)
- 应用程序组件：、、、、`activity`（请`service`参阅“ [Android 平台 API](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/) ”和“ [Android 上的数据存储”](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)`provider``receiver`
- 可调试标志：（`debuggable`参见“ [Android 应用程序的代码质量和构建设置](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/)”）

请参阅上述章节以了解有关如何测试每个点的更多信息。

##### 应用二进制[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#app-binary)

如上文“[探索应用程序包](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)`classes.dex`”中所示，可以在应用程序包的Root目录中找到应用程序二进制文件 ( )。它是一个所谓的 DEX（Dalvik 可执行文件）文件，其中包含已编译的 Java 代码。由于其性质，在应用一些转换后，您将能够使用反编译器生成 Java 代码。我们还看到了`smali`运行 apktool 后获得的文件夹。它包含以称为 smali 的中间语言编写的反汇编 Dalvik 字节码，smali 是 Dalvik 可执行文件的人类可读表示。

有关如何对 DEX 文件进行逆向工程的更多信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中的“[查看反编译的 Java 代码”部分。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)

##### 编译的应用程序二进制文件[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#compiled-app-binary)

在某些情况下，检索已编译的应用程序二进制文件 (.odex) 可能很有用。

首先获取应用程序数据目录的路径：

```
adb shell pm path com.example.myapplication
package:/data/app/~~DEMFPZh7R4qfUwwwh1czYA==/com.example.myapplication-pOslqiQkJclb_1Vk9-WAXg==/base.apk
```

删除`/base.apk`部分，添加`/oat/arm64/base.odex`并使用生成的路径从设备中提取 base.odex：

```
adb root
adb pull /data/app/~~DEMFPZh7R4qfUwwwh1czYA==/com.example.myapplication-pOslqiQkJclb_1Vk9-WAXg==/oat/arm64/base.odex
```

请注意，具体目录将Root据您的 Android 版本而有所不同。如果`/oat/arm64/base.odex`找不到该文件，请在返回的目录中手动搜索`pm path`。

##### Native库(NATIVE LIBRARIES)[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#native-libraries)

您可以检查`lib`APK 中的文件夹：

```
$ ls -1 lib/armeabi/
libdatabase_sqlcipher.so
libnative.so
libsqlcipher_android.so
libstlport_shared.so
```

或来自objection设备：

```
...g.vp.owasp_mobile.omtg_android on (google: 8.1.0) [usb] # ls lib
Type    ...  Name
------  ...  ------------------------
File    ...  libnative.so
File    ...  libdatabase_sqlcipher.so
File    ...  libstlport_shared.so
File    ...  libsqlcipher_android.so
```

目前，这就是您可以获得的有关Native库(NATIVE LIBRARIES)的所有信息，除非您开始对它们进行逆向工程，这是使用与用于逆向应用程序二进制文件的方法不同的方法完成的，因为此代码无法反编译，只能反汇编。有关如何对这些库进行逆向工程的更多信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中的“[查看反汇编Native代码”部分。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)

##### 其他应用资源[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#other-app-resources)

通常值得查看您可能在 APK 的Root文件夹中找到的其余资源和文件，因为有时它们包含其他好东西，如密钥存储、加密数据库、证书等。

#### 访问应用程序数据目录[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#accessing-app-data-directories)

安装该应用程序后，您可以探索更多信息，其中objection等工具会派上用场。

使用 objection 时可以检索各种信息，其中`env`会显示应用程序的所有目录信息。

```
$ objection -g sg.vp.owasp_mobile.omtg_android explore

...g.vp.owasp_mobile.omtg_android on (google: 8.1.0) [usb] # env

Name                    Path
----------------------  ---------------------------------------------------------------------------
cacheDirectory          /data/user/0/sg.vp.owasp_mobile.omtg_android/cache
codeCacheDirectory      /data/user/0/sg.vp.owasp_mobile.omtg_android/code_cache
externalCacheDirectory  /storage/emulated/0/Android/data/sg.vp.owasp_mobile.omtg_android/cache
filesDirectory          /data/user/0/sg.vp.owasp_mobile.omtg_android/files
obbDir                  /storage/emulated/0/Android/obb/sg.vp.owasp_mobile.omtg_android
packageCodePath         /data/app/sg.vp.owasp_mobile.omtg_android-kR0ovWl9eoU_yh0jPJ9caQ==/base.apk
```

在这些信息中，我们发现：

- `/data/data/[package-name]`位于或处的内部数据目录（又名沙箱目录）`/data/user/0/[package-name]`
- 外部数据目录位于`/storage/emulated/0/Android/data/[package-name]`或`/sdcard/Android/data/[package-name]`
- 应用程序包的路径在`/data/app/`

内部数据目录是应用程序用来存储Runtime(运行时)创建的数据的目录，其基本结构如下：

```
...g.vp.owasp_mobile.omtg_android on (google: 8.1.0)  [usb] # ls
Type       ...  Name
---------  ...  -------------------
Directory  ...  cache
Directory  ...  code_cache
Directory  ...  lib
Directory  ...  shared_prefs
Directory  ...  files
Directory  ...  databases

Readable: True  Writable: True
```

每个文件夹都有自己的用途：

- **cache**：此位置用于数据缓存。例如，WebView 缓存就在这个目录中。
- **code_cache**：这是用于存储缓存代码的文件系统特定于应用程序的缓存目录的位置。在运行 Android 5.0（API 级别 21）或更高版本的设备上，当应用程序或整个平台升级时，系统将删除存储在该位置的所有文件。
- **lib**：此文件夹存储用 C/C++ 编写的Native库(NATIVE LIBRARIES)。这些库可以具有多个文件扩展名之一，包括 .so 和 .dll（x86 支持）。此文件夹包含应用程序具有原生库的平台的子目录，包括
- armeabi：所有基于 ARM 的处理器的编译代码
- armeabi-v7a：编译代码适用于所有基于 ARM 的处理器，仅限版本 7 及更高版本
- arm64-v8a：所有基于 ARM 的 64 位处理器的编译代码，仅基于版本 8 及更高版本
- x86：仅针对 x86 处理器编译的代码
- x86_64：仅为 x86_64 处理器编译的代码
- mips：MIPS 处理器的编译代码
- **shared_prefs**：此文件夹包含一个 XML 文件，该文件存储通过[SharedPreferences API](https://developer.android.com/training/basics/data-storage/shared-preferences.html)保存的值。
- **files**：此文件夹存储应用程序创建的常规文件。
- **databases**：该文件夹存放应用在Runtime(运行时)生成的SQLite数据库文件，如用户数据文件。

但是，应用程序可能不仅在这些文件夹中而且在父文件夹 ( `/data/data/[package-name]`) 中存储更多数据。

有关安全存储敏感数据的更多信息和最佳实践，请参阅“[测试数据存储”一章。](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)

#### 监控系统日志[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#monitoring-system-logs)

在 Android 上，您可以使用 轻松检查系统消息的日志[`Logcat`](https://developer.android.com/tools/debugging/debugging-log.html)。Logcat的执行方式有两种：

- Logcat 是 Android Studio 中*Dalvik Debug Monitor Server* (DDMS) 的一部分。如果应用程序在调试模式下运行，日志输出将显示在 Logcat 选项卡上的 Android Monitor 中。您可以通过在 Logcat 中定义模式来过滤应用程序的日志输出。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/log_output_Android_Studio.png)

- 您可以使用 adb 执行 Logcat 以永久存储日志输出：

```
adb logcat > logcat.log
```

使用以下命令，您可以专门 grep 范围内应用程序的日志输出，只需插入包名称即可。当然，您的应用程序需要运行`ps`才能获得其 PID。

```
adb logcat | grep "$(adb shell ps | grep <package-name> | awk '{print $2}')"
```

## 设置网络测试环境[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-a-network-testing-environment)

### 基本网络监控/嗅探[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#basic-network-monitoringsniffing)

使用[tcpdump](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#tcpdump)、 netcat (nc) 和[Wireshark](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#wireshark)[可以实时远程嗅探所有 Android 流量](https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/)。首先，确保您的手机上安装了最新版本的[Android tcpdump](https://www.androidtcpdump.com/)。以下是[安装步骤](https://wladimir-tm4pda.github.io/porting/tcpdump.html)：

```
adb root
adb remount
adb push /wherever/you/put/tcpdump /system/xbin/tcpdump
```

如果执行`adb root`返回错误`adbd cannot run as root in production builds`，请按如下方式安装 tcpdump：

```
adb push /wherever/you/put/tcpdump /data/local/tmp/tcpdump
adb shell
su
mount -o rw,remount /system;
cp /data/local/tmp/tcpdump /system/xbin/
cd /system/xbin
chmod 755 tcpdump
```

在某些生产构建中，您可能会遇到错误`mount: '/system' not in /proc/mounts`。

在这种情况下，您可以将上面的行替换为`$ mount -o rw,remount /system;`，`$ mount -o rw,remount /`如[本 Stack Overflow 帖子](https://stackoverflow.com/a/28018008)中所述。

> 切记：要使用tcpdump，需要手机root权限！

执行`tcpdump`一次，看看是否有效。一旦有几个数据包进来，您可以按 CTRL+c 停止 tcpdump。

```
$ tcpdump
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on wlan0, link-type EN10MB (Ethernet), capture size 262144 bytes
04:54:06.590751 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
04:54:09.659658 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
04:54:10.579795 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
^C
3 packets captured
3 packets received by filter
0 packets dropped by kernel
```

要远程嗅探 Android 手机的网络流量，首先执行`tcpdump`并将其输出通过管道传输到`netcat`(nc)：

```
tcpdump -i wlan0 -s0 -w - | nc -l -p 11111
```

上面的 tcpdump 命令涉及

- 在 wlan0 接口上监听，
- 以字节为单位定义捕获的大小（快照长度）以获取所有内容（-s0），以及
- 写入文件 (-w)。我们传递的不是文件名，`-`这将使 tcpdump 写入标准输出。

通过使用管道 ( `|`)，我们将 tcpdump 的所有输出发送到 netcat，它在端口 11111 上打开一个侦听器。您通常需要监视 wlan0 接口。如果您需要另一个接口，请使用命令列出可用选项`$ ip addr`。

要访问端口 11111，您需要通过 adb 将端口转发到您的主机。

```
adb forward tcp:11111 tcp:11111
```

以下命令通过 netcat 和管道连接到转发端口到 Wireshark。

```
nc localhost 11111 | wireshark -k -S -i -
```

Wireshark 应立即启动 (-k)。它通过连接到转发端口的 netcat 从标准输入 (-i -) 获取所有数据。您应该从 wlan0 接口看到所有手机的流量。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/Android_Wireshark.png)

您可以使用 Wireshark 以人类可读的格式显示捕获的流量。弄清楚使用了哪些协议以及它们是否未加密。捕获所有流量（TCP 和 UDP）很重要，因此您应该执行被测应用程序的所有功能并对其进行分析。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/tcpdump_and_wireshard_on_android.png)

这个巧妙的小技巧现在可以让您识别使用了哪种协议以及应用程序正在与哪些端点通信。现在的问题是，如果 Burp 无法显示流量，我该如何测试端点？对此没有简单的答案，但一些 Burp 插件可以帮助您入门。

#### Firebase/谷歌云消息传递（FCM/GCM）[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#firebasegoogle-cloud-messaging-fcmgcm)

Firebase Cloud Messaging (FCM) 是 Google Cloud Messaging (GCM) 的继任者，是 Google 提供的一项免费服务，允许您在应用程序服务器和客户端应用程序之间发送消息。服务器和客户端应用程序通过 FCM/GCM 连接服务器进行通信，该服务器处理下游和上游消息。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/FCM-notifications-overview.png)

下游消息（推送通知）从应用服务器发送到客户端应用；上游消息从客户端应用程序发送到服务器。

FCM 适用于 Android、iOS 和 Chrome。FCM 目前提供两种连接服务器协议：HTTP 和 XMPP。如[官方文档](https://firebase.google.com/docs/cloud-messaging/server#choose)所述，这些协议的实现方式不同。以下示例演示了如何拦截这两种协议。

##### 测试设置的准备[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#preparation-of-test-setup)

您需要在手机上配置 iptables 或使用 bettercap 才能拦截流量。

FCM 可以使用 XMPP 或 HTTP 与 Google 后端通信。

##### HTTP[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#http)

FCM 使用端口 5228、5229 和 5230 进行 HTTP 通信。通常，仅使用端口 5228。

- 为 FCM 使用的端口配置本地端口转发。以下示例适用于 macOS：

```
$ echo "
rdr pass inet proto tcp from any to any port 5228-> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5229 -> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5230 -> 127.0.0.1 port 8080
" | sudo pfctl -ef -
```

- 拦截代理必须监听上面端口转发规则中指定的端口（端口8080）。

##### XMPP[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#xmpp)

对于 XMPP 通信，[FCM 使用端口](https://firebase.google.com/docs/cloud-messaging/xmpp-server-ref)5235（生产）和 5236（测试）。

- 为 FCM 使用的端口配置本地端口转发。以下示例适用于 macOS：

```
$ echo "
rdr pass inet proto tcp from any to any port 5235-> 127.0.0.1 port 8080
rdr pass inet proto tcp from any to any port 5236 -> 127.0.0.1 port 8080
" | sudo pfctl -ef -
```

##### 拦截请求[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#intercepting-the-requests)

拦截代理必须监听上面端口转发规则中指定的端口（端口8080）。

启动应用程序并触发使用 FCM 的函数。您应该在拦截代理中看到 HTTP 消息。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/FCM_Intercept.png)

##### 推送通知的端到端加密[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#end-to-end-encryption-for-push-notifications)

作为额外的安全层，可以使用[Capillary](https://github.com/google/capillary)对推送通知进行加密。Capillary 是一个库，用于简化从基于 Java 的应用程序服务器到 Android 客户端的端到端 (E2E) 加密推送消息的发送。

### 设置拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-an-interception-proxy)

一些工具支持对依赖 HTTP(S) 协议的应用程序进行网络分析。最重要的工具是所谓的拦截代理；[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)和[Burp Suite](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#burp-suite) Professional 是最著名的。拦截代理为测试人员提供了中间人的位置。这个位置对于读取和/或修改所有应用程序请求和端点响应很有用，这些请求和端点响应用于测试授权、会话、管理等。

#### 虚拟设备的拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#interception-proxy-for-a-virtual-device)

##### 在 ANDROID 虚拟设备 (AVD) 上设置 WEB 代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-a-web-proxy-on-an-android-virtual-device-avd)

以下过程适用于 Android Studio 3.x 附带的 Android 模拟器，用于在模拟器上设置 HTTP 代理：

1. 设置您的代理以侦听本地主机，例如端口 8080。
2. 在模拟器设置中配置 HTTP 代理：
   - 单击模拟器菜单栏中的三个点
   - 打开**设置**菜单
   - 单击**代理**选项卡
   - 选择**手动代理配置**
   - **在主机名字**段中输入“127.0.0.1”，在**端口号**字段中输入您的代理端口（例如，“8080”）
   - 点击**应用**

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/emulator-proxy.png)

HTTP 和 HTTPS 请求现在应该通过主机上的代理进行路由。如果没有，请尝试关闭和打开飞行模式。

还可以在启动 AVD 时使用[emulator 命令在命令行上配置 AVD 的代理。](https://developer.android.com/studio/run/emulator-commandline)以下示例启动 AVD Nexus_5X_API_23 并将代理设置为 127.0.0.1 和端口 8080。

```
emulator @Nexus_5X_API_23 -http-proxy 127.0.0.1:8080
```

##### 在虚拟设备上安装 CA 证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#installing-a-ca-certificate-on-the-virtual-device)

安装 CA 证书的一种简单方法是将证书推送到设备并通过安全设置将其添加到证书存储区。例如，您可以按如下方式安装 PortSwigger (Burp) CA 证书：

1. 启动 Burp 并使用主机上的 Web 浏览器导航到 burp/，然后`cacert.der`单击“CA 证书”按钮进行下载。

2. 将文件扩展名从更改`.der`为`.cer`.

3. 将文件推送到模拟器：

   ```
   adb push cacert.cer /sdcard/
   ```

4. 导航到**设置**->**安全**->**从 SD 卡安装**。

5. 向下滚动并点按`cacert.cer`。

然后系统会提示您确认安装证书（如果您还没有设置设备 PIN 码，系统还会要求您设置）。

这会将证书安装在用户证书存储中（在 Genymotion VM 上测试）。为了将证书放在Root存储中，您可以执行以下步骤：

1. `adb root`使用和以 root 身份运行 adb `adb shell`。
2. 在 找到新安装的证书`/data/misc/user/0/cacerts-added/`。
3. 将证书复制到以下文件夹`/system/etc/security/cacerts/`。
4. 重启Android虚拟机。

对于 Android 7.0（API 级别 24）及更高版本，请遵循“[绕过网络安全配置](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-the-network-security-configuration)”部分中描述的相同过程。

#### 物理设备的拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#interception-proxy-for-a-physical-device)

必须首先评估可用的网络设置选项。用于测试的移动设备和运行拦截代理的主机必须连接到同一 Wi-Fi 网络。使用（现有的）接入点或创建[临时无线网络](https://portswigger.net/support/creating-an-ad-hoc-wireless-network-in-os-x)。

配置网络并在测试主机和移动设备之间建立连接后，还需要执行几个步骤。

- 代理必须[配置为指向拦截代理](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp)。
- 拦截代理的[CA 证书必须添加到 Android 设备证书存储中的受信任证书中](https://portswigger.net/support/installing-burp-suites-ca-certificate-in-an-android-device)。用于存储 CA 证书的菜单的位置可能取决于 Android 版本和 Android OEM 对设置菜单的修改。
- 某些应用程序（例如[Chrome 浏览器](https://bugs.chromium.org/p/chromium/issues/detail?id=475745)）可能会显示`NET::ERR_CERT_VALIDITY_TOO_LONG`错误，如果叶证书的有效期恰好延长了特定时间（Chrome 为 39 个月）。如果使用默认的 Burp CA 证书，就会发生这种情况，因为 Burp Suite 颁发的叶证书与其 CA 证书具有相同的有效性。您可以通过创建自己的 CA 证书并将其导入 Burp Suite 来规避此问题，如本[博](https://blog.nviso.be/2018/01/31/using-a-custom-root-ca-with-burp-for-inspecting-android-n-traffic/)文中所述。

完成这些步骤并启动应用程序后，请求应显示在拦截代理中。

> [在secure.force.com](https://security.secure.force.com/security/tools/webapp/zapandroidsetup)上可以找到使用 Android 设备设置[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)的视频。

其他一些差异：从 Android 8.0（API 级别 26）开始，当 HTTPS 流量通过另一个连接隧道传输时，应用程序的网络行为会发生变化。从 Android 9（API 级别 28）开始，当握手期间出现问题时，SSLSocket 和 SSLEngine 在错误处理方面的行为会有所不同。

如前所述，从 Android 7.0（API 级别 24）开始，Android 操作系统将默认不再信任用户 CA 证书，除非在应用程序中指定。在下一节中，我们将介绍两种绕过此 Android 安全控制的方法。

#### 绕过网络安全配置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-the-network-security-configuration)

在本节中，我们将介绍几种绕过 Android[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)的方法。

##### 将自定义用户证书添加到网络安全配置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#adding-custom-user-certificates-to-the-network-security-configuration)

网络安全配置有不同的配置可用于通过 src 属性[添加非系统证书颁发机构：](https://developer.android.com/training/articles/security-config#CustomTrust)

```
<certificates src=["system" | "user" | "raw resource"]
              overridePins=["true" | "false"] />
```

每个证书可以是以下之一：

- `"raw resource"`是指向包含 X.509 证书的文件的 ID
- `"system"`对于预装的系统 CA 证书
- `"user"`对于用户添加的 CA 证书

App信任的CA证书可以是系统信任CA，也可以是用户CA。通常，您已经将拦截代理的证书添加为 Android 中的附加 CA。因此，我们将重点关注“用户”设置，它允许您使用以下网络安全配置强制 Android 应用程序信任此证书：

```
<network-security-config>
   <base-config>
      <trust-anchors>
          <certificates src="system" />
          <certificates src="user" />
      </trust-anchors>
   </base-config>
</network-security-config>
```

要实施此新设置，您必须按照以下步骤操作：

- 使用 apktool 等反编译工具反编译应用程序：

  ```
  apktool d <filename>.apk
  ```

- 通过创建包含`<certificates src="user" />`如上所述的网络安全配置，使应用程序信任用户证书

- 在反编译应用程序时进入apktool创建的目录并使用apktool重建应用程序。新的 apk 将在`dist`目录中。

  ```
  apktool b
  ```

- 您需要重新打包应用程序，如“逆向工程和篡改”一章的“[重新打包](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#repackaging)”部分所述。有关重新打包过程的更多详细信息，您还可以查阅[Android 开发人员文档](https://developer.android.com/studio/publish/app-signing#signing-manually)，该文档解释了整个过程。

请注意，即使此方法非常简单，其主要缺点是您必须对要评估的每个应用程序应用此操作，这会增加测试开销。

> 请记住，如果您正在测试的应用程序有额外的强化措施，例如验证应用程序签名，您可能无法再启动该应用程序。作为重新打包的一部分，您将使用自己的密钥对应用程序进行签名，因此签名更改将导致触发此类检查，从而可能导致应用程序立即终止。您需要通过在应用程序重新打包期间修补它们或通过 Frida 进行动态检测来识别和禁用此类检查。

有一个 python 脚本可以自动执行上述步骤，称为[Android-CertKiller](https://github.com/51j0/Android-CertKiller)。这个 Python 脚本可以从已安装的 Android 应用程序中提取 APK、反编译、使其可调试、添加允许用户证书的新网络安全配置、构建和签署新 APK 并使用 SSL 绕过安装新 APK。

```
python main.py -w

***************************************
Android CertKiller (v0.1)
***************************************

CertKiller Wizard Mode
---------------------------------
List of devices attached
4200dc72f27bc44d    device

---------------------------------

Enter Application Package Name: nsc.android.mstg.owasp.org.android_nsc

Package: /data/app/nsc.android.mstg.owasp.org.android_nsc-1/base.apk

I. Initiating APK extraction from device
   complete
------------------------------
I. Decompiling
   complete
------------------------------
I. Applying SSL bypass
   complete
------------------------------
I. Building New APK
   complete
------------------------------
I. Signing APK
   complete
------------------------------

Would you like to install the APK on your device(y/N): y
------------------------------------
 Installing Unpinned APK
------------------------------
Finished
```

##### 使用 MAGISK 在系统信任的 CA 中添加代理的证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#adding-the-proxys-certificate-among-system-trusted-cas-using-magisk)

为了避免为每个应用程序配置网络安全配置的义务，我们必须强制设备接受代理的证书作为系统信任的证书之一。

有一个[Magisk 模块](https://github.com/NVISO-BE/MagiskTrustUserCerts)会自动将所有用户安装的 CA 证书添加到系统信任的 CA 列表中。

[在Github 发布页面](https://github.com/NVISO-BE/MagiskTrustUserCerts/releases)下载最新版本的模块，将下载的文件推送到设备并通过单击`+`按钮将其导入 Magisk Manager 的“模块”视图。最后，Magisk Manager 需要重启才能让更改生效。

从现在开始，用户通过“设置”、“安全和位置”、“加密和凭据”、“从存储安装”（位置可能不同）安装的任何 CA 证书都会由此自动推送到系统的信任库中魔力模块。重新启动并验证 CA 证书是否列在“设置”、“安全和位置”、“加密和凭据”、“受信任的凭据”（位置可能不同）中。

##### 在系统信任的 CA 中手动添加 PROXY 的证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#manually-adding-the-proxys-certificate-among-system-trusted-cas)

或者，您可以手动执行以下步骤以获得相同的结果：

- 使 /system 分区可写，这只有在有Root设备上才有可能。运行“mount”命令以确保 /system 是可写的：`mount -o rw,remount /system`。如果此命令失败，请尝试运行以下命令`mount -o rw,remount -t ext4 /system`

- 准备代理的 CA 证书以匹配系统证书格式。以格式导出代理的证书`der`（这是 Burp Suite 中的默认格式），然后运行以下命令：

  ```
  $ openssl x509 -inform DER -in cacert.der -out cacert.pem
  $ openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1
  mv cacert.pem <hash>.0
  ```

- 最后，将该`<hash>.0`文件复制到目录 /system/etc/security/cacerts 中，然后运行以下命令：

  ```
  chmod 644 <hash>.0
  ```

通过执行上述步骤，您允许任何应用程序信任代理的证书，这允许您拦截其流量，当然除非应用程序使用 SSL 固定。

### 潜在障碍[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#potential-obstacles)

应用程序通常实施安全控制，这使得对应用程序执行安全审查变得更加困难，例如Root检测和证书固定。理想情况下，您将获得启用这些控件的应用程序版本和禁用控件的应用程序版本。这允许您分析控件的正确实现，之后您可以继续使用安全性较低的版本进行进一步测试。

当然，这并不总是可行的，您可能需要对启用所有安全控制的应用程序执行黑盒评估。下面的部分向您展示了如何绕过不同应用程序的证书固定。

#### 无线网络中的客户端隔离[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#client-isolation-in-wireless-networks)

一旦设置了拦截代理并拥有 MITM 位置，您可能仍然看不到任何东西。这可能是由于应用程序中的限制（请参阅下一节），但也可能是由于您所连接的 Wi-Fi 中所谓的客户端隔离。

[无线客户端隔离](https://documentation.meraki.com/MR/Firewall_and_Traffic_Shaping/Wireless_Client_Isolation)是一种安全功能，可防止无线客户端相互通信。此功能对来宾和 BYOD SSID 很有用，可增加安全级别以限制连接到无线网络的设备之间的攻击和威胁。

如果我们需要测试的Wi-Fi有客户端隔离怎么办？

你可以在你的Android设备上配置代理指向127.0.0.1:8080，通过USB连接你的手机到你的主机并使用adb做一个反向端口转发：

```
adb reverse tcp:8080 tcp:8080
```

完成此操作后，Android 手机上的所有代理流量都将转到 127.0.0.1 上的 8080 端口，并将通过 adb 重定向到主机上的 127.0.0.1:8080，现在您将在 Burp 中看到流量。使用此技巧，您还可以在具有客户端隔离的 Wi-Fi 中测试和拦截流量。

#### 非代理感知应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#non-proxy-aware-apps)

一旦设置了拦截代理并拥有 MITM 位置，您可能仍然看不到任何东西。这主要是由于以下原因：

- 该应用程序使用像 Xamarin 这样的框架，它Root本不使用 Android 操作系统的代理设置或
- 您正在测试的应用程序正在验证是否设置了代理并且现在不允许任何通信。

在这两种情况下，您都需要额外的步骤才能最终看到流量。在下面的部分中，我们将描述两种不同的解决方案，bettercap 和 iptables。

您还可以使用受您控制的接入点来重定向流量，但这需要额外的硬件，我们现在专注于软件解决方案。

> 对于这两种解决方案，您需要在代理选项卡/选项/编辑界面中的 Burp 中激活“支持不可见代理”。

##### IPTABLES[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#iptables)

您可以在 Android 设备上使用 iptables 将所有流量重定向到您的拦截代理。以下命令会将端口 80 重定向到在端口 8080 上运行的代理

```
iptables -t nat -A OUTPUT -p tcp --dport 80 -j DNAT --to-destination <Your-Proxy-IP>:8080
```

验证 iptables 设置并检查 IP 和端口。

```
$ iptables -t nat -L
Chain PREROUTING (policy ACCEPT)
target     prot opt source               destination

Chain INPUT (policy ACCEPT)
target     prot opt source               destination

Chain OUTPUT (policy ACCEPT)
target     prot opt source               destination
DNAT       tcp  --  anywhere             anywhere             tcp dpt:5288 to:<Your-Proxy-IP>:8080

Chain POSTROUTING (policy ACCEPT)
target     prot opt source               destination

Chain natctrl_nat_POSTROUTING (0 references)
target     prot opt source               destination

Chain oem_nat_pre (0 references)
target     prot opt source               destination
```

如果你想重置 iptables 配置，你可以刷新规则：

```
iptables -t nat -F
```

##### 贝特帽[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bettercap)

[阅读“测试网络通信](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/)”一章和测试用例“[模拟中间人攻击](https://mas.owasp.org/MASTG/General/0x04f-Testing-Network-Communication/#simulating-a-man-in-the-middle-attack-with-bettercap)”以进一步准备和运行 bettercap 的说明。

运行代理的主机和 Android 设备必须连接到同一无线网络。使用以下命令启动 bettercap，将下面的 IP 地址 (XXXX) 替换为您的 Android 设备的 IP 地址。

```
$ sudo bettercap -eval "set arp.spoof.targets X.X.X.X; arp.spoof on; set arp.spoof.internal true; set arp.spoof.fullduplex true;"
bettercap v2.22 (built for darwin amd64 with go1.12.1) [type 'help' for a list of commands]

[19:21:39] [sys.log] [inf] arp.spoof enabling forwarding
[19:21:39] [sys.log] [inf] arp.spoof arp spoofer started, probing 1 targets.
```

#### 代理检测[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#proxy-detection)

一些移动应用程序正在尝试检测是否设置了代理。如果是这种情况，他们会认为这是恶意的并且无法正常工作。

为了绕过这种保护机制，您可以设置 bettercap 或配置不需要在您的 Android 手机上设置代理的 iptables。我们之前没有提到但适用于此场景的第三个选项是使用 Frida。[`ProxyInfo`](https://developer.android.com/reference/android/net/ProxyInfo)在 Android 上可以通过查询类并检查 getHost() 和 getPort() 方法来检测是否设置了系统代理。可能有多种其他方法可以实现相同的任务，您需要反编译 APK 才能识别实际的类和方法名称。

您可以在下面找到 Frida 脚本的样板源代码，该脚本将帮助您重载验证代理是否已设置并始终返回 false 的方法（在本例中称为 isProxySet）。即使现在配置了代理，应用程序现在也会认为没有设置任何代理，因为函数返回 false。

```
setTimeout(function(){
    Java.perform(function (){
        console.log("[*] Script loaded")

        var Proxy = Java.use("<package-name>.<class-name>")

        Proxy.isProxySet.overload().implementation = function() {
            console.log("[*] isProxySet function invoked")
            return false
        }
    });
});
```

### 绕过证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-certificate-pinning)

一些应用程序将实施 SSL Pinning，这会阻止应用程序接受您的拦截证书作为有效证书。这意味着您将无法监控应用程序和服务器之间的流量。

对于大多数应用程序，可以在几秒钟内绕过证书固定，但前提是应用程序使用这些工具涵盖的 API 函数。如果应用程序使用自定义框架或库实施 SSL Pinning，则必须手动修补和停用 SSL Pinning，这可能很耗时。

本节介绍绕过 SSL Pinning 的各种方法，并提供有关在现有工具无济于事时应该采取的措施的指导。

#### 绕过方法[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-methods)

有几种方法可以绕过黑盒测试的证书固定，具体取决于设备上可用的框架：

- Cydia Substrate：安装[Android-SSL-TrustKiller](https://github.com/iSECPartners/Android-SSL-TrustKiller)包。
- Frida：使用[frida-multiple-unpinning](https://codeshare.frida.re/@akabe1/frida-multiple-unpinning/)脚本。
- objection：使用`android sslpinning disable`命令。
- Xposed：安装[TrustMeAlready](https://github.com/ViRb3/TrustMeAlready)或[SSLUnpinning](https://github.com/ac-pm/SSLUnpinning_Xposed)模块。

如果你有安装了 frida-server 的 root 设备，你可以通过运行以下[Objection](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)命令来绕过 SSL 固定（如果你使用的是非 root 设备，请[重新打包你的应用程序）：](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#repackaging-apps)

```
android sslpinning disable
```

下面是一个输出示例：

![反对 Android SSL Pinning 绕过](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/Images/Chapters/0x05b/android_ssl_pinning_bypass.png)

另请参阅[Objection 关于为 Android 禁用 SSL Pinning 的帮助以](https://github.com/sensepost/objection/blob/master/objection/console/helpfiles/android.sslpinning.disable.txt)获取更多信息，并检查[pinning.ts](https://github.com/sensepost/objection/blob/master/agent/src/android/pinning.ts)文件以了解旁路的工作原理。

#### 静态绕过自定义证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypass-custom-certificate-pinning-statically)

在应用程序的某处，必须定义端点和证书（或其哈希）。反编译应用程序后，您可以搜索：

- 证书哈希：`grep -ri "sha256\|sha1" ./smali`. 用您的代理 CA 的哈希值替换已识别的哈希值。或者，如果哈希伴随着域名，您可以尝试将域名修改为不存在的域，以便不固定原始域。这适用于混淆的 OkHTTP 实现。
- 证书文件：`find ./assets -type f \( -iname \*.cer -o -iname \*.crt \)`. 用您代理的证书替换这些文件，确保它们的格式正确。
- 信任库文件：`find ./ -type f \( -iname \*.jks -o -iname \*.bks \)`. 将代理的证书添加到信任库并确保它们的格式正确。

> 请记住，应用程序可能包含没有扩展名的文件。最常见的文件位置是`assets`和`res`目录，也应该对其进行调查。

例如，假设您找到一个使用 BKS (BouncyCastle) 信任库的应用程序并且它存储在文件`res/raw/truststore.bks`. 要绕过 SSL Pinning，您需要使用命令行工具将代理的证书添加到信任库`keytool`。`Keytool`Java SDK自带，执行命令需要以下值：

- password - 密钥库的密码。在反编译的应用程序代码中查找硬编码密码。
- providerpath - BouncyCastle Provider jar 文件的位置。您可以从[The Legion of the Bouncy Castle](https://www.bouncycastle.org/latest_releases.html)下载它。
- proxy.cer - 您的代理证书。
- aliascert - 将用作代理证书别名的唯一值。

要添加代理的证书，请使用以下命令：

```
keytool -importcert -v -trustcacerts -file proxy.cer -alias aliascert -keystore "res/raw/truststore.bks" -provider org.bouncycastle.jce.provider.BouncyCastleProvider -providerpath "providerpath/bcprov-jdk15on-164.jar" -storetype BKS -storepass password
```

要列出 BKS 信任库中的证书，请使用以下命令：

```
keytool -list -keystore "res/raw/truststore.bks" -provider org.bouncycastle.jce.provider.BouncyCastleProvider -providerpath "providerpath/bcprov-jdk15on-164.jar"  -storetype BKS -storepass password
```

进行这些修改后，使用 apktool 重新打包应用程序并将其安装到您的设备上。

如果应用程序使用本地库来实现网络通信，则需要进一步进行逆向工程。可以在博客文章[识别 smali 代码中的 SSL Pinning 逻辑、修补它并重新组装 APK中找到这种方法的示例](https://serializethoughts.wordpress.com/2016/08/18/bypassing-ssl-pinning-in-android-applications/)

#### 动态绕过自定义证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypass-custom-certificate-pinning-dynamically)

动态绕过固定逻辑使其更加方便，因为无需绕过任何完整性检查，并且执行试错尝试要快得多。

找到正确的Hook方法通常是最困难的部分，并且可能需要相当长的时间，具体取决于混淆程度。由于开发人员通常会重用现有库，因此搜索标识所用库的字符串和许可文件是一种很好的方法。确定库后，检查未混淆的源代码以找到适合动态检测的方法。

例如，假设您找到一个使用混淆的 OkHTTP3 库的应用程序。[文档](https://square.github.io/okhttp/3.x/okhttp/)显示该类`CertificatePinner.Builder`负责为特定域添加引脚。如果您可以修改[Builder.add 方法](https://square.github.io/okhttp/3.x/okhttp/okhttp3/CertificatePinner.Builder.html#add-java.lang.String-java.lang.String...-)的参数，则可以将散列更改为属于您的证书的正确散列。可以通过两种方式找到正确的方法，正如Jeroen Beckers在[这篇博文中所解释的那样：](https://blog.nviso.eu/2019/04/02/circumventing-ssl-pinning-in-obfuscated-apps-with-okhttp/)

- 按照上一节中的说明搜索哈希和域名。实际固定方法通常会在这些字符串附近使用或定义
- 在 SMALI 代码中搜索方法签名

对于 Builder.add 方法，您可以通过运行以下 grep 命令找到可能的方法：`grep -ri java/lang/String;\[Ljava/lang/String;)L ./`

此命令将搜索所有将字符串和字符串变量列表作为参数的方法，并返回一个复杂对象。Root据应用程序的大小，代码中可能有一个或多个匹配项。

使用 Frida Hook每个方法并打印参数。其中一个将打印出域名和证书哈希，之后您可以修改参数以规避已实施的固定。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#references)

- 手动签名（Android 开发人员文档）- https://developer.android.com/studio/publish/app-signing#signing-manually
- 自定义信任 - https://developer.android.com/training/articles/security-config#CustomTrust
- Android 网络安全配置培训 - https://developer.android.com/training/articles/security-config
- Android P 网络安全配置安全分析师指南 - [https://www.nowsecure.com/blog/2018/08/15/a-security-analysts-guide-to-network-security-configuration-in-android-p /](https://www.nowsecure.com/blog/2018/08/15/a-security-analysts-guide-to-network-security-configuration-in-android-p/)
- Android 8.0 行为变化 - https://developer.android.com/about/versions/oreo/android-8.0-changes
- Android 9.0 行为变更 - https://developer.android.com/about/versions/pie/android-9.0-changes-all#device-security-changes
- 代号、标签和版本号 - https://source.android.com/setup/start/build-numbers
- 创建和管理虚拟设备 - https://developer.android.com/studio/run/managing-avds.html
- 移动设备Root指南 - https://www.xda-developers.com/root/
- API 级别 - https://developer.android.com/guide/topics/manifest/uses-sdk-element#ApiLevels
- AssetManager - https://developer.android.com/reference/android/content/res/AssetManager
- SharedPreferences API - https://developer.android.com/training/basics/data-storage/shared-preferences.html
- 使用 Logcat 调试 - https://developer.android.com/studio/command-line/logcat
- Android 的 APK 格式 - https://en.wikipedia.org/wiki/Apk_(file_format)
- 使用 Tcpdump、nc 和 Wireshark 进行 Android 远程嗅探 - https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/
- 无线客户端隔离 - https://documentation.meraki.com/MR/Firewall_and_Traffic_Shaping/Wireless_Client_Isolation
