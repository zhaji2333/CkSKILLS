# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 5 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p5.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 5

> 分段 5/10。索引见 `Android篡改和逆向工程.md`。

## 承接

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
