# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 1 · part 1

> 分段 1/2。索引见 `Android数据存储-p1.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 1

> 分段 1/6。索引见 `Android数据存储.md`。

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
