# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 2 · part 1

> 分段 1/2。索引见 `Android平台API-p2.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 2

> 分段 2/8。索引见 `Android平台API.md`。

## 承接

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

