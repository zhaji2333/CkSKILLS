# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis)

## 测试应用程序权限 (MSTG-PLATFORM-1)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-app-permissions-mstg-platform-1)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview)

Android 为每个已安装的应用程序分配一个独特的系统标识（Linux 用户 ID 和组 ID）。由于每个 Android 应用程序都在进程沙箱中运行，因此应用程序必须明确请求访问其沙箱之外的资源和数据。他们通过声明使用系统数据和功能所需的权限来请求此访问权限。根据数据或功能的敏感程度或关键程度，Android 系统会自动授予权限或要求用户批准请求。

Android 权限根据它们提供的保护级别分为四个不同的类别：

- **正常**：此权限允许应用程序访问隔离的应用程序级功能，而对其他应用程序、用户和系统的风险最小。对于以 Android 6.0（API 级别 23）或更高版本为目标的应用，这些权限会在安装时自动授予。对于针对较低 API 级别的应用程序，用户需要在安装时批准它们。例子：`android.permission.INTERNET`。
- **危险**：此权限通常允许应用程序以影响用户的方式控制用户数据或控制设备。安装时可能不会授予此类权限；该应用程序是否应该具有权限可能留给用户来决定。例子：`android.permission.RECORD_AUDIO`。
- **Signature**：仅当请求应用程序使用用于签署声明该权限的应用程序的相同证书进行签名时，才会授予此权限。如果签名匹配，将自动授予权限。此权限在安装时授予。例子：`android.permission.ACCESS_MOCK_LOCATION`。
- **SystemOrSignature**：此权限仅授予嵌入系统映像中的应用程序或使用用于签署声明该权限的应用程序的相同证书签名的应用程序。例子：`android.permission.ACCESS_DOWNLOAD_MANAGER`。

