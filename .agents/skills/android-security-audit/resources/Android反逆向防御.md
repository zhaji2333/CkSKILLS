# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses)

## 测试Root检测 (MSTG-RESILIENCE-1)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-root-detection-mstg-resilience-1)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview)

在反逆向的背景下，root 检测的目标是让应用程序在有 root 权限的设备上运行更加困难，这反过来会阻止逆向工程师喜欢使用的一些工具和技术。与大多数其他防御措施一样，Root检测本身并不是很有效，但是实施分散在整个应用程序中的多个根检查可以提高整体防篡改方案的有效性。

对于 Android，我们将“root 检测”定义得更广泛一些，包括自定义 ROM 检测，即确定设备是原装 Android 版本还是自定义版本。

### 常见的Root检测方法[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#common-root-detection-methods)

在下一节中，我们列出了您会遇到的一些常见的Root检测方法。您会在 OWASP 移动测试指南随附的[OWASP UnCrackable Apps for Android](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-crackmes)中找到其中一些方法的实现。

Root检测也可以通过[RootBeer](https://github.com/scottyab/rootbeer)等库来实现。

#### SafetyNet[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#safetynet)

SafetyNet 是一个 Android API，它提供一组服务并根据软件和硬件信息创建设备配置文件。然后将此配置文件与已通过 Android 兼容性测试的可接受设备型号列表进行比较。谷歌[建议](https://developers.google.com/android/reference/com/google/android/gms/safetynet/SafetyNet)将该功能用作“作为反滥用系统一部分的附加深度防御信号”。

SafetyNet 的具体工作原理没有详细记录，并且可能随时更改。当您调用此 API 时，SafetyNet 会下载包含 Google 提供的设备验证代码的二进制包，然后通过反射动态执行该代码。[John Kozyrakis](https://koz.io/inside-safetynet/)的一项分析表明，SafetyNet 还尝试检测设备是否已获得 root 权限，但具体如何确定尚不清楚。

要使用该 API，应用程序可以调用该`SafetyNetApi.attest`方法（该方法返回带有*Attestation Result*的 JWS 消息），然后检查以下字段：

- `ctsProfileMatch`：如果为“true”，则设备配置文件与 Google 列出的设备之一相匹配。
- `basicIntegrity`：如果为“true”，则运行该应用程序的设备可能未被篡改。
- `nonces`: 匹配对其请求的响应。
- `timestampMs`: 检查自您发出请求到收到响应后经过了多长时间。延迟响应可能表明存在可疑活动。
- `apkPackageName`, `apkCertificateDigestSha256`, `apkDigestSha256`: 提供APK的信息，用于验证调用应用程序的身份。如果 API 无法可靠地确定 APK 信息，则不存在这些参数。

以下是示例证明结果：

```
{
  "nonce": "R2Rra24fVm5xa2Mg",
  "timestampMs": 9860437986543,
  "apkPackageName": "com.package.name.of.requesting.app",
  "apkCertificateDigestSha256": ["base64 encoded, SHA-256 hash of the
                                  certificate used to sign requesting app"],
  "apkDigestSha256": "base64 encoded, SHA-256 hash of the app's APK",
  "ctsProfileMatch": true,
  "basicIntegrity": true,
}
```

##### CTSPROFILEMATCH 与 BASICINTEGRITY[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#ctsprofilematch-vs-basicintegrity)

`basicIntegrity`SafetyNet Attestation API 最初提供了一个名为帮助开发人员确定设备完整性的单一值。随着 API 的发展，谷歌引入了一种新的、更严格的检查，其结果显示在一个名为 的值中`ctsProfileMatch`，它允许开发人员更精细地评估运行其应用程序的设备。

从广义上讲，`basicIntegrity`为您提供有关设备及其 API 的一般完整性的信号。许多 Root 设备失败`basicIntegrity`，模拟器、虚拟设备和有篡改迹象的设备（例如 API Hook）也是如此。

另一方面，`ctsProfileMatch`给你一个关于设备兼容性的更严格的信号。只有经过谷歌认证的未经修改的设备才能通过`ctsProfileMatch`。将失败`ctsProfileMatch`的设备包括：

- 失败的设备`basicIntegrity`
- 具有解锁引导加载程序的设备
- 具有自定义系统映像（自定义 ROM）的设备
- 制造商未申请或未通过 Google 认证的设备
- 具有直接从 Android 开源程序源文件构建的系统映像的设备
- 系统映像作为测试版或开发者预览计划（包括 Android 测试版计划）的一部分分发的设备

##### 使用时的建议`SAFETYNETAPI.ATTEST`[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#recommendations-when-using-safetynetapiattest)

- 使用加密安全随机函数在您的服务器上创建一个大的（16 字节或更长）随机数，以便恶意用户无法重用成功的证明结果来代替不成功的结果
- 仅当 的值为true时才信任 APK 信息（`apkPackageName`和`apkCertificateDigestSha256`） 。`apkDigestSha256``ctsProfileMatch`
- 应使用安全连接将整个 JWS 响应发送到您的服务器以进行验证。不建议直接在应用程序中执行验证，因为在这种情况下，无法保证验证逻辑本身未被修改。
- 该`verify`方法仅验证 JWS 消息是否由 SafetyNet 签名。它不会验证判决的有效负载是否符合您的预期。尽管这项服务看起来很有用，但它仅用于测试目的，并且它有非常严格的使用配额，每个项目每天 10,000 个请求，不会根据请求增加。因此，您应该参考[SafetyNet 验证示例](https://github.com/googlesamples/android-play-safetynet/tree/master/server/java/src/main/java)并以不依赖于 Google 服务器的方式在您的服务器上实施数字签名验证逻辑。
- SafetyNet Attestation API 为您提供了发出证明请求时设备状态的快照。成功的证明并不一定意味着该设备在过去或将来会通过证明。建议规划一个策略，使用最少数量的证明来满足用例。
- 为防止无意中达到您的`SafetyNetApi.attest`配额并出现证明错误，您应该构建一个系统来监控您对 API 的使用，并在您达到配额之前向您发出警告，以便您可以增加配额。您还应该准备好处理由于超出配额而导致的证明失败，并避免在这种情况下阻止所有用户。如果您即将达到您的配额，或者预计可能会导致您超出配额的短期峰值，您可以提交此[表单](https://support.google.com/googleplay/android-developer/contact/safetynetqr)以请求短期或长期增加您的 API 密钥的配额。这个过程以及额外的配额都是免费的。

遵循此[清单](https://developer.android.com/training/safetynet/attestation-checklist)以确保您已完成将`SafetyNetApi.attest`API 集成到应用程序中所需的每个步骤。

#### 程序检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#programmatic-detection)

##### 文件存在检查[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#file-existence-checks)

也许最广泛使用的程序化检测方法是检查通常在已获得 root 权限的设备上找到的文件，例如常见的 root 权限应用程序及其相关文件和目录的包文件，包括以下内容：

```
/system/app/Superuser.apk
/system/etc/init.d/99SuperSUDaemon
/dev/com.koushikdutta.superuser.daemon/
/system/xbin/daemonsu
```

检测代码还经常查找通常在设备被 root 后安装的二进制文件。这些搜索包括检查 busybox 并尝试在不同位置打开*su*二进制文件：

```
/sbin/su
/system/bin/su
/system/bin/failsafe/su
/system/xbin/su
/system/xbin/busybox
/system/sd/xbin/su
/data/local/su
/data/local/xbin/su
/data/local/bin/su
```

检查是否`su`在 PATH 上也有效：

```
    public static boolean checkRoot(){
        for(String pathDir : System.getenv("PATH").split(":")){
            if(new File(pathDir, "su").exists()) {
                return true;
            }
        }
        return false;
    }
```

文件检查可以在 Java 和Native代码中轻松实现。以下 JNI 示例（改编自[rootinspector](https://github.com/devadvance/rootinspector/)）使用`stat`系统调用来检索有关文件的信息并在文件存在时返回“1”。

```
jboolean Java_com_example_statfile(JNIEnv * env, jobject this, jstring filepath) {
  jboolean fileExists = 0;
  jboolean isCopy;
  const char * path = (*env)->GetStringUTFChars(env, filepath, &isCopy);
  struct stat fileattrib;
  if (stat(path, &fileattrib) < 0) {
    __android_log_print(ANDROID_LOG_DEBUG, DEBUG_TAG, "NATIVE: stat error: [%s]", strerror(errno));
  } else
  {
    __android_log_print(ANDROID_LOG_DEBUG, DEBUG_TAG, "NATIVE: stat success, access perms: [%d]", fileattrib.st_mode);
    return 1;
  }

  return 0;
}
```

##### 执行`SU`和其他命令[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#executing-su-and-other-commands)

确定是否`su`存在的另一种方法是尝试通过该`Runtime.getRuntime.exec`方法执行它。如果`su`不在 PATH 上，将抛出 IOException。可以使用相同的方法来检查经常在 root 设备上找到的其他程序，例如 busybox 和通常指向它的符号链接。

##### 检查正在运行的进程[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#checking-running-processes)

Supersu - 迄今为止最流行的 root 工具 - 运行名为 的身份验证守护程序`daemonsu`，因此此进程的存在是 root 设备的另一个标志。可以使用API、命令`ActivityManager.getRunningAppProcesses`和浏览目录来枚举正在运行的进程。以下是在[rootinspector](https://github.com/devadvance/rootinspector/)中实现的示例：`manager.getRunningServices``ps``/proc`

```
    public boolean checkRunningProcesses() {

      boolean returnValue = false;

      // Get currently running application processes
      List<RunningServiceInfo> list = manager.getRunningServices(300);

      if(list != null){
        String tempName;
        for(int i=0;i<list.size();++i){
          tempName = list.get(i).process;

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

要绕过此问题，我们必须稍微修改应用程序的行为（最简单的方法是使用 NOP 修补对 的调用`_exit`并将函数挂接到`_exit`中`libc.so`）。在这一点上，我们已经进入了众所周知的“军备竞赛”：实施更复杂的这种防御形式以及绕过它总是可能的。

### 绕过调试器检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-debugger-detection)

没有绕过反调试的通用方法：最好的方法取决于用于防止或检测调试的特定机制以及整体保护方案中的其他防御措施。例如，如果没有完整性检查或您已经停用了它们，则为应用程序打补丁可能是最简单的方法。在其他情况下，Hook框架或内核模块可能更可取。以下方法描述了绕过调试器检测的不同方法：

- 修补反调试功能：通过简单地用 NOP 指令覆盖它来禁用不需要的行为。请注意，如果反调试机制设计良好，可能需要更复杂的补丁。
- `isDebuggable`使用 Frida 或 Xposed 在 Java 和Native层上挂接 API：操纵函数的返回值，例如`isDebuggerConnected`隐藏调试器。
- 改变环境：Android 是一个开放的环境。如果实在不行，可以修改操作系统，颠覆开发者在设计反调试技巧时的假设。

#### 绕过示例：UnCrackable App for Android Level 2[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-example-uncrackable-app-for-android-level-2)

在处理经过混淆的应用程序时，您经常会发现开发人员故意将数据和功能“隐藏”在Native库(NATIVE LIBRARIES)中。您将[在“UnCrackable App for Android”的第 2 级中](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l2)找到这方面的示例。

乍一看，代码看起来像之前的挑战。一个名为的类`CodeCheck`负责验证用户输入的代码。实际检查似乎发生在`bar`声明为本*机*方法的方法中。

```
package sg.vantagepoint.uncrackable2;

public class CodeCheck {
    public CodeCheck() {
        super();
    }

    public boolean a(String arg2) {
        return this.bar(arg2.getBytes());
    }

    private native boolean bar(byte[] arg1) {
    }
}

    static {
        System.loadLibrary("foo");
    }
```

请在 GitHub 中[查看针对 Android Crackme Level 2 的不同建议解决方案。](https://mas.owasp.org/crackmes/Android#android-uncrackable-l2)

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_1)

检查反调试机制，包括以下标准：

- 附加基于 jdb 和 ptrace 的调试器失败或导致应用程序终止或出现故障。
- 多种检测方法分散在整个应用程序的源代码中（而不是它们都在一个方法或函数中）。
- 反调试防御在多个 API 层（Java、Native库(NATIVE LIBRARIES)函数、汇编器/系统调用）上运行。
- 这些机制在某种程度上是原创的（而不是从 StackOverflow 或其他来源复制和粘贴）。

努力绕过反调试防御并回答以下问题：

- 是否可以轻松绕过这些机制（例如，通过Hook单个 API 函数）？
- 通过静态和动态分析识别反调试代码有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您对绕过这些机制的难度的主观评估是什么？

如果反调试机制缺失或太容易被绕过，请根据上述有效性标准提出建议。这些建议可能包括添加更多检测机制以及将现有机制与其他防御措施更好地集成。

## 测试文件完整性检查 (MSTG-RESILIENCE-3)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-file-integrity-checks-mstg-resilience-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_2)

有两个与文件完整性相关的主题：

1. *代码完整性检查：*在“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中，我们讨论了Android 的APK 代码签名检查。我们还看到坚定的逆向工程师可以通过重新打包和重新签名应用程序轻松绕过此检查。为了使这个绕过过程更加复杂，可以通过对应用程序字节码、Native库(NATIVE LIBRARIES)和重要数据文件进行 CRC 检查来增强保护方案。这些检查可以在 Java 和Native层上实现。这个想法是要有额外的控制，这样即使代码签名有效，应用程序也只能在未修改的状态下正确运行。
2. *文件存储完整性检查：*应保护应用程序存储在SD卡或公共存储中的文件的完整性和存储的键值对的完整性`SharedPreferences`。

#### 示例实现 - 应用程序源代码[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#sample-implementation-application-source-code)

完整性检查通常会计算所选文件的校验和或哈希值。通常受保护的文件包括

- AndroidManifest.xml,
- 类文件 *.dex,
- Native库(NATIVE LIBRARIES) (*.so)。

以下[来自 Android 破解博客的示例实现](https://androidcracking.blogspot.com/2011/06/anti-tampering-with-crc-check.html)计算了一个 CRC `classes.dex`，并将其与预期值进行比较。

```
private void crcTest() throws IOException {
 boolean modified = false;
 // required dex crc value stored as a text string.
 // it could be any invisible layout element
 long dexCrc = Long.parseLong(Main.MyContext.getString(R.string.dex_crc));

 ZipFile zf = new ZipFile(Main.MyContext.getPackageCodePath());
 ZipEntry ze = zf.getEntry("classes.dex");

 if ( ze.getCrc() != dexCrc ) {
  // dex has been modified
  modified = true;
 }
 else {
  // dex not tampered with
  modified = false;
 }
}
```

#### 示例实施 - 存储[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#sample-implementation-storage)

当在存储本身上提供完整性时，您可以在给定的键值对（对于 Android `SharedPreferences`）上创建 HMAC 或在文件系统提供的完整文件上创建 HMAC。

使用 HMAC 时，您可以[使用充气城堡实现或 AndroidKeyStore 对给定内容进行 HMAC](https://web.archive.org/web/20210804035343/https://cseweb.ucsd.edu/~mihir/papers/oem.html)。

使用 BouncyCastle 生成 HMAC 时完成以下过程：

1. 确保 BouncyCastle 或 SpongyCastle 已注册为security providers。
2. 使用密钥（可以存储在密钥库中）初始化 HMAC。
3. 获取需要 HMAC 的内容的字节数组。
4. 使用字节码调用`doFinal`HMAC。
5. 将 HMAC 附加到步骤 3 中获得的 bytearray。
6. 存储步骤 5 的结果。

使用 BouncyCastle 验证 HMAC 时完成以下过程：

1. 确保 BouncyCastle 或 SpongyCastle 已注册为security providers。
2. 将消息和 HMAC 字节提取为单独的数组。
3. 重复生成 HMAC 过程的步骤 1-4。
4. 将提取的 HMAC 字节与步骤 3 的结果进行比较。

当基于[Android Keystore](https://developer.android.com/training/articles/keystore.html)生成 HMAC 时，最好只对 Android 6.0（API 级别 23）及更高版本执行此操作。

以下是一个方便的 HMAC 实现，没有`AndroidKeyStore`：

```
public enum HMACWrapper {
    HMAC_512("HMac-SHA512"), //please note that this is the spec for the BC provider
    HMAC_256("HMac-SHA256");

    private final String algorithm;

    private HMACWrapper(final String algorithm) {
        this.algorithm = algorithm;
    }

    public Mac createHMAC(final SecretKey key) {
        try {
            Mac e = Mac.getInstance(this.algorithm, "BC");
            SecretKeySpec secret = new SecretKeySpec(key.getKey().getEncoded(), this.algorithm);
            e.init(secret);
            return e;
        } catch (NoSuchProviderException | InvalidKeyException | NoSuchAlgorithmException e) {
            //handle them
        }
    }

    public byte[] hmac(byte[] message, SecretKey key) {
        Mac mac = this.createHMAC(key);
        return mac.doFinal(message);
    }

    public boolean verify(byte[] messageWithHMAC, SecretKey key) {
        Mac mac = this.createHMAC(key);
        byte[] checksum = extractChecksum(messageWithHMAC, mac.getMacLength());
        byte[] message = extractMessage(messageWithHMAC, mac.getMacLength());
        byte[] calculatedChecksum = this.hmac(message, key);
        int diff = checksum.length ^ calculatedChecksum.length;

        for (int i = 0; i < checksum.length && i < calculatedChecksum.length; ++i) {
            diff |= checksum[i] ^ calculatedChecksum[i];
        }

        return diff == 0;
    }

    public byte[] extractMessage(byte[] messageWithHMAC) {
        Mac hmac = this.createHMAC(SecretKey.newKey());
        return extractMessage(messageWithHMAC, hmac.getMacLength());
    }

    private static byte[] extractMessage(byte[] body, int checksumLength) {
        if (body.length >= checksumLength) {
            byte[] message = new byte[body.length - checksumLength];
            System.arraycopy(body, 0, message, 0, message.length);
            return message;
        } else {
            return new byte[0];
        }
    }

    private static byte[] extractChecksum(byte[] body, int checksumLength) {
        if (body.length >= checksumLength) {
            byte[] checksum = new byte[checksumLength];
            System.arraycopy(body, body.length - checksumLength, checksum, 0, checksumLength);
            return checksum;
        } else {
            return new byte[0];
        }
    }

    static {
        Security.addProvider(new BouncyCastleProvider());
    }
}
```

提供完整性的另一种方法是对您获得的字节数组进行签名，并将签名添加到原始字节数组。

#### 绕过文件完整性检查[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-file-integrity-checks)

##### 绕过应用程序源完整性检查[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-the-application-source-integrity-checks)

1. 修补反调试功能。通过简单地用 NOP 指令覆盖相关的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed 在 Java 和Native层上Hook文件系统 API。返回原始文件的句柄而不是修改后的文件。
3. 使用内核模块拦截与文件相关的系统调用。当进程尝试打开修改后的文件时，返回文件未修改版本的文件描述符。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

##### 绕过存储完整性检查[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-the-storage-integrity-checks)

1. 如“[测试设备绑定](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-device-binding-mstg-resilience-10)”部分所述，从设备中检索数据。
2. 更改检索到的数据，然后将其放回存储中。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_2)

**应用程序源完整性检查：**

在未修改的状态下运行应用程序并确保一切正常。将简单的补丁应用到`classes.dex`应用程序包中的任何 .so 库。按照“基本安全测试”一章中的描述重新打包并重新签署应用程序，然后运行该应用程序。该应用程序应检测到修改并以某种方式做出响应。至少，应用程序应该提醒用户和/或终止。绕过防御并回答以下问题：

- 是否可以轻松绕过这些机制（例如，通过Hook单个 API 函数）？
- 通过静态和动态分析识别反调试代码有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您如何评估绕过这些机制的难度？

**存储完整性检查：**

适用类似于应用程序源完整性检查的方法。回答以下问题：

- 这些机制是否可以被简单地绕过（例如，通过更改文件的内容或键值）？
- 获取 HMAC 密钥或非对称私钥有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您如何评估绕过这些机制的难度？

## 测试逆向工程工具检测 (MSTG-RESILIENCE-4)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-reverse-engineering-tools-detection-mstg-resilience-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_3)

逆向工程师常用的工具、框架和应用程序的存在可能表明有人试图对应用程序进行逆向工程。其中一些工具只能在获得 root 权限的设备上运行，而其他工具则强制应用程序进入调试模式或依赖于在手机上启动后台服务。因此，应用程序可以通过不同的方式来检测逆向工程攻击并对其做出反应，例如通过终止自身。

### 检测方法[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#detection-methods)

您可以通过查找关联的应用程序包、文件、进程或其他特定于工具的修改和工件来检测以未修改形式安装的流行逆向工程工具。在以下示例中，我们将讨论检测本指南中广泛使用的 Frida 检测框架的不同方法。其他工具如Substrate、Xposed等也可以类似检测。请注意，DBI/注入/Hook工具通常可以通过Runtime(运行时)完整性检查隐式检测，这将在下面讨论。

例如，在 root 设备上的默认配置中，Frida 作为 frida-server 在设备上运行。当您显式附加到目标应用程序时（例如通过 frida-trace 或 Frida REPL），Frida 将 frida-agent 注入到应用程序的内存中。因此，您可能希望在附加到应用程序之后（而不是之前）找到它。如果你检查`/proc/<pid>/maps`你会发现 frida-agent 是 frida-agent-64.so：

```
bullhead:/ # cat /proc/18370/maps | grep -i frida
71b6bd6000-71b7d62000 r-xp  /data/local/tmp/re.frida.server/frida-agent-64.so
71b7d7f000-71b7e06000 r--p  /data/local/tmp/re.frida.server/frida-agent-64.so
71b7e06000-71b7e28000 rw-p  /data/local/tmp/re.frida.server/frida-agent-64.so
```

另一种方法（也适用于非 root 设备）包括将[frida-gadget](https://www.frida.re/docs/gadget/)嵌入到 APK 中并*强制*应用程序将其作为其本地库之一加载。如果您在启动应用程序后检查应用程序内存映射（无需明确附加到它），您会发现嵌入的 frida-gadget 为 libfrida-gadget.so。

```
bullhead:/ # cat /proc/18370/maps | grep -i frida

71b865a000-71b97f1000 r-xp  /data/app/sg.vp.owasp_mobile.omtg_android-.../lib/arm64/libfrida-gadget.so
71b9802000-71b988a000 r--p  /data/app/sg.vp.owasp_mobile.omtg_android-.../lib/arm64/libfrida-gadget.so
71b988a000-71b98ac000 rw-p  /data/app/sg.vp.owasp_mobile.omtg_android-.../lib/arm64/libfrida-gadget.so
```

看着Frida*留下的这两条**痕迹*，您可能已经想到检测它们将是一项微不足道的任务。实际上，绕过该检测是如此微不足道。但事情会变得更加复杂。下表简要介绍了一组典型的 Frida 检测方法，并简要讨论了它们的有效性。

> [Berdhard Mueller 的文章“The Ji-Jitsu of Detecting Frida”](https://web.archive.org/web/20181227120751/http://www.vantagepoint.sg/blog/90-the-jiu-jitsu-of-detecting-frida)中介绍了以下一些检测方法（已存档）。请参阅它以获取更多详细信息和示例代码片段。

| 方法                           | 描述                                                         | 讨论                                                         |
| :----------------------------- | :----------------------------------------------------------- | :----------------------------------------------------------- |
| **检查应用程序签名**           | 为了将 frida-gadget 嵌入到 APK 中，需要重新打包并退出。您可以在应用启动时检查 APK 的签名（例如，自 API 级别 28 起的[GET_SIGNING_CERTIFICATES](https://developer.android.com/reference/android/content/pm/PackageManager#GET_SIGNING_CERTIFICATES)），并将其与您固定在 APK 中的签名进行比较。 | 不幸的是，这太微不足道了，无法绕过，例如通过修补 APK 或执行系统调用Hook。 |
| **检查相关工件的环境**         | 工件可以是包文件、二进制文件、库、进程和临时文件。对于 Frida，这可能是在目标（有根）系统中运行的 frida-server（负责通过 TCP 公开 Frida 的守护进程）。检查正在运行的服务 ( [`getRunningServices`](https://developer.android.com/reference/android/app/ActivityManager.html#getRunningServices(int))) 和进程 ( `ps`)，搜索名称为“frida-server”的服务。您还可以遍历已加载库的列表并检查是否存在可疑库（例如名称中包含“frida”的库）。 | 从 Android 7.0（API 级别 24）开始，检查正在运行的服务/进程不会向您显示像 frida-server 这样的守护进程，因为它不是由应用程序本身启动的。即使有可能，绕过这个也很容易，只需重命名相应的 Frida 工件 (frida-server/frida-gadget/frida-agent)。 |
| **检查打开的 TCP 端口**        | frida-server 进程默认绑定到 TCP 端口 27042。检查此端口是否打开是检测守护进程的另一种方法。 | 此方法在其默认模式下检测 frida-server，但可以通过命令行参数更改监听端口，因此绕过它有点太简单了。 |
| **检查响应 D-Bus Auth 的端口** | `frida-server`使用 D-Bus 协议进行通信，因此您可以期望它响应 D-Bus AUTH。向每个打开的端口发送一条 D-Bus AUTH 消息并检查答案，希望它`frida-server`会自己显示出来。 | 这是一种相当可靠的检测方法`frida-server`，但 Frida 提供了不需要 frida-server 的替代操作模式。 |
| **扫描进程内存以查找已知工件** | 扫描内存以查找在 Frida 库中发现的工件，例如所有版本的 frida-gadget 和 frida-agent 中都存在字符串“LIBFRIDA”。例如，使用`Runtime.getRuntime().exec`并遍历在`/proc/self/maps`或`/proc/<pid>/maps`（取决于 Android 版本）搜索字符串中列出的内存映射。 | 这种方法更有效一些，仅使用 Frida 很难绕过，尤其是在添加了一些混淆并且正在扫描多个工件的情况下。但是，所选工件可能会在 Frida 二进制文件中进行修补。[在Berdhard Mueller 的 GitHub](https://github.com/muellerberndt/frida-detection-demo/blob/master/AntiFrida/app/src/main/cpp/native-lib.cpp)上找到源代码。 |

请记住，这张表远非详尽无遗。我们可以开始讨论[命名管道](https://en.wikipedia.org/wiki/Named_pipe)（由 frida-server 用于外部通信）、检测[蹦床](https://en.wikipedia.org/wiki/Trampoline_(computing))（在函数序言处插入的间接跳转向量），这将有助于检测 Substrate 或 Frida 的拦截器，但例如，不会有效对抗Frida的追猎者；以及许多其他或多或少有效的检测方法。它们中的每一个都将取决于您是否使用有Root设备、Root方法的特定版本和/或工具本身的版本。此外，该应用程序可以尝试通过使用各种混淆技术来使其更难检测已实施的保护机制，如下面“[针对逆向工程的测试弹性”部分所述](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-obfuscation-mstg-resilience-9)”。最后，这是保护在不受信任的环境（在用户设备中运行的应用程序）上处理的数据的猫捉老鼠游戏的一部分。

> 重要的是要注意，这些控制只会增加逆向工程过程的复杂性。如果使用，最好的方法是巧妙地组合控件而不是单独使用它们。然而，它们都不能保证 100% 的有效性，因为逆向工程师总是可以完全访问设备，因此总是会赢！您还必须考虑将某些控件集成到您的应用程序中可能会增加应用程序的复杂性，甚至会影响其性能。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_3)

使用测试设备中安装的各种逆向工程工具和框架启动应用程序。至少包括以下内容：Frida、Xposed、Android 的 Substrate、RootCloak、Android SSL Trust Killer。

该应用程序应以某种方式响应这些工具的存在。例如：

- 提醒用户并要求承担责任。
- 通过优雅终止来防止执行。
- 安全擦除存储在设备上的任何敏感数据。
- 向后端服务器报告，例如，用于欺诈检测。

接下来，绕过逆向工程工具的检测并回答以下问题：

- 是否可以轻松绕过这些机制（例如，通过Hook单个 API 函数）？
- 通过静态和动态分析识别反逆向工程代码有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您如何评估绕过这些机制的难度？

绕过逆向工程工具的检测时，应遵循以下步骤：

1. 修补反逆向工程功能。通过简单地用 NOP 指令覆盖相关的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed 在 Java 和Native层上Hook文件系统 API。返回原始文件的句柄，而不是修改后的文件。
3. 使用内核模块拦截与文件相关的系统调用。当进程尝试打开修改后的文件时，返回文件未修改版本的文件描述符。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

## 测试仿真器检测 (MSTG-RESILIENCE-5)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-emulator-detection-mstg-resilience-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_4)

在反逆向的背景下，模拟器检测的目标是增加应用程序在模拟设备上运行的难度，这阻碍了逆向工程师喜欢使用的一些工具和技术。这种增加的难度迫使逆向工程师击败仿真器检查或利用物理设备，从而禁止进行大规模设备分析所需的访问。

### 模拟器检测示例[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#emulator-detection-examples)

有几个指标表明正在模拟有问题的设备。尽管所有这些 API 调用都可以Hook，但这些指标提供了适度的第一道防线。

第一组指标在文件中`build.prop`。

```
API Method          Value           Meaning
Build.ABI           armeabi         possibly emulator
BUILD.ABI2          unknown         possibly emulator
Build.BOARD         unknown         emulator
Build.Brand         generic         emulator
Build.DEVICE        generic         emulator
Build.FINGERPRINT   generic         emulator
Build.Hardware      goldfish        emulator
Build.Host          android-test    possibly emulator
Build.ID            FRF91           emulator
Build.MANUFACTURER  unknown         emulator
Build.MODEL         sdk             emulator
Build.PRODUCT       sdk             emulator
Build.RADIO         unknown         possibly emulator
Build.SERIAL        null            emulator
Build.USER          android-build   emulator
```

您可以在已获得 root 权限的 Android 设备上编辑该文件`build.prop`，或在从源代码编译 AOSP 时对其进行修改。这两种技术都可以让您绕过上面的静态字符串检查。

下一组静态指示器使用电话管理器。所有 Android 模拟器都有此 API 可以查询的固定值。

```
API                                                     Value                   Meaning
TelephonyManager.getDeviceId()                          0's                     emulator
TelephonyManager.getLine1 Number()                      155552155               emulator
TelephonyManager.getNetworkCountryIso()                 us                      possibly emulator
TelephonyManager.getNetworkType()                       3                       possibly emulator
TelephonyManager.getNetworkOperator().substring(0,3)    310                     possibly emulator
TelephonyManager.getNetworkOperator().substring(3)      260                     possibly emulator
TelephonyManager.getPhoneType()                         1                       possibly emulator
TelephonyManager.getSimCountryIso()                     us                      possibly emulator
TelephonyManager.getSimSerial Number()                  89014103211118510720    emulator
TelephonyManager.getSubscriberId()                      310260000000000         emulator
TelephonyManager.getVoiceMailNumber()                   15552175049             emulator
```

请记住，Xposed 或 Frida 等Hook框架可以Hook此 API 以提供虚假数据。

### 绕过模拟器检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-emulator-detection)

1. 修补模拟器检测功能。通过简单地用 NOP 指令覆盖相关的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed API 在 Java 和Native层上Hook文件系统 API。返回看起来无辜的值（最好从真实设备中获取）而不是明显的模拟器值。例如，您可以覆盖该`TelephonyManager.getDeviceID`方法以返回 IMEI 值。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_4)

在模拟器中安装并运行该应用程序。该应用程序应检测到它正在模拟器中执行，并终止或拒绝执行应受保护的功能。

绕过防御并回答以下问题：

- 通过静态和动态分析识别模拟器检测代码有多难？
- 是否可以轻松绕过检测机制（例如，通过Hook单个 API 函数）？
- 您是否需要编写自定义代码来禁用反仿真功能？你需要多少时间？
- 您如何评估绕过这些机制的难度？

## 测试Runtime(运行时)完整性检查 (MSTG-RESILIENCE-6)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-runtime-integrity-checks-mstg-resilience-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_5)

此类别中的控件验证应用程序内存空间的完整性，以保护应用程序免受Runtime(运行时)应用的内存补丁的影响。此类补丁包括对二进制代码、字节码、函数指针表和重要数据结构的不必要更改，以及加载到进程内存中的流氓代码。完整性可以通过以下方式验证：

1. 将内存的内容或内容的校验和与正确的值进行比较，
2. 在内存中搜索不需要的修改的签名。

与“检测逆向工程工具和框架”类别有一些重叠，事实上，当我们展示如何在进程内存中搜索与 Frida 相关的字符串时，我们展示了基于签名的方法。以下是各种完整性监控的更多示例。

#### Runtime(运行时)完整性检查示例[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#runtime-integrity-check-examples)

##### 检测对 JAVA Runtime(运行时)的篡改[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#detecting-tampering-with-the-java-runtime)

此检测代码来自[dead && end 博客](https://d3adend.org/blog/?p=589)。

```
try {
  throw new Exception();
}
catch(Exception e) {
  int zygoteInitCallCount = 0;
  for(StackTraceElement stackTraceElement : e.getStackTrace()) {
    if(stackTraceElement.getClassName().equals("com.android.internal.os.ZygoteInit")) {
      zygoteInitCallCount++;
      if(zygoteInitCallCount == 2) {
        Log.wtf("HookDetection", "Substrate is active on the device.");
      }
    }
    if(stackTraceElement.getClassName().equals("com.saurik.substrate.MS$2") &&
        stackTraceElement.getMethodName().equals("invoked")) {
      Log.wtf("HookDetection", "A method on the stack trace has been hooked using Substrate.");
    }
    if(stackTraceElement.getClassName().equals("de.robv.android.xposed.XposedBridge") &&
        stackTraceElement.getMethodName().equals("main")) {
      Log.wtf("HookDetection", "Xposed is active on the device.");
    }
    if(stackTraceElement.getClassName().equals("de.robv.android.xposed.XposedBridge") &&
        stackTraceElement.getMethodName().equals("handleHookedMethod")) {
      Log.wtf("HookDetection", "A method on the stack trace has been hooked using Xposed.");
    }

  }
}
```

##### 检测NativeHook[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#detecting-native-hooks)

通过使用 ELF 二进制文件，可以通过覆盖内存中的函数指针（例如，全局偏移表或 PLT Hook）或修补部分函数代码本身（内联Hook）来安装Native函数Hook。检查各个内存区域的完整性是检测这种Hook的一种方法。

全局偏移表 (GOT) 用于解析库函数。在Runtime(运行时)，动态链接器用全局符号的绝对地址修补这个表。*GOT 钩子*覆盖存储的函数地址并将合法的函数调用重定向到对手控制的代码。这种类型的Hook可以通过枚举进程内存映射并验证每个 GOT 入口指向合法加载的库来检测。

与 GNU 相比`ld`，它仅在第一次需要符号地址时才解析符号地址（惰性绑定），Android 链接器解析所有外部函数并在加载库后立即写入相应的 GOT 条目（立即绑定）。因此，您可以期望所有 GOT 条目在Runtime(运行时)都指向其各自库的代码段中的有效内存位置。GOT hook 检测方法通常是遍历 GOT 并验证这一点。

*内联Hook*通过覆盖函数代码开头或结尾的一些指令来工作。在Runtime(运行时)，这个所谓的蹦床将执行重定向到注入的代码。您可以通过检查库函数的序言和结尾是否有可疑指令来检测内联Hook，例如远跳转到库外的位置。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_5)

确保禁用所有基于文件的逆向工程工具检测。然后，使用Xposed、Frida、Substrate注入代码，并尝试安装native hooks和Java method hooks。该应用程序应检测其内存中的“恶意”代码并做出相应响应。

使用以下技术绕过检查：

1. 修补完整性检查。通过使用 NOP 指令覆盖相应的字节码或Native代码来禁用不需要的行为。
2. 使用 Frida 或 Xposed Hook用于检测的 API 并返回假值。

有关修补、代码注入和内核模块的示例，请参阅“ [Android 上的篡改和逆向工程”一章。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)

## 测试混淆 (MSTG-RESILIENCE-9)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-obfuscation-mstg-resilience-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_6)

[“移动应用程序篡改和逆向工程”](https://mas.owasp.org/MASTG/General/0x04c-Tampering-and-Reverse-Engineering/#obfuscation)一章介绍了几种众所周知的混淆技术，通常可以在移动应用程序中使用。

Android 应用程序可以使用不同的工具实施其中一些混淆技术。例如，[ProGuard](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#proguard)提供了一种简单的方法来缩小和混淆代码，并从 Android Java 应用程序的字节码中去除不需要的调试信息。它用无意义的字符串替换标识符，例如类名、方法名和变量名。这是一种布局混淆，不会影响程序的性能。

> 反编译 Java 类是微不足道的，因此建议始终对生产字节码应用一些基本的混淆。

详细了解 Android 混淆技术：

- Gautam Arvind[的“Android Native代码的安全加固”](https://darvincitech.wordpress.com/2020/01/07/security-hardening-of-android-native-code/)
- Eduardo Novella[的“APKiD：AppShielding 产品的快速识别”](https://github.com/enovella/cve-bio-enovella/blob/master/slides/APKiD-NowSecure-Connect19-enovella.pdf)
- [“原生 Android 应用程序的挑战：混淆和漏洞”](https://www.theses.fr/2020REN1S047.pdf)，作者 Pierre Graux

#### 使用混淆器[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-proguard)

开发人员使用 build.gradle 文件来启用混淆。`minifyEnabled`在下面的示例中，您可以看到`proguardFiles`已设置。创建异常以保护某些类免受混淆（使用`-keepclassmembers`和`-keep class`）是很常见的。因此，审核 ProGuard 配置文件以查看哪些类被豁免很重要。该方法从文件夹中`getDefaultProguardFile('proguard-android.txt')`获取默认的 ProGuard 设置。`<Android SDK>/tools/proguard/`

有关如何缩小、混淆和优化您的应用程序的更多信息，请参阅[Android 开发人员文档](https://developer.android.com/studio/build/shrink-code)。

> 当您使用 Android Studio 3.4 或 Android Gradle 插件 3.4.0 或更高版本构建项目时，该插件不再使用 ProGuard 来执行编译时代码优化。相反，该插件使用 R8 编译器。R8 适用于您现有的所有 ProGuard 规则文件，因此更新 Android Gradle 插件以使用 R8 不需要您更改现有规则。

R8 是来自 Google 的新代码收缩器，在 Android Studio 3.3 beta 中引入。默认情况下，R8 会删除对调试有用的属性，包括行号、源文件名和变量名。R8 是一个免费的 Java 类文件收缩器、优化器、混淆器和预验证器，并且比 ProGuard 更快，另请参阅[Android 开发人员博客文章了解更多详细信息](https://android-developers.googleblog.com/2018/11/r8-new-code-shrinker-from-google-is.html)。它与 Android 的 SDK 工具一起提供。要为发布版本激活收缩，请将以下内容添加到 build.gradle：

```
android {
    buildTypes {
        release {
            // Enables code shrinking, obfuscation, and optimization for only
            // your project's release build type.
            minifyEnabled true

            // Includes the default ProGuard rules files that are packaged with
            // the Android Gradle plugin. To learn more, go to the section about
            // R8 configuration files.
            proguardFiles getDefaultProguardFile(
                    'proguard-android-optimize.txt'),
                    'proguard-rules.pro'
        }
    }
    ...
}
```

该文件`proguard-rules.pro`是您定义自定义 ProGuard 规则的地方。使用该标志`-keep`，您可以保留未被 R8 删除的某些代码，否则可能会产生错误。例如，保留常见的 Android 类，如我们的示例配置`proguard-rules.pro`文件中所示：

```
...
-keep public class * extends android.app.Activity
-keep public class * extends android.app.Application
-keep public class * extends android.app.Service
...
```

您可以使用[以下语法](https://developer.android.com/studio/build/shrink-code#configuration-files)对项目中的特定类或库进行更精细的定义：

```
-keep public class MyClass
```

混淆通常会以Runtime(运行时)性能为代价，因此它通常只应用于代码的某些非常特定的部分，通常是那些处理安全和Runtime(运行时)保护的部分。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#static-analysis)

[反编译APK](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#decompiling-java-code)并[查看它](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)以确定代码库是否已被混淆。

您可以在下面找到混淆代码块的示例：

```
package com.a.a.a;

import com.a.a.b.a;
import java.util.List;

class a$b
  extends a
{
  public a$b(List paramList)
  {
    super(paramList);
  }

  public boolean areAllItemsEnabled()
  {
    return true;
  }

  public boolean isEnabled(int paramInt)
  {
    return true;
  }
}
```

以下是一些注意事项：

- 有意义的标识符，例如类名、方法名和变量名，可能已被丢弃。
- 二进制文件中的字符串资源和字符串可能已被加密。
- 与受保护功能相关的代码和数据可能会被加密、打包或以其他方式隐藏。

对于Native代码：

- [libc API](https://man7.org/linux/man-pages/dir_section_3.html)（例如打开、读取）可能已被操作系统[系统调用](https://man7.org/linux/man-pages/man2/syscalls.2.html)取代。
- [Obfuscator-LLVM](https://github.com/obfuscator-llvm/obfuscator)可能已被应用于执行[“控制流扁平化”](https://github.com/obfuscator-llvm/obfuscator/wiki/Control-Flow-Flattening)或[“虚假控制流”](https://github.com/obfuscator-llvm/obfuscator/wiki/Bogus-Control-Flow)。

其中一些技术在Gautam Arvind的博客文章[“Android Native代码的安全强化”](https://darvincitech.wordpress.com/2020/01/07/security-hardening-of-android-native-code/)和Eduardo Novella的[“APKiD：AppShielding 产品的快速识别”演示文稿中进行了讨论和分析。](https://github.com/enovella/cve-bio-enovella/blob/master/slides/APKiD-NowSecure-Connect19-enovella.pdf)

要进行更详细的评估，您需要详细了解相关威胁和使用的混淆方法。诸如[APKiD 之](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apkid)类的工具可能会为您提供有关目标应用程序使用了哪些技术的额外指示，例如混淆器、加壳器和反调试措施。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis)

您可以使用[APKiD](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#apkid)来检测应用程序是否已被混淆。

[使用适用于 Android 4 级的 UnCrackable App 的](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l4)示例：

```
apkid owasp-mastg/Crackmes/Android/Level_04/r2pay-v1.0.apk
[+] APKiD 2.1.2 :: from RedNaga :: rednaga.io
[*] owasp-mastg/Crackmes/Android/Level_04/r2pay-v1.0.apk!classes.dex
 |-> anti_vm : Build.TAGS check, possible ro.secure check
 |-> compiler : r8
 |-> obfuscator : unreadable field names, unreadable method names
```

在这种情况下，它会检测到应用程序具有不可读的字段名称和方法名称等。

## 测试设备绑定 (MSTG-RESILIENCE-10)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-device-binding-mstg-resilience-10)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_7)

设备绑定的目标是阻止攻击者尝试将应用程序及其状态从设备 A 复制到设备 B 并继续在设备 B 上执行该应用程序。在确定设备 A 可信后，它可能拥有比设备更多的权限B. 当应用程序从设备 A 复制到设备 B 时，这些差别特权不应改变。

在我们描述可用的标识符之前，让我们快速讨论一下如何将它们用于绑定。允许设备绑定的方法有以下三种：

- 使用设备标识符增强用于身份验证的凭据。如果应用程序需要频繁地重新验证自己和/或用户，这是有意义的。

- 使用与设备强绑定的密钥材料对存储在设备中的数据进行加密可以加强设备绑定。Android Keystore 提供了不可导出的私钥，我们可以将其用于此目的。当恶意行为者从设备中提取此类数据时，将无法解密数据，因为密钥不可访问。实现这一点，需要以下步骤：

- `KeyGenParameterSpec`使用API在 Android Keystore 中生成密钥对。

  ```
  //Source: <https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.html>
  KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(
          KeyProperties.KEY_ALGORITHM_RSA, "AndroidKeyStore");
  keyPairGenerator.initialize(
          new KeyGenParameterSpec.Builder(
                  "key1",
                  KeyProperties.PURPOSE_DECRYPT)
                  .setDigests(KeyProperties.DIGEST_SHA256, KeyProperties.DIGEST_SHA512)
                  .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_RSA_OAEP)
                  .build());
  KeyPair keyPair = keyPairGenerator.generateKeyPair();
  Cipher cipher = Cipher.getInstance("RSA/ECB/OAEPWithSHA-256AndMGF1Padding");
  cipher.init(Cipher.DECRYPT_MODE, keyPair.getPrivate());
  ...
  
  // The key pair can also be obtained from the Android Keystore any time as follows:
  KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
  keyStore.load(null);
  PrivateKey privateKey = (PrivateKey) keyStore.getKey("key1", null);
  PublicKey publicKey = keyStore.getCertificate("key1").getPublicKey();
  ```

- 为 AES-GCM 生成密钥：

  ```
  //Source: <https://developer.android.com/reference/android/security/keystore/KeyGenParameterSpec.html>
  KeyGenerator keyGenerator = KeyGenerator.getInstance(
          KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
  keyGenerator.init(
          new KeyGenParameterSpec.Builder("key2",
                  KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                  .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                  .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                  .build());
  SecretKey key = keyGenerator.generateKey();
  
  // The key can also be obtained from the Android Keystore any time as follows:
  KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
  keyStore.load(null);
  key = (SecretKey) keyStore.getKey("key2", null);
  ```

- 通过 AES-GCM 密码使用密钥对应用程序存储的身份验证数据和其他敏感数据进行加密，并使用实例 ID 等设备特定参数作为关联数据：

  ```
  Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
  final byte[] nonce = new byte[GCM_NONCE_LENGTH];
  random.nextBytes(nonce);
  GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, nonce);
  cipher.init(Cipher.ENCRYPT_MODE, key, spec);
  byte[] aad = "<deviceidentifierhere>".getBytes();;
  cipher.updateAAD(aad);
  cipher.init(Cipher.ENCRYPT_MODE, key);
  
  //use the cipher to encrypt the authentication data see 0x50e for more details.
  ```

- 使用存储在 Android Keystore 中的公钥对密钥进行加密，并将加密后的密钥存储在应用程序的私有存储中。

- 每当需要访问令牌等身份验证数据或其他敏感数据时，使用存储在 Android Keystore 中的私钥解密密钥，然后使用解密的密钥解密密文。

- 使用基于令牌的设备身份验证（实例 ID）确保使用相同的应用程序实例。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#static-analysis_1)

过去，Android 开发人员通常依赖于`Settings.Secure.ANDROID_ID`(SSAID) 和 MAC 地址。这[随着 Android 8.0（API 级别 26）的发布而改变](https://android-developers.googleblog.com/2017/04/changes-to-device-identifiers-in.html)。由于 MAC 地址现在经常在未连接到接入点时随机化，并且 SSAID 不再是设备绑定 ID。相反，它成为绑定到用户、设备和请求 SSAID 的应用程序的应用程序签名密钥的值。此外，Google 的 SDK 文档中还有[关于标识符的新建议。](https://developer.android.com/training/articles/user-data-ids.html)基本上，谷歌建议：

- 在广告方面使用广告 ID ( `AdvertisingIdClient.Info`)，以便用户可以选择拒绝。
- 使用实例 ID ( `FirebaseInstanceId`) 进行设备识别。
- 仅将 SSAID 用于欺诈检测和由同一开发人员签名的应用程序之间共享状态。

请注意，实例 ID 和广告 ID 在设备升级和设备重置过程中并不稳定。但是，实例 ID 至少可以识别设备上当前安装的软件。

当源代码可用时，您可以查找一些关键术语：

- 不再有效的唯一标识符：
- `Build.SERIAL`没有`Build.getSerial`
- `htc.camera.sensor.front_SN`适用于 HTC 设备
- `persist.service.bdroid.bdadd`
- `Settings.Secure.bluetooth_address`或`WifiInfo.getMacAddress`from ，除非在清单中启用`WifiManager`了系统权限。`LOCAL_MAC_ADDRESS`
- `ANDROID_ID`仅用作标识符。随着时间的推移，这将影响旧设备的绑定质量。
- 缺少实例 ID、`Build.SERIAL`和 IMEI。

```
  TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
  String IMEI = tm.getDeviceId();
```

- `AndroidKeyStore`在使用`KeyPairGeneratorSpec`或`KeyGenParameterSpec`API中创建私钥。

为确保可以使用标识符，请检查`AndroidManifest.xml`IMEI 和`Build.Serial`. 该文件应包含权限`<uses-permission android:name="android.permission.READ_PHONE_STATE" />`。

> 适用于 Android 8.0（API 级别 26）的应用在请求时将获得“未知”结果`Build.Serial`。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis_1)

有几种方法可以测试应用程序绑定：

#### 使用仿真器进行动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis-with-an-emulator)

1. 在模拟器上运行应用程序。
2. 确保您可以提高对应用程序实例的信任（例如，在应用程序中进行身份验证）。
3. 按照以下步骤从模拟器中检索数据：
4. 通过 ADB shell 通过 SSH 连接到您的模拟器。
5. 执行`run-as <your app-id>`。您的应用程序 ID 是 AndroidManifest.xml 中描述的包。
6. `chmod 777`缓存和Shared Preferences的内容。
7. 从 app-id 退出当前用户。
8. `/data/data/<your appid>/cache`将和的内容复制`shared-preferences`到 SD 卡。
9. 使用 ADB 或 DDMS 来拉取内容。
10. 在另一个模拟器上安装应用程序。
11. 在应用程序的数据文件夹中，覆盖第 3 步中的数据。
12. 将步骤 3 中的数据复制到第二个模拟器的 SD 卡。
13. 通过 ADB shell 通过 SSH 连接到您的模拟器。
14. 执行`run-as <your app-id>`。您的 app-id 是 中描述的包 `AndroidManifest.xml`。
15. `chmod 777`文件夹的缓存和Shared Preferences。
16. 复制 SD 卡的旧内容`to /data/data/<your appid>/cache`和`shared-preferences`.
17. 你能继续处于认证状态吗？如果是这样，绑定可能无法正常工作。

#### 谷歌实例 ID[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#google-instance-id)

[Google 实例 ID](https://developers.google.com/instance-id/)使用令牌来验证正在运行的应用程序实例。当应用程序被重置、卸载等时，实例 ID 会被重置，这意味着您将拥有一个新的应用程序“实例”。为实例 ID 执行以下步骤：

1. 在您的 Google Developer Console 中为给定的应用程序配置您的实例 ID。这包括管理 PROJECT_ID。

2. 设置 Google Play 服务。在文件`build.gradle`中，添加

   ```
   apply plugin: 'com.android.application'
       ...
   
       dependencies {
           compile 'com.google.android.gms:play-services-gcm:10.2.4'
       }
   ```

3. 获取实例 ID。

   ```
   String iid = Instance ID.getInstance(context).getId();
   //now submit this iid to your server.
   ```

4. 生成令牌。

   ```
   String authorizedEntity = PROJECT_ID; // Project id from Google Developer Console
   String scope = "GCM"; // e.g. communicating using GCM, but you can use any
                       // URL-safe characters up to a maximum of 1000, or
                       // you can also leave it blank.
   String token = Instance ID.getInstance(context).getToken(authorizedEntity,scope);
   //now submit this token to the server.
   ```

5. 确保您可以处理来自实例 ID 的回调，以防出现无效设备信息、安全问题等。这需要扩展`Instance IDListenerService`和处理那里的回调：

   ```
   public class MyInstance IDService extends Instance IDListenerService {
   public void onTokenRefresh() {
       refreshAllTokens();
   }
   
   private void refreshAllTokens() {
       // assuming you have defined TokenList as
       // some generalized store for your tokens for the different scopes.
       // Please note that for application validation having just one token with one scopes can be enough.
       ArrayList<TokenList> tokenList = TokensList.get();
       Instance ID iid = Instance ID.getInstance(this);
       for(tokenItem : tokenList) {
       tokenItem.token =
           iid.getToken(tokenItem.authorizedEntity,tokenItem.scope,tokenItem.options);
       // send this tokenItem.token to your server
       }
   }
   };
   ```

6. 在您的 Android 清单中注册该服务：

   ```
   <service android:name=".MyInstance IDService" android:exported="false">
   <intent-filter>
           <action android:name="com.google.android.gms.iid.Instance ID" />
   </intent-filter>
   </service>
   ```

当您将实例 ID (iid) 和令牌提交到您的服务器时，您可以将该服务器与实例 ID 云服务一起使用来验证令牌和 iid。当 iid 或令牌似乎无效时，您可以触发保护程序（例如，通知服务器可能存在复制或安全问题或从应用程序中删除数据并要求重新注册）。

请注意，[Firebase 还支持实例 ID](https://firebase.google.com/docs/reference/android/com/google/firebase/iid/FirebaseInstanceId)。

#### IMEI 和序列号[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#imei-serial)

Google 建议不要使用这些标识符，除非应用程序存在高风险。

对于Android 8.0（API level 26）之前的Android设备，可以通过如下方式请求串口：

```
   String serial = android.os.Build.SERIAL;
```

对于运行 Android 版本 O 及更高版本的设备，您可以通过以下方式请求设备的序列号：

1. 在您的 Android 清单中设置权限：

   ```
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
   ```

2. 在Runtime(运行时)向用户请求权限：有关详细信息，请参阅[https://developer.android.com/training/permissions/requesting.html 。](https://developer.android.com/training/permissions/requesting.html)

3. 获取序列号：

   ```
   String serial = android.os.Build.getSerial();
   ```

检索 IMEI：

1. 在您的 Android 清单中设置所需的权限：

   ```
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   ```

2. 如果您使用的是 Android 版本 Android 6（API 级别 23）或更高版本，请在Runtime(运行时)向用户请求权限：有关更多详细信息，请参阅https://developer.android.com/training/permissions/requesting.html。

3. 获取 IMEI：

   ```
   TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
   String IMEI = tm.getDeviceId();
   ```

#### SSAID[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#ssaid)

Google 建议不要使用这些标识符，除非应用程序存在高风险。您可以按如下方式检索 SSAID：

```
  String SSAID = Settings.Secure.ANDROID_ID;
```

[自 Android 8.0（API 级别 26）以来](https://android-developers.googleblog.com/2017/04/changes-to-device-identifiers-in.html)，SSAID 和 MAC 地址的行为发生了变化。此外，Google 的 SDK 文档中还有关于标识符的[新建议](https://developer.android.com/training/articles/user-data-ids.html)。由于这种新行为，我们建议开发人员不要单独依赖 SSAID。标识符变得不太稳定。例如，在恢复出厂设置后或在升级到 Android 8.0（API 级别 26）后重新安装应用程序时，SSAID 可能会发生变化。有些设备具有相同的`ANDROID_ID`和/或具有`ANDROID_ID`可以被覆盖的。因此，最好使用从使用加密中`ANDROID_ID`随机生成的密钥来加密。加密后应存储在`AndroidKeyStore``AES_GCM``ANDROID_ID``SharedPreferences`（私下）。应用程序签名更改的那一刻，应用程序可以检查增量并注册新的`ANDROID_ID`. 在没有新的应用程序签名密钥的情况下发生变化的那一刻，它应该表明其他地方出了问题。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_6)

当源代码可用时，您可以查找一些关键术语：

- 不再有效的唯一标识符：
- `Build.SERIAL`没有`Build.getSerial`
- `htc.camera.sensor.front_SN`适用于 HTC 设备
- `persist.service.bdroid.bdadd`
- `Settings.Secure.bluetooth_address`或`WifiInfo.getMacAddress`from ，除非在清单中启用`WifiManager`了系统权限。`LOCAL_MAC_ADDRESS`
- ANDROID_ID 仅用作标识符。随着时间的推移，这将影响旧设备上的绑定质量。
- 缺少实例 ID、`Build.SERIAL`和 IMEI。

```
  TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
  String IMEI = tm.getDeviceId();
```

为确保可以使用标识符，请检查`AndroidManifest.xml`IMEI 和`Build.Serial`. 清单应包含权限`<uses-permission android:name="android.permission.READ_PHONE_STATE" />`。

有几种动态测试设备绑定的方法：

#### 使用模拟器[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-an-emulator)

请参阅上面的“[使用仿真器进行动态分析](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis-with-an-emulator)”部分。

#### 使用两个不同的 root 设备[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-two-different-rooted-devices)

1. 在您的 root 设备上运行该应用程序。
2. 确保您可以在应用程序实例中提高信任度（例如，在应用程序中进行身份验证）。
3. 从第一个有Root设备检索数据。
4. 在第二个获得 root 权限的设备上安装应用程序。
5. 在应用程序的数据文件夹中，覆盖第 3 步中的数据。
6. 你能继续处于认证状态吗？如果是这样，绑定可能无法正常工作。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#owasp-masvs)

- MSTG-RESILIENCE-1：“该应用程序通过提醒用户或终止该应用程序来检测并响应已破解或越狱设备的存在。”
- MSTG-RESILIENCE-2：“应用程序阻止调试和/或检测并响应附加的调试器。必须涵盖所有可用的调试协议。”
- MSTG-RESILIENCE-3：“该应用程序检测并响应篡改其自身沙箱中的可执行文件和关键数据。”
- MSTG-RESILIENCE-4：“该应用程序检测并响应设备上广泛使用的逆向工程工具和框架的存在。”
- MSTG-RESILIENCE-5：“应用程序检测并响应在模拟器中运行。”
- MSTG-RESILIENCE-6：“该应用程序检测并响应篡改其自身内存空间中的代码和数据。”
- MSTG-RESILIENCE-9：“混淆应用于程序化防御，这反过来又通过动态分析阻碍了去混淆。”
- MSTG-RESILIENCE-10：“该应用程序使用从设备唯一的多个属性派生的设备指纹来实现‘设备绑定’功能。”

### 安全网认证[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#safetynet-attestation)

- 开发人员指南 - https://developer.android.com/training/safetynet/attestation.html
- SafetyNet 认证清单 - https://developer.android.com/training/safetynet/attestation-checklist
- SafetyNet 认证的注意事项 - https://android-developers.googleblog.com/2017/11/10-things-you-might-be-doing-wrong-when.html
- SafetyNet 验证示例 - https://github.com/googlesamples/android-play-safetynet/
- SafetyNet Attestation API - 配额请求 - https://support.google.com/googleplay/android-developer/contact/safetynetqr
- 混淆器-LLVM - https://github.com/obfuscator-llvm/obfuscator
