# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 5 · part 1

> 分段 1/2。索引见 `Android平台API-p5.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 5

> 分段 5/8。索引见 `Android平台API.md`。

## 承接

                        sendUnrecognisedMessage();
                        return;
                    }
           }
   }
```

### 广播接收器[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#broadcast-receivers)

#### 检查 AndroidManifest[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-androidmanifest_2)

在“Android Insecure Bank”应用程序中，我们在清单中找到一个广播接收器，标识为`<receiver>`：

```
<receiver android:exported="true" android:name="com.android.insecurebankv2.MyBroadCastReceiver">
    <intent-filter>
        <action android:name="theBroadcast" />
    </intent-filter>
</receiver>
```

#### 检查源代码[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-source-code_2)

在源代码中搜索`sendBroadcast`、`sendOrderedBroadcast`和等字符串`sendStickyBroadcast`。确保应用程序不发送任何敏感数据。

如果 Intent 仅在应用程序内广播和接收，`LocalBroadcastManager`则可用于防止其他应用程序接收广播消息。这降低了泄露敏感信息的风险。

为了更多地了解接收器的用途，我们必须深入静态分析并搜索用于动态创建接收器的类`android.content.BroadcastReceiver`和方法的用法。`Context.registerReceiver`

以下目标应用程序源代码的摘录表明，广播接收器触发了包含用户解密密码的 SMS 消息的传输。

```
public class MyBroadCastReceiver extends BroadcastReceiver {
  String usernameBase64ByteString;
  public static final String MYPREFS = "mySharedPreferences";

  @Override
  public void onReceive(Context context, Intent intent) {
    // TODO Auto-generated method stub

        String phn = intent.getStringExtra("phonenumber");
        String newpass = intent.getStringExtra("newpass");

    if (phn != null) {
      try {
                SharedPreferences settings = context.getSharedPreferences(MYPREFS, Context.MODE_WORLD_READABLE);
                final String username = settings.getString("EncryptedUsername", null);
                byte[] usernameBase64Byte = Base64.decode(username, Base64.DEFAULT);
                usernameBase64ByteString = new String(usernameBase64Byte, "UTF-8");
                final String password = settings.getString("superSecurePassword", null);
                CryptoClass crypt = new CryptoClass();
                String decryptedPassword = crypt.aesDeccryptedString(password);
                String textPhoneno = phn.toString();
                String textMessage = "Updated Password from: "+decryptedPassword+" to: "+newpass;
                SmsManager smsManager = SmsManager.getDefault();
                System.out.println("For the changepassword - phonenumber: "+textPhoneno+" password is: "+textMessage);
smsManager.sendTextMessage(textPhoneno, null, textMessage, null, null);
          }
     }
  }
}
```

