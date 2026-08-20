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

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_3)

StrictMode 是一种开发人员工具，用于检测违规行为，例如应用程序主线程上的意外磁盘或网络访问。它还可用于检查良好的编码实践，例如实现高性能代码。

下面是一个为磁盘和网络访问主线程启用策略[的示例：`StrictMode`](https://developer.android.com/reference/android/os/StrictMode.html)

```
public void onCreate() {
     if (DEVELOPER_MODE) {
         StrictMode.setThreadPolicy(new StrictMode.ThreadPolicy.Builder()
                 .detectDiskReads()
                 .detectDiskWrites()
                 .detectNetwork()   // or .detectAll() for all detectable problems
                 .penaltyLog()
                 .build());
         StrictMode.setVmPolicy(new StrictMode.VmPolicy.Builder()
                 .detectLeakedSqlLiteObjects()
                 .detectLeakedClosableObjects()
                 .penaltyLog()
                 .penaltyDeath()
                 .build());
     }
     super.onCreate();
 }
```

建议在带有条件的`if`语句中插入策略。`DEVELOPER_MODE`要禁用`StrictMode`，`DEVELOPER_MODE`必须为发布版本禁用。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_3)

要确定是否`StrictMode`已启用，您可以查找`StrictMode.setThreadPolicy`或`StrictMode.setVmPolicy`方法。他们很可能会在`onCreate`方法中。

