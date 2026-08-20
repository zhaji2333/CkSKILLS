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

反编译 APK 与`apkx`.

```
$ apkx HelloWord-JNI.apk
Extracting HelloWord-JNI.apk to HelloWord-JNI
Converting: classes.dex -> classes.jar (dex2jar)
dex2jar HelloWord-JNI/classes.dex -> HelloWord-JNI/classes.jar
Decompiling to HelloWord-JNI/src (cfr)
```

这会将源代码提取到`HelloWord-JNI/src`目录中。主要活动在文件中找到`HelloWord-JNI/src/sg/vantagepoint/helloworldjni/MainActivity.java`。“Hello World”文本视图在`onCreate`方法中填充：

```
public class MainActivity
extends AppCompatActivity {
    static {
        System.loadLibrary("native-lib");
    }

    @Override
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        this.setContentView(2130968603);
        ((TextView)this.findViewById(2131427422)).setText((CharSequence)this. \
        stringFromJNI());
    }

    public native String stringFromJNI();
}
```

注意`public native String stringFromJNI`底部的声明。关键字“native”告诉 Java 编译器这个方法是用本地语言实现的。相应的函数在Runtime(运行时)解析，但前提是加载了导出具有预期签名的全局符号的Native库(NATIVE LIBRARIES)（签名包括包名、类名和方法名）。在此示例中，此要求由以下 C 或 C++ 函数满足：

```
JNIEXPORT jstring JNICALL Java_sg_vantagepoint_helloworld_MainActivity_stringFromJNI(JNIEnv *env, jobject)
```

那么这个函数的原生实现在哪里呢？如果您查看解压缩的 APK 存档的“lib”目录，您会看到几个子目录（每个受支持的处理器架构一个），每个子目录都包含一个版本的Native库(NATIVE LIBRARIES)，在本例中为`libnative-lib.so`. 调用时`System.loadLibrary`，加载器会根据运行应用程序的设备选择正确的版本。在继续之前，请注意传递给当前 JNI 函数的第一个参数。它与`JNIEnv`本节前面讨论的数据结构相同。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/archs.jpg)

按照上面提到的命名约定，您可以期望库导出一个名为`Java_sg_vantagepoint_helloworld_MainActivity_stringFromJNI`. 在 Linux 系统上，您可以使用`readelf`（包含在 GNU binutils 中）或检索符号列表`nm`。在 macOS 上使用该`greadelf`工具执行此操作，您可以通过 Macports 或 Homebrew 安装该工具。以下示例使用`greadelf`：

```
$ greadelf -W -s libnative-lib.so | grep Java
     3: 00004e49   112 FUNC    GLOBAL DEFAULT   11 Java_sg_vantagepoint_helloworld_MainActivity_stringFromJNI
```

您还可以使用 radare2 的 rabin2 看到这一点：

```
$ rabin2 -s HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so | grep -i Java
003 0x00000e78 0x00000e78 GLOBAL   FUNC   16 Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI
```

`stringFromJNI`这是调用Native方法时最终执行的Native函数。

要反汇编代码，您可以加载`libnative-lib.so`到任何理解 ELF 二进制文件的反汇编程序（即任何反汇编程序）中。如果应用程序附带不同架构的二进制文件，理论上您可以选择您最熟悉的架构，只要它与反汇编程序兼容即可。每个版本都从相同的源代码编译并实现相同的功能。但是，如果您计划稍后在实时设备上调试该库，通常明智的做法是选择 ARM 版本。

为了同时支持较旧和较新的 ARM 处理器，Android 应用附带了针对不同应用程序二进制接口 (ABI) 版本编译的多个 ARM 版本。ABI 定义了应用程序的机器代码在Runtime(运行时)应该如何与系统交互。支持以下 ABI：

- armeabi：ABI 适用于至少支持 ARMv5TE 指令集的基于 ARM 的 CPU。
- armeabi-v7a：此 ABI 扩展了 armeabi 以包含多个 CPU 指令集扩展。
- arm64-v8a：用于支持 AArch64（新的 64 位 ARM 架构）的基于 ARMv8 的 CPU 的 ABI。

大多数反汇编程序都可以处理这些架构中的任何一种。`HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so`下面，我们将在 radare2 和 IDA Pro 中查看 armeabi-v7a 版本（位于）。请参阅下面的“[检查反汇编的Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)”部分，了解在检查反汇编的Native代码时如何进行。

##### RADARE2[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#radare2)

