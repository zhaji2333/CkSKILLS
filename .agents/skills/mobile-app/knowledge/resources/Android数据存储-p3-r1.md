# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 3 · part 1

> 分段 1/2。索引见 `Android数据存储-p3.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 3

> 分段 3/6。索引见 `Android数据存储.md`。

## 承接

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

