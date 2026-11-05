# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 4 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p4.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 4

> 分段 4/10。索引见 `Android篡改和逆向工程.md`。

## 承接

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

