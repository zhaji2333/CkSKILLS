# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 6 · part 2

> 分段 2/2。索引见 `Android数据存储-p6.md`。

- 等等

重复测试和内存转储将帮助您获得有关数据暴露长度的统计信息。此外，观察特定内存段（例如，字节数组）的变化方式可能会引导您找到一些无法识别的敏感数据（更多信息请参见下面的“补救”部分）。

## 测试设备访问安全策略 (MSTG-STORAGE-11)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-the-device-access-security-policy-mstg-storage-11)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_10)

处理或查询敏感信息的应用程序应在受信任且安全的环境中运行。要创建此环境，应用程序可以检查设备的以下内容：

- PIN 或密码保护设备锁定
- 最近的 Android 操作系统版本
- USB调试激活
- 设备加密
- 设备Root（另请参阅“测试Root检测”）

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_10)

要测试应用程序执行的设备访问安全策略，必须提供该策略的书面副本。该政策应该定义可用的检查及其执行。例如，一项检查可能要求应用仅在 Android 6.0（API 级别 23）或更高版本上运行，如果 Android 版本低于 6.0，则关闭应用或显示警告。

检查实现该策略的功能的源代码并确定它是否可以被绕过。

[*您可以通过查询Settings.Secure*](https://developer.android.com/reference/android/provider/Settings.Secure.html)的系统偏好设置来在 Android 设备上实施检查 。[*设备管理 API*](https://developer.android.com/guide/topics/admin/device-admin.html)提供了创建应用程序的技术，这些应用程序可以执行密码策略和设备加密。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_9)

动态分析取决于应用程序强制执行的检查及其预期行为。如果可以绕过检查，则必须对其进行验证。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#owasp-masvs)

- MSTG-STORAGE-1：“需要使用系统凭证存储设施来存储敏感数据，例如 PII、用户凭证或加密密钥。”
- MSTG-STORAGE-2：“不应将敏感数据存储在应用程序容器或系统凭证存储设施之外。”
- MSTG-STORAGE-3：“没有敏感数据写入应用程序日志。”
- MSTG-STORAGE-4：“除非是架构的必要部分，否则不会与第三方共享敏感数据。”
- MSTG-STORAGE-5：“键盘缓存在处理敏感数据的文本输入上被禁用。”
- MSTG-STORAGE-6：“没有敏感数据通过 IPC 机制公开。”
- MSTG-STORAGE-7：“没有敏感数据，例如密码或个人识别码，会通过用户界面暴露出来。”
- MSTG-STORAGE-8：“移动操作系统生成的备份中不包含任何敏感数据。”
- MSTG-STORAGE-9：“当移动到后台时，该应用程序会从视图中删除敏感数据。”
- MSTG-STORAGE-10：“该应用不会将敏感数据保存在内存中超过必要的时间，并且内存会在使用后明确清除。”
- MSTG-STORAGE-11：“该应用程序执行最低限度的设备访问安全策略，例如要求用户设置设备密码。”
- MSTG-PLATFORM-2：“来自外部来源和用户的所有输入都经过验证，并在必要时进行清理。这包括通过 UI、IPC 机制（如意图、自定义 URL 和网络来源）接收的数据。”

### 库（Libraries）[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#libraries)

- [Java AES Crypto](https://github.com/tozny/java-aes-crypto)
- [SQL Cipher](https://www.zetetic.net/sqlcipher/sqlcipher-for-android)
- [Secure Preferences](https://github.com/scottyab/secure-preferences)
- [Themis](https://github.com/cossacklabs/themis)
