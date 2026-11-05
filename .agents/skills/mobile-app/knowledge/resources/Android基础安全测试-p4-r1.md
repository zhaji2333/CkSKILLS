# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 4 · part 1

> 分段 1/2。索引见 `Android基础安全测试-p4.md`。

# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 4

> 分段 4/5。索引见 `Android基础安全测试.md`。

##### 在虚拟设备上安装 CA 证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#installing-a-ca-certificate-on-the-virtual-device)

安装 CA 证书的一种简单方法是将证书推送到设备并通过安全设置将其添加到证书存储区。例如，您可以按如下方式安装 PortSwigger (Burp) CA 证书：

1. 启动 Burp 并使用主机上的 Web 浏览器导航到 burp/，然后`cacert.der`单击“CA 证书”按钮进行下载。

2. 将文件扩展名从更改`.der`为`.cer`.

3. 将文件推送到模拟器：

   ```
   adb push cacert.cer /sdcard/
   ```

4. 导航到**设置**->**安全**->**从 SD 卡安装**。

5. 向下滚动并点按`cacert.cer`。

然后系统会提示您确认安装证书（如果您还没有设置设备 PIN 码，系统还会要求您设置）。

这会将证书安装在用户证书存储中（在 Genymotion VM 上测试）。为了将证书放在Root存储中，您可以执行以下步骤：

1. `adb root`使用和以 root 身份运行 adb `adb shell`。
2. 在 找到新安装的证书`/data/misc/user/0/cacerts-added/`。
3. 将证书复制到以下文件夹`/system/etc/security/cacerts/`。
4. 重启Android虚拟机。

对于 Android 7.0（API 级别 24）及更高版本，请遵循“[绕过网络安全配置](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-the-network-security-configuration)”部分中描述的相同过程。

#### 物理设备的拦截代理[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#interception-proxy-for-a-physical-device)

