# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage)

保护身份验证令牌、私人信息和其他敏感数据是移动安全的关键。在本章中，您将了解 Android 为本地数据存储提供的 API 以及使用它们的最佳实践。

保存数据的准则可以很容易地概括为：公共数据应该对每个人都可用，但必须保护敏感和私有数据，或者更好的是，将其排除在设备存储之外。

本章分为两节，第一节从安全角度着重介绍数据存储理论，并简要说明和示例 Android 上的各种数据存储方法。

第二部分侧重于通过使用静态和动态分析的测试用例来测试这些数据存储解决方案。

## 理论概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#theory-overview)

[存储数据](https://developer.android.com/guide/topics/data/data-storage.html)对许多移动应用程序来说都是必不可少的。传统观点认为，应将尽可能少的敏感数据存储在永久本地存储中。然而，在大多数实际场景中，必须存储某种类型的用户数据。例如，就可用性而言，每次启动应用程序时要求用户输入非常复杂的密码并不是一个好主意。大多数应用程序必须在本地缓存某种身份验证令牌以避免这种情况。如果给定场景需要，也可以保存个人身份信息 (PII) 和其他类型的敏感数据。

如果敏感数据没有受到持续存储它的应用程序的适当保护，那么它很容易受到攻击。该应用程序可能能够将数据存储在多个位置，例如，在设备上或外部 SD 卡上。当您尝试利用这些类型的问题时，请考虑可能会在不同位置处理和存储大量信息。

首先，重要的是要确定移动应用程序处理的信息类型和用户输入的信息类型。接下来，确定哪些可以被视为对攻击者有价值的敏感数据（例如，密码、信用卡信息、PII）并不总是一项微不足道的任务，它在很大程度上取决于目标应用程序的上下文。[您可以在“移动应用程序安全测试”一章的“识别敏感数据](https://mas.owasp.org/MASTG/General/0x04b-Mobile-App-Security-Testing/#identifying-sensitive-data)”部分找到有关数据分类的更多详细信息。有关 Android 数据存储安全的一般信息，请参阅Android 开发人员指南中的[存储数据安全提示。](https://developer.android.com/training/articles/security-tips.html#StoringData)

披露敏感信息会产生多种后果，包括解密信息。通常，攻击者可能会识别此信息并将其用于其他攻击，例如社会工程（如果 PII 已被泄露）、帐户劫持（如果会话信息或身份验证令牌已被泄露），以及从具有以下权限的应用程序收集信息：支付选项（攻击和滥用他们）。

除了保护敏感数据之外，您还需要确保从任何存储源读取的数据都经过验证并可能经过清理。验证的范围通常从检查正确的数据类型到使用额外的加密控制，例如 HMAC，您可以验证数据的完整性。

## 数据存储方法概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#data-storage-methods-overview)

Android根据用户、开发人员和应用程序的需要提供了多种[数据存储方法。](https://developer.android.com/guide/topics/data/data-storage.html)例如，某些应用程序使用数据存储来跟踪用户设置或用户提供的数据。可以通过多种方式为这个用例持久存储数据。以下列出了 Android 平台上广泛使用的持久性存储技术：

- Shared Preferences
- SQLite 数据库
- Firebase Databases
- Realm Databases
- 内部存储器(Internal Storage)
- 外置储存(External Storage)
- 密钥库

除此之外，Android 中还有许多为各种用例构建的其他功能，这些功能也可能导致数据存储，也应分别进行测试，例如：

- 记录功能
- Android备份
- 进程内存
- 键盘缓存
- 截图

了解每个相关的数据存储功能对于正确执行适当的测试用例非常重要。本概述旨在提供这些数据存储方法中的每一种的简要概述，以及点测试人员进一步相关的文档。

### Shared Preferences[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#shared-preferences)

[SharedPreferences](https://developer.android.com/training/data-storage/shared-preferences) API 通常用于永久保存键值对的小型集合。存储在 SharedPreferences 对象中的数据被写入纯文本 XML 文件。SharedPreferences 对象可以声明为全球可读（所有应用程序均可访问）或私有。滥用 SharedPreferences API 通常会导致敏感数据暴露。考虑以下示例：

Java 示例：

```
SharedPreferences sharedPref = getSharedPreferences("key", MODE_WORLD_READABLE);
SharedPreferences.Editor editor = sharedPref.edit();
editor.putString("username", "administrator");
editor.putString("password", "supersecret");
editor.commit();
```

Kotlin的例子：

```
var sharedPref = getSharedPreferences("key", Context.MODE_WORLD_READABLE)
var editor = sharedPref.edit()
editor.putString("username", "administrator")
editor.putString("password", "supersecret")
editor.commit()
```

调用活动后，将使用提供的数据创建文件 key.xml。此代码违反了多项最佳实践。

- 用户名和密码以明文形式存储在`/data/data/<package-name>/shared_prefs/key.xml`.

```
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
  <string name="username">administrator</string>
  <string name="password">supersecret</string>
</map>
```

- `MODE_WORLD_READABLE`允许所有应用程序访问和读取`key.xml`.

```
root@hermes:/data/data/sg.vp.owasp_mobile.myfirstapp/shared_prefs # ls -la
-rw-rw-r-- u0_a118    170 2016-04-23 16:51 key.xml
```

> 请注意，从 API 级别 17 开始弃用`MODE_WORLD_READABLE`和`MODE_WORLD_WRITEABLE`。虽然较新的设备可能不会受此影响，但如果应用程序`android:targetSdkVersion`在 Android 4.2（API 级别 17）之前发布的操作系统版本上运行，则使用小于 17 的值编译的应用程序可能会受到影响).

### 数据库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#databases)

Android 平台提供了前面列表中提到的许多数据库选项。每个数据库选项都有自己需要了解的怪癖和方法。

#### SQLite 数据库（未加密）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#sqlite-database-unencrypted)

SQLite 是一种将数据存储在`.db`文件中的 SQL 数据库引擎。Android SDK[内置了](https://developer.android.com/training/data-storage/sqlite)对 SQLite 数据库的支持。用于管理数据库的主要包是`android.database.sqlite`. 例如，您可以使用以下代码在活动中存储敏感信息：

Java 中的示例：

```
SQLiteDatabase notSoSecure = openOrCreateDatabase("privateNotSoSecure", MODE_PRIVATE, null);
notSoSecure.execSQL("CREATE TABLE IF NOT EXISTS Accounts(Username VARCHAR, Password VARCHAR);");
notSoSecure.execSQL("INSERT INTO Accounts VALUES('admin','AdminPass');");
notSoSecure.close();
```

Kotlin 中的示例：

```
var notSoSecure = openOrCreateDatabase("privateNotSoSecure", Context.MODE_PRIVATE, null)
notSoSecure.execSQL("CREATE TABLE IF NOT EXISTS Accounts(Username VARCHAR, Password VARCHAR);")
notSoSecure.execSQL("INSERT INTO Accounts VALUES('admin','AdminPass');")
notSoSecure.close()
```

调用活动后，将使用提供的数据创建数据库文件`privateNotSoSecure`并将其存储在明文文件`/data/data/<package-name>/databases/privateNotSoSecure`中。

除了 SQLite 数据库之外，数据库的目录可能包含几个文件：

- [日志文件](https://www.sqlite.org/tempfiles.html)：这些是用于实现原子提交和回滚的临时文件。
- [锁定文件](https://www.sqlite.org/lockingv3.html)：锁定文件是锁定和日志功能的一部分，旨在提高 SQLite 并发性并减少写入器饥饿问题。

敏感信息不应存储在未加密的 SQLite 数据库中。

#### SQLite 数据库（加密）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#sqlite-databases-encrypted)

使用库[SQLCipher](https://www.zetetic.net/sqlcipher/sqlcipher-for-android/)，可以对 SQLite 数据库进行密码加密。

Java 中的示例：

```
SQLiteDatabase secureDB = SQLiteDatabase.openOrCreateDatabase(database, "password123", null);
secureDB.execSQL("CREATE TABLE IF NOT EXISTS Accounts(Username VARCHAR,Password VARCHAR);");
secureDB.execSQL("INSERT INTO Accounts VALUES('admin','AdminPassEnc');");
secureDB.close();
```

Kotlin 中的示例：

```
var secureDB = SQLiteDatabase.openOrCreateDatabase(database, "password123", null)
secureDB.execSQL("CREATE TABLE IF NOT EXISTS Accounts(Username VARCHAR,Password VARCHAR);")
secureDB.execSQL("INSERT INTO Accounts VALUES('admin','AdminPassEnc');")
secureDB.close()
```

检索数据库密钥的安全方法包括：

- 打开应用程序后要求用户使用 PIN 或密码解密数据库（弱密码和 PIN 容易受到暴力攻击）
- 将密钥存储在服务器上并只允许从网络服务访问它（这样应用程序只能在设备在线时使用）

#### Firebase 实时数据库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#firebase-real-time-databases)

Firebase 是一个拥有超过 15 种产品的开发平台，其中之一就是 Firebase Real-time Database。应用程序开发人员可以利用它来存储数据并与 NoSQL 云托管数据库同步。数据以 JSON 格式存储，并实时同步到每个连接的客户端，即使在应用程序离线时也仍然可用。

可以通过进行以下网络调用来识别配置错误的 Firebase 实例：

```
https://_firebaseProjectName_.firebaseio.com/.json
```

可以通过对应用程序进行逆向工程从移动应用程序中检索*firebaseProjectName 。*或者，分析师可以使用[Firebase Scanner](https://github.com/shivsahni/FireBaseScanner)，这是一个自动执行上述任务的 python 脚本，如下所示：

```
python FirebaseScanner.py -p <pathOfAPKFile>

python FirebaseScanner.py -f <commaSeperatedFirebaseProjectNames>
```

#### Realm Databases[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#realm-databases)

[Java Realm Databases](https://mongodb.com/docs/realm/sdk/java/)在开发人员中越来越受欢迎。数据库及其内容可以使用存储在配置文件中的密钥进行加密。

```
//the getKey() method either gets the key from the server or from a KeyStore, or is derived from a password.
RealmConfiguration config = new RealmConfiguration.Builder()
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

虽然密钥证明过程可以直接在应用程序中实现，但出于安全原因，建议在服务器端实现。以下是安全实施密钥证明的高级指南：

- 服务器应通过使用 CSPRNG（加密安全随机数生成器）安全地创建随机数来启动密钥证明过程，并将该随机数作为质询发送给用户。

- 客户端应`setAttestationChallenge`使用从服务器收到的质询调用 API，然后应使用该`KeyStore.getCertificateChain`方法检索证明证书链。

- 应将证明响应发送到服务器进行验证，并应执行以下检查以验证密钥证明响应：

- 验证证书链，直到根并执行证书健全性检查，例如有效性、完整性和可信度。如果链中的证书都没有被撤销，请检查由 Google 维护的[证书撤销状态列表。](https://developer.android.com/training/articles/security-key-attestation#root_certificat)

- 检查根证书是否使用谷歌证明根密钥签名，这使得证明过程值得信赖。

- 提取证明

  证书扩展数据

  ，它出现在证书链的第一个元素中，并执行以下检查：

  - 验证证明质询是否具有与启动证明过程时在服务器上生成的相同的值。
  - 验证密钥证明响应中的签名。
  - 验证 Keymaster 的安全级别以确定设备是否具有安全密钥存储机制。Keymaster 是一款在安全上下文中运行并提供所有安全密钥库操作的软件。安全级别将是`Software`或`TrustedEnvironment`之一`StrongBox`。`TrustedEnvironment`如果安全级别为或`StrongBox`且证明证书链包含使用 Google 证明根密钥签名的根证书，则客户端支持硬件级密钥证明。
  - 验证客户端的状态以确保完整的信任链 - 验证启动密钥、锁定引导加载程序和验证启动状态。
  - 此外，您还可以验证密钥对的属性，例如用途、访问时间、身份验证要求等。

> 请注意，如果由于任何原因该过程失败，则意味着密钥不在安全硬件中。这并不意味着密钥已泄露。

Android Keystore 认证响应的典型示例如下所示：

```
{
    "fmt": "android-key",
    "authData": "9569088f1ecee3232954035dbd10d7cae391305a2751b559bb8fd7cbb229bd...",
    "attStmt": {
        "alg": -7,
        "sig": "304402202ca7a8cfb6299c4a073e7e022c57082a46c657e9e53...",
        "x5c": [
            "308202ca30820270a003020102020101300a06082a8648ce3d040302308188310b30090603550406130...",
            "308202783082021ea00302010202021001300a06082a8648ce3d040302308198310b300906035504061...",
            "3082028b30820232a003020102020900a2059ed10e435b57300a06082a8648ce3d040302308198310b3..."
        ]
    }
}
```

在上面的 JSON 片段中，密钥具有以下含义： `fmt`：证明语句格式标识符 `authData`：它表示证明的身份验证器数据 `alg`：用于签名的算法 `sig`：签名 `x5c`：证明证书链

注意：`sig`是通过连接`authData`和`clientDataHash`（服务器发送的质询）生成的，并使用签名算法通过凭据私钥进行`alg`签名，并在服务器端使用第一个证书中的公钥对其进行验证。

如需更多了解实施指南，可参考[Google Sample Code 。](https://github.com/googlesamples/android-key-attestation/blob/master/server/src/main/java/com/android/example/KeyAttestationExample.java)

从安全分析的角度来看，分析师可以对密钥证明的安全实施执行以下检查：

- 检查密钥证明是否完全在客户端实现。在这种情况下，可以通过篡改应用程序、方法Hook等方式轻松绕过。
- 检查服务器在启动密钥证明时是否使用随机质询。因为不这样做会导致不安全的实施，从而使其容易受到重放攻击。此外，应执行与挑战的随机性有关的检查。
- 检查服务器是否验证密钥证明响应的完整性。
- 检查服务器是否对链上证书进行完整性验证、信任验证、有效性等基本检查。

#### 安全密钥导入到密钥库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#secure-key-import-into-keystore)

Android 9（API 级别 28）添加了将密钥安全导入到`AndroidKeystore`. 首先`AndroidKeystore`生成一个密钥对，使用`PURPOSE_WRAP_KEY`它也应该用证明证书保护，这对旨在保护导入到的密钥`AndroidKeystore`。加密密钥生成为 ASN.1 编码消息，其`SecureKeyWrapper`格式还包含对允许使用导入密钥的方式的描述。然后，密钥在`AndroidKeystore`属于生成包装密钥的特定设备的硬件内部被解密，因此它们永远不会以明文形式出现在设备的主机内存中。

![将密钥安全导入 Keystore](https://mas.owasp.org/assets/Images/Chapters/0x05d/Android9_secure_key_import_to_keystore.jpg)

Java 中的示例：

```
KeyDescription ::= SEQUENCE {
    keyFormat INTEGER,
    authorizationList AuthorizationList
}

SecureKeyWrapper ::= SEQUENCE {
    wrapperFormatVersion INTEGER,
    encryptedTransportKey OCTET_STRING,
    initializationVector OCTET_STRING,
    keyDescription KeyDescription,
    secureKey OCTET_STRING,
    tag OCTET_STRING
}
```

上面的代码显示了在生成 SecureKeyWrapper 格式的加密密钥时要设置的不同参数。查看 Android 文档以[`WrappedKeyEntry`](https://developer.android.com/reference/android/security/keystore/WrappedKeyEntry)获取更多详细信息。

在定义 KeyDescription AuthorizationList 时，以下参数将影响加密密钥的安全性：

- 参数指定使用密钥的`algorithm`加密算法
- 参数指定密钥的`keySize`大小（以位为单位），以密钥算法的正常方式测量
- 该`digest`参数指定可与密钥一起使用以执行签名和验证操作的摘要算法

#### 较旧的 KeyStore 实现[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#older-keystore-implementations)

较旧的 Android 版本不包含 KeyStore，但它们*确实*包含来自 JCA（Java 加密体系结构）的 KeyStore 接口。您可以使用实现此接口的 KeyStore 来确保使用 KeyStore 存储的密钥的保密性和完整性；建议使用 BouncyCastle KeyStore (BKS)。所有实现都基于文件存储在文件系统上这一事实；所有文件均受密码保护。要创建一个，您可以使用`KeyStore.getInstance("BKS", "BC") method`，其中“BKS”是 KeyStore 名称 (BouncyCastle Keystore)，“BC”是提供者 (BouncyCastle)。您还可以使用 SpongyCastle 作为包装器并按如下方式初始化 KeyStore `KeyStore.getInstance("BKS", "SC")`：

请注意，并非所有 KeyStore 都能正确保护存储在 KeyStore 文件中的密钥。

#### 钥匙链[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#keychain)

[KeyChain 类](https://developer.android.com/reference/android/security/KeyChain.html)用于存储和检索*系统范围内的*私钥及其相应的证书（链）。如果首次将某些内容导入 KeyChain，系统将提示用户设置锁屏 PIN 码或密码以保护凭据存储。请注意，KeyChain 是系统范围的，每个应用程序都可以访问存储在 KeyChain 中的资料。

检查源代码以确定原生 Android 机制是否识别敏感信息。敏感信息应该加密，而不是以明文形式存储。对于必须存储在设备上的敏感信息，可以使用多个 API 调用来通过`KeyChain`类保护数据。完成以下步骤：

- 确保该应用使用 Android KeyStore 和 Cipher 机制在设备上安全地存储加密信息。寻找模式`AndroidKeystore`, `import java.security.KeyStore`, `import javax.crypto.Cipher`, `import java.security.SecureRandom`, 和相应的用法。
- 使用该`store(OutputStream stream, char[] password)`函数将 KeyStore 存储到带有密码的磁盘。确保密码由用户提供，而不是硬编码。

#### 存储加密密钥：技术[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-a-cryptographic-key-techniques)

为了减少在 Android 设备上未经授权使用密钥的情况，Android KeyStore 允许应用程序在生成或导入密钥时指定对其密钥的授权使用。授权一旦做出，便无法更改。

存储密钥——从最安全到最不安全：

- 密钥存储在硬件支持的 Android KeyStore 中
- 所有密钥都存储在服务器上，经过强认证后可用
- 主密钥存储在服务器上，用于加密存储在 Android SharedPreferences 中的其他密钥
- 密钥每次都来自强大的用户提供的具有足够长度和盐的密码
- 密钥存储在 Android KeyStore 的软件实现中
- master key 存储在 Android Keystore 的软件实现中，用于加密存储在 SharedPreferences 中的其他密钥
- 【不推荐】所有key都存储在SharedPreferences中
- [不推荐] 在源代码中硬编码加密密钥
- 【不推荐】基于稳定属性的可预测混淆函数或密钥推导函数
- [不推荐] 将生成的密钥存储在公共场所（如`/sdcard/`）

##### 使用硬件支持的 ANDROID KEYSTORE 存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-using-hardware-backed-android-keystore)

如果设备运行的是 Android 7.0（API 级别 24）及更高版本且具有可用的硬件组件（可信执行环境 (TEE) 或安全元件 (SE)），您可以使用[硬件支持的 Android KeyStore 。](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#hardware-backed-android-keystore)[您甚至可以使用为密钥证明的安全实施](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#key-attestation)提供的指南来验证密钥是否由硬件支持。如果硬件组件不可用和/或需要支持 Android 6.0（API 级别 23）及以下版本，那么您可能希望将密钥存储在远程服务器上并在身份验证后使其可用。

##### 在服务器上存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-on-the-server)

可以将密钥安全地存储在密钥管理服务器上，但是应用程序需要在线才能解密数据。这可能是某些移动应用程序用例的限制，应该仔细考虑，因为这会成为应用程序架构的一部分，并且可能会严重影响可用性。

##### 从用户输入派生密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#deriving-keys-from-user-input)

从用户提供的密码派生密钥是一种常见的解决方案（取决于您使用的 Android API 级别），但它也会影响可用性，可能会影响攻击面并可能引入其他弱点。

每次应用程序需要执行加密操作时，都需要用户的密码。要么每次都提示用户输入它，这不是理想的用户体验，要么只要用户通过身份验证，密码就会保存在内存中。将密码短语保存在内存中并不是最佳做法，因为任何加密材料只能在使用时保存在内存中。[如“清理密钥材料”](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cleaning-out-key-material)中所述，将密钥清零通常是一项非常具有挑战性的任务。

此外，请考虑从密码派生的密钥有其自身的弱点。例如，密码或密码短语可能会被用户重复使用或容易被猜到。请参阅[测试密码学章节](https://mas.owasp.org/MASTG/General/0x04g-Testing-Cryptography/#weak-key-generation-functions)以获取更多信息。

##### 清理密钥材料[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cleaning-out-key-material)

一旦不再需要密钥材料，就应将其从内存中清除。在使用垃圾收集器 (Java) 和不可变字符串（Swift、Objective-C、Kotlin）的语言中，真正清理秘密数据存在一定的局限性。[Java Cryptography Architecture Reference Guide](https://docs.oracle.com/en/java/javase/16/security/java-cryptography-architecture-jca-reference-guide.html#GUID-C9F76AFB-6B20-45A7-B84F-96756C8A94B4)建议使用`char[]`instead of`String`来存储敏感数据，并在使用后使数组无效。

请注意，某些密码没有正确清理其字节数组。例如，BouncyCastle 中的 AES 密码并不总是清理其最新的工作密钥，在内存中留下一些字节数组的副本。接下来，如果不付出额外的努力，就无法将基于 BigInteger 的密钥（例如私钥）从堆中移除或清零。清除字节数组可以通过编写一个实现[Destroyable](https://docs.oracle.com/javase/8/docs/api/javax/security/auth/Destroyable.html#destroy--)的包装器来实现。

##### 使用 ANDROID KEYSTORE API 存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-using-android-keystore-api)

更人性化和推荐的方法是使用[Android KeyStore API](https://developer.android.com/reference/java/security/KeyStore.html)系统（本身或通过 KeyChain）来存储密钥材料。如果可能，应使用硬件支持的存储。否则，它应该回退到 Android Keystore 的软件实现。但是，请注意，`AndroidKeyStore`在不同版本的 Android 中，API 已发生重大变化。在早期版本中，`AndroidKeyStore`API 仅支持存储公钥/私钥对（例如，RSA）。自 Android 6.0（API 级别 23）起才添加对称密钥支持。因此，开发人员需要处理不同的 Android API 级别以安全地存储对称密钥。

##### 通过使用其他密钥加密来存储密钥[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-keys-by-encrypting-them-with-other-keys)

为了在运行 Android 5.1（API 级别 22）或更低版本的设备上安全地存储对称密钥，我们需要生成一个公钥/私钥对。我们使用公钥加密对称密钥并将私钥存储在`AndroidKeyStore`. 加密的对称密钥可以使用 base64 编码并存储在`SharedPreferences`. 每当我们需要对称密钥时，应用程序都会从中检索私钥`AndroidKeyStore`并解密对称密钥。

信封加密或密钥包装是一种类似的方法，它使用对称加密来封装密钥材料。数据加密密钥 (DEK) 可以使用安全存储的密钥加密密钥 (KEK) 进行加密。加密的 DEK 可以存储在文件中`SharedPreferences`或写入文件。需要时，应用程序读取 KEK，然后解密 DEK。请参阅[OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html#encrypting-stored-keys)以了解有关加密密钥的更多信息。

此外，作为此方法的说明，请参阅[androidx.security.crypto 包中的 EncryptedSharedPreferences](https://developer.android.com/jetpack/androidx/releases/security)。

##### 存储密钥的不安全选项[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#insecure-options-to-store-keys)

存储加密密钥的安全性较低的方法是在 Android 的 SharedPreferences 中。使用[SharedPreferences](https://developer.android.com/reference/android/content/SharedPreferences.html)时，文件只能由创建它的应用程序读取。但是，在有Root设备上，任何其他具有根访问权限的应用程序都可以简单地读取其他应用程序的 SharedPreference 文件。AndroidKeyStore 不是这种情况。由于 AndroidKeyStore 访问是在内核级别管理的，因此需要相当多的工作和技巧才能在 AndroidKeyStore 不清除或破坏密钥的情况下绕过。

最后三个选项是在源代码中使用硬编码的加密密钥，具有可预测的混淆功能或基于稳定属性的密钥派生功能，并将生成的密钥存储在公共场所，如`/sdcard/`. 硬编码加密密钥是一个问题，因为这意味着应用程序的每个实例都使用相同的加密密钥。攻击者可以对应用程序的本地副本进行逆向工程以提取加密密钥，并使用该密钥解密任何设备上应用程序加密的任何数据。

接下来，当您具有基于标识符的可预测密钥派生函数时，其他应用程序可以访问该函数，攻击者只需找到 KDF 并将其应用于设备即可找到密钥。最后，公开存储加密密钥也是非常不鼓励的，因为其他应用程序可能有权读取公共分区并窃取密钥。

#### 第三方库[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-libraries)

有几个不同的开源库提供特定于 Android 平台的加密功能。

- **[Java AES Crypto](https://github.com/tozny/java-aes-crypto)** - 一个简单的 Android 类，用于加密和解密字符串。
- **[SQL Cipher](https://www.zetetic.net/sqlcipher/sqlcipher-for-android/)** - SQLCipher 是 SQLite 的开源扩展，提供透明的 256 位 AES 数据库文件加密。
- **[Secure Preferences](https://github.com/scottyab/secure-preferences)** - Android Shared preference wrapper 比加密 Shared Preferences 的键和值。
- **[Themis](https://github.com/cossacklabs/themis)** - 一个跨平台的高级加密库，它在许多平台上提供相同的 API，用于在身份验证、存储、消息传递等过程中保护数据。

> 请记住，只要密钥未存储在 KeyStore 中，就始终可以轻松地在获得 root 权限的设备上检索密钥，然后解密您试图保护的值。

### 日志[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#logs)

在移动设备上创建日志文件有很多正当理由，例如跟踪崩溃、错误和使用情况统计信息。当应用程序离线时，日志文件可以存储在本地，并在应用程序在线时发送到端点。但是，记录敏感数据可能会将数据暴露给攻击者或恶意应用程序，并且还可能侵犯用户机密。您可以通过多种方式创建日志文件。以下列表包括两个可用于 Android 的类：

- [日志类](https://developer.android.com/reference/android/util/Log.html)
- [记录器类](https://developer.android.com/reference/java/util/logging/Logger.html)

### 备份[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#backups)

Android 为用户提供了自动备份功能。备份通常包括所有已安装应用程序的数据和设置副本。鉴于其多样化的生态系统，Android 支持许多备份选项：

- Stock Android 具有内置的 USB 备份功能。启用USB调试后，您可以使用该`adb backup`命令创建完整数据备份和应用程序数据目录的备份。
- Google 提供了“备份我的数据”功能，可以将所有应用程序数据备份到 Google 的服务器。
- 应用程序开发人员可以使用两个备份 API：
- [键/值备份](https://developer.android.com/guide/topics/data/keyvaluebackup.html)（备份 API 或 Android 备份服务）上传到 Android 备份服务云。
- [应用程序自动备份](https://developer.android.com/guide/topics/data/autobackup.html)：在 Android 6.0（API 级别 23）及更高版本中，Google 添加了“应用程序自动备份”功能。此功能会自动将最多 25MB 的应用程序数据与用户的 Google Drive 帐户同步。
- OEM 可能会提供其他选项。例如，HTC 设备有一个“HTC 备份”选项，激活后可以每天备份到云端。

应用程序必须小心确保敏感的用户数据不会在这些备份中结束，因为这可能允许攻击者提取它。

### 进程内存[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#process-memory)

Android 上的所有应用程序都使用内存来执行正常的计算操作，就像任何普通的现代计算机一样。因此，有时会在进程内存中执行敏感操作也就不足为奇了。出于这个原因，重要的是一旦处理了相关的敏感数据，就应该尽快将其从进程内存中清除。

可以通过内存转储和通过调试器实时分析内存来调查应用程序的内存。

这在“测试敏感数据的内存”部分中有进一步解释。

## 测试敏感数据的本地存储（MSTG-STORAGE-1 和 MSTG-STORAGE-2）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-local-storage-for-sensitive-data-mstg-storage-1-and-mstg-storage-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview)

此测试用例侧重于识别应用程序存储的潜在敏感数据并验证它是否安全存储。应执行以下检查：

- 分析源代码中的数据存储。
- 确保触发应用程序中所有可能的功能（例如，通过单击所有可能的地方）以确保数据生成。
- 检查所有应用程序生成和修改的文件，并确保存储方法足够安全。
- 这包括 SharedPreferences、SQL 数据库、Realm Databases、内部存储、外部存储等。

一般来说，存储在设备本地的敏感数据至少应该加密，并且任何用于加密方法的密钥都应该安全地存储在 Android Keystore 中。这些文件也应该存储在应用程序沙箱中。如果应用程序可以实现，敏感数据应该存储在设备之外，或者更好的是，根本不存储。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis)

首先，尝试确定 Android 应用程序使用的存储类型，并找出该应用程序是否以不安全的方式处理敏感数据。

- 检查`AndroidManifest.xml`读/写外部存储权限，例如，`uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"`.
- 检查用于存储数据的关键字和 API 调用的源代码：
- 文件权限，例如：
  - `MODE_WORLD_READABLE`或`MODE_WORLD_WRITABLE`：您应该避免对文件使用`MODE_WORLD_WRITEABLE`and `MODE_WORLD_READABLE`，因为任何应用程序都可以读取或写入文件，即使它们存储在应用程序的私有数据目录中。如果必须与其他应用程序共享数据，请考虑使用内容提供程序。Content Provider(内容提供者)向其他应用程序提供读写权限，并且可以根据具体情况授予动态权限。
- 类和函数，例如：
  - `SharedPreferences`类（存储键值对）
  - 类`FileOutPutStream`（使用内部或外部存储）
  - 功能（使用`getExternal*`外部存储）
  - `getWritableDatabase`函数（返回一个用于写入的 SQLiteDatabase ）
  - 函数（返回一个用于读取的`getReadableDatabase`SQLiteDatabase）
  - the `getCacheDir`and`getExternalCacheDirs`函数（使用缓存文件）

加密应该使用经过验证的 SDK 函数来实现。下面描述了在源代码中查找的不良做法：

- 本地存储的敏感信息通过异或或位翻转等简单位操作“加密”。应避免这些操作，因为加密数据很容易恢复。
- 在没有 Android 板载功能（例如 Android KeyStore）的情况下使用或创建的密钥
- 通过硬编码公开的密钥

典型的误用是硬编码加密密钥。硬编码和世界可读的加密密钥显着增加了恢复加密数据的可能性。一旦攻击者获得了数据，对其进行解密就变得轻而易举了。对称加密密钥必须存储在设备上，因此识别它们只是时间和精力的问题。考虑以下代码：

```
this.db = localUserSecretStore.getWritableDatabase("SuperPassword123");
```

获取密钥很简单，因为它包含在源代码中并且对于应用程序的所有安装都是相同的。以这种方式加密数据没有好处。寻找硬编码的 API 密钥/私钥和其他有价值的数据；他们构成了类似的风险。编码/加密密钥代表了另一种尝试，使获得皇冠上的珠宝变得更难但并非不可能。

考虑以下代码：

Java 中的示例：

```
//A more complicated effort to store the XOR'ed halves of a key (instead of the key itself)
private static final String[] myCompositeKey = new String[]{
  "oNQavjbaNNSgEqoCkT9Em4imeQQ=","3o8eFOX4ri/F8fgHgiy/BS47"
};
```

Kotlin 中的示例：

```
private val myCompositeKey = arrayOf<String>("oNQavjbaNNSgEqoCkT9Em4imeQQ=", "3o8eFOX4ri/F8fgHgiy/BS47")
```

解码原始密钥的算法可能是这样的：

Java 中的示例：

```
public void useXorStringHiding(String myHiddenMessage) {
  byte[] xorParts0 = Base64.decode(myCompositeKey[0],0);
  byte[] xorParts1 = Base64.decode(myCompositeKey[1],0);

  byte[] xorKey = new byte[xorParts0.length];
  for(int i = 0; i < xorParts1.length; i++){
    xorKey[i] = (byte) (xorParts0[i] ^ xorParts1[i]);
  }
  HidingUtil.doHiding(myHiddenMessage.getBytes(), xorKey, false);
}
```

Kotlin 中的示例：

```
fun useXorStringHiding(myHiddenMessage:String) {
  val xorParts0 = Base64.decode(myCompositeKey[0], 0)
  val xorParts1 = Base64.decode(myCompositeKey[1], 0)
  val xorKey = ByteArray(xorParts0.size)
  for (i in xorParts1.indices)
  {
    xorKey[i] = (xorParts0[i] xor xorParts1[i]).toByte()
  }
  HidingUtil.doHiding(myHiddenMessage.toByteArray(), xorKey, false)
}
```

验证秘密的常见位置：

- 资源（通常位于 res/values/strings.xml）示例：

```
<resources>
    <string name="app_name">SuperApp</string>
    <string name="hello_world">Hello world!</string>
    <string name="action_settings">Settings</string>
    <string name="secret_key">My_Secret_Key</string>
  </resources>
```

- 构建配置，例如 local.properties 或 gradle.properties 示例：

```
buildTypes {
  debug {
    minifyEnabled true
    buildConfigField "String", "hiddenPassword", "\"${hiddenPassword}\""
  }
}
```

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis)

安装和使用该应用程序，至少执行一次所有功能。数据可以在用户输入时生成，由端点发送，或随应用程序一起发送。然后完成以下操作：

- 检查内部和外部本地存储中是否包含应用程序创建的包含敏感数据的任何文件。
- 识别不应包含在生产版本中的开发文件、备份文件和旧文件。
- 确定 SQLite 数据库是否可用以及它们是否包含敏感信息。SQLite 数据库存储在`/data/data/<package-name>/databases`.
- 确定 SQLite 数据库是否已加密。如果是这样，请确定数据库密码是如何生成和存储的，以及它是否如密钥库概述的“[存储密钥](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#storing-a-key)”部分中所述受到充分保护。
- 检查存储为 XML 文件（在 中`/data/data/<package-name>/shared_prefs`）的Shared Preferences以获取敏感信息。默认情况下，Shared Preferences是不安全且未加密的。某些应用程序可能会选择使用[安全首选项](https://github.com/scottyab/secure-preferences)来加密存储在Shared Preferences中的值。
- 检查 中文件的权限`/data/data/<package-name>`。只有安装应用程序时创建的用户和组（例如 u0_a82）才应该具有用户读取、写入和执行权限 ( `rwx`)。其他用户不应该有访问文件的权限，但他们可能有目录的执行权限。
- 检查任何 Firebase 实时数据库的使用情况，并尝试通过进行以下网络调用来确定它们是否配置错误：
- `https://_firebaseProjectName_.firebaseio.com/.json`
- 判断 Realm 数据库是否可用`/data/data/<package-name>/files/`，是否未加密，是否包含敏感信息。默认情况下，文件扩展名是`realm`，文件名是`default`。[使用领域浏览器](https://github.com/realm/realm-browser-osx)检查Realm Databases。

## 测试本地存储以进行输入验证 (MSTG-PLATFORM-2)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-local-storage-for-input-validation-mstg-platform-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_1)

对于任何可公开访问的数据存储，任何进程都可以覆盖数据。这意味着需要在再次读回数据时应用输入验证。

> 注意：类似的情况适用于 root 设备上的私人可访问数据

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_1)

#### 使用Shared Preferences[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#using-shared-preferences)

当您使用`SharedPreferences.Editor`读取或写入 int/boolean/long 值时，您无法检查数据是否被覆盖。然而：除了链接值外，它几乎不能用于实际攻击（例如，不能打包额外的漏洞来接管控制流）。在 a`String`或 a的情况下，`StringSet`您应该注意数据的解释方式。使用基于反射的持久化？查看 Android 的“测试对象持久性”部分，了解应如何对其进行验证。使用`SharedPreferences.Editor`来存储和读取证书或密钥？确保你已经修补了你的Security Provider给定的漏洞，例如在[Bouncy Castle](https://www.cvedetails.com/cve/CVE-2018-1000613/)中发现的漏洞。

在所有情况下，对内容进行 HMACed 有助于确保未应用任何添加和/或更改。

#### 使用其他存储机制[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#using-other-storage-mechanisms)

如果使用其他公共存储机制（而不是`SharedPreferences.Editor`），则需要在从存储机制读取数据时验证数据。

## 敏感数据测试日志 (MSTG-STORAGE-3)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-logs-for-sensitive-data-mstg-storage-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_2)

此测试用例侧重于识别系统和应用程序日志中的任何敏感应用程序数据。应执行以下检查：

- 分析日志相关代码的源代码。
- 检查日志文件的应用程序数据目录。
- 收集系统消息和日志并分析任何敏感数据。

作为避免潜在的敏感应用程序数据泄漏的一般建议，应从生产版本中删除日志记录语句，除非认为对应用程序有必要或明确标识为安全的，例如作为安全审计的结果。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_2)

应用程序通常会使用[Log Class](https://developer.android.com/reference/android/util/Log.html)和[Logger Class](https://developer.android.com/reference/java/util/logging/Logger.html)来创建日志。要发现这一点，您应该审核应用程序的源代码以查找任何此类日志记录类。这些通常可以通过搜索以下关键字找到：

- 函数和类，例如：
- `android.util.Log`
- `Log.d`| `Log.e`| `Log.i`| `Log.v`| `Log.w`|`Log.wtf`
- `Logger`
- 关键字和系统输出：
- `System.out.print`|`System.err.print`
- 日志文件
- 记录
- 日志

在准备生产版本时，您可以使用[ProGuard](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#proguard)（包含在 Android Studio 中）等工具。要确定`android.util.Log`类中的所有日志功能是否已被删除，请检查 ProGuard 配置文件 (proguard-rules.pro) 中的以下选项（根据[删除日志代码的示例](https://www.guardsquare.com/en/products/proguard/manual/examples#logging)和这篇关于[在 Android Studio 项目中启用 ProGuard 的](https://developer.android.com/studio/build/shrink-code#enable)文章） :

```
-assumenosideeffects class android.util.Log
{
  public static boolean isLoggable(java.lang.String, int);
  public static int v(...);
  public static int i(...);
  public static int w(...);
  public static int d(...);
  public static int e(...);
  public static int wtf(...);
}
```

请注意，上面的示例仅确保删除对 Log 类方法的调用。如果要记录的字符串是动态构造的，则构造该字符串的代码可能会保留在字节码中。例如，以下代码发出隐式`StringBuilder`构造日志语句：

Java 中的示例：

```
Log.v("Private key tag", "Private key [byte format]: " + key);
```

Kotlin 中的示例：

```
Log.v("Private key tag", "Private key [byte format]: $key")
```

然而，编译后的字节码等同于以下日志语句的字节码，它显式地构造了字符串：

Java 中的示例：

```
Log.v("Private key tag", new StringBuilder("Private key [byte format]: ").append(key.toString()).toString());
```

Kotlin 中的示例：

```
Log.v("Private key tag", StringBuilder("Private key [byte format]: ").append(key).toString())
```

ProGuard 保证移除`Log.v`方法调用。是否删除其余代码 ( `new StringBuilder ...`) 取决于代码的复杂性和[ProGuard 版本](https://stackoverflow.com/questions/6009078/removing-unused-strings-during-proguard-optimisation)。

这是一个安全风险，因为（未使用的）字符串将纯文本数据泄漏到内存中，可以通过调试器或内存转储访问内存。

不幸的是，这个问题不存在灵丹妙药，但一个选择是实现一个自定义日志记录工具，它采用简单的参数并在内部构造日志语句。

```
SecureLog.v("Private key [byte format]: ", key);
```

然后配置 ProGuard 以剥离其调用。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_1)

至少使用所有移动应用程序功能一次，然后识别应用程序的数据目录并查找日志文件 ( `/data/data/<package-name>`)。查看应用日志，判断是否产生了日志数据；一些移动应用程序创建自己的日志并将其存储在数据目录中。

许多应用程序开发人员仍然使用`System.out.println`or`printStackTrace`代替适当的日志记录类。因此，您的测试策略必须包括应用程序启动、运行和关闭时生成的所有输出。`System.out.println`要确定or直接打印了哪些数据`printStackTrace`，您可以[`Logcat`](https://developer.android.com/tools/debugging/debugging-log.html)按照“基本安全测试”一章“监控系统日志”一节中的说明使用。

请记住，您可以通过过滤 Logcat 输出来定位特定应用程序，如下所示：

```
adb logcat | grep "$(adb shell ps | grep <package-name> | awk '{print $2}')"
```

> 如果您已经知道应用程序的 PID，您可以直接使用`--pid`标志给它。

如果您希望某些字符串或模式出现在日志中，您可能还想应用更多过滤器或正则表达式（例如使用`logcat`的正则表达式标志）。`-e <expr>, --regex=<expr>`

## 确定敏感数据是否与第三方共享 (MSTG-STORAGE-4)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#determining-whether-sensitive-data-is-shared-with-third-parties-mstg-storage-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_3)

敏感信息可能通过多种方式泄露给第三方，包括但不限于以下方式：

### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app)

这些服务提供的功能可能涉及跟踪服务以监控用户在使用应用程序时的行为、销售横幅广告或改善用户体验。

缺点是开发人员通常不知道通过第三方库执行的代码的细节。因此，不应向服务发送超过必要的信息，也不应泄露敏感信息。

大多数第三方服务以两种方式实现：

- 有一个独立的库
- 使用完整的 SDK

### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications)

重要的是要了解[通知](https://developer.android.com/guide/topics/ui/notifiers/notifications)永远不应被视为私人的。当 Android 系统处理通知时，它会在系统范围内广播，并且任何使用[NotificationListenerService](https://developer.android.com/reference/kotlin/android/service/notification/NotificationListenerService)运行的应用程序都可以侦听这些通知以完整接收它们，并可以根据需要进行处理。

有许多已知的恶意软件样本，例如[Joker](https://research.checkpoint.com/2020/new-joker-variant-hits-google-play-with-an-old-trick/)和[Alien](https://www.threatfabric.com/blogs/alien_the_story_of_cerberus_demise.html)，它们滥用`NotificationListenerService`监听设备上的通知，然后将它们发送到攻击者控制的 C2 基础设施。通常这样做是为了侦听双因素身份验证 (2FA) 代码，这些代码在设备上显示为通知，然后发送给攻击者。对用户来说更安全的替代方法是使用不生成通知的 2FA 应用程序。

此外，Google Play 商店中有许多提供通知日志记录的应用程序，这些应用程序基本上在本地记录 Android 系统上的任何通知。这突出表明，通知在 Android 上绝不是私有的，设备上的任何其他应用程序都可以访问。

出于这个原因，应检查所有通知使用情况，以查找可能被恶意应用程序使用的机密或高风险信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_3)

#### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app_1)

要确定第三方库提供的 API 调用和函数是否根据最佳实践使用，请查看其源代码、请求的权限并检查是否存在任何已知漏洞（请参阅[“检查第三方库中的弱点 (MSTG-CODE-5) ）”](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#checking-for-weaknesses-in-third-party-libraries-mstg-code-5)）。

发送到第三方服务的所有数据都应匿名，以防止泄露 PII（个人身份信息），从而允许第三方识别用户帐户。不应将其他数据（例如可以映射到用户帐户或会话的 ID）发送给第三方。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_1)

搜索`NotificationManager`可能指示某种形式的通知管理的类的任何用法。如果正在使用该类，下一步将是了解应用程序如何[生成通知](https://developer.android.com/training/notify-user/build-notification#SimpleNotification)以及最终显示哪些数据。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_2)

#### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app_2)

检查对外部服务的所有请求以获取嵌入的敏感信息。[要拦截客户端和服务器之间的流量，您可以通过使用Burp Suite](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#burp-suite) Professional 或[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)发起中间人 (MITM) 攻击来执行动态分析。通过拦截代理路由流量后，您可以尝试嗅探在应用程序和服务器之间传递的流量。应检查所有未直接发送到托管主要功能的服务器的应用程序请求是否包含敏感信息，例如跟踪器或广告服务中的 PII。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_2)

运行应用程序并开始跟踪对与通知创建相关的函数的所有调用，例如`setContentTitle`或`setContentText`from [`NotificationCompat.Builder`](https://developer.android.com/reference/androidx/core/app/NotificationCompat.Builder)。最后观察跟踪并评估它是否包含其他应用程序可能窃听的任何敏感信息。

## 确定是否为文本输入字段禁用键盘缓存（MSTG-STORAGE-5）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#determining-whether-the-keyboard-cache-is-disabled-for-text-input-fields-mstg-storage-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_4)

当用户在输入字段中键入时，软件会自动建议数据。此功能对于消息传递应用程序非常有用。但是，当用户选择包含此类信息的输入字段时，键盘缓存可能会泄露敏感信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_4)

在活动的布局定义中，您可以定义`TextViews`具有 XML 属性的活动。如果 XML 属性`android:inputType`的值为`textNoSuggestions`，则在选择输入字段时不会显示键盘缓存。用户将不得不手动输入所有内容。

```
   <EditText
        android:id="@+id/KeyBoardCache"
        android:inputType="textNoSuggestions" />
```

所有包含敏感信息的输入字段的代码都应包含此 XML 属性以[禁用键盘建议](https://developer.android.com/reference/android/text/InputType.html#TYPE_TEXT_FLAG_NO_SUGGESTIONS)。

或者，开发人员可以使用以下常量：

| XML`android:inputType`                                       | 代码`InputType`                                              | API级别 |
| :----------------------------------------------------------- | :----------------------------------------------------------- | :------ |
| [`textPassword`](https://developer.android.com/reference/android/widget/TextView#attr_android:inputType:~:text=_SUGGESTIONS.-,textPassword,-81) | [`TYPE_TEXT_VARIATION_PASSWORD`](https://developer.android.com/reference/android/text/InputType#TYPE_TEXT_VARIATION_PASSWORD) | 3个     |
| [`textVisiblePassword`](https://developer.android.com/reference/android/widget/TextView#attr_android:inputType:~:text=_URI.-,textVisiblePassword,-91) | [`TYPE_TEXT_VARIATION_VISIBLE_PASSWORD`](https://developer.android.com/reference/android/text/InputType#TYPE_TEXT_VARIATION_VISIBLE_PASSWORD) | 3个     |
| [`numberPassword`](https://developer.android.com/reference/android/widget/TextView#attr_android:inputType:~:text=_DECIMAL.-,numberPassword,-12) | [`TYPE_NUMBER_VARIATION_PASSWORD`](https://developer.android.com/reference/android/text/InputType#TYPE_NUMBER_VARIATION_PASSWORD) | 11      |
| [`textWebPassword`](https://developer.android.com/reference/android/widget/TextView#attr_android:inputType:~:text=_ADDRESS.-,textWebPassword,-e1) | [`TYPE_TEXT_VARIATION_WEB_PASSWORD`](https://developer.android.com/reference/android/text/InputType#TYPE_TEXT_VARIATION_WEB_PASSWORD) | 11      |

检查应用程序代码以验证没有任何输入类型被覆盖。例如，通过`findViewById(R.id.KeyBoardCache).setInputType(InputType.TYPE_CLASS_TEXT)`将输入字段的输入类型`KeyBoardCache`设置为`text`重新启用键盘缓存。

最后，检查 Android Manifest ( `android:minSdkVersion`) 中所需的最低 SDK 版本，因为它必须支持使用的常量（例如，Android SDK 版本 11 是必需的`textWebPassword`）。否则，编译后的应用程序将不会接受允许键盘缓存的已使用输入类型常量。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_3)

启动应用程序并单击包含敏感数据的输入字段。如果建议使用字符串，则这些字段的键盘缓存尚未禁用。

## 确定敏感存储数据是否已通过 IPC 机制公开 (MSTG-STORAGE-6)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#determining-whether-sensitive-stored-data-has-been-exposed-via-ipc-mechanisms-mstg-storage-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_5)

作为 Android 的 IPC 机制的一部分，内容提供程序允许其他应用访问和修改应用存储的数据。如果配置不当，这些机制可能会泄露敏感数据。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_5)

第一步是查看`AndroidManifest.xml`以检测应用公开的Content Provider(内容提供者)。`<provider>`您可以通过元素识别Content Provider(内容提供者)。完成以下步骤：

- 判断导出标签( `android:exported`) 的值是否为`"true"`。即使不是，`"true"`如果`<intent-filter>`已经为标签定义了标签，标签也会自动设置为。如果内容仅供应用程序本身访问，请设置`android:exported`为`"false"`. 如果不是，请将标志设置为`"true"`并定义适当的读/写权限。
- 确定数据是否受到权限标记 ( `android:permission`) 的保护。权限标签限制对其他应用程序的曝光。
- 确定`android:protectionLevel`属性是否具有值`signature`。此设置表示数据仅供来自同一企业的应用程序访问（即，使用相同的密钥签名）。要使其他应用程序可以访问数据，请对`<permission>`元素应用安全策略并设置适当的`android:protectionLevel`. 如果您使用`android:permission`，其他应用程序必须`<uses-permission>`在其清单中声明相应的元素才能与您的Content Provider(内容提供者)交互。您可以使用该`android:grantUriPermissions`属性向其他应用程序授予更具体的访问权限；您可以限制对`<grant-uri-permission>`元素的访问。

检查源代码以了解内容提供程序的使用方式。搜索以下关键字：

- `android.content.ContentProvider`
- `android.database.Cursor`
- `android.database.sqlite`
- `.query`
- `.update`
- `.delete`

> 为避免应用程序内的 SQL 注入攻击，请使用参数化查询方法，例如`query`、`update`和`delete`。确保正确清理所有方法参数；例如，如果`selection`参数由串联的用户输入组成，则可能会导致 SQL 注入。

如果公开内容提供程序，请确定是否使用参数化[查询方法](https://developer.android.com/reference/android/content/ContentProvider.html#query(android.net.Uri%2C java.lang.String[]%2C java.lang.String%2C java.lang.String[]%2C java.lang.String))（`query`、`update`和`delete`）来防止 SQL 注入。如果是这样，请确保他们的所有论点都经过适当的过滤。

我们将使用易受攻击的密码管理器应用程序[Sieve](https://github.com/mwrlabs/drozer/releases/download/2.3.4/sieve.apk)作为易受攻击的内容提供程序的示例。

#### 检查 Android 清单[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#inspect-the-android-manifest)

识别所有定义的`<provider>`元素：

```
<provider
      android:authorities="com.mwr.example.sieve.DBContentProvider"
      android:exported="true"
      android:multiprocess="true"
      android:name=".DBContentProvider">
    <path-permission
          android:path="/Keys"
          android:readPermission="com.mwr.example.sieve.READ_KEYS"
          android:writePermission="com.mwr.example.sieve.WRITE_KEYS"
     />
</provider>
<provider
      android:authorities="com.mwr.example.sieve.FileBackupProvider"
      android:exported="true"
      android:multiprocess="true"
      android:name=".FileBackupProvider"
/>
```

如上所示`AndroidManifest.xml`，应用程序导出了两个内容提供程序。请注意，一个路径（“/Keys”）受读写权限保护。

#### 检查源代码[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#inspect-the-source-code)

检查文件中的`query`函数`DBContentProvider.java`以确定是否泄露了任何敏感信息：

Java 中的示例：

```
public Cursor query(final Uri uri, final String[] array, final String s, final String[] array2, final String s2) {
    final int match = this.sUriMatcher.match(uri);
    final SQLiteQueryBuilder sqLiteQueryBuilder = new SQLiteQueryBuilder();
    if (match >= 100 && match < 200) {
        sqLiteQueryBuilder.setTables("Passwords");
    }
    else if (match >= 200) {
        sqLiteQueryBuilder.setTables("Key");
    }
    return sqLiteQueryBuilder.query(this.pwdb.getReadableDatabase(), array, s, array2, (String)null, (String)null, s2);
}
```

Kotlin 中的示例：

```
fun query(uri: Uri?, array: Array<String?>?, s: String?, array2: Array<String?>?, s2: String?): Cursor {
        val match: Int = this.sUriMatcher.match(uri)
        val sqLiteQueryBuilder = SQLiteQueryBuilder()
        if (match >= 100 && match < 200) {
            sqLiteQueryBuilder.tables = "Passwords"
        } else if (match >= 200) {
            sqLiteQueryBuilder.tables = "Key"
        }
        return sqLiteQueryBuilder.query(this.pwdb.getReadableDatabase(), array, s, array2, null as String?, null as String?, s2)
    }
```

这里我们看到实际上有两条路径，“/Keys”和“/Passwords”，后者在清单中没有受到保护，因此很容易受到攻击。

访问 URI 时，查询语句返回所有密码和路径`Passwords/`。我们将在“动态分析”部分解决这个问题并显示所需的确切 URI。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_4)

#### 测试Content Provider(内容提供者)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-content-providers)

要动态分析应用程序的Content Provider(内容提供者)，首先枚举攻击面：将应用程序的包名称传递给 Drozer 模块`app.provider.info`：

```
dz> run app.provider.info -a com.mwr.example.sieve
  Package: com.mwr.example.sieve
  Authority: com.mwr.example.sieve.DBContentProvider
  Read Permission: null
  Write Permission: null
  Content Provider: com.mwr.example.sieve.DBContentProvider
  Multiprocess Allowed: True
  Grant Uri Permissions: False
  Path Permissions:
  Path: /Keys
  Type: PATTERN_LITERAL
  Read Permission: com.mwr.example.sieve.READ_KEYS
  Write Permission: com.mwr.example.sieve.WRITE_KEYS
  Authority: com.mwr.example.sieve.FileBackupProvider
  Read Permission: null
  Write Permission: null
  Content Provider: com.mwr.example.sieve.FileBackupProvider
  Multiprocess Allowed: True
  Grant Uri Permissions: False
```

在此示例中，导出了两个内容提供程序。两者都可以未经许可访问，`/Keys`除了`DBContentProvider`. 使用此信息，您可以重建部分内容 URI 以访问`DBContentProvider`（URI 以 开头`content://`）。

要在应用程序中识别Content Provider(内容提供者) URI，请使用 Drozer 的`scanner.provider.finduris`模块。该模块以多种方式猜测路径并确定可访问的内容 URI：

```
dz> run scanner.provider.finduris -a com.mwr.example.sieve
Scanning com.mwr.example.sieve...
Unable to Query content://com.mwr.example.sieve.DBContentProvider/
...
Unable to Query content://com.mwr.example.sieve.DBContentProvider/Keys
Accessible content URIs:
content://com.mwr.example.sieve.DBContentProvider/Keys/
content://com.mwr.example.sieve.DBContentProvider/Passwords
content://com.mwr.example.sieve.DBContentProvider/Passwords/
```

获得可访问Content Provider(内容提供者)列表后，尝试使用以下`app.provider.query`模块从每个提供者中提取数据：

```
dz> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --vertical
_id: 1
service: Email
username: incognitoguy50
password: PSFjqXIMVa5NJFudgDuuLVgJYFD+8w== (Base64 - encoded)
email: incognitoguy50@gmail.com
```

您还可以使用 Drozer 插入、更新和删除易受攻击的Content Provider(内容提供者)的记录：

- 插入记录

```
dz> run app.provider.insert content://com.vulnerable.im/messages
                --string date 1331763850325
                --string type 0
                --integer _id 7
```

- 更新记录

```
dz> run app.provider.update content://settings/secure
                --selection "name=?"
                --selection-args assisted_gps_enabled
                --integer value 0
```

- 删除记录

```
dz> run app.provider.delete content://settings/secure
                --selection "name=?"
                --selection-args my_setting
```

#### Content Provider(内容提供者)中的 SQL 注入[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#sql-injection-in-content-providers)

Android 平台提倡使用 SQLite 数据库来存储用户数据。因为这些数据库是基于 SQL 的，所以它们可能容易受到 SQL 注入的攻击。您可以使用 Drozer 模块`app.provider.query`通过操作传递给内容提供程序的投影和选择字段来测试 SQL 注入：

```
dz> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection "'"
unrecognized token: "' FROM Passwords" (code 1): , while compiling: SELECT ' FROM Passwords

dz> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --selection "'"
unrecognized token: "')" (code 1): , while compiling: SELECT * FROM Passwords WHERE (')
```

如果应用程序容易受到 SQL 注入攻击，它将返回详细的错误消息。Android 上的 SQL 注入可用于修改或查询来自易受攻击的内容提供程序的数据。在下面的示例中，Drozer 模块`app.provider.query`用于列出所有数据库表：

```
dz> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection "*
FROM SQLITE_MASTER WHERE type='table';--"
| type  | name             | tbl_name         | rootpage | sql              |
| table | android_metadata | android_metadata | 3        | CREATE TABLE ... |
| table | Passwords        | Passwords        | 4        | CREATE TABLE ... |
| table | Key              | Key              | 5        | CREATE TABLE ... |
```

SQL 注入也可用于从其他受保护的表中检索数据：

```
dz> run app.provider.query content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection "* FROM Key;--"
| Password | pin |
| thisismypassword | 9876 |
```

您可以使用该模块自动执行这些步骤，该`scanner.provider.injection`模块会自动在应用程序中查找易受攻击的Content Provider(内容提供者)：

```
dz> run scanner.provider.injection -a com.mwr.example.sieve
Scanning com.mwr.example.sieve...
Injection in Projection:
  content://com.mwr.example.sieve.DBContentProvider/Keys/
  content://com.mwr.example.sieve.DBContentProvider/Passwords
  content://com.mwr.example.sieve.DBContentProvider/Passwords/
Injection in Selection:
  content://com.mwr.example.sieve.DBContentProvider/Keys/
  content://com.mwr.example.sieve.DBContentProvider/Passwords
  content://com.mwr.example.sieve.DBContentProvider/Passwords/
```

#### 基于文件系统的Content Provider(内容提供者)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#file-system-based-content-providers)

Content Provider(内容提供者)可以提供对底层文件系统的访问。这允许应用程序共享文件（Android 沙箱通常会阻止这种情况）。您可以使用 Drozer 模块`app.provider.read`和`app.provider.download`分别从导出的基于文件的内容提供程序读取和下载文件。这些Content Provider(内容提供者)容易受到目录遍历的影响，这允许读取目标应用程序沙箱中其他受保护的文件。

```
dz> run app.provider.download content://com.vulnerable.app.FileProvider/../../../../../../../../data/data/com.vulnerable.app/database.db /home/user/database.db
Written 24488 bytes
```

使用该`scanner.provider.traversal`模块自动执行查找易受目录遍历影响的内容提供程序的过程：

```
dz> run scanner.provider.traversal -a com.mwr.example.sieve
Scanning com.mwr.example.sieve...
Vulnerable Providers:
  content://com.mwr.example.sieve.FileBackupProvider/
  content://com.mwr.example.sieve.FileBackupProvider
```

请注意，`adb`也可用于查询Content Provider(内容提供者)：

```
$ adb shell content query --uri content://com.owaspomtg.vulnapp.provider.CredentialProvider/credentials
Row: 0 id=1, username=admin, password=StrongPwd
Row: 1 id=2, username=test, password=test
...
```

## 通过用户界面检查敏感数据泄露 (MSTG-STORAGE-7)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#checking-for-sensitive-data-disclosure-through-the-user-interface-mstg-storage-7)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_6)

例如，在注册帐户或付款时输入敏感信息是使用许多应用程序的重要部分。此数据可能是财务信息，例如信用卡数据或用户帐户密码。如果应用程序在键入时未正确屏蔽数据，则数据可能会暴露。

为了防止泄露和减轻诸如[肩窥](https://en.wikipedia.org/wiki/Shoulder_surfing_(computer_security))之类的风险，您应该验证没有通过用户界面暴露任何敏感数据，除非明确要求（例如输入密码）。对于需要显示的数据，应该对其进行适当的屏蔽，通常是显示星号或点而不是明文。

仔细检查所有显示此类信息或将其作为输入的 UI 组件。搜索敏感信息的任何痕迹，并评估是否应将其屏蔽或完全删除。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_6)

#### 文本字段[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#text-fields)

为确保应用程序屏蔽了敏感的用户输入，请检查 的定义中的以下属性`EditText`：

```
android:inputType="textPassword"
```

使用此设置，点（而不是输入字符）将显示在文本字段中，防止应用程序将密码或 PIN 泄漏到用户界面。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_3)

在静态评估应用程序时，建议搜索`NotificationManager`类的任何使用情况，这可能表明某种形式的通知管理。如果正在使用该类，下一步就是了解应用程序如何[生成通知](https://developer.android.com/training/notify-user/build-notification#SimpleNotification)。

这些代码位置可以输入到下面的动态分析部分，提供应用程序通知可以动态生成的位置的想法。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_5)

要确定应用程序是否向用户界面泄露了任何敏感信息，请运行应用程序并识别可能泄露信息的组件。

#### 文本字段[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#text-fields_1)

如果信息被屏蔽，例如，用星号或点替换输入，应用程序不会将数据泄漏到用户界面。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_4)

识别通知的使用贯穿整个应用程序及其所有可用功能，寻找触发任何通知的方法。考虑到您可能需要在应用程序外部执行操作才能触发某些通知。

在运行应用程序时，您可能希望开始跟踪对与通知创建相关的函数的所有调用，例如`setContentTitle`或`setContentText`from [`NotificationCompat.Builder`](https://developer.android.com/reference/androidx/core/app/NotificationCompat.Builder)。最后观察痕迹并评估它是否包含任何敏感信息。

## 测试敏感数据的备份 (MSTG-STORAGE-8)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-backups-for-sensitive-data-mstg-storage-8)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_7)

此测试用例侧重于确保备份不存储敏感的应用程序特定数据。应执行以下检查：

- 检查`AndroidManifest.xml`相关的备份标志。
- 尝试备份应用程序并检查敏感数据的备份。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_7)

#### 当地的[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#local)

Android 提供了一个名为[`allowBackup`](https://developer.android.com/guide/topics/manifest/application-element.html#allowbackup)备份所有应用程序数据的属性。该属性在`AndroidManifest.xml`文件中设置。如果此属性的值为**true**，则设备允许用户通过命令使用 Android Debug Bridge (ADB) 备份应用程序`$ adb backup`。

要防止应用程序数据备份，请将`android:allowBackup`属性设置为**false**。当此属性不可用时，默认情况下启用 allowBackup 设置，并且必须手动停用备份。

> 注意：如果设备已加密，则备份文件也将被加密。

检查`AndroidManifest.xml`文件中是否有以下标志：

```
android:allowBackup="true"
```

如果标志值为**true**，则确定应用程序是否保存任何类型的敏感数据（检查测试用例“测试本地存储中的敏感数据”）。

#### 云[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cloud)

无论您使用键/值备份还是自动备份，您都必须确定以下内容：

- 哪些文件被发送到云端（例如，SharedPreferences）
- 文件是否包含敏感信息
- 敏感信息在发送到云端之前是否加密。

> 如果您不想与 Google Cloud 共享文件，可以将它们从[Auto Backup](https://developer.android.com/guide/topics/data/autobackup.html#IncludingFiles)中排除。静态存储在设备上的敏感信息在发送到云端之前应该进行加密。

- **自动备份**`android:allowBackup`：您可以通过应用程序清单文件中的布尔属性配置自动备份。针对 Android 6.0（API 级别 23）的应用程序默认启用[自动备份。](https://developer.android.com/guide/topics/data/autobackup.html#EnablingAutoBackup)实现备份代理时可以使用该属性`android:fullBackupOnly`激活自动备份，但该属性仅适用于Android 6.0及以上版本。其他 Android 版本改为使用键/值备份。

```
android:fullBackupOnly
```

自动备份包括几乎所有应用程序文件，并在用户的 Google 云端硬盘帐户中为每个应用程序存储多达 25 MB 的文件。仅存储最近的备份；之前的备份被删除。

- **键/值备份**：要启用键/值备份，您必须在清单文件中定义备份代理。查找`AndroidManifest.xml`以下属性：

```
android:backupAgent
```

要实现键/值备份，请扩展以下类之一：

- [备份代理](https://developer.android.com/reference/android/app/backup/BackupAgent.html)
- [备份代理助手](https://developer.android.com/reference/android/app/backup/BackupAgentHelper.html)

要检查键/值备份实现，请在源代码中查找这些类。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_6)

执行所有可用的应用程序功能后，尝试通过备份`adb`。如果备份成功，请检查备份存档中的敏感数据。打开终端并运行以下命令：

```
adb backup -apk -nosystem <package-name>
```

ADB现在应该回复“现在解锁您的设备并确认备份操作”，并且应该在 Android 手机上要求您输入密码。这是一个可选步骤，您无需提供。如果电话未提示此消息，请尝试以下命令（包括引号）：

```
adb backup "-apk -nosystem <package-name>"
```

当您的设备的 adb 版本早于 1.0.31 时，就会出现此问题。如果是这种情况，您还必须在主机上使用 1.0.31 的 adb 版本。1.0.32 之后的 adb 版本[打破了向后兼容性。](https://issuetracker.google.com/issues/37096097)

*通过选择“备份我的数据”*选项批准从您的设备进行备份。备份过程完成后，文件*.ab*将位于您的工作目录中。运行以下命令将 .ab 文件转换为 tar。

```
dd if=mybackup.ab bs=24 skip=1|openssl zlib -d > mybackup.tar
```

如果出现错误`openssl:Error: 'zlib' is an invalid command.`，您可以尝试改用 Python。

```
dd if=backup.ab bs=1 skip=24 | python -c "import zlib,sys;sys.stdout.write(zlib.decompress(sys.stdin.read()))" > backup.tar
```

[*Android Backup Extractor*](https://github.com/nelenkov/android-backup-extractor)是另一种备用备份工具。要使该工具正常工作，您必须下载适用于[JRE7](https://www.oracle.com/technetwork/java/javase/downloads/jce-7-download-432124.html)或[JRE8](http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)的 Oracle JCE Unlimited Strength Jurisdiction Policy Files并将它们放在 JRE lib/security 文件夹中。运行以下命令以转换 tar 文件：

```
java -jar abe.jar unpack backup.ab
```

如果显示一些Cipher信息和用法，说明还没有解包成功。在这种情况下，您可以尝试使用更多参数：

```
abe [-debug] [-useenv=yourenv] unpack <backup.ab> <backup.tar> [password]
```

[password]: 是你的Android设备之前询问你时的密码。例如这里是：123

```
java -jar abe.jar unpack backup.ab backup.tar 123
```

将 tar 文件提取到您的工作目录。

```
tar xvf mybackup.tar
```

## 在自动生成的屏幕截图中查找敏感信息 (MSTG-STORAGE-9)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#finding-sensitive-information-in-auto-generated-screenshots-mstg-storage-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_8)

制造商希望在应用程序启动和退出时为设备用户提供美观的体验，因此他们引入了屏幕截图保存功能，以便在应用程序后台Runtime(运行时)使用。此功能可能会带来安全风险。如果用户在显示敏感数据时故意截屏应用程序，则可能会暴露敏感数据。在设备上运行并能够连续捕获屏幕的恶意应用程序也可能会泄露数据。屏幕截图被写入本地存储，它们可能会被流氓应用程序（如果设备已获得 root 权限）或窃取设备的人从中恢复。

例如，捕获银行应用程序的屏幕截图可能会泄露有关用户帐户、信用、交易等的信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_8)

当前活动的屏幕截图是在 Android 应用程序进入后台时截取的，并在应用程序返回前台时出于美观目的显示。但是，这可能会泄露敏感信息。

要确定应用程序是否可能通过应用程序切换器公开敏感信息，请查看是否[`FLAG_SECURE`](https://developer.android.com/reference/android/view/Display.html#FLAG_SECURE)已设置该选项。您应该找到类似于以下代码片段的内容：

Java 中的示例：

```
getWindow().setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE);

setContentView(R.layout.activity_main);
```

Kotlin 中的示例：

```
window.setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE)

setContentView(R.layout.activity_main)
```

如果未设置该选项，则应用程序容易受到屏幕捕获的影响。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_7)

在对应用程序进行黑盒测试时，导航到包含敏感信息的任何屏幕并单击主页按钮将应用程序发送到后台，然后按应用程序切换器按钮以查看快照。如下图，如果`FLAG_SECURE`设置了（左图），快照将为空；如果未设置标志（右图），将显示活动信息：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/2.png) ![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/1.png)

在支持[基于文件的加密 (FBE) 的](https://source.android.com/security/encryption/file-based)设备上，快照存储在该`/data/system_ce/<USER_ID>/<IMAGE_FOLDER_NAME>`文件夹中。`<IMAGE_FOLDER_NAME>`取决于供应商，但最常见的名称是`snapshots`和`recent_images`。如果设备不支持 FBE，`/data/system/<IMAGE_FOLDER_NAME>`则使用该文件夹。

> 访问这些文件夹和快照需要 root。

## 测试内存中的敏感数据 (MSTG-STORAGE-10)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-memory-for-sensitive-data-mstg-storage-10)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_9)

分析内存可以帮助开发人员确定几个问题的根本原因，例如应用程序崩溃。但是，它也可用于访问敏感数据。本节介绍如何通过进程内存检查数据泄露。

首先识别存储在内存中的敏感信息。敏感资产可能已在某个时候加载到内存中。目的是验证此信息是否已尽可能简短地公开。

要调查应用程序的内存，您必须首先创建内存转储。您还可以实时分析内存，例如，通过调试器。无论采用何种方法，内存转储在验证方面都是一个非常容易出错的过程，因为每个转储都包含已执行函数的输出。您可能会错过执行关键场景。此外，除非您知道数据的足迹（确切值或数据格式），否则在分析过程中很可能会忽略数据。例如，如果应用程序使用随机生成的对称密钥进行加密，您可能无法在内存中发现它，除非您可以在另一个上下文中识别密钥的值。

因此，您最好从静态分析开始。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_9)

有关可能的数据泄露来源的概述，请在检查源代码之前查看文档并确定应用程序组件。例如，来自后端的敏感数据可能在 HTTP 客户端、XML 解析器等中。您希望尽快从内存中删除所有这些副本。

此外，了解应用程序的体系结构和体系结构在系统中的作用将帮助您识别根本不必暴露在内存中的敏感信息。例如，假设您的应用程序从一台服务器接收数据并在不进行任何处理的情况下将其传输到另一台服务器。该数据可以以加密格式处理，从而防止暴露在内存中。

但是，如果您需要公开内存中的敏感数据，则应确保您的应用程序设计为尽可能短地公开尽可能少的数据副本。换句话说，您希望集中处理敏感数据（即使用尽可能少的组件）并基于原始的、可变的数据结构。

后一个要求为开发人员提供了直接的内存访问权限。确保他们使用此访问权限用虚拟数据（通常为零）覆盖敏感数据。首选数据类型的示例包括`byte []`and `char []`，但不包括`String`or `BigInteger`。每当您尝试修改不可变对象（如`String`）时，您都会创建并更改该对象的副本。

`StringBuffer`使用像和这样的非原始可变类型`StringBuilder`可能是可以接受的，但它是指示性的，需要小心。类型 like`StringBuffer`用于修改内容（这是你想要做的）。但是，要访问此类类型的值，您将使用该`toString`方法，该方法将创建数据的不可变副本。有几种方法可以在不创建不可变副本的情况下使用这些数据类型，但它们比简单地使用原始数组需要更多的努力。安全内存管理是使用类似类型的好处之一`StringBuffer`，但这可能是一把两刃剑。如果您尝试修改其中一种类型的内容并且副本超出缓冲区容量，缓冲区大小将自动增加。缓冲区内容可能会被复制到不同的位置，使旧内容没有可用于覆盖它的引用。

不幸的是，很少有库和框架旨在允许覆盖敏感数据。例如，销毁一个密钥，如下所示，并没有真正从内存中删除该密钥：

Java 中的示例：

```
SecretKey secretKey = new SecretKeySpec("key".getBytes(), "AES");
secretKey.destroy();
```

Kotlin 中的示例：

```
val secretKey: SecretKey = SecretKeySpec("key".toByteArray(), "AES")
secretKey.destroy()
```

覆盖来自的支持字节数组`secretKey.getEncoded`也不会删除密钥；基于 SecretKeySpec 的密钥返回支持字节数组的副本。请参阅以下部分了解`SecretKey`从内存中删除 a 的正确方法。

RSA 密钥对基于`BigInteger`类型，因此在首次在`AndroidKeyStore`. 一些密码（例如 中的 AES `Cipher`）`BouncyCastle`没有正确清理它们的字节数组。

用户提供的数据（凭证、社会安全号码、信用卡信息等）是另一种可能暴露在内存中的数据。无论您是否将其标记为密码字段，都会通过界面`EditText`将内容传送到应用程序。`Editable`如果您的应用不提供`Editable.Factory`，用户提供的数据可能会在内存中暴露的时间超过必要的时间。默认`Editable`实现 ,导致与 Java和cause`SpannableStringBuilder`相同的问题（上面讨论过）。`StringBuilder``StringBuffer`

总之，在执行静态分析以识别暴露在内存中的敏感数据时，您应该：

- 尝试识别应用程序组件并映射数据的使用位置。
- 确保敏感数据由尽可能少的组件处理。
- 一旦不再需要包含敏感数据的对象，请确保正确删除对象引用。
- 确保在删除引用后请求垃圾回收。
- 确保敏感数据在不再需要时立即被覆盖。
- 不要用不可变数据类型（例如`String`和`BigInteger`）表示此类数据。
- 避免使用非原始数据类型（例如`StringBuilder`）。
- 在方法外部删除引用之前覆盖引用`finalize`。
- 注意第三方组件（库和框架）。公共 API 是很好的指标。确定公共 API 是否按照本章所述处理敏感数据。

**以下部分描述了内存中数据泄漏的陷阱以及避免它们的最佳实践。**

不要使用不可变结构（例如，`String`和`BigInteger`）来表示秘密。使这些结构无效：垃圾收集器可能会收集它们，但它们可能会在垃圾收集后保留在堆上。然而，您应该在每个关键操作（例如，加密、解析包含敏感信息的服务器响应）之后请求垃圾收集。当信息的副本没有被正确清理（如下所述）时，您的请求将有助于减少这些副本在内存中可用的时间长度。

要从内存中正确清除敏感信息，请将其存储在原始数据类型中，例如字节数组 ( `byte[]`) 和字符数组 ( `char[]`)。如上面“静态分析”部分所述，您应该避免将信息存储在可变的非原始数据类型中。

一旦不再需要对象，请确保覆盖关键对象的内容。用零覆盖内容是一种简单且非常流行的方法：

Java 中的示例：

```
byte[] secret = null;
try{
    //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        Arrays.fill(secret, (byte) 0);
    }
}
```

Kotlin 中的示例：

```
val secret: ByteArray? = null
try {
     //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        Arrays.fill(secret, 0.toByte())
    }
}
```

但是，这并不能保证内容会在Runtime(运行时)被覆盖。为了优化字节码，编译器会分析并决定不覆盖数据，因为它以后不会被使用（即，这是一个不必要的操作）。即使代码在已编译的 DEX 中，优化也可能发生在 VM 中的即时或提前编译期间。

这个问题没有灵丹妙药，因为不同的解决方案会产生不同的后果。例如，您可能会执行额外的计算（例如，将数据异或到虚拟缓冲区），但您无法知道编译器优化分析的范围。另一方面，在编译器范围之外使用被覆盖的数据（例如，在临时文件中序列化它）保证它会被覆盖，但显然会影响性能和维护。

然后，使用`Arrays.fill`覆盖数据是一个坏主意，因为该方法是一个明显的Hook目标（有关更多详细信息，请参阅“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章）。

上述示例的最后一个问题是内容仅被零覆盖。您应该尝试用随机数据或非关键对象的内容覆盖关键对象。这将使构建能够根据其管理识别敏感数据的扫描仪变得非常困难。

下面是前面例子的改进版本：

Java 中的示例：

```
byte[] nonSecret = somePublicString.getBytes("ISO-8859-1");
byte[] secret = null;
try{
    //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        for (int i = 0; i < secret.length; i++) {
            secret[i] = nonSecret[i % nonSecret.length];
        }

        FileOutputStream out = new FileOutputStream("/dev/null");
        out.write(secret);
        out.flush();
        out.close();
    }
}
```

Kotlin 中的示例：

```
val nonSecret: ByteArray = somePublicString.getBytes("ISO-8859-1")
val secret: ByteArray? = null
try {
     //get or generate the secret, do work with it, make sure you make no local copies
} finally {
    if (null != secret) {
        for (i in secret.indices) {
            secret[i] = nonSecret[i % nonSecret.size]
        }

        val out = FileOutputStream("/dev/null")
        out.write(secret)
        out.flush()
        out.close()
        }
}
```

有关详细信息，请查看[在 RAM 中安全存储敏感数据](https://www.nowsecure.com/resources/secure-mobile-development/coding-practices/securely-store-sensitive-data-in-ram/)。

在“静态分析”部分中，我们提到了在使用`AndroidKeyStore`or时处理加密密钥的正确方法`SecretKey`。

为了更好地实现`SecretKey`，请查看`SecureSecretKey`下面的类。尽管该实现可能缺少一些使类与 兼容的样板代码`SecretKey`，但它解决了主要的安全问题：

- 不对敏感数据进行跨上下文处理。密钥的每个副本都可以从创建它的范围内清除。
- 根据上面给出的建议清除本地副本。

Java 中的示例：

```
  public class SecureSecretKey implements javax.crypto.SecretKey, Destroyable {
      private byte[] key;
      private final String algorithm;

      /** Constructs SecureSecretKey instance out of a copy of the provided key bytes.
        * The caller is responsible of clearing the key array provided as input.
        * The internal copy of the key can be cleared by calling the destroy() method.
        */
      public SecureSecretKey(final byte[] key, final String algorithm) {
          this.key = key.clone();
          this.algorithm = algorithm;
      }

      public String getAlgorithm() {
          return this.algorithm;
      }

      public String getFormat() {
          return "RAW";
      }

      /** Returns a copy of the key.
        * Make sure to clear the returned byte array when no longer needed.
        */
      public byte[] getEncoded() {
          if(null == key){
              throw new NullPointerException();
          }

          return key.clone();
      }

      /** Overwrites the key with dummy data to ensure this copy is no longer present in memory.*/
      public void destroy() {
          if (isDestroyed()) {
              return;
          }

          byte[] nonSecret = new String("RuntimeException").getBytes("ISO-8859-1");
          for (int i = 0; i < key.length; i++) {
            key[i] = nonSecret[i % nonSecret.length];
          }

          FileOutputStream out = new FileOutputStream("/dev/null");
          out.write(key);
          out.flush();
          out.close();

          this.key = null;
          System.gc();
      }

      public boolean isDestroyed() {
          return key == null;
      }
  }
```

Kotlin 中的示例：

```
class SecureSecretKey(key: ByteArray, algorithm: String) : SecretKey, Destroyable {
    private var key: ByteArray?
    private val algorithm: String
    override fun getAlgorithm(): String {
        return algorithm
    }

    override fun getFormat(): String {
        return "RAW"
    }

    /** Returns a copy of the key.
     * Make sure to clear the returned byte array when no longer needed.
     */
    override fun getEncoded(): ByteArray {
        if (null == key) {
            throw NullPointerException()
        }
        return key!!.clone()
    }

    /** Overwrites the key with dummy data to ensure this copy is no longer present in memory. */
    override fun destroy() {
        if (isDestroyed) {
            return
        }
        val nonSecret: ByteArray = String("RuntimeException").toByteArray(charset("ISO-8859-1"))
        for (i in key!!.indices) {
            key!![i] = nonSecret[i % nonSecret.size]
        }
        val out = FileOutputStream("/dev/null")
        out.write(key)
        out.flush()
        out.close()
        key = null
        System.gc()
    }

    override fun isDestroyed(): Boolean {
        return key == null
    }

    /** Constructs SecureSecretKey instance out of a copy of the provided key bytes.
     * The caller is responsible of clearing the key array provided as input.
     * The internal copy of the key can be cleared by calling the destroy() method.
     */
    init {
        this.key = key.clone()
        this.algorithm = algorithm
    }
}
```

安全的用户提供的数据是通常在内存中找到的最终安全信息类型。这通常通过实施自定义输入法来管理，您应该遵循此处给出的建议。但是，Android 允许`EditText`通过自定义`Editable.Factory`.

```
EditText editText = ...; //  point your variable to your EditText instance
EditText.setEditableFactory(new Editable.Factory() {
  public Editable newEditable(CharSequence source) {
  ... // return a new instance of a secure implementation of Editable.
  }
});
```

有关示例实现，请参阅`SecureSecretKey`上面的示例`Editable`。`editText.getText`请注意，如果您提供工厂，您将能够安全地处理由您制作的所有副本。您也可以尝试`EditText`通过调用覆盖内部缓冲区`editText.setText`，但不能保证缓冲区不会被复制。如果您选择依赖默认输入法 和`EditText`，您将无法控制所使用的键盘或其他组件。因此，您应该仅将此方法用于半机密信息。

在所有情况下，请确保在用户退出应用程序时清除内存中的敏感数据。最后，确保在`onPause`触发 Activity 或 Fragment 的事件时清除高度敏感的信息。

> 请注意，这可能意味着每次应用程序恢复时用户都必须重新进行身份验证。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_8)

静态分析会帮助你识别潜在的问题，但它无法提供数据在内存中暴露了多长时间的统计数据，也无法帮助你识别闭源依赖中的问题。这就是动态分析发挥作用的地方。

有多种方法可以分析进程的内存，例如通过调试器/动态检测进行实时分析以及分析一个或多个内存转储。

#### 检索和分析内存转储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#retrieving-and-analyzing-a-memory-dump)

无论您使用的是 root 设备还是非 root 设备，您都可以使用[objection](https://github.com/sensepost/objection)和[Fridump](https://github.com/Nightbringer21/fridump)转储应用程序的进程内存。您可以在“Android 上的篡改和逆向工程”一章的“[内存转储](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-dump)”部分找到有关此过程的详细说明。

内存转储后（例如转储到名为“内存”的文件），根据您要查找的数据的性质，您将需要一组不同的工具来处理和分析该内存转储。例如，如果您专注于字符串，那么执行命令`strings`或`rabin2 -zz`提取这些字符串可能就足够了。

```
# using strings
$ strings memory > strings.txt

# using rabin2
$ rabin2 -ZZ memory > strings.txt
```

在您最喜欢的编辑器中打开`strings.txt`并深入挖掘以识别敏感信息。

但是，如果您想检查其他类型的数据，您更愿意使用 radare2 及其搜索功能。`/?`有关详细信息和选项列表，请参阅 radare2 关于搜索命令 ( ) 的帮助。以下仅显示其中的一个子集：

```
$ r2 <name_of_your_dump_file>

[0x00000000]> /?
Usage: /[!bf] [arg]  Search stuff (see 'e??search' for options)
|Use io.va for searching in non virtual addressing spaces
| / foo\x00                    search for string 'foo\0'
| /c[ar]                       search for crypto materials
| /e /E.F/i                    match regular expression
| /i foo                       search for string 'foo' ignoring case
| /m[?][ebm] magicfile         search for magic, filesystems or binary headers
| /v[1248] value               look for an `cfg.bigendian` 32bit value
| /w foo                       search for wide string 'f\0o\0o\0'
| /x ff0033                    search for hex string
| /z min max                   search for strings of given size
...
```

#### Runtime(运行时)内存分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#runtime-memory-analysis)

除了将内存转储到主机上，您还可以使用[r2frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#r2frida)。有了它，您可以在应用程序Runtime(运行时)分析和检查应用程序的内存。例如，您可以从 r2frida 运行之前的搜索命令并在内存中搜索字符串、十六进制值等。执行此操作时，请记住`\`在启动会话后在搜索命令（以及任何其他 r2frida 特定命令）前面加上反斜杠与`r2 frida://usb//<name_of_your_app>`。

有关更多信息、选项和方法，请参阅“ Android 上的篡改和逆向工程”一章中的“[内存中搜索](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#in-memory-search)”部分。

#### 显式转储和分析 Java 堆[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#explicitly-dumping-and-analyzing-the-java-heap)

对于基本分析，您可以使用 Android Studio 的内置工具。它们位于*Android 监视器*选项卡上。要转储内存，请选择要分析的设备和应用程序，然后单击*转储 Java 堆*。*这将在捕获*目录中创建一个*.hprof*文件，该目录位于应用程序的项目路径中。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/Dump_Java_Heap.png)

要浏览保存在内存转储中的类实例，请在显示*.hprof*文件的选项卡中选择包树视图。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/Package_Tree_View.png)

要对内存转储进行更高级的分析，请使用[Eclipse 内存分析器工具 (MAT)](https://eclipse.org/mat/downloads.php)。它可以作为 Eclipse 插件和独立应用程序使用。

要在 MAT 中分析转储，请使用Android SDK 附带的*hprof-conv平台工具。*

```
./hprof-conv memory.hprof memory-mat.hprof
```

MAT 提供了几种用于分析内存转储的工具。例如，*直方图*提供了从给定类型中捕获的对象数量的估计值，而*线程概览*显示了进程的线程和堆栈帧。*Dominator Tree*提供有关对象之间保持活动依赖关系的信息。您可以使用正则表达式来过滤这些工具提供的结果。

*Object Query Language* studio 是一种 MAT 功能，允许您使用类似 SQL 的语言从内存转储中查询对象。该工具允许您通过调用 Java 方法来转换简单的对象，它还提供了一个 API 用于在 MAT 之上构建复杂的工具。

```
SELECT * FROM java.lang.String
```

`String`在上面的示例中，将选择内存转储中存在的所有对象。结果将包括对象的类、内存地址、值和保留计数。要过滤此信息并仅查看每个字符串的值，请使用以下代码：

```
SELECT toString(object) FROM java.lang.String object
```

或者

```
SELECT object.toString() FROM java.lang.String object
```

SQL 也支持原始数据类型，所以你可以像下面这样来访问所有`char`数组的内容：

```
SELECT toString(arr) FROM char[] arr
```

如果您得到的结果与之前的结果相似，请不要感到惊讶；毕竟，`String`其他 Java 数据类型只是原始数据类型的包装器。现在让我们过滤结果。以下示例代码将选择包含 RSA 密钥的 ASN.1 OID 的所有字节数组。这并不意味着给定的字节数组实际上包含 RSA（相同的字节序列可能是其他内容的一部分），但这是可能的。

```
SELECT * FROM byte[] b WHERE toString(b).matches(".*1\.2\.840\.113549\.1\.1\.1.*")
```

最后，您不必选择整个对象。考虑一个 SQL 类比：类是表，对象是行，字段是列。如果要查找所有具有“密码”字段的对象，可以执行以下操作：

```
SELECT password FROM ".*" WHERE (null != password)
```

在分析过程中，搜索：

- 指示性字段名称：“password”、“pass”、“pin”、“secret”、“private”等。
- 字符串、字符数组、字节数组等中的指示性模式（例如，RSA 足迹）。
- 已知秘密（例如，您输入的信用卡号或后端提供的身份验证令牌）
- 等等

重复测试和内存转储将帮助您获得有关数据暴露长度的统计信息。此外，观察特定内存段（例如，字节数组）的变化方式可能会引导您找到一些无法识别的敏感数据（更多信息请参见下面的“补救”部分）。

## 测试设备访问安全策略 (MSTG-STORAGE-11)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-the-device-access-security-policy-mstg-storage-11)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_10)

处理或查询敏感信息的应用程序应在受信任且安全的环境中运行。要创建此环境，应用程序可以检查设备的以下内容：

- PIN 或密码保护设备锁定
- 最近的 Android 操作系统版本
- USB调试激活
- 设备加密
- 设备Root（另请参阅“测试Root检测”）

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_10)

要测试应用程序执行的设备访问安全策略，必须提供该策略的书面副本。该政策应该定义可用的检查及其执行。例如，一项检查可能要求应用仅在 Android 6.0（API 级别 23）或更高版本上运行，如果 Android 版本低于 6.0，则关闭应用或显示警告。

检查实现该策略的功能的源代码并确定它是否可以被绕过。

[*您可以通过查询Settings.Secure*](https://developer.android.com/reference/android/provider/Settings.Secure.html)的系统偏好设置来在 Android 设备上实施检查 。[*设备管理 API*](https://developer.android.com/guide/topics/admin/device-admin.html)提供了创建应用程序的技术，这些应用程序可以执行密码策略和设备加密。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_9)

动态分析取决于应用程序强制执行的检查及其预期行为。如果可以绕过检查，则必须对其进行验证。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#owasp-masvs)

- MSTG-STORAGE-1：“需要使用系统凭证存储设施来存储敏感数据，例如 PII、用户凭证或加密密钥。”
- MSTG-STORAGE-2：“不应将敏感数据存储在应用程序容器或系统凭证存储设施之外。”
- MSTG-STORAGE-3：“没有敏感数据写入应用程序日志。”
- MSTG-STORAGE-4：“除非是架构的必要部分，否则不会与第三方共享敏感数据。”
- MSTG-STORAGE-5：“键盘缓存在处理敏感数据的文本输入上被禁用。”
- MSTG-STORAGE-6：“没有敏感数据通过 IPC 机制公开。”
- MSTG-STORAGE-7：“没有敏感数据，例如密码或个人识别码，会通过用户界面暴露出来。”
- MSTG-STORAGE-8：“移动操作系统生成的备份中不包含任何敏感数据。”
- MSTG-STORAGE-9：“当移动到后台时，该应用程序会从视图中删除敏感数据。”
- MSTG-STORAGE-10：“该应用不会将敏感数据保存在内存中超过必要的时间，并且内存会在使用后明确清除。”
- MSTG-STORAGE-11：“该应用程序执行最低限度的设备访问安全策略，例如要求用户设置设备密码。”
- MSTG-PLATFORM-2：“来自外部来源和用户的所有输入都经过验证，并在必要时进行清理。这包括通过 UI、IPC 机制（如意图、自定义 URL 和网络来源）接收的数据。”

### 库（Libraries）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#libraries)

- [Java AES Crypto](https://github.com/tozny/java-aes-crypto)
- [SQL Cipher](https://www.zetetic.net/sqlcipher/sqlcipher-for-android)
- [Secure Preferences](https://github.com/scottyab/secure-preferences)
- [Themis](https://github.com/cossacklabs/themis)