[要在radare2](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#radare2)中打开文件，您只需运行`r2 -A HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so`. “ [Android 基本安全测试](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/)”一章已经介绍了radare2。请记住，您可以在加载二进制文件后立即使用标志`-A`运行`aaa`命令，以便分析所有引用的代码。

```
$ r2 -A HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so

[x] Analyze all flags starting with sym. and entry0 (aa)
[x] Analyze function calls (aac)
[x] Analyze len bytes of instructions for references (aar)
[x] Check for objc references
[x] Check for vtables
[x] Finding xrefs in noncode section with anal.in=io.maps
[x] Analyze value pointers (aav)
[x] Value from 0x00000000 to 0x00001dcf (aav)
[x] 0x00000000-0x00001dcf in 0x0-0x1dcf (aav)
[x] Emulate code to find computed references (aae)
[x] Type matching analysis for all functions (aaft)
[x] Use -AA or aaaa to perform additional experimental analysis.
 -- Print the contents of the current block with the 'p' command
[0x00000e3c]>
```

请注意，对于更大的二进制文件，直接从标志开始`-A`可能非常耗时而且没有必要。根据您的目的，您可以在没有此选项的情况下打开二进制文件，然后应用不太复杂的分析`aa`或更具体的分析类型，例如`aa`（所有函数的基本分析）或`aac`（分析函数调用）中提供的分析。请记住始终键入`?`以获取帮助或将其附加到命令以查看更多命令或选项。例如，如果您输入，`aa?`您将获得完整的分析命令列表。

```
[0x00001760]> aa?
Usage: aa[0*?]   # see also 'af' and 'afna'
| aa                  alias for 'af@@ sym.*;af@entry0;afva'
| aaa[?]              autoname functions after aa (see afna)
| aab                 abb across bin.sections.rx
| aac [len]           analyze function calls (af @@ `pi len~call[1]`)
| aac* [len]          flag function calls without performing a complete analysis
| aad [len]           analyze data references to code
| aae [len] ([addr])  analyze references with ESIL (optionally to address)
| aaf[e|t]            analyze all functions (e anal.hasnext=1;afr @@c:isq) (aafe=aef@@f)
| aaF [sym*]          set anal.in=block for all the spaces between flags matching glob
| aaFa [sym*]         same as aaF but uses af/a2f instead of af+/afb+ (slower but more accurate)
| aai[j]              show info of all analysis parameters
| aan                 autoname functions that either start with fcn.* or sym.func.*
| aang                find function and symbol names from golang binaries
| aao                 analyze all objc references
| aap                 find and analyze function preludes
| aar[?] [len]        analyze len bytes of instructions for references
| aas [len]           analyze symbols (af @@= `isq~[0]`)
| aaS                 analyze all flags starting with sym. (af @@ sym.*)
| aat [len]           analyze all consecutive functions in section
| aaT [len]           analyze code after trap-sleds
| aau [len]           list mem areas (larger than len bytes) not covered by functions
| aav [sat]           find values referencing a specific section or map
```

关于 radare2 与其他反汇编程序（如 IDA Pro）的对比，有一点值得注意。以下引用自radare2 博客 ( [https://radareorg.github.io/blog/ ) 的这篇](https://radareorg.github.io/blog/)[文章](https://radareorg.github.io/blog/posts/analysis-by-default/)提供了一个很好的总结。

> 代码分析不是一项快速操作，甚至无法预测或需要线性时间来处理。与默认情况下仅加载标头和字符串信息相比，这使得启动时间非常繁重。
>
> 习惯于[IDA](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#ida-pro-commercial-tool)或[Hopper](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#hopper-commercial-tool)的人只是加载二进制文件，出去泡杯咖啡，然后在分析完成后，他们开始进行手动分析以了解程序在做什么。确实，这些工具在后台执行分析，并且 GUI 未被阻止。但这会占用大量 CPU 时间，而且 r2 的目标是在更多平台上运行，而不仅仅是高端台式计算机。

这就是说，请参阅“[审查反汇编Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)”部分以了解更多关于 radare2 如何帮助我们更快地执行逆向任务的信息。例如，获取特定函数的反汇编是一项可以在一个命令中执行的微不足道的任务。

##### IDA专业版[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#ida-pro)

如果您拥有[IDA Pro](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#ida-pro-commercial-tool)Licenses（许可证），请打开文件，然后在“加载新文件”对话框中，选择“ELF for ARM（共享对象）”作为文件类型（IDA 应该会自动检测到这一点），然后选择“ARM Little-Endian” " 作为处理器类型。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/IDA_open_file.jpg)

> 不幸的是，IDA Pro 的免费版本不支持 ARM 处理器类型。

## 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#static-analysis)

对于白盒源代码测试，您需要一个类似于开发人员设置的设置，包括一个包含 Android SDK 和 IDE 的测试环境。建议访问物理设备或模拟器（用于调试应用程序）。

在**黑盒测试**期间，您将无法访问源代码的原始形式。您通常会有[Android APK 格式](https://en.wikipedia.org/wiki/Android_application_package)的应用程序包，可以将其安装在 Android 设备上或按照“反汇编和反编译”部分中的说明进行逆向工程。

### 基本信息收集[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#basic-information-gathering)

如前几节所述，Android 应用程序可以同时包含 Java/Kotlin 字节码和Native代码。在本节中，我们将学习一些使用静态分析收集基本信息的方法和工具。

#### 检索字符串[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#retrieving-strings)

在执行任何类型的二进制分析时，字符串可以被视为最有价值的起点之一，因为它们提供了上下文。例如，类似“数据加密失败”的错误日志字符串。给我们一个提示，相邻的代码可能负责执行某种加密操作。

##### JAVA 和 KOTLIN 字节码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#java-and-kotlin-bytecode)

我们已经知道，Android 应用程序的所有 Java 和 Kotlin 字节码都被编译成一个 DEX 文件。每个 DEX 文件都包含一个[字符串标识符列表](https://source.android.com/devices/tech/dalvik/dex-format#file-layout)(strings_ids)，其中包含每当引用字符串时二进制文件中使用的所有字符串标识符，包括内部命名（例如，类型描述符）或代码引用的常量对象（例如，硬编码字符串） . [您可以使用 Ghidra（基于 GUI）或Dextra](http://newandroidbook.com/tools/dextra.html)（基于 CLI）等工具简单地转储此列表。

使用 Ghidra，只需加载 DEX 文件并在菜单中选择**Window -> Defined strings即可获取字符串。**

> 将 APK 文件直接加载到 Ghidra 中可能会导致不一致。因此，建议通过解压缩 APK 文件来提取 DEX 文件，然后将其加载到 Ghidra 中。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/ghidra_dex_strings.png)

使用 Dextra，您可以使用以下命令转储所有字符串：

```
dextra -S classes.dex
```

Dextra 的输出可以使用标准的 Linux 命令进行操作，例如，`grep`用于搜索某些关键字。

重要的是要知道，使用上述工具获得的字符串列表可能非常大，因为它还包括应用程序中使用的各种类和包名称。浏览完整列表，特别是对于大型二进制文件，可能会非常麻烦。因此，建议从基于关键字的搜索开始，仅在关键字搜索无济于事时才浏览列表。一些可以作为良好起点的通用关键字是 - password、key 和 secret。当您使用应用程序本身时，可以获得特定于应用程序上下文的其他有用关键字。例如，假设应用程序具有登录表单，您可以记下显示的占位符或输入字段的标题文本，并将其用作静态分析的入口点。

##### Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#native-code)

为了从 Android 应用程序中使用的Native代码中提取字符串，您可以使用 Ghidra 或 Cutter 等 GUI 工具，或者依赖基于 CLI 的工具，例如*字符串*Unix 实用程序 ( `strings <path_to_binary>`) 或 radare2 的 rabin2 ( `rabin2 -zz <path_to_binary>`)。使用基于 CLI 的工具时，您可以利用 grep 等其他工具（例如结合正则表达式）进一步过滤和分析结果。

#### 交叉引用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#cross-references)

##### JAVA 和Kotlin[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#java-and-kotlin)

有许多 RE 工具支持检索 Java 交叉引用。对于许多基于 GUI 的函数，这通常是通过右键单击所需函数并选择相应的选项来完成的，例如在 Ghidra 中**显示对**的引用或在 jadx中[查找](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)[**用法**](https://github.com/skylot/jadx/wiki/jadx-gui-features-overview#find-usage)。

##### Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#native-code_1)

与 Java 分析类似，您也可以使用 Ghidra 分析原生库并通过右键单击所需函数并选择**Show References to 来**获取交叉引用。

#### 接口使用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#api-usage)

Android 平台为应用程序中的常用功能提供了许多内置库，例如加密、蓝牙、NFC、网络或位置库。确定这些库在应用程序中的存在可以为我们提供有关其性质的宝贵信息。

例如，如果应用程序正在导入`javax.crypto.Cipher`，则表明该应用程序将执行某种加密操作。幸运的是，密码调用本质上是非常标准的，即它们需要以特定顺序调用才能正常工作，这一知识在分析密码 API 时会很有帮助。例如，通过查找`Cipher.getInstance`函数，我们可以确定所使用的加密算法。通过这种方法，我们可以直接转向分析加密资产，这在应用程序中通常非常关键。有关如何分析 Android 加密 API 的更多信息，请参阅“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”部分。

同样，上述方法可用于确定应用程序在何处以及如何使用 NFC。例如，使用基于主机的卡仿真来执行数字支付的应用程序必须使用该`android.nfc`包。因此，NFC API 分析的一个很好的陈述点是查阅[Android 开发者文档](https://developer.android.com/guide/topics/connectivity/nfc/hce)以获得一些想法并开始搜索关键函数，例如`processCommandApdu`来自`android.nfc.cardemulation.HostApduService`类的函数。

#### 网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#network-communication)

您可能遇到的大多数应用程序都连接到远程端点。即使在您执行任何动态分析（例如流量捕获和分析）之前，您也可以通过枚举应用程序应该与之通信的域来获得一些初始输入或入口点。

通常，这些域将作为字符串出现在应用程序的二进制文件中。实现这一目标的一种方法是使用自动化工具，例如[APKEnum](https://github.com/shivsahni/APKEnum)或[MobSF](https://github.com/MobSF/Mobile-Security-Framework-MobSF)。或者，您可以使用正则表达式对域名进行*grep 。*为此，您可以直接以应用程序二进制文件为目标或对其进行反向工程并以反汇编或反编译代码为目标。后一种选择有一个明显的优势：它可以为您提供**context**，因为您将能够看到每个域在哪个上下文中被使用（例如类和方法）。``

从这里开始，您可以使用此信息获得更多见解，这些见解可能会在稍后的分析过程中使用，例如，您可以将域与固定证书或[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)文件进行匹配，或者对域名执行进一步侦察以了解更多信息目标环境。在评估应用程序时，检查网络安全配置文件很重要，因为通常（安全性较低）调试配置可能会被错误地推送到最终版本中。

安全连接的实施和验证可能是一个复杂的过程，需要考虑许多方面。例如，许多应用程序使用除 HTTP 之外的其他协议，例如 XMPP 或纯 TCP 数据包，或执行证书固定以试图阻止 MITM 攻击，但不幸的是在其实现中存在严重的逻辑错误或固有错误的安全网络配置。

请记住，在大多数情况下，仅使用静态分析是不够的，与可以获得更可靠结果的动态替代方案（例如使用拦截器代理）相比，甚至可能变得极其低效。在本节中，我们只是略微触及了表面，请参阅“Android 基本安全测试”一章中的“[基本网络监控/嗅探”部分，并查看“ ](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#basic-network-monitoringsniffing)[Android 网络通信](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/)”一章中的测试用例。

### 手动（反向）代码审查[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#manual-reversed-code-review)

#### 查看反编译的 Java 代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)

按照[“反编译 Java 代码”](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#decompiling-java-code)中的示例，我们假设您已在 IntelliJ 中成功反编译并打开[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)。一旦 IntelliJ 为代码编制了索引，您就可以像浏览任何其他 Java 项目一样浏览它。请注意，许多反编译的包、类和方法都有奇怪的单字母名称；这是因为字节码在构建时已经用混淆器“缩小”了。这是一种基本类型的[混淆](https://mas.owasp.org/MASTG/General/0x04c-Tampering-and-Reverse-Engineering/#obfuscation)，它使字节码更难阅读，但是对于像这样一个相当简单的应用程序，它不会让您感到很头疼。但是，当您分析更复杂的应用程序时，它会变得非常烦人。

在分析混淆代码时，在进行过程中注释类名、方法名和其他标识符是一种很好的做法。打开`MainActivity`包中的类`sg.vantagepoint.uncrackable1`。`verify`当您点击“验证”按钮时调用该方法。此方法将用户输入传递给名为 的静态方法`a.a`，该方法返回一个布尔值。验证用户输入似乎是合理的`a.a`，因此我们将重构代码以反映这一点。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/check_input.jpg)

右键单击类名（中的第一个）并从下拉菜单中选择 Refactor -> Rename（或按 Shift-F6）`a`。`a.a`根据您目前对课程的了解，将课程名称更改为更有意义的名称。例如，您可以将其称为“Validator”（您以后可以随时修改名称）。`a.a`现在变成了`Validator.a`。按照相同的步骤将静态方法重命名`a`为`check_input`.

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/refactored.jpg)

恭喜，您刚刚学习了静态分析的基础知识！这一切都是关于对所分析的程序进行理论化、注释和逐渐修改理论，直到您完全理解它，或者至少对您想要实现的目标足够了解为止。

接下来，按住 Ctrl 单击（或在 Mac 上按住 Command 单击）该`check_input`方法。这会将您带到方法定义。反编译的方法如下所示：

```
    public static boolean check_input(String string) {
        byte[] arrby = Base64.decode((String) \
        "5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc=", (int)0);
        byte[] arrby2 = new byte[]{};
        try {
            arrby = sg.vantagepoint.a.a.a(Validator.b("8d127684cbc37c17616d806cf50473cc"), arrby);
            arrby2 = arrby;
        }sa
        catch (Exception exception) {
            Log.d((String)"CodeCheck", (String)("AES error:" + exception.getMessage()));
        }
        if (string.equals(new String(arrby2))) {
            return true;
        }
        return false;
    }
```

所以，你有一个 Base64 编码的字符串，它被传递给`a`包中的函数 \ `sg.vantagepoint.a.a`（同样，一切都被调用`a`）以及看起来可疑的十六进制加密密钥（16 个十六进制字节 = 128 位，一个通用密钥长度） . 这个特别的到底是`a`做什么的？按住 Ctrl 键并单击它以找出答案。

```
public class a {
    public static byte[] a(byte[] object, byte[] arrby) {
        object = new SecretKeySpec((byte[])object, "AES/ECB/PKCS7Padding");
        Cipher cipher = Cipher.getInstance("AES");
        cipher.init(2, (Key)object);
        return cipher.doFinal(arrby);
    }
}
```

现在您有所收获：它只是标准的 AES-ECB。看起来存储在其中的Base64字符串`arrby1`是`check_input`一个密文。它使用 128 位 AES 解密，然后与用户输入进行比较。作为奖励任务，尝试解密提取的密文并找到秘密值！

获取解密字符串的更快方法是添加动态分析。稍后我们将重新访问[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)以展示如何操作（例如在“调试”部分），所以不要删除该项目！

#### 查看反汇编的Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)

按照“反汇编Native代码”中的示例，我们将使用不同的反汇编程序来查看反汇编的Native代码。

##### RADARE2[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#radare2_1)

在 radare2 中打开文件后，您应该首先获取要查找的函数的地址。您可以通过列出或获取`i`有关某些关键字的符号`s`( `is`) 和 grepping（`~`radare2 的内置 grep）的信息来执行此操作，在我们的例子中，我们正在寻找 JNI 相关符号，因此我们输入“Java”：

```
$ r2 -A HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so
...
[0x00000e3c]> is~Java
003 0x00000e78 0x00000e78 GLOBAL   FUNC   16 Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI
```

该方法可以在地址找到`0x00000e78`。要显示其反汇编，只需运行以下命令：

```
[0x00000e3c]> e emu.str=true;
[0x00000e3c]> s 0x00000e78
[0x00000e78]> af
[0x00000e78]> pdf
╭ (fcn) sym.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI 12
│   sym.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI (int32_t arg1);
│           ; arg int32_t arg1 @ r0
│           0x00000e78  ~   0268           ldr r2, [r0]                ; arg1
│           ;-- aav.0x00000e79:
│           ; UNKNOWN XREF from aav.0x00000189 (+0x3)
│           0x00000e79                    unaligned
│           0x00000e7a      0249           ldr r1, aav.0x00000f3c      ; [0xe84:4]=0xf3c aav.0x00000f3c
│           0x00000e7c      d2f89c22       ldr.w r2, [r2, 0x29c]
│           0x00000e80      7944           add r1, pc                  ; "Hello from C++" section..rodata
╰           0x00000e82      1047           bx r2
```

让我们解释一下前面的命令：

- `e emu.str=true;`启用 radare2 的字符串模拟。多亏了这个，我们可以看到我们正在寻找的字符串（“Hello from C++”）。
- `s 0x00000e78`是对我们目标函数所在地址的*搜索。*`s 0x00000e78`我们这样做是为了将以下命令应用于该地址。
- `pdf`表示*功能的打印反汇编*。

使用 radare2，您可以快速运行命令并使用标志退出`-qc '<commands>'`。从前面的步骤我们已经知道该怎么做，所以我们将简单地将所有内容放在一起：

```
$ r2 -qc 'e emu.str=true; s 0x00000e78; af; pdf' HelloWord-JNI/lib/armeabi-v7a/libnative-lib.so

╭ (fcn) sym.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI 12
│   sym.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI (int32_t arg1);
│           ; arg int32_t arg1 @ r0
│           0x00000e78      0268           ldr r2, [r0]                ; arg1
│           0x00000e7a      0249           ldr r1, [0x00000e84]        ; [0xe84:4]=0xf3c
│           0x00000e7c      d2f89c22       ldr.w r2, [r2, 0x29c]
│           0x00000e80      7944           add r1, pc                  ; "Hello from C++" section..rodata
╰           0x00000e82      1047           bx r2
```

请注意，在这种情况下，我们不是以`-A`标志 not running开始的`aaa`。相反，我们只是告诉 radare2 使用*analyze function* `af`命令分析那个函数。这是我们可以加快工作流程的案例之一，因为您专注于应用程序的某些特定部分。

[通过使用r2ghidra-dec](https://github.com/radareorg/r2ghidra-dec)可以进一步改进工作流程， r2ghidra-dec是针对 radare2 的 Ghidra 反编译器的深度集成。r2ghidra-dec 生成反编译的 C 代码，这有助于快速分析二进制文件。

##### IDA专业版[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#ida-pro_1)

我们假设您已经`lib/armeabi-v7a/libnative-lib.so`在 IDA pro 中成功打开。加载文件后，单击左侧的“功能”窗口，然后按`Alt+t`打开搜索对话框。输入“java”并按回车键。这应该突出`Java_sg_vantagepoint_helloworld_ MainActivity_stringFromJNI`功能。双击函数跳转到它在反汇编窗口中的地址。“Ida View-A”现在应该显示函数的反汇编。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/helloworld_stringfromjni.jpg)

那里的代码不多，但你应该分析一下。您需要知道的第一件事是传递给每个 JNI 函数的第一个参数是 JNI 接口指针。接口指针是指向指针的指针。这个指针指向一个函数表：一个由更多指针组成的数组，每个指针都指向一个 JNI 接口函数（你是不是头晕了？）。函数表由 Java VM 初始化，并允许Native函数与 Java 环境交互。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/JNI_interface.png)

考虑到这一点，让我们看一下每一行汇编代码。

```
LDR  R2, [R0]
```

请记住：第一个参数（在 R0 中）是指向 JNI 函数表指针的指针。该`LDR`指令将此函数表指针加载到 R2 中。

```
LDR  R1, =aHelloFromC
```

该指令将字符串“Hello from C++”的 PC 相对偏移量加载到 R1 中。请注意，此字符串直接出现在功能块结束后的偏移量 0xe84 处。相对于程序计数器的寻址允许代码独立于其在内存中的位置运行。

```
LDR.W  R2, [R2, #0x29C]
```

该指令将函数指针从偏移量 0x29C 加载到 R2 指向的 JNI 函数指针表中。这就是`NewStringUTF`功能。您可以查看 jni.h 中的函数指针列表，它包含在 Android NDK 中。函数原型如下所示：

```
jstring     (*NewStringUTF)(JNIEnv*, const char*);
```

该函数有两个参数：JNIEnv 指针（已经在 R0 中）和一个 String 指针。接下来，PC 的当前值与 R1 相加，得到静态字符串“Hello from C++”的绝对地址（PC + 偏移量）。

```
ADD  R1, PC
```

`NewStringUTF`最后，程序对加载到R2中的函数指针执行分支指令：

```
BX   R2
```

当此函数返回时，R0 包含指向新构造的 UTF 字符串的指针。这是最终的返回值，所以 R0 保持不变，函数返回。

##### Ghidra[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#ghidra)

在 Ghidra 中打开库后，我们可以在 Functions 下的**Symbol Tree**面板中看到定义的所有**函数**。当前应用程序的Native库(NATIVE LIBRARIES)相对非常小。共有三个用户定义函数：`FUN_001004d0`、`FUN_0010051c`和`Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI`。其他符号不是用户定义的，而是为共享库的正常运行而生成的。函数中的指令`Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI`已经在前面的章节中详细讨论过。在本节中，我们可以查看函数的反编译。

在当前函数内部有对另一个函数的调用，其地址是通过访问`JNIEnv`指针中的偏移量（发现为`plParm1`）获得的。上面也以图解方式演示了此逻辑。反汇编函数的相应 C 代码显示在**反编译**器窗口中。这段反编译的 C 代码使理解所进行的函数调用变得更加容易。由于这个函数很小而且非常简单，反编译输出非常准确，这在处理复杂函数时可能会发生巨大变化。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/Ghidra_decompiled_function.png)

### 自动静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#automated-static-analysis)

您应该使用工具进行高效的静态分析。它们允许测试人员专注于更复杂的业务逻辑。有大量静态代码分析器可用，从开源扫描器到成熟的企业级扫描器。适合这项工作的最佳工具取决于预算、客户要求和测试人员的偏好。

一些静态分析器依赖于源代码的可用性；其他人将编译后的 APK 作为输入。请记住，静态分析器可能无法自行发现所有问题，即使它们可以帮助我们关注潜在问题。仔细检查每个发现并尝试了解该应用程序正在做什么以提高您发现漏洞的机会。

正确配置静态分析器以减少误报的可能性，并且可能只在扫描中选择几个漏洞类别。否则静态分析器生成的结果可能是压倒性的，如果您必须手动调查大型报告，您的努力可能会适得其反。

有多种开源工具可用于对 APK 进行自动安全分析。

- [Androbugs](https://github.com/AndroBugs/AndroBugs_Framework)
- [JAADAS](https://github.com/flankerhqd/JAADAS)
- [MobSF](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#mobsf)
- [QARK](https://github.com/linkedin/qark/)

## 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#dynamic-analysis)

动态分析通过执行和运行应用程序二进制文件并分析其工作流中的漏洞来测试移动应用程序。例如，在静态分析中有时可能很难发现有关数据存储的漏洞，但在动态分析中，您可以轻松发现持久存储的信息以及信息是否得到适当保护。除此之外，动态分析允许测试人员正确识别：

- 业务逻辑缺陷
- 测试环境中的漏洞
- 通过一项或多项服务处理时输入验证薄弱和输入/输出编码错误

在评估应用程序时，可以借助自动化工具（例如[MobSF ）进行分析。](https://github.com/MobSF/Mobile-Security-Framework-MobSF/)可以通过侧面加载、重新打包或简单地攻击已安装的版本来评估应用程序。

### 非 Root 设备的动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#dynamic-analysis-on-non-rooted-devices)

非Root设备具有复制应用程序预期运行的环境的好处。

多亏了诸如[objection](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)之类的工具，您可以为应用程序打补丁以便测试它，就像您在已获得 root 权限的设备上一样（但当然会被囚禁在那个应用程序上）。为此，您必须执行一个额外[的步骤：修补 APK](https://github.com/sensepost/objection/wiki/Patching-Android-Applications#patching---patching-an-apk)以包含[Frida 小工具](https://www.frida.re/docs/gadget/)库。

现在您可以使用 objection 在非 root 设备上动态分析应用程序。

[以下命令以UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)为例总结了如何使用 objection 打补丁和启动动态分析：

```
# Download the Uncrackable APK
$ wget https://raw.githubusercontent.com/OWASP/owasp-mastg/master/Crackmes/Android/Level_01/UnCrackable-Level1.apk
# Patch the APK with the Frida Gadget
$ objection patchapk --source UnCrackable-Level1.apk
# Install the patched APK on the android phone
$ adb install UnCrackable-Level1.objection.apk
# After running the mobile phone, objection will detect the running frida-server through the APK
$ objection explore
```

### 基本信息收集[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#basic-information-gathering_1)

如前所述，Android 在修改后的 Linux 内核之上运行，并保留了 Linux 的[proc 文件系统](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)(procfs)，该文件系统挂载在`/proc`. Procfs 提供系统上运行的进程的基于目录的视图，提供有关进程本身、其线程和其他系统范围诊断的详细信息。Procfs 可以说是 Android 上最重要的文件系统之一，许多操作系统原生工具都依赖它作为信息来源。

许多命令行工具并未随 Android 固件一起提供以减小尺寸，但可以使用[BusyBox](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#busybox)轻松安装在已获得 root 权限的设备上。`cut`我们还可以使用、`grep`等命令创建自己的自定义脚本`sort`来解析 proc 文件系统信息。

在本节中，我们将直接或间接使用来自 procfs 的信息来收集有关正在运行的进程的信息。

#### 打开文件[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#open-files)

您可以使用`lsof`with 标志`-p <pid>`来返回指定进程的打开文件列表。有关更多选项，请参见[手册页](http://man7.org/linux/man-pages/man8/lsof.8.html)。

```
# lsof -p 6233
COMMAND     PID       USER   FD      TYPE             DEVICE  SIZE/OFF       NODE NAME
.foobar.c  6233     u0_a97  cwd       DIR                0,1         0          1 /
.foobar.c  6233     u0_a97  rtd       DIR                0,1         0          1 /
.foobar.c  6233     u0_a97  txt       REG             259,11     23968        399 /system/bin/app_process64
.foobar.c  6233     u0_a97  mem   unknown                                         /dev/ashmem/dalvik-main space (region space) (deleted)
.foobar.c  6233     u0_a97  mem       REG              253,0   2797568    1146914 /data/dalvik-cache/arm64/system@framework@boot.art
.foobar.c  6233     u0_a97  mem       REG              253,0   1081344    1146915 /data/dalvik-cache/arm64/system@framework@boot-core-libart.art
...
```

在上面的输出中，与我们最相关的字段是：

- `NAME`: 文件路径。
- `TYPE`: 文件的类型，例如file是目录还是普通文件。

在使用混淆或其他反逆向工程技术监控应用程序时，这对于发现异常文件非常有用，而无需逆向代码。例如，应用程序可能正在执行数据的加密解密并将其临时存储在文件中。

#### 打开连接[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#open-connections)

`/proc/net`您可以在目录中或仅通过检查目录来找到系统范围的网络信息`/proc/<pid>/net`（出于某种原因而不是特定于进程）。这些目录中存在多个文件，其中`tcp`,`tcp6`和`udp`从测试人员的角度来看可能被认为是相关的。

```
# cat /proc/7254/net/tcp
sl  local_address rem_address   st tx_queue rx_queue tr tm->when retrnsmt   uid  timeout inode
...
69: 1101A8C0:BB2F 9A447D4A:01BB 01 00000000:00000000 00:00000000 00000000 10093        0 75412 1 0000000000000000 20 3 19 10 -1
70: 1101A8C0:917C E3CB3AD8:01BB 01 00000000:00000000 00:00000000 00000000 10093        0 75553 1 0000000000000000 20 3 23 10 -1
71: 1101A8C0:C1E3 9C187D4A:01BB 01 00000000:00000000 00:00000000 00000000 10093        0 75458 1 0000000000000000 20 3 19 10 -1
...
```

在上面的输出中，与我们最相关的字段是：

- `rem_address`: 远程地址和端口号对（十六进制表示）。
- `tx_queue`和`rx_queue`：根据内核内存使用情况的传出和传入数据队列。这些字段指示连接的使用活跃程度。
- `uid`: 包含套接字创建者的有效 UID。

另一种选择是使用`netstat`命令，它还以更易读的格式提供有关整个系统网络活动的信息，并且可以根据我们的要求轻松过滤。例如，我们可以很容易地通过 PID 过滤它：

```
# netstat -p | grep 24685
Active Internet connections (w/o servers)
Proto Recv-Q Send-Q Local Address           Foreign Address         State       PID/Program Name
tcp        0      0 192.168.1.17:47368      172.217.194.103:https   CLOSE_WAIT  24685/com.google.android.youtube
tcp        0      0 192.168.1.17:47233      172.217.194.94:https    CLOSE_WAIT  24685/com.google.android.youtube
tcp        0      0 192.168.1.17:38480      sc-in-f100.1e100.:https ESTABLISHED 24685/com.google.android.youtube
tcp        0      0 192.168.1.17:44833      74.125.24.91:https      ESTABLISHED 24685/com.google.android.youtube
tcp        0      0 192.168.1.17:38481      sc-in-f100.1e100.:https ESTABLISHED 24685/com.google.android.youtube
...
```

`netstat`output 显然比 reading 更人性化`/proc/<pid>/net`。与之前的输出类似，与我们最相关的字段如下：

- `Foreign Address`: 远程地址和端口号对（端口号可以替换为与端口关联的协议的众所周知的名称）。
- `Recv-Q`and `Send-Q`：与接收和发送队列相关的统计信息。指示连接的使用活跃程度。
- `State`：套接字的状态，例如，如果套接字处于活动使用状态 ( `ESTABLISHED`) 或关闭状态 ( `CLOSED`)。

#### 加载Native库(NATIVE LIBRARIES)[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#loaded-native-libraries)

该文件`/proc/<pid>/maps`包含当前映射的内存区域及其访问权限。使用此文件，我们可以获得进程中加载的库列表。

```
# cat /proc/9568/maps
12c00000-52c00000 rw-p 00000000 00:04 14917                              /dev/ashmem/dalvik-main space (region space) (deleted)
6f019000-6f2c0000 rw-p 00000000 fd:00 1146914                            /data/dalvik-cache/arm64/system@framework@boot.art
...
7327670000-7329747000 r--p 00000000 fd:00 1884627                        /data/app/com.google.android.gms-4FJbDh-oZv-5bCw39jkIMQ==/oat/arm64/base.odex
..
733494d000-7334cfb000 r-xp 00000000 fd:00 1884542                        /data/app/com.google.android.youtube-Rl_hl9LptFQf3Vf-JJReGw==/lib/arm64/libcronet.80.0.3970.3.so
...
```

#### 沙箱检查[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#sandbox-inspection)

应用程序数据存储在位于 的沙盒目录中`/data/data/<app_package_name>`。该目录的内容已在“[访问应用程序数据目录](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#accessing-app-data-directories)”部分进行了详细讨论。

### 调试[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#debugging)

到目前为止，您一直在使用静态分析技术而不运行目标应用程序。在现实世界中，尤其是在逆向恶意软件或更复杂的应用程序时，纯静态分析非常困难。在Runtime(运行时)观察和操作应用程序可以更容易地破译其行为。接下来，我们将了解可帮助您做到这一点的动态分析方法。

Android 应用程序支持两种不同类型的调试：使用 Java Debug Wire Protocol (JDWP) 在 Java Runtime(运行时)级别进行调试，以及在Native层进行 Linux/Unix 风格的基于 ptrace 的调试，这两种调试对逆向工程师都很有价值.

#### 调试发布应用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#debugging-release-apps)

Dalvik 和 ART 支持 JDWP，这是一种用于在调试器和它调试的 Java 虚拟机 (VM) 之间进行通信的协议。JDWP 是一种标准调试协议，所有命令行工具和 Java IDE 都支持它，包括 jdb、JEB、IntelliJ 和 Eclipse。Android 的 JDWP 实现还包括用于支持由 Dalvik Debug Monitor Server (DDMS) 实现的额外功能的Hook。

JDWP 调试器允许您逐步执行 Java 代码、在 Java 方法上设置断点以及检查和修改局部变量和实例变量。大多数时候，您将使用 JDWP 调试器来调试“普通”Android 应用程序（即，不会多次调用Native库(NATIVE LIBRARIES)的应用程序）。

下面我们将介绍如何单独使用jdb解决[UnCrackable App for Android Level 1 。](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)请注意，这不是解决此 crackme的*有效方法。*实际上，您可以使用 Frida 和其他方法更快地完成此操作，我们将在本指南后面介绍。然而，这只是对 Java 调试器功能的介绍。

#### 使用 jdb 进行调试[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#debugging-with-jdb)

`adb`命令行工具在“ Android[基础安全测试](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/)”一章中介绍过。您可以使用它的`adb jdwp`命令列出连接设备上运行的所有可调试进程的进程 ID（即托管 JDWP 传输的进程）。使用该`adb forward`命令，您可以在主机上打开一个侦听套接字，并将该套接字的传入 TCP 连接转发到所选进程的 JDWP 传输。

```
$ adb jdwp
12167
$ adb forward tcp:7777 jdwp:12167
```

您现在已准备好附加 jdb。但是，附加调试器会导致应用程序恢复，这是您不希望的。您想让它保持暂停状态，以便您可以先进行探索。为防止进程恢复，将`suspend`命令通过管道传输到 jdb：

```
$ { echo "suspend"; cat; } | jdb -attach localhost:7777
Initializing jdb ...
> All threads suspended.
>
```

您现在已附加到挂起的进程并准备好继续执行 jdb 命令。输入`?`打印完整的命令列表。遗憾的是，Android VM 不支持所有可用的 JDWP 功能。例如，`redefine`不支持让您重新定义类代码的命令。另一个重要的限制是行断点不起作用，因为发布字节码不包含行信息。但是，方法断点确实有效。有用的工作命令包括：

- classes: 列出所有加载的类
- class/methods/fields *class id* : 打印有关类的详细信息并列出其方法和字段
- locals：打印当前栈帧中的局部变量
- print/dump *expr* : 打印关于一个对象的信息
- stop in *method* : 设置方法断点
- 清除*方法*：删除方法断点
- set *lvalue* = *expr*：为字段/变量/数组元素分配新值

让我们重新审视[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)的反编译代码，并思考可能的解决方案。一个好的方法是暂停应用程序，使秘密字符串以纯文本形式保存在变量中，以便您可以检索它。不幸的是，除非您首先处理根/篡改检测，否则您不会走那么远。

查看代码，您会看到该方法`sg.vantagepoint.uncrackable1.MainActivity.a`显示“This in acceptable...”消息框。此方法为事件创建`AlertDialog`并设置侦听器类`onClick`。这个类（名为`b`）有一个回调方法，一旦用户点击**OK**按钮就会终止应用程序。为了防止用户简单地取消对话框，`setCancelable`调用了该方法。

```
  private void a(final String title) {
        final AlertDialog create = new AlertDialog$Builder((Context)this).create();
        create.setTitle((CharSequence)title);
        create.setMessage((CharSequence)"This in unacceptable. The app is now going to exit.");
        create.setButton(-3, (CharSequence)"OK", (DialogInterface$OnClickListener)new b(this));
        create.setCancelable(false);
        create.show();
    }
```

您可以通过一点Runtime(运行时)篡改来绕过它。在应用程序仍然暂停的情况下，设置方法断点`android.app.Dialog.setCancelable`并恢复应用程序。

```
> stop in android.app.Dialog.setCancelable
Set breakpoint android.app.Dialog.setCancelable
> resume
All threads resumed.
>
Breakpoint hit: "thread=main", android.app.Dialog.setCancelable(), line=1,110 bci=0
main[1]
```

该应用程序现在在该`setCancelable`方法的第一条指令处暂停。您可以打印通过命令传递给`setCancelable`的`locals`参数（参数在“局部变量”下显示不正确）。

```
main[1] locals
Method arguments:
Local variables:
flag = true
```

`setCancelable(true)`被调用，所以这不可能是我们正在寻找的调用。使用命令恢复进程`resume`。

```
main[1] resume
Breakpoint hit: "thread=main", android.app.Dialog.setCancelable(), line=1,110 bci=0
main[1] locals
flag = false
```

您现在已经`setCancelable`通过参数 调用了`false`。`true`使用命令将变量设置为`set`并恢复。

```
main[1] set flag = true
 flag = true = true
main[1] resume
```

重复这个过程，设置`flag`为`true`每次到断点，直到最后出现alert框（断点会到五六次）。警告框现在应该可以取消了！点击框旁边的屏幕，它会在不终止应用程序的情况下关闭。

现在防篡改已经完成，您已准备好提取秘密字符串！在“静态分析”部分，您看到字符串是用AES解密的，然后与输入到消息框的字符串进行比较。该类的方法`equals`将`java.lang.String`输入的字符串与秘密字符串进行比较。在 上设置方法断点`java.lang.String.equals`，在编辑字段中输入任意文本字符串，然后点击“验证”按钮。到达断点后，您可以使用`locals`命令读取方法参数。

```
> stop in java.lang.String.equals
Set breakpoint java.lang.String.equals
>
Breakpoint hit: "thread=main", java.lang.String.equals(), line=639 bci=2

main[1] locals
Method arguments:
Local variables:
other = "radiusGravity"
main[1] cont

Breakpoint hit: "thread=main", java.lang.String.equals(), line=639 bci=2

main[1] locals
Method arguments:
Local variables:
other = "I want to believe"
main[1] cont
```

这就是您要查找的明文字符串！

#### 使用 IDE 进行调试[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#debugging-with-an-ide)

在 IDE 中使用反编译的源代码设置项目是一个巧妙的技巧，它允许您直接在源代码中设置方法断点。在大多数情况下，您应该能够单步执行应用程序并使用 GUI 检查变量的状态。体验不会是完美的，毕竟它不是原始源代码，因此您将无法设置行断点，有时甚至无法正常工作。话又说回来，逆向代码绝非易事，有效地导航和调试普通的旧 Java 代码是一种非常方便的方法。[NetSPI 博客](https://blog.netspi.com/attacking-android-applications-with-debuggers/)中描述了类似的方法。

要设置 IDE 调试，首先在 IntelliJ 中创建您的 Android 项目，并将反编译的 Java 源代码复制到源文件夹中，如上文“[查看反编译的 Java 代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)”部分所述。在设备上，在“开发者选项”（本教程中[的 UnCrackable App for Android Level 1 ）中选择应用程序作为](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)**调试应用程序**，并确保您已打开“等待调试器”功能。

从启动器中点击应用程序图标后，它将以“等待调试器”模式暂停。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/waitfordebugger.png)

现在您可以设置断点并使用“附加调试器”工具栏按钮附加到应用进程。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/set_breakpoint_and_attach_debugger.png)

请注意，从反编译源调试应用程序时，只有方法断点有效。一旦到达方法断点，您将有机会在方法执行期间单步执行。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/Choose_Process.png)

从列表中选择应用程序后，调试器将附加到应用程序进程，您将到达在该`onCreate`方法上设置的断点。此应用程序在方法内触发反调试和反篡改控件`onCreate`。`onCreate`这就是为什么在执行反篡改和反调试检查之前在方法上设置断点是一个好主意。

`onCreate`接下来，通过在调试器视图中单击“Force Step Into”来单步执行该方法。“Force Step Into”选项允许您调试通常被调试器忽略的 Android 框架函数和核心 Java 类。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/Force_Step_Into.png)

一旦你“Force Step Into”，调试器将停止在下一个方法的开始，也就是`a`类的方法`sg.vantagepoint.a.c`。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/fucntion_a_of_class_sg_vantagepoint_a.png)

`/system/xbin`此方法在目录列表（和其他目录）中搜索“su”二进制文件。由于您是在已获得 root 权限的设备/模拟器上运行该应用程序，因此您需要通过操纵变量和/或函数返回值来击败此检查。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/fucntion_a_of_class_sg_vantagepoint_a.png)

您可以在“变量”窗口中查看目录名称，方法是单击调试器视图中的“跳过”以进入并通过该`a`方法。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/step_over.png)

`System.getenv`使用“Force Step Into”功能进入方法。

获得以冒号分隔的目录名称后，调试器光标将返回到`a`方法的开头，而不是下一个可执行行。发生这种情况是因为您正在处理反编译代码而不是源代码。这种跳过使得遵循代码流对于调试反编译的应用程序至关重要。否则，识别要执行的下一行将变得复杂。

如果不想调试核心Java和Android类，可以在Debugger视图中点击“Step Out”跳出函数。一旦您到达核心 Java 和 Android 类的反编译源和“Step Out”，使用“Force Step Into”可能是个好主意。这将有助于在您关注核心类函数的返回值的同时加快调试速度。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/step_out.png)

该`a`方法获取目录名称后，将在这些目录中搜索`su`二进制文件。要击败此检查，请逐步执行检测方法并检查变量内容。一旦执行到达将检测到二进制文件的位置，`su`通过按 F2 或右键单击并选择“设置值”来修改保存文件名或目录名的变量之一。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/set_value.png)

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/modified_binary_name.png)

一旦修改了二进制名称或目录名称，`File.exists`应该返回`false`.

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/file_exists_false.png)

这会破坏应用程序的第一个Root检测控件。其余的防篡改和反调试控件可以用类似的方法攻破，这样你就可以最终达到秘密字符串验证功能。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/anti_debug_anti_tamper_defeated.png)

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/MainActivity_verify.png)

密码通过`a`类的方法验证`sg.vantagepoint.uncrackable1.a`。在方法上设置断点，`a`并在到达断点时“强制进入”。然后，单步执行直到您到达对 的调用`String.equals`。这是将用户输入与秘密字符串进行比较的地方。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/sg_vantagepoint_uncrackable1_a_function_a.png)

当您到达`String.equals`方法调用时，您可以在“变量”视图中看到秘密字符串。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/secret_code.png)

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/success.png)

#### 调试Native代码[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#debugging-native-code)

Android 上的Native代码被打包到 ELF 共享库中，并像任何其他Native Linux 程序一样运行。因此，您可以使用标准工具（包括 GDB 和内置 IDE 调试器，如 IDA Pro 和 JEB）对其进行调试，只要它们支持设备的处理器架构（大多数设备基于 ARM 芯片组，因此这通常不是问题).

