# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 1 · part 2

> 分段 2/2。索引见 `Android平台API-p1.md`。

`android:permission`通过标记内的属性应用的权限`<provider>`限制对 ContentProvider 中数据的访问。Content Provider(内容提供者)有一个重要的附加安全设施，称为 URI 权限，接下来将对其进行描述。与其他组件不同，ContentProvider 有两个可以设置的单独权限属性，`android:readPermission`限制谁可以从提供者读取，以及`android:writePermission`限制谁可以写入它。如果 ContentProvider 受读写权限保护，则仅持有写入权限不会同时授予读取权限。

当您第一次检索提供程序时以及使用 ContentProvider 执行操作时会检查权限。使用`ContentResolver.query`需要持有读权限；使用`ContentResolver.insert`, `ContentResolver.update`,`ContentResolver.delete`需要写权限。`SecurityException`如果在所有这些情况下都未持有适当的权限，则将从调用中抛出A。

### Content Provider(内容提供者) URI 权限[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#content-provider-uri-permissions)

与Content Provider(内容提供者)一起使用时，标准权限系统是不够的。例如，Content Provider(内容提供者)可能希望将权限限制为 READ 权限以保护自己，同时使用自定义 URI 来检索信息。应用程序应该只拥有该特定 URI 的权限。

解决方案是每个 URI 权限。当启动活动或从活动返回结果时，该方法可以设置`Intent.FLAG_GRANT_READ_URI_PERMISSION`和/或`Intent.FLAG_GRANT_WRITE_URI_PERMISSION`。这会授予特定 URI 的活动权限，而不管它是否有权访问来自Content Provider(内容提供者)的数据。

这允许一个通用的能力样式模型，其中用户交互驱动特别授予细粒度的权限。这可能是将应用程序所需的权限减少到仅与其行为直接相关的权限的关键工具。如果没有此模型，恶意用户可能会通过未受保护的 URI 访问其他成员的电子邮件附件或收集联系人列表以供将来使用。在清单中，[`android:grantUriPermissions`](https://developer.android.com/guide/topics/manifest/provider-element#gprmsn)属性或节点有助于限制 URI。

### URI 权限的文档[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#documentation-for-uri-permissions)

- [grantUriPermission](https://developer.android.com/reference/android/content/Context.html#grantUriPermission(java.lang.String, android.net.Uri, int))
- [撤销Uri权限](https://developer.android.com/reference/android/content/Context#revokeUriPermission(android.net.Uri, int))
- [检查Uri权限](https://developer.android.com/reference/android/content/Context#checkUriPermission(android.net.Uri, int, int, int))

#### 自定义权限[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#custom-permissions)

Android 允许应用程序将其服务/组件公开给其他应用程序。应用程序访问公开的组件需要自定义权限。您可以通过创建具有两个强制属性的权限标记来定义[自定义权限](https://developer.android.com/guide/topics/permissions/defining.html)：和。`AndroidManifest.xml``android:name``android:protectionLevel`

*创建遵守最小特权原则的*自定义权限至关重要：权限应明确定义其用途，并带有有意义且准确的标签和描述。

下面是一个名为 的自定义权限的示例，`START_MAIN_ACTIVITY`启动`TEST_ACTIVITY`Activity 时需要该权限。

第一个代码块定义了新的权限，这是不言自明的。label 标记是权限的摘要，description 是摘要的更详细版本。您可以根据将授予的权限类型设置保护级别。定义权限后，您可以通过将其添加到应用程序的清单来强制执行。在我们的示例中，第二个块表示我们将使用我们创建的权限来限制的组件。它可以通过添加`android:permission`属性来强制执行。

```
<permission android:name="com.example.myapp.permission.START_MAIN_ACTIVITY"
        android:label="Start Activity in myapp"
        android:description="Allow the app to launch the activity of myapp app, any app you grant this permission will be able to launch main activity by myapp app."
        android:protectionLevel="normal" />

<activity android:name="TEST_ACTIVITY"
    android:permission="com.example.myapp.permission.START_MAIN_ACTIVITY">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
     </intent-filter>
</activity>
```

创建权限后，应用程序可以通过文件中的标记`START_MAIN_ACTIVITY`请求它。任何授予自定义权限的应用程序都可以启动. 请注意必须在 之前声明，否则在Runtime(运行时)会发生异常。请参阅下面基于[权限概述](https://developer.android.com/guide/topics/permissions/overview)和[manifest-intro](https://developer.android.com/guide/topics/manifest/manifest-intro#filestruct)的示例。`uses-permission``AndroidManifest.xml``START_MAIN_ACTIVITY``TEST_ACTIVITY``<uses-permission android:name="myapp.permission.START_MAIN_ACTIVITY" />``<application>`

```
<manifest>
<uses-permission android:name="com.example.myapp.permission.START_MAIN_ACTIVITY" />
        <application>
            <activity>
            </activity>
        </application>
</manifest>
```

我们建议在注册权限时使用反向域注释，如上例（例如`com.domain.application.permission`），以避免与其他应用程序发生冲突。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis)

#### Android权限[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-permissions)

检查权限以确保应用确实需要它们并删除不必要的权限。例如，`INTERNET`AndroidManifest.xml 文件中的权限是 Activity 将网页加载到 WebView 所必需的。由于用户可以撤销应用程序使用危险权限的权利，因此开发人员应在每次执行需要该权限的操作时检查应用程序是否具有适当的权限。

```
<uses-permission android:name="android.permission.INTERNET" />
```

与开发人员一起检查权限，以确定每个权限集的用途并删除不必要的权限。

除了手动检查 AndroidManifest.xml 文件外，您还可以使用 Android 资产打包工具 (aapt) 检查 APK 文件的权限。

> aapt 随附于 build-tools 文件夹中的 Android SDK。它需要一个 APK 文件作为输入。您可以通过运行来列出设备中的 APK，`adb shell pm list packages -f | grep -i <keyword>`如“[列出已安装的应用程序](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#listing-installed-apps)”中所示。

```
$ aapt d permissions app-x86-debug.apk
package: sg.vp.owasp_mobile.omtg_android
uses-permission: name='android.permission.WRITE_EXTERNAL_STORAGE'
uses-permission: name='android.permission.INTERNET'
```

或者，您可以通过 adb 和 dumpsys 工具获得更详细的权限列表：

```
$ adb shell dumpsys package sg.vp.owasp_mobile.omtg_android | grep permission
    requested permissions:
      android.permission.WRITE_EXTERNAL_STORAGE
      android.permission.INTERNET
      android.permission.READ_EXTERNAL_STORAGE
    install permissions:
      android.permission.INTERNET: granted=true
      runtime permissions:
```

请参考此[权限概述](https://developer.android.com/guide/topics/permissions/overview#permission-groups)，了解列出的被视为危险的权限的说明。

```
READ_CALENDAR
WRITE_CALENDAR
READ_CALL_LOG
WRITE_CALL_LOG
PROCESS_OUTGOING_CALLS
CAMERA
READ_CONTACTS
WRITE_CONTACTS
GET_ACCOUNTS
ACCESS_FINE_LOCATION
ACCESS_COARSE_LOCATION
RECORD_AUDIO
READ_PHONE_STATE
READ_PHONE_NUMBERS
CALL_PHONE
ANSWER_PHONE_CALLS
ADD_VOICEMAIL
USE_SIP
BODY_SENSORS
SEND_SMS
RECEIVE_SMS
READ_SMS
RECEIVE_WAP_PUSH
RECEIVE_MMS
READ_EXTERNAL_STORAGE
WRITE_EXTERNAL_STORAGE
```

#### 自定义权限[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#custom-permissions_1)

