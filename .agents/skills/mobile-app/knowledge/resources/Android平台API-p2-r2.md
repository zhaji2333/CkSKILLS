# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 2 · part 2

> 分段 2/2。索引见 `Android平台API-p2.md`。

上面定义了一个Content Provider(内容提供者)，它`AndroidManifest.xml`被导出并因此可用于所有其他应用程序。应该检查类中的`query`函数。`OMTG_CODING_003_SQL_Injection_Content_Provider_Implementation.java`

```
@Override
public Cursor query(Uri uri, String[] projection, String selection,String[] selectionArgs, String sortOrder) {
    SQLiteQueryBuilder qb = new SQLiteQueryBuilder();
    qb.setTables(STUDENTS_TABLE_NAME);

    switch (uriMatcher.match(uri)) {
        case STUDENTS:
            qb.setProjectionMap(STUDENTS_PROJECTION_MAP);
            break;

        case STUDENT_ID:
            // SQL Injection when providing an ID
            qb.appendWhere( _ID + "=" + uri.getPathSegments().get(1));
            Log.e("appendWhere",uri.getPathSegments().get(1).toString());
            break;

        default:
            throw new IllegalArgumentException("Unknown URI " + uri);
    }

    if (sortOrder == null || sortOrder == ""){
        /**
         * By default sort on student names
         */
        sortOrder = NAME;
    }
    Cursor c = qb.query(db, projection, selection, selectionArgs,null, null, sortOrder);

    /**
     * register to watch a content URI for changes
     */
    c.setNotificationUri(getContext().getContentResolver(), uri);
    return c;
}
```

当用户在 提供 STUDENT_ID 时`content://sg.vp.owasp_mobile.provider.College/students`，查询语句容易出现 SQL 注入。显然，必须使用[准备好的语句](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)来避免 SQL 注入，但还应应用[输入验证，以便只处理应用程序期望的输入。](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

所有处理通过 UI 传入的数据的应用程序功能都应实施输入验证：

- 对于用户界面输入，可以使用[Android Saripaar v2 。](https://github.com/ragunathjawahar/android-saripaar)
- 对于来自 IPC 或 URL 方案的输入，应创建验证功能。例如，以下确定[字符串是否为字母数字](https://stackoverflow.com/questions/11241690/regex-for-checking-if-a-string-is-strictly-alphanumeric)：

```
public boolean isAlphaNumeric(String s){
    String pattern= "^[a-zA-Z0-9]*$";
    return s.matches(pattern);
}
```

验证函数的替代方法是类型转换，例如，`Integer.parseInt`如果只需要整数。[OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)包含有关此主题的更多信息。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_1)

测试人员应使用字符串手动测试输入字段`OR 1=1--`，例如，是否已识别出本地 SQL 注入漏洞。

在获得 root 权限的设备上，命令内容可用于从Content Provider(内容提供者)处查询数据。以下命令查询上述易受攻击的函数。

```
# content query --uri content://sg.vp.owasp_mobile.provider.College/students
```

可以使用以下命令利用 SQL 注入。用户可以检索所有数据，而不是只获取 Bob 的记录。

```
# content query --uri content://sg.vp.owasp_mobile.provider.College/students --where "name='Bob') OR 1=1--''"
```

## 片段注入测试 (MSTG-PLATFORM-2)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-fragment-injection-mstg-platform-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_2)

Android SDK 为开发人员提供了一种[`Preferences activity`](https://developer.android.com/reference/android/preference/PreferenceActivity.html)向用户呈现的方式，允许开发人员扩展和适配这个抽象类。

这个抽象类解析 Intent 的额外数据字段，特别是`PreferenceActivity.EXTRA_SHOW_FRAGMENT(:android:show_fragment)`和`Preference Activity.EXTRA_SHOW_FRAGMENT_ARGUMENTS(:android:show_fragment_arguments)`字段。

第一个字段应包含`Fragment`类名，第二个字段应包含传递给`Fragment`.

因为`PreferenceActivity`使用反射来加载片段，所以可能会在包或 Android SDK 中加载任意类。加载的类在导出此活动的应用程序的上下文中运行。

利用此漏洞，攻击者可以调用目标应用程序内部的片段或运行其他类的构造函数中存在的代码。任何在 Intent 中传递但不扩展 Fragment 类的类都将导致`java.lang.CastException`异常，但空构造函数将在抛出异常之前执行，从而允许类构造函数中存在的代码运行。

`isValidFragment`为了防止此漏洞，在 Android 4.4（API 级别 19）中添加了一个名为的新方法。它允许开发人员覆盖此方法并定义可能在此上下文中使用的片段。

默认实现返回`true`早于 Android 4.4（API 级别 19）的版本；它会在以后的版本中抛出异常。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_1)

脚步：

- 检查是否`android:targetSdkVersion`小于 19。
- 查找扩展`PreferenceActivity`类的导出活动。
- 确定该方法`isValidFragment`是否已被重写。
- 如果应用程序当前`android:targetSdkVersion`在清单中将其设置为小于 19 的值并且易受攻击的类不包含任何 then 的实现，`isValidFragment`则该漏洞继承自`PreferenceActivity`.
- 为了修复，开发人员应该将 更新`android:targetSdkVersion`到 19 或更高版本。或者，如果`android:targetSdkVersion`无法更新，则开发人员应按说明实施`isValidFragment`。

以下示例显示了扩展此活动的活动：

```
public class MyPreferences extends PreferenceActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
```

以下示例显示了使用仅`isValidFragment`允许加载的实现覆盖的方法`MyPreferenceFragment`：

```
@Override
protected boolean isValidFragment(String fragmentName)
{
return "com.fullpackage.MyPreferenceFragment".equals(fragmentName);
}
```

### 易受攻击的应用程序和利用示例[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#example-of-vulnerable-app-and-exploitation)

主活动类

```
