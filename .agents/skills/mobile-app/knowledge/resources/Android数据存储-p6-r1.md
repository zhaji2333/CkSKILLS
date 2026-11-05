# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 6 · part 1

> 分段 1/2。索引见 `Android数据存储-p6.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 6

> 分段 6/6。索引见 `Android数据存储.md`。

## 承接

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
