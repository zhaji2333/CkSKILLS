# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 2 · part 1

> 分段 1/2。索引见 `Android代码质量和构建设置-p2.md`。

# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 2

> 分段 2/2。索引见 `Android代码质量和构建设置.md`。

## 承接

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