您现在将设置 JNI 演示应用程序 HelloWorld-JNI.apk 以进行调试。它与您在“静态分析Native代码”中下载的 APK 相同。用于`adb install`将其安装在您的设备或模拟器上。

```
adb install HelloWorld-JNI.apk
```

如果您按照本章开头的说明进行操作，您应该已经拥有了 Android NDK。它包含用于各种体系结构的 gdbserver 的预构建版本。将 gdbserver 二进制文件复制到您的设备：

```
adb push $NDK/prebuilt/android-arm/gdbserver/gdbserver /data/local/tmp
```

该`gdbserver --attach`命令使 gdbserver 附加到正在运行的进程并绑定到在中指定的 IP 地址和端口`comm`，在本例中为 HOST:PORT 描述符。在设备上启动 HelloWorldJNI，然后连接到设备并确定 HelloWorldJNI 进程的 PID (sg.vantagepoint.helloworldjni)。然后切换到 root 用户并附加`gdbserver`：

```
$ adb shell
$ ps | grep helloworld
u0_a164   12690 201   1533400 51692 ffffffff 00000000 S sg.vantagepoint.helloworldjni
$ su
# /data/local/tmp/gdbserver --attach localhost:1234 12690
Attached; pid = 12690
Listening on port 1234
```

该进程现在已挂起，并`gdbserver`正在侦听端口上的调试客户端`1234`。通过 USB 连接设备后，您可以使用以下`abd forward`命令将此端口转发到主机上的本地端口：

```
adb forward tcp:1234 tcp:1234
```

您现在将使用`gdb`NDK 工具链中包含的预构建版本。

```
$ $TOOLCHAIN/bin/gdb libnative-lib.so
GNU gdb (GDB) 7.11
(...)
Reading symbols from libnative-lib.so...(no debugging symbols found)...done.
(gdb) target remote :1234
Remote debugging using :1234
0xb6e0f124 in ?? ()
```

您已成功附加到该进程！唯一的问题是您已经来不及调试 JNI 函数了`StringFromJNI`；它只在启动时运行一次。您可以通过激活“等待调试器”选项来解决此问题。转到**Developer Options** -> **Select debug app**并选择 HelloWorldJNI，然后激活**Wait for debugger**开关。然后终止并重新启动该应用程序。它应该自动暂停。

`Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI`我们的目标是在恢复应用程序之前在Native函数的第一条指令处设置断点。不幸的是，这在执行的这一点上是不可能的，因为`libnative-lib.so`它还没有映射到进程内存中，它是在Runtime(运行时)动态加载的。要使其正常工作，您将首先使用 jdb 将进程轻轻地更改为所需状态。

首先，通过附加 jdb 恢复 Java VM 的执行。但是，您不希望进程立即恢复，因此将`suspend`命令通过管道传输到 jdb：

```
$ adb jdwp
14342
$ adb forward tcp:7777 jdwp:14342
$ { echo "suspend"; cat; } | jdb -attach localhost:7777
```

接下来，挂起 Java Runtime(运行时)加载的进程`libnative-lib.so`。在jdb中，在`java.lang.System.loadLibrary`方法处设置断点并恢复进程。到达断点后，执行`step up`命令，该命令将恢复进程直到`loadLibrary`返回。此时，`libnative-lib.so`已经加载完毕。

```
> stop in java.lang.System.loadLibrary
> resume
All threads resumed.
Breakpoint hit: "thread=main", java.lang.System.loadLibrary(), line=988 bci=0
> step up
main[1] step up
>
Step completed: "thread=main", sg.vantagepoint.helloworldjni.MainActivity.<clinit>(), line=12 bci=5

main[1]
```

