# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 2 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p2.md`。

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
