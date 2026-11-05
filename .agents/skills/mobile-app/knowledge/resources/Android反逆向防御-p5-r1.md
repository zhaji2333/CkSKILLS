# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 5 · part 1

> 分段 1/2。索引见 `Android反逆向防御-p5.md`。

# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 5

> 分段 5/5。索引见 `Android反逆向防御.md`。

## 承接

                  KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                  .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                  .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                  .build());
  SecretKey key = keyGenerator.generateKey();
  
  // The key can also be obtained from the Android Keystore any time as follows:
  KeyStore keyStore = KeyStore.getInstance("AndroidKeyStore");
  keyStore.load(null);
  key = (SecretKey) keyStore.getKey("key2", null);
  ```

- 通过 AES-GCM 密码使用密钥对应用程序存储的身份验证数据和其他敏感数据进行加密，并使用实例 ID 等设备特定参数作为关联数据：

  ```
  Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
  final byte[] nonce = new byte[GCM_NONCE_LENGTH];
  random.nextBytes(nonce);
  GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, nonce);
  cipher.init(Cipher.ENCRYPT_MODE, key, spec);
  byte[] aad = "<deviceidentifierhere>".getBytes();;
  cipher.updateAAD(aad);
  cipher.init(Cipher.ENCRYPT_MODE, key);
  
  //use the cipher to encrypt the authentication data see 0x50e for more details.
  ```

- 使用存储在 Android Keystore 中的公钥对密钥进行加密，并将加密后的密钥存储在应用程序的私有存储中。

- 每当需要访问令牌等身份验证数据或其他敏感数据时，使用存储在 Android Keystore 中的私钥解密密钥，然后使用解密的密钥解密密文。

- 使用基于令牌的设备身份验证（实例 ID）确保使用相同的应用程序实例。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#static-analysis_1)

过去，Android 开发人员通常依赖于`Settings.Secure.ANDROID_ID`(SSAID) 和 MAC 地址。这[随着 Android 8.0（API 级别 26）的发布而改变](https://android-developers.googleblog.com/2017/04/changes-to-device-identifiers-in.html)。由于 MAC 地址现在经常在未连接到接入点时随机化，并且 SSAID 不再是设备绑定 ID。相反，它成为绑定到用户、设备和请求 SSAID 的应用程序的应用程序签名密钥的值。此外，Google 的 SDK 文档中还有[关于标识符的新建议。](https://developer.android.com/training/articles/user-data-ids.html)基本上，谷歌建议：

- 在广告方面使用广告 ID ( `AdvertisingIdClient.Info`)，以便用户可以选择拒绝。
- 使用实例 ID ( `FirebaseInstanceId`) 进行设备识别。
- 仅将 SSAID 用于欺诈检测和由同一开发人员签名的应用程序之间共享状态。

请注意，实例 ID 和广告 ID 在设备升级和设备重置过程中并不稳定。但是，实例 ID 至少可以识别设备上当前安装的软件。

当源代码可用时，您可以查找一些关键术语：

- 不再有效的唯一标识符：
- `Build.SERIAL`没有`Build.getSerial`
- `htc.camera.sensor.front_SN`适用于 HTC 设备
- `persist.service.bdroid.bdadd`
- `Settings.Secure.bluetooth_address`或`WifiInfo.getMacAddress`from ，除非在清单中启用`WifiManager`了系统权限。`LOCAL_MAC_ADDRESS`
- `ANDROID_ID`仅用作标识符。随着时间的推移，这将影响旧设备的绑定质量。
- 缺少实例 ID、`Build.SERIAL`和 IMEI。

```
  TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
  String IMEI = tm.getDeviceId();
