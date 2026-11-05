# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 1 · part 1

> 分段 1/2。索引见 `Android代码质量和构建设置-p1.md`。

# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 1

> 分段 1/2。索引见 `Android代码质量和构建设置.md`。

# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings)

## 确保应用程序已正确签名 (MSTG-CODE-1)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#making-sure-that-the-app-is-properly-signed-mstg-code-1)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview)

Android 要求所有 APK 在安装或运行之前使用证书进行数字签名。数字签名用于验证应用程序更新的所有者身份。此过程可以防止应用程序被篡改或修改以包含恶意代码。

签名 APK 时，会附加一个公钥证书。此证书将 APK 与开发者和开发者的私钥唯一关联。在调试模式下构建应用程序时，Android SDK 使用专门为调试目的创建的调试密钥对应用程序进行签名。使用调试密钥签名的应用程序不打算分发，也不会被大多数应用程序商店（包括 Google Play 商店）接受。

应用程序的[最终发布版本](https://developer.android.com/studio/publish/app-signing.html)必须使用有效的发布密钥进行签名。在 Android Studio 中，可以手动或通过创建分配给发布构建类型的签名配置来对应用进行签名。

Android 9之前（API level 28）Android上所有应用更新都需要使用同一个证书进行签名，所以[建议有效期为25年以上](https://developer.android.com/studio/publish/app-signing#considerations)。在 Google Play 上发布的应用程序必须使用有效期在 2033 年 10 月 22 日之后结束的密钥进行签名。

三种 APK 签名方案可用：

- JAR 签名（v1 方案），
- APK Signature Scheme v2（v2方案），
- APK Signature Scheme v3（v3 方案）。

Android 7.0（API 级别 24）及更高版本支持的 v2 签名与 v1 方案相比提供了更高的安全性和性能。Android 9（API 级别 28）及更高版本支持的 V3 签名使应用能够在 APK 更新时更改其签名密钥。此功能通过允许使用新旧密钥来确保兼容性和应用程序的持续可用性。请注意，在撰写本文时，它只能通过 apksigner 获得。

对于每个签名方案，发布版本也应该始终通过其以前的所有方案进行签名。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis)

确保已通过适用于 Android 7.0（API 级别 24）及更高版本的 v1 和 v2 方案以及适用于 Android 9（API 级别 28）及更高版本的所有三种方案对发布版本进行签名，并且代码签名证书在 APK 中属于开发者。

可以使用该`apksigner`工具验证 APK 签名。它位于`[SDK-Path]/build-tools/[version]`。

```
$ apksigner verify --verbose Desktop/example.apk
Verifies
Verified using v1 scheme (JAR signing): true
Verified using v2 scheme (APK Signature Scheme v2): true
Verified using v3 scheme (APK Signature Scheme v3): true
Number of signers: 1
```

可以使用 来检查签名证书的内容`jarsigner`。请注意，Common Name (CN) 属性在调试证书中设置为“Android Debug”。

使用调试证书签名的 APK 的输出如下所示：

```
$ jarsigner -verify -verbose -certs example.apk

sm     11116 Fri Nov 11 12:07:48 ICT 2016 AndroidManifest.xml

      X.509, CN=Android Debug, O=Android, C=US
      [certificate is valid from 3/24/16 9:18 AM to 8/10/43 9:18 AM]
      [CertPath not validated: Path doesn\'t chain with any of the trust anchors]
(...)
```

忽略“CertPath 未验证”错误。Java SDK 7 及更高版本会出现此错误。`jarsigner`您可以依靠`apksigner`来验证证书链，而不是。

签名配置可以通过 Android Studio`signingConfig`或`build.gradle`. 要激活 v1 和 v2 方案，必须设置以下值：

```
v1SigningEnabled true
v2SigningEnabled true
```

官方 Android 开发人员文档中提供了[配置应用程序发布](https://developer.android.com/tools/publishing/preparing.html#publishing-configure)的几个最佳实践。

最后但同样重要的是：确保应用程序从未使用您的内部测试证书进行部署。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis)

应使用静态分析来验证 APK 签名。

## 测试应用程序是否可调试 (MSTG-CODE-2)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#testing-whether-the-app-is-debuggable-mstg-code-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_1)

[Android 清单中定义的元素](https://developer.android.com/guide/topics/manifest/application-element.html)中的`android:debuggable`属性决定了应用程序是否可以调试。[`Application`](https://developer.android.com/guide/topics/manifest/application-element.html)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_1)

检查`AndroidManifest.xml`以确定`android:debuggable`属性是否已设置并找到属性的值：

```
    ...
    <application android:allowBackup="true" android:debuggable="true" android:icon="@drawable/ic_launcher" android:label="@string/app_name" android:theme="@style/AppTheme">
    ...
```

您可以通过`aapt`以下命令行使用 Android SDK 中的工具来快速检查`android:debuggable="true"`指令是否存在：

```
# If the command print 1 then the directive is present
# The regex search for this line: android:debuggable(0x0101000f)=(type 0x12)0xffffffff
$ aapt d xmltree sieve.apk AndroidManifest.xml | grep -Ec "android:debuggable\(0x[0-9a-f]+\)=\(type\s0x[0-9a-f]+\)0xffffffff"
1
```

对于发布版本，此属性应始终设置为`"false"`（默认值）。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_1)

`adb`可用于确定应用程序是否可调试。

使用以下命令：

```
# If the command print a number superior to zero then the application have the debug flag
# The regex search for these lines:
# flags=[ DEBUGGABLE HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP ]
# pkgFlags=[ DEBUGGABLE HAS_CODE ALLOW_CLEAR_USER_DATA ALLOW_BACKUP ]
$ adb shell dumpsys package com.mwr.example.sieve | grep -c "DEBUGGABLE"
2
$ adb shell dumpsys package com.nondebuggableapp | grep -c "DEBUGGABLE"
0
```

如果应用程序是可调试的，则执行应用程序命令是微不足道的。在`adb`shell 中，`run-as`通过将包名称和应用程序命令附加到二进制名称来执行：

```
$ run-as com.vulnerable.app id
uid=10084(u0_a84) gid=10084(u0_a84) groups=10083(u0_a83),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats) context=u:r:untrusted_app:s0:c512,c768
```

[Android Studio](https://developer.android.com/tools/debugging/debugging-studio.html)还可用于调试应用程序和验证应用程序的调试激活。

另一种确定应用程序是否可调试的方法是附加`jdb`到正在运行的进程。如果成功，将激活调试。

以下过程可用于启动调试会话`jdb`：

1. 使用`adb`和`jdwp`，确定您要调试的活动应用程序的 PID：

   ```
   $ adb jdwp
   2355
   16346  <== last launched, corresponds to our application
   ```

2. `adb`通过使用特定的本地端口在应用程序进程（带有 PID）和您的主机之间创建一个通信通道：

   ```
   # adb forward tcp:[LOCAL_PORT] jdwp:[APPLICATION_PID]
   $ adb forward tcp:55555 jdwp:16346
   ```

3. 使用`jdb`，将调试器附加到本地通信通道端口并启动调试会话：

   ```
   $ jdb -connect com.sun.jdi.SocketAttach:hostname=localhost,port=55555
   Set uncaught java.lang.Throwable
   Set deferred uncaught java.lang.Throwable
   Initializing jdb ...
   > help
   ```

关于调试的几点说明：

- 该工具[`JADX`](https://github.com/skylot/jadx)可用于识别感兴趣的断点插入位置。
- 可以在[Tutorialspoint](https://www.tutorialspoint.com/jdb/jdb_basic_commands.htm)找到 jdb 基本命令的用法。
- 如果在绑定到本地通信通道端口时收到错误提示“与调试器的连接已关闭” `jdb`，请终止所有 adb 会话并启动一个新会话。

## 调试符号测试 (MSTG-CODE-3)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#testing-for-debugging-symbols-mstg-code-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_2)

通常，您应该提供尽可能少的解释的编译代码。一些元数据，例如调试信息、行号和描述性函数或方法名称，使逆向工程师更容易理解二进制或字节码，但在发布版本中不需要这些，因此可以安全地省略而不会影响应用程序的功能。

要检查Native二进制文件，请使用标准工具（如`nm`或`objdump`检查符号表）。发布版本通常不应包含任何调试符号。如果目标是混淆库，还建议删除不必要的动态符号。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_2)

符号通常在构建过程中被剥离，因此您需要编译的字节码和库来确保丢弃不必要的元数据。

首先，`nm`在您的 Android NDK 中找到二进制文件并将其导出（或创建别名）。

```
export NM = $ANDROID_NDK_DIR/toolchains/arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-nm
```

显示调试符号：

```
$NM -a libfoo.so
/tmp/toolchains/arm-linux-androideabi-4.9/prebuilt/darwin-x86_64/bin/arm-linux-androideabi-nm: libfoo.so: no symbols
```

显示动态符号：

```
$NM -D libfoo.so
```

或者，在您喜欢的反汇编程序中打开文件并手动检查符号表。

可以通过`visibility`编译器标志去除动态符号。添加此标志会导致 gcc 丢弃函数名称，同时保留声明为`JNIEXPORT`.

确保以下内容已添加到 build.gradle 中：

```
externalNativeBuild {
    cmake {
        cppFlags "-fvisibility=hidden"
    }
}
```

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_2)

应该使用静态分析来验证调试符号。

## 测试调试代码和详细错误记录 (MSTG-CODE-4)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#testing-for-debugging-code-and-verbose-error-logging-mstg-code-4)