线程策略的[检测方法](https://javabeat.net/strictmode-android-1/)是

```
detectDiskWrites()
detectDiskReads()
detectNetwork()
```

[违反线程策略](https://javabeat.net/strictmode-android-1/)的惩罚是

```
penaltyLog() // Logs a message to LogCat
penaltyDeath() // Crashes application, runs at the end of all enabled penalties
penaltyDialog() // Shows a dialog
```

查看使用 StrictMode 的[最佳实践](https://code.tutsplus.com/tutorials/android-best-practices-strictmode--mobile-7581)。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_3)

有几种检测方法`StrictMode`；最佳选择取决于政策角色的实施方式。他们包括

- 日志,
- 一个警告对话框，
- 应用程序崩溃。

## 检查第三方库中的弱点 (MSTG-CODE-5)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#checking-for-weaknesses-in-third-party-libraries-mstg-code-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_4)

Android 应用程序通常使用第三方库。这些第三方库加速了开发，因为开发人员必须编写更少的代码才能解决问题。库分为两类：

- 没有（或不应）打包在实际生产应用程序中的库，例如`Mockito`用于测试的库和`JavaAssist`用于编译某些其他库的库。
- 打包在实际生产应用程序中的库，例如`Okhttp3`.

这些库可能会导致不必要的副作用：

- 一个库可能包含一个漏洞，这将使应用程序容易受到攻击。一个很好的例子是`OKHTTP`2.7.5 之前的版本，其中 TLS 链污染可以绕过 SSL 固定。
- 库无法再维护或几乎无法使用，这就是没有报告和/或修复漏洞的原因。这可能会导致通过库在您的应用程序中出现错误和/或易受攻击的代码。
- 库（Libraries）可以使用 LGPL2.1 等Licenses（许可证），这要求应用程序作者为使用该应用程序并要求深入了解其源代码的人提供对源代码的访问权限。事实上，应用程序应该被允许在修改其源代码的情况下重新分发。这可能危及应用程序的知识产权 (IP)。

请注意，此问题可能存在于多个层面：当您使用 webview 并在 webview 中运行 JavaScript 时，JavaScript 库也可能存在这些问题。这同样适用于 Cordova、React-native 和 Xamarin 应用程序的插件/库。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_4)

#### 检测第三方库的漏洞[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#detecting-vulnerabilities-of-third-party-libraries)

检测第三方依赖项中的漏洞可以通过 OWASP 依赖项检查器来完成。这最好通过使用 gradle 插件来完成，例如[`dependency-check-gradle`](https://github.com/jeremylong/dependency-check-gradle). 为了使用该插件，需要执行以下步骤： 通过将以下脚本添加到您的 build.gradle，从 Maven 中央存储库安装插件：

```
buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath 'org.owasp:dependency-check-gradle:3.2.0'
    }
}

apply plugin: 'org.owasp.dependencycheck'
```

gradle 调用插件后，您可以通过运行以下命令创建报告：

```
gradle assemble
gradle dependencyCheckAnalyze --info
```

`build/reports`除非另有配置，否则报告将在。使用该报告来分析发现的漏洞。鉴于在库中发现的漏洞，请参阅补救措施。

请注意，该插件需要下载漏洞源。如果插件出现问题，请查阅文档。

或者，有一些商业工具可能更好地覆盖为正在使用的库找到的依赖项，例如[Sonatype Nexus IQ](https://www.sonatype.com/nexus/iqserver)、[Sourceclear](https://www.sourceclear.com/)、[Snyk](https://snyk.io/)或[Blackduck](https://www.blackducksoftware.com/)。使用 OWASP Dependency Checker 或其他工具的实际结果因（NDK 相关或 SDK 相关）库的类型而异。

最后，请注意对于混合应用程序，必须使用 RetireJS 检查 JavaScript 依赖项。同样对于 Xamarin，必须检查 C# 依赖项。

当发现某个库包含漏洞时，则适用以下推理：

- 该库是否与应用程序打包在一起？然后查看该库是否有补丁漏洞的版本。如果不是，请检查该漏洞是否实际影响了应用程序。如果是这种情况或将来可能是这种情况，那么寻找一种提供类似功能但没有漏洞的替代方案。
- 该库是否未与应用程序打包在一起？看看有没有修复漏洞的补丁版本。如果不是这种情况，请检查漏洞对构建过程的影响。该漏洞是否会阻碍构建或削弱构建管道的安全性？然后尝试寻找修复漏洞的替代方案。

当源不可用时，可以反编译应用程序并检查 JAR 文件。当正确应用 Dexguard 或[ProGuard](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#proguard)时，有关库的版本信息通常会被混淆并因此消失。否则，您仍然可以在给定库的 Java 文件的注释中经常找到这些信息。MobSF 等工具可以帮助分析应用程序中可能包含的库。如果您可以通过注释或某些版本中使用的特定方法检索库的版本，则可以手动查找 CVE。

如果应用程序是高风险应用程序，您将最终手动审查库。在这种情况下，对Native代码有特定要求，您可以在“[测试代码质量](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/)”一章中找到这些要求。其次，最好检查是否应用了所有软件工程最佳实践。

#### 检测应用程序库使用的Licenses（许可证）[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#detecting-the-licenses-used-by-the-libraries-of-the-application)

为了确保不侵犯版权法，最好使用一个可以迭代不同库的插件来检查依赖关系，例如`License Gradle Plugin`. 可以通过以下步骤使用此插件。

在你的`build.gradle`文件中添加：

```
plugins {
    id "com.github.hierynomus.license-report" version"{license_plugin_version}"
}
```

现在，选择插件后，使用以下命令：

```
gradle assemble
gradle downloadLicenses
```

现在会生成一个license-report，可以用来查询第三方库使用的license。请检查许可协议以查看应用程序是否需要包含版权声明以及许可类型是否需要开源应用程序的代码。

与依赖性检查类似，还有一些商业工具也可以检查Licenses（许可证），例如[Sonatype Nexus IQ](https://www.sonatype.com/nexus/iqserver)、[Sourceclear](https://www.sourceclear.com/)、[Snyk](https://snyk.io/)或[Blackduck](https://www.blackducksoftware.com/)。

> 注意：如果对第三方库（Libraries）使用的许可模式的影响有疑问，请咨询法律专家。

当库包含应用程序 IP 需要开源的Licenses（许可证）时，检查是否有可用于提供类似功能的库的替代方案。

注意：如果是混合应用程序，请检查使用的构建工具：它们中的大多数都有Licenses（许可证）枚举插件来查找正在使用的Licenses（许可证）。

当源不可用时，可以反编译应用程序并检查 JAR 文件。当正确应用 Dexguard 或[ProGuard](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#proguard)时，有关库的版本信息通常会消失。否则，您仍然可以在给定库的 Java 文件的注释中经常找到它。MobSF 等工具可以帮助分析应用程序中可能包含的库。如果您可以通过注释或通过某些版本中使用的特定方法检索库的版本，则可以查找它们以获取手动使用的Licenses（许可证）。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_4)

本节的动态分析包括验证是否遵守了Licenses（许可证）的版权。这通常意味着应用程序应该有一个`about`或`EULA`部分，其中根据第三方库的许可要求注明版权声明。

## 测试异常处理（MSTG-CODE-6 和 MSTG-CODE-7）[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#testing-exception-handling-mstg-code-6-and-mstg-code-7)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_5)

当应用程序进入异常或错误状态时，就会出现异常。Java 和 C++ 都可能抛出异常。测试异常处理是为了确保应用程序将处理异常并转换到安全状态，而不会通过 UI 或应用程序的日志记录机制暴露敏感信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_5)

查看源代码以了解应用程序并确定它如何处理不同类型的错误（IPC 通信、远程服务调用等）。以下是在此阶段需要检查的一些示例：

- 确保应用程序使用设计良好且统一的方案来[处理异常](https://wiki.sei.cmu.edu/confluence/pages/viewpage.action?pageId=88487665)。
- 通过创建适当的空检查、绑定检查等来规划标准`RuntimeException`s（例如`NullPointerException`, `IndexOutOfBoundsException`, `ActivityNotFoundException`, `CancellationException`, ）。可以在 Android 开发人员文档中找到可用子类`SQLException`的[概述。`RuntimeException`](https://developer.android.com/reference/java/lang/RuntimeException.html)`RuntimeException`应该有意抛出一个子对象，并且这个意图应该由调用方法处理。
- 确保对于每个非Runtime(运行时)`Throwable`都有一个正确的 catch 处理程序，它最终正确地处理实际的异常。
- 抛出异常时，确保应用程序具有集中处理程序来处理导致类似行为的异常。这可以是静态类。对于特定于方法的异常，提供特定的 catch 块。
- 确保应用程序在处理其 UI 或日志语句中的异常时不会暴露敏感信息。确保异常仍然足够详细以向用户解释问题。
- 确保在`finally`块执行期间始终擦除高风险应用程序处理的所有机密信息。

```
byte[] secret;
try{
    //use secret
} catch (SPECIFICEXCEPTIONCLASS | SPECIFICEXCEPTIONCLASS2 e) {
    // handle any issues
} finally {
    //clean the secret.
}
```

为未捕获的异常添加通用异常处理程序是在即将发生崩溃时重置应用程序状态的最佳实践：

```
public class MemoryCleanerOnCrash implements Thread.UncaughtExceptionHandler {

    private static final MemoryCleanerOnCrash S_INSTANCE = new MemoryCleanerOnCrash();
    private final List<Thread.UncaughtExceptionHandler> mHandlers = new ArrayList<>();

    //initialize the handler and set it as the default exception handler
    public static void init() {
        S_INSTANCE.mHandlers.add(Thread.getDefaultUncaughtExceptionHandler());
        Thread.setDefaultUncaughtExceptionHandler(S_INSTANCE);
    }

     //make sure that you can still add exception handlers on top of it (required for ACRA for instance)
    public void subscribeCrashHandler(Thread.UncaughtExceptionHandler handler) {
        mHandlers.add(handler);
    }

    @Override
    public void uncaughtException(Thread thread, Throwable ex) {

            //handle the cleanup here
            //....
            //and then show a message to the user if possible given the context

        for (Thread.UncaughtExceptionHandler handler : mHandlers) {
            handler.uncaughtException(thread, ex);
        }
    }
}
```

现在必须在您的自定义`Application`类中调用处理程序的初始化程序（例如，扩展的类`Application`）：

```
@Override
protected void attachBaseContext(Context base) {
    super.attachBaseContext(base);
    MemoryCleanerOnCrash.init();
}
```

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_5)

有几种方法可以进行动态分析：

- 使用 Xposed Hook方法并使用意外值调用它们或使用意外值（例如，空值）覆盖现有变量。
- 在 Android 应用程序的 UI 字段中键入意外值。
- 使用其意图、公共提供者和意外值与应用程序交互。
- 篡改网络通信和/或应用程序存储的文件。

应用程序永远不会崩溃；它应该

- 从错误中恢复或转换到可以通知用户无法继续的状态，
- 如有必要，告诉用户采取适当的行动（消息不应泄露敏感信息。），
- 不在应用程序使用的日志记录机制中提供任何信息。

## 内存损坏错误 (MSTG-CODE-8)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#memory-corruption-bugs-mstg-code-8)

Android 应用程序通常在 VM 上运行，其中大部分内存损坏问题都已得到解决。这并不意味着没有内存损坏错误。以[CVE-2018-9522](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2018-9522)为例，它与使用 Parcels 的序列化问题有关。接下来，在Native代码中，我们仍然会看到与我们在一般内存损坏部分中解释的相同的问题。最后，我们看到了支持服务中的内存错误，例如[BlackHat](https://www.blackhat.com/docs/us-15/materials/us-15-Drake-Stagefright-Scary-Code-In-The-Heart-Of-Android.pdf)中展示的 Stagefright 攻击。

内存泄漏通常也是一个问题。例如，当对`Context`对象的引用被传递给非`Activity`类时，或者当您将对类的引用传递`Activity`给您的帮助类时，就会发生这种情况。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_6)

有多种物品可供寻找：

- 有本地代码部分吗？如果是这样：检查一般内存损坏部分中的给定问题。给定 JNI 包装器、.CPP/.H/.C 文件、NDK 或其他原生框架，可以轻松发现原生代码。
- 有Java代码或者Kotlin代码吗？查找序列化/反序列化问题，如[Android 反序列化漏洞简史](https://securitylab.github.com/research/android-deserialization-vulnerabilities)中所述。

请注意，Java/Kotlin 代码中也可能存在内存泄漏。查找各种项目，例如：未注册的 BroadcastReceivers、对`Activity`或`View`类的静态引用、引用 的单例类`Context`、内部类引用、匿名类引用、AsyncTask 引用、处理程序引用、错误的线程、TimerTask 引用。更多详情，请查看：

- [在 Android 中避免内存泄漏的 9 种方法](https://android.jlelse.eu/9-ways-to-avoid-memory-leaks-in-android-b6d81648e35e)
- [Android 中的内存泄漏模式](https://android.jlelse.eu/memory-leak-patterns-in-android-4741a7fcb570)。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#dynamic-analysis_6)

需要采取各种步骤：

- 对于Native代码：使用 Valgrind 或 Mempatrol 分析代码的内存使用情况和内存调用。
- 如果是 Java/Kotlin 代码，请尝试重新编译应用程序并将其与[Squares leak canary](https://github.com/square/leakcanary)一起使用。
- [使用Android Studio 中的 Memory Profiler](https://developer.android.com/studio/profile/memory-profiler)检查是否有泄漏。
- 使用[Android Java Deserialization Vulnerability Tester](https://github.com/modzero/modjoda)检查序列化漏洞。

## 确保激活了免费的安全功能 (MSTG-CODE-9)[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#make-sure-that-free-security-features-are-activated-mstg-code-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#overview_6)

用于检测[二进制保护机制](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#binary-protection-mechanisms)是否存在的测试在很大程度上取决于用于开发应用程序的语言。

一般来说，应该测试所有二进制文件，包括主要应用程序可执行文件以及所有库/依赖项。然而，在 Android 上，我们将专注于本地库，因为主要的可执行文件被认为是安全的，我们将在接下来看到。

Android 从应用程序 DEX 文件（例如 classes.dex）优化其 Dalvik 字节码并生成一个包含Native代码的新文件，通常具有 .odex、.oat 扩展名。这个[Android 编译的二进制文件](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#compiled-app-binary)使用[ELF 格式](https://refspecs.linuxfoundation.org/elf/gabi4+/contents.html)包装，这是 Linux 和 Android 用来打包汇编代码的格式。

该应用程序的[NDK 原生库](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#native-libraries)也[使用 ELF 格式](https://developer.android.com/ndk/guides/abis)。

- [**PIE（位置独立可执行文件）**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#position-independent-code)：
- 从 Android 7.0（API 级别 24）开始，主要可执行文件[默认启用PIC 编译。](https://source.android.com/devices/tech/dalvik/configure)
- [在 Android 5.0（API 级别 21）中，不再](https://source.android.com/security/enhancements/enhancements50)支持非 PIE 启用的Native库(NATIVE LIBRARIES)，从那时起，PIE[由链接器强制执行](https://cs.android.com/android/platform/superproject/+/master:bionic/linker/linker_main.cpp;l=430)。
- [**内存管理**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#memory-management)：
- 垃圾收集将只针对主要二进制文件运行，二进制文件本身无需检查任何内容。
- 垃圾收集不适用于 Android Native库(NATIVE LIBRARIES)。开发人员负责进行适当的[手动内存管理](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#manual-memory-management)。请参阅[“内存损坏错误 (MSTG-CODE-8)”](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#memory-corruption-bugs-mstg-code-8)。
- [**堆栈粉碎保护**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#stack-smashing-protection)：
- Android 应用程序被编译为 Dalvik 字节码，这被认为是内存安全的（至少用于缓解缓冲区溢出）。其他框架（例如 Flutter）不会使用堆栈金丝雀进行编译，因为它们的语言（在本例中为 Dart）会减轻缓冲区溢出。
- 必须为 Android Native库(NATIVE LIBRARIES)启用它，但可能很难完全确定它。
  - NDK 库应该启用它，因为编译器默认启用它。
  - 其他自定义 C/C++ 库可能未启用它。

学到更多：

- [Android可执行格式](https://lief-project.github.io/doc/latest/tutorials/10_android_formats.html)
- [Android Runtime(运行时) (ART)](https://source.android.com/devices/tech/dalvik/configure#how_art_works)
- [AndroidNDK](https://developer.android.com/ndk/guides)
- [NDK 开发人员的 Android 链接器更改](https://android.googlesource.com/platform/bionic/+/master/android-changes-for-ndk-developers.md)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_7)

测试应用原生库以确定它们是否启用了 PIE 和堆栈粉碎保护。

您可以使用[radare2 的 rabin2](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#radare2)来获取二进制信息。我们将使用[UnCrackable App for Android Level 4](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l4) v1.0 APK 作为示例。

所有Native库(NATIVE LIBRARIES)都必须具有`canary`并且`pic`都设置为`true`.

情况就是这样`libnative-lib.so`：

```
rabin2 -I lib/x86_64/libnative-lib.so | grep -E "canary|pic"
canary   true
pic      true
```

但不是为了`libtool-checker.so`：

```
rabin2 -I lib/x86_64/libtool-checker.so | grep -E "canary|pic"
canary   false
pic      true
```

在此示例中，`libtool-checker.so`必须使用堆栈粉碎保护支持重新编译。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#owasp-masvs)

- MSTG-CODE-1：“该应用程序已签名并使用有效证书进行配置，其中的私钥受到适当保护。”
- MSTG-CODE-2：“该应用程序已在发布模式下构建，具有适用于发布构建的设置（例如不可调试）。”
- MSTG-CODE-3：“调试符号已从Native二进制文件中删除。”
- MSTG-CODE-4：“调试代码和开发人员帮助代码（例如测试代码、后门、隐藏设置）已被删除。该应用程序不会记录详细错误或调试消息。”
- MSTG-CODE-5：“移动应用程序使用的所有第三方组件，例如库和框架，都被识别并检查已知漏洞。”
- MSTG-CODE-6：“应用程序捕获并处理可能的异常。”
- MSTG-CODE-7：“安全控制中的错误处理逻辑默认拒绝访问。”
- MSTG-CODE-8：“在非托管代码中，安全地分配、释放和使用内存。”
- MSTG-CODE-9：“工具链提供的免费安全功能已激活，例如字节码缩小、堆栈保护、PIE 支持和自动引用计数。”

### 内存分析参考[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#memory-analysis-references)

- Android 反序列化漏洞简史 - https://securitylab.github.com/research/android-deserialization-vulnerabilities
- 在 Android 中避免内存泄漏的 9 种方法 - https://android.jlelse.eu/9-ways-to-avoid-memory-leaks-in-android-b6d81648e35e
- Android 中的内存泄漏模式 - https://android.jlelse.eu/memory-leak-patterns-in-android-4741a7fcb570

### Android文档[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-documentation)

- 带密钥轮换的 APK 签名方案 - https://developer.android.com/about/versions/pie/android-9.0#apk-key-rotation
