# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 1 · part 1

> 分段 1/2。索引见 `Android平台API-p1.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 1

> 分段 1/8。索引见 `Android平台API.md`。

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

