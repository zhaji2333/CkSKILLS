# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 7 · part 1

> 分段 1/2。索引见 `Android平台API-p7.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 7

> 分段 7/8。索引见 `Android平台API.md`。

## 承接

  //getters, setters, etc
  //..

}
```

现在您可以在另一个类中使用`ObjectInputStream`/读/写对象。`ObjectOutputStream`

#### JSON[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#json)

有几种方法可以将对象的内容序列化为 JSON。Android 自带`JSONObject`和`JSONArray`类。各种各样的库，包括[GSON](https://github.com/google/gson)、[Jackson](https://github.com/FasterXML/jackson-core)、[Moshi](https://github.com/square/moshi), 也可以使用。这些库之间的主要区别在于它们是否使用反射来组合对象、是否支持注释、是否创建不可变对象以及它们使用的内存量。请注意，几乎所有 JSON 表示都是基于字符串的，因此是不可变的。这意味着存储在 JSON 中的任何秘密都将更难从内存中删除。JSON 本身可以存储在任何地方，例如 (NoSQL) 数据库或文件。您只需要确保任何包含秘密的 JSON 都得到了适当的保护（例如，加密/HMACed）。[有关详细信息，请参阅“ Android 上](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)的数据存储”一章。下面是一个使用 GSON 编写和读取 JSON 的简单示例（来自 GSON 用户指南）。在这个例子中，一个实例的内容`BagOfPrimitives`被序列化成JSON：

```
class BagOfPrimitives {
  private int value1 = 1;
  private String value2 = "abc";
  private transient int value3 = 3;
  BagOfPrimitives() {
    // no-args constructor
  }
}

// Serialization
BagOfPrimitives obj = new BagOfPrimitives();
Gson gson = new Gson();
String json = gson.toJson(obj);  

// ==> json is {"value1":1,"value2":"abc"}
```

#### XML[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#xml)

有多种方法可以将对象的内容序列化为 XML 并返回。Android 自带的`XmlPullParser`接口允许易于维护的 XML 解析。Android 中有两种实现：`KXmlParser`和`ExpatPullParser`. [Android 开发人员指南](https://developer.android.com/training/basics/network-ops/xml#java)提供了有关如何使用它们的精彩文章。接下来，还有各种替代方案，例如`SAX`Java Runtime(运行时)附带的解析器。有关更多信息，请参阅[来自 ibm.com 的博文](https://www.ibm.com/developerworks/opensource/library/x-android/index.html)。与 JSON 类似，XML 存在主要基于字符串工作的问题，这意味着字符串类型的秘密将更难从内存中删除。XML 数据可以存储在任何地方（数据库、文件），但需要额外的保护以防秘密或不应更改的信息。见章节“[Android 上的数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)”以获取更多详细信息。如前所述：XML 中的真正危险在于[XML 外部实体 (XXE)](https://owasp.org/www-community/vulnerabilities/XML_External_Entity_(XXE)_Processing)攻击，因为它可能允许读取仍可在应用程序中访问的外部数据源。

#### 对象关系管理[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#orm)

有一些库提供直接将对象的内容存储在数据库中然后用数据库内容实例化对象的功能。这称为对象关系映射 (ORM)。使用 SQLite 数据库的库包括

- [OrmLite](http://ormlite.com/) ,
- [糖ORM](https://satyan.github.io/sugar/)，
- [GreenDAO](https://greenrobot.org/greendao/)和
- [活跃的Android](http://www.activeandroid.com/)。

另一方面，[Realm使用自己的数据库来存储类的内容。](https://realm.io/docs/java/latest/)ORM 可以提供的保护量主要取决于数据库是否加密。[有关详细信息，请参阅“ Android 上](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)的数据存储”一章。Realm 网站包含一个很好[的 ORM Lite 示例](https://github.com/j256/ormlite-examples/tree/master/android/HelloAndroid)。

#### 可包裹[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#parcelable)

[`Parcelable`](https://developer.android.com/reference/android/os/Parcelable.html)是类的接口，其实例可以写入[`Parcel`](https://developer.android.com/reference/android/os/Parcel.html). 包通常用于将类打包为`Bundle`for an 的一部分`Intent`。这是一个 Android 开发人员文档示例，它实现了`Parcelable`：

```
public class MyParcelable implements Parcelable {
     private int mData;

     public int describeContents() {
         return 0;
     }

     public void writeToParcel(Parcel out, int flags) {
         out.writeInt(mData);
     }

     public static final Parcelable.Creator<MyParcelable> CREATOR
             = new Parcelable.Creator<MyParcelable>() {
         public MyParcelable createFromParcel(Parcel in) {
             return new MyParcelable(in);
         }

         public MyParcelable[] newArray(int size) {
             return new MyParcelable[size];
         }
     };

     private MyParcelable(Parcel in) {
         mData = in.readInt();
     }
 }
```

因为这种涉及 Parcels 和 Intents 的机制可能会随着时间的推移而改变，并且`Parcelable`可能包含`IBinder`指针，`Parcelable`所以不建议通过存储数据到磁盘。

#### 协议缓冲区[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#protocol-buffers)

[Google 的Protocol Buffers](https://developers.google.com/protocol-buffers/)是一种平台和语言中立的机制，用于通过[二进制数据格式](https://developers.google.com/protocol-buffers/docs/encoding)序列化结构化数据。Protocol Buffers 存在一些漏洞，例如[CVE-2015-5237](https://www.cvedetails.com/cve/CVE-2015-5237/)。请注意，Protocol Buffers 不提供任何机密性保护：没有内置加密。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_8)

如果对象持久性用于在设备上存储敏感信息，请首先确保信息已加密并签名/HMAC。[有关详细信息，请参阅“Android上的数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)”和“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”章节。接下来，确保只有在用户通过身份验证后才能获得解密和验证密钥。[应按照最佳实践](https://wiki.sei.cmu.edu/confluence/display/java/SER04-J. Do not allow serialization and deserialization to bypass the security manager)中的定义，在正确的位置进行安全检查。

您可以随时采取一些通用的补救步骤：

1. 确保敏感数据在序列化/持久化后已被加密和 HMACed/签名。在使用数据之前评估签名或 HMAC。有关详细信息，请参阅“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”一章。
2. 确保无法轻易提取步骤 1 中使用的密钥。用户和/或应用程序实例应该经过适当的身份验证/授权才能获取密钥。[有关详细信息，请参阅“ Android 上](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)的数据存储”一章。
3. 确保反序列化对象中的数据在被主动使用之前经过仔细验证（例如，不利用业务/应用程序逻辑）。

对于注重可用性的高危应用，我们建议您`Serializable`只在序列化类稳定的情况下使用。其次，我们建议不要使用基于反射的持久化，因为

- 攻击者可以通过基于字符串的参数找到方法的签名
- 攻击者可能能够操纵基于反射的步骤来执行业务逻辑。

有关更多详细信息，请参阅“ [Android 反逆向防御](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/)”一章。

#### 对象序列化[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#object-serialization_1)

在源代码中搜索以下关键字：

- `import java.io.Serializable`
- `implements Serializable`

#### JSON[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#json_1)

如果您需要对抗内存转储，请确保非常敏感的信息没有以 JSON 格式存储，因为您无法保证使用标准库来防止反内存转储技术。您可以在相应的库中检查以下关键字：

**`JSONObject`**在源代码中搜索以下关键字：

- `import org.json.JSONObject;`
- `import org.json.JSONArray;`

**`GSON`**在源代码中搜索以下关键字：

- `import com.google.gson`
- `import com.google.gson.annotations`
- `import com.google.gson.reflect`
- `import com.google.gson.stream`
- `new Gson();`
- 注释，例如`@Expose`, `@JsonAdapter`, `@SerializedName`,`@Since`和`@Until`

**`Jackson`**在源代码中搜索以下关键字：

- `import com.fasterxml.jackson.core`
- `import org.codehaus.jackson`对于旧版本。

#### 对象关系管理[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#orm_1)

当您使用 ORM 库时，请确保数据存储在加密数据库中，并且在存储之前对类表示进行单独加密。[有关详细信息，请参阅“Android上的数据存储](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/)”和“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”章节。您可以在相应的库中检查以下关键字：

**`OrmLite`**在源代码中搜索以下关键字：

- `import com.j256.*`
- `import com.j256.dao`
- `import com.j256.db`
- `import com.j256.stmt`
- `import com.j256.table\`

请确保已禁用日志记录。

**`SugarORM`**在源代码中搜索以下关键字：

- `import com.github.satyan`
- `extends SugarRecord<Type>`
- 在 AndroidManifest 中，将有包含、和`meta-data`等值的条目。`DATABASE``VERSION``QUERY_LOG``DOMAIN_PACKAGE_NAME`

确保将`QUERY_LOG`其设置为 false。

**`GreenDAO`**在源代码中搜索以下关键字：

- `import org.greenrobot.greendao.annotation.Convert`
- `import org.greenrobot.greendao.annotation.Entity`
- `import org.greenrobot.greendao.annotation.Generated`
- `import org.greenrobot.greendao.annotation.Id`
- `import org.greenrobot.greendao.annotation.Index`
- `import org.greenrobot.greendao.annotation.NotNull`
- `import org.greenrobot.greendao.annotation.*`
- `import org.greenrobot.greendao.database.Database`
- `import org.greenrobot.greendao.query.Query`

**`ActiveAndroid`**在源代码中搜索以下关键字：

- `ActiveAndroid.initialize(<contextReference>);`
- `import com.activeandroid.Configuration`
- `import com.activeandroid.query.*`

**`Realm`**在源代码中搜索以下关键字：

- `import io.realm.RealmObject;`
- `import io.realm.annotations.PrimaryKey;`

