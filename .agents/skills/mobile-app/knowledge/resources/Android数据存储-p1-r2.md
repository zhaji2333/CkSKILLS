# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 1 · part 2

> 分段 2/2。索引见 `Android数据存储-p1.md`。

  .encryptionKey(getKey())
  .build();

Realm realm = Realm.getInstance(config);
```

如果数据库*未*加密，您应该能够获取数据。如果数据库*已*加密，请确定密钥是否在源或资源中进行了硬编码，以及它是否未受保护地存储在Shared Preferences或其他某个位置。

### 内部存储器(Internal Storage)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#internal-storage)

您可以将文件保存到设备的[内部存储器(Internal Storage)](https://developer.android.com/guide/topics/data/data-storage.html#filesInternal)中。保存到内部存储的文件默认是容器化的，不能被设备上的其他应用程序访问。当用户卸载您的应用程序时，这些文件将被删除。以下代码片段会将敏感数据持久存储到内部存储中。

Java 示例：

```
FileOutputStream fos = null;
try {
   fos = openFileOutput(FILENAME, Context.MODE_PRIVATE);
   fos.write(test.getBytes());
   fos.close();
} catch (FileNotFoundException e) {
   e.printStackTrace();
} catch (IOException e) {
   e.printStackTrace();
}
```

Kotlin的例子：

```
var fos: FileOutputStream? = null
fos = openFileOutput("FILENAME", Context.MODE_PRIVATE)
fos.write(test.toByteArray(Charsets.UTF_8))
fos.close()
```

您应该检查文件模式以确保只有应用程序可以访问该文件。您可以使用 设置此访问权限`MODE_PRIVATE`。`MODE_WORLD_READABLE`(deprecated) 和(deprecated)等模式`MODE_WORLD_WRITEABLE`可能会带来安全风险。

搜索类`FileInputStream`以找出在应用程序中打开和读取的文件。

### 外置储存(External Storage)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#external-storage)

每个 Android 兼容设备都支持[共享外部存储](https://developer.android.com/guide/topics/data/data-storage.html#filesExternal)。此存储可以是可移动的（例如 SD 卡）或内部的（不可移动的）。保存到外部存储的文件是全球可读的。启用 USB 大容量存储后，用户可以修改它们。您可以使用以下代码片段将敏感信息作为文件内容持久存储到外部存储器`password.txt`。

Java 示例：

```
File file = new File (Environment.getExternalFilesDir(), "password.txt");
String password = "SecretPassword";
FileOutputStream fos;
    fos = new FileOutputStream(file);
    fos.write(password.getBytes());
    fos.close();