BroadcastReceivers 应该使用该`android:permission`属性；否则，其他应用程序可以调用它们。您可以使用它`Context.sendBroadcast(intent, receiverPermission);`来指定接收者[读取广播](https://developer.android.com/reference/android/content/Context#sendBroadcast(android.content.Intent, java.lang.String))所必须具有的权限。您还可以设置一个明确的应用程序包名称，以限制此 Intent 将解析到的组件。如果保留为默认值 (null)，则将考虑所有应用程序中的所有组件。如果非空，则 Intent 只能匹配给定应用程序包中的组件。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_4)

[您可以使用MobSF](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#mobsf)枚举 IPC 组件。要列出所有导出的 IPC 组件，请上传 APK 文件，组件集合将显示在以下屏幕中：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05h/MobSF_Show_Components.png)

#### Content Provider(内容提供者)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#content-providers)

“Sieve”应用程序实现了一个易受攻击的内容提供程序。要列出 Sieve 应用程序导出的Content Provider(内容提供者)，请执行以下命令：

```
$ adb shell dumpsys package com.mwr.example.sieve | grep -Po "Provider{[\w\d\s\./]+}" | sort -u
Provider{34a20d5 com.mwr.example.sieve/.FileBackupProvider}
Provider{64f10ea com.mwr.example.sieve/.DBContentProvider}
```

一旦确定，您可以使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)对应用程序进行逆向工程并分析导出的内容提供程序的源代码以识别潜在的漏洞。

要识别Content Provider(内容提供者)的相应类别，请使用以下信息：

- 包裹名称：`com.mwr.example.sieve`.
- Content Provider(内容提供者)类名：`DBContentProvider`.

在分析类`com.mwr.example.sieve.DBContentProvider`时，您会看到它包含几个 URI：

```
package com.mwr.example.sieve;
...
public class DBContentProvider extends ContentProvider {
    public static final Uri KEYS_URI = Uri.parse("content://com.mwr.example.sieve.DBContentProvider/Keys");
    public static final Uri PASSWORDS_URI = Uri.parse("content://com.mwr.example.sieve.DBContentProvider/Passwords");
...
}
```

使用以下命令使用识别的 URI 调用Content Provider(内容提供者)：

```
$ adb shell content query --uri content://com.mwr.example.sieve.DBContentProvider/Keys/
Row: 0 Password=1234567890AZERTYUIOPazertyuiop, pin=1234

$ adb shell content query --uri content://com.mwr.example.sieve.DBContentProvider/Passwords/
Row: 0 _id=1, service=test, username=test, password=BLOB, email=t@tedt.com
Row: 1 _id=2, service=bank, username=owasp, password=BLOB, email=user@tedt.com

$ adb shell content query --uri content://com.mwr.example.sieve.DBContentProvider/Passwords/ --projection email:username:password --where 'service=\"bank\"'
Row: 0 email=user@tedt.com, username=owasp, password=BLOB
```

您现在可以检索所有数据库条目（查看输出中以“Row:”开头的所有行）。

#### 活动[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#activities_1)

要列出应用程序导出的活动，您可以使用以下命令并关注`activity`元素：

```
$ aapt d xmltree sieve.apk AndroidManifest.xml
...
E: activity (line=32)
  A: android:label(0x01010001)=@0x7f05000f
  A: android:name(0x01010003)=".FileSelectActivity" (Raw: ".FileSelectActivity")
  A: android:exported(0x01010010)=(type 0x12)0xffffffff
  A: android:finishOnTaskLaunch(0x01010014)=(type 0x12)0xffffffff
  A: android:clearTaskOnLaunch(0x01010015)=(type 0x12)0xffffffff
  A: android:excludeFromRecents(0x01010017)=(type 0x12)0xffffffff
E: activity (line=40)
  A: android:label(0x01010001)=@0x7f050000
  A: android:name(0x01010003)=".MainLoginActivity" (Raw: ".MainLoginActivity")
  A: android:excludeFromRecents(0x01010017)=(type 0x12)0xffffffff
  A: android:launchMode(0x0101001d)=(type 0x10)0x2
  A: android:windowSoftInputMode(0x0101022b)=(type 0x11)0x14
  E: intent-filter (line=46)
    E: action (line=47)
      A: android:name(0x01010003)="android.intent.action.MAIN" (Raw: "android.intent.action.MAIN")
    E: category (line=49)
      A: android:name(0x01010003)="android.intent.category.LAUNCHER" (Raw: "android.intent.category.LAUNCHER")
E: activity (line=52)
  A: android:label(0x01010001)=@0x7f050009
  A: android:name(0x01010003)=".PWList" (Raw: ".PWList")
  A: android:exported(0x01010010)=(type 0x12)0xffffffff
  A: android:finishOnTaskLaunch(0x01010014)=(type 0x12)0xffffffff
  A: android:clearTaskOnLaunch(0x01010015)=(type 0x12)0xffffffff
  A: android:excludeFromRecents(0x01010017)=(type 0x12)0xffffffff
E: activity (line=60)
  A: android:label(0x01010001)=@0x7f05000a
  A: android:name(0x01010003)=".SettingsActivity" (Raw: ".SettingsActivity")
  A: android:finishOnTaskLaunch(0x01010014)=(type 0x12)0xffffffff
  A: android:clearTaskOnLaunch(0x01010015)=(type 0x12)0xffffffff
  A: android:excludeFromRecents(0x01010017)=(type 0x12)0xffffffff
...
```

您可以使用以下属性之一标识导出的活动：

- 它有一个`intent-filter`子声明。
- 它具有`android:exported`.`0xffffffff`

您还可以使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)`AndroidManifest.xml`使用上述标准识别文件中导出的活动：

```
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.mwr.example.sieve">
...
  <!-- This activity is exported via the attribute "exported" -->
  <activity android:name=".FileSelectActivity" android:exported="true" />
   <!-- This activity is exported via the "intent-filter" declaration  -->
  <activity android:name=".MainLoginActivity">
    <intent-filter>
      <action android:name="android.intent.action.MAIN"/>
      <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
  </activity>
  <!-- This activity is exported via the attribute "exported" -->
  <activity android:name=".PWList" android:exported="true" />
  <!-- Activities below are not exported -->
  <activity android:name=".SettingsActivity" />
  <activity android:name=".AddEntryActivity"/>
  <activity android:name=".ShortLoginActivity" />
  <activity android:name=".WelcomeActivity" />
  <activity android:name=".PINActivity" />
...
</manifest>
```

枚举易受攻击的密码管理器“Sieve”中的活动表明导出了以下活动：

- `.MainLoginActivity`
- `.PWList`
- `.FileSelectActivity`

使用以下命令启动活动：

```
# Start the activity without specifying an action or an category
$ adb shell am start -n com.mwr.example.sieve/.PWList
Starting: Intent { cmp=com.mwr.example.sieve/.PWList }

# Start the activity indicating an action (-a) and an category (-c)
$ adb shell am start -n "com.mwr.example.sieve/.MainLoginActivity" -a android.intent.action.MAIN -c android.intent.category.LAUNCHER
Starting: Intent { act=android.intent.action.MAIN cat=[android.intent.category.LAUNCHER] cmp=com.mwr.example.sieve/.MainLoginActivity }
```

由于`.PWList`此示例中直接调用了该活动，因此您可以使用它绕过保护密码管理器的登录表单，并访问密码管理器中包含的数据。

#### 服务[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#services_1)

可以使用 Drozer 模块枚举服务`app.service.info`：

```
dz> run app.service.info -a com.mwr.example.sieve
Package: com.mwr.example.sieve
  com.mwr.example.sieve.AuthService
    Permission: null
  com.mwr.example.sieve.CryptoService
    Permission: null
```

要与服务通信，您必须首先使用静态分析来识别所需的输入。

