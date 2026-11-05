# Android本地认证[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#android-local-authentication) · part 1 · part 2

> 分段 2/2。索引见 `Android本地认证-p1.md`。

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