```

Kotlin的例子：

```
val password = "SecretPassword"
val path = context.getExternalFilesDir(null)
val file = File(path, "password.txt")
file.appendText(password)
```

调用活动后，将创建文件并将数据存储在外部存储器中的明文文件中。

还值得注意的是，`data/data/<package-name>/`当用户卸载应用程序时，存储在应用程序文件夹 ( ) 之外的文件不会被删除。最后，值得注意的是，在某些情况下，攻击者可以使用外部存储来任意控制应用程序。有关详细信息：[请参阅 Checkpoint 的博客](https://blog.checkpoint.com/2018/08/12/man-in-the-disk-a-new-attack-surface-for-android-apps/)。

### 密钥库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#keystore)

[Android KeyStore](https://www.androidauthority.com/use-android-keystore-store-passwords-sensitive-information-623779/)支持相对安全的凭证存储。从 Android 4.3（API 级别 18）开始，它提供了用于存储和使用应用程序私钥的公共 API。应用程序可以使用公钥创建新的私钥/公钥对来加密应用程序机密，并且可以使用私钥解密机密。

您可以使用确认凭证流中的用户身份验证来保护存储在 Android KeyStore 中的密钥。用户的锁屏凭据（图案、PIN、密码或指纹）用于身份验证。

您可以在以下两种模式之一中使用存储的密钥：

1. 用户被授权在验证后的一段有限时间内使用密钥。在此模式下，只要用户解锁设备，就可以使用所有密钥。您可以自定义每个密钥的授权期限。仅当启用安全锁定屏幕时才能使用此选项。如果用户禁用安全锁屏，所有存储的密钥将永久失效。
2. 用户被授权使用与一个密钥关联的特定加密操作。在这种模式下，用户必须为涉及密钥的每个操作请求单独的授权。目前，指纹认证是请求此类授权的唯一方式。

Android KeyStore 提供的安全级别取决于它的实现，而这取决于设备。大多数现代设备都提供[硬件支持的 KeyStore 实现](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#hardware-backed-android-keyStore)：密钥在可信执行环境 (TEE) 或安全元件 (SE) 中生成和使用，操作系统无法直接访问它们。这意味着加密密钥本身无法轻易检索，即使是从已获得 root 权限的设备也是如此。[您可以使用密钥证明](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#key-attestation)来验证硬件支持的密钥您可以通过检查方法的返回值来确定密钥是否在安全硬件内部，该`isInsideSecureHardware`方法是[`KeyInfo`类](https://developer.android.com/reference/android/security/keystore/KeyInfo.html)的一部分。

> 请注意，相关的 KeyInfo 表明秘密密钥和 HMAC 密钥不安全地存储在多个设备上，尽管私钥已正确存储在安全硬件上。

纯软件实现的密钥使用[每个用户的加密主密钥进行加密](https://nelenkov.blogspot.sg/2013/08/credential-storage-enhancements-android-43.html)。攻击者可以访问存储在文件夹中具有此实现的 root 设备上的所有密钥`/data/misc/keystore/`。因为用户的锁屏密码/密码用于生成主密钥，所以当设备被锁定时，Android KeyStore 不可用。为了提高安全性，Android 9（API 级别 28）引入了该`unlockedDeviceRequired`标志。通过传递`true`给该`setUnlockedDeviceRequired`方法，应用程序可以防止其存储的密钥在`AndroidKeystore`设备锁定时被解密，并且它需要在允许解密之前解锁屏幕。

#### 硬件支持的 Android KeyStore[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#hardware-backed-android-keystore)

如前所述，硬件支持的 Android KeyStore 为 Android 的纵深防御安全概念提供了另一层。Android 6（API 级别 23）引入了 Keymaster 硬件抽象层 (HAL)。应用程序可以验证密钥是否存储在安全硬件中（通过检查是否`KeyInfo.isinsideSecureHardware`返回`true`）。运行 Android 9（API 级别 28）及更高版本的设备可以有一个`StrongBox Keymaster`模块，即驻留在硬件安全模块中的 Keymaster HAL 的实现，该模块具有自己的 CPU、安全存储、真正的随机数生成器和防止包篡改的机制. 要使用此功能，`true`必须在使用生成或导入密钥时传递给类或类`setIsStrongBoxBacked`中的方法`KeyGenParameterSpec.Builder``KeyProtection.Builder``AndroidKeystore`. 为确保在Runtime(运行时)使用 StrongBox，请检查是否`isInsideSecureHardware`返回，如果 StrongBox Keymaster 对于给定的算法和与密钥关联的密钥大小不可用，`true`系统不会抛出该异常。`StrongBoxUnavailableException`可以在[AOSP 页面](https://source.android.com/security/keystore)上找到基于硬件的密钥库的功能描述。

Keymaster HAL 是硬件支持组件（可信执行环境 (TEE) 或安全元件 (SE)）的接口，由 Android Keystore 使用。这种硬件支持组件的一个例子是[Titan](https://android-developers.googleblog.com/2018/10/building-titan-better-security-through.html) M。

#### 密钥认证[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#key-attestation)

对于严重依赖 Android Keystore 进行关键业务操作的应用程序，例如通过加密原语进行多因素身份验证，在客户端安全存储敏感数据等。Android 提供了[密钥证明](https://developer.android.com/training/articles/security-key-attestation)功能，有助于分析安全性通过 Android Keystore 管理的加密材料。从 Android 8.0（API 级别 26）开始，所有需要为 Google 应用程序进行设备认证的新设备（Android 7.0 或更高版本）都必须进行密钥证明。此类设备使用由[谷歌硬件认证根证书](https://developer.android.com/training/articles/security-key-attestation#root_certificate)签名的认证密钥，同样可以通过密钥认证过程进行验证。

在密钥证明期间，我们可以指定密钥对的别名，并作为回报，得到一个证书链，我们可以使用它来验证该密钥对的属性。如果链的根证书是[谷歌硬件证明根证书](https://developer.android.com/training/articles/security-key-attestation#root_certificate)，并且进行了与硬件中密钥对存储相关的检查，则可以保证设备支持硬件级密钥证明，并且密钥位于硬件支持的密钥库中谷歌认为是安全的。或者，如果证明链有任何其他根证书，则 Google 不会对硬件的安全性做出任何声明。

