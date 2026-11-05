# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 2 · part 1

> 分段 1/2。索引见 `Android基础安全测试-p2.md`。

# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 2

> 分段 2/5。索引见 `Android基础安全测试.md`。

## 承接

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

