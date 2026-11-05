# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 3 · part 1

> 分段 1/2。索引见 `Android基础安全测试-p3.md`。

# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 3

> 分段 3/5。索引见 `Android基础安全测试.md`。

## 承接

- 应用程序组件：、、、、`activity`（请`service`参阅“ [Android 平台 API](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/) ”和“ [Android 上的数据存储”](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)`provider``receiver`
- 可调试标志：（`debuggable`参见“ [Android 应用程序的代码质量和构建设置](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/)”）

请参阅上述章节以了解有关如何测试每个点的更多信息。

##### 应用二进制[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#app-binary)

如上文“[探索应用程序包](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)`classes.dex`”中所示，可以在应用程序包的Root目录中找到应用程序二进制文件 ( )。它是一个所谓的 DEX（Dalvik 可执行文件）文件，其中包含已编译的 Java 代码。由于其性质，在应用一些转换后，您将能够使用反编译器生成 Java 代码。我们还看到了`smali`运行 apktool 后获得的文件夹。它包含以称为 smali 的中间语言编写的反汇编 Dalvik 字节码，smali 是 Dalvik 可执行文件的人类可读表示。

有关如何对 DEX 文件进行逆向工程的更多信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中的“[查看反编译的 Java 代码”部分。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-decompiled-java-code)

##### 编译的应用程序二进制文件[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#compiled-app-binary)

在某些情况下，检索已编译的应用程序二进制文件 (.odex) 可能很有用。

首先获取应用程序数据目录的路径：

```
adb shell pm path com.example.myapplication
package:/data/app/~~DEMFPZh7R4qfUwwwh1czYA==/com.example.myapplication-pOslqiQkJclb_1Vk9-WAXg==/base.apk
```

删除`/base.apk`部分，添加`/oat/arm64/base.odex`并使用生成的路径从设备中提取 base.odex：

```
adb root
adb pull /data/app/~~DEMFPZh7R4qfUwwwh1czYA==/com.example.myapplication-pOslqiQkJclb_1Vk9-WAXg==/oat/arm64/base.odex
```

请注意，具体目录将Root据您的 Android 版本而有所不同。如果`/oat/arm64/base.odex`找不到该文件，请在返回的目录中手动搜索`pm path`。

##### Native库(NATIVE LIBRARIES)[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#native-libraries)

您可以检查`lib`APK 中的文件夹：

```
$ ls -1 lib/armeabi/
libdatabase_sqlcipher.so
libnative.so
libsqlcipher_android.so
libstlport_shared.so
```

或来自objection设备：

```
...g.vp.owasp_mobile.omtg_android on (google: 8.1.0) [usb] # ls lib
Type    ...  Name
------  ...  ------------------------
File    ...  libnative.so
File    ...  libdatabase_sqlcipher.so
File    ...  libstlport_shared.so
File    ...  libsqlcipher_android.so
```

