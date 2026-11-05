# Android本地认证[¶](https://mas.owasp.org/MASTG/Android/0x05f-Testing-Local-Authentication/#android-local-authentication) · part 2

> 分段 2/2。索引见 `Android本地认证.md`。

## 承接

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
