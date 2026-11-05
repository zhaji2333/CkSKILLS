# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 2 · part 2

> 分段 2/2。索引见 `Android基础安全测试-p2.md`。

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
