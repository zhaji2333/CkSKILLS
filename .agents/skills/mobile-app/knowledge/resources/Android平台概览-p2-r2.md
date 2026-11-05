# Android平台概览[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#android-platform-overview) · part 2 · part 2

> 分段 2/2。索引见 `Android平台概览-p2.md`。

            <action android:name="com.owasp.myapplication.myaction" />
        </intent-filter>
    </receiver>

    <application
        android:icon="@drawable/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.Material.Light" >
        <activity
            android:name="com.owasp.myapplication.MainActivity" >
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

可用清单选项的完整列表在官方[Android 清单文件文档](https://developer.android.com/guide/topics/manifest/manifest-intro.html)中。

### 应用组件(App Components¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#app-components)

Android 应用程序由多个高级组件组成。主要组成部分是：

- Activities
- Fragments
- Intents
- Broadcast receivers
- Content providers and services

所有这些元素均由 Android 操作系统以可通过 API 提供的预定义类的形式提供。

#### 活动(Activities)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#activities)

活动构成了任何应用程序的可见部分。每个屏幕有一个 Activity，因此具有三个不同屏幕的应用会实现三个不同的 Activity。活动通过扩展 Activity 类来声明。它们包含所有用户界面元素：片段、视图和布局。

每个活动都需要使用以下语法在 Android Manifest 中声明：

```
<activity android:name="ActivityName">
</activity>
```

无法显示未在清单中声明的活动，尝试启动它们将引发异常。

像应用程序一样，活动有自己的生命周期，需要监控系统变化来处理它们。活动可以处于以下状态：活动、暂停、停止和非活动。这些状态由 Android 操作系统管理。因此，活动可以实现以下事件管理器：

- 创建时
- onSaveInstanceState
- 启动时
- 恢复时
- onRestoreInstanceState
- 暂停
- 停止
- 重新启动
- 销毁时

- onCreate
- onSaveInstanceState
- onStart
- onResume
- onRestoreInstanceState
- onPause
- onStop
- onRestart
- onDestroy

应用程序可能不会显式实现所有事件管理器，在这种情况下会采取默认操作。通常，至少`onCreate`管理器会被应用程序开发人员覆盖。大多数用户界面组件都是这样声明和初始化的。`onDestroy`当必须显式释放资源（如网络连接或数据库连接）或应用程序关闭时必须执行特定操作时，可能会被覆盖。

#### 碎片(Fragments¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#fragments)

片段表示活动中的行为或用户界面的一部分。Fragments 是在 Android 版本 Honeycomb 3.0（API 级别 11）中引入的。

片段旨在封装界面的各个部分，以促进可重用性和适应不同的屏幕尺寸。片段是自治实体，因为它们包含所有必需的组件（它们有自己的布局、按钮等）。但是，它们必须与活动集成在一起才能发挥作用：片段不能单独存在。它们有自己的生命周期，与实现它们的活动的生命周期相关联。

因为片段有自己的生命周期，所以片段类包含可以重新定义和扩展的事件管理器。这些事件管理器包括 onAttach、onCreate、onStart、onDestroy 和 onDetach。其他几个存在；读者应参考[Android Fragment 规范](https://developer.android.com/guide/components/fragments)了解更多详细信息。

Fragments可以通过扩展Android提供的Fragment类来轻松实现：

Java 中的示例：

```
public class MyFragment extends Fragment {
    ...
}
```

Kotlin 中的示例：

```
class MyFragment : Fragment() {
    ...
}
```

片段不需要在清单文件中声明，因为它们依赖于活动。

要管理其片段，活动可以使用片段管理器（FragmentManager 类）。此类使查找、添加、删除和替换关联片段变得容易。

可以通过以下方式创建片段管理器：

Java 中的示例：

```
FragmentManager fm = getFragmentManager();
```

Kotlin 中的示例：

```
var fm = fragmentManager
```

片段不一定有用户界面；它们可以是管理与应用程序用户界面相关的后台操作的一种方便有效的方式。一个片段可以被声明为持久的，这样即使它的 Activity 被销毁，系统也会保留它的状态。

#### Content Provider(内容提供者)(Content Providers¶)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#content-providers)

Android 使用 SQLite 永久存储数据：与 Linux 一样，数据存储在文件中。SQLite 是一种轻量、高效、开源的关系数据存储技术，不需要太多的处理能力，这使得它非常适合移动使用。具有特定类（Cursor、ContentValues、SQLiteOpenHelper、ContentProvider、ContentResolver 等）的完整 API 可用。SQLite 不作为单独的进程运行；它是应用程序的一部分。默认情况下，属于给定应用程序的数据库只能由该应用程序访问。然而，Content Provider(内容提供者)提供了一个很好的抽象数据源的机制（包括数据库和平面文件）；它们还提供了一种标准且高效的机制来在应用程序（包括Native应用程序）之间共享数据。为了让其他应用程序可以访问，Content Provider(内容提供者)需要在将共享它的应用程序的清单文件中明确声明。只要未声明Content Provider(内容提供者)，它们就不会被导出，只能由创建它们的应用程序调用。

Content Provider(内容提供者)是通过 URI 寻址方案实现的：它们都使用 content:// 模型。无论源的类型如何（SQLite 数据库、平面文件等），寻址方案总是相同的，从而将源抽象化并为开发人员提供独特的方案。Content Provider(内容提供者)提供所有常规数据库操作：创建、读取、更新、删除。这意味着任何在其清单文件中拥有适当权限的应用程序都可以操纵来自其他应用程序的数据。

#### 服务(Services)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#services)

服务是在后台执行任务（数据处理、启动意图和通知等）而不显示用户界面的 Android 操作系统组件（基于 Service 类）。服务旨在长期运行流程。它们的系统优先级低于活动应用程序的系统优先级，高于非活动应用程序的系统优先级。因此，它们不太可能在系统需要资源时被杀死，并且可以将它们配置为在有足够的资源可用时自动重启。这使得服务成为运行后台任务的理想选择。请注意，服务，如活动，在主应用程序线程中执行。服务不会创建自己的线程，也不会在单独的进程中运行，除非您另有指定。

### 进程间通信(Inter-Process Communication)[¶](https://mas.owasp.org/MASTG/Android/0x05a-Platform-Overview/#inter-process-communication)

正如我们已经了解到的，每个 Android 进程都有自己的沙盒地址空间。进程间通信设施允许应用程序安全地交换信号和数据。Android 的 IPC 不是依赖于默认的 Linux IPC 工具，而是基于 Binder，这是 OpenBinder 的自定义实现。大多数 Android 系统服务和所有高级 IPC 服务都依赖于 Binder。

术语*Binder*代表许多不同的事物，包括：

- Binder Driver：内核级驱动
- Binder 协议：用于与 Binder 驱动程序通信的低级基于 ioctl 的协议
- IBinder 接口：Binder 对象实现的定义明确的行为
- Binder对象：IBinder接口的通用实现
- Binder服务：Binder对象的实现；例如，位置服务和传感器服务
- Binder客户端：使用Binder服务的对象

Binder 框架包括一个客户端-服务器通信模型。要使用 IPC，应用程序会调用代理对象中的 IPC 方法。代理对象透明地将调用参数*编组*到一个*包裹*中，并将事务发送到作为字符驱动程序 (/dev/binder) 实现的 Binder 服务器。服务器拥有一个线程池，用于处理传入的请求并将消息传递到目标对象。从客户端应用程序的角度来看，所有这些似乎都是常规方法调用，所有繁重的工作都由 Binder 框架完成。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05a/binder.jpg)

- *Binder 概述 - 图片来源：[Thorsten Schreiber 的 Android Binder](https://1library.net/document/z33dd47z-android-android-interprocess-communication-thorsten-schreiber-somorovsky-bussmeyer.html)*

允许其他应用程序绑定到它们的服务称为*绑定服务*。这些服务必须向客户端提供 IBinder 接口。开发人员使用 Android 接口描述语言 (AIDL) 为远程服务编写接口。

ServiceManager 是一个系统守护进程，负责管理系统服务的注册和查找。它为所有已注册的服务维护一个名称/绑定器对列表。`addService`使用以下静态`getService`方法按名称添加和检索服务`android.os.ServiceManager`：

Java 中的示例：

```
public static IBinder getService(String name) {
        try {
            IBinder service = sCache.get(name);
            if (service != null) {
                return service;
            } else {
                return getIServiceManager().getService(name);
