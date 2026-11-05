# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 5 · part 2

> 分段 2/2。索引见 `Android平台API-p5.md`。

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
