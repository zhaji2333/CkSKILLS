# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 3 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p3.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 3

> 分段 3/10。索引见 `Android篡改和逆向工程.md`。

## 承接


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
