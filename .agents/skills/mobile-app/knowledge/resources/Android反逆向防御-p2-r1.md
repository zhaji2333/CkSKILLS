# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 2 · part 1

> 分段 1/2。索引见 `Android反逆向防御-p2.md`。

# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 2

> 分段 2/5。索引见 `Android反逆向防御.md`。

## 承接

```

#### 弄乱与 JDWP 相关的数据结构[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#messing-with-jdwp-related-data-structures)

在 Dalvik 中，可以通过该`DvmGlobals`结构访问全局虚拟机状态。全局变量 gDvm 持有指向该结构的指针。`DvmGlobals`包含对 JDWP 调试很重要并且可以被篡改的各种变量和指针。

```
struct DvmGlobals {
    /*
     * Some options that could be worth tampering with :)
     */

    bool        jdwpAllowed;        // debugging allowed for this process?
    bool        jdwpConfigured;     // has debugging info been provided?
    JdwpTransportType jdwpTransport;
    bool        jdwpServer;
    char*       jdwpHost;
    int         jdwpPort;
    bool        jdwpSuspend;

    Thread*     threadList;

    bool        nativeDebuggerActive;
    bool        debuggerConnected;      /* debugger or DDMS is connected */
    bool        debuggerActive;         /* debugger is making requests */
    JdwpState*  jdwpState;

};
```

例如，[将 gDvm.methDalvikDdmcServer_dispatch 函数指针设置为 NULL 会使 JDWP 线程崩溃](https://github.com/crazykid95/Backup-Mobile-Security-Report/blob/master/AndroidREnDefenses201305.pdf)：

```
JNIEXPORT jboolean JNICALL Java_poc_c_crashOnInit ( JNIEnv* env , jobject ) {
  gDvm.methDalvikDdmcServer_dispatch = NULL;
}
```

即使 gDvm 变量不可用，您也可以在 ART 中使用类似的技术来禁用调试。ART Runtime(运行时)将一些 JDWP 相关类的 vtables 导出为全局符号（在 C++ 中，vtables 是保存指向类方法的指针的表）。这包括类`JdwpSocketState`和的虚表`JdwpAdbState`，它们分别通过网络套接字和 ADB 处理 JDWP 连接。[您可以通过覆盖相关 vtables](https://web.archive.org/web/20200307152820/https://www.vantagepoint.sg/blog/88-anti-debugging-fun-with-android-art)（存档）中的方法指针来操纵调试Runtime(运行时)的行为。

覆盖方法指针的一种方法是用 的地址覆盖函数`jdwpAdbState::ProcessIncoming`的地址`JdwpAdbState::Shutdown`。这将导致调试器立即断开连接。

```
#include <jni.h>
#include <string>
#include <android/log.h>
#include <dlfcn.h>
#include <sys/mman.h>
#include <jdwp/jdwp.h>

#define log(FMT, ...) __android_log_print(ANDROID_LOG_VERBOSE, "JDWPFun", FMT, ##__VA_ARGS__)

// Vtable structure. Just to make messing around with it more intuitive

struct VT_JdwpAdbState {
    unsigned long x;
    unsigned long y;
    void * JdwpSocketState_destructor;
    void * _JdwpSocketState_destructor;
    void * Accept;
    void * showmanyc;
    void * ShutDown;
    void * ProcessIncoming;
};

extern "C"

