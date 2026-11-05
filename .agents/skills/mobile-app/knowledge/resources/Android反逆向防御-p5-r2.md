# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 5 · part 2

> 分段 2/2。索引见 `Android反逆向防御-p5.md`。

[自 Android 8.0（API 级别 26）以来](https://android-developers.googleblog.com/2017/04/changes-to-device-identifiers-in.html)，SSAID 和 MAC 地址的行为发生了变化。此外，Google 的 SDK 文档中还有关于标识符的[新建议](https://developer.android.com/training/articles/user-data-ids.html)。由于这种新行为，我们建议开发人员不要单独依赖 SSAID。标识符变得不太稳定。例如，在恢复出厂设置后或在升级到 Android 8.0（API 级别 26）后重新安装应用程序时，SSAID 可能会发生变化。有些设备具有相同的`ANDROID_ID`和/或具有`ANDROID_ID`可以被覆盖的。因此，最好使用从使用加密中`ANDROID_ID`随机生成的密钥来加密。加密后应存储在`AndroidKeyStore``AES_GCM``ANDROID_ID``SharedPreferences`（私下）。应用程序签名更改的那一刻，应用程序可以检查增量并注册新的`ANDROID_ID`. 在没有新的应用程序签名密钥的情况下发生变化的那一刻，它应该表明其他地方出了问题。

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_6)

当源代码可用时，您可以查找一些关键术语：

- 不再有效的唯一标识符：
- `Build.SERIAL`没有`Build.getSerial`
- `htc.camera.sensor.front_SN`适用于 HTC 设备
- `persist.service.bdroid.bdadd`
- `Settings.Secure.bluetooth_address`或`WifiInfo.getMacAddress`from ，除非在清单中启用`WifiManager`了系统权限。`LOCAL_MAC_ADDRESS`
- ANDROID_ID 仅用作标识符。随着时间的推移，这将影响旧设备上的绑定质量。
- 缺少实例 ID、`Build.SERIAL`和 IMEI。

```
  TelephonyManager tm = (TelephonyManager) context.getSystemService(Context.TELEPHONY_SERVICE);
  String IMEI = tm.getDeviceId();
```

为确保可以使用标识符，请检查`AndroidManifest.xml`IMEI 和`Build.Serial`. 清单应包含权限`<uses-permission android:name="android.permission.READ_PHONE_STATE" />`。

有几种动态测试设备绑定的方法：

#### 使用模拟器[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-an-emulator)

请参阅上面的“[使用仿真器进行动态分析](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#dynamic-analysis-with-an-emulator)”部分。

#### 使用两个不同的 root 设备[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#using-two-different-rooted-devices)

1. 在您的 root 设备上运行该应用程序。
2. 确保您可以在应用程序实例中提高信任度（例如，在应用程序中进行身份验证）。
3. 从第一个有Root设备检索数据。
4. 在第二个获得 root 权限的设备上安装应用程序。
5. 在应用程序的数据文件夹中，覆盖第 3 步中的数据。
6. 你能继续处于认证状态吗？如果是这样，绑定可能无法正常工作。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#owasp-masvs)

- MSTG-RESILIENCE-1：“该应用程序通过提醒用户或终止该应用程序来检测并响应已破解或越狱设备的存在。”
- MSTG-RESILIENCE-2：“应用程序阻止调试和/或检测并响应附加的调试器。必须涵盖所有可用的调试协议。”
- MSTG-RESILIENCE-3：“该应用程序检测并响应篡改其自身沙箱中的可执行文件和关键数据。”
- MSTG-RESILIENCE-4：“该应用程序检测并响应设备上广泛使用的逆向工程工具和框架的存在。”
- MSTG-RESILIENCE-5：“应用程序检测并响应在模拟器中运行。”
- MSTG-RESILIENCE-6：“该应用程序检测并响应篡改其自身内存空间中的代码和数据。”
- MSTG-RESILIENCE-9：“混淆应用于程序化防御，这反过来又通过动态分析阻碍了去混淆。”
- MSTG-RESILIENCE-10：“该应用程序使用从设备唯一的多个属性派生的设备指纹来实现‘设备绑定’功能。”

### 安全网认证[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#safetynet-attestation)

- 开发人员指南 - https://developer.android.com/training/safetynet/attestation.html
- SafetyNet 认证清单 - https://developer.android.com/training/safetynet/attestation-checklist
- SafetyNet 认证的注意事项 - https://android-developers.googleblog.com/2017/11/10-things-you-might-be-doing-wrong-when.html
- SafetyNet 验证示例 - https://github.com/googlesamples/android-play-safetynet/
- SafetyNet Attestation API - 配额请求 - https://support.google.com/googleplay/android-developer/contact/safetynetqr
- 混淆器-LLVM - https://github.com/obfuscator-llvm/obfuscator
