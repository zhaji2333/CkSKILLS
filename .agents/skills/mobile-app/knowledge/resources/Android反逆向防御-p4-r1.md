# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 4 · part 1

> 分段 1/2。索引见 `Android反逆向防御-p4.md`。

# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 4

> 分段 4/5。索引见 `Android反逆向防御.md`。

## 承接

TelephonyManager.getNetworkOperator().substring(3)      260                     possibly emulator
TelephonyManager.getPhoneType()                         1                       possibly emulator
TelephonyManager.getSimCountryIso()                     us                      possibly emulator
TelephonyManager.getSimSerial Number()                  89014103211118510720    emulator
TelephonyManager.getSubscriberId()                      310260000000000         emulator
TelephonyManager.getVoiceMailNumber()                   15552175049             emulator
```

请记住，Xposed 或 Frida 等Hook框架可以Hook此 API 以提供虚假数据。

### 绕过模拟器检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-emulator-detection)

1. 修补模拟器检测功能。通过简单地用 NOP 指令覆盖相关的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed API 在 Java 和Native层上Hook文件系统 API。返回看起来无辜的值（最好从真实设备中获取）而不是明显的模拟器值。例如，您可以覆盖该`TelephonyManager.getDeviceID`方法以返回 IMEI 值。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_4)

在模拟器中安装并运行该应用程序。该应用程序应检测到它正在模拟器中执行，并终止或拒绝执行应受保护的功能。

绕过防御并回答以下问题：

- 通过静态和动态分析识别模拟器检测代码有多难？
- 是否可以轻松绕过检测机制（例如，通过Hook单个 API 函数）？
- 您是否需要编写自定义代码来禁用反仿真功能？你需要多少时间？
- 您如何评估绕过这些机制的难度？

## 测试Runtime(运行时)完整性检查 (MSTG-RESILIENCE-6)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-runtime-integrity-checks-mstg-resilience-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_5)

此类别中的控件验证应用程序内存空间的完整性，以保护应用程序免受Runtime(运行时)应用的内存补丁的影响。此类补丁包括对二进制代码、字节码、函数指针表和重要数据结构的不必要更改，以及加载到进程内存中的流氓代码。完整性可以通过以下方式验证：

1. 将内存的内容或内容的校验和与正确的值进行比较，
2. 在内存中搜索不需要的修改的签名。

与“检测逆向工程工具和框架”类别有一些重叠，事实上，当我们展示如何在进程内存中搜索与 Frida 相关的字符串时，我们展示了基于签名的方法。以下是各种完整性监控的更多示例。

#### Runtime(运行时)完整性检查示例[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#runtime-integrity-check-examples)

##### 检测对 JAVA Runtime(运行时)的篡改[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#detecting-tampering-with-the-java-runtime)

此检测代码来自[dead && end 博客](https://d3adend.org/blog/?p=589)。

```
try {
  throw new Exception();
}
catch(Exception e) {
  int zygoteInitCallCount = 0;
  for(StackTraceElement stackTraceElement : e.getStackTrace()) {
    if(stackTraceElement.getClassName().equals("com.android.internal.os.ZygoteInit")) {
      zygoteInitCallCount++;
      if(zygoteInitCallCount == 2) {
        Log.wtf("HookDetection", "Substrate is active on the device.");
      }
    }
    if(stackTraceElement.getClassName().equals("com.saurik.substrate.MS$2") &&
        stackTraceElement.getMethodName().equals("invoked")) {
      Log.wtf("HookDetection", "A method on the stack trace has been hooked using Substrate.");
    }
    if(stackTraceElement.getClassName().equals("de.robv.android.xposed.XposedBridge") &&
        stackTraceElement.getMethodName().equals("main")) {
      Log.wtf("HookDetection", "Xposed is active on the device.");
    }
    if(stackTraceElement.getClassName().equals("de.robv.android.xposed.XposedBridge") &&
        stackTraceElement.getMethodName().equals("handleHookedMethod")) {
      Log.wtf("HookDetection", "A method on the stack trace has been hooked using Xposed.");
    }

  }
}
```

##### 检测NativeHook[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#detecting-native-hooks)

通过使用 ELF 二进制文件，可以通过覆盖内存中的函数指针（例如，全局偏移表或 PLT Hook）或修补部分函数代码本身（内联Hook）来安装Native函数Hook。检查各个内存区域的完整性是检测这种Hook的一种方法。

全局偏移表 (GOT) 用于解析库函数。在Runtime(运行时)，动态链接器用全局符号的绝对地址修补这个表。*GOT 钩子*覆盖存储的函数地址并将合法的函数调用重定向到对手控制的代码。这种类型的Hook可以通过枚举进程内存映射并验证每个 GOT 入口指向合法加载的库来检测。

与 GNU 相比`ld`，它仅在第一次需要符号地址时才解析符号地址（惰性绑定），Android 链接器解析所有外部函数并在加载库后立即写入相应的 GOT 条目（立即绑定）。因此，您可以期望所有 GOT 条目在Runtime(运行时)都指向其各自库的代码段中的有效内存位置。GOT hook 检测方法通常是遍历 GOT 并验证这一点。

*内联Hook*通过覆盖函数代码开头或结尾的一些指令来工作。在Runtime(运行时)，这个所谓的蹦床将执行重定向到注入的代码。您可以通过检查库函数的序言和结尾是否有可疑指令来检测内联Hook，例如远跳转到库外的位置。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_5)

确保禁用所有基于文件的逆向工程工具检测。然后，使用Xposed、Frida、Substrate注入代码，并尝试安装native hooks和Java method hooks。该应用程序应检测其内存中的“恶意”代码并做出相应响应。

使用以下技术绕过检查：

1. 修补完整性检查。通过使用 NOP 指令覆盖相应的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed Hook用于检测的 API 并返回假值。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

## 测试混淆 (MSTG-RESILIENCE-9)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-obfuscation-mstg-resilience-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_6)

[“移动应用程序篡改和逆向工程”](https://mas.owasp.org/MASTG/General/0x04c-Tampering-and-Reverse-Engineering/#obfuscation)一章介绍了几种众所周知的混淆技术，通常可以在移动应用程序中使用。

Android 应用程序可以使用不同的工具实施其中一些混淆技术。例如，[ProGuard](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#proguard)提供了一种简单的方法来缩小和混淆代码，并从 Android Java 应用程序的字节码中去除不需要的调试信息。它用无意义的字符串替换标识符，例如类名、方法名和变量名。这是一种布局混淆，不会影响程序的性能。

> 反编译 Java 类是微不足道的，因此建议始终对生产字节码应用一些基本的混淆。

详细了解 Android 混淆技术：

- Gautam Arvind[的“Android Native代码的安全加固”](https://darvincitech.wordpress.com/2020/01/07/security-hardening-of-android-native-code/)
- Eduardo Novella[的“APKiD：AppShielding 产品的快速识别”](https://github.com/enovella/cve-bio-enovella/blob/master/slides/APKiD-NowSecure-Connect19-enovella.pdf)
- [“原生 Android 应用程序的挑战：混淆和漏洞”](https://www.theses.fr/2020REN1S047.pdf)，作者 Pierre Graux

#### 使用混淆器[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-proguard)

开发人员使用 build.gradle 文件来启用混淆。`minifyEnabled`在下面的示例中，您可以看到`proguardFiles`已设置。创建异常以保护某些类免受混淆（使用`-keepclassmembers`和`-keep class`）是很常见的。因此，审核 ProGuard 配置文件以查看哪些类被豁免很重要。该方法从文件夹中`getDefaultProguardFile('proguard-android.txt')`获取默认的 ProGuard 设置。`<Android SDK>/tools/proguard/`

有关如何缩小、混淆和优化您的应用程序的更多信息，请参阅[Android 开发人员文档](https://developer.android.com/studio/build/shrink-code)。

> 当您使用 Android Studio 3.4 或 Android Gradle 插件 3.4.0 或更高版本构建项目时，该插件不再使用 ProGuard 来执行编译时代码优化。相反，该插件使用 R8 编译器。R8 适用于您现有的所有 ProGuard 规则文件，因此更新 Android Gradle 插件以使用 R8 不需要您更改现有规则。

R8 是来自 Google 的新代码收缩器，在 Android Studio 3.3 beta 中引入。默认情况下，R8 会删除对调试有用的属性，包括行号、源文件名和变量名。R8 是一个免费的 Java 类文件收缩器、优化器、混淆器和预验证器，并且比 ProGuard 更快，另请参阅[Android 开发人员博客文章了解更多详细信息](https://android-developers.googleblog.com/2018/11/r8-new-code-shrinker-from-google-is.html)。它与 Android 的 SDK 工具一起提供。要为发布版本激活收缩，请将以下内容添加到 build.gradle：

```
android {
    buildTypes {
        release {
            // Enables code shrinking, obfuscation, and optimization for only
            // your project's release build type.
            minifyEnabled true

            // Includes the default ProGuard rules files that are packaged with
            // the Android Gradle plugin. To learn more, go to the section about
            // R8 configuration files.
            proguardFiles getDefaultProguardFile(
                    'proguard-android-optimize.txt'),
                    'proguard-rules.pro'
        }
    }
    ...
}
```