执行`gdbserver`附加到挂起的应用程序。这将导致应用程序被 Java VM 和 Linux 内核挂起（创建“双挂起”状态）。

```
$ adb forward tcp:1234 tcp:1234
$ $TOOLCHAIN/arm-linux-androideabi-gdb libnative-lib.so
GNU gdb (GDB) 7.7
Copyright (C) 2014 Free Software Foundation, Inc.
(...)
(gdb) target remote :1234
Remote debugging using :1234
0xb6de83b8 in ?? ()
```

### 追踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#tracing)

#### 执行追踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#execution-tracing)

除了对调试有用之外，jdb 命令行工具还提供基本的执行跟踪功能。要从一开始就跟踪应用程序，您可以使用 Android“等待调试器”功能或`kill -STOP`命令暂停应用程序，并附加 jdb 以在任何初始化方法上设置延迟方法断点。到达断点后，使用`trace go methods`命令激活方法跟踪并继续执行。jdb 将从该点开始转储所有方法入口和出口。

```
$ adb forward tcp:7777 jdwp:7288
$ { echo "suspend"; cat; } | jdb -attach localhost:7777
Set uncaught java.lang.Throwable
Set deferred uncaught java.lang.Throwable
Initializing jdb ...
> All threads suspended.
> stop in com.acme.bob.mobile.android.core.BobMobileApplication.<clinit>()
Deferring breakpoint com.acme.bob.mobile.android.core.BobMobileApplication.<clinit>().
It will be set after the class is loaded.
> resume
All threads resumed.M
Set deferred breakpoint com.acme.bob.mobile.android.core.BobMobileApplication.<clinit>()

Breakpoint hit: "thread=main", com.acme.bob.mobile.android.core.BobMobileApplication.<clinit>(), line=44 bci=0
main[1] trace go methods
main[1] resume
Method entered: All threads resumed.
```

Dalvik Debug Monitor Server (DDMS) 是一个 GUI 工具，包含在 Android Studio 中。它可能看起来不多，但它的 Java 方法跟踪器是您可以拥有的最棒的工具之一，而且它对于分析混淆的字节码是不可或缺的。

然而，DDMS 有点令人困惑；它可以通过多种方式启动，并且将根据跟踪方法的方式启动不同的跟踪查看器。在 Android Studio 中有一个名为“Traceview”的独立工具和一个内置查看器，两者都提供不同的方式来导航跟踪。您通常会使用 Android Studio 的内置查看器，它为您提供所有方法调用的可*缩放*分层时间轴。然而，独立工具也很有用，它有一个配置文件面板，显示每个方法所花费的时间以及每个方法的父项和子项。

要在 Android Studio 中记录执行跟踪，请打开GUI 底部的**Android选项卡。**在列表中选择目标进程，然后单击左侧的小**秒表按钮。**这将开始录音。完成后，单击相同的按钮停止录制。集成跟踪视图将打开并显示记录的跟踪。您可以使用鼠标或触控板滚动和缩放时间线视图。

执行跟踪也可以记录在独立的 Android 设备监视器中。设备监视器可以在 Android Studio 中启动（**工具**-> **Android** -> **Android 设备监视器**）或使用命令从 shell`ddms`启动。

**要开始记录跟踪信息，请在Devices**选项卡中选择目标进程，然后单击**Start Method Profiling**。单击**停止**按钮停止记录，之后 Traceview 工具将打开并显示记录的轨迹。单击配置文件面板中的任何方法会在时间轴面板中突出显示所选方法。

DDMS 还提供了一个方便的堆转储按钮，可以将进程的 Java 堆转储到 .hprof 文件。Android Studio 用户指南包含有关 Traceview 的更多信息。

##### 跟踪系统调用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#tracing-system-calls)

在操作系统层次结构中向下移动一个级别，您到达需要 Linux 内核功能的特权功能。这些功能可通过系统调用接口供正常进程使用。检测和拦截对内核的调用是粗略了解用户进程正在做什么的有效方法，并且通常是停用低级篡改防御的最有效方法。

Strace 是一个标准的 Linux 实用程序，默认情况下不包含在 Android 中，但可以通过 Android NDK 从源代码轻松构建。它监视进程和内核之间的交互，是一种非常方便的监视系统调用的方式。然而，也有一个缺点：由于 strace 依赖于`ptrace`附加到目标进程的系统调用，一旦反调试措施生效，它就会停止工作。

**如果设置 > 开发人员选项**中的“等待调试器”功能不可用，您可以使用 shell 脚本启动进程并立即附加 strace（不是一个优雅的解决方案，但它可以工作）：

```
while true; do pid=$(pgrep 'target_process' | head -1); if [[ -n "$pid" ]]; then strace -s 2000 - e "!read" -ff -p "$pid"; break; fi; done
```

##### 跟踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#ftrace)

Ftrace 是直接内置于 Linux 内核中的跟踪实用程序。在获得 root 权限的设备上，ftrace 可以比 strace 更透明地跟踪内核系统调用（strace 依赖 ptrace 系统调用来附加到目标进程）。

方便的是，Lollipop 和 Marshmallow 上的原生 Android 内核都包含 ftrace 功能。可以使用以下命令启用该功能：

```
echo 1 > /proc/sys/kernel/ftrace_enabled
```

该`/sys/kernel/debug/tracing`目录包含与 ftrace 相关的所有控制和输出文件。在此目录中找到以下文件：

- available_tracers：该文件列出了编译到内核中的可用跟踪器。
- current_tracer：此文件设置或显示当前跟踪器。
- tracing_on：将“1”回显到此文件中以允许/开始更新环形缓冲区。回显“0”将阻止进一步写入环形缓冲区。

##### KPROBES[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#kprobes)

KProbes 接口提供了一种更强大的检测内核的方法：它允许您将探测器插入内核内存中的（几乎）任意代码地址。KProbes 在指定地址插入断点指令。一旦到达断点，控制传递给 KProbes 系统，然后执行用户定义的处理函数和原始指令。除了非常适合功能跟踪之外，KProbes 还可以实现类似 rootkit 的功能，例如文件隐藏。

Jprobes 和 Kretprobes 是其他基于 KProbes 的探测类型，它们允许Hook函数入口和出口。

普通的 Android 内核没有可加载模块支持，这是一个问题，因为 Kprobes 通常作为内核模块部署。Android 内核编译时使用的严格内存保护是另一个问题，因为它会阻止对内核内存的某些部分进行修补。Elfmaster 的系统调用Hook方法导致库存 Lollipop 和 Marshmallow 发生内核恐慌，因为 sys_call_table 是不可写的。但是，您可以通过编译自己的、更宽松的内核（稍后详细介绍）在沙箱中使用 KProbes。

#### 方法追踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-tracing)

与告诉您调用方法的频率的方法分析不同，方法跟踪还可以帮助您确定其输入和输出值。在处理具有大型代码库和/或被混淆的应用程序时，这种技术可以证明是非常有用的。

正如我们将在下一节中很快讨论的那样，`frida-trace`为 Android/iOS Native代码跟踪和 iOS 高级方法跟踪提供开箱即用的支持。如果您更喜欢基于 GUI 的方法，您可以使用[RMS - Runtime Mobile Security](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#RMS-Runtime-Mobile-Security)等工具，它可以提供更直观的体验并包含多个方便的[跟踪选项](https://github.com/m0bilesecurity/RMS-Runtime-Mobile-Security#3-hook-on-the-fly-classesmethods-and-trace-their-args-and-return-values)。

#### Native代码跟踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#native-code-tracing)

与 Java 方法跟踪相比，Native方法跟踪可以相对容易地执行。`frida-trace`是一个用于动态跟踪函数调用的 CLI 工具。它使跟踪Native函数变得微不足道，并且对于收集有关应用程序的信息非常有用。

为了使用`frida-trace`，Frida 服务器应该在设备上运行。下面演示了使用跟踪 libc`open`函数的示例，其中连接到 USB 设备并指定要包含在跟踪中的函数。`frida-trace``-U``-i`

```
frida-trace -U -i "open" com.android.chrome
```

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/frida_trace_native_functions.png)

请注意，默认情况下，如何只显示传递给函数的参数，而不显示返回值。在后台，`frida-trace`在自动生成的`__handlers__`文件夹中为每个匹配的函数生成一个小的 JavaScript 处理程序文件，然后 Frida 将其注入到进程中。您可以编辑这些文件以获得更高级的用法，例如获取函数的返回值、它们的输入参数、访问内存等。查看 Frida 的[JavaScript API](https://www.frida.re/docs/javascript-api/)了解更多详细信息。

在这种情况下，跟踪所有`open`函数调用的生成脚本`libc.so`位于 is 中`__handlers__/libc.so/open.js`，如下所示：

```
{
  onEnter: function (log, args, state) {
    log('open(' +
      'path="' + args[0].readUtf8String() + '"' +
      ', oflag=' + args[1] +
    ')');
  },


  onLeave: function (log, retval, state) {
      log('\t return: ' + retval);      \\ edited
  }
}
```

在上面的脚本中，`onEnter`负责以正确的格式记录对此函数的调用及其两个输入参数。您可以编辑`onLeave`事件以打印返回值，如上所示。

> 请注意，libc 是一个众所周知的库，Frida 能够导出其`open`函数的输入参数并自动正确记录它们。但对于其他库或 Android Kotlin/Java 代码，情况并非如此。在这种情况下，您可能希望通过参考 Android 开发人员文档或首先对应用程序进行逆向工程来获取您感兴趣的函数的签名。

在上面的输出中要注意的另一件事是它是彩色的。一个应用程序可以有多个线程运行，每个线程可以`open`独立调用函数。通过使用这样的配色方案，每个线程的输出可以很容易地在视觉上分离。

`frida-trace`是一个非常通用的工具，有多种配置选项可用，例如：

- 包括`-I`和排除`-X`整个模块。
- `-i "Java_*"`使用（注意使用 glob`*`来匹配以“Java_”开头的所有可能函数）跟踪 Android 应用程序中的所有 JNI 函数。
- 当没有可用的函数名称符号（剥离的二进制文件）时按地址跟踪函数，例如`-a "libjpeg.so!0x4793c"`.

```
frida-trace -U -i "Java_*" com.android.chrome
```

许多二进制文件被剥离并且没有可用的函数名称符号。在这种情况下，也可以使用其地址来跟踪函数。

```
frida-trace -p 1372 -a "libjpeg.so!0x4793c"
```

Frida 12.10 引入了一种新的有用语法来查询 Java 类和方法，以及通过`-j`（从 frida-tools 8.0 开始）对 frida-trace 的 Java 方法跟踪支持。

- 在 Frida 脚本中：例如`Java.enumerateMethods('*youtube*!on*')`，使用 globs 获取所有名称中包含“youtube”的类，并枚举所有以“on”开头的方法。
- 在 frida-trace 中：例如`-j '*!*certificate*/isu'`触发不区分大小写的查询（`i`），包括方法签名（`s`）并排除系统类（`u`）。

有关详细信息，请参阅[发行说明](https://frida.re/news/2020/06/29/frida-12-10-released/)。要了解有关高级用法的所有选项的更多信息，请查看[Frida 官方网站上的文档](https://frida.re/docs/frida-trace/)。

#### JNI 跟踪[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#jni-tracing)

如[审查反汇编Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)部分中所述，传递给每个 JNI 函数的第一个参数是 JNI 接口指针。该指针包含一个函数表，允许Native代码访问 Android Runtime(运行时)。识别对这些函数的调用有助于理解库功能，例如创建了哪些字符串或调用了 Java 方法。

[jnitrace](https://github.com/chame1eon/jnitrace)是一个类似于 frida-trace 的基于 Frida 的工具，它专门针对本地库对 Android 的 JNI API 的使用，提供了一种获取 JNI 方法跟踪（包括参数和返回值）的便捷方式。

您可以通过运行轻松安装它`pip install jnitrace`并直接运行它，如下所示：

```
jnitrace -l libnative-lib.so sg.vantagepoint.helloworldjni
```

> `-l`可以多次提供该选项以跟踪多个库，`*`也可以提供该选项以跟踪所有库。然而，这可能会提供很多输出。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/jni_tracing_helloworldjni.png)

在输出中，您可以看到`NewStringUTF`从Native代码调用的跟踪（它的返回值然后返回给 Java 代码，请参阅“[审查反汇编的Native代码](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)”部分了解更多详细信息）。请注意与 frida-trace 的相似之处，输出是彩色的，有助于在视觉上区分不同的线程。

跟踪 JNI API 调用时，您可以在顶部看到线程 ID，然后是 JNI 方法调用，包括方法名称、输入参数和返回值。在从Native代码调用 Java 方法的情况下，还将提供 Java 方法参数。最后，jnitrace 将尝试使用 Frida 回溯库来显示 JNI 调用的来源。

要了解有关高级用法的所有选项的更多信息，请查看[jnitrace GitHub 页面上的文档](https://github.com/chame1eon/jnitrace)。

### 基于仿真的分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#emulation-based-analysis)

Android 模拟器基于 QEMU，一个通用的开源机器模拟器。QEMU 通过将运行中的客户指令翻译成主机处理器可以理解的指令来模拟客户 CPU。来宾指令的每个基本块都被反汇编并翻译成称为微型代码生成器 (TCG) 的中间表示。TCG 块被编译成主机指令块，存储在代码缓存中，并被执行。基本块执行后，QEMU 为下一个客户指令块重复该过程（或从缓存中加载已翻译的块）。整个过程称为动态二进制翻译。

因为 Android 模拟器是 QEMU 的一个分支，所以它具有 QEMU 的所有功能，包括监控、调试和跟踪功能。QEMU 特定的参数可以通过`-qemu`命令行标志传递给模拟器。您可以使用 QEMU 的内置跟踪工具来记录执行的指令和虚拟寄存器值。使用命令行标志启动 QEMU`-d`将导致它转储客户代码块、微操作或正在执行的主机指令。有了这个`-d_asm`标志，QEMU 会在客户代码进入 QEMU 的翻译功能时记录所有基本块。以下命令将所有已翻译的块记录到一个文件中：

```
emulator -show-kernel -avd Nexus_4_API_19 -snapshot default-boot -no-snapshot-save -qemu -d in_asm,cpu 2>/tmp/qemu.log
```

不幸的是，使用 QEMU 生成完整的客户指令跟踪是不可能的，因为代码块仅在它们被翻译时写入日志，而不是在它们从缓存中取出时写入日志。例如，如果一个块在循环中重复执行，则只有第一次迭代会打印到日志中。没有办法在 QEMU 中禁用 TB 缓存（除了破解源代码）。尽管如此，该功能足以完成基本任务，例如重建Native执行的密码算法的反汇编。

### 二进制分析[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#binary-analysis)

二进制分析框架为您提供了强大的方法来自动执行几乎不可能手动完成的任务。二进制分析框架通常使用一种称为符号执行的技术，它可以确定达到特定目标所需的条件。它将程序的语义翻译成逻辑公式，其中一些变量由具有特定约束的符号表示。通过解析约束，可以找到执行程序某个分支所必需的条件。

#### 符号执行[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#symbolic-execution)

符号执行是工具箱中非常有用的技术，尤其是在处理需要找到正确输入以到达特定代码块的问题时。在本节中，我们将使用[Angr](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#angr)二进制分析框架作为我们的符号执行引擎来解决一个简单的 Android crackme。

目标 crackme 是一个简单的[Android License Validator](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-license-validator)可执行文件。正如我们很快就会观察到的那样，crackme 中的关键验证逻辑是用Native代码实现的。人们普遍认为，分析已编译的Native代码比分析等效的已编译 Java 代码更难，因此，关键业务逻辑通常是用Native编写的。当前的示例应用程序可能不代表现实世界的问题，但它有助于获得一些关于符号执行的基本概念，您可以在实际情况中使用这些概念。您可以在带有混淆Native库(NATIVE LIBRARIES)的 Android 应用程序上使用相同的技术（事实上，混淆代码通常专门放入Native库(NATIVE LIBRARIES)中，以增加去混淆的难度）。

crackme 由单个 ELF 可执行文件组成，可以按照以下说明在任何 Android 设备上执行：

```
$ adb push validate /data/local/tmp
[100%] /data/local/tmp/validate

$ adb shell chmod 755 /data/local/tmp/validate

$ adb shell /data/local/tmp/validate
Usage: ./validate <serial>

$ adb shell /data/local/tmp/validate 12345
Incorrect serial (wrong format).
```

到目前为止一切顺利，但我们对有效的Licenses（许可证）密钥是什么样子一无所知。首先，在 Cutter 等反汇编程序中打开 ELF 可执行文件。主要功能位于`0x00001874`反汇编中的偏移处。重要的是要注意这个二进制文件启用了 PIE，并且 Cutter 选择加载二进制文件`0x0`作为图像基地址。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/disass_main_1874.png)

函数名称已从二进制文件中剥离，但幸运的是有足够的调试字符串为我们提供代码上下文。接下来，我们将从 offset 处的入口函数开始分析二进制文件`0x00001874`，并记下我们可以轻松获得的所有信息。在此分析过程中，我们还将尝试识别适合符号执行的代码区域。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/graph_1874.png)

`strlen`在 offset 处调用`0x000018a8`，并将返回值与 offset 处的 0x10 进行比较`0x000018b0`。紧接着，输入字符串被传递到 offset 处的 Base32 解码函数`0x00001340`。这为我们提供了有价值的信息，即输入的Licenses（许可证）密钥是一个 Base32 编码的 16 个字符的字符串（原始总计 10 个字节）。然后将解码的输入传递给 offset 处的函数，该函数`0x00001760`验证Licenses（许可证）密钥。该函数的反汇编如下所示。

我们现在可以使用有关预期输入的信息进一步研究 处的验证函数`0x00001760`。

```
╭ (fcn) fcn.00001760 268
│   fcn.00001760 (int32_t arg1);
│           ; var int32_t var_20h @ fp-0x20
│           ; var int32_t var_14h @ fp-0x14
│           ; var int32_t var_10h @ fp-0x10
│           ; arg int32_t arg1 @ r0
│           ; CALL XREF from fcn.00001760 (+0x1c4)
│           0x00001760      push {r4, fp, lr}
│           0x00001764      add fp, sp, 8
│           0x00001768      sub sp, sp, 0x1c
│           0x0000176c      str r0, [var_20h]                          ; 0x20 ; "$!" ; arg1
│           0x00001770      ldr r3, [var_20h]                          ; 0x20 ; "$!" ; entry.preinit0
│           0x00001774      str r3, [var_10h]                          ; str.
│                                                                      ; 0x10
│           0x00001778      mov r3, 0
│           0x0000177c      str r3, [var_14h]                          ; 0x14
│       ╭─< 0x00001780      b 0x17d0
│       │   ; CODE XREF from fcn.00001760 (0x17d8)
│      ╭──> 0x00001784      ldr r3, [var_10h]                          ; str.
│       │                                                              ; 0x10 ; entry.preinit0
│      ╎│   0x00001788      ldrb r2, [r3]
│      ╎│   0x0000178c      ldr r3, [var_10h]                          ; str.
│      ╎│                                                              ; 0x10 ; entry.preinit0
│      ╎│   0x00001790      add r3, r3, 1
│      ╎│   0x00001794      ldrb r3, [r3]
│      ╎│   0x00001798      eor r3, r2, r3
│      ╎│   0x0000179c      and r2, r3, 0xff
│      ╎│   0x000017a0      mvn r3, 0xf
│      ╎│   0x000017a4      ldr r1, [var_14h]                          ; 0x14 ; entry.preinit0
│      ╎│   0x000017a8      sub r0, fp, 0xc
│      ╎│   0x000017ac      add r1, r0, r1
│      ╎│   0x000017b0      add r3, r1, r3
│      ╎│   0x000017b4      strb r2, [r3]
│      ╎│   0x000017b8      ldr r3, [var_10h]                          ; str.
│      ╎│                                                              ; 0x10 ; entry.preinit0
│      ╎│   0x000017bc      add r3, r3, 2                              ; "ELF\x01\x01\x01" ; aav.0x00000001
│      ╎│   0x000017c0      str r3, [var_10h]                          ; str.
│      ╎│                                                              ; 0x10
│      ╎│   0x000017c4      ldr r3, [var_14h]                          ; 0x14 ; entry.preinit0
│      ╎│   0x000017c8      add r3, r3, 1
│      ╎│   0x000017cc      str r3, [var_14h]                          ; 0x14
│      ╎│   ; CODE XREF from fcn.00001760 (0x1780)
│      ╎╰─> 0x000017d0      ldr r3, [var_14h]                          ; 0x14 ; entry.preinit0
│      ╎    0x000017d4      cmp r3, 4                                  ; aav.0x00000004 ; aav.0x00000001 ; aav.0x00000001
│      ╰──< 0x000017d8      ble 0x1784                                 ; likely
│           0x000017dc      ldrb r4, [fp, -0x1c]                       ; "4"
│           0x000017e0      bl fcn.000016f0
│           0x000017e4      mov r3, r0
│           0x000017e8      cmp r4, r3
│       ╭─< 0x000017ec      bne 0x1854                                 ; likely
│       │   0x000017f0      ldrb r4, [fp, -0x1b]
│       │   0x000017f4      bl fcn.0000170c
│       │   0x000017f8      mov r3, r0
│       │   0x000017fc      cmp r4, r3
│      ╭──< 0x00001800      bne 0x1854                                 ; likely
│      ││   0x00001804      ldrb r4, [fp, -0x1a]
│      ││   0x00001808      bl fcn.000016f0
│      ││   0x0000180c      mov r3, r0
│      ││   0x00001810      cmp r4, r3
│     ╭───< 0x00001814      bne 0x1854                                 ; likely
│     │││   0x00001818      ldrb r4, [fp, -0x19]
│     │││   0x0000181c      bl fcn.00001728
│     │││   0x00001820      mov r3, r0
│     │││   0x00001824      cmp r4, r3
│    ╭────< 0x00001828      bne 0x1854                                 ; likely
│    ││││   0x0000182c      ldrb r4, [fp, -0x18]
│    ││││   0x00001830      bl fcn.00001744
│    ││││   0x00001834      mov r3, r0
│    ││││   0x00001838      cmp r4, r3
│   ╭─────< 0x0000183c      bne 0x1854                                 ; likely
│   │││││   0x00001840      ldr r3, [0x0000186c]                       ; [0x186c:4]=0x270 section..hash ; section..hash
│   │││││   0x00001844      add r3, pc, r3                             ; 0x1abc ; "Product activation passed. Congratulations!"
│   │││││   0x00001848      mov r0, r3                                 ; 0x1abc ; "Product activation passed. Congratulations!" ;
│   │││││   0x0000184c      bl sym.imp.puts                            ; int puts(const char *s)
│   │││││                                                              ; int puts("Product activation passed. Congratulations!")
│  ╭──────< 0x00001850      b 0x1864
│  ││││││   ; CODE XREFS from fcn.00001760 (0x17ec, 0x1800, 0x1814, 0x1828, 0x183c)
│  │╰╰╰╰╰─> 0x00001854      ldr r3, aav.0x00000288                     ; [0x1870:4]=0x288 aav.0x00000288
│  │        0x00001858      add r3, pc, r3                             ; 0x1ae8 ; "Incorrect serial." ;
│  │        0x0000185c      mov r0, r3                                 ; 0x1ae8 ; "Incorrect serial." ;
│  │        0x00001860      bl sym.imp.puts                            ; int puts(const char *s)
│  │                                                                   ; int puts("Incorrect serial.")
│  │        ; CODE XREF from fcn.00001760 (0x1850)
│  ╰──────> 0x00001864      sub sp, fp, 8
╰           0x00001868      pop {r4, fp, pc}                           ; entry.preinit0 ; entry.preinit0 ;
```

讨论函数中的所有指令超出了本章的范围，我们将只讨论分析所需的重点。在验证函数中，存在一个循环，该循环`0x00001784`在 offset 处执行 XOR 运算`0x00001798`。循环在下面的图形视图中更清晰可见。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/loop_1784.png)

XOR 是一种非常常用的*加密*信息的技术，其中混淆是目标而不是安全性。**XOR 不应该用于任何严格的加密**，因为它可以使用频率分析来破解。因此，仅在此类验证逻辑中存在 XOR 加密总是需要特别注意和分析。

向前移动，在偏移处`0x000017dc`，将从上面获得的 XOR 解码值与子函数调用的返回值进行比较`0x000017e8`。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/values_compare_17dc.png)