目前，这就是您可以获得的有关Native库(NATIVE LIBRARIES)的所有信息，除非您开始对它们进行逆向工程，这是使用与用于逆向应用程序二进制文件的方法不同的方法完成的，因为此代码无法反编译，只能反汇编。有关如何对这些库进行逆向工程的更多信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中的“[查看反汇编Native代码”部分。](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#reviewing-disassembled-native-code)

##### 其他应用资源[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#other-app-resources)

通常值得查看您可能在 APK 的Root文件夹中找到的其余资源和文件，因为有时它们包含其他好东西，如密钥存储、加密数据库、证书等。

#### 访问应用程序数据目录[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#accessing-app-data-directories)

安装该应用程序后，您可以探索更多信息，其中objection等工具会派上用场。

使用 objection 时可以检索各种信息，其中`env`会显示应用程序的所有目录信息。

```
$ objection -g sg.vp.owasp_mobile.omtg_android explore

...g.vp.owasp_mobile.omtg_android on (google: 8.1.0) [usb] # env

Name                    Path
----------------------  ---------------------------------------------------------------------------
cacheDirectory          /data/user/0/sg.vp.owasp_mobile.omtg_android/cache
codeCacheDirectory      /data/user/0/sg.vp.owasp_mobile.omtg_android/code_cache
externalCacheDirectory  /storage/emulated/0/Android/data/sg.vp.owasp_mobile.omtg_android/cache
filesDirectory          /data/user/0/sg.vp.owasp_mobile.omtg_android/files
obbDir                  /storage/emulated/0/Android/obb/sg.vp.owasp_mobile.omtg_android
packageCodePath         /data/app/sg.vp.owasp_mobile.omtg_android-kR0ovWl9eoU_yh0jPJ9caQ==/base.apk
```

在这些信息中，我们发现：

- `/data/data/[package-name]`位于或处的内部数据目录（又名沙箱目录）`/data/user/0/[package-name]`
- 外部数据目录位于`/storage/emulated/0/Android/data/[package-name]`或`/sdcard/Android/data/[package-name]`
- 应用程序包的路径在`/data/app/`

内部数据目录是应用程序用来存储Runtime(运行时)创建的数据的目录，其基本结构如下：

```
...g.vp.owasp_mobile.omtg_android on (google: 8.1.0)  [usb] # ls
Type       ...  Name
---------  ...  -------------------
Directory  ...  cache
Directory  ...  code_cache
Directory  ...  lib
Directory  ...  shared_prefs
Directory  ...  files
Directory  ...  databases

Readable: True  Writable: True
```

每个文件夹都有自己的用途：

- **cache**：此位置用于数据缓存。例如，WebView 缓存就在这个目录中。
- **code_cache**：这是用于存储缓存代码的文件系统特定于应用程序的缓存目录的位置。在运行 Android 5.0（API 级别 21）或更高版本的设备上，当应用程序或整个平台升级时，系统将删除存储在该位置的所有文件。
- **lib**：此文件夹存储用 C/C++ 编写的Native库(NATIVE LIBRARIES)。这些库可以具有多个文件扩展名之一，包括 .so 和 .dll（x86 支持）。此文件夹包含应用程序具有原生库的平台的子目录，包括
- armeabi：所有基于 ARM 的处理器的编译代码
- armeabi-v7a：编译代码适用于所有基于 ARM 的处理器，仅限版本 7 及更高版本
- arm64-v8a：所有基于 ARM 的 64 位处理器的编译代码，仅基于版本 8 及更高版本
- x86：仅针对 x86 处理器编译的代码
- x86_64：仅为 x86_64 处理器编译的代码
- mips：MIPS 处理器的编译代码
- **shared_prefs**：此文件夹包含一个 XML 文件，该文件存储通过[SharedPreferences API](https://developer.android.com/training/basics/data-storage/shared-preferences.html)保存的值。
- **files**：此文件夹存储应用程序创建的常规文件。
- **databases**：该文件夹存放应用在Runtime(运行时)生成的SQLite数据库文件，如用户数据文件。

但是，应用程序可能不仅在这些文件夹中而且在父文件夹 ( `/data/data/[package-name]`) 中存储更多数据。

有关安全存储敏感数据的更多信息和最佳实践，请参阅“[测试数据存储”一章。](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)

#### 监控系统日志[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#monitoring-system-logs)

在 Android 上，您可以使用 轻松检查系统消息的日志[`Logcat`](https://developer.android.com/tools/debugging/debugging-log.html)。Logcat的执行方式有两种：

- Logcat 是 Android Studio 中*Dalvik Debug Monitor Server* (DDMS) 的一部分。如果应用程序在调试模式下运行，日志输出将显示在 Logcat 选项卡上的 Android Monitor 中。您可以通过在 Logcat 中定义模式来过滤应用程序的日志输出。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05b/log_output_Android_Studio.png)

- 您可以使用 adb 执行 Logcat 以永久存储日志输出：

```
adb logcat > logcat.log
```

使用以下命令，您可以专门 grep 范围内应用程序的日志输出，只需插入包名称即可。当然，您的应用程序需要运行`ps`才能获得其 PID。

```
adb logcat | grep "$(adb shell ps | grep <package-name> | awk '{print $2}')"
```

## 设置网络测试环境[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#setting-up-a-network-testing-environment)

### 基本网络监控/嗅探[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#basic-network-monitoringsniffing)

使用[tcpdump](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#tcpdump)、 netcat (nc) 和[Wireshark](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#wireshark)[可以实时远程嗅探所有 Android 流量](https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/)。首先，确保您的手机上安装了最新版本的[Android tcpdump](https://www.androidtcpdump.com/)。以下是[安装步骤](https://wladimir-tm4pda.github.io/porting/tcpdump.html)：

```
adb root
adb remount
adb push /wherever/you/put/tcpdump /system/xbin/tcpdump
```

如果执行`adb root`返回错误`adbd cannot run as root in production builds`，请按如下方式安装 tcpdump：

```
adb push /wherever/you/put/tcpdump /data/local/tmp/tcpdump
adb shell
su
mount -o rw,remount /system;
cp /data/local/tmp/tcpdump /system/xbin/
cd /system/xbin
chmod 755 tcpdump
```

在某些生产构建中，您可能会遇到错误`mount: '/system' not in /proc/mounts`。

在这种情况下，您可以将上面的行替换为`$ mount -o rw,remount /system;`，`$ mount -o rw,remount /`如[本 Stack Overflow 帖子](https://stackoverflow.com/a/28018008)中所述。

> 切记：要使用tcpdump，需要手机root权限！

执行`tcpdump`一次，看看是否有效。一旦有几个数据包进来，您可以按 CTRL+c 停止 tcpdump。

```
$ tcpdump
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on wlan0, link-type EN10MB (Ethernet), capture size 262144 bytes
04:54:06.590751 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
04:54:09.659658 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
04:54:10.579795 00:9e:1e:10:7f:69 (oui Unknown) > Broadcast, RRCP-0x23 reply
^C
3 packets captured
3 packets received by filter
0 packets dropped by kernel
```

