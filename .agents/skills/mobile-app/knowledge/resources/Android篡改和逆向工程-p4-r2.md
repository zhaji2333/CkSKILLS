# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 4 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p4.md`。

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