显然这个功能并不复杂，可以手动分析，但仍然是一项繁琐的工作。尤其是在大型代码库上工作时，时间可能是一个主要限制因素，因此希望能够自动执行此类分析。动态符号执行正是在这些情况下很有帮助。在上面的 crackme 中，符号执行引擎可以通过映射Licenses（许可证）检查的第一条指令 (at `0x00001760`) 和打印“产品激活通过”消息的代码(at `0x00001840`)之间的路径来确定输入字符串的每个字节的约束条件.

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/graph_ifelse_1760.png)

从上述步骤获得的约束被传递给求解器引擎，该引擎找到满足它们的输入 - 有效的Licenses（许可证）密钥。

您需要执行几个步骤来初始化 Angr 的符号执行引擎：

- 将二进制文件加载到 a`Project`中，这是 Angr 中任何类型分析的起点。
- 传递分析应从其开始的地址。在这种情况下，我们将使用串行验证函数的第一条指令初始化状态。这使得问题更容易解决，因为您避免了以符号方式执行 Base32 实现。
- 传递分析应该到达的代码块的地址。在这种情况下，这是 offset `0x00001840`，负责打印“产品激活已通过”消息的代码所在的位置。
- 此外，指定分析不应到达的地址。在这种情况下，打印“Incorrect serial”消息的代码块`0x00001854`并不有趣。

> 请注意，Angr 加载器将加载基地址为 的 PIE 可执行文件，`0x400000`在将其传递给 Angr 之前，需要将其添加到 Cutter 的偏移量中。

最终的解决方案脚本如下所示：

```
import angr # Version: 9.2.2
import base64

load_options = {}

b = angr.Project("./validate", load_options = load_options)
# The key validation function starts at 0x401760, so that's where we create the initial state.
# This speeds things up a lot because we're bypassing the Base32-encoder.

options = {
    angr.options.SYMBOL_FILL_UNCONSTRAINED_MEMORY,
    angr.options.ZERO_FILL_UNCONSTRAINED_REGISTERS,
}

state = b.factory.blank_state(addr=0x401760, add_options=options)

simgr = b.factory.simulation_manager(state)
simgr.explore(find=0x401840, avoid=0x401854)

# 0x401840 = Product activation passed
# 0x401854 = Incorrect serial
found = simgr.found[0]

# Get the solution string from *(R11 - 0x20).

addr = found.memory.load(found.regs.r11 - 0x20, 1, endness="Iend_LE")
concrete_addr = found.solver.eval(addr)
solution = found.solver.eval(found.memory.load(concrete_addr,10), cast_to=bytes)
print(base64.b32encode(solution))
```

正如之前在“[动态二进制](https://mas.owasp.org/MASTG/General/0x04c-Tampering-and-Reverse-Engineering/#static-and-dynamic-binary-analysis)检测”部分中讨论的那样，符号执行引擎为给定的程序输入构建一个操作的二叉树，并为可能采用的每个可能路径生成一个数学方程式。在内部，Angr 探索我们指定的两点之间的所有路径，并将相应的数学方程传递给求解器以返回有意义的具体结果。我们可以通过`simulation_manager.found`列表访问这些解决方案，其中包含满足我们指定搜索条件的 Angr 探索的所有可能路径。

仔细查看正在检索最终解决方案字符串的脚本的后半部分。字符串的地址是从 address 中获得的`r11 - 0x20`。这乍一看似乎很神奇，但仔细分析 处的函数可以`0x00001760`找到线索，因为它确定给定的输入字符串是否是有效的Licenses（许可证）密钥。在上面的反汇编中，您可以看到函数的输入字符串（在寄存器 R0 中）是如何存储到局部堆栈变量中的`0x0000176c str r0, [var_20h]`。因此，我们决定使用此值来检索脚本中的最终解决方案。使用`found.solver.eval`你可以问求解器问题，比如“给定这个操作序列的输出（ 中的当前状态`found`），输入（`addr`）必须是什么？”）。

> 在 ARMv7 中，R11 称为 fp（*函数指针*），因此`R11 - 0x20`等同于`fp-0x20`：`var int32_t var_20h @ fp-0x20`

接下来，`endness`脚本中的参数指定数据以“小端”方式存储，几乎所有 Android 设备都是这种情况。

此外，它可能看起来好像脚本只是从脚本的内存中读取解决方案字符串。但是，它是从符号内存中读取的。字符串和指向字符串的指针都不存在。求解器确保它提供的解决方案与程序执行到该点时相同。

运行此脚本应返回以下输出：

```
$ python3 solve.py
WARNING | ... | cle.loader | The main binary is a position-independent executable. It is being loaded with a base address of 0x400000.

b'JACE6ACIARNAAIIA'
```

现在您可以在您的 Android 设备中运行验证二进制文件来验证[此处](https://mas.owasp.org/MASTG/Android/Crackmes/README.md#android-license-validator)所示的解决方案。

> 您可能会使用脚本获得不同的解决方案，因为可能有多个有效的Licenses（许可证）密钥。

总而言之，学习符号执行一开始可能看起来有点吓人，因为它需要深刻的理解和广泛的实践。然而，考虑到与手动分析复杂的反汇编指令相比可以节省宝贵的时间，这种努力是合理的。通常您会使用混合技术，如上例所示，我们对反汇编代码进行手动分析，为符号执行引擎提供正确的标准。有关 Angr 用法的更多示例，请参阅 iOS 章节。

## 篡改和Runtime(运行时)检测[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#tampering-and-runtime-instrumentation)

首先，我们将了解一些修改和检测移动应用程序的简单方法。*篡改*意味着对应用程序进行补丁或Runtime(运行时)更改以影响其行为。例如，您可能想要停用阻碍测试过程的 SSL 固定或二进制保护。*Runtime Instrumentation*包括添加Hook和Runtime(运行时)补丁以观察应用程序的行为。然而，在移动应用程序安全性中，该术语泛指各种Runtime(运行时)操作，包括覆盖方法以更改行为。

### 修补、重新打包和重新签名[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-repackaging-and-re-signing)

对 Android 清单或字节码进行小的更改通常是修复阻止您测试或逆向工程应用程序的小烦恼的最快方法。在 Android 上，两个问题尤其经常发生：

1. 您无法使用代理拦截 HTTPS 流量，因为该应用程序使用 SSL 固定。
2. 您无法将调试器附加到应用程序，因为该`android:debuggable`标志未`"true"`在 Android 清单中设置。

在大多数情况下，这两个问题都可以通过对应用程序进行微小更改（也称为打补丁）然后重新签名和重新打包来解决。在默认 Android 代码签名之外运行额外完整性检查的应用程序是一个例外。在这些情况下，您还必须修补额外的检查。

第一步是使用以下命令解压和反汇编 APK `apktool`：

```
apktool d target_apk.apk
```

> `--no-src`注意：为了节省时间，如果您只想解压 APK 而不想反汇编代码，则可以使用该标志。例如，当您只想修改 Android Manifest 并立即重新打包时。

#### 修补示例：禁用证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-example-disabling-certificate-pinning)

对于出于正当理由想要拦截 HTTPS 通信的安全测试人员来说，证书固定是一个问题。修补字节码以停用 SSL 固定可以帮助解决这个问题。为了演示绕过证书固定，我们将在一个示例应用程序中完成一个实现。

解压和反汇编 APK 后，就可以在 Smali 源代码中找到证书固定检查了。在代码中搜索诸如“X509TrustManager”之类的关键字应该会为您指明正确的方向。

在我们的示例中，搜索“X509TrustManager”会返回一个实现自定义 TrustManager 的类。派生类实现方法`checkClientTrusted`、`checkServerTrusted`和`getAcceptedIssuers`。

要绕过固定检查，请将`return-void`操作码添加到每个方法的第一行。此操作码导致检查立即返回。通过此修改，不执行证书检查，并且应用程序接受所有证书。

```
.method public checkServerTrusted([LJava/security/cert/X509Certificate;Ljava/lang/String;)V
  .locals 3
  .param p1, "chain"  # [Ljava/security/cert/X509Certificate;
  .param p2, "authType"   # Ljava/lang/String;

  .prologue
  return-void      # <-- OUR INSERTED OPCODE!
  .line 102
  iget-object v1, p0, Lasdf/t$a;->a:Ljava/util/ArrayList;

  invoke-virtual {v1}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

  move-result-object v1

  :goto_0
  invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z
```

此修改将破坏 APK 签名，因此您还必须在重新打包后重新签署更改后的 APK 存档。

#### 修补示例：使应用程序可调试[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-example-making-an-app-debuggable)

每个启用调试器的进程都运行一个额外的线程来处理 JDWP 协议数据包。此线程仅针对`android:debuggable="true"`在其清单文件`<application>`元素中设置了标志的应用程序启动。这是交付给最终用户的 Android 设备的典型配置。

在对应用程序进行逆向工程时，您通常只能访问目标应用程序的发布版本。发布版本并不意味着要调试，这就是*调试版本*的目的。如果系统属性`ro.debuggable`设置为“0”，Android 将不允许发布版本的 JDWP 和Native调试。虽然这很容易绕过，但您仍然可能会遇到限制，例如缺少行断点。*尽管如此，即使是一个不完美的调试器仍然是一个非常*宝贵的工具，能够检查程序的Runtime(运行时)状态使得理解程序变得容易得多。

要将发布版本*转换*为可调试版本，您需要修改 Android 清单文件 (AndroidManifest.xml) 中的标志。解压应用程序（例如`apktool d --no-src UnCrackable-Level1.apk`）并解码 Android Manifest 后，`android:debuggable="true"`使用文本编辑器将其添加：

```
<application android:allowBackup="true" android:debuggable="true" android:icon="@drawable/ic_launcher" android:label="@string/app_name" android:name="com.xxx.xxx.xxx" android:theme="@style/AppTheme">
```

即使我们没有更改源代码，此修改也会破坏 APK 签名，因此您还必须重新签署更改后的 APK 存档。

#### 重新包装[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#repackaging)

您可以通过执行以下操作轻松地重新打包应用程序：

```
cd UnCrackable-Level1
apktool b
zipalign -v 4 dist/UnCrackable-Level1.apk ../UnCrackable-Repackaged.apk
```

请注意，Android Studio 构建工具目录必须在路径中。它位于`[SDK-Path]/build-tools/[version]`。`zipalign`和`apksigner`工具都在这个目录中。

#### 重签[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#re-signing)

在重新签名之前，您首先需要一个代码签名证书。如果您之前在 Android Studio 中构建过项目，则 IDE 已经在`$HOME/.android/debug.keystore`. 此 KeyStore 的默认密码为“android”，密钥称为“androiddebugkey”。

标准 Java 发行版包括`keytool`用于管理 KeyStore 和证书的内容。您可以创建自己的签名证书和密钥，然后将其添加到调试密钥库：

```
keytool -genkey -v -keystore ~/.android/debug.keystore -alias signkey -keyalg RSA -keysize 2048 -validity 20000
```

证书可用后，您可以使用它重新签署 APK。确保它`apksigner`在路径中，并且您从重新打包的 APK 所在的文件夹运行它。

```
apksigner sign --ks  ~/.android/debug.keystore --ks-key-alias signkey UnCrackable-Repackaged.apk
```

注意：如果您在使用 时遇到 JRE 兼容性问题`apksigner`，可以`jarsigner`改为使用。执行此操作时，`zipalign`必须**在**签名后调用。

```
jarsigner -verbose -keystore ~/.android/debug.keystore ../UnCrackable-Repackaged.apk signkey
zipalign -v 4 dist/UnCrackable-Level1.apk ../UnCrackable-Repackaged.apk
```

现在您可以重新安装该应用程序：

```
adb install UnCrackable-Repackaged.apk
```

#### “等待调试器”功能[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#the-wait-for-debugger-feature)

[Android 级别 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)的UnCrackable 应用程序并不愚蠢：它注意到它已在可调试模式下运行，并通过关闭做出反应。立即显示模式对话框，点击“确定”后 crackme 终止。

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
    _methods: Object.getOwnPropertyNames(jClass.__proto__).filter(function(m) {
      return !m.startsWith('$') // filter out Frida related special properties
        || m == 'class' || m == 'constructor' // optional
    }),
    _fields: jClass.class.getFields().map(function(f) {
      return( f.toString());
    })
  }, null, 2));
}
```

将脚本保存到名为 java_class_listing.js 的文件后，您可以告诉 Frida CLI 使用标志加载它，`-l`并将其注入到指定的进程 ID 中`-p`。

```
frida -U -l java_class_listing.js -p <pid>