必须首先评估可用的网络设置选项。用于测试的移动设备和运行拦截代理的主机必须连接到同一 Wi-Fi 网络。使用（现有的）接入点或创建[临时无线网络](https://portswigger.net/support/creating-an-ad-hoc-wireless-network-in-os-x)。

配置网络并在测试主机和移动设备之间建立连接后，还需要执行几个步骤。

- 代理必须[配置为指向拦截代理](https://portswigger.net/support/configuring-an-android-device-to-work-with-burp)。
- 拦截代理的[CA 证书必须添加到 Android 设备证书存储中的受信任证书中](https://portswigger.net/support/installing-burp-suites-ca-certificate-in-an-android-device)。用于存储 CA 证书的菜单的位置可能取决于 Android 版本和 Android OEM 对设置菜单的修改。
- 某些应用程序（例如[Chrome 浏览器](https://bugs.chromium.org/p/chromium/issues/detail?id=475745)）可能会显示`NET::ERR_CERT_VALIDITY_TOO_LONG`错误，如果叶证书的有效期恰好延长了特定时间（Chrome 为 39 个月）。如果使用默认的 Burp CA 证书，就会发生这种情况，因为 Burp Suite 颁发的叶证书与其 CA 证书具有相同的有效性。您可以通过创建自己的 CA 证书并将其导入 Burp Suite 来规避此问题，如本[博](https://blog.nviso.be/2018/01/31/using-a-custom-root-ca-with-burp-for-inspecting-android-n-traffic/)文中所述。

完成这些步骤并启动应用程序后，请求应显示在拦截代理中。

> [在secure.force.com](https://security.secure.force.com/security/tools/webapp/zapandroidsetup)上可以找到使用 Android 设备设置[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)的视频。

其他一些差异：从 Android 8.0（API 级别 26）开始，当 HTTPS 流量通过另一个连接隧道传输时，应用程序的网络行为会发生变化。从 Android 9（API 级别 28）开始，当握手期间出现问题时，SSLSocket 和 SSLEngine 在错误处理方面的行为会有所不同。

如前所述，从 Android 7.0（API 级别 24）开始，Android 操作系统将默认不再信任用户 CA 证书，除非在应用程序中指定。在下一节中，我们将介绍两种绕过此 Android 安全控制的方法。

#### 绕过网络安全配置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-the-network-security-configuration)

在本节中，我们将介绍几种绕过 Android[网络安全配置](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-security-configuration)的方法。

##### 将自定义用户证书添加到网络安全配置[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#adding-custom-user-certificates-to-the-network-security-configuration)

网络安全配置有不同的配置可用于通过 src 属性[添加非系统证书颁发机构：](https://developer.android.com/training/articles/security-config#CustomTrust)

```
<certificates src=["system" | "user" | "raw resource"]
              overridePins=["true" | "false"] />
```

每个证书可以是以下之一：

- `"raw resource"`是指向包含 X.509 证书的文件的 ID
- `"system"`对于预装的系统 CA 证书
- `"user"`对于用户添加的 CA 证书

App信任的CA证书可以是系统信任CA，也可以是用户CA。通常，您已经将拦截代理的证书添加为 Android 中的附加 CA。因此，我们将重点关注“用户”设置，它允许您使用以下网络安全配置强制 Android 应用程序信任此证书：

```
<network-security-config>
   <base-config>
      <trust-anchors>
          <certificates src="system" />
          <certificates src="user" />
      </trust-anchors>
   </base-config>
</network-security-config>
```

要实施此新设置，您必须按照以下步骤操作：

- 使用 apktool 等反编译工具反编译应用程序：

  ```
  apktool d <filename>.apk
  ```

- 通过创建包含`<certificates src="user" />`如上所述的网络安全配置，使应用程序信任用户证书

- 在反编译应用程序时进入apktool创建的目录并使用apktool重建应用程序。新的 apk 将在`dist`目录中。

  ```
  apktool b
  ```

- 您需要重新打包应用程序，如“逆向工程和篡改”一章的“[重新打包](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#repackaging)”部分所述。有关重新打包过程的更多详细信息，您还可以查阅[Android 开发人员文档](https://developer.android.com/studio/publish/app-signing#signing-manually)，该文档解释了整个过程。

请注意，即使此方法非常简单，其主要缺点是您必须对要评估的每个应用程序应用此操作，这会增加测试开销。

> 请记住，如果您正在测试的应用程序有额外的强化措施，例如验证应用程序签名，您可能无法再启动该应用程序。作为重新打包的一部分，您将使用自己的密钥对应用程序进行签名，因此签名更改将导致触发此类检查，从而可能导致应用程序立即终止。您需要通过在应用程序重新打包期间修补它们或通过 Frida 进行动态检测来识别和禁用此类检查。

有一个 python 脚本可以自动执行上述步骤，称为[Android-CertKiller](https://github.com/51j0/Android-CertKiller)。这个 Python 脚本可以从已安装的 Android 应用程序中提取 APK、反编译、使其可调试、添加允许用户证书的新网络安全配置、构建和签署新 APK 并使用 SSL 绕过安装新 APK。

```
python main.py -w

***************************************
Android CertKiller (v0.1)
***************************************

CertKiller Wizard Mode
---------------------------------
List of devices attached
4200dc72f27bc44d    device

---------------------------------

Enter Application Package Name: nsc.android.mstg.owasp.org.android_nsc

Package: /data/app/nsc.android.mstg.owasp.org.android_nsc-1/base.apk

I. Initiating APK extraction from device
   complete
------------------------------
I. Decompiling
   complete
------------------------------
I. Applying SSL bypass
   complete
------------------------------
I. Building New APK
   complete
------------------------------
I. Signing APK
   complete
------------------------------

Would you like to install the APK on your device(y/N): y
------------------------------------
 Installing Unpinned APK
------------------------------
Finished
```

##### 使用 MAGISK 在系统信任的 CA 中添加代理的证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#adding-the-proxys-certificate-among-system-trusted-cas-using-magisk)

为了避免为每个应用程序配置网络安全配置的义务，我们必须强制设备接受代理的证书作为系统信任的证书之一。

有一个[Magisk 模块](https://github.com/NVISO-BE/MagiskTrustUserCerts)会自动将所有用户安装的 CA 证书添加到系统信任的 CA 列表中。

[在Github 发布页面](https://github.com/NVISO-BE/MagiskTrustUserCerts/releases)下载最新版本的模块，将下载的文件推送到设备并通过单击`+`按钮将其导入 Magisk Manager 的“模块”视图。最后，Magisk Manager 需要重启才能让更改生效。

从现在开始，用户通过“设置”、“安全和位置”、“加密和凭据”、“从存储安装”（位置可能不同）安装的任何 CA 证书都会由此自动推送到系统的信任库中魔力模块。重新启动并验证 CA 证书是否列在“设置”、“安全和位置”、“加密和凭据”、“受信任的凭据”（位置可能不同）中。

##### 在系统信任的 CA 中手动添加 PROXY 的证书[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#manually-adding-the-proxys-certificate-among-system-trusted-cas)

或者，您可以手动执行以下步骤以获得相同的结果：

- 使 /system 分区可写，这只有在有Root设备上才有可能。运行“mount”命令以确保 /system 是可写的：`mount -o rw,remount /system`。如果此命令失败，请尝试运行以下命令`mount -o rw,remount -t ext4 /system`

- 准备代理的 CA 证书以匹配系统证书格式。以格式导出代理的证书`der`（这是 Burp Suite 中的默认格式），然后运行以下命令：

  ```
  $ openssl x509 -inform DER -in cacert.der -out cacert.pem
  $ openssl x509 -inform PEM -subject_hash_old -in cacert.pem | head -1
  mv cacert.pem <hash>.0
  ```

- 最后，将该`<hash>.0`文件复制到目录 /system/etc/security/cacerts 中，然后运行以下命令：

  ```
  chmod 644 <hash>.0
  ```

通过执行上述步骤，您允许任何应用程序信任代理的证书，这允许您拦截其流量，当然除非应用程序使用 SSL 固定。

### 潜在障碍[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#potential-obstacles)

