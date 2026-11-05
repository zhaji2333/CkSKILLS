# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 3 · part 1

> 分段 1/2。索引见 `Android反逆向防御-p3.md`。

# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 3

> 分段 3/5。索引见 `Android反逆向防御.md`。

## 承接

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