// Output
[Huawei Nexus 6P::sg.vantagepoint.helloworldjni]->
...

com.scottyab.rootbeer.sample.MainActivity
{
  "_name": "com.scottyab.rootbeer.sample.MainActivity",
  "_methods": [
  ...
    "beerView",
    "checkRootImageViewList",
    "floatingActionButton",
    "infoDialog",
    "isRootedText",
    "isRootedTextDisclaimer",
    "mActivity",
    "GITHUB_LINK"
  ],
  "_fields": [
    "public static final int android.app.Activity.DEFAULT_KEYS_DIALER",
...
```

考虑到输出的冗长，可以通过编程方式过滤掉系统类，使输出更具可读性并与用例相关。

##### 获取加载的库[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#getting-loaded-libraries)

您可以使用`Process`命令直接从 Frida CLI 检索进程相关信息。在`Process`命令中，该函数`enumerateModules`列出了加载到进程内存中的库。

```
[Huawei Nexus 6P::sg.vantagepoint.helloworldjni]-> Process.enumerateModules()
[
    {
        "base": "0x558a442000",
        "name": "app_process64",
        "path": "/system/bin/app_process64",
        "size": 32768
    },
    {
        "base": "0x78bc984000",
        "name": "libandroid_runtime.so",
        "path": "/system/lib64/libandroid_runtime.so",
        "size": 2011136
    },
...
```

#### 方法Hook[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-hooking)

##### XPOSED[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#xposed)

假设您正在测试一个应用程序，该应用程序在您的 root 设备上顽固地退出。您反编译应用程序并发现以下高度可疑的方法：

```
package com.example.a.b

public static boolean c() {
  int v3 = 0;
  boolean v0 = false;

  String[] v1 = new String[]{"/sbin/", "/system/bin/", "/system/xbin/", "/data/local/xbin/",
    "/data/local/bin/", "/system/sd/xbin/", "/system/bin/failsafe/", "/data/local/"};

    int v2 = v1.length;

    for(int v3 = 0; v3 < v2; v3++) {
      if(new File(String.valueOf(v1[v3]) + "su").exists()) {
         v0 = true;
         return v0;
      }
    }

    return v0;
}
```

此方法遍历目录列表，如果在其中任何目录中找到二进制文件，则返回`true`（设备已根目录） 。`su`像这样的检查很容易停用所有你需要做的就是用返回“false”的东西替换代码。使用 Xposed 模块Hook方法是一种方法（有关 Xposed 安装和基础知识的更多详细信息，请参阅“Android 基本安全测试”）。

该方法 `XposedHelpers.findAndHookMethod`允许您覆盖现有的类方法。通过查看反编译后的源码，可以发现执行检查的方法是`c`. 此方法位于类中`com.example.a.b`。下面是一个 Xposed 模块，它覆盖了函数，因此它总是返回 false：

```
package com.awesome.pentestcompany;

import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class DisableRootCheck implements IXposedHookLoadPackage {

    public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals("com.example.targetapp"))
            return;

        findAndHookMethod("com.example.a.b", lpparam.classLoader, "c", new XC_MethodHook() {
            @Override

            protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                XposedBridge.log("Caught root check!");
                param.setResult(false);
            }

        });
    }
}
```

就像常规的 Android 应用程序一样，Xposed 模块是使用 Android Studio 开发和部署的。Xposed模块的编写、编译、安装等更多细节，可参考其作者[rovo89](https://www.xda-developers.com/rovo89-updates-on-the-situation-regarding-xposed-for-nougat/)提供的教程。

##### Frida[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#frida)

我们将使用 Frida 解决[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)，并演示我们如何轻松绕过 root 检测并从应用程序中提取秘密数据。

当您在模拟器或已获得 root 权限的设备上启动 crackme 应用程序时，您会发现它会显示一个对话框并在您按下“确定”后立即退出，因为它检测到 root：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/crackme-frida-1.png)

让我们看看如何防止这种情况发生。

主要方法（使用 CFR 反编译）如下所示：

```
package sg.vantagepoint.uncrackable1;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.Editable;
import android.view.View;
import android.widget.EditText;
import sg.vantagepoint.a.b;
import sg.vantagepoint.a.c;
import sg.vantagepoint.uncrackable1.a;

public class MainActivity
extends Activity {
    private void a(String string) {
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        alertDialog.setTitle((CharSequence)string);
        alertDialog.setMessage((CharSequence)"This is unacceptable. The app is now going to exit.");
        alertDialog.setButton(-3, (CharSequence)"OK", new DialogInterface.OnClickListener(){

            public void onClick(DialogInterface dialogInterface, int n) {
                System.exit((int)0);
            }
        });
        alertDialog.setCancelable(false);
        alertDialog.show();
    }

    protected void onCreate(Bundle bundle) {
        if (c.a() || c.b() || c.c()) {
            this.a("Root detected!");
        }
        if (b.a(this.getApplicationContext())) {
            this.a("App is debuggable!");
        }
        super.onCreate(bundle);
        this.setContentView(2130903040);
    }

    /*
     * Enabled aggressive block sorting
     */
    public void verify(View object) {
        object = ((EditText)this.findViewById(2130837505)).getText().toString();
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        if (a.a((String)object)) {
            alertDialog.setTitle((CharSequence)"Success!");
            object = "This is the correct secret.";
        } else {
            alertDialog.setTitle((CharSequence)"Nope...");
            object = "That's not it. Try again.";
        }
        alertDialog.setMessage((CharSequence)object);
        alertDialog.setButton(-3, (CharSequence)"OK", new DialogInterface.OnClickListener(){

            public void onClick(DialogInterface dialogInterface, int n) {
                dialogInterface.dismiss();
            }
        });
        alertDialog.show();
    }
}
```

请注意方法中的“Root detected”消息`onCreate`和前面语句中调用的各种方法`if`（执行实际的根检查）。还要注意来自类的第一个方法的“这是不可接受的...”消息`private void a`。显然，这个方法显示对话框。方法调用中有一个`alertDialog.onClickListener`回调集，它在成功检测`setButton`到根后关闭应用程序。使用 Frida，您可以通过Hook方法或其中的回调`System.exit`来防止应用程序退出。`MainActivity.a`下面的示例显示了如何Hook`MainActivity.a`并防止它结束应用程序。

```
setImmediate(function() { //prevent timeout
    console.log("[*] Starting script");

    Java.perform(function() {
      var mainActivity = Java.use("sg.vantagepoint.uncrackable1.MainActivity");
      mainActivity.a.implementation = function(v) {
         console.log("[*] MainActivity.a called");
      };
      console.log("[*] MainActivity.a modified");

    });
});
```

将您的代码包装在函数`setImmediate`中以防止超时（您可能需要也可能不需要这样做），然后调用`Java.perform`以使用 Frida 的方法来处理 Java。然后检索类的包装器`MainActivity`并覆盖其`a`方法。与原始版本不同，新版本`a`仅写入控制台输出并且不会退出应用程序。另一种解决方案是Hook接口`onClick`的方法`OnClickListener`。您可以覆盖该`onClick`方法并防止它通过`System.exit`调用结束应用程序。如果您想注入自己的 Frida 脚本，它应该`AlertDialog`完全禁用或更改该`onClick`方法的行为，以便在您单击“确定”时应用程序不会退出。

将上面的脚本另存为`uncrackable1.js`并加载它：

```
frida -U -f owasp.mstg.uncrackable1 -l uncrackable1.js --no-pause
```

在您看到“MainActivity.a modified”消息后，应用程序将不再退出。

您现在可以尝试输入“秘密字符串”。但是你从哪里得到它？

如果您查看 class `sg.vantagepoint.uncrackable1.a`，您可以看到与您的输入进行比较的加密字符串：

```
package sg.vantagepoint.uncrackable1;

import android.util.Base64;
import android.util.Log;

public class a {
    public static boolean a(String string) {

        byte[] arrby = Base64.decode((String)"5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc=", (int)0);

        try {
            arrby = sg.vantagepoint.a.a.a(a.b("8d127684cbc37c17616d806cf50473cc"), arrby);
        }
        catch (Exception exception) {
            StringBuilder stringBuilder = new StringBuilder();
            stringBuilder.append("AES error:");
            stringBuilder.append(exception.getMessage());
            Log.d((String)"CodeCheck", (String)stringBuilder.toString());
            arrby = new byte[]{};
        }
        return string.equals((Object)new String(arrby));
    }

    public static byte[] b(String string) {
        int n = string.length();
        byte[] arrby = new byte[n / 2];
        for (int i = 0; i < n; i += 2) {
            arrby[i / 2] = (byte)((Character.digit((char)string.charAt(i), (int)16) << 4) + Character.digit((char)string.charAt(i + 1), (int)16));
        }
        return arrby;
    }
}
```

查看方法`string.equals`末尾的比较和上面块`a`中字符串的创建`arrby`。是函数的返回值。comparison 将您的输入与 进行比较。所以我们想要的返回值`try``arrby``sg.vantagepoint.a.a.a``string.equals``arrby``sg.vantagepoint.a.a.a.`

无需逆向解密例程来重建密钥，您可以简单地忽略应用程序中的所有解密逻辑并Hook`sg.vantagepoint.a.a.a`函数以捕获其返回值。这是防止在 root 上退出并拦截秘密字符串解密的完整脚本：

```
setImmediate(function() { //prevent timeout
    console.log("[*] Starting script");

    Java.perform(function() {
        var mainActivity = Java.use("sg.vantagepoint.uncrackable1.MainActivity");
        mainActivity.a.implementation = function(v) {
           console.log("[*] MainActivity.a called");
        };
        console.log("[*] MainActivity.a modified");

        var aaClass = Java.use("sg.vantagepoint.a.a");
        aaClass.a.implementation = function(arg1, arg2) {
        var retval = this.a(arg1, arg2);
        var password = '';
        for(var i = 0; i < retval.length; i++) {
            password += String.fromCharCode(retval[i]);
        }

        console.log("[*] Decrypted: " + password);
            return retval;
        };
        console.log("[*] sg.vantagepoint.a.a.a modified");
    });
});
```

在 Frida 中运行脚本并在控制台中看到“[*] sg.vantagepoint.aaa modified”消息后，为“secret string”输入一个随机值并按验证。您应该得到类似于以下内容的输出：

```
$ frida -U -f owasp.mstg.uncrackable1 -l uncrackable1.js --no-pause

[*] Starting script
[USB::Android Emulator 5554::sg.vantagepoint.uncrackable1]-> [*] MainActivity.a modified
[*] sg.vantagepoint.a.a.a modified
[*] MainActivity.a called.
[*] Decrypted: I want to believe
```

钩子函数输出解密的字符串。您提取了秘密字符串，而不必深入研究应用程序代码及其解密例程。

您现在已经了解了 Android 上静态/动态分析的基础知识。当然，*真正*学习它的唯一方法是亲身体验：在 Android Studio 中构建您自己的项目，观察您的代码如何被翻译成字节码和原生代码，并尝试破解我们的挑战。

在其余部分中，我们将介绍一些高级主题，包括进程探索、内核模块和动态执行。

#### 过程探索[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#process-exploration)

在测试应用程序时，进程探索可以让测试人员深入了解应用程序进程内存。它可以通过Runtime(运行时)检测来实现，并允许执行以下任务：

- 检索内存映射和加载的库。
- 搜索特定数据的出现。
- 经过查找，得到内存映射中某个偏移量的位置。
- 执行内存转储并*离线*检查或反向工程二进制数据。
- 在Runtime(运行时)对Native库(NATIVE LIBRARIES)进行逆向工程。

如您所见，这些被动任务帮助我们收集信息。此信息通常用于其他技术，例如方法Hook。

在以下部分中，您将使用[r2frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#r2frida)直接从应用程序Runtime(运行时)检索信息。请参考[r2frida官方安装说明](https://github.com/nowsecure/r2frida/blob/master/README.md#installation)。首先打开一个 r2frida 会话到目标应用程序（例如[HelloWorld JNI](https://github.com/OWASP/owasp-mastg/raw/master/Samples/Android/01_HelloWorld-JNI/HelloWord-JNI.apk) APK），该应用程序应该在您的 Android 手机上运行（通过 USB 连接）。使用以下命令：

```
r2 frida://usb//sg.vantagepoint.helloworldjni
```

> 查看所有选项`r2 frida://?`。

一旦进入 r2frida 会话，所有命令都以`\`. 例如，在 radare2 中你会运行`i`以显示二进制信息，但在 r2frida 中你会使用`\i`.

##### 内存映射和检查[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-maps-and-inspection)

您可以通过运行检索应用程序的内存映射`\dm`，Android 中的输出可能会很长（例如 1500 到 2000 行之间），以缩小搜索范围并仅查看直接属于应用程序的内容`~`，按包名称应用 grep () `\dm~<package_name>`：

```
[0x00000000]> \dm~sg.vantagepoint.helloworldjni
0x000000009b2dc000 - 0x000000009b361000 rw- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x000000009b361000 - 0x000000009b36e000 --- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x000000009b36e000 - 0x000000009b371000 rw- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x0000007d103be000 - 0x0000007d10686000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.vdex
0x0000007d10dd0000 - 0x0000007d10dee000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d10dee000 - 0x0000007d10e2b000 r-x /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d10e3a000 - 0x0000007d10e3b000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d10e3b000 - 0x0000007d10e3c000 rw- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d1c499000 - 0x0000007d1c49a000 r-x /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4a9000 - 0x0000007d1c4aa000 r-- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4aa000 - 0x0000007d1c4ab000 rw- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c516000 - 0x0000007d1c54d000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007dbd23c000 - 0x0000007dbd247000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007dc05db000 - 0x0000007dc05dc000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art
```

当您搜索或探索应用程序内存时，您始终可以在内存映射中验证您在每个时刻所处的位置（您当前的偏移量所在的位置）。您无需注意并搜索此列表中的内存地址，只需运行`\dm.`. 您将在下一节“内存中搜索”中找到示例。

如果您只对应用加载的模块（二进制文件和库）感兴趣，可以使用以下命令`\il`列出所有模块：

```
[0x00000000]> \il
0x000000558b1fd000 app_process64
0x0000007dbc859000 libandroid_runtime.so
0x0000007dbf5d7000 libbinder.so
0x0000007dbff4d000 libcutils.so
0x0000007dbfd13000 libhwbinder.so
0x0000007dbea00000 liblog.so
0x0000007dbcf17000 libnativeloader.so
0x0000007dbf21c000 libutils.so
0x0000007dbde4b000 libc++.so
0x0000007dbe09b000 libc.so
...
0x0000007d10dd0000 base.odex
0x0000007d1c499000 libnative-lib.so
0x0000007d2354e000 frida-agent-64.so
0x0000007dc065d000 linux-vdso.so.1
0x0000007dc065f000 linker64
```

如您所料，您可以将库的地址与内存映射相关联：例如，应用程序的Native库(NATIVE LIBRARIES)位于 ，`0x0000007d1c499000`优化的 dex (base.odex) 位于`0x0000007d10dd0000`。

您也可以使用objection来显示相同的信息。

```
$ objection --gadget sg.vantagepoint.helloworldjni explore

