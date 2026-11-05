# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 1 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p1.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 1

> 分段 1/10。索引见 `Android篡改和逆向工程.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering)

Android 的开放性使其成为逆向工程师的有利环境。在下一章中，我们将把 Android 逆向和特定于操作系统的工具视为进程的一些特性。

Android 为逆向工程师提供了 iOS 所不具备的巨大优势。由于 Android 是开源的，您可以在 Android 开源项目 (AOSP) 中研究其源代码，并以任何您想要的方式修改操作系统及其标准工具。即使在标准的零售设备上，也可以在不跳过许多步骤的情况下执行诸如激活开发者模式和侧载应用程序之类的操作。从 SDK 附带的强大工具到范围广泛的可用逆向工程工具，有很多细节可以让您的生活更轻松。

但是，也存在一些特定于 Android 的挑战。例如，您需要同时处理 Java 字节码和Native代码。Java Native接口 (JNI) 有时会被故意用于混淆逆向工程师（公平地说，使用 JNI 有正当理由，例如提高性能或支持遗留代码）。开发人员有时会使用Native层来“隐藏”数据和功能，并且他们可能会构建他们的应用程序，以便执行经常在两层之间跳转。

您至少需要了解基于 Java 的 Android 环境以及 Android 所基于的 Linux 操作系统和内核。您还需要合适的工具集来处理运行在 Java 虚拟机上的字节码和Native代码。

请注意，我们将使用[适用于 Android 的 OWASP UnCrackable 应用程序](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-crackmes)作为示例，在以下部分中演示各种逆向工程技术，因此请期待部分和全部剧透。我们鼓励您在继续阅读之前亲自尝试挑战！

## 逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reverse-engineering)

逆向工程是将应用程序拆开以了解其工作原理的过程。您可以通过检查已编译的应用程序（静态分析）、在Runtime(运行时)观察应用程序（动态分析）或两者的组合来做到这一点。

### 反汇编和反编译[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#disassembling-and-decompiling)

在Android应用程序安全测试中，如果应用程序完全基于Java并且没有任何本地代码（C/C++代码），逆向工程过程相对容易并且恢复（反编译）几乎所有的源代码。在这些情况下，黑盒测试（可以访问编译后的二进制文件，但不能访问原始源代码）可以非常接近白盒测试。

然而，如果代码被有意混淆（或应用了一些破坏工具的反编译技巧），逆向工程过程可能非常耗时且效率低下。这也适用于包含Native代码的应用程序。它们仍然可以进行逆向工程，但该过程不是自动化的，并且需要了解低级细节。

#### 反编译 Java 代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#decompiling-java-code)

**Java反汇编代码（smali）：**

如果您想检查应用程序的 smali 代码（而不是 Java），您可以[在 Android Studio 中](https://developer.android.com/studio/debug/apk-debugger)通过单击“欢迎屏幕”中的**配置文件或调试 APK**打开您的 APK （即使您不打算调试它，您也可以使用查看smali代码）。

或者，您可以使用[apktool](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apktool)直接从 APK 存档中提取和反汇编资源，并将 Java 字节码反汇编为 smali。apktool 允许您重新组装包，这对于为应用程序打[补丁](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-repackaging-and-re-signing)或对 Android Manifest 等应用更改很有用。

**Java反编译代码：**

如果您想在 GUI 上直接查看 Java 源代码，只需使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)或[Bytecode Viewer](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#bytecode-viewer)打开您的 APK 。

Android 反编译器更进一步，尝试将 Android 字节码转换回 Java 源代码，使其更易于阅读。幸运的是，Java 反编译器通常可以很好地处理 Android 字节码。上面提到的工具嵌入，有时甚至结合流行的免费反编译器，例如：

- [JD](https://java-decompiler.github.io/)
- [JAD](http://www.javadecompilers.com/jad)
- [jadx](https://github.com/skylot/jadx)
- [Procyon](https://github.com/mstrobel/procyon)
- [CFR](https://www.benf.org/other/cfr/)

或者，您可以使用Visual Studio Code的[APKLab扩展或在您的 APK 上运行](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apklab)[apkx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apkx)，或使用从以前的工具导出的文件在您首选的 IDE 上打开反向源代码。

在下面的示例中，我们将使用[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)。首先，让我们在设备或模拟器上安装应用程序并运行它以查看 crackme 是关于什么的。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/crackme-1.png)

看来我们要找到某种密码了！

我们正在寻找存储在应用程序内部某处的秘密字符串，因此下一步是查看内部。首先，解压缩 APK 文件 ( `unzip UnCrackable-Level1.apk -d UnCrackable-Level1`) 并查看内容。在标准设置中，所有 Java 字节码和应用程序数据都在`classes.dex`应用程序根目录 ( `UnCrackable-Level1/`) 的文件中。此文件符合 Dalvik 可执行格式 (DEX)，这是一种特定于 Android 的 Java 程序打包方式。大多数 Java 反编译器将普通类文件或 JAR 作为输入，因此您需要先将 classes.dex 文件转换为 JAR。您可以使用`dex2jar`或执行此操作`enjarify`。

一旦有了 JAR 文件，就可以使用任何免费的反编译器来生成 Java 代码。在这个例子中，我们将使用[CFR 反编译器](https://www.benf.org/other/cfr/)。CFR 版本可在作者的网站上找到。CFR 是在 MIT 许可下发布的，因此您可以自由使用它，即使它的源代码不可用。

运行 CFR 的最简单方法是通过[apkx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apkx)，它还打包`dex2jar`并自动执行提取、转换和反编译。在 APK 上运行它，你应该在目录中找到反编译源`Uncrackable-Level1/src`。要查看源代码，一个简单的文本编辑器（最好带有语法高亮显示）就可以了，但是将代码加载到 Java IDE 中会使导航更容易。让我们将代码导入 IntelliJ，它也提供了设备上的调试功能。

打开 IntelliJ 并在“新建项目”对话框的左侧选项卡中选择“Android”作为项目类型。输入“Uncrackable1”作为应用程序名称，输入“vantagepoint.sg”作为公司名称。这导致包名称“sg.vantagepoint.uncrackable1”，与原始包名称匹配。如果您想稍后将调试器附加到正在运行的应用程序，使用匹配的包名称很重要，因为 IntelliJ 使用包名称来识别正确的进程。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/intellij_new_project.jpg)

在下一个对话框中，选择任何 API 编号；您实际上并不想编译该项目，因此数字无关紧要。单击“下一步”并选择“不添加活动”，然后单击“完成”。

创建项目后，展开左侧的“1：项目”视图并导航到文件夹`app/src/main/java`。右键单击并删除 IntelliJ 创建的默认包“sg.vantagepoint.uncrackable1”。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/delete_package.jpg)

现在，`Uncrackable-Level1/src`在文件浏览器中打开目录并将`sg`目录拖到 IntelliJ 项目视图中现在空的`Java`文件夹中（按住“alt”键复制文件夹而不是移动它）。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/drag_code.jpg)

您最终会得到一个类似于构建应用程序的原始 Android Studio 项目的结构。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/final_structure.jpg)

请参阅下面的“[查看反编译的 Java 代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)”部分，了解在检查反编译的 Java 代码时如何进行。

#### 反汇编Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#disassembling-native-code)

Dalvik 和 ART 都支持 Java Native接口 (JNI)，它定义了 Java 代码与用 C/C++ 编写的Native代码交互的方式。与其他基于 Linux 的操作系统一样，Native代码被打包（编译）到 ELF 动态库 (*.so) 中，Android 应用程序在Runtime(运行时)通过该`System.load`方法加载。但是，Android 二进制文件不是依赖于广泛使用的 C 库（例如 glibc），而是针对名为[Bionic](https://github.com/android/platform_bionic)的自定义 libc 构建的。Bionic 添加了对重要的 Android 特定服务的支持，例如系统属性和日志记录，但它并不完全与 POSIX 兼容。

在逆向包含Native代码的 Android 应用程序时，我们需要了解一些与 Java 和Native代码之间的 JNI 桥相关的数据结构。从逆向的角度来看，我们需要了解两个关键的数据结构：`JavaVM`和`JNIEnv`。它们都是指向函数表指针的指针：

- `JavaVM`提供一个接口来调用用于创建和销毁 JavaVM 的函数。Android 只允许`JavaVM`每个进程一个，并且与我们的逆向目的无关。
- `JNIEnv`提供对大多数 JNI 函数的访问，这些函数可以通过`JNIEnv`指针以固定偏移量访问。这个`JNIEnv`指针是传递给每个 JNI 函数的第一个参数。我们将在本章后面的例子中再次讨论这个概念。

值得强调的是，分析反汇编的Native代码比反汇编的 Java 代码更具挑战性。在 Android 应用程序中逆向Native代码时，我们将需要一个反汇编程序。

在下一个示例中，我们将从 OWASP MASTG 存储库中反转 HelloWorld-JNI.apk。在模拟器或 Android 设备中安装和运行它是可选的。

```
wget https://github.com/OWASP/owasp-mastg/raw/master/Samples/Android/01_HelloWorld-JNI/HelloWord-JNI.apk
```

> 这个应用程序并不十分引人注目，它所做的只是显示一个带有文本“Hello from C++”的标签。这是Android在新建一个支持C/C++的项目时默认生成的app，足以说明JNI调用的基本原理。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/helloworld.png)

