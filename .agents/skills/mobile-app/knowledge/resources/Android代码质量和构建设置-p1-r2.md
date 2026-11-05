# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 1 · part 2

> 分段 2/2。索引见 `Android代码质量和构建设置-p1.md`。

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

