# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 2 · part 1

> 分段 1/2。索引见 `Android平台概览-p2.md`。

# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 2

> 分段 2/4。索引见 `Android平台概览.md`。

## 承接

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
