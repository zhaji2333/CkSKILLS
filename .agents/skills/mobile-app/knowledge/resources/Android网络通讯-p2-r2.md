# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 2 · part 2

> 分段 2/2。索引见 `Android网络通讯-p2.md`。

       // There is likely a man in the middle attack going on, be careful!
     } else if (message.indexOf("CONNECTION_FAILED") >- 1) {
       // There was no connection (yet). Internet may be down. Try again (a few times) after a little timeout.
     }
   }
```

解压 APK 文件后，Cordova/Phonegap 文件将位于 /assets/www 文件夹中。'plugins' 文件夹会让您看到所使用的插件。我们需要在应用程序的 JavaScript 代码中搜索此方法以确认其用法。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis_2)

按照[“测试端点识别验证 > 动态分析”](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-endpoint-identify-verification-mstg-network-3)中的说明进行操作。如果这样做不会导致流量被代理，则可能意味着实际上已实施证书固定并且所有安全措施都已到位。所有域都会发生同样的情况吗？

作为快速冒烟测试，您可以尝试使用[objection](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#objection)绕过证书固定，如[“绕过证书固定”](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#bypassing-certificate-pinning)中所述。被objectionHook的固定相关 API 应该出现在objection的输出中。

![反对 Android SSL Pinning 绕过](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/Images/Chapters/0x05b/android_ssl_pinning_bypass.png)

但是，请记住：

- API 可能不完整。
- 如果没有任何东西被钩住，那并不一定意味着该应用程序没有实现固定。

[在这两种情况下，应用程序或其某些组件可能会以 objection 支持](https://github.com/sensepost/objection/blob/master/agent/src/android/pinning.ts)的方式实现自定义固定。请查看静态分析部分以了解具体的固定指标和更深入的测试。

## 测试security providers (MSTG-NETWORK-6)[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#testing-the-security-provider-mstg-network-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#overview_2)

Android 依靠security providers来提供基于 SSL/TLS 的连接。设备附带的这种security providers（一个例子是[OpenSSL](https://www.openssl.org/news/vulnerabilities.html)）的问题是它经常有错误和/或漏洞。为避免已知漏洞，开发人员需要确保应用程序将安装适当的security providers。自 2016 年 7 月 11 日起，谷歌[一直拒绝](https://support.google.com/faqs/answer/6376725?hl=en)使用易受攻击的 OpenSSL 版本的 Play 商店应用程序提交（包括新应用程序和更新）。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#static-analysis_3)

基于Android SDK 的应用程序应该依赖于GooglePlayServices。例如，在 gradle 构建文件中，您会`compile 'com.google.android.gms:play-services-gcm:x.x.x'`在 dependencies 块中找到。您需要确保使用或`ProviderInstaller`调用该类。需要由应用程序的组件尽早调用。这些方法抛出的异常应该被正确捕获和处理。如果应用程序无法修补其security providers，它可以通知 API 其安全性较低的状态或限制用户操作（因为在这种情况下所有 HTTPS 流量都应被视为风险更高）。`installIfNeeded``installIfNeededAsync``ProviderInstaller`

[以下是Android 开发人员文档](https://developer.android.com/training/articles/security-gms-provider.html)中的两个示例，展示了如何更新security providers以防止 SSL 攻击。在这两种情况下，开发人员都需要正确处理异常，并且在应用程序使用未打补丁的security providers时向后端报告可能是明智的。

同步修补：

```
//this is a sync adapter that runs in the background, so you can run the synchronous patching.
public class SyncAdapter extends AbstractThreadedSyncAdapter {

  ...

  // This is called each time a sync is attempted; this is okay, since the
  // overhead is negligible if the security provider is up-to-date.
  @Override
  public void onPerformSync(Account account, Bundle extras, String authority,
      ContentProviderClient provider, SyncResult syncResult) {
    try {
      ProviderInstaller.installIfNeeded(getContext());
    } catch (GooglePlayServicesRepairableException e) {

      // Indicates that Google Play services is out of date, disabled, etc.

      // Prompt the user to install/update/enable Google Play services.
      GooglePlayServicesUtil.showErrorNotification(
          e.getConnectionStatusCode(), getContext());

      // Notify the SyncManager that a soft error occurred.
      syncResult.stats.numIOExceptions++;
      return;

    } catch (GooglePlayServicesNotAvailableException e) {
      // Indicates a non-recoverable error; the ProviderInstaller is not able
      // to install an up-to-date Provider.

      // Notify the SyncManager that a hard error occurred.
