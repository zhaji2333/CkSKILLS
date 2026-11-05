# Android基础安全测试[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#android-basic-security-testing) · part 5

> 分段 5/5。索引见 `Android基础安全测试.md`。

## 承接

另请参阅[Objection 关于为 Android 禁用 SSL Pinning 的帮助以](https://github.com/sensepost/objection/blob/master/objection/console/helpfiles/android.sslpinning.disable.txt)获取更多信息，并检查[pinning.ts](https://github.com/sensepost/objection/blob/master/agent/src/android/pinning.ts)文件以了解旁路的工作原理。

#### 静态绕过自定义证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypass-custom-certificate-pinning-statically)

在应用程序的某处，必须定义端点和证书（或其哈希）。反编译应用程序后，您可以搜索：

- 证书哈希：`grep -ri "sha256\|sha1" ./smali`. 用您的代理 CA 的哈希值替换已识别的哈希值。或者，如果哈希伴随着域名，您可以尝试将域名修改为不存在的域，以便不固定原始域。这适用于混淆的 OkHTTP 实现。
- 证书文件：`find ./assets -type f \( -iname \*.cer -o -iname \*.crt \)`. 用您代理的证书替换这些文件，确保它们的格式正确。
- 信任库文件：`find ./ -type f \( -iname \*.jks -o -iname \*.bks \)`. 将代理的证书添加到信任库并确保它们的格式正确。

> 请记住，应用程序可能包含没有扩展名的文件。最常见的文件位置是`assets`和`res`目录，也应该对其进行调查。

例如，假设您找到一个使用 BKS (BouncyCastle) 信任库的应用程序并且它存储在文件`res/raw/truststore.bks`. 要绕过 SSL Pinning，您需要使用命令行工具将代理的证书添加到信任库`keytool`。`Keytool`Java SDK自带，执行命令需要以下值：

- password - 密钥库的密码。在反编译的应用程序代码中查找硬编码密码。
- providerpath - BouncyCastle Provider jar 文件的位置。您可以从[The Legion of the Bouncy Castle](https://www.bouncycastle.org/latest_releases.html)下载它。
- proxy.cer - 您的代理证书。
- aliascert - 将用作代理证书别名的唯一值。

要添加代理的证书，请使用以下命令：

```
keytool -importcert -v -trustcacerts -file proxy.cer -alias aliascert -keystore "res/raw/truststore.bks" -provider org.bouncycastle.jce.provider.BouncyCastleProvider -providerpath "providerpath/bcprov-jdk15on-164.jar" -storetype BKS -storepass password
```

要列出 BKS 信任库中的证书，请使用以下命令：

```
keytool -list -keystore "res/raw/truststore.bks" -provider org.bouncycastle.jce.provider.BouncyCastleProvider -providerpath "providerpath/bcprov-jdk15on-164.jar"  -storetype BKS -storepass password
```

进行这些修改后，使用 apktool 重新打包应用程序并将其安装到您的设备上。

如果应用程序使用本地库来实现网络通信，则需要进一步进行逆向工程。可以在博客文章[识别 smali 代码中的 SSL Pinning 逻辑、修补它并重新组装 APK中找到这种方法的示例](https://serializethoughts.wordpress.com/2016/08/18/bypassing-ssl-pinning-in-android-applications/)

#### 动态绕过自定义证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypass-custom-certificate-pinning-dynamically)

动态绕过固定逻辑使其更加方便，因为无需绕过任何完整性检查，并且执行试错尝试要快得多。

找到正确的Hook方法通常是最困难的部分，并且可能需要相当长的时间，具体取决于混淆程度。由于开发人员通常会重用现有库，因此搜索标识所用库的字符串和许可文件是一种很好的方法。确定库后，检查未混淆的源代码以找到适合动态检测的方法。

例如，假设您找到一个使用混淆的 OkHTTP3 库的应用程序。[文档](https://square.github.io/okhttp/3.x/okhttp/)显示该类`CertificatePinner.Builder`负责为特定域添加引脚。如果您可以修改[Builder.add 方法](https://square.github.io/okhttp/3.x/okhttp/okhttp3/CertificatePinner.Builder.html#add-java.lang.String-java.lang.String...-)的参数，则可以将散列更改为属于您的证书的正确散列。可以通过两种方式找到正确的方法，正如Jeroen Beckers在[这篇博文中所解释的那样：](https://blog.nviso.eu/2019/04/02/circumventing-ssl-pinning-in-obfuscated-apps-with-okhttp/)

- 按照上一节中的说明搜索哈希和域名。实际固定方法通常会在这些字符串附近使用或定义
- 在 SMALI 代码中搜索方法签名

对于 Builder.add 方法，您可以通过运行以下 grep 命令找到可能的方法：`grep -ri java/lang/String;\[Ljava/lang/String;)L ./`

此命令将搜索所有将字符串和字符串变量列表作为参数的方法，并返回一个复杂对象。Root据应用程序的大小，代码中可能有一个或多个匹配项。

使用 Frida Hook每个方法并打印参数。其中一个将打印出域名和证书哈希，之后您可以修改参数以规避已实施的固定。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#references)

- 手动签名（Android 开发人员文档）- https://developer.android.com/studio/publish/app-signing#signing-manually
- 自定义信任 - https://developer.android.com/training/articles/security-config#CustomTrust
- Android 网络安全配置培训 - https://developer.android.com/training/articles/security-config
- Android P 网络安全配置安全分析师指南 - [https://www.nowsecure.com/blog/2018/08/15/a-security-analysts-guide-to-network-security-configuration-in-android-p /](https://www.nowsecure.com/blog/2018/08/15/a-security-analysts-guide-to-network-security-configuration-in-android-p/)
- Android 8.0 行为变化 - https://developer.android.com/about/versions/oreo/android-8.0-changes
- Android 9.0 行为变更 - https://developer.android.com/about/versions/pie/android-9.0-changes-all#device-security-changes
- 代号、标签和版本号 - https://source.android.com/setup/start/build-numbers
- 创建和管理虚拟设备 - https://developer.android.com/studio/run/managing-avds.html
- 移动设备Root指南 - https://www.xda-developers.com/root/
- API 级别 - https://developer.android.com/guide/topics/manifest/uses-sdk-element#ApiLevels
- AssetManager - https://developer.android.com/reference/android/content/res/AssetManager
- SharedPreferences API - https://developer.android.com/training/basics/data-storage/shared-preferences.html
- 使用 Logcat 调试 - https://developer.android.com/studio/command-line/logcat
- Android 的 APK 格式 - https://en.wikipedia.org/wiki/Apk_(file_format)
- 使用 Tcpdump、nc 和 Wireshark 进行 Android 远程嗅探 - https://blog.dornea.nu/2015/02/20/android-remote-sniffing-using-tcpdump-nc-and-wireshark/
- 无线客户端隔离 - https://documentation.meraki.com/MR/Firewall_and_Traffic_Shaping/Wireless_Client_Isolation