sg.vantagepoint.helloworldjni on (google: 8.1.0) [usb] # memory list modules
Save the output by adding `--json modules.json` to this command

Name                                             Base          Size                  Path
-----------------------------------------------  ------------  --------------------  --------------------------------------------------------------------
app_process64                                    0x558b1fd000  32768 (32.0 KiB)      /system/bin/app_process64
libandroid_runtime.so                            0x7dbc859000  1982464 (1.9 MiB)     /system/lib64/libandroid_runtime.so
libbinder.so                                     0x7dbf5d7000  557056 (544.0 KiB)    /system/lib64/libbinder.so
libcutils.so                                     0x7dbff4d000  77824 (76.0 KiB)      /system/lib64/libcutils.so
libhwbinder.so                                   0x7dbfd13000  163840 (160.0 KiB)    /system/lib64/libhwbinder.so
base.odex                                        0x7d10dd0000  442368 (432.0 KiB)    /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
libnative-lib.so                                 0x7d1c499000  73728 (72.0 KiB)      /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
```

您甚至可以直接在 Android 文件系统中查看该二进制文件的大小和路径。

##### 内存搜索[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#in-memory-search)

内存中搜索是一种非常有用的技术，可用于测试应用程序内存中可能存在的敏感数据。

请参阅 r2frida 的搜索命令帮助 ( `\/?`) 以了解搜索命令并获取选项列表。以下仅显示其中的一个子集：

```
[0x00000000]> \/?
 /      search
 /j     search json
 /w     search wide
 /wj    search wide json
 /x     search hex
 /xj    search hex json
...
```

您可以使用搜索设置调整搜索`\e~search`。例如，`\e search.quiet=true;`将只打印结果并隐藏搜索进度：

```
[0x00000000]> \e~search
e search.in=perm:r--
e search.quiet=false
```

现在，我们将继续使用默认值并专注于字符串搜索。这个应用程序实际上非常简单，它从其Native库(NATIVE LIBRARIES)中加载字符串“Hello from C++”并将其显示给我们。您可以从搜索“Hello”开始，然后查看 r2frida 找到的内容：

```
[0x00000000]> \/ Hello
Searching 5 bytes: 48 65 6c 6c 6f
...
hits: 11
0x13125398 hit0_0 HelloWorldJNI
0x13126b90 hit0_1 Hello World!
0x1312e220 hit0_2 Hello from C++
0x70654ec5 hit0_3 Hello
0x7d1c499560 hit0_4 Hello from C++
0x7d1c4a9560 hit0_5 Hello from C++
0x7d1c51cef9 hit0_6 HelloWorldJNI
0x7d30ba11bc hit0_7 Hello World!
0x7d39cd796b hit0_8 Hello.java
0x7d39d2024d hit0_9 Hello;
0x7d3aa4d274 hit0_10 Hello
```

现在您想知道这些地址实际上在哪里。您可以通过为匹配 glob`\dm.`的所有命中运行命令来执行此操作：`@@``hit0_*`

```
[0x00000000]> \dm.@@ hit0_*
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x00000000703c2000 - 0x00000000709b5000 rw- /data/dalvik-cache/arm64/system@framework@boot-framework.art
0x0000007d1c499000 - 0x0000007d1c49a000 r-x /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4a9000 - 0x0000007d1c4aa000 r-- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c516000 - 0x0000007d1c54d000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d396bc000 - 0x0000007d3a998000 r-- /system/framework/arm64/boot-framework.vdex
0x0000007d396bc000 - 0x0000007d3a998000 r-- /system/framework/arm64/boot-framework.vdex
0x0000007d3a998000 - 0x0000007d3aa9c000 r-- /system/framework/arm64/boot-ext.vdex
```

此外，您可以搜索出现的[宽版本字符串](https://en.wikipedia.org/wiki/Wide_character)( `\/w`)，并再次检查它们的内存区域：

```
[0x00000000]> \/w Hello
Searching 10 bytes: 48 00 65 00 6c 00 6c 00 6f 00
hits: 6
0x13102acc hit1_0 480065006c006c006f00
0x13102b9c hit1_1 480065006c006c006f00
0x7d30a53aa0 hit1_2 480065006c006c006f00
0x7d30a872b0 hit1_3 480065006c006c006f00
0x7d30bb9568 hit1_4 480065006c006c006f00
0x7d30bb9a68 hit1_5 480065006c006c006f00

[0x00000000]> \dm.@@ hit1_*
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
```

它们与前面的字符串之一 ( `0x0000007d30a00000`) 位于相同的 rw- 区域中。请注意，搜索宽版本的字符串有时是找到它们的唯一方法，您将在下一节中看到。

内存中搜索对于快速了解某些数据是否位于主应用程序二进制文件、共享库或其他区域中非常有用。您还可以使用它来测试应用程序关于数据如何保存在内存中的行为。例如，您可以分析一个执行登录并搜索用户密码的应用程序。另外，您可以在登录完成后检查您是否仍然可以在内存中找到密码，以验证该敏感数据是否在使用后从内存中擦除。

此外，您可以使用这种方法来定位和提取加密密钥。例如，在应用程序加密/解密数据和处理内存中的密钥的情况下，而不是使用 AndroidKeyStore API。有关详细信息，请参阅“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”一章中的“[测试密钥管理](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-key-management-mstg-storage-1-mstg-crypto-1-and-mstg-crypto-5)”部分。

##### 内存转储[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-dump)

[您可以使用objection](https://github.com/sensepost/objection)和[Fridump](https://github.com/Nightbringer21/fridump)转储应用程序的进程内存。要在非 root 设备上利用这些工具，Android 应用程序必须重新打包`frida-gadget.so`并重新签名。这个过程的详细解释在“[非 Root 设备上的动态分析](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#dynamic-analysis-on-non-rooted-devices)”部分。要在 Root 手机上使用这些工具，只需安装并运行 frida-server。

> 注意：使用这些工具时，您可能会遇到一些通常可以忽略的内存访问冲突错误。这些工具会注入 Frida 代理并尝试转储应用程序的所有映射内存，而不管访问权限（读/写/执行）如何。因此，当注入的 Frida 代理试图读取一个不可读的区域时，它会返回相应的*memory access violation errors*。有关更多详细信息，请参阅上一节“内存映射和检查”。

如果反对，可以使用命令转储设备上正在运行的进程的所有内存`memory dump all`。

```
$ objection --gadget sg.vantagepoint.helloworldjni explore

sg.vantagepoint.helloworldjni on (google: 8.1.0) [usb] # memory dump all /Users/foo/memory_Android/memory

