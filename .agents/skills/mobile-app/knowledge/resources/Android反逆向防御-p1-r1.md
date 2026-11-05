# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 1 · part 1

> 分段 1/2。索引见 `Android反逆向防御-p1.md`。

# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 1

> 分段 1/5。索引见 `Android反逆向防御.md`。

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

