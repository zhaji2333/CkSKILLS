# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 8 · part 1

> 分段 1/2。索引见 `Android平台API-p8.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 8

> 分段 8/8。索引见 `Android平台API.md`。

## 承接

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