```

- `AndroidKeyStore`在使用`KeyPairGeneratorSpec`或`KeyGenParameterSpec`API中创建私钥。

为确保可以使用标识符，请检查`AndroidManifest.xml`IMEI 和`Build.Serial`. 该文件应包含权限`<uses-permission android:name="android.permission.READ_PHONE_STATE" />`。

> 适用于 Android 8.0（API 级别 26）的应用在请求时将获得“未知”结果`Build.Serial`。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis_1)

有几种方法可以测试应用程序绑定：

#### 使用仿真器进行动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis-with-an-emulator)

1. 在模拟器上运行应用程序。
2. 确保您可以提高对应用程序实例的信任（例如，在应用程序中进行身份验证）。
3. 按照以下步骤从模拟器中检索数据：
4. 通过 ADB shell 通过 SSH 连接到您的模拟器。
5. 执行`run-as <your app-id>`。您的应用程序 ID 是 AndroidManifest.xml 中描述的包。
6. `chmod 777`缓存和Shared Preferences的内容。
7. 从 app-id 退出当前用户。
8. `/data/data/<your appid>/cache`将和的内容复制`shared-preferences`到 SD 卡。
9. 使用 ADB 或 DDMS 来拉取内容。
10. 在另一个模拟器上安装应用程序。
11. 在应用程序的数据文件夹中，覆盖第 3 步中的数据。
12. 将步骤 3 中的数据复制到第二个模拟器的 SD 卡。
13. 通过 ADB shell 通过 SSH 连接到您的模拟器。
14. 执行`run-as <your app-id>`。您的 app-id 是 中描述的包 `AndroidManifest.xml`。
15. `chmod 777`文件夹的缓存和Shared Preferences。
16. 复制 SD 卡的旧内容`to /data/data/<your appid>/cache`和`shared-preferences`.
17. 你能继续处于认证状态吗？如果是这样，绑定可能无法正常工作。

#### 谷歌实例 ID[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#google-instance-id)

[Google 实例 ID](https://developers.google.com/instance-id/)使用令牌来验证正在运行的应用程序实例。当应用程序被重置、卸载等时，实例 ID 会被重置，这意味着您将拥有一个新的应用程序“实例”。为实例 ID 执行以下步骤：

1. 在您的 Google Developer Console 中为给定的应用程序配置您的实例 ID。这包括管理 PROJECT_ID。

2. 设置 Google Play 服务。在文件`build.gradle`中，添加

   ```
   apply plugin: 'com.android.application'
       ...
   
       dependencies {
           compile 'com.google.android.gms:play-services-gcm:10.2.4'
       }
   ```

3. 获取实例 ID。

   ```
   String iid = Instance ID.getInstance(context).getId();
   //now submit this iid to your server.
   ```

4. 生成令牌。

   ```
   String authorizedEntity = PROJECT_ID; // Project id from Google Developer Console
   String scope = "GCM"; // e.g. communicating using GCM, but you can use any
                       // URL-safe characters up to a maximum of 1000, or
                       // you can also leave it blank.
   String token = Instance ID.getInstance(context).getToken(authorizedEntity,scope);
   //now submit this token to the server.
   ```

5. 确保您可以处理来自实例 ID 的回调，以防出现无效设备信息、安全问题等。这需要扩展`Instance IDListenerService`和处理那里的回调：

   ```
   public class MyInstance IDService extends Instance IDListenerService {
   public void onTokenRefresh() {
       refreshAllTokens();
   }
   
   private void refreshAllTokens() {
       // assuming you have defined TokenList as
       // some generalized store for your tokens for the different scopes.
       // Please note that for application validation having just one token with one scopes can be enough.
       ArrayList<TokenList> tokenList = TokensList.get();
       Instance ID iid = Instance ID.getInstance(this);
       for(tokenItem : tokenList) {
       tokenItem.token =
           iid.getToken(tokenItem.authorizedEntity,tokenItem.scope,tokenItem.options);
       // send this tokenItem.token to your server
       }
   }
   };
   ```

6. 在您的 Android 清单中注册该服务：

   ```
   <service android:name=".MyInstance IDService" android:exported="false">
   <intent-filter>
           <action android:name="com.google.android.gms.iid.Instance ID" />
   </intent-filter>
   </service>
   ```

当您将实例 ID (iid) 和令牌提交到您的服务器时，您可以将该服务器与实例 ID 云服务一起使用来验证令牌和 iid。当 iid 或令牌似乎无效时，您可以触发保护程序（例如，通知服务器可能存在复制或安全问题或从应用程序中删除数据并要求重新注册）。

请注意，[Firebase 还支持实例 ID](https://firebase.google.com/docs/reference/android/com/google/firebase/iid/FirebaseInstanceId)。

#### IMEI 和序列号[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#imei-serial)

Google 建议不要使用这些标识符，除非应用程序存在高风险。

对于Android 8.0（API level 26）之前的Android设备，可以通过如下方式请求串口：

```
   String serial = android.os.Build.SERIAL;
```

对于运行 Android 版本 O 及更高版本的设备，您可以通过以下方式请求设备的序列号：

1. 在您的 Android 清单中设置权限：

   ```
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
   ```

2. 在Runtime(运行时)向用户请求权限：有关详细信息，请参阅[https://developer.android.com/training/permissions/requesting.html 。](https://developer.android.com/training/permissions/requesting.html)

3. 获取序列号：

   ```
   String serial = android.os.Build.getSerial();
   ```

检索 IMEI：

1. 在您的 Android 清单中设置所需的权限：

   ```
   <uses-permission android:name="android.permission.READ_PHONE_STATE" />
   ```

2. 如果您使用的是 Android 版本 Android 6（API 级别 23）或更高版本，请在Runtime(运行时)向用户请求权限：有关更多详细信息，请参阅https://developer.android.com/training/permissions/requesting.html。

3. 获取 IMEI：

   ```
   TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
   String IMEI = tm.getDeviceId();
   ```

#### SSAID[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#ssaid)

Google 建议不要使用这些标识符，除非应用程序存在高风险。您可以按如下方式检索 SSAID：

```
  String SSAID = Settings.Secure.ANDROID_ID;
```