JNIEXPORT void JNICALL Java_sg_vantagepoint_jdwptest_MainActivity_JDWPfun(
        JNIEnv *env,
        jobject /* this */) {

    void* lib = dlopen("libart.so", RTLD_NOW);

    if (lib == NULL) {
        log("Error loading libart.so");
        dlerror();
    }else{

        struct VT_JdwpAdbState *vtable = ( struct VT_JdwpAdbState *)dlsym(lib, "_ZTVN3art4JDWP12JdwpAdbStateE");

        if (vtable == 0) {
            log("Couldn't resolve symbol '_ZTVN3art4JDWP12JdwpAdbStateE'.\n");
        }else {

            log("Vtable for JdwpAdbState at: %08x\n", vtable);

            // Let the fun begin!

            unsigned long pagesize = sysconf(_SC_PAGE_SIZE);
            unsigned long page = (unsigned long)vtable & ~(pagesize-1);

            mprotect((void *)page, pagesize, PROT_READ | PROT_WRITE);

            vtable->ProcessIncoming = vtable->ShutDown;

            // Reset permissions & flush cache

            mprotect((void *)page, pagesize, PROT_READ);

        }
    }
}
```

### 传统反调试[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#traditional-anti-debugging)

在 Linux 上，[`ptrace`系统调用](http://man7.org/linux/man-pages/man2/ptrace.2.html)用于观察和控制进程（*tracee*）的执行，并检查和更改该进程的内存和寄存器。`ptrace`是在原生代码中实现系统调用跟踪和断点调试的主要方式。大多数 JDWP 反调试技巧（对于基于计时器的检查可能是安全的）不会捕获基于的经典调试器`ptrace`，因此，许多 Android 反调试技巧包括`ptrace`，通常利用这样一个事实，即一次只有一个调试器可以附加到一个过程。

#### 检查 TracerPid[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-tracerpid)

当您调试应用程序并在Native代码上设置断点时，Android Studio 会将所需的文件复制到目标设备并启动将用于`ptrace`附加到进程的 lldb-server。从这一刻起，如果你检查被调试进程的[状态文件](http://man7.org/linux/man-pages/man5/proc.5.html)（`/proc/<pid>/status`或`/proc/self/status`），你会看到“TracerPid”字段的值不为0，这是调试的标志。

> 请记住，**这仅适用于Native代码**。如果您正在调试 Java/Kotlin-only 应用程序，“TracerPid”字段的值应为 0。

这种技术通常应用在 C 语言的 JNI Native库(NATIVE LIBRARIES)中，如[Google 的 gperftools (Google Performance Tools)) Heap Checker](https://github.com/gperftools/gperftools/blob/master/src/heap-checker.cc#L112)方法的实现所示`IsDebuggerAttached`。但是，如果您希望将此检查作为 Java/Kotlin 代码的一部分包含在内，您可以参考[Tim Strazzere 的 Anti-Emulator 项目](https://github.com/strazzere/anti-emulator/)`hasTracerPid`中该方法的Java 实现。

当尝试自己实现这样的方法时，您可以使用 ADB 手动检查 TracerPid 的值。以下清单使用 Google 的 NDK 示例应用程序[hello-jni (com.example.hellojni)](https://github.com/android/ndk-samples/tree/android-mk/hello-jni)在附加 Android Studio 的调试器后执行检查：

```
$ adb shell ps -A | grep com.example.hellojni
u0_a271      11657   573 4302108  50600 ptrace_stop         0 t com.example.hellojni
$ adb shell cat /proc/11657/status | grep -e "^TracerPid:" | sed "s/^TracerPid:\t//"
TracerPid:      11839
$ adb shell ps -A | grep 11839
u0_a271      11839 11837   14024   4548 poll_schedule_timeout 0 S lldb-server
```

您可以看到 com.example.hellojni (PID=11657) 的状态文件如何包含 11839 的 TracerPID，我们可以将其识别为 lldb-server 进程。

#### 使用 Fork 和 ptrace[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-fork-and-ptrace)

您可以通过类似于以下简单示例代码的代码派生子进程并将其作为调试器附加到父进程来阻止进程调试：

```
void fork_and_attach()
{
  int pid = fork();

  if (pid == 0)
    {
      int ppid = getppid();

      if (ptrace(PTRACE_ATTACH, ppid, NULL, NULL) == 0)
        {
          waitpid(ppid, NULL, 0);

          /* Continue the parent process */
          ptrace(PTRACE_CONT, NULL, NULL);
        }
    }
}
```

附加子项后，进一步尝试附加到父项将失败。我们可以通过将代码编译成 JNI 函数并将其打包到我们在设备上运行的应用程序中来验证这一点。

```
root@android:/ # ps | grep -i anti
u0_a151   18190 201   1535844 54908 ffffffff b6e0f124 S sg.vantagepoint.antidebug
u0_a151   18224 18190 1495180 35824 c019a3ac b6e0ee5c S sg.vantagepoint.antidebug
```

尝试使用 gdbserver 附加到父进程失败并出现错误：

```
root@android:/ # ./gdbserver --attach localhost:12345 18190
warning: process 18190 is already traced by process 18224
Cannot attach to lwp 18190: Operation not permitted (1)
Exiting
```

但是，您可以轻松地绕过此失败，方法是杀死子级并“释放”父级使其免于被追踪。因此，您通常会发现更复杂的方案，涉及多个进程和线程以及某种形式的监控以防止篡改。常用方法包括

- 分叉多个相互跟踪的进程，
- 跟踪正在运行的进程以确保孩子们活着，
- 监控`/proc`文件系统中的值，例如`/proc/pid/status`.

让我们看一下对上述方法的简单改进。在 initial 之后`fork`，我们在 parent 中启动一个额外的线程，持续监控 child 的状态。根据应用程序是在调试模式还是发布模式下构建（由`android:debuggable`清单中的标志指示），子进程应该执行以下操作之一：

- 在发布模式下：对 ptrace 的调用失败，子进程立即崩溃并出现分段错误（退出代码 11）。
- 在调试模式下：对 ptrace 的调用有效，孩子应该无限期地运行。因此，对 的调用`waitpid(child_pid)`永远不会返回。如果是这样，那就有问题了，我们会杀死整个进程组。

以下是使用 JNI 函数实现此改进的完整代码：

```
#include <jni.h>
#include <unistd.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <pthread.h>

