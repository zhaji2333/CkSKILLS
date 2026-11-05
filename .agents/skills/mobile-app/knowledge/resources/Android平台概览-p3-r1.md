# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 3 · part 1

> 分段 1/2。索引见 `Android平台概览-p3.md`。

# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 3

> 分段 3/4。索引见 `Android平台概览.md`。

## 承接

            }
        } catch (RemoteException e) {
            Log.e(TAG, "error in getService", e);
        }
        return null;
    }
```

Kotlin 中的示例：

```
companion object {
        private val sCache: Map<String, IBinder> = ArrayMap()
        fun getService(name: String): IBinder? {
            try {
                val service = sCache[name]
                return service ?: getIServiceManager().getService(name)
            } catch (e: RemoteException) {
                Log.e(FragmentActivity.TAG, "error in getService", e)
            }
            return null
        }
    }
```

您可以使用`service list`命令查询系统服务列表。

```
$ adb shell service list
Found 99 services:
0 carrier_config: [com.android.internal.telephony.ICarrierConfigLoader]
1 phone: [com.android.internal.telephony.ITelephony]
2 isms: [com.android.internal.telephony.ISms]
3 iphonesubinfo: [com.android.internal.telephony.IPhoneSubInfo]
```

#### 意图(Intents)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#intents)

*Intent 消息传递*是构建在 Binder 之上的异步通信框架。该框架允许点对点和发布-订阅消息传递。*Intent*是一个消息传递对象，可用于从另一个应用程序组件请求操作。尽管意图以多种方式促进组件间通信，但有三个基本用例：

- 开始一项活动
- 一个活动代表应用程序中的单个屏幕。您可以通过将意图传递给 来启动活动的新实例`startActivity`。意图描述活动并携带必要的数据。
- 启动服务
- 服务是在后台执行操作的组件，没有用户界面。在 Android 5.0（API 级别 21）及更高版本中，您可以使用 JobScheduler 启动服务。
- 进行广播
- 广播是任何应用程序都可以接收的消息。系统为系统事件发送广播，包括系统启动和充电初始化。您可以通过将意图传递给`sendBroadcast`或来向其他应用程序发送广播`sendOrderedBroadcast`。

有两种类型的意图。显式意图命名将要启动的组件（完全限定的类名）。例如：

Java 中的示例：

```
Intent intent = new Intent(this, myActivity.myClass);
```

Kotlin 中的示例：

```
var intent = Intent(this, myActivity.myClass)
```

隐式意图被发送到操作系统以对给定的数据集执行给定的操作（我们下面示例中的 OWASP 网站的 URL）。由系统决定哪个应用程序或类将执行相应的服务。例如：

Java 中的示例：

```
Intent intent = new Intent(Intent.MY_ACTION, Uri.parse("https://www.owasp.org"));
```

Kotlin 中的示例：

```
var intent = Intent(Intent.MY_ACTION, Uri.parse("https://www.owasp.org"))
```

*Intent 过滤器*是 Android Manifest 文件中的一个表达式，它指定组件想要接收的 Intent 类型。例如，通过为 Activity 声明一个 Intent 过滤器，您可以让其他应用程序以某种 Intent 直接启动您的 Activity。同样，如果您没有为它声明任何意图过滤器，则您的活动只能以明确的意图开始。

Android 使用 Intent 向应用程序广播消息（例如来电或短信）、重要的电源信息（例如电池电量不足）和网络变化（例如连接丢失）。可以将额外数据添加到意图（通过`putExtra`/ `getExtras`）。

这是操作系统发送的意图的简短列表。所有常量都在 Intent 类中定义，整个列表在官方 Android 文档中：

- ACTION_CAMERA_BUTTON 按钮
- ACTION_MEDIA_EJECT
- ACTION_NEW_OUTGOING_CALL
- ACTION_TIMEZONE_CHANGED

为了提高安全性和隐私性，本地广播管理器用于在应用程序内发送和接收意图，而无需将它们发送到操作系统的其余部分。这对于确保敏感和私有数据不会离开应用边界（例如地理位置数据）非常有用。

#### 广播接收器(Broadcast Receivers)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#broadcast-receivers)

广播接收器是允许应用程序从其他应用程序和系统本身接收通知的组件。有了它们，应用程序可以对事件（内部的、由其他应用程序发起的或由操作系统发起的）做出反应。它们通常用于更新用户界面、启动服务、更新内容和创建用户通知。

有两种方法可以让系统知道广播接收器。一种方法是在 Android Manifest 文件中声明它。清单应指定广播接收器和意图过滤器之间的关联，以指示接收器要侦听的操作。

清单中带有意图过滤器的广播接收器声明示例：

```
<receiver android:name=".MyReceiver" >
    <intent-filter>
        <action android:name="com.owasp.myapplication.MY_ACTION" />
    </intent-filter>