可以在[Android 开发人员文档](https://developer.android.com/guide/topics/permissions/overview.html)中找到所有权限的列表以及有关如何执行以下操作的具体步骤：

- 在应用的清单文件中[声明应用权限。](https://developer.android.com/training/permissions/declaring)
- 以编程[方式请求应用权限。](https://developer.android.com/training/permissions/requesting)
- [定义自定义应用程序权限](https://developer.android.com/guide/topics/permissions/defining)以与其他应用程序共享您的应用程序资源和功能。

#### Android 8.0（API 级别 26）更改[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-80-api-level-26-changes)

以下[更改](https://developer.android.com/about/versions/oreo/android-8.0-changes#atap)会影响在 Android 8.0（API 级别 26）上运行的所有应用，甚至会影响那些针对较低 API 级别的应用。

- **联系人提供程序使用统计信息更改**：当应用程序请求[`READ_CONTACTS`](https://developer.android.com/reference/android/Manifest.permission.html#READ_CONTACTS)权限时，对联系人使用数据的查询将返回近似值而不是精确值（自动完成 API 不受此更改的影响）。

以 Android 8.0（API 级别 26）或更高版本为目标平台的应用[会受到](https://developer.android.com/about/versions/oreo/android-8.0-changes#o-apps)以下影响：

- **帐户访问和可发现性改进**：应用程序不再只能通过[`GET_ACCOUNTS`](https://developer.android.com/reference/android/Manifest.permission.html#GET_ACCOUNTS)授予权限来访问用户帐户，除非身份验证器拥有帐户或用户授予该访问权限。

- **新的电话权限**：以下权限（分类为危险）现在是`PHONE`权限组的一部分：

- 该`ANSWER_PHONE_CALLS`权限允许以编程方式接听来电（通过`acceptRingingCall`）。

- 该`READ_PHONE_NUMBERS`权限授予对存储在设备中的电话号码的读取权限。

- **授予危险权限时的限制**：危险权限分为权限组（例如`STORAGE`组包含`READ_EXTERNAL_STORAGE`和`WRITE_EXTERNAL_STORAGE`）。在 Android 8.0（API 级别 26）之前，为了同时获得该组的所有权限，请求该组的一个权限就足够了。这[从 Android 8.0（API 级别 26）开始](https://developer.android.com/about/versions/oreo/android-8.0-changes#rmp)发生了变化：每当应用程序在Runtime(运行时)请求权限时，系统将专门授予该特定权限。但是，请注意，**该权限组中的所有后续权限请求都将自动授予**，而不会向用户显示权限对话框。请参阅 Android 开发人员文档中的示例：

  > 假设某个应用在其清单中列出了 READ_EXTERNAL_STORAGE 和 WRITE_EXTERNAL_STORAGE。该应用程序请求 READ_EXTERNAL_STORAGE 并且用户授予它。如果应用程序的目标 API 级别为 25 或更低，系统也会同时授予 WRITE_EXTERNAL_STORAGE，因为它属于同一个 STORAGE 权限组并且也在清单中注册。如果应用程序针对 Android 8.0（API 级别 26），系统此时仅授予 READ_EXTERNAL_STORAGE；但是，如果应用稍后请求 WRITE_EXTERNAL_STORAGE，系统会立即授予该权限，而不会提示用户。

  [您可以在Android 开发人员文档](https://developer.android.com/guide/topics/permissions/overview.html#permission-groups)中查看权限组列表。为了让这更令人困惑，[谷歌还警告说](https://developer.android.com/guide/topics/permissions/overview.html#perm-groups)，在 Android SDK 的未来版本中，特定权限可能会从一个组移动到另一个组，因此，应用程序的逻辑不应依赖于这些权限组的结构。最佳做法是在需要时明确请求每个权限。

#### Android 9（API 级别 28）更改[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-9-api-level-28-changes)

以下[更改](https://developer.android.com/about/versions/pie/android-9.0-changes-all)会影响在 Android 9 上运行的所有应用，甚至会影响那些针对 API 级别低于 28 的应用。

- **对通话记录的限制访问**：`READ_CALL_LOG`、`WRITE_CALL_LOG`和`PROCESS_OUTGOING_CALLS`（危险）权限已移至`PHONE`新`CALL_LOG`权限组。这意味着能够拨打电话（例如，通过`PHONE`授予组的权限）不足以访问通话记录。
- **限制访问电话号码**`READ_CALL_LOG`：在 Android 9（API 级别 28）上Runtime(运行时)，想要读取电话号码的应用需要获得许可。
- **限制访问 Wi-Fi 位置和连接信息**：无法检索 SSID 和 BSSID 值（例如通过[`WifiManager.getConnectionInfo`](https://developer.android.com/reference/android/net/wifi/WifiManager#getConnectionInfo())，除非满足以下*所有*条件：
- 或`ACCESS_FINE_LOCATION`许可`ACCESS_COARSE_LOCATION`。
- `ACCESS_WIFI_STATE`许可。
- 位置服务已启用（在**Settings** -> **Location**下）。

以 Android 9（API 级别 28）或更高版本为目标平台的应用[会受到](https://developer.android.com/about/versions/pie/android-9.0-changes-28)以下影响：

- **构建序列号弃用**[`Build.getSerial`](https://developer.android.com/reference/android/os/Build.html#getSerial())：除非`READ_PHONE_STATE`授予（危险）权限，否则无法读取设备的硬件序列号（例如通过）。

#### Android 10（API 级别 29）更改[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-10-api-level-29-changes)

Android 10（API 级别 29）引入了多项[用户隐私增强功能](https://developer.android.com/about/versions/10/highlights#privacy_for_users)。有关权限的更改会影响在 Android 10（API 级别 29）上运行的所有应用程序，包括那些针对较低 API 级别的应用程序。

- **受限**的位置访问：“仅在使用应用程序时”的位置访问的新权限选项。
- **默认范围存储**：针对 Android 10（API 级别 29）的应用无需声明任何存储权限即可访问外部存储中应用特定目录中的文件以及从媒体存储创建的文件。
- **对屏幕内容的限制访问**: `READ_FRAME_BUFFER`、`CAPTURE_VIDEO_OUTPUT`和`CAPTURE_SECURE_VIDEO_OUTPUT`权限现在仅限签名访问，这可防止静默访问设备的屏幕内容。
- **面向用户的遗留应用程序权限检查**：首次运行针对 Android 5.1（API 级别 22）或更低版本的应用程序时，系统会提示用户使用权限屏幕，他们可以在其中撤销对特定*遗留权限*的访问（以前是安装时自动授予）。

### 活动许可执行[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#activity-permission-enforcement)

权限通过清单中标记`android:permission`内的属性应用。`<activity>`这些权限限制哪些应用程序可以启动该活动。`Context.startActivity`在和期间检查权限`Activity.startActivityForResult`。不持有所需的权限会导致`SecurityException`调用被抛出。

### 服务权限执行[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#service-permission-enforcement)

```
android:permission`通过清单中标记内的属性应用的权限`<service>`限制谁可以启动或绑定到关联的服务。在和`Context.startService`期间检查权限。不持有所需的权限会导致调用被抛出。`Context.stopService``Context.bindService``SecurityException
```

### 广播许可执行[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#broadcast-permission-enforcement)

`android:permission`通过标签内的属性应用的权限`<receiver>`限制将广播发送到关联的`BroadcastReceiver`. 返回后检查持有的权限`Context.sendBroadcast`，同时尝试将发送的广播传递给给定的接收者。不持有所需的权限不会引发异常，结果是未发送的广播。

可以提供权限`Context.registerReceiver`以控制谁可以向以编程方式注册的接收器广播。换句话说，可以在调用时提供权限`Context.sendBroadcast`以限制允许哪些广播接收器接收广播。

请注意，接收者和广播者都可能需要许可。发生这种情况时，两个权限检查都必须通过才能将意图传递给关联的目标。有关详细信息，请参阅Android 开发人员文档中的“[使用权限限制广播”部分。](https://developer.android.com/guide/components/broadcasts#restrict-broadcasts-permissions)

### Content Provider(内容提供者)许可执行[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#content-provider-permission-enforcement)

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

除了通过应用程序清单文件强制执行自定义权限外，您还可以通过编程方式检查权限。但是，不建议这样做，因为它更容易出错，并且可以更容易地通过Runtime(运行时)检测等方式绕过。建议`ContextCompat.checkSelfPermission`调用该方法来检查活动是否具有指定权限。每当您看到类似以下代码段的代码时，请确保在清单文件中强制执行相同的权限。

```
private static final String TAG = "LOG";
int canProcess = checkCallingOrSelfPermission("com.example.perm.READ_INCOMING_MSG");
if (canProcess != PERMISSION_GRANTED)
throw new SecurityException();
```

或者`ContextCompat.checkSelfPermission`将其与清单文件进行比较。

```
if (ContextCompat.checkSelfPermission(secureActivity.this, Manifest.READ_INCOMING_MSG)
        != PackageManager.PERMISSION_GRANTED) {
            //!= stands for not equals PERMISSION_GRANTED
            Log.v(TAG, "Permission denied");
        }
```

### 请求权限[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#requesting-permissions)

如果您的应用程序具有需要在Runtime(运行时)请求的权限，则应用程序必须调用该`requestPermissions`方法才能获得它们。该应用程序将所需的权限和您指定的整数请求代码异步传递给用户，一旦用户选择接受或拒绝同一线程中的请求，就会返回。返回响应后，相同的请求代码将传递给应用程序的回调方法。

```
private static final String TAG = "LOG";
// We start by checking the permission of the current Activity
if (ContextCompat.checkSelfPermission(secureActivity.this,
        Manifest.permission.WRITE_EXTERNAL_STORAGE)
        != PackageManager.PERMISSION_GRANTED) {

    // Permission is not granted
    // Should we show an explanation?
    if (ActivityCompat.shouldShowRequestPermissionRationale(secureActivity.this,
        //Gets whether you should show UI with rationale for requesting permission.
        //You should do this only if you do not have permission and the permission requested rationale is not communicated clearly to the user.
            Manifest.permission.WRITE_EXTERNAL_STORAGE)) {
        // Asynchronous thread waits for the users response.
        // After the user sees the explanation try requesting the permission again.
    } else {
        // Request a permission that doesn't need to be explained.
        ActivityCompat.requestPermissions(secureActivity.this,
                new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE},
                MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE);
        // MY_PERMISSIONS_REQUEST_WRITE_EXTERNAL_STORAGE will be the app-defined int constant.
        // The callback method gets the result of the request.
    }
} else {
    // Permission already granted debug message printed in terminal.
    Log.v(TAG, "Permission already granted.");
}
```

请注意，如果您需要向用户提供任何信息或解释，则需要在调用之前完成`requestPermissions`，因为系统对话框一旦调用就无法更改。

### 处理对权限请求的响应[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#handling-responses-to-permission-requests)

现在您的应用程序必须重写系统方法`onRequestPermissionsResult`以查看是否授予了权限。此方法接收`requestCode`整数作为输入参数（与在 中创建的请求代码相同`requestPermissions`）。

以下回调方法可用于`WRITE_EXTERNAL_STORAGE`.

```
@Override //Needed to override system method onRequestPermissionsResult()
public void onRequestPermissionsResult(int requestCode, //requestCode is what you specified in requestPermissions()
        String permissions[], int[] permissionResults) {
    switch (requestCode) {
        case MY_PERMISSIONS_WRITE_EXTERNAL_STORAGE: {
            if (grantResults.length > 0
                && permissionResults[0] == PackageManager.PERMISSION_GRANTED) {
                // 0 is a canceled request, if int array equals requestCode permission is granted.
            } else {
                // permission denied code goes here.
                Log.v(TAG, "Permission denied");
            }
            return;
        }
        // Other switch cases can be added here for multiple permission checks.
    }
}
```

应该为每个需要的权限明确请求权限，即使已经请求了来自同一组的类似权限。对于以 Android 7.1（API 级别 25）及更早版本为目标的应用程序，如果用户授予该组请求的权限之一，Android 将自动向应用程序授予该权限组中的所有权限。从Android 8.0（API level 26）开始，如果用户已经授予了同一个权限组的权限，仍然会自动授予权限，但应用仍然需要显式请求该权限。在这种情况下，`onRequestPermissionsResult`处理程序将在没有任何用户交互的情况下自动触发。

例如，如果`READ_EXTERNAL_STORAGE`和`WRITE_EXTERNAL_STORAGE`都列在 Android Manifest 中，但只为 授予权限`READ_EXTERNAL_STORAGE`，则请求`WRITE_EXTERNAL_STORAGE`将自动获得权限，无需用户交互，因为它们在同一组中且未明确请求。

### 权限分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#permission-analysis)

始终检查应用程序是否正在请求它实际需要的权限。确保没有请求与应用程序目标无关的权限，尤其是权限`DANGEROUS`，`SIGNATURE`因为如果处理不当，它们会影响用户和应用程序。例如，如果单人游戏应用程序需要访问`android.permission.WRITE_SMS`.

在分析权限时，您应该调查应用程序的具体用例场景，并始终检查是否有任何`DANGEROUS`正在使用的权限的替换 API。一个很好的例子是[SMS Retriever API](https://developers.google.com/identity/sms-retriever/overview)，它在执行基于 SMS 的用户验证时简化了 SMS 权限的使用。通过使用此 API，应用程序不必声明`DANGEROUS`权限，这对应用程序的用户和开发人员都有利，他们不必提交[权限声明表](https://support.google.com/googleplay/android-developer/answer/9214102?hl=en)。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis)

可以使用 检索已安装应用程序的权限`adb`。以下摘录演示了如何检查应用程序使用的权限。

```
$ adb shell dumpsys package com.google.android.youtube
...
declared permissions:
  com.google.android.youtube.permission.C2D_MESSAGE: prot=signature, INSTALLED
requested permissions:
  android.permission.INTERNET
  android.permission.ACCESS_NETWORK_STATE
install permissions:
  com.google.android.c2dm.permission.RECEIVE: granted=true
  android.permission.USE_CREDENTIALS: granted=true
  com.google.android.providers.gsf.permission.READ_GSERVICES: granted=true  
...
```

输出显示使用以下类别的所有权限：

- **声明的权限**：所有*自定义*权限的列表。
- **请求和安装权限**：所有安装时权限的列表，包括*普通*权限和*签名*权限。
- **Runtime(运行时)权限**：所有*危险*权限的列表。

在进行动态分析时：

- [评估](https://developer.android.com/training/permissions/evaluating)应用程序是否真的需要请求的权限。例如：需要访问 的单人游戏`android.permission.WRITE_SMS`可能不是一个好主意。
- 在许多情况下，应用程序可以选择[声明权限的替代方法](https://developer.android.com/training/permissions/evaluating#alternatives)，例如：
- 请求`ACCESS_COARSE_LOCATION`权限而不是`ACCESS_FINE_LOCATION`. 或者甚至更好，根本不请求权限，而是要求用户输入邮政编码。
- 调用`ACTION_IMAGE_CAPTURE`或`ACTION_VIDEO_CAPTURE`意图操作而不是请求`CAMERA`权限。
- 在与蓝牙设备配对时使用[Companion Device Pairing](https://developer.android.com/guide/topics/connectivity/companion-device-pairing)（Android 8.0（API 级别 26）及更高版本）而不是声明`ACCESS_FINE_LOCATION`、`ACCESS_COARSE_LOCATIION`或`BLUETOOTH_ADMIN`权限。
- 使用[隐私仪表板](https://developer.android.com/training/permissions/explaining-access#privacy-dashboard)（Android 12（API 级别 31）及更高版本）验证应用如何[解释对敏感信息](https://developer.android.com/training/permissions/explaining-access)的访问。

要获取有关特定权限的详细信息，您可以参考[Android 文档](https://developer.android.com/reference/android/Manifest.permission)。

## 注入缺陷测试 (MSTG-PLATFORM-2)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-injection-flaws-mstg-platform-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_1)

Android 应用程序可以通过深层链接（这是 Intents 的一部分）公开功能。他们可以将功能公开给：

- 其他应用程序（通过深度链接或其他 IPC 机制，例如 Intents 或 BroadcastReceivers）。
- 用户（通过用户界面）。

来自这些来源的输入都不可信任；它必须经过验证和/或消毒。验证确保仅处理应用程序期望的数据。如果不强制执行验证，任何输入都可以发送到应用程序，这可能允许攻击者或恶意应用程序利用应用程序功能。

如果暴露了任何应用程序功能，则应检查源代码的以下部分：

- 深层链接。检查测试用例[“测试深层链接”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links-mstg-platform-3)以及进一步的测试场景。
- IPC 机制（意图、绑定器、Android 共享内存或广播接收器）。检查测试用例[“通过 IPC 测试敏感功能暴露”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-sensitive-functionality-exposure-through-ipc-mstg-platform-4)以及进一步的测试场景。
- 用户界面。检查测试用例[“测试覆盖攻击”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-overlay-attacks-mstg-platform-9)。

下面显示了一个易受攻击的 IPC 机制的示例。

您可以使用*ContentProvider*访问数据库信息，并且可以探测服务以查看它们是否返回数据。如果数据未正确验证，Content Provider(内容提供者)可能会在其他应用程序与其交互时容易发生 SQL 注入。请参阅以下易受攻击的*ContentProvider*实现。

```
<provider
    android:name=".OMTG_CODING_003_SQL_Injection_Content_Provider_Implementation"
    android:authorities="sg.vp.owasp_mobile.provider.College">
</provider>
```

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
public class MainActivity extends PreferenceActivity {
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
```

我的片段类

```
public class MyFragment extends Fragment {
    public void onCreate (Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragmentLayout, null);
        WebView myWebView = (WebView) wv.findViewById(R.id.webview);
        myWebView.getSettings().setJavaScriptEnabled(true);
        myWebView.loadUrl(this.getActivity().getIntent().getDataString());
        return v;
    }
}
```

要利用此易受攻击的 Activity，您可以使用以下代码创建一个应用程序：

```
Intent i = new Intent();
i.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK);
i.setClassName("pt.claudio.insecurefragment","pt.claudio.insecurefragment.MainActivity");
i.putExtra(":android:show_fragment","pt.claudio.insecurefragment.MyFragment");
i.setData(Uri.parse("https://security.claudio.pt"));
startActivity(i);
```

[Vulnerable App](https://github.com/clviper/android-fragment-injection/raw/master/vulnerableapp.apk)和Exploit [PoC App](https://github.com/clviper/android-fragment-injection/blob/master/exploit.apk)可供下载。

## 在 WebView 中测试 URL 加载 (MSTG-PLATFORM-2)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-url-loading-in-webviews-mstg-platform-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_3)

WebView 是 Android 的嵌入式组件，允许您的应用程序在您的应用程序中打开网页。除了与移动应用程序相关的威胁之外，WebViews 还可能使您的应用程序面临常见的网络威胁（例如 XSS、Open Redirect 等）。

测试 WebView 时要做的最重要的事情之一是确保只能在其中加载受信任的内容。任何新加载的页面都可能具有潜在的恶意，请尝试利用任何 WebView 绑定或尝试对用户进行网络钓鱼。除非您正在开发浏览器应用程序，否则通常您希望将加载的页面限制在您的应用程序的域中。一个好的做法是阻止用户甚至有机会在 WebViews 中输入任何 URL（这是 Android 上的默认设置）或导航到受信任的域之外。即使在受信任的域上导航时，仍然存在用户可能会遇到并单击指向不可信内容的其他链接的风险（例如，如果该页面允许其他用户发表评论）。此外，一些开发人员甚至可能会覆盖一些对用户有潜在危险的默认行为。有关详细信息，请参阅下面的静态分析部分。

#### 安全浏览 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#safebrowsing-api)

为了提供更安全的网络浏览体验，Android 8.1（API 级别 27）引入了[`SafeBrowsing API`](https://developers.google.com/safe-browsing/v4)，它允许您的应用程序检测 Google 已归类为已知威胁的 URL。

默认情况下，WebView 会向用户显示有关安全风险的警告，并提供加载 URL 或停止加载页面的选项。使用 SafeBrowsing API，您可以通过向 SafeBrowsing 报告威胁或执行特定操作（例如每次遇到已知威胁时返回安全状态）来自定义应用程序的行为。请查看[Android 开发者文档](https://developer.android.com/about/versions/oreo/android-8.1#safebrowsing)以获取使用示例。

您可以使用[SafetyNet 库](https://developer.android.com/training/safetynet/safebrowsing)独立于 WebView 使用 SafeBrowsing API ，该库实现了安全浏览网络协议 v4 的客户端。SafetyNet 允许您分析您的应用程序应该加载的所有 URL。您可以检查具有不同方案（例如 http、文件）的 URL，因为 SafeBrowsing 不了解 URL 方案`TYPE_POTENTIALLY_HARMFUL_APPLICATION`以及`TYPE_SOCIAL_ENGINEERING`威胁类型。

#### Virus Total API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#virus-total-api)

Virus Total 提供了一个 API，用于分析已知威胁的 URL 和本地文件。API 参考在[Virus Total 开发者页面](https://developers.virustotal.com/reference#getting-started)上可用。

> 发送要检查已知威胁的 URL 或文件时，请确保它们不包含可能危及用户隐私或暴露应用程序敏感内容的敏感数据。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_2)

正如我们之前提到的，应该仔细分析[处理页面导航](https://developer.android.com/guide/webapps/webview#HandlingNavigation)，尤其是当用户可能能够离开受信任的环境时。Android 上默认且最安全的行为是让默认网络浏览器打开用户可能在 WebView 中单击的任何链接。但是，可以通过配置`WebViewClient`允许导航请求由应用程序本身处理的 a 来修改此默认逻辑。如果是这种情况，请务必搜索并检查以下拦截回调函数：

- `shouldOverrideUrlLoading`允许您的应用程序通过返回来中止加载带有可疑内容`true`的 WebView，或者通过返回来允许 WebView 加载 URL `false`。注意事项：
- POST 请求不会调用此方法。
- 不会为 XmlHttpRequests、iFrames、HTML 或`<script>`标记中包含的“src”属性调用此方法。相反，`shouldInterceptRequest`应该注意这一点。
- `shouldInterceptRequest`允许应用程序从资源请求中返回数据。如果返回值为 null，WebView 将照常继续加载资源。否则，使用该`shouldInterceptRequest`方法返回的数据。注意事项：
- 为各种 URL 方案（例如 、 、 等）调用此回调，`http(s):`而不仅仅是那些通过网络发送请求的方案。`data:``file:`
- 这不是针对URL`javascript:`或通过 URL 访问的`blob:`资产。在重定向的情况下，这只会为初始资源 URL 调用，而不是任何后续的重定向 URL。`file:///android_asset/``file:///android_res/`
- 启用安全浏览后，这些 URL 仍会接受安全浏览检查，但开发人员可以通过回调允许 URL`setSafeBrowsingWhitelist`甚至忽略警告。`onSafeBrowsingHit`

如您所见，在测试配置了 WebViewClient 的 WebView 的安全性时需要考虑很多要点，因此请务必通过查看[`WebViewClient`文档](https://developer.android.com/reference/android/webkit/WebViewClient)仔细阅读并理解所有这些要点。

虽然默认值为`EnableSafeBrowsing`，`true`但某些应用程序可能会选择禁用它。要验证 SafeBrowsing 是否已启用，请检查 AndroidManifest.xml 文件并确保不存在以下配置：

```
<manifest>
    <application>
        <meta-data android:name="android.webkit.WebView.EnableSafeBrowsing"
                   android:value="false" />
        ...
    </application>
</manifest>
```

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_2)

动态测试深度链接的一种便捷方法是使用 Frida 或 frida-trace 并在使用应用程序并单击 WebView 中的链接时挂接`shouldOverrideUrlLoading`,方法。`shouldInterceptRequest`确保还Hook其他相关[`Uri`](https://developer.android.com/reference/android/net/Uri)方法，例如`getHost`，`getScheme`或`getPath`通常用于检查请求并匹配已知模式或拒绝列表的方法。

## 测试深层链接 (MSTG-PLATFORM-3)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links-mstg-platform-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_4)

*深层链接*是将用户直接带到应用程序中特定内容的任何方案的 URI。应用程序可以通过在 Android Manifest 上添加*意图过滤器*并从传入的意图中提取数据来将用户导航到正确的活动来[设置深层链接。](https://developer.android.com/training/app-links/deep-linking)

Android 支持两种类型的深层链接：

- **自定义 URL 方案**，它们是使用任何自定义 URL 方案的深层链接，例如`myapp://`（未经操作系统验证）。
- **Android 应用程序链接**（Android 6.0（API 级别 23）及更高版本），它们是使用`http://`和`https://`方案并包含`autoVerify`属性（触发操作系统验证）的深层链接。

#### 深度链接冲突[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#deep-link-collision)

使用未经验证的深层链接可能会导致严重问题 - 安装在用户设备上的任何其他应用程序都可以声明并尝试处理相同的意图，这被称为**深层链接冲突**。任何任意应用程序都可以声明对属于另一个应用程序的完全相同的深层链接的控制权。

在最新版本的 Android 中，这会导致向用户显示一个所谓的*消歧对话框*，要求他们选择应该处理深层链接的应用程序。用户可能会错误地选择恶意应用程序而不是合法应用程序。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05h/app-disambiguation.png)

#### Android应用链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-links)

为了解决深度链接冲突问题，Android 6.0（API 级别 23）引入了[**Android App Links**](https://developer.android.com/training/app-links)，这是基于开发者明确注册的网站 URL[验证的深度链接。](https://developer.android.com/training/app-links/verify-site-associations)单击应用程序链接将立即打开已安装的应用程序。

与未经验证的深层链接有一些关键区别：

- App Links 仅使用`http://`和`https://`方案，不允许任何其他自定义 URL 方案。
- 应用程序链接需要一个实时域才能通过 HTTPS提供[数字资产链接文件。](https://developers.google.com/digital-asset-links/v1/getting-started)
- 应用链接不会遭受深度链接冲突，因为当用户打开它们时它们不会显示消歧对话框。

#### 测试深层链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links)

任何现有的深层链接（包括应用链接）都可能增加应用的攻击面。这[包括许多风险](https://people.cs.vt.edu/gangwang/deep17.pdf)，例如链接劫持、敏感功能暴露等。应用程序运行的 Android 版本也会影响风险：

- 在 Android 12（API 级别 31）之前，如果应用程序有任何[不可验证的链接](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)，可能会导致系统无法验证该应用程序的所有 Android 应用程序链接。
- 从 Android 12（API 级别 31）开始，应用程序受益于[减少的攻击面](https://developer.android.com/training/app-links/deep-linking)。通用网络意图解析为用户的默认浏览器应用程序，除非目标应用程序已获准用于该网络意图中包含的特定域。

必须枚举和验证所有深层链接以确保正确的网站关联。他们执行的操作必须经过良好测试，尤其是所有输入数据，这些数据应被视为不可信，因此应始终进行验证。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_3)

#### 枚举深层链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#enumerate-deep-links)

**检查 Android 清单：**

[您可以通过使用 apktool 解码应用程序](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#exploring-the-app-package)并检查 Android Manifest 文件以查找[``元素](https://developer.android.com/guide/components/intents-filters.html#DataTest)来轻松确定是否定义了深层链接（有或没有自定义 URL 方案）。

- **自定义 Url 方案**：以下示例指定了一个深度链接，其中包含名为 的自定义 URL 方案`myapp://`。

```
<activity android:name=".MyUriActivity">
  <intent-filter>
      <action android:name="android.intent.action.VIEW" />
      <category android:name="android.intent.category.DEFAULT" />
      <category android:name="android.intent.category.BROWSABLE" />
      <data android:scheme="myapp" android:host="path" />
  </intent-filter>
</activity>
```

- **深层链接**：以下示例指定了一个同时使用`http://`和`https://`方案的深层链接，以及将激活它的主机和路径（在本例中，完整的 URL 为`https://www.myapp.com/my/app/path`）：

```
<intent-filter>
  ...
  <data android:scheme="http" android:host="www.myapp.com" android:path="/my/app/path" />
  <data android:scheme="https" android:host="www.myapp.com" android:path="/my/app/path" />
</intent-filter>
```

- **App Links**：如果`<intent-filter>`包含该标志`android:autoVerify="true"`，这会导致 Android 系统接触声明`android:host`以尝试访问[Digital Asset Links 文件](https://developers.google.com/digital-asset-links/v1/getting-started)以[验证 App Links](https://developer.android.com/training/app-links/verify-site-associations)。**只有验证成功才能将深度链接视为 App Link。**

```
<intent-filter android:autoVerify="true">
```

列出深层链接时，请记住，`<data>`同一元素中的元素`<intent-filter>`实际上合并在一起，以说明其组合属性的所有变化。

```
<intent-filter>
  ...
  <data android:scheme="https" android:host="www.example.com" />
  <data android:scheme="app" android:host="open.my.app" />
</intent-filter>
```

看起来这似乎只支持`https://www.example.com`和`app://open.my.app`。但是，它实际上支持：

- `https://www.example.com`
- `app://open.my.app`
- `app://www.example.com`
- `https://open.my.app`

**使用 Dumpsys：**

使用[adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)运行以下将显示所有方案的命令：

```
adb shell dumpsys package com.example.package
```

**使用Android“App Link Verification”测试仪：**

使用[Android“App Link Verification”Tester](https://github.com/inesmartins/Android-App-Link-Verification-Tester)脚本列出所有深层链接 ( `list-all`) 或仅列出应用程序链接 ( `list-applinks`)：

```
python3 deeplink_analyser.py -op list-all -apk ~/Downloads/example.apk

.MainActivity

app://open.my.app
app://www.example.com
https://open.my.app
https://www.example.com
```

#### 检查正确的网站关联[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-for-correct-website-association)

即使深层链接包含该`android:autoVerify="true"`属性，它们也必须经过*实际*验证才能被视为应用链接。您应该测试任何可能阻止完整验证的错误配置。

##### 自动验证[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#automatic-verification)

使用[Android“App Link Verification”Tester](https://github.com/inesmartins/Android-App-Link-Verification-Tester)脚本获取所有应用程序链接的验证状态 ( `verify-applinks`)。[请在此处](https://github.com/inesmartins/Android-App-Link-Verification-Tester#use-an-apk-to-check-for-dals-for-all-app-links)查看示例。

**仅适用于 Android 12（API 级别 31）或更高版本：**

无论应用程序是否针对 Android 12（API 级别 31），您都可以使用[adb来测试验证逻辑。](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)此功能允许您：

- [手动调用验证过程](https://developer.android.com/training/app-links/verify-site-associations#manual-verification)。
- [在您的设备上重置目标应用的 Android 应用链接的状态](https://developer.android.com/training/app-links/verify-site-associations#reset-state)。
- [调用域验证过程](https://developer.android.com/training/app-links/verify-site-associations#invoke-domain-verification)。

您还可以[查看验证结果](https://developer.android.com/training/app-links/verify-site-associations#review-results)。例如：

```
adb shell pm get-app-links com.example.package

com.example.package:
    ID: 01234567-89ab-cdef-0123-456789abcdef
    Signatures: [***]
    Domain verification state:
      example.com: verified
      sub.example.com: legacy_failure
      example.net: verified
      example.org: 1026
```

> `adb shell dumpsys package com.example.package`通过运行（仅适用于 Android 12（API 级别 31）或更高版本）可以找到相同的信息。

##### 人工验证[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#manual-verification)

本节详细介绍了验证过程失败或未实际触发的几个（可能有很多）原因。请参阅[Android 开发人员文档](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)和白皮书[“衡量 Android 移动深度链接的不安全性”](https://people.cs.vt.edu/gangwang/deep17.pdf)中的更多信息。

**检查[数字资产链接文件](https://developers.google.com/digital-asset-links/v1/getting-started)：**

- 检查**丢失**的数字资产链接文件：
- 尝试在域的`/.well-known/`路径中找到它。例子：`https://www.example.com/.well-known/assetlinks.json`
- 或尝试`https://digitalassetlinks.googleapis.com/v1/statements:list?source.web.site=www.example.com`
- 检查**通过 HTTP**提供的有效数字资产链接文件。
- 检查通过 HTTPS 提供的**无效**数字资产链接文件。例如：
- 该文件包含无效的 JSON。
- 该文件不包含目标应用程序的包。

**检查重定向：**

为了增强应用程序的安全性，如果服务器设置了诸如to或to之类的重定向，系统[不会验证应用程序的任何 Android 应用程序链接](https://developer.android.com/training/app-links/verify-site-associations#fix-errors)。`http://example.com``https://example.com``example.com``www.example.com`

**检查子域：**

如果意图过滤器列出了具有不同子域的多个主机，则每个域上都必须有一个有效的数字资产链接文件。例如，以下意向过滤器包括`www.example.com`和`mobile.example.com`作为接受的意向 URL 主机。

```
<application>
  <activity android:name=”MainActivity”>
    <intent-filter android:autoVerify="true">
      <action android:name="android.intent.action.VIEW" />
      <category android:name="android.intent.category.DEFAULT" />
      <category android:name="android.intent.category.BROWSABLE" />
      <data android:scheme="https" />
      <data android:scheme="https" />
      <data android:host="www.example.com" />
      <data android:host="mobile.example.com" />
    </intent-filter>
  </activity>
</application>
```

为了正确注册深层链接，必须在`https://www.example.com/.well-known/assetlinks.json`和上发布有效的数字资产链接文件`https://mobile.example.com/.well-known/assetlinks.json`。

**检查通配符：**

如果主机名包含通配符（例如`*.example.com`），您应该能够在根主机名处找到有效的数字资产链接文件：`https://example.com/.well-known/assetlinks.json`。

#### 检查处理程序方法[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-the-handler-method)

即使正确验证了深层链接，也应该仔细分析处理程序方法的逻辑。特别注意**用于传输数据的深层链接**（由用户或任何其他应用程序在外部控制）。

`<activity>`首先，从定义目标的 Android Manifest 元素中获取 Activity 的名称`<intent-filter>`并搜索 和 的[`getIntent`](https://developer.android.com/reference/android/content/Intent#getIntent(java.lang.String))用法[`getData`](https://developer.android.com/reference/android/content/Intent#getData())。在执行逆向工程时，这种定位这些方法的一般方法可以在大多数应用程序中使用，并且在尝试了解应用程序如何使用深度链接和处理任何外部提供的输入数据以及它是否可能受到任何类型的滥用时是关键。

以下示例是[使用 jadx 反编译](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#decompiling-java-code)的示例性 Kotlin 应用程序的片段。从[静态分析](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#enumerate-deep-links)我们知道它支持深度链接`deeplinkdemo://load.html/`作为`com.mstg.deeplinkdemo.WebViewActivity`.

```
// snippet edited for simplicity
public final class WebViewActivity extends AppCompatActivity {
    private ActivityWebViewBinding binding;

    public void onCreate(Bundle savedInstanceState) {
        Uri data = getIntent().getData();
        String html = data == null ? null : data.getQueryParameter("html");
        Uri data2 = getIntent().getData();
        String deeplink_url = data2 == null ? null : data2.getQueryParameter("url");
        View findViewById = findViewById(R.id.webView);
        if (findViewById != null) {
            WebView wv = (WebView) findViewById;
            wv.getSettings().setJavaScriptEnabled(true);
            if (deeplink_url != null) {
                wv.loadUrl(deeplink_url);
            ...
```

您可以简单地跟随`deeplink_url`String 变量并查看`wv.loadUrl`调用的结果。这意味着攻击者可以完全控制加载到 WebView 的 URL（如上所示启用了[JavaScript](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)。

同一个 WebView 也可能呈现攻击者控制的参数。在这种情况下，以下深层链接有效负载将在 WebView 的上下文中触发[反射跨站点脚本 (XSS) ：](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#cross-site-scripting-flaws-mstg-platform-2)

```
deeplinkdemo://load.html?attacker_controlled=<svg onload=alert(1)>
```

但是还有很多其他的可能性。请务必查看以下部分，以了解有关预期结果以及如何测试不同场景的更多信息：

- [“跨站点脚本缺陷 (MSTG-PLATFORM-2)”](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#cross-site-scripting-flaws-mstg-platform-2)。
- [“注入缺陷（MSTG-ARCH-2 和 MSTG-PLATFORM-2）”](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#injection-flaws-mstg-arch-2-and-mstg-platform-2)。
- [“测试对象持久性 (MSTG-PLATFORM-8)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-object-persistence-mstg-platform-8)。
- [“在 WebView 中测试 URL 加载 (MSTG-PLATFORM-2)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-url-loading-in-webviews-mstg-platform-2)
- [“在 WebView 中测试 JavaScript 执行 (MSTG-PLATFORM-5)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)
- [“测试 WebView 协议处理程序 (MSTG-PLATFORM-6)”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webview-protocol-handlers-mstg-platform-6)

此外，我们建议搜索和阅读公开报告（搜索词：）`"deep link*"|"deeplink*" site:https://hackerone.com/reports/`。例如：

- [“[HackerOne#1372667\] 能够从深层链接窃取不记名令牌”](https://hackerone.com/reports/1372667)
- [“[HackerOne#401793\] 不安全的深层链接导致敏感信息泄露”](https://hackerone.com/reports/401793)
- [“[HackerOne#583987\] Android 应用深层链接在后续操作中导致 CSRF”](https://hackerone.com/reports/583987)
- [“[HackerOne#637194\] 在 Android 应用程序中可以绕过生物识别安全功能”](https://hackerone.com/reports/637194)
- [“[HackerOne#341908\] XSS 通过直接消息深度链接”](https://hackerone.com/reports/341908)

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_3)

在这里，您将使用来自静态分析的深层链接列表来迭代和确定每个处理程序方法和处理的数据（如果有）。您将首先启动[Frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#frida)Hook，然后开始调用深层链接。

以下示例假定目标应用程序接受此深层链接：`deeplinkdemo://load.html`。但是，我们还不知道相应的处理程序方法，也不知道它可能接受的参数。

**[第一步] Frida Hooking：**

您可以使用[Frida CodeShare中的脚本](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#frida-codeshare)[“Android Deep Link Observer”](https://codeshare.frida.re/@leolashkevych/android-deep-link-observer/)来监控所有触发对. 您还可以使用该脚本作为基础，根据手头的用例包含您自己的修改。在这种情况下，我们在脚本中[包含堆栈跟踪](https://github.com/FrenchYeti/frida-trick/blob/master/README.md)，因为我们对调用.`Intent.getData``Intent.getData`

**[步骤 2] 调用深层链接：**

[现在，您可以使用adb](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#adb)和[活动管理器 (am)](https://developer.android.com/training/app-links/deep-linking#testing-filters)调用任何深层链接，这将在 Android 设备内发送意图。例如：

```
adb shell am start -W -a android.intent.action.VIEW -d "deeplinkdemo://load.html/?message=ok#part1"

Starting: Intent { act=android.intent.action.VIEW dat=deeplinkdemo://load.html/?message=ok }
Status: ok
LaunchState: WARM
Activity: com.mstg.deeplinkdemo/.WebViewActivity
TotalTime: 210
WaitTime: 217
Complete
```

> 这可能会在使用“http/https”架构时或其他已安装的应用程序支持相同的自定义 URL 架构时触发消歧对话框。您可以包含包名称以使其成为明确的意图。

此调用将记录以下内容：

```
[*] Intent.getData() was called
[*] Activity: com.mstg.deeplinkdemo.WebViewActivity
[*] Action: android.intent.action.VIEW

[*] Data
- Scheme: deeplinkdemo://
- Host: /load.html
- Params: message=ok
- Fragment: part1

[*] Stacktrace:

android.content.Intent.getData(Intent.java)
com.mstg.deeplinkdemo.WebViewActivity.onCreate(WebViewActivity.kt)
android.app.Activity.performCreate(Activity.java)
...
com.android.internal.os.ZygoteInit.main(ZygoteInit.java)
```

在这种情况下，我们制作了包含任意参数 ( `?message=ok`) 和片段 ( `#part1`) 的深层链接。我们仍然不知道它们是否被使用。上面的信息揭示了您现在可以用来对应用程序进行逆向工程的有用信息。请参阅[“检查处理程序方法”](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#check-the-handler-method)部分以了解您应该考虑的事项。

- 文件：`WebViewActivity.kt`
- 班级：`com.mstg.deeplinkdemo.WebViewActivity`
- 方法：`onCreate`

> 有时您甚至可以利用您知道与目标应用程序交互的其他应用程序。您可以对应用程序进行反向工程（例如，提取所有字符串并过滤那些包含目标深层链接的字符串，`deeplinkdemo:///load.html`在之前的案例中），或者将它们用作触发器，同时如前所述Hook应用程序。

## 通过 IPC 测试敏感功能暴露 (MSTG-PLATFORM-4)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-sensitive-functionality-exposure-through-ipc-mstg-platform-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_5)

在移动应用程序的实现过程中，开发人员可能会应用传统的 IPC 技术（例如使用共享文件或网络套接字）。应该使用移动应用平台提供的IPC系统功能，因为它比传统技术成熟得多。在没有考虑安全性的情况下使用 IPC 机制可能会导致应用程序泄漏或暴露敏感数据。

以下是可能暴露敏感数据的 Android IPC 机制列表：

- [粘合剂](https://developer.android.com/reference/android/os/Binder.html)
- [服务](https://developer.android.com/guide/components/services.html)
- [绑定服务](https://developer.android.com/guide/components/bound-services.html)
- [AIDL](https://developer.android.com/guide/components/aidl.html)
- [意图](https://developer.android.com/reference/android/content/Intent.html)
- [Content Provider(内容提供者)](https://developer.android.com/reference/android/content/ContentProvider.html)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_4)

我们首先查看 AndroidManifest.xml，其中必须声明源代码中包含的所有活动、服务和内容提供程序（否则系统将无法识别它们，它们将无法运行）。广播接收器可以在清单中声明或动态创建。您将想要识别元素，例如

- [``](https://developer.android.com/guide/topics/manifest/intent-filter-element.html)
- [``](https://developer.android.com/guide/topics/manifest/service-element.html)
- [``](https://developer.android.com/guide/topics/manifest/provider-element.html)
- [``](https://developer.android.com/guide/topics/manifest/receiver-element.html)

其他应用可以访问“导出的”活动、服务或内容。有两种常见的方法可以将组件指定为已导出。显而易见的是将 export 标签设置为 true `android:exported="true"`。第二种方式涉及`<intent-filter>`在组件元素内定义一个 ( `<activity>`, `<service>`, `<receiver>`)。完成后，导出标签会自动设置为“true”。为防止所有其他 Android 应用程序与 IPC 组件元素交互，请确保`android:exported="true"`值和 an`<intent-filter>`不在其`AndroidManifest.xml`文件中，除非这是必要的。

请记住，使用权限标记 ( `android:permission`) 还会限制其他应用程序对组件的访问。如果您的 IPC 旨在供其他应用程序访问，您可以对`<permission>`元素应用安全策略并设置适当的`android:protectionLevel`. 在服务声明中使用时，其他应用程序必须在自己的清单中`android:permission`声明相应的元素以启动、停止或绑定到服务。`<uses-permission>`

关于Content Provider(内容提供者)的更多信息，请参考“测试数据存储”章节中的测试用例“测试存储的敏感数据是否通过IPC机制暴露”。

一旦确定了 IPC 机制列表，请查看源代码以查看在使用这些机制时是否泄露了敏感数据。例如，Content Provider(内容提供者)可用于访问数据库信息，服务可被探测以查看它们是否返回数据。如果探测或嗅探，广播接收器可能会泄露敏感信息。

在下文中，我们使用两个示例应用程序并给出识别易受攻击的 IPC 组件的示例：

- [“Sieve”](https://github.com/mwrlabs/drozer/releases/download/2.3.4/sieve.apk)
- [“Android不安全银行”](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#insecurebankv2)

### 活动[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#activities)

#### 检查 AndroidManifest[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-androidmanifest)

在“Sieve”应用程序中，我们找到三个导出的活动，标识为`<activity>`：

```
<activity android:excludeFromRecents="true" android:label="@string/app_name" android:launchMode="singleTask" android:name=".MainLoginActivity" android:windowSoftInputMode="adjustResize|stateVisible">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>
</activity>
<activity android:clearTaskOnLaunch="true" android:excludeFromRecents="true" android:exported="true" android:finishOnTaskLaunch="true" android:label="@string/title_activity_file_select" android:name=".FileSelectActivity" />
<activity android:clearTaskOnLaunch="true" android:excludeFromRecents="true" android:exported="true" android:finishOnTaskLaunch="true" android:label="@string/title_activity_pwlist" android:name=".PWList" />
```

#### 检查源代码[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-source-code)

通过检查该`PWList.java`活动，我们看到它提供了列出所有键、添加、删除等选项。如果我们直接调用它，我们将能够绕过 LoginActivity。有关更多信息，请参见下面的动态分析。

### 服务[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#services)

#### 检查 AndroidManifest[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-androidmanifest_1)

在“Sieve”应用程序中，我们找到两个导出服务，标识为`<service>`：

```
<service android:exported="true" android:name=".AuthService" android:process=":remote" />
<service android:exported="true" android:name=".CryptoService" android:process=":remote" />
```

#### 检查源代码[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#inspect-the-source-code_1)

检查类的源代码`android.app.Service`：

通过对目标应用进行逆向，我们可以看到该服务`AuthService`提供了修改密码和PIN码保护目标应用的功能。

```
   public void handleMessage(Message msg) {
            AuthService.this.responseHandler = msg.replyTo;
            Bundle returnBundle = msg.obj;
            int responseCode;
            int returnVal;
            switch (msg.what) {
                ...
                case AuthService.MSG_SET /*6345*/:
                    if (msg.arg1 == AuthService.TYPE_KEY) /*7452*/ {
                        responseCode = 42;
                        if (AuthService.this.setKey(returnBundle.getString("com.mwr.example.sieve.PASSWORD"))) {
                            returnVal = 0;
                        } else {
                            returnVal = 1;
                        }
                    } else if (msg.arg1 == AuthService.TYPE_PIN) {
                        responseCode = 41;
                        if (AuthService.this.setPin(returnBundle.getString("com.mwr.example.sieve.PIN"))) {
                            returnVal = 0;
                        } else {
                            returnVal = 1;
                        }
                    } else {
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

因为此服务是导出的，所以您可以使用该模块`app.service.send`与服务通信并更改存储在目标应用程序中的密码：

```
dz> run app.service.send com.mwr.example.sieve com.mwr.example.sieve.AuthService --msg 6345 7452 1 --extra string com.mwr.example.sieve.PASSWORD "abcdabcdabcdabcd" --bundle-as-obj
Got a reply from com.mwr.example.sieve/com.mwr.example.sieve.AuthService:
  what: 4
  arg1: 42
  arg2: 0
  Empty
```

#### 广播接收器[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#broadcast-receivers_1)

要列出应用程序导出的广播接收器，您可以使用以下命令并关注`receiver`元素：

```
$ aapt d xmltree InsecureBankv2.apk AndroidManifest.xml
...
E: receiver (line=88)
  A: android:name(0x01010003)="com.android.insecurebankv2.MyBroadCastReceiver" (Raw: "com.android.insecurebankv2.MyBroadCastReceiver")
  A: android:exported(0x01010010)=(type 0x12)0xffffffff
  E: intent-filter (line=91)
    E: action (line=92)
      A: android:name(0x01010003)="theBroadcast" (Raw: "theBroadcast")
E: receiver (line=119)
  A: android:name(0x01010003)="com.google.android.gms.wallet.EnableWalletOptimizationReceiver" (Raw: "com.google.android.gms.wallet.EnableWalletOptimizationReceiver")
  A: android:exported(0x01010010)=(type 0x12)0x0
  E: intent-filter (line=122)
    E: action (line=123)
      A: android:name(0x01010003)="com.google.android.gms.wallet.ENABLE_WALLET_OPTIMIZATION" (Raw: "com.google.android.gms.wallet.ENABLE_WALLET_OPTIMIZATION")
...
```

您可以使用以下属性之一标识导出的广播接收器：

- 它有一个`intent-filter`子声明。
- 它的属性`android:exported`设置为`0xffffffff`。

您还可以使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)`AndroidManifest.xml`使用上述标准识别文件中导出的广播接收器：

```
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.android.insecurebankv2">
...
  <!-- This broadcast receiver is exported via the attribute "exported" as well as the "intent-filter" declaration -->
  <receiver android:name="com.android.insecurebankv2.MyBroadCastReceiver" android:exported="true">
    <intent-filter>
      <action android:name="theBroadcast"/>
    </intent-filter>
  </receiver>
  <!-- This broadcast receiver is NOT exported because the attribute "exported" is explicitly set to false -->
  <receiver android:name="com.google.android.gms.wallet.EnableWalletOptimizationReceiver" android:exported="false">
    <intent-filter>
      <action android:name="com.google.android.gms.wallet.ENABLE_WALLET_OPTIMIZATION"/>
    </intent-filter>
  </receiver>
...
</manifest>
```

以上来自易受攻击的银行应用程序[InsecureBankv2](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#insecurebankv2)的示例表明，仅`com.android.insecurebankv2.MyBroadCastReceiver`导出名为的广播接收器。

现在您知道有一个导出的广播接收器，您可以深入研究并使用[jadx](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#jadx)对应用程序进行逆向工程。这将允许您分析源代码，寻找您以后可以尝试利用的潜在漏洞。导出的广播接收器源代码如下：

```
package com.android.insecurebankv2;
...
public class MyBroadCastReceiver extends BroadcastReceiver {
    public static final String MYPREFS = "mySharedPreferences";
    String usernameBase64ByteString;

    public void onReceive(Context context, Intent intent) {
        String phn = intent.getStringExtra("phonenumber");
        String newpass = intent.getStringExtra("newpass");
        if (phn != null) {
            try {
                SharedPreferences settings = context.getSharedPreferences("mySharedPreferences", 1);
                this.usernameBase64ByteString = new String(Base64.decode(settings.getString("EncryptedUsername", (String) null), 0), "UTF-8");
                String decryptedPassword = new CryptoClass().aesDeccryptedString(settings.getString("superSecurePassword", (String) null));
                String textPhoneno = phn.toString();
                String textMessage = "Updated Password from: " + decryptedPassword + " to: " + newpass;
                SmsManager smsManager = SmsManager.getDefault();
                System.out.println("For the changepassword - phonenumber: " + textPhoneno + " password is: " + textMessage);
                smsManager.sendTextMessage(textPhoneno, (String) null, textMessage, (PendingIntent) null, (PendingIntent) null);
            } catch (Exception e) {
                e.printStackTrace();
            }
        } else {
            System.out.println("Phone number is null");
        }
    }
}
```

正如您在源代码中所见，此广播接收器需要两个名为`phonenumber`和的参数`newpass`。有了这些信息，您现在可以尝试通过使用自定义值向它发送事件来利用这个广播接收器：

```
# Send an event with the following properties:
# Action is set to "theBroadcast"
# Parameter "phonenumber" is set to the string "07123456789"
# Parameter "newpass" is set to the string "12345"
$ adb shell am broadcast -a theBroadcast --es phonenumber "07123456789" --es newpass "12345"
Broadcasting: Intent { act=theBroadcast flg=0x400000 (has extras) }
Broadcast completed: result=0
```

这会生成以下 SMS：

```
Updated Password from: SecretPassword@ to: 12345
```

##### 嗅探意图[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#sniffing-intents)

如果 Android 应用程序在未设置所需权限或指定目标包的情况下广播意图，则该意图可以被设备上运行的任何应用程序监视。

要注册广播接收器以嗅探意图，请使用 Drozer 模块`app.broadcast.sniff`并使用参数指定要监视的操作`--action`：

```
dz> run app.broadcast.sniff  --action theBroadcast
[*] Broadcast receiver registered to sniff matching intents
[*] Output is updated once a second. Press Control+C to exit.

Action: theBroadcast
Raw: Intent { act=theBroadcast flg=0x10 (has extras) }
Extra: phonenumber=07123456789 (java.lang.String)
Extra: newpass=12345 (java.lang.String)`
```

您还可以使用以下命令来嗅探意图。但是不会显示extras传递的内容：

```
$ adb shell dumpsys activity broadcasts | grep "theBroadcast"
BroadcastRecord{fc2f46f u0 theBroadcast} to user 0
Intent { act=theBroadcast flg=0x400010 (has extras) }
BroadcastRecord{7d4f24d u0 theBroadcast} to user 0
Intent { act=theBroadcast flg=0x400010 (has extras) }
45: act=theBroadcast flg=0x400010 (has extras)
46: act=theBroadcast flg=0x400010 (has extras)
121: act=theBroadcast flg=0x400010 (has extras)
144: act=theBroadcast flg=0x400010 (has extras)
```

## 在 WebView 中测试 JavaScript 执行 (MSTG-PLATFORM-5)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-javascript-execution-in-webviews-mstg-platform-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_6)

JavaScript 可以通过反射、存储或基于 DOM 的跨站点脚本 (XSS) 注入 Web 应用程序。移动应用程序在沙盒环境中执行，在Native实现时不存在此漏洞。然而，WebViews 可能是本地应用程序的一部分，以允许查看网页。每个应用程序都有自己的 WebView 缓存，不会与Native浏览器或其他应用程序共享。在 Android 上，WebViews 使用 WebKit 渲染引擎来显示网页，但页面被精简到最少的功能，例如，页面没有地址栏。如果 WebView 实现过于松散并允许使用 JavaScript，则 JavaScript 可用于攻击应用程序并获取对其数据的访问权限。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_5)

必须检查源代码以了解 WebView 类的用法和实现。要创建和使用 WebView，您必须创建 WebView 类的实例。

```
WebView webview = new WebView(this);
setContentView(webview);
webview.loadUrl("https://www.owasp.org/");
```

可以对 WebView 应用各种设置（激活/停用 JavaScript 就是一个例子）。WebView 默认禁用 JavaScript，必须明确启用。寻找[`setJavaScriptEnabled`](https://developer.android.com/reference/android/webkit/WebSettings#setJavaScriptEnabled(boolean))检查 JavaScript 激活的方法。

```
webview.getSettings().setJavaScriptEnabled(true);
```

这允许 WebView 解释 JavaScript。只有在必要时才应启用它以减少应用程序的攻击面。如果需要 JavaScript，您应该确保

- 与端点的通信始终依赖 HTTPS（或其他允许加密的协议）来保护 HTML 和 JavaScript 在传输过程中不被篡改。
- JavaScript 和 HTML 在本地加载，从应用程序数据目录内或仅从受信任的 Web 服务器加载。
- 用户无法通过基于用户提供的输入加载不同的资源来定义加载哪些源。

要删除所有 JavaScript 源代码和本地存储的数据，请[`clearCache`](https://developer.android.com/reference/android/webkit/WebView#clearCache(boolean))在应用关闭时清除 WebView 的缓存。

运行早于 Android 4.4（API 级别 19）的平台的设备使用存在多个安全问题的 WebKit 版本。作为解决方法，如果应用程序在这些设备上运行，则应用程序必须确认 WebView 对象[仅显示受信任的内容。](https://developer.android.com/training/articles/security-tips.html#WebView)

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_5)

动态分析取决于操作条件。有几种方法可以将 JavaScript 注入到应用程序的 WebView 中：

- 端点中存储的跨站点脚本漏洞；当用户导航到易受攻击的功能时，漏洞将被发送到移动应用程序的 WebView。
- 攻击者占据中间人 (MITM) 位置并通过注入 JavaScript 篡改响应。
- 恶意软件篡改由 WebView 加载的本地文件。

要解决这些攻击向量，请检查以下内容：

- 端点提供的所有功能都应该没有[存储的 XSS](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/02-Testing_for_Stored_Cross_Site_Scripting)。
- 只有应用程序数据目录中的文件应该在 WebView 中呈现（请参阅测试用例“测试本地文件包含在 WebView 中”）。
- 必须根据最佳实践实施 HTTPS 通信以避免 MITM 攻击。这表示：
- 所有通信都通过 TLS 加密（请参阅测试用例“测试网络上未加密的敏感数据”），
- 证书被正确检查（参见测试用例“测试端点识别验证”），和/或
- 应该固定证书（请参阅“测试自定义证书存储和证书固定”）。

## 测试 WebView 协议处理程序 (MSTG-PLATFORM-6)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webview-protocol-handlers-mstg-platform-6)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_7)

Android URL 有几种默认[架构。](https://developer.android.com/guide/appendix/g-app-intents.html)它们可以在 WebView 中通过以下方式触发：

- http(s)://
- 文件：//
- 电话：//

WebView 可以从端点加载远程内容，但它们也可以从应用程序数据目录或外部存储加载本地内容。如果加载本地内容，用户不应该能够影响文件名或用于加载文件的路径，并且用户不应该能够编辑加载的文件。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_6)

检查 WebView 使用的源代码。以下[WebView 设置](https://developer.android.com/reference/android/webkit/WebSettings.html)控制资源访问：

- `setAllowContentAccess`: 内容 URL 访问允许 WebViews 从系统上安装的内容提供程序加载内容，默认情况下启用。
- `setAllowFileAccess`：启用和禁用 WebView 中的文件访问。默认值是`true`针对 Android 10（API 级别 29）及更低版本以及`false`Android 11（API 级别 30）及更高版本。请注意，这仅启用和禁用[文件系统访问](https://developer.android.com/reference/android/webkit/WebSettings.html#setAllowFileAccess(boolean))。资产和资源访问不受影响，可通过`file:///android_asset`和访问`file:///android_res`。
- `setAllowFileAccessFromFileURLs`：是否允许在文件方案 URL 的上下文中运行的 JavaScript 访问来自其他文件方案 URL 的内容。默认值适用`true`于 Android 4.0.3 - 4.0.4（API 级别 15）及更低版本以及`false`Android 4.1（API 级别 16）及更高版本。
- `setAllowUniversalAccessFromFileURLs`：是否允许在文件方案 URL 上下文中运行的 JavaScript 访问来自任何来源的内容。默认值适用`true`于 Android 4.0.3 - 4.0.4（API 级别 15）及更低版本以及`false`Android 4.1（API 级别 16）及更高版本。

如果激活了上述一种或多种方法，您应该确定这些方法是否真的是应用程序正常运行所必需的。

如果能识别到WebView实例，则通过该方法判断是否加载了本地文件[`loadURL`](https://developer.android.com/reference/android/webkit/WebView.html#loadUrl(java.lang.String))。

```
WebView = new WebView(this);
webView.loadUrl("file:///android_asset/filename.html");
```

必须验证加载 HTML 文件的位置。例如，如果文件是从外部存储加载的，则该文件对每个人都是可读可写的。这被认为是一种不好的做法。相反，该文件应放在应用程序的资产目录中。

```
webview.loadUrl("file:///" +
Environment.getExternalStorageDirectory().getPath() +
"filename.html");
```

应检查中指定的 URL`loadURL`是否有可操作的动态参数；他们的操作可能会导致包含本地文件。

使用以下[代码片段和最佳实践](https://github.com/nowsecure/secure-mobile-development/blob/master/en/android/webview-best-practices.md#remediation)来停用协议处理程序（如果适用）：

```
//If attackers can inject script into a WebView, they could access local resources. This can be prevented by disabling local file system access, which is enabled by default. You can use the Android WebSettings class to disable local file system access via the public method `setAllowFileAccess`.
webView.getSettings().setAllowFileAccess(false);

webView.getSettings().setAllowFileAccessFromFileURLs(false);

webView.getSettings().setAllowUniversalAccessFromFileURLs(false);

webView.getSettings().setAllowContentAccess(false);
```

- 创建一个列表，定义允许加载的本地和远程网页和协议。
- 创建本地 HTML/JavaScript 文件的校验和，并在应用程序启动时检查它们。缩小 JavaScript 文件以使其更难阅读。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_6)

要确定协议处理程序的使用情况，请寻找在您使用该应用程序时触发电话呼叫的方法以及从文件系统访问文件的方法。

## 确定是否通过 WebView 公开 Java 对象 (MSTG-PLATFORM-7)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#determining-whether-java-objects-are-exposed-through-webviews-mstg-platform-7)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_8)

Android 为在 WebView 中执行的 JavaScript 提供了一种调用和使用 Android 应用程序（注释为`@JavascriptInterface`）的原生功能的[`addJavascriptInterface`](https://developer.android.com/reference/android/webkit/WebView.html#addJavascriptInterface(java.lang.Object, java.lang.String))方法。这称为*WebView JavaScript 桥*或*Native桥*。

请注意，**当您使用 时`addJavascriptInterface`，您是在明确授予该 WebView 中加载的所有页面访问已注册的 JavaScript 接口对象的权限**。这意味着，如果用户在您的应用程序或域之外导航，所有其他外部页面也将可以访问那些 JavaScript 接口对象，如果通过这些接口暴露任何敏感数据，这可能会带来潜在的安全风险。

> 警告：特别注意针对 Android 4.2（API 级别 17）以下 Android 版本的应用程序，因为它们在执行时[容易受到缺陷](https://labs.mwrinfosecurity.com/blog/webview-addjavascriptinterface-remote-code-execution/)`addJavascriptInterface`的攻击：一种滥用反射的攻击，当恶意 JavaScript 注入到网络视图。这是因为默认情况下可以访问所有 Java Object 方法（而不仅仅是那些注释的方法）。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_7)

您需要确定该方法是否`addJavascriptInterface`被使用，如何使用，以及攻击者是否可以注入恶意 JavaScript。

以下示例显示了如何`addJavascriptInterface`在 WebView 中桥接 Java 对象和 JavaScript：

```
WebView webview = new WebView(this);
WebSettings webSettings = webview.getSettings();
webSettings.setJavaScriptEnabled(true);

MSTG_ENV_008_JS_Interface jsInterface = new MSTG_ENV_008_JS_Interface(this);

myWebView.addJavascriptInterface(jsInterface, "Android");
myWebView.loadURL("http://example.com/file.html");
setContentView(myWebView);
```

在 Android 4.2（API 级别 17）及更高版本中，注解`@JavascriptInterface`明确允许 JavaScript 访问 Java 方法。

```
public class MSTG_ENV_008_JS_Interface {

        Context mContext;

        /** Instantiate the interface and set the context */
        MSTG_ENV_005_JS_Interface(Context c) {
            mContext = c;
        }

        @JavascriptInterface
        public String returnString () {
            return "Secret String";
        }

        /** Show a toast from the web page */
        @JavascriptInterface
        public void showToast(String toast) {
            Toast.makeText(mContext, toast, Toast.LENGTH_SHORT).show();
        }
}
```

这是`returnString`从 JavaScript 调用方法的方法，字符串“Secret String”将存储在变量中`result`：

```
var result = window.Android.returnString();
```

通过访问 JavaScript 代码，例如通过存储的 XSS 或 MITM 攻击，攻击者可以直接调用暴露的 Java 方法。

如有`addJavascriptInterface`必要，请考虑以下事项：

- 只应允许 APK 提供的 JavaScript 使用桥接器，例如，通过验证每个桥接 Java 方法上的 URL（通过`WebView.getUrl`）。
- 不应从远程端点加载任何 JavaScript，例如，通过将页面导航保持在应用程序的域内并在默认浏览器（例如 Chrome、Firefox）上打开所有其他域。
- 如果出于遗留原因（例如，必须支持旧设备）有必要，请至少在应用程序的清单文件 ( `<uses-sdk android:minSdkVersion="17" />`) 中将最低 API 级别设置为 17。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_7)

应用程序的动态分析可以向您显示加载了哪些 HTML 或 JavaScript 文件以及存在哪些漏洞。利用该漏洞的过程从生成 JavaScript 负载并将其注入到应用程序请求的文件中开始。如果文件存储在外部存储中，则可以通过 MITM 攻击或直接修改文件来完成注入。整个过程可以通过 Drozer 和 weasel（MWR 的高级利用有效载荷）来完成，它们可以安装完整代理，将有限代理注入正在运行的进程或连接反向 shell 作为远程访问工具 (RAT)。

攻击的完整描述包含在[MWR 的博客文章中](https://labs.mwrinfosecurity.com/blog/webview-addjavascriptinterface-remote-code-execution/)。

## 测试对象持久性 (MSTG-PLATFORM-8)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-object-persistence-mstg-platform-8)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_9)

有几种方法可以在 Android 上持久化一个对象：

#### 对象序列化[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#object-serialization)

对象及其数据可以表示为字节序列。这是在 Java 中通过[对象序列化](https://developer.android.com/reference/java/io/Serializable.html)完成的。序列化本身并不安全。它只是一种二进制格式（或表示形式），用于将数据本地存储在 .ser 文件中。只要密钥安全存储，就可以对 HMAC 序列化数据进行加密和签名。反序列化一个对象需要一个与用于序列化该对象的类版本相同的类。更改类后，`ObjectInputStream`无法从旧的 .ser 文件创建对象。`Serializable`下面的示例显示了如何通过实现`Serializable`接口来创建类。

```
import java.io.Serializable;

public class Person implements Serializable {
  private String firstName;
  private String lastName;

  public Person(String firstName, String lastName) {
    this.firstName = firstName;
    this.lastName = lastName;
    }
  //..
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

#### 可包裹[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#parcelable_1)

当敏感信息通过包含 Parcelable 的 Bundle 存储在 Intent 中时，请确保采取适当的安全措施。使用应用程序级 IPC（例如，签名验证、意图权限、加密）时，使用显式意图并验证适当的附加安全控制。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_8)

有几种执行动态分析的方法：

1. 对于实际的持久性：使用数据存储一章中描述的技术。
2. 对于基于反射的方法：使用 Xposed Hook到反序列化方法或向序列化对象添加不可处理的信息以查看它们是如何处理的（例如，应用程序是否崩溃或可以通过丰富对象来提取额外信息）。

### 测试 WebViews 清理 (MSTG-PLATFORM-10)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webviews-cleanup-mstg-platform-10)

#### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_10)

当应用程序访问 WebView 中的任何敏感数据时，清除 WebView 资源是至关重要的一步。这包括本地存储的任何文件、RAM 缓存和任何加载的 JavaScript。

作为一项附加措施，您可以使用服务器端标头（例如`no-cache`）来防止应用程序缓存特定内容。

> 从 Android 10（API 级别 29）开始，应用程序能够检测 WebView 是否变得[无响应](https://developer.android.com/about/versions/10/features?hl=en#webview-hung)。如果发生这种情况，操作系统将自动调用该`onRenderProcessUnresponsive`方法。

[在Android Developers](https://developer.android.com/training/articles/security-tips?hl=en#WebView)上使用 WebView 时，您可以找到更多安全最佳实践。

#### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_9)

应用程序可以在几个区域删除 WebView 相关数据。您应该检查所有相关的 API 并尝试全面跟踪数据删除。

- **Web 视图 API**：

- **初始化**`setDomStorageEnabled`：应用程序可能会以某种方式初始化 WebView ，以避免使用`setAppCacheEnabled`或`setDatabaseEnabled`from存储某些信息[`android.webkit.WebSettings`](https://developer.android.com/reference/android/webkit/WebSettings)。默认情况下禁用 DOM 存储（用于使用 HTML5 本地存储）、应用程序缓存和数据库存储 API，但应用程序可能会将这些设置明确设置为“true”。

- **缓存**：Android 的 WebView 类提供了[`clearCache`](https://developer.android.com/reference/android/webkit/WebView#clearCache(boolean))可用于清除应用程序使用的所有 WebView 的缓存的方法。它接收一个布尔输入参数 ( `includeDiskFiles`)，它将擦除所有存储的资源，包括 RAM 缓存。但是，如果它设置为 false，它只会清除 RAM 缓存。检查源代码以了解该`clearCache`方法的用法并验证其输入参数。此外，您还可以检查应用程序是否覆盖`onRenderProcessUnresponsive`了 WebView 可能变得无响应的情况，因为该`clearCache`方法也可能从那里调用。

- **WebStorage APIs**：[`WebStorage.deleteAllData`](https://developer.android.com/reference/android/webkit/WebStorage#deleteAllData)也可用于清除当前被 JavaScript 存储 APIs 使用的所有存储，包括 Web SQL 数据库和 HTML5 Web Storage APIs。

  > 一些应用程序*需要*启用 DOM 存储才能显示一些使用本地存储的 HTML5 网站。这应该仔细调查，因为这可能包含敏感数据。

- **Cookies**：可以使用[CookieManager.removeAllCookies](https://developer.android.com/reference/android/webkit/CookieManager#removeAllCookies(android.webkit.ValueCallback))删除任何现有的 cookies 。

- **文件 API**：在某些目录中正确删除数据可能不是那么简单，一些应用程序使用实用的解决方案，即*手动*删除已知保存用户数据的选定目录。这可以使用`java.io.File`API 来完成，例如[`java.io.File.deleteRecursively`](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io/java.io.-file/delete-recursively.html).

**例子：**

这个来自[开源 Firefox Focus](https://github.com/mozilla-mobile/focus-android/blob/v8.17.1/app/src/main/java/org/mozilla/focus/webview/SystemWebView.kt#L220)应用程序的 Kotlin 示例显示了不同的清理步骤：

```
override fun cleanup() {
        clearFormData() // Removes the autocomplete popup from the currently focused form field, if present. Note this only affects the display of the autocomplete popup, it does not remove any saved form data from this WebView's store. To do that, use WebViewDatabase#clearFormData.
        clearHistory()
        clearMatches()
        clearSslPreferences()
        clearCache(true)

        CookieManager.getInstance().removeAllCookies(null)

        WebStorage.getInstance().deleteAllData() // Clears all storage currently being used by the JavaScript storage APIs. This includes the Application Cache, Web SQL Database and the HTML5 Web Storage APIs.

        val webViewDatabase = WebViewDatabase.getInstance(context)
        // It isn't entirely clear how this differs from WebView.clearFormData()
        @Suppress("DEPRECATION")
        webViewDatabase.clearFormData() // Clears any saved data for web forms.
        webViewDatabase.clearHttpAuthUsernamePassword()

        deleteContentFromKnownLocations(context) // calls FileUtils.deleteWebViewDirectory(context) which deletes all content in "app_webview".
    }
```

该函数以一些额外的*手动*文件删除结束，`deleteContentFromKnownLocations`其中从[`FileUtils`](https://github.com/mozilla-mobile/focus-android/blob/v8.17.1/app/src/main/java/org/mozilla/focus/utils/FileUtils.kt). 这些函数使用[`java.io.File.deleteRecursively`](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io/java.io.-file/delete-recursively.html)方法递归地从指定目录中删除文件。

```
private fun deleteContent(directory: File, doNotEraseWhitelist: Set<String> = emptySet()): Boolean {
    val filesToDelete = directory.listFiles()?.filter { !doNotEraseWhitelist.contains(it.name) } ?: return false
    return filesToDelete.all { it.deleteRecursively() }
}
```

#### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_9)

打开访问敏感数据的 WebView，然后注销应用程序。访问应用程序的存储容器并确保删除所有 WebView 相关文件。以下文件和文件夹通常与 WebView 相关：

- app_webview
- 饼干
- pref_store
- blob_storage
- 会话存储
- 网络数据
- 服务工作者

## 覆盖攻击测试 (MSTG-PLATFORM-9)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-overlay-attacks-mstg-platform-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_11)

当恶意应用程序设法将自己置于另一个应用程序之上时，屏幕覆盖攻击就会发生，而另一个应用程序仍然可以正常工作，就好像它在前台一样。恶意应用程序可能会创建模仿外观和感觉的 UI 元素以及原始应用程序甚至 Android 系统 UI。其目的通常是让用户相信他们一直在与合法应用程序交互，然后尝试提升权限（例如，通过授予某些权限）、隐蔽的网络钓鱼、捕获用户点击和击键等。

有多种攻击影响不同的 Android 版本，包括：

- [**Tapjacking**](https://medium.com/devknoxio/what-is-tapjacking-in-android-and-how-to-prevent-it-50140e57bf44)（Android 6.0（API 级别 23）及更低版本）滥用 Android 的屏幕覆盖功能，监听点击并拦截传递给底层活动的任何信息。
- [**Cloak & Dagger**](https://cloak-and-dagger.org/)攻击影响针对 Android 5.0（API 级别 21）到 Android 7.1（API 级别 25）的应用。他们滥用`SYSTEM_ALERT_WINDOW`（“draw on top”）和`BIND_ACCESSIBILITY_SERVICE`（“a11y”）中的一个或两个权限，如果应用程序是从 Play 商店安装的，用户不需要明确授予，甚至不会通知他们.
- [**Toast Overlay**](https://unit42.paloaltonetworks.com/unit42-android-toast-overlay-attack-cloak-and-dagger-with-no-permissions/)与 Cloak & Dagger 非常相似，但不需要用户授予特定的 Android 权限。它在 Android 8.0（API 级别 26）上以 CVE-2017-0752 关闭。

通常，此类攻击是Android系统版本存在某些漏洞或设计问题所固有的。这使得它们具有挑战性，而且通常几乎无法预防，除非应用升级到安全的 Android 版本（API 级别）。

多年来，许多已知的恶意软件（如 MazorBot、BankBot 或 MysteryBot）一直在滥用 Android 的屏幕覆盖功能来攻击关键业务应用程序，即银行业。此[博客](https://www.infosecurity-magazine.com/opinions/overlay-attacks-safeguard-mobile/)讨论了有关此类恶意软件的更多信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_10)

[您可以在Android 开发者文档](https://developer.android.com/reference/android/view/View#security)中找到一些关于 Android View 安全的通用指南，请务必仔细阅读。例如，所谓的*触摸过滤*是针对窃听劫持的常见防御措施，有助于保护用户免受这些漏洞的侵害，通常与我们在本节中介绍的其他技术和注意事项相结合。

要开始静态分析，您可以检查以下方法和属性的源代码（非详尽列表）：

- 重写[`onFilterTouchEventForSecurity`](https://developer.android.com/reference/android/view/View#onFilterTouchEventForSecurity(android.view.MotionEvent))以获得更细粒度的控制并为视图实施自定义安全策略。
- 将布局属性设置[`android:filterTouchesWhenObscured`](https://developer.android.com/reference/android/view/View#attr_android:filterTouchesWhenObscured)为 true 或调用[`setFilterTouchesWhenObscured`](https://developer.android.com/reference/android/view/View.html#setFilterTouchesWhenObscured(boolean)).
- 检查[FLAG_WINDOW_IS_OBSCURED](https://developer.android.com/reference/android/view/MotionEvent.html#FLAG_WINDOW_IS_OBSCURED)（从 API 级别 9 开始）或[FLAG_WINDOW_IS_PARTIALLY_OBSCURED](https://developer.android.com/reference/android/view/MotionEvent.html#FLAG_WINDOW_IS_PARTIALLY_OBSCURED)（从 API 级别 29 开始）。

某些属性可能会影响整个应用程序，而其他属性可能会应用于特定组件。后者就是这种情况，例如，业务需要专门允许覆盖，同时希望保护敏感的输入 UI 元素。开发人员还可以采取额外的预防措施来确认用户的实际意图（这可能是合法的）并将其与潜在的攻击区分开来。

最后一点，请始终记住正确检查应用程序所针对的 API 级别及其含义。例如，[Android 8.0（API 级别 26）](https://developer.android.com/about/versions/oreo/android-8.0-changes#all-aw)对需要`SYSTEM_ALERT_WINDOW`（“在顶部绘制”）的应用程序进行了更改。从这个 API 级别开始，使用的应用程序`TYPE_APPLICATION_OVERLAY`将始终显示在具有其他类型（例如或）[的其他窗口上方](https://developer.android.com/about/versions/oreo/android-8.0-changes#all-aw)。您可以使用此信息来确保至少对于此具体 Android 版本中的此应用程序不会发生覆盖攻击。`TYPE_SYSTEM_OVERLAY``TYPE_SYSTEM_ALERT`

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_10)

以动态方式滥用此类漏洞可能非常具有挑战性且非常专业，因为它与目标 Android 版本密切相关。例如，对于最高至 Android 7.0（API 级别 24）的版本，您可以使用以下 APK 作为概念验证来识别漏洞的存在。

- [Tapjacking POC](https://github.com/FSecureLABS/tapjacking-poc)：此 APK 创建一个位于测试应用程序之上的简单覆盖层。
- [隐形键盘](https://github.com/DEVizzi/Invisible-Keyboard)：此 APK 在键盘上创建多个叠加层以捕获击键。这是 Cloak and Dagger 攻击中展示的漏洞之一。

## 测试强制更新 (MSTG-ARCH-9)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-enforced-updating-mstg-arch-9)

从 Android 5.0（API 级别 21）开始，与 Play Core Library 一起，可以强制更新应用程序。该机制基于使用`AppUpdateManager`. 在此之前，使用了其他机制，例如对 Google Play 商店进行 http 调用，这些机制并不可靠，因为 Play 商店的 API 可能会发生变化。或者，Firebase 也可用于检查可能的强制更新（请参阅此[博客](https://medium.com/@sembozdemir/force-your-users-to-update-your-app-with-using-firebase-33f1e0bcec5a)）。当由于证书/公钥轮换而必须刷新 pin 时，强制更新在涉及公钥固定（有关更多详细信息，请参阅测试网络通信）时非常有用。接下来，漏洞很容易通过强制更新的方式进行修补。

请注意，较新版本的应用程序不会修复存在于应用程序与之通信的后端中的安全问题。允许应用程序不与其通信可能还不够。拥有适当的 API 生命周期管理是这里的关键。同样，当用户没有被迫更新时，不要忘记根据您的 API 测试您应用程序的旧版本和/或使用适当的 API 版本控制。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_11)

下面的代码示例显示了应用程序更新的示例：

```
//Part 1: check for update
// Creates instance of the manager.
AppUpdateManager appUpdateManager = AppUpdateManagerFactory.create(context);

// Returns an intent object that you use to check for an update.
Task<AppUpdateInfo> appUpdateInfo = appUpdateManager.getAppUpdateInfo();

// Checks that the platform will allow the specified type of update.
if (appUpdateInfo.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
      // For a flexible update, use AppUpdateType.FLEXIBLE
      && appUpdateInfo.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)) {



                  //...Part 2: request update
                  appUpdateManager.startUpdateFlowForResult(
                     // Pass the intent that is returned by 'getAppUpdateInfo()'.
                     appUpdateInfo,
                     // Or 'AppUpdateType.FLEXIBLE' for flexible updates.
                     AppUpdateType.IMMEDIATE,
                     // The current activity making the update request.
                     this,
                     // Include a request code to later monitor this update request.
                     MY_REQUEST_CODE);



                     //...Part 3: check if update completed successfully
 @Override
 public void onActivityResult(int requestCode, int resultCode, Intent data) {
   if (myRequestCode == MY_REQUEST_CODE) {
     if (resultCode != RESULT_OK) {
       log("Update flow failed! Result code: " + resultCode);
       // If the update is cancelled or fails,
       // you can request to start the update again in case of forced updates
     }
   }
 }

 //..Part 4:
 // Checks that the update is not stalled during 'onResume()'.
// However, you should execute this check at all entry points into the app.
@Override
protected void onResume() {
  super.onResume();

  appUpdateManager
      .getAppUpdateInfo()
      .addOnSuccessListener(
          appUpdateInfo -> {
            ...
            if (appUpdateInfo.updateAvailability()
                == UpdateAvailability.DEVELOPER_TRIGGERED_UPDATE_IN_PROGRESS) {
                // If an in-app update is already running, resume the update.
                manager.startUpdateFlowForResult(
                    appUpdateInfo,
                    IMMEDIATE,
                    this,
                    MY_REQUEST_CODE);
            }
          });
}
}
```

> 来源：[https ://developer.android.com/guide/app-bundle/in-app-updates](https://developer.android.com/guide/app-bundle/in-app-updates)

在检查正确的更新机制时，请确保`AppUpdateManager`存在 的用法。如果还没有，那么这意味着用户可以继续使用具有给定漏洞的旧版本应用程序。接下来，注意`AppUpdateType.IMMEDIATE`使用：如果有安全更新，那么应该使用这个标志，以确保用户在不更新应用程序的情况下无法继续使用该应用程序。如您所见，在示例的第 3 部分：确保取消或错误最终会在重新检查中结束，并且在关键安全更新的情况下用户无法继续进行。最后，在第 4 部分：您可以看到对于应用程序中的每个入口点，都应该强制执行更新机制，这样绕过它会更难。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_11)

为了测试是否正确更新：尝试下载具有安全漏洞的旧版本应用程序，可以通过开发人员发布的版本或使用第三方应用程序商店。接下来，验证您是否可以在不更新应用程序的情况下继续使用该应用程序。如果给出了更新提示，请通过取消提示或以其他方式通过正常的应用程序使用来规避它来验证您是否仍然可以使用该应用程序。这包括验证后端是否会停止调用易受攻击的后端和/或易受攻击的应用程序版本本身是否被后端阻止。最后，看看您是否可以使用中间人应用程序的版本号，看看后端如何对此做出响应（例如，它是否被记录下来）。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#references)

### Android App Bundle 和更新[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-bundles-and-updates)

- https://developer.android.com/guide/app-bundle/in-app-updates

### Android片段注入[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-fragment-injection)

- https://www.synopsys.com/blogs/software-security/fragment-injection/
- https://securityintelligence.com/wp-content/uploads/2013/12/android-collapses-into-fragments.pdf

### Android权限文档[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-permissions-documentation)

- https://developer.android.com/training/permissions/usage-notes
- https://developer.android.com/training/permissions/requesting#java
- https://developer.android.com/guide/topics/permissions/overview#permission-groups
- https://developer.android.com/guide/topics/manifest/provider-element#gprmsn
- [https://developer.android.com/reference/android/content/Context#revokeUriPermission(android.net.Uri,%20int)](https://developer.android.com/reference/android/content/Context#revokeUriPermission(android.net.Uri, int))
- [https://developer.android.com/reference/android/content/Context#checkUriPermission(android.net.Uri,%20int,%20int,%20int)](https://developer.android.com/reference/android/content/Context#checkUriPermission(android.net.Uri, int, int, int))
- https://developer.android.com/guide/components/broadcasts#restricting_broadcasts_with_permissions
- https://developer.android.com/guide/topics/permissions/overview
- https://developer.android.com/guide/topics/manifest/manifest-intro#filestruct

### Android 捆绑包和即时应用[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-bundles-and-instant-apps)

- https://developer.android.com/topic/google-play-instant/getting-started/instant-enabled-app-bundle
- https://developer.android.com/topic/google-play-instant/guides/multiple-entry-points
- https://developer.android.com/studio/projects/dynamic-delivery

### Android 8 中的 Android 权限更改[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-permissions-changes-in-android-8)

- https://developer.android.com/about/versions/oreo/android-8.0-changes

### Android WebViews 和安全浏览[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-webviews-and-safebrowsing)

- https://developer.android.com/training/articles/security-tips#WebView
- https://developer.android.com/guide/webapps/managing-webview#safe-browsing
- https://developer.android.com/about/versions/oreo/android-8.1#safebrowsing
- https://support.virustotal.com/hc/en-us/articles/115002146549-Mobile-Apps

### Android 自定义 URL 方案[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-custom-url-schemes)

- https://developer.android.com/training/app-links/
- https://developer.android.com/training/app-links/deep-linking
- https://developer.android.com/training/app-links/verify-site-associations
- https://developers.google.com/digital-asset-links/v1/getting-started
- https://pdfs.semanticscholar.org/0415/59c01d5235f8cf38a3c69ccee7e1f1a98067.pdf

### Android应用程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-notifications)

- https://developer.android.com/guide/topics/ui/notifiers/notifications
- https://developer.android.com/training/notify-user/build-notification
- https://developer.android.com/reference/android/service/notification/NotificationListenerService
- https://medium.com/csis-techblog/analysis-of-joker-a-spy-premium-subscription-bot-on-googleplay-9ad24f044451

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#owasp-masvs)

- MSTG-PLATFORM-1：“该应用程序仅请求必要的最少权限集。”
- MSTG-PLATFORM-2：“来自外部来源和用户的所有输入都经过验证，并在必要时进行清理。这包括通过 UI、IPC 机制（如意图、自定义 URL 和网络来源）接收的数据。”
- MSTG-PLATFORM-3：“该应用程序不会通过自定义 URL 方案导出敏感功能，除非这些机制得到适当保护。”
- MSTG-PLATFORM-4：“该应用程序不会通过 IPC 设施导出敏感功能，除非这些机制得到适当保护。”
- MSTG-PLATFORM-5：“除非明确要求，否则 JavaScript 在 WebView 中被禁用。”
- MSTG-PLATFORM-6：“WebViews 配置为仅允许所需的最小协议处理程序集（理想情况下，仅支持 https）。禁用潜在危险的处理程序，例如文件、电话和应用程序 ID。”
- MSTG-PLATFORM-7：“如果应用程序的Native方法暴露给 WebView，请验证 WebView 仅呈现应用程序包中包含的 JavaScript。”
- MSTG-PLATFORM-8：“对象序列化（如果有的话）是使用安全序列化 API 实现的。”
- MSTG-PLATFORM-10：“在销毁 WebView 之前，应清除 WebView 的缓存、存储和加载的资源（JavaScript 等）。”
- MSTG-ARCH-9：“存在强制更新移动应用程序的机制。”