static int child_pid;

void *monitor_pid() {

    int status;

    waitpid(child_pid, &status, 0);

    /* Child status should never change. */

    _exit(0); // Commit seppuku

}

void anti_debug() {

    child_pid = fork();

    if (child_pid == 0)
    {
        int ppid = getppid();
        int status;

        if (ptrace(PTRACE_ATTACH, ppid, NULL, NULL) == 0)
        {
            waitpid(ppid, &status, 0);

            ptrace(PTRACE_CONT, ppid, NULL, NULL);

            while (waitpid(ppid, &status, 0)) {

                if (WIFSTOPPED(status)) {
                    ptrace(PTRACE_CONT, ppid, NULL, NULL);
                } else {
                    // Process has exited
                    _exit(0);
                }
            }
        }

    } else {
        pthread_t t;

        /* Start the monitoring thread */
        pthread_create(&t, NULL, monitor_pid, (void *)NULL);
    }
}

JNIEXPORT void JNICALL
Java_sg_vantagepoint_antidebug_MainActivity_antidebug(JNIEnv *env, jobject instance) {

    anti_debug();
}
```

同样，我们将其打包到 Android 应用程序中以查看其是否有效。和以前一样，当我们运行应用程序的调试版本时，会出现两个进程。

```
root@android:/ # ps | grep -I anti-debug
u0_a152   20267 201   1552508 56796 ffffffff b6e0f124 S sg.vantagepoint.anti-debug
u0_a152   20301 20267 1495192 33980 c019a3ac b6e0ee5c S sg.vantagepoint.anti-debug
```

但是，如果我们此时终止子进程，父进程也会退出：

```
root@android:/ # kill -9 20301
130|root@hammerhead:/ # cd /data/local/tmp
root@android:/ # ./gdbserver --attach localhost:12345 20267
gdbserver: unable to open /proc file '/proc/20267/status'
Cannot attach to lwp 20267: No such file or directory (2)
Exiting
```

