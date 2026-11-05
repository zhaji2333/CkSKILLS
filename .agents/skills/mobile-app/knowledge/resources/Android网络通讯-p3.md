# Android网络通讯[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-network-communication) · part 3

> 分段 3/3。索引见 `Android网络通讯.md`。

## 承接

      //in this case: make sure that you inform your API of it.
      syncResult.stats.numAuthExceptions++;
      return;
    }

    // If this is reached, you know that the provider was already up-to-date,
    // or was successfully updated.
  }
}
```

异步修补：

```
//This is the mainactivity/first activity of the application that's there long enough to make the async installing of the securityprovider work.
public class MainActivity extends Activity
    implements ProviderInstaller.ProviderInstallListener {

  private static final int ERROR_DIALOG_REQUEST_CODE = 1;

  private boolean mRetryProviderInstall;

  //Update the security provider when the activity is created.
  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    ProviderInstaller.installIfNeededAsync(this, this);
  }

  /**
   * This method is only called if the provider is successfully updated
   * (or is already up-to-date).
   */
  @Override
  protected void onProviderInstalled() {
    // Provider is up-to-date, app can make secure network calls.
  }

  /**
   * This method is called if updating fails; the error code indicates
   * whether the error is recoverable.
   */
  @Override
  protected void onProviderInstallFailed(int errorCode, Intent recoveryIntent) {
    if (GooglePlayServicesUtil.isUserRecoverableError(errorCode)) {
      // Recoverable error. Show a dialog prompting the user to
      // install/update/enable Google Play services.
      GooglePlayServicesUtil.showErrorDialogFragment(
          errorCode,
          this,
          ERROR_DIALOG_REQUEST_CODE,
          new DialogInterface.OnCancelListener() {
            @Override
            public void onCancel(DialogInterface dialog) {
              // The user chose not to take the recovery action
              onProviderInstallerNotAvailable();
            }
          });
    } else {
      // Google Play services is not available.
      onProviderInstallerNotAvailable();
    }
  }

  @Override
  protected void onActivityResult(int requestCode, int resultCode,
      Intent data) {
    super.onActivityResult(requestCode, resultCode, data);
    if (requestCode == ERROR_DIALOG_REQUEST_CODE) {
      // Adding a fragment via GooglePlayServicesUtil.showErrorDialogFragment
      // before the instance state is restored throws an error. So instead,
      // set a flag here, which will cause the fragment to delay until
      // onPostResume.
      mRetryProviderInstall = true;
    }
  }

  /**
   * On resume, check to see if we flagged that we need to reinstall the
   * provider.
   */
  @Override
  protected void onPostResume() {
    super.onPostResult();
    if (mRetryProviderInstall) {
      // We can now safely retry installation.
      ProviderInstall.installIfNeededAsync(this, this);
    }
    mRetryProviderInstall = false;
  }

  private void onProviderInstallerNotAvailable() {
    // This is reached if the provider cannot be updated for some reason.
    // App should consider all HTTP communication to be vulnerable, and take
    // appropriate action (e.g. inform backend, block certain high-risk actions, etc.).
  }
}
```

确保基于 NDK 的应用程序仅绑定到最新且已正确修补的库，该库提供 SSL/TLS 功能。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#dynamic-analysis_3)

当你有源代码时：

- 在调试模式下运行应用程序，然后在应用程序将首先联系端点的位置创建一个断点。
- 右键单击突出显示的代码并选择`Evaluate Expression`。
- 键入`Security.getProviders()`并按回车键。
- 检查提供商并尝试查找`GmsCore_OpenSSL`，这应该是新的排名靠前的提供商。

当您没有源代码时：

- 使用 Xposed Hook到`java.security`包中，然后`java.security.Security`使用方法Hook`getProviders`（不带参数）。返回值将是一个数组`Provider`。
- 确定第一个提供者是否是`GmsCore_OpenSSL`。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#owasp-masvs)

- MSTG-NETWORK-1：“数据在网络上使用 TLS 加密。整个应用程序始终使用安全通道。”
- MSTG-NETWORK-2：“TLS 设置符合当前最佳实践，或者如果移动操作系统不支持推荐标准，则尽可能接近。”
- MSTG-NETWORK-3：“应用程序在建立安全通道时验证远程端点的 X.509 证书。只接受由受信任的 CA 签名的证书。”
- MSTG-NETWORK-4：“该应用程序要么使用自己的证书存储，要么固定端点证书或公钥，随后不会与提供不同证书或密钥的端点建立连接，即使由受信任的 CA 签名也是如此。”
- MSTG-NETWORK-6：“该应用程序仅依赖于最新的连接和安全库。”

### Android开发者文档[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#android-developer-documentation)

- 网络安全配置 - https://developer.android.com/training/articles/security-config
- 网络安全配置（缓存替代）- [https://webcache.googleusercontent.com/search?q=cache:hOONLxvMTwYJ:https://developer.android.com/training/articles/security-config+&cd=10&hl=nl&ct= clnk&gl=nl](https://webcache.googleusercontent.com/search?q=cache:hOONLxvMTwYJ:https://developer.android.com/training/articles/security-config+&cd=10&hl=nl&ct=clnk&gl=nl)

### Xamarin 证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#xamarin-certificate-pinning)

- 使用 Xamarin 固定证书和公钥 - https://thomasbandt.com/certificate-and-public-key-pinning-with-xamarin
- ServicePointManager - https://msdn.microsoft.com/en-us/library/system.net.servicepointmanager(v=vs.110).aspx

### Cordova 证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05g-Testing-Network-Communication/#cordova-certificate-pinning)

- PhoneGap SSL 证书检查器插件 - https://github.com/EddyVerbruggen/SSLCertificateChecker-PhoneGap-Plugin
