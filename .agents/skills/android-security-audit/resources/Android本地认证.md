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
- 无法绕过此解决方案，即使在已获得 root 权限的设备上也是如此，因为来自 KeyStore 的密钥只能在成功进行生物识别身份验证后使用。

如果`CryptoObject`未用作身份验证方法的一部分，则可以使用 Frida 绕过它。有关详细信息，请参阅“动态检测”部分。

开发人员可以使用 Android 提供的多个[验证类](https://source.android.com/security/biometric#validation)来测试其应用程序中生物识别身份验证的实现。

#### 指纹管理器[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#fingerprintmanager)

> 本节介绍如何使用`FingerprintManager`该类实现生物认证。请记住，此类已弃用，应使用[生物识别库作为最佳实践。](https://developer.android.com/jetpack/androidx/releases/biometric)本节仅供参考，以防遇到这样的实现需要分析。

首先搜索`FingerprintManager.authenticate`呼叫。传递给此方法的第一个参数应该是一个`CryptoObject`实例，它是FingerprintManager 支持的[加密对象的包装类。](https://developer.android.com/reference/android/hardware/fingerprint/FingerprintManager.CryptoObject.html)如果该参数设置为`null`，这意味着指纹授权纯粹是事件绑定的，可能会产生安全问题。

用于初始化密码包装器的密钥的创建可以追溯到`CryptoObject`. 验证密钥`KeyGenerator`除了`setUserAuthenticationRequired(true)`在创建对象期间被调用外，还使用该类创建`KeyGenParameterSpec`（请参见下面的代码示例）。

确保验证身份验证逻辑。为了使身份验证成功，远程端点**必须**要求客户端提供从 KeyStore 检索到的秘密、从秘密派生的值或用客户端私钥签名的值（见上文）。

安全地实施指纹认证需要遵循一些简单的原则，首先检查该类型的认证是否可用。在最基本的方面，设备必须运行 Android 6.0 或更高版本 (API 23+)。还必须验证其他四个先决条件：

- 必须在 Android Manifest 中请求权限：

  ```
  <uses-permission
      android:name="android.permission.USE_FINGERPRINT" />
  ```

- 指纹硬件必须可用：

  ```
  FingerprintManager fingerprintManager = (FingerprintManager)
                  context.getSystemService(Context.FINGERPRINT_SERVICE);
  fingerprintManager.isHardwareDetected();
  ```

- 用户必须有一个受保护的锁屏：

  ```
  KeyguardManager keyguardManager = (KeyguardManager) context.getSystemService(Context.KEYGUARD_SERVICE);
  keyguardManager.isKeyguardSecure();  //note if this is not the case: ask the user to setup a protected lock screen
  ```

- 至少应注册一根手指：

  ```
  fingerprintManager.hasEnrolledFingerprints();
  ```

- 该应用程序应有权要求提供用户指纹：

  ```
  context.checkSelfPermission(Manifest.permission.USE_FINGERPRINT) == PermissionResult.PERMISSION_GRANTED;
  ```

如果上述任何检查失败，则不应提供指纹认证选项。

请务必记住，并非所有 Android 设备都提供硬件支持的密钥存储。该类`KeyInfo`可用于查明密钥是否位于安全硬件内，例如可信执行环境 (TEE) 或安全元件 (SE)。

```
SecretKeyFactory factory = SecretKeyFactory.getInstance(getEncryptionKey().getAlgorithm(), ANDROID_KEYSTORE);
KeyInfo secetkeyInfo = (KeyInfo) factory.getKeySpec(yourencryptionkeyhere, KeyInfo.class);
secetkeyInfo.isInsideSecureHardware()
```

在某些系统上，也可以通过硬件实施生物特征认证策略。这是通过以下方式检查的：

```
keyInfo.isUserAuthenticationRequirementEnforcedBySecureHardware();
```

下面介绍如何使用对称密钥对进行指纹认证。

指纹认证可以通过使用类创建一个新的 AES 密钥来实现，方法是`KeyGenerator`添加`setUserAuthenticationRequired(true)`.`KeyGenParameterSpec.Builder`

```
generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, KEYSTORE);

generator.init(new KeyGenParameterSpec.Builder (KEY_ALIAS,
        KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
        .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
        .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
        .setUserAuthenticationRequired(true)
        .build()
);

generator.generateKey();
```

要使用受保护的密钥执行加密或解密，请创建一个`Cipher`对象并使用密钥别名对其进行初始化。

```
SecretKey keyspec = (SecretKey)keyStore.getKey(KEY_ALIAS, null);

if (mode == Cipher.ENCRYPT_MODE) {
    cipher.init(mode, keyspec);
```

请记住，不能立即使用新密钥 - 它必须先通过身份验证`FingerprintManager`。这涉及在识别之前将传递到的`Cipher`对象包装起来。`FingerprintManager.CryptoObject``FingerprintManager.authenticate`

```
cryptoObject = new FingerprintManager.CryptoObject(cipher);
fingerprintManager.authenticate(cryptoObject, new CancellationSignal(), 0, this, null);
```

`onAuthenticationSucceeded(FingerprintManager.AuthenticationResult result)`认证成功时调用回调方法。`CryptoObject`然后可以从结果中检索经过身份验证的。

```
public void authenticationSucceeded(FingerprintManager.AuthenticationResult result) {
    cipher = result.getCryptoObject().getCipher();

    //(... do something with the authenticated cipher object ...)
}
```

下面介绍如何使用非对称密钥对进行指纹认证。

要使用非对称加密实现指纹认证，首先使用`KeyPairGenerator`该类创建一个签名密钥，然后将公钥注册到服务器。然后，您可以通过在客户端上签名并在服务器上验证签名来验证数据片段。可以在[Android 开发人员博客](https://android-developers.googleblog.com/2015/10/new-in-android-samples-authenticating.html)中找到使用指纹 API 向远程服务器进行身份验证的详细示例。

密钥对生成如下：

```
KeyPairGenerator.getInstance(KeyProperties.KEY_ALGORITHM_EC, "AndroidKeyStore");
keyPairGenerator.initialize(
        new KeyGenParameterSpec.Builder(MY_KEY,
                KeyProperties.PURPOSE_SIGN)
                .setDigests(KeyProperties.DIGEST_SHA256)
                .setAlgorithmParameterSpec(new ECGenParameterSpec("secp256r1"))
                .setUserAuthenticationRequired(true)
                .build());
keyPairGenerator.generateKeyPair();
```

要使用密钥进行签名，您需要实例化一个 CryptoObject 并通过`FingerprintManager`.

```
Signature.getInstance("SHA256withECDSA");
KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
keyStore.load(null);
PrivateKey key = (PrivateKey) keyStore.getKey(MY_KEY, null);
signature.initSign(key);
CryptoObject cryptoObject = new FingerprintManager.CryptoObject(signature);

CancellationSignal cancellationSignal = new CancellationSignal();
FingerprintManager fingerprintManager =
        context.getSystemService(FingerprintManager.class);
fingerprintManager.authenticate(cryptoObject, cancellationSignal, 0, this, null);
```

您现在可以`inputBytes`按如下方式对字节数组的内容进行签名。

```
Signature signature = cryptoObject.getSignature();
signature.update(inputBytes);
byte[] signed = signature.sign();
```

- 请注意，在交易已签名的情况下，应生成一个随机随机数并将其添加到已签名的数据中。否则，攻击者可以重放交易。
- 要使用对称指纹身份验证实现身份验证，请使用质询-响应协议。

#### 额外的安全功能[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#additional-security-features)

Android 7.0（API 级别 24）将`setInvalidatedByBiometricEnrollment(boolean invalidateKey)`方法添加到`KeyGenParameterSpec.Builder`. 当`invalidateKey`值设置为`true`（默认值）时，在登记新指纹时，对指纹认证有效的密钥将不可逆转地失效。这可以防止攻击者检索他们的密钥，即使他们能够注册额外的指纹也是如此。

Android 8.0（API 级别 26）添加了两个额外的错误代码：

- `FINGERPRINT_ERROR_LOCKOUT_PERMANENT`：用户尝试使用指纹读取器解锁设备的次数过多。
- `FINGERPRINT_ERROR_VENDOR`：发生特定于供应商的指纹读取器错误。

#### 第三方 SDK[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#third-party-sdks)

确保指纹认证和/或其他类型的生物识别认证完全基于 Android SDK 及其 API。如果不是这种情况，请确保替代 SDK 已针对任何弱点进行了适当审查。确保 SDK 由 TEE/SE 提供支持，TEE/SE 会根据生物识别身份验证解锁（加密）秘密。这个秘密不应该被任何其他东西解锁，而是一个有效的生物识别条目。这样，指纹逻辑就永远不会被绕过。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#dynamic-analysis_1)

请查看[这篇关于 Android KeyStore 和生物识别身份验证的详细博客文章](https://labs.withsecure.com/blog/how-secure-is-your-android-keystore-authentication)。这项研究包括两个 Frida 脚本，可用于测试生物识别身份验证的不安全实现并尝试绕过它们：

- [指纹绕过](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass.js)：当类的方法中`CryptoObject`未使用时，此 Frida 脚本将绕过身份验证。身份验证实现依赖于被调用的回调。`authenticate``BiometricPrompt``onAuthenticationSucceded`
- [通过异常处理绕过指纹](https://github.com/FSecureLABS/android-keystore-audit/blob/master/frida-scripts/fingerprint-bypass-via-exception-handling.js)：此 Frida 脚本将在使用时尝试绕过身份验证`CryptoObject`，但使用方式不正确。详细解释可以在博文中的“加密对象异常处理”部分找到。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#owasp-masvs)

- MSTG-AUTH-1：“如果应用程序为用户提供对远程服务的访问权限，则在远程端点执行某种形式的身份验证，例如用户名/密码身份验证。”
- MSTG-AUTH-8：“生物识别身份验证（如果有的话）不是事件绑定的（即使用简单返回“真”或“假”的 API）。相反，它基于解锁钥匙串/密钥库。”
- MSTG-STORAGE-11：“该应用程序执行最低限度的设备访问安全策略，例如要求用户设置设备密码。”

### 请求应用程序权限[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#request-app-permissions)

- Runtime(运行时)权限 - https://developer.android.com/training/permissions/requesting
