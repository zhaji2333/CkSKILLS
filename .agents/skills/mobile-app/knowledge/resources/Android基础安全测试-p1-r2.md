# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 1 · part 2

> 分段 2/2。索引见 `Android基础安全测试-p1.md`。

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