</receiver>
```

请注意，在此示例中，广播接收器不包含该[`android:exported`](https://developer.android.com/guide/topics/manifest/receiver-element)属性。由于至少定义了一个过滤器，因此默认值将设置为“true”。在没有任何过滤器的情况下，它将被设置为“false”。

另一种方法是在代码中动态创建接收器。然后接收方可以使用该方法进行注册[`Context.registerReceiver`](https://developer.android.com/reference/android/content/Context.html#registerReceiver(android.content.BroadcastReceiver,%20android.content.IntentFilter))。

动态注册广播接收器的示例：

Java 中的示例：

```
// Define a broadcast receiver
BroadcastReceiver myReceiver = new BroadcastReceiver() {
    @Override
    public void onReceive(Context context, Intent intent) {
        Log.d(TAG, "Intent received by myReceiver");
    }
};
// Define an intent filter with actions that the broadcast receiver listens for
IntentFilter intentFilter = new IntentFilter();
intentFilter.addAction("com.owasp.myapplication.MY_ACTION");
// To register the broadcast receiver
registerReceiver(myReceiver, intentFilter);
// To un-register the broadcast receiver
unregisterReceiver(myReceiver);
```

Kotlin 中的示例：

```
// Define a broadcast receiver
val myReceiver: BroadcastReceiver = object : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        Log.d(FragmentActivity.TAG, "Intent received by myReceiver")
    }
}
// Define an intent filter with actions that the broadcast receiver listens for
val intentFilter = IntentFilter()
intentFilter.addAction("com.owasp.myapplication.MY_ACTION")
// To register the broadcast receiver
registerReceiver(myReceiver, intentFilter)
// To un-register the broadcast receiver
unregisterReceiver(myReceiver)
```

请注意，当引发相关意图时，系统会自动启动带有已注册接收器的应用程序。

根据[Broadcasts Overview](https://developer.android.com/guide/components/broadcasts)，如果广播不专门针对应用程序，则广播被视为“隐式”。收到隐式广播后，Android 将列出所有已在其过滤器中注册给定操作的应用程序。如果有多个应用程序注册了同一操作，Android 将提示用户从可用应用程序列表中进行选择。

Broadcast Receiver 的一个有趣特性是它们可以被优先化；这样，一个意图将根据他们的优先级传递给所有授权的接收者。`android:priority`可以通过属性以及通过方法以编程方式将优先级分配给清单中的意图过滤器[`IntentFilter.setPriority`](https://developer.android.com/reference/android/content/IntentFilter#setPriority(int))。但是，请注意具有相同优先级的接收器将以[任意顺序运行](https://developer.android.com/guide/components/broadcasts.html#sending-broadcasts)。

如果您的应用不应跨应用发送广播，请使用本地广播管理器 ( [`LocalBroadcastManager`](https://developer.android.com/reference/androidx/localbroadcastmanager/content/LocalBroadcastManager.html))。它们可用于确保仅从内部应用程序接收意图，并且将丢弃来自任何其他应用程序的任何意图。这对于提高应用程序的安全性和效率非常有用，因为不涉及进程间通信。但是，请注意`LocalBroadcastManager`该类已被[弃用](https://developer.android.com/reference/androidx/localbroadcastmanager/content/LocalBroadcastManager.html)，Google 建议使用替代方法，例如[`LiveData`](https://developer.android.com/reference/androidx/lifecycle/LiveData.html).

有关广播接收器的更多安全注意事项，请参阅[安全注意事项和最佳实践](https://developer.android.com/guide/components/broadcasts.html#security-and-best-practices)。

#### 隐式广播接收器限制[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#implicit-broadcast-receiver-limitation)

根据[Background Optimizations](https://developer.android.com/topic/performance/background-optimization)，针对 Android 7.0（API 级别 24）或更高版本的应用程序不再接收`CONNECTIVITY_ACTION`广播，除非他们向`Context.registerReceiver()`. 系统也不发送`ACTION_NEW_PICTURE`和`ACTION_NEW_VIDEO`广播。

根据[Background Execution Limits ，针对 Android 8.0（API 级别 26）或更高版本的应用程序不能再在其清单中为隐式广播注册广播接收器，隐](https://developer.android.com/about/versions/oreo/background.html#broadcasts)[式广播异常](https://developer.android.com/guide/components/broadcast-exceptions)中列出的除外。在Runtime(运行时)通过调用创建的广播接收器`Context.registerReceiver`不受此限制的影响。

根据[Changes to System Broadcasts](https://developer.android.com/guide/components/broadcasts#changes-system-broadcasts)，从 Android 9（API 级别 28）开始，`NETWORK_STATE_CHANGED_ACTION`广播不会接收有关用户位置或个人身份数据的信息。

## Android应用发布[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-application-publishing)

应用程序开发成功后，下一步就是发布并与他人共享。然而，应用程序不能简单地添加到商店并共享，它们必须先被签名。加密签名用作应用程序开发人员放置的可验证标记。它识别应用程序的作者，并确保应用程序自最初分发以来未被修改。

### 签名流程(Signing Process)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#signing-process)

