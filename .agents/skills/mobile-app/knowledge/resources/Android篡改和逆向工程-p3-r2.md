# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 3 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p3.md`。

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
