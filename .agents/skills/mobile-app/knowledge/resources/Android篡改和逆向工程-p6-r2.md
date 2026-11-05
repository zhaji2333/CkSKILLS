# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 6 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p6.md`。

幸运的是，Android 的“开发人员选项”包含有用的“等待调试器”功能，它允许您自动暂停正在启动的应用程序，直到 JDWP 调试器连接。使用此功能，您可以在检测机制运行之前连接调试器，并跟踪、调试和停用该机制。这确实是一种不公平的优势，但另一方面，逆向工程师从不公平竞争！

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/debugger_detection.png)

在开发人员选项中，选择`Uncrackable1`调试应用程序并激活“等待调试器”开关。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/developer-options.png)

注意：即使在 中`ro.debuggable`设置为“1” `default.prop`，应用也不会出现在“调试应用”列表中，除非在 Android 清单中将`android:debuggable`标志设置为`"true"`。

#### 修补 React Native 应用程序[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-react-native-applications)

如果使用[React Native](https://facebook.github.io/react-native)框架进行开发，则主要应用代码位于文件`assets/index.android.bundle`. 此文件包含 JavaScript 代码。大多数情况下，此文件中的 JavaScript 代码会被缩小。通过使用工具[JStillery](https://mindedsecurity.github.io/jstillery)，可以重试文件的人类可读版本，从而允许代码分析。[应首选JStillery](https://github.com/mindedsecurity/jstillery/)的CLI 版本或本地服务器，而不是使用在线版本，否则会将源代码发送并披露给第三方。

可以使用以下方法来修补 JavaScript 文件：

1. `apktool`使用工具解压 APK 存档。
2. 将文件内容复制`assets/index.android.bundle`到一个临时文件中。
3. 用于`JStillery`美化和反混淆临时文件的内容。
4. 确定应在临时文件中修补代码的位置并实施更改。
5. 将*修补后的代码*放在一行中，然后将其复制到原始`assets/index.android.bundle`文件中。
6. 使用工具重新打包 APK 存档`apktool`并在将其安装到目标设备/模拟器之前对其进行签名。

#### 库注入[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#library-injection)

在上一节中，我们了解了如何修补应用程序代码以协助我们的分析，但这种方法有几个局限性。例如，您想记录通过网络发送的所有内容，而不必执行 MITM 攻击。为此，您必须修补所有可能的网络 API 调用，这在处理大型应用程序时很快就会变得不切实际。此外，每个应用程序的补丁都是唯一的这一事实也可以被认为是一个缺点，因为该代码不能轻易重用。

使用库注入，您可以开发可重用的库并将它们注入到不同的应用程序中，有效地使它们的行为有所不同，而无需修改它们的原始源代码。`LD_PRELOAD`这在 Windows（广泛用于修改和绕过游戏中的反作弊机制）、 Linux 和`DYLD_INSERT_LIBRARIES`macOS上被称为 DLL 注入。在 Android 和 iOS 上，一个常见的例子是当 Frida 所谓的[注入](https://frida.re/docs/modes/#injected)操作模式不合适时使用 Frida Gadget（即您无法在目标设备上运行 Frida 服务器）。在这种情况下，您可以使用您将在本节中学习的相同方法来[注入 Gadget库。](https://frida.re/docs/gadget/)

在许多情况下都需要库注入，例如：

- 执行进程内省（例如，列出类、跟踪方法调用、监视访问的文件、监视网络访问、获取直接内存访问）。
- 用您自己的实现支持或替换现有代码（例如，替换应提供随机数的函数）。
- 向现有应用程序引入新功能。
- 在您没有原始源代码的代码上调试和修复难以捉摸的Runtime(运行时)错误。
- 在非 root 设备上启用动态测试（例如使用 Frida）。

在本节中，我们将了解在 Android 上执行库注入的技术，主要包括修补应用程序代码（smali 或Native）或使用`LD_PRELOAD`操作系统加载程序本身提供的功能。

##### 修补应用程序的 SMALI 代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-the-applications-smali-code)

可以修补 Android 应用程序的反编译 smali 代码以引入对`System.loadLibrary`. 下面的 smali 补丁注入了一个名为 libinject.so 的库：

```
const-string v0, "inject"
invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
```

[理想情况下，您应该在应用程序生命周期](https://developer.android.com/guide/components/activities/activity-lifecycle)的早期插入上述代码，例如在`onCreate`方法中。重要的是要记住在`lib`APK 文件夹的相应架构文件夹（armeabi-v7a、arm64-v8a、x86）中添加库 libinject.so。最后，您需要在使用前重新签署应用程序。

这种技术的一个众所周知的用例是将 Frida 小工具加载到应用程序，特别是在非 root 设备上工作时（这[`objection patchapk`](https://github.com/sensepost/objection/wiki/Patching-Android-Applications)基本上是这样做的）。

##### 修补应用程序的Native库(NATIVE LIBRARIES)[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-applications-native-library)

出于各种性能和安全原因，许多 Android 应用程序除了使用 Java 代码外还使用Native代码。Native代码以 ELF 共享库的形式存在。ELF 可执行文件包含一个共享库（依赖项）列表，这些共享库链接到可执行文件以使其发挥最佳功能。可以修改此列表以插入要注入到进程中的附加库。

手动修改 ELF 文件结构以注入库可能很麻烦且容易出错。[但是，可以使用LIEF](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#LIEF)（库到仪器可执行格式）相对轻松地执行此任务。使用它只需要几行 Python 代码，如下所示：

```
import lief

libnative = lief.parse("libnative.so")
libnative.add_library("libinject.so") # Injection!
libnative.write("libnative.so")
```

在上面的示例中，libinject.so 库作为Native库(NATIVE LIBRARIES) (libnative.so) 的依赖项被注入，应用程序默认情况下已加载该库。可以使用这种方法将 Frida 小工具注入到应用程序中，如[LIEF 文档](https://lief.quarkslab.com/doc/latest/tutorials/09_frida_lief.html)中的详细说明。与上一节一样，重要的是要记住将库添加到`lib`APK 中的相应体系结构文件夹，最后重新签署应用程序。

##### 预加载符号[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#preloading-symbols)

上面我们研究了需要对应用程序代码进行某种修改的技术。还可以使用操作系统加载程序提供的功能将库注入到进程中。`LD_PRELOAD`在基于 Linux 的操作系统 Android 上，您可以通过设置环境变量来加载额外的库。

正如[ld.so 手册页](http://man7.org/linux/man-pages/man8/ld.so.8.html)所述，从 using 传递的库加载的符号`LD_PRELOAD`始终具有优先权，即加载程序在解析符号时首先搜索它们，从而有效地覆盖原始符号。此功能通常用于检查一些常用 libc 函数的输入参数，例如`fopen`、`read`、`write`、`strcmp`等，特别是在混淆程序中，在这些程序中理解它们的行为可能具有挑战性。因此，了解正在打开哪些文件或正在比较哪些字符串可能非常有价值。这里的关键思想是“函数包装”，这意味着您不能修补 libc 等系统调用`fopen`，但您可以覆盖（包装）它，包括自定义代码，例如，为您打印输入参数并仍然调用对`fopen`调用者透明的原始剩余部分。

在 Android 上，设置`LD_PRELOAD`与其他 Linux 发行版略有不同。如果您还记得“[平台概述](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#zygote)”部分，Android 中的每个应用程序都是从 Zygote 派生出来的，它在 Android 启动时很早就启动了。因此，`LD_PRELOAD`无法在 Zygote 上进行设置。作为此问题的解决方法，Android 支持`setprop`（设置属性）功能。下面您可以看到一个带有包名称的应用程序示例`com.foo.bar`（注意附加`wrap.`前缀）：

```
setprop wrap.com.foo.bar LD_PRELOAD=/data/local/tmp/libpreload.so
```

> 请注意，如果要预加载的库没有分配 SELinux 上下文，从 Android 5.0（API 级别 21）开始，您需要禁用 SELinux 才能`LD_PRELOAD`工作，这可能需要 root 权限。

### 动态仪表[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#dynamic-instrumentation)

#### 信息收集[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#information-gathering)

在本节中，我们将了解如何使用 Frida 获取有关正在运行的应用程序的信息。

##### 获取加载的类及其方法[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#getting-loaded-classes-and-their-methods)

您可以使用`Java`Frida CLI 中的命令来访问 Java Runtime(运行时)并从正在运行的应用程序中检索信息。请记住，与适用于 iOS 的 Frida 不同，在 Android 中，您需要将代码包装在一个`Java.perform`函数中。因此，使用 Frida 脚本更方便，例如获取加载的 Java 类列表及其相应的方法和字段，或者更复杂的信息收集或检测。下面列出了一个这样的脚本。[Github](https://github.com/frida/frida-java-bridge/issues/44)上提供了列出下面使用的类方法的脚本。

```
// Get list of loaded Java classes and methods

// Filename: java_class_listing.js

Java.perform(function() {
    Java.enumerateLoadedClasses({
        onMatch: function(className) {
            console.log(className);
            describeJavaClass(className);
        },
        onComplete: function() {}
    });
});

// Get the methods and fields
function describeJavaClass(className) {
  var jClass = Java.use(className);
  console.log(JSON.stringify({
    _name: className,
