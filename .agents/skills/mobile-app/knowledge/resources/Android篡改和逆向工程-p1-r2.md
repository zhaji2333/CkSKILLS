# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 1 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p1.md`。

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
