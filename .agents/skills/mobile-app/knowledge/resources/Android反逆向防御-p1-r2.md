# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 1 · part 2

> 分段 2/2。索引见 `Android反逆向防御-p1.md`。

          if(tempName.contains("supersu") || tempName.contains("superuser")){
            returnValue = true;
          }
        }
      }
      return returnValue;
    }
```

##### 检查已安装的应用程序包[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-installed-app-packages)

您可以使用 Android 包管理器获取已安装包的列表。以下软件包名称属于流行的Root工具：

```
com.thirdparty.superuser
eu.chainfire.supersu
com.noshufou.android.su
com.koushikdutta.superuser
com.zachspong.temprootremovejb
com.ramdroid.appquarantine
com.topjohnwu.magisk
```

##### 检查可写分区和系统目录[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-for-writable-partitions-and-system-directories)

系统目录上的异常权限可能表示设备是自定义的或已获得 root 权限的。尽管系统和数据目录通常以只读方式挂载，但您有时会发现在设备获得 root 后它们以读写方式挂载。寻找这些使用“rw”标志挂载的文件系统或尝试在数据目录中创建一个文件。

##### 检查自定义 ANDROID 版本[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-for-custom-android-builds)

检查测试版本和自定义 ROM 的迹象也很有帮助。一种方法是检查 BUILD 标签中的测试密钥，这通常[表示自定义 Android 图像](https://resources.infosecinstitute.com/android-hacking-security-part-8-root-detection-evasion//)。[检查 BUILD 标签如下](https://github.com/scottyab/rootbeer/blob/master/rootbeerlib/src/main/java/com/scottyab/rootbeer/RootBeer.java#L76)：

```
private boolean isTestKeyBuild()
{
String str = Build.TAGS;
if ((str != null) && (str.contains("test-keys")));
for (int i = 1; ; i = 0)
  return i;
}
```

缺少谷歌无线 (OTA) 证书是自定义 ROM 的另一个标志：在现有的 Android 构建中，[OTA 更新谷歌的公共证书](https://blog.netspi.com/android-root-detection-techniques/)。

#### 绕过Root检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-root-detection)

使用 jdb 、[DDMS](https://developer.android.com/studio/profile/monitor)和/或内核模块运行执行跟踪，`strace`以了解应用程序正在做什么。您通常会看到与操作系统的各种可疑交互，例如打开`su`以供阅读和获取进程列表。这些相互作用是Root检测的可靠标志。识别并停用Root检测机制，一次一个。如果您正在执行黑盒弹性评估，则禁用Root检测机制是您的第一步。

要绕过这些检查，您可以使用几种技术，其中大部分在“逆向工程和篡改”一章中介绍过：

- 重命名二进制文件。例如，在某些情况下，简单地重命名`su`二进制文件就足以阻止Root检测（尽管尽量不要破坏您的环境！）。
- 卸载`/proc`以防止读取进程列表。有时，不可用`/proc`就足以绕过此类检查。
- 使用 Frida 或 Xposed 在 Java 和Native层上挂接 API。这会隐藏文件和进程，隐藏文件内容，并返回应用程序请求的各种虚假值。
- 使用内核模块挂接低级 API。
- 修补应用程序以删除检查。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment)

检查Root检测机制，包括以下标准：

- 多种检测方法分散在整个应用程序中（而不是将所有内容都放在一个方法中）。
- Root检测机制在多个 API 层（Java API、Native库(NATIVE LIBRARIES)函数、汇编器/系统调用）上运行。
- 这些机制在某种程度上是原创的（它们不是从 StackOverflow 或其他来源复制和粘贴的）。

开发Root检测机制的绕过方法并回答以下问题：

- 是否可以使用 RootCloak 等标准工具轻松绕过这些机制？
- 处理Root检测是否需要静态/动态分析？
- 您需要编写自定义代码吗？
- 成功绕过这些机制需要多长时间？
- 您如何评估绕过这些机制的难度？

如果Root检测缺失或太容易被绕过，请根据上面列出的有效性标准提出建议。这些建议可能包括更多检测机制以及现有机制与其他防御措施的更好集成。

## 测试反调试检测（MSTG-RESILIENCE-2）[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-anti-debugging-detection-mstg-resilience-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_1)

调试是分析Runtime(运行时)应用程序行为的一种非常有效的方法。它允许逆向工程师单步执行代码、在任意点停止应用程序执行、检查变量状态、读取和修改内存等等。

反调试功能可以是预防性的或反应性的。顾名思义，预防性反调试首先防止调试器附加；反应式反调试涉及检测调试器并以某种方式对它们做出反应（例如，终止应用程序或触发隐藏行为）。适用“越多越好”的规则：为了最大限度地提高效率，防御者结合了多种预防和检测方法，这些方法在不同的 API 层上运行，并且分布在整个应用程序中。

正如在“逆向工程和篡改”一章中提到的，我们必须处理 Android 上的两种调试协议：我们可以使用 JDWP 在 Java 级别进行调试，或者通过基于 ptrace 的调试器在Native层进行调试。一个好的反调试方案应该抵御这两种类型的调试。

### JDWP反调试[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#jdwp-anti-debugging)

在“逆向工程和篡改”一章中，我们谈到了 JDWP，它是用于调试器和 Java 虚拟机之间通信的协议。`ro.debuggable`我们展示了通过修补其清单文件并更改为所有应用程序启用调试的系统属性，可以轻松为任何应用程序启用调试。让我们看看开发人员为检测和禁用 JDWP 调试器所做的一些事情。

#### 检查 ApplicationInfo 中的可调试标志[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-the-debuggable-flag-in-applicationinfo)

我们已经遇到了`android:debuggable`属性。Android Manifest 中的这个标志决定了 JDWP 线程是否为应用程序启动。它的值可以通过应用程序的`ApplicationInfo`对象以编程方式确定。如果设置了标志，则清单已被篡改并允许调试。

```
    public static boolean isDebuggable(Context context){

        return ((context.getApplicationContext().getApplicationInfo().flags & ApplicationInfo.FLAG_DEBUGGABLE) != 0);

    }
```

#### isDebuggerConnected[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#isdebuggerconnected)

虽然这对于逆向工程师来说很容易规避，但您可以使用`isDebuggerConnected`from`android.os.Debug`类来确定是否连接了调试器。

```
    public static boolean detectDebugger() {
        return Debug.isDebuggerConnected();
    }
```

通过访问 DvmGlobals 全局结构，可以通过Native代码调用相同的 API。

```
JNIEXPORT jboolean JNICALL Java_com_test_debugging_DebuggerConnectedJNI(JNIenv * env, jobject obj) {
    if (gDvm.debuggerConnected || gDvm.debuggerActive)
        return JNI_TRUE;
    return JNI_FALSE;
}
```

#### 计时器检查[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#timer-checks)

`Debug.threadCpuTimeNanos`指示当前线程执行代码的时间量。因为调试会减慢进程的执行速度，[所以可以根据执行时间的差异来猜测是否附加了调试器](https://www.yumpu.com/en/document/read/15228183/android-reverse-engineering-defenses-bluebox-labs)。

```
static boolean detect_threadCpuTimeNanos(){
  long start = Debug.threadCpuTimeNanos();

  for(int i=0; i<1000000; ++i)
    continue;

  long stop = Debug.threadCpuTimeNanos();

  if(stop - start < 10000000) {
    return false;
  }
  else {
    return true;
  }
}
