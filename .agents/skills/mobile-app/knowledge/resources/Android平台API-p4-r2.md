# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 4 · part 2

> 分段 2/2。索引见 `Android平台API-p4.md`。

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
