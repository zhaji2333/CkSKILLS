# Android本地认证[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#android-local-authentication) · part 1 · part 1

> 分段 1/2。索引见 `Android本地认证-p1.md`。

# Android本地认证[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#android-local-authentication) · part 1

> 分段 1/2。索引见 `Android本地认证.md`。

# Android本地认证[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#android-local-authentication)

在本地身份验证期间，应用程序根据设备本地存储的凭据对用户进行身份验证。换句话说，用户通过提供有效的 PIN、密码或面部或指纹等生物特征来“解锁”应用程序或某些内层功能，这些特征通过引用本地数据进行验证。通常，这样做是为了让用户可以更方便地恢复与远程服务的现有会话，或者作为一种加强身份验证的方式来保护某些关键功能。

正如之前在“[移动应用程序身份验证架构](https://mas.owasp.org/MASTG/General/0x04e-Testing-Authentication-and-Session-Management/)”一章中所述：测试人员应该知道本地身份验证应该始终在远程端点或基于加密原语强制执行。如果身份验证过程没有返回数据，攻击者可以轻松绕过本地身份验证。

在 Android 中，Android Runtime(运行时)支持两种本地身份验证机制：确认凭证流程和生物识别身份验证流程。

## 测试确认凭据（MSTG-AUTH-1 和 MSTG-STORAGE-11）[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#testing-confirm-credentials-mstg-auth-1-and-mstg-storage-11)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#overview)

确认凭证流程自 Android 6.0 起可用，用于确保用户不必输入应用专用密码以及锁屏保护。相反：如果用户最近登录过设备，则可以使用 confirm-credentials 从`AndroidKeystore`. 也就是说，如果用户在设定的时限（`setUserAuthenticationValidityDurationSeconds`）内解锁了设备，否则需要再次解锁设备。

请注意，Confirm Credentials 的安全性仅与锁定屏幕上设置的保护一样强。这通常意味着使用简单的预测锁屏模式，因此我们不推荐任何需要 L2 安全控制才能使用确认凭证的应用程序。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#static-analysis)

确保锁定屏幕已设置：

```
KeyguardManager mKeyguardManager = (KeyguardManager) getSystemService(Context.KEYGUARD_SERVICE);
if (!mKeyguardManager.isKeyguardSecure()) {
    // Show a message that the user hasn't set up a lock screen.
}
```

- 创建受锁屏保护的密钥。为了使用这个密钥，用户需要在最后 X 秒内解锁设备，或者需要再次解锁设备。确保此超时时间不会太长，因为越来越难以确保使用该应用程序的用户与解锁设备的用户是同一用户：

  ```
  try {
      KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
      keyStore.load(null);
      KeyGenerator keyGenerator = KeyGenerator.getInstance(
              KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
  
      // Set the alias of the entry in Android KeyStore where the key will appear
      // and the constrains (purposes) in the constructor of the Builder
      keyGenerator.init(new KeyGenParameterSpec.Builder(KEY_NAME,
              KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
              .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
              .setUserAuthenticationRequired(true)
                      // Require that the user has unlocked in the last 30 seconds
              .setUserAuthenticationValidityDurationSeconds(30)
              .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
              .build());
      keyGenerator.generateKey();
  } catch (NoSuchAlgorithmException | NoSuchProviderException
          | InvalidAlgorithmParameterException | KeyStoreException
          | CertificateException | IOException e) {
      throw new RuntimeException("Failed to create a symmetric key", e);
  }
  ```

- 设置锁屏确认：

  ```
  private static final int REQUEST_CODE_CONFIRM_DEVICE_CREDENTIALS = 1; //used as a number to verify whether this is where the activity results from
  Intent intent = mKeyguardManager.createConfirmDeviceCredentialIntent(null, null);
  if (intent != null) {
      startActivityForResult(intent, REQUEST_CODE_CONFIRM_DEVICE_CREDENTIALS);
  }
  ```

- 锁屏后使用钥匙：

  ```
  @Override
  protected void onActivityResult(int requestCode, int resultCode, Intent data) {
      if (requestCode == REQUEST_CODE_CONFIRM_DEVICE_CREDENTIALS) {
          // Challenge completed, proceed with using cipher
          if (resultCode == RESULT_OK) {
              //use the key for the actual authentication flow
          } else {
              // The user canceled or didn’t complete the lock screen
              // operation. Go to error/cancellation flow.
          }
      }
  }
  ```

确保在申请流程中使用未锁定的密钥。例如，密钥可用于解密本地存储或从远程端点接收的消息。如果应用程序只是检查用户是否已解锁密钥，则应用程序可能容易受到本地身份验证绕过攻击。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#dynamic-analysis)

验证用户成功验证后授权使用密钥的持续时间（秒）。只有在使用时才需要`setUserAuthenticationRequired`。

## 测试生物认证 (MSTG-AUTH-8)[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#testing-biometric-authentication-mstg-auth-8)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#overview_1)

生物识别身份验证是一种方便的身份验证机制，但在使用时也会引入额外的攻击面。Android 开发人员文档提供了一个有趣的概述和[衡量生物识别解锁安全性](https://source.android.com/security/biometric/measure#strong-weak-unlocks)的指标。

Android 平台提供了三种不同的生物认证类：

- Android 10（API 级别 29）及更高版本：`BiometricManager`
- Android 9（API 级别 28）及更高版本：`BiometricPrompt`
- Android 6.0（API 级别 23）及更高版本：（`FingerprintManager`在 Android 9（API 级别 28）中已弃用）

![img](https://mas.owasp.org/assets/Images/Chapters/0x05f/biometricprompt-architecture.png)

该类[`BiometricManager`](https://developer.android.com/reference/kotlin/android/hardware/biometrics/BiometricManager)可用于验证设备上是否提供生物识别硬件以及是否由用户配置。如果是这种情况，该类[`BiometricPrompt`](https://developer.android.com/reference/kotlin/android/hardware/biometrics/BiometricPrompt)可用于显示系统提供的生物识别对话框。

该类`BiometricPrompt`是一项重大改进，因为它允许在 Android 上为生物识别身份验证提供一致的 UI，并且还支持更多的传感器，而不仅仅是指纹。

这与`FingerprintManager`仅支持指纹传感器而不提供 UI 的类不同，迫使开发人员构建自己的指纹 UI。

[Android 开发者博客](https://android-developers.googleblog.com/2019/10/one-biometric-api-over-all-android.html)上发布了 Android 生物识别 API 的非常详细的概述和解释。

#### FingerprintManager（在 Android 9（API 级别 28）中已弃用）[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#fingerprintmanager-deprecated-in-android-9-api-level-28)

Android 6.0（API 级别 23）引入了用于通过指纹对用户进行身份验证的公共 API，但在 Android 9（API 级别 28）中已弃用。通过[`FingerprintManager`](https://developer.android.com/reference/android/hardware/fingerprint/)类提供对指纹硬件的访问。应用程序可以通过实例化`FingerprintManager`对象并调用其`authenticate`方法来请求指纹身份验证。调用者注册回调方法来处理身份验证过程的可能结果（即成功、失败或错误）。请注意，此方法并不构成实际执行指纹身份验证的有力证据 - 例如，身份验证步骤可能会被攻击者修补，或者“成功”回调可能会使用动态检测过载。

`KeyGenerator`通过将指纹 API 与 Android类结合使用，您可以获得更好的安全性。通过这种方法，对称密钥存储在 Android KeyStore 中并使用用户的指纹解锁。例如，为了使用户能够访问远程服务，会创建一个 AES 密钥来加密身份验证令牌。通过在创建密钥时调用`setUserAuthenticationRequired(true)`，确保用户必须重新验证才能检索到它。然后可以将加密的身份验证令牌直接保存在设备上（例如通过Shared Preferences）。这种设计是一种相对安全的方式，可以确保用户实际输入的是经过授权的指纹。

一个更安全的选择是使用非对称加密。在这里，移动应用程序在 KeyStore 中创建一个非对称密钥对，并在服务器后端注册公钥。随后的交易使用私钥进行签名，并由服务器使用公钥进行验证。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#static-analysis_1)

请注意，有相当多的供应商/第三方 SDK 提供生物识别支持，但它们有自己的不安全性。使用第三方 SDK 处理敏感的身份验证逻辑时要非常谨慎。

以下部分解释了不同的生物识别身份验证类。

#### 生物特征库[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#biometric-library)

Android 提供了一个名为[Biometric](https://developer.android.com/jetpack/androidx/releases/biometric)的库，它提供了`BiometricPrompt`和`BiometricManager`API 的兼容版本，如 Android 10 中所实现的那样，具有回到 Android 6.0 (API 23) 的完整功能支持。

您可以在 Android 开发人员文档中找到有关如何[显示生物识别身份验证对话框的参考实现和说明。](https://developer.android.com/training/sign-in/biometric-auth)

类中有两种`authenticate`方法可用`BiometricPrompt`。其中之一需要一个[`CryptoObject`](https://developer.android.com/reference/android/hardware/biometrics/BiometricPrompt.CryptoObject.html)，它为生物识别身份验证增加了一层额外的安全性。

使用 CryptoObject 时，身份验证流程如下：

- 该应用程序在 KeyStore 中创建一个密钥`setUserAuthenticationRequired`并将其`setInvalidatedByBiometricEnrollment`设置为 true。此外，`setUserAuthenticationValidityDurationSeconds`应设置为 -1。
- 此密钥用于加密对用户进行身份验证的信息（例如会话信息或身份验证令牌）。
- 在从 KeyStore 释放密钥以解密数据之前，必须提供一组有效的生物识别信息，该数据通过`authenticate`方法和`CryptoObject`.
