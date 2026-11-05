# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 4 · part 2

> 分段 2/2。索引见 `Android反逆向防御-p4.md`。

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