Will dump 719 rw- images, totalling 1.6 GiB
Dumping 1002.8 MiB from base: 0x14140000  [------------------------------------]    0%  00:11:03(session detach message) process-terminated
Dumping 8.0 MiB from base: 0x7fc753e000  [####################################]  100%
Memory dumped to file: /Users/foo/memory_Android/memory
```

> 在这种情况下，出现了一个错误，这可能是由于我们已经预料到的内存访问冲突。只要我们能够在文件系统中看到提取的转储，就可以安全地忽略此错误。如果您有任何问题，第一步是`-d`在运行反对时启用调试标志，或者，如果这没有帮助，请在[反对的 GitHub](https://github.com/sensepost/objection/issues)中提出问题。

接下来，我们可以使用 radare2 找到“Hello from C++”字符串：

```
$ r2 /Users/foo/memory_Android/memory
[0x00000000]> izz~Hello from
1136 0x00065270 0x00065270  14  15 () ascii Hello from C++
```

或者你可以使用 Fridump。这一次，我们将输入一个字符串，看看能否在内存转储中找到它。为此，打开[MASTG Hacking Playground](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#mastg-hacking-playground)应用程序，导航至“OMTG_DATAST_002_LOGGING”并在密码字段中输入“owasp-mstg”。接下来，运行 Fridump：

```
python3 fridump.py -U sg.vp.owasp_mobile.omtg_android -s

Current Directory: /Users/foo/git/fridump
Output directory is set to: /Users/foo/git/fridump/dump
Starting Memory dump...
Oops, memory access violation!-------------------------------] 0.28% Complete
Progress: [##################################################] 99.58% Complete
Running strings on all files:
Progress: [##################################################] 100.0% Complete

Finished!
```

> `-v`提示：如果您想查看更多详细信息（例如引发内存访问冲突的区域），请通过包含标志来启用详细信息。

它需要一段时间才能完成，您将在转储文件夹中获得一组 *.data 文件。添加`-s`标志时，所有字符串都从转储的原始内存文件中提取并添加到文件`strings.txt`中，该文件也存储在转储目录中。

```
ls dump/
dump/1007943680_dump.data dump/357826560_dump.data  dump/630456320_dump.data ... strings.txt
```

最后，在转储目录中搜索输入字符串：

```
$ grep -nri owasp-mstg dump/
Binary file dump//316669952_dump.data matches
Binary file dump//strings.txt matches
```

“owasp-mstg”字符串可以在其中一个转储文件以及已处理的字符串文件中找到。

##### Runtime(运行时)逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#runtime-reverse-engineering)

Runtime(运行时)逆向工程可以看作是实时版本的逆向工程，您没有主机的二进制数据。相反，您将直接从应用程序的内存中分析它。

我们将继续使用 HelloWorld JNI 应用程序，使用 r2frida 打开一个会话，`r2 frida://usb//sg.vantagepoint.helloworldjni`您可以使用以下`\i`命令显示目标二进制信息：

```
[0x00000000]> \i
arch                arm
bits                64
os                  linux
pid                 13215
uid                 10096
objc                false
runtime             V8
java                true
cylang              false
pageSize            4096
pointerSize         8
codeSigningPolicy   optional
isDebuggerAttached  false
cwd                 /
dataDir             /data/user/0/sg.vantagepoint.helloworldjni
codeCacheDir        /data/user/0/sg.vantagepoint.helloworldjni/code_cache
extCacheDir         /storage/emulated/0/Android/data/sg.vantagepoint.helloworldjni/cache
obbDir              /storage/emulated/0/Android/obb/sg.vantagepoint.helloworldjni
filesDir            /data/user/0/sg.vantagepoint.helloworldjni/files
noBackupDir         /data/user/0/sg.vantagepoint.helloworldjni/no_backup
codePath            /data/app/sg.vantagepoint.helloworldjni-1/base.apk
packageName         sg.vantagepoint.helloworldjni
androidId           c92f43af46f5578d
cacheDir            /data/local/tmp
jniEnv              0x7d30a43c60
```

搜索某个模块的所有符号`\is <lib>`，例如`\is libnative-lib.so`。

```
[0x00000000]> \is libnative-lib.so

[0x00000000]>
```

在这种情况下是空的。或者，您可能更愿意查看导入/导出。例如，列出导入`\ii <lib>`：

```
[0x00000000]> \ii libnative-lib.so
0x7dbe1159d0 f __cxa_finalize /system/lib64/libc.so
0x7dbe115868 f __cxa_atexit /system/lib64/libc.so
```

并列出出口`\iE <lib>`：

```
[0x00000000]> \iE libnative-lib.so
0x7d1c49954c f Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI
```

> 对于大型二进制文件，建议通过附加 , 将输出传输到内部 less 程序`~..`，即`\ii libandroid_runtime.so~..`（如果不是，对于此二进制文件，您将在终端上打印近 2500 行）。

接下来您可能想要查看的是**当前加载**的Java 类：

```
[0x00000000]> \ic~sg.vantagepoint.helloworldjni
sg.vantagepoint.helloworldjni.MainActivity
```

列出类字段：

```
[0x00000000]> \ic sg.vantagepoint.helloworldjni.MainActivity~sg.vantagepoint.helloworldjni
public native java.lang.String sg.vantagepoint.helloworldjni.MainActivity.stringFromJNI()
public sg.vantagepoint.helloworldjni.MainActivity()
```

请注意，我们已按包名称进行过滤，因为`MainActivity`它包含 Android`Activity`类中的所有方法。

您还可以显示有关类加载器的信息：

```
[0x00000000]> \icL
dalvik.system.PathClassLoader[
 DexPathList[
  [
   directory "."]
  ,
  nativeLibraryDirectories=[
   /system/lib64,
    /vendor/lib64,
    /system/lib64,
    /vendor/lib64]
  ]
 ]
java.lang.BootClassLoader@b1f1189dalvik.system.PathClassLoader[
 DexPathList[
  [
   zip file "/data/app/sg.vantagepoint.helloworldjni-1/base.apk"]
  ,
  nativeLibraryDirectories=[
   /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64,
    /data/app/sg.vantagepoint.helloworldjni-1/base.apk!/lib/arm64-v8a,
    /system/lib64,
    /vendor/lib64]
  ]
 ]
```

接下来，假设您对 libnative-lib.so 导出的方法感兴趣`0x7d1c49954c f Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI`。您可以使用 查找该地址`s 0x7d1c49954c`，分析该函数`af`并打印其反汇编的 10 行`pd 10`：

```
[0x7d1c49954c]> pdf
            ;-- sym.fun.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI:
╭ (fcn) fcn.7d1c49954c 18
│   fcn.7d1c49954c (int32_t arg_40f942h);
│           ; arg int32_t arg_40f942h @ x29+0x40f942
│           0x7d1c49954c      080040f9       ldr x8, [x0]
│           0x7d1c499550      01000090       adrp x1, 0x7d1c499000
│           0x7d1c499554      21801591       add x1, x1, 0x560         ; hit0_4
│           0x7d1c499558      029d42f9       ldr x2, [x8, 0x538]       ; [0x538:4]=-1 ; 1336
│           0x7d1c49955c      4000           invalid
```

请注意，标记为 的行`; hit0_4`对应于我们之前找到的字符串：`0x7d1c499560 hit0_4 Hello from C++`。

要了解更多信息，请参阅[r2frida wiki](https://github.com/enovella/r2frida-wiki/blob/master/README.md)。

## 为逆向工程定制 Android[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-android-for-reverse-engineering)

在真实设备上工作具有优势，特别是对于交互式、调试器支持的静态/动态分析。例如，在真实设备上工作会更快。此外，在真实设备上运行目标应用程序不太可能触发防御。在战略点检测实时环境可为您提供有用的跟踪功能和操纵环境的能力，这将帮助您绕过应用程序可能实施的任何防篡改防御措施。

### 自定义 RAMDisk[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-the-ramdisk)

Initramfs 是存储在引导映像中的小型 CPIO 存档。它包含一些在启动时需要的文件，在安装实际的根文件系统之前。在 Android 上，initramfs 会无限期地挂载。它包含一个重要的配置文件 default.prop，它定义了一些基本的系统属性。更改此文件可以使 Android 环境更容易进行逆向工程。出于我们的目的，default.prop 中最重要的设置是`ro.debuggable`和`ro.secure`。

```
$ cat /default.prop
#
# ADDITIONAL_DEFAULT_PROPERTIES
#
ro.secure=1
ro.allow.mock.location=0
ro.debuggable=1
ro.zygote=zygote32
persist.radio.snapshot_enabled=1
persist.radio.snapshot_timer=2
persist.radio.use_cc_names=true
persist.sys.usb.config=mtp
rild.libpath=/system/lib/libril-qc-qmi-1.so
camera.disable_zsl_mode=1
ro.adb.secure=1
dalvik.vm.dex2oat-Xms=64m
dalvik.vm.dex2oat-Xmx=512m
dalvik.vm.image-dex2oat-Xms=64m
dalvik.vm.image-dex2oat-Xmx=64m
ro.dalvik.vm.native.bridge=0
```

设置`ro.debuggable`为“1”使所有正在运行的应用程序都可调试（即，调试器线程将在每个进程中运行），而不管`android:debuggable`Android Manifest 中的属性值。设置`ro.secure`为“0”会导致 adbd 以 root 身份运行。要在任何 Android 设备上修改 initrd，请使用 TWRP 备份原始引导映像或使用以下命令转储它：

```
adb shell cat /dev/mtd/mtd0 >/mnt/sdcard/boot.img
adb pull /mnt/sdcard/boot.img /tmp/boot.img
```

要提取引导映像的内容，请使用 Krzysztof Adamski 的操作指南中所述的 abootimg 工具：

```
mkdir boot
cd boot
../abootimg -x /tmp/boot.img
mkdir initrd
cd initrd
cat ../initrd.img | gunzip | cpio -vid
```

注意写入bootimg.cfg的引导参数；引导新内核和 ramdisk 时需要它们。

```
$ ~/Desktop/abootimg/boot$ cat bootimg.cfg
bootsize = 0x1600000
pagesize = 0x800
kerneladdr = 0x8000
ramdiskaddr = 0x2900000
secondaddr = 0xf00000
tagsaddr = 0x2700000
name =
cmdline = console=ttyHSL0,115200,n8 androidboot.hardware=hammerhead user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1
```

修改 default.prop 并打包你的新 ramdisk：

```
cd initrd
find . | cpio --create --format='newc' | gzip > ../myinitd.img
```

### 自定义 Android 内核[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-the-android-kernel)

Android 内核是逆向工程师的强大盟友。尽管常规的 Android 应用程序受到无可救药的限制和沙盒化，但作为逆向者，您可以按照自己的意愿自定义和更改操作系统和内核的行为。这给您带来了优势，因为大多数完整性检查和防篡改功能最终都依赖于内核执行的服务。部署一个滥用这种信任并且毫不掩饰地对自身和环境撒谎的内核，对于击败恶意软件作者（或普通开发人员）可以向您发起的大多数逆向防御大有帮助。

Android 应用程序有多种方式与操作系统交互。通过 Android 应用程序框架的 API 进行交互是标准的。然而，在最低层，许多重要的功能（例如分配内存和访问文件）被转换为老式的 Linux 系统调用。在 ARM Linux 上，系统调用是通过触发软件中断的 SVC 指令调用的。此中断调用`vector_swi`内核函数，然后内核函数使用系统调用编号作为函数指针表（在 Android 上称为 sys_call_table）的偏移量。

拦截系统调用最直接的方法就是将自己的代码注入内核内存，然后覆盖系统调用表中原有的函数，重定向执行。不幸的是，当前的 Android 内核会强制执行内存限制来防止这种情况发生。具体来说，库存棒棒糖和棉花糖内核是在启用 CONFIG_STRICT_MEMORY_RWX 选项的情况下构建的。这可以防止写入标记为只读的内核内存区域，因此任何修补内核代码或系统调用表的尝试都会导致分段错误并重新启动。要解决这个问题，请构建您自己的内核。然后您可以停用此保护并进行许多其他有用的自定义以简化逆向工程。如果您定期对 Android 应用程序进行逆向，那么构建您自己的逆向工程沙箱是轻而易举的事。

对于黑客攻击，我推荐支持 AOSP 的设备。谷歌的 Nexus 智能手机和平板电脑是最合乎逻辑的候选者，因为从 AOSP 构建的内核和系统组件可以毫无问题地运行在它们上面。索尼的Xperia系列也以开放着称。要构建 AOSP 内核，您需要一个工具链（一组用于交叉编译源代码的程序）和相应版本的内核源代码。按照 Google 的说明为给定的设备和 Android 版本识别正确的 git 存储库和分支。

https://source.android.com/source/building-kernels.html#id-version

例如，要获得与 Nexus 5 兼容的 Lollipop 的内核源代码，您需要克隆`msm`存储库并检查其中一个`android-msm-hammerhead`分支（hammerhead 是 Nexus 5 的代号，找到正确的分支是一件令人困惑的事情）。下载源代码后，使用命令创建默认内核配置`make hammerhead_defconfig`（将“hammerhead”替换为目标设备）。

```
git clone https://android.googlesource.com/kernel/msm.git
cd msm
git checkout origin/android-msm-hammerhead-3.4-lollipop-mr1
export ARCH=arm
export SUBARCH=arm
make hammerhead_defconfig
vim .config
```

我建议使用以下设置来添加可加载模块支持，启用最重要的跟踪功能，并打开内核内存以进行修补。

```
CONFIG_MODULES=Y
CONFIG_STRICT_MEMORY_RWX=N
CONFIG_DEVMEM=Y
CONFIG_DEVKMEM=Y
CONFIG_KALLSYMS=Y
CONFIG_KALLSYMS_ALL=Y
CONFIG_HAVE_KPROBES=Y
CONFIG_HAVE_KRETPROBES=Y
CONFIG_HAVE_FUNCTION_TRACER=Y
CONFIG_HAVE_FUNCTION_GRAPH_TRACER=Y
CONFIG_TRACING=Y
CONFIG_FTRACE=Y
CONFIG KDB=Y
```

完成编辑后保存 .config 文件，构建内核。

```
export ARCH=arm
export SUBARCH=arm
export CROSS_COMPILE=/path_to_your_ndk/arm-eabi-4.8/bin/arm-eabi-
make
```

您现在可以创建一个独立的工具链来交叉编译内核和后续任务。要为 Android 7.0（API 级别 24）创建工具链，请从 Android NDK 包运行 make-standalone-toolchain.sh：

```
cd android-ndk-rXXX
build/tools/make-standalone-toolchain.sh --arch=arm --platform=android-24 --install-dir=/tmp/my-android-toolchain
```

将 CROSS_COMPILE 环境变量设置为指向您的 NDK 目录并运行“make”来构建内核。

```
export CROSS_COMPILE=/tmp/my-android-toolchain/bin/arm-eabi-
make
```

### 引导自定义环境[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#booting-the-custom-environment)

在启动到新内核之前，请复制您设备的原始启动映像。找到引导分区：

```
root@hammerhead:/dev # ls -al /dev/block/platform/msm_sdcc.1/by-name/
lrwxrwxrwx root     root              1970-08-30 22:31 DDR -> /dev/block/mmcblk0p24
lrwxrwxrwx root     root              1970-08-30 22:31 aboot -> /dev/block/mmcblk0p6
lrwxrwxrwx root     root              1970-08-30 22:31 abootb -> /dev/block/mmcblk0p11
lrwxrwxrwx root     root              1970-08-30 22:31 boot -> /dev/block/mmcblk0p19
(...)
lrwxrwxrwx root     root              1970-08-30 22:31 userdata -> /dev/block/mmcblk0p28
```

然后将整个东西转储到一个文件中：

```
adb shell "su -c dd if=/dev/block/mmcblk0p19 of=/data/local/tmp/boot.img"
adb pull /data/local/tmp/boot.img
```

接下来，提取 ramdisk 和有关引导映像结构的信息。有多种工具可以做到这一点；我使用了 Gilles Grandou 的 abootimg 工具。安装该工具并在启动映像上运行以下命令：

```
abootimg -x boot.img
```

这应该在本地目录中创建文件 bootimg.cfg、initrd.img 和 zImage（您的原始内核）。

您现在可以使用 fastboot 来测试新内核。该`fastboot boot`命令允许您运行内核而无需实际刷新它（一旦您确定一切正常，您可以使用 fastboot flash 使更改永久生效，但您不必这样做）。使用以下命令以快速启动模式重启设备：

```
adb reboot bootloader
```

然后使用`fastboot boot`命令使用新内核启动 Android。除了新构建的内核和原始 ramdisk 之外，还指定内核偏移量、ramdisk 偏移量、标签偏移量和命令行（使用您提取的 bootimg.cfg 中列出的值）。

```
fastboot boot zImage-dtb initrd.img --base 0 --kernel-offset 0x8000 --ramdisk-offset 0x2900000 --tags-offset 0x2700000 -c "console=ttyHSL0,115200,n8 androidboot.hardware=hammerhead user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1"
```

系统现在应该正常启动。要快速验证正确的内核是否正在运行，请导航至**设置**->**关于手机**并检查**内核版本**字段。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/custom_kernel.jpg)

### 使用内核模块Hook系统调用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#system-call-hooking-with-kernel-modules)

系统调用Hook允许您攻击任何依赖于内核提供的功能的反逆向防御。自定义内核就位后，您现在可以使用 LKM 将其他代码加载到内核中。您还可以访问 /dev/kmem 接口，您可以使用该接口即时修补内核内存。这是一种经典的 Linux rootkit 技术，由 Dong-Hoon You 在 Phrack Magazine - “Android platform based linux kernel rootkit”2011 年 4 月 4 日针对 Android 进行了描述。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/syscall_hooking.jpg)

您首先需要 sys_call_table 的地址。幸运的是，它在 Android 内核中作为符号导出（iOS 逆向器就没那么幸运了）。您可以在 /proc/kallsyms 文件中查找地址：

```
$ adb shell "su -c echo 0 > /proc/sys/kernel/kptr_restrict"
$ adb shell cat /proc/kallsyms | grep sys_call_table
c000f984 T sys_call_table
```

这是编写内核模块所需的唯一内存地址。您可以使用从内核头文件中获取的偏移量来计算其他所有内容（希望您还没有删除它们）。

#### 示例：文件隐藏[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#example-file-hiding)

在本指南中，我们将使用内核模块来隐藏文件。在设备上创建一个文件，以便稍后隐藏它：

```
$ adb shell "su -c echo ABCD > /data/local/tmp/nowyouseeme"
$ adb shell cat /data/local/tmp/nowyouseeme
ABCD
```

是时候编写内核模块了。对于文件隐藏，您需要Hook用于打开（或检查文件是否存在）的系统调用之一。其中有很多：`open`, `openat`, `access`, `accessat`, `facessat`, `stat`,`fstat`等。现在，您将只Hook`openat`系统调用。这是 /bin/cat 程序在访问文件时使用的系统调用，因此该调用应该适合演示。

您可以在内核头文件 arch/arm/include/asm/unistd.h 中找到所有系统调用的函数原型。使用以下代码创建一个名为 kernel_hook.c 的文件：

```
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/unistd.h>
#include <linux/slab.h>
#include <asm/uaccess.h>

asmlinkage int (*real_openat)(int, const char __user*, int);

void **sys_call_table;

int new_openat(int dirfd, const char \__user* pathname, int flags)
{
  char *kbuf;
  size_t len;

  kbuf=(char*)kmalloc(256,GFP_KERNEL);
  len = strncpy_from_user(kbuf,pathname,255);

  if (strcmp(kbuf, "/data/local/tmp/nowyouseeme") == 0) {
    printk("Hiding file!\n");
    return -ENOENT;
  }

  kfree(kbuf);

  return real_openat(dirfd, pathname, flags);
}

int init_module() {

  sys_call_table = (void*)0xc000f984;
  real_openat = (void*)(sys_call_table[\__NR_openat]);

return 0;

}
```

要构建内核模块，您需要内核源代码和可用的工具链。由于您已经构建了一个完整的内核，所以一切就绪。创建一个包含以下内容的 Makefile：

```
KERNEL=[YOUR KERNEL PATH]
TOOLCHAIN=[YOUR TOOLCHAIN PATH]

obj-m := kernel_hook.o

all:
        make ARCH=arm CROSS_COMPILE=$(TOOLCHAIN)/bin/arm-eabi- -C $(KERNEL) M=$(shell pwd) CFLAGS_MODULE=-fno-pic modules

clean:
        make -C $(KERNEL) M=$(shell pwd) clean
```

运行`make`以编译代码，这将创建文件 kernel_hook.ko。将 kernel_hook.ko 复制到设备并使用`insmod`命令加载它。使用该`lsmod`命令验证模块是否已成功加载。

```
$ make
(...)
$ adb push kernel_hook.ko /data/local/tmp/
[100%] /data/local/tmp/kernel_hook.ko
$ adb shell su -c insmod /data/local/tmp/kernel_hook.ko
$ adb shell lsmod
kernel_hook 1160 0 [permanent], Live 0xbf000000 (PO)
```

现在您将访问 /dev/kmem 以`sys_call_table`用您新注入的函数的地址覆盖原始函数指针（这可以直接在内核模块中完成，但 /dev/kmem 提供了一种简单的方法来切换您的钩子和关闭）。为此，我们改编了 Dong-Hoon You 的 Phrack 文章中的代码。但是，您可以使用文件接口而不是`mmap`因为后者可能会导致内核崩溃。使用以下代码创建一个名为 kmem_util.c 的文件：

```
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <asm/unistd.h>
#include <sys/mman.h>

#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)

int kmem;
void read_kmem2(unsigned char *buf, off_t off, int sz)
{
  off_t offset; ssize_t bread;
  offset = lseek(kmem, off, SEEK_SET);
  bread = read(kmem, buf, sz);
  return;
}

void write_kmem2(unsigned char *buf, off_t off, int sz) {
  off_t offset; ssize_t written;
  offset = lseek(kmem, off, SEEK_SET);
  if (written = write(kmem, buf, sz) == -1) { perror("Write error");
    exit(0);
  }
  return;
}

int main(int argc, char *argv[]) {

  off_t sys_call_table;
  unsigned int addr_ptr, sys_call_number;

  if (argc < 3) {
    return 0;
  }

  kmem=open("/dev/kmem",O_RDWR);

  if(kmem<0){
    perror("Error opening kmem"); return 0;
  }

  sscanf(argv[1], "%x", &sys_call_table); sscanf(argv[2], "%d", &sys_call_number);
  sscanf(argv[3], "%x", &addr_ptr); char buf[256];
  memset (buf, 0, 256); read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("Original value: %02x%02x%02x%02x\n", buf[3], buf[2], buf[1], buf[0]);
  write_kmem2((void*)&addr_ptr,sys_call_table+(sys_call_number*4),4);
  read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("New value: %02x%02x%02x%02x\n", buf[3], buf[2], buf[1], buf[0]);
  close(kmem);

  return 0;
}
```

从 Android 5.0（API 级别 21）开始，所有可执行文件都必须使用 PIE 支持进行编译。使用预构建的工具链构建 kmem_util.c 并将其复制到设备：

```
/tmp/my-android-toolchain/bin/arm-linux-androideabi-gcc -pie -fpie -o kmem_util kmem_util.c
adb push kmem_util /data/local/tmp/
adb shell chmod 755 /data/local/tmp/kmem_util
```

在开始访问内核内存之前，您仍然需要知道系统调用表中的正确偏移量。系统调用在内核源代码中的`openat`unistd.h 中定义：

```
$ grep -r "__NR_openat" arch/arm/include/asm/unistd.h
\#define __NR_openat            (__NR_SYSCALL_BASE+322)
```

拼图的最后一块是您的替换地址 - `openat`。同样，您可以从 /proc/kallsyms 中获取此地址。

```
$ adb shell cat /proc/kallsyms | grep new_openat
bf000000 t new_openat    [kernel_hook]
```

现在您拥有覆盖`sys_call_table`条目所需的一切。kmem_util 的语法是：

```
./kmem_util <syscall_table_base_address> <offset> <func_addr>
```

以下命令修补`openat`系统调用表，使其指向您的新函数。

```
$ adb shell su -c /data/local/tmp/kmem_util c000f984 322 bf000000
Original value: c017a390
New value: bf000000
```

假设一切正常，/bin/cat 应该*看不到*该文件。

```
$ adb shell su -c cat /data/local/tmp/nowyouseeme
tmp-mksh: cat: /data/local/tmp/nowyouseeme: No such file or directory
```

瞧！文件“nowyouseeme”现在对所有*用户模式*进程有点隐藏。请注意，可以使用其他系统调用轻松找到该文件，并且您需要执行更多操作才能正确隐藏文件，包括Hook`stat`、`access`和其他系统调用。

文件隐藏当然只是冰山一角：您可以使用内核模块完成很多工作，包括绕过许多Root检测措施、完整性检查和反调试措施。您可以在 Bernhard Mueller 的 Hacking Soft Tokens 论文 [#mueller] 的“案例研究”部分找到更多示例。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#references)

- Bionic - https://github.com/android/platform_bionic
- 使用调试器攻击 Android 应用程序（2015 年 1 月 19 日）- https://blog.netspi.com/attacking-android-applications-with-debuggers/
- [#josse] Sébastien Josse，动态恶意软件重新编译（2014 年 1 月 6 日）- http://ieeexplore.ieee.org/document/6759227/
- Xposed for Nougat 开发更新 - https://www.xda-developers.com/rovo89-updates-on-the-situation-regarding-xposed-for-nougat/
- 基于 Android 平台的 Linux 内核 rootkit（2011 年 4 月 4 日 - Phrack 杂志）
- [#mueller] Bernhard Mueller，黑客软令牌。Android 上的高级逆向工程（2016 年）- https://packetstormsecurity.com/files/138504/HITB_Hacking_Soft_Tokens_v1.2.pdf
