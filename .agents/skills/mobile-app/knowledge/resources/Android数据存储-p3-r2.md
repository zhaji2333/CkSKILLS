# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 3 · part 2

> 分段 2/2。索引见 `Android数据存储-p3.md`。

ProGuard 保证移除`Log.v`方法调用。是否删除其余代码 ( `new StringBuilder ...`) 取决于代码的复杂性和[ProGuard 版本](https://stackoverflow.com/questions/6009078/removing-unused-strings-during-proguard-optimisation)。

这是一个安全风险，因为（未使用的）字符串将纯文本数据泄漏到内存中，可以通过调试器或内存转储访问内存。

不幸的是，这个问题不存在灵丹妙药，但一个选择是实现一个自定义日志记录工具，它采用简单的参数并在内部构造日志语句。

```
SecureLog.v("Private key [byte format]: ", key);
```

然后配置 ProGuard 以剥离其调用。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_1)

至少使用所有移动应用程序功能一次，然后识别应用程序的数据目录并查找日志文件 ( `/data/data/<package-name>`)。查看应用日志，判断是否产生了日志数据；一些移动应用程序创建自己的日志并将其存储在数据目录中。

许多应用程序开发人员仍然使用`System.out.println`or`printStackTrace`代替适当的日志记录类。因此，您的测试策略必须包括应用程序启动、运行和关闭时生成的所有输出。`System.out.println`要确定or直接打印了哪些数据`printStackTrace`，您可以[`Logcat`](https://developer.android.com/tools/debugging/debugging-log.html)按照“基本安全测试”一章“监控系统日志”一节中的说明使用。

请记住，您可以通过过滤 Logcat 输出来定位特定应用程序，如下所示：

```
adb logcat | grep "$(adb shell ps | grep <package-name> | awk '{print $2}')"
```

> 如果您已经知道应用程序的 PID，您可以直接使用`--pid`标志给它。

如果您希望某些字符串或模式出现在日志中，您可能还想应用更多过滤器或正则表达式（例如使用`logcat`的正则表达式标志）。`-e <expr>, --regex=<expr>`

## 确定敏感数据是否与第三方共享 (MSTG-STORAGE-4)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#determining-whether-sensitive-data-is-shared-with-third-parties-mstg-storage-4)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_3)

敏感信息可能通过多种方式泄露给第三方，包括但不限于以下方式：

### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app)

这些服务提供的功能可能涉及跟踪服务以监控用户在使用应用程序时的行为、销售横幅广告或改善用户体验。

缺点是开发人员通常不知道通过第三方库执行的代码的细节。因此，不应向服务发送超过必要的信息，也不应泄露敏感信息。

大多数第三方服务以两种方式实现：

- 有一个独立的库
- 使用完整的 SDK

### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications)

重要的是要了解[通知](https://developer.android.com/guide/topics/ui/notifiers/notifications)永远不应被视为私人的。当 Android 系统处理通知时，它会在系统范围内广播，并且任何使用[NotificationListenerService](https://developer.android.com/reference/kotlin/android/service/notification/NotificationListenerService)运行的应用程序都可以侦听这些通知以完整接收它们，并可以根据需要进行处理。

有许多已知的恶意软件样本，例如[Joker](https://research.checkpoint.com/2020/new-joker-variant-hits-google-play-with-an-old-trick/)和[Alien](https://www.threatfabric.com/blogs/alien_the_story_of_cerberus_demise.html)，它们滥用`NotificationListenerService`监听设备上的通知，然后将它们发送到攻击者控制的 C2 基础设施。通常这样做是为了侦听双因素身份验证 (2FA) 代码，这些代码在设备上显示为通知，然后发送给攻击者。对用户来说更安全的替代方法是使用不生成通知的 2FA 应用程序。

此外，Google Play 商店中有许多提供通知日志记录的应用程序，这些应用程序基本上在本地记录 Android 系统上的任何通知。这突出表明，通知在 Android 上绝不是私有的，设备上的任何其他应用程序都可以访问。

出于这个原因，应检查所有通知使用情况，以查找可能被恶意应用程序使用的机密或高风险信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_3)

#### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app_1)

要确定第三方库提供的 API 调用和函数是否根据最佳实践使用，请查看其源代码、请求的权限并检查是否存在任何已知漏洞（请参阅[“检查第三方库中的弱点 (MSTG-CODE-5) ）”](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#checking-for-weaknesses-in-third-party-libraries-mstg-code-5)）。

发送到第三方服务的所有数据都应匿名，以防止泄露 PII（个人身份信息），从而允许第三方识别用户帐户。不应将其他数据（例如可以映射到用户帐户或会话的 ID）发送给第三方。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_1)

搜索`NotificationManager`可能指示某种形式的通知管理的类的任何用法。如果正在使用该类，下一步将是了解应用程序如何[生成通知](https://developer.android.com/training/notify-user/build-notification#SimpleNotification)以及最终显示哪些数据。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_2)

#### App内嵌的第三方服务[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#third-party-services-embedded-in-the-app_2)

检查对外部服务的所有请求以获取嵌入的敏感信息。[要拦截客户端和服务器之间的流量，您可以通过使用Burp Suite](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#burp-suite) Professional 或[OWASP ZAP](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#owasp-zap)发起中间人 (MITM) 攻击来执行动态分析。通过拦截代理路由流量后，您可以尝试嗅探在应用程序和服务器之间传递的流量。应检查所有未直接发送到托管主要功能的服务器的应用程序请求是否包含敏感信息，例如跟踪器或广告服务中的 PII。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_2)

运行应用程序并开始跟踪对与通知创建相关的函数的所有调用，例如`setContentTitle`或`setContentText`from [`NotificationCompat.Builder`](https://developer.android.com/reference/androidx/core/app/NotificationCompat.Builder)。最后观察跟踪并评估它是否包含其他应用程序可能窃听的任何敏感信息。

## 确定是否为文本输入字段禁用键盘缓存（MSTG-STORAGE-5）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#determining-whether-the-keyboard-cache-is-disabled-for-text-input-fields-mstg-storage-5)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_4)

当用户在输入字段中键入时，软件会自动建议数据。此功能对于消息传递应用程序非常有用。但是，当用户选择包含此类信息的输入字段时，键盘缓存可能会泄露敏感信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_4)

在活动的布局定义中，您可以定义`TextViews`具有 XML 属性的活动。如果 XML 属性`android:inputType`的值为`textNoSuggestions`，则在选择输入字段时不会显示键盘缓存。用户将不得不手动输入所有内容。

```
   <EditText
        android:id="@+id/KeyBoardCache"
        android:inputType="textNoSuggestions" />
```

所有包含敏感信息的输入字段的代码都应包含此 XML 属性以[禁用键盘建议](https://developer.android.com/reference/android/text/InputType.html#TYPE_TEXT_FLAG_NO_SUGGESTIONS)。

或者，开发人员可以使用以下常量：

| XML`android:inputType`                                       | 代码`InputType`                                              | API级别 |
