# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 5 · part 1

> 分段 1/2。索引见 `Android数据存储-p5.md`。

# Android数据存储[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#android-data-storage) · part 5

> 分段 5/6。索引见 `Android数据存储.md`。

#### 文本字段[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#text-fields)

为确保应用程序屏蔽了敏感的用户输入，请检查 的定义中的以下属性`EditText`：

```
android:inputType="textPassword"
```

使用此设置，点（而不是输入字符）将显示在文本字段中，防止应用程序将密码或 PIN 泄漏到用户界面。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_3)

在静态评估应用程序时，建议搜索`NotificationManager`类的任何使用情况，这可能表明某种形式的通知管理。如果正在使用该类，下一步就是了解应用程序如何[生成通知](https://developer.android.com/training/notify-user/build-notification#SimpleNotification)。

这些代码位置可以输入到下面的动态分析部分，提供应用程序通知可以动态生成的位置的想法。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_5)

要确定应用程序是否向用户界面泄露了任何敏感信息，请运行应用程序并识别可能泄露信息的组件。

#### 文本字段[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#text-fields_1)

如果信息被屏蔽，例如，用星号或点替换输入，应用程序不会将数据泄漏到用户界面。

#### 程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#app-notifications_4)

识别通知的使用贯穿整个应用程序及其所有可用功能，寻找触发任何通知的方法。考虑到您可能需要在应用程序外部执行操作才能触发某些通知。

在运行应用程序时，您可能希望开始跟踪对与通知创建相关的函数的所有调用，例如`setContentTitle`或`setContentText`from [`NotificationCompat.Builder`](https://developer.android.com/reference/androidx/core/app/NotificationCompat.Builder)。最后观察痕迹并评估它是否包含任何敏感信息。

## 测试敏感数据的备份 (MSTG-STORAGE-8)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#testing-backups-for-sensitive-data-mstg-storage-8)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_7)

此测试用例侧重于确保备份不存储敏感的应用程序特定数据。应执行以下检查：

- 检查`AndroidManifest.xml`相关的备份标志。
- 尝试备份应用程序并检查敏感数据的备份。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_7)

#### 当地的[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#local)

Android 提供了一个名为[`allowBackup`](https://developer.android.com/guide/topics/manifest/application-element.html#allowbackup)备份所有应用程序数据的属性。该属性在`AndroidManifest.xml`文件中设置。如果此属性的值为**true**，则设备允许用户通过命令使用 Android Debug Bridge (ADB) 备份应用程序`$ adb backup`。

要防止应用程序数据备份，请将`android:allowBackup`属性设置为**false**。当此属性不可用时，默认情况下启用 allowBackup 设置，并且必须手动停用备份。

> 注意：如果设备已加密，则备份文件也将被加密。

检查`AndroidManifest.xml`文件中是否有以下标志：

```
android:allowBackup="true"
```

如果标志值为**true**，则确定应用程序是否保存任何类型的敏感数据（检查测试用例“测试本地存储中的敏感数据”）。

#### 云[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#cloud)

无论您使用键/值备份还是自动备份，您都必须确定以下内容：

- 哪些文件被发送到云端（例如，SharedPreferences）
- 文件是否包含敏感信息
- 敏感信息在发送到云端之前是否加密。

> 如果您不想与 Google Cloud 共享文件，可以将它们从[Auto Backup](https://developer.android.com/guide/topics/data/autobackup.html#IncludingFiles)中排除。静态存储在设备上的敏感信息在发送到云端之前应该进行加密。

- **自动备份**`android:allowBackup`：您可以通过应用程序清单文件中的布尔属性配置自动备份。针对 Android 6.0（API 级别 23）的应用程序默认启用[自动备份。](https://developer.android.com/guide/topics/data/autobackup.html#EnablingAutoBackup)实现备份代理时可以使用该属性`android:fullBackupOnly`激活自动备份，但该属性仅适用于Android 6.0及以上版本。其他 Android 版本改为使用键/值备份。

```
android:fullBackupOnly
```

自动备份包括几乎所有应用程序文件，并在用户的 Google 云端硬盘帐户中为每个应用程序存储多达 25 MB 的文件。仅存储最近的备份；之前的备份被删除。

- **键/值备份**：要启用键/值备份，您必须在清单文件中定义备份代理。查找`AndroidManifest.xml`以下属性：

```
android:backupAgent
```

要实现键/值备份，请扩展以下类之一：

- [备份代理](https://developer.android.com/reference/android/app/backup/BackupAgent.html)
- [备份代理助手](https://developer.android.com/reference/android/app/backup/BackupAgentHelper.html)

要检查键/值备份实现，请在源代码中查找这些类。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_6)

执行所有可用的应用程序功能后，尝试通过备份`adb`。如果备份成功，请检查备份存档中的敏感数据。打开终端并运行以下命令：

```
adb backup -apk -nosystem <package-name>
```

ADB现在应该回复“现在解锁您的设备并确认备份操作”，并且应该在 Android 手机上要求您输入密码。这是一个可选步骤，您无需提供。如果电话未提示此消息，请尝试以下命令（包括引号）：

```
adb backup "-apk -nosystem <package-name>"
```

当您的设备的 adb 版本早于 1.0.31 时，就会出现此问题。如果是这种情况，您还必须在主机上使用 1.0.31 的 adb 版本。1.0.32 之后的 adb 版本[打破了向后兼容性。](https://issuetracker.google.com/issues/37096097)

*通过选择“备份我的数据”*选项批准从您的设备进行备份。备份过程完成后，文件*.ab*将位于您的工作目录中。运行以下命令将 .ab 文件转换为 tar。

```
dd if=mybackup.ab bs=24 skip=1|openssl zlib -d > mybackup.tar
```

如果出现错误`openssl:Error: 'zlib' is an invalid command.`，您可以尝试改用 Python。

```
dd if=backup.ab bs=1 skip=24 | python -c "import zlib,sys;sys.stdout.write(zlib.decompress(sys.stdin.read()))" > backup.tar
```

[*Android Backup Extractor*](https://github.com/nelenkov/android-backup-extractor)是另一种备用备份工具。要使该工具正常工作，您必须下载适用于[JRE7](https://www.oracle.com/technetwork/java/javase/downloads/jce-7-download-432124.html)或[JRE8](http://www.oracle.com/technetwork/java/javase/downloads/jce8-download-2133166.html)的 Oracle JCE Unlimited Strength Jurisdiction Policy Files并将它们放在 JRE lib/security 文件夹中。运行以下命令以转换 tar 文件：

```
java -jar abe.jar unpack backup.ab
```

如果显示一些Cipher信息和用法，说明还没有解包成功。在这种情况下，您可以尝试使用更多参数：

```
abe [-debug] [-useenv=yourenv] unpack <backup.ab> <backup.tar> [password]
```

[password]: 是你的Android设备之前询问你时的密码。例如这里是：123

```
java -jar abe.jar unpack backup.ab backup.tar 123
```

将 tar 文件提取到您的工作目录。

```
tar xvf mybackup.tar
```

## 在自动生成的屏幕截图中查找敏感信息 (MSTG-STORAGE-9)[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#finding-sensitive-information-in-auto-generated-screenshots-mstg-storage-9)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#overview_8)

制造商希望在应用程序启动和退出时为设备用户提供美观的体验，因此他们引入了屏幕截图保存功能，以便在应用程序后台Runtime(运行时)使用。此功能可能会带来安全风险。如果用户在显示敏感数据时故意截屏应用程序，则可能会暴露敏感数据。在设备上运行并能够连续捕获屏幕的恶意应用程序也可能会泄露数据。屏幕截图被写入本地存储，它们可能会被流氓应用程序（如果设备已获得 root 权限）或窃取设备的人从中恢复。

例如，捕获银行应用程序的屏幕截图可能会泄露有关用户帐户、信用、交易等的信息。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#static-analysis_8)

当前活动的屏幕截图是在 Android 应用程序进入后台时截取的，并在应用程序返回前台时出于美观目的显示。但是，这可能会泄露敏感信息。

要确定应用程序是否可能通过应用程序切换器公开敏感信息，请查看是否[`FLAG_SECURE`](https://developer.android.com/reference/android/view/Display.html#FLAG_SECURE)已设置该选项。您应该找到类似于以下代码片段的内容：

Java 中的示例：

```
getWindow().setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE);

setContentView(R.layout.activity_main);
```

Kotlin 中的示例：

```
window.setFlags(WindowManager.LayoutParams.FLAG_SECURE,
                WindowManager.LayoutParams.FLAG_SECURE)

setContentView(R.layout.activity_main)
```

如果未设置该选项，则应用程序容易受到屏幕捕获的影响。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05d-Testing-Data-Storage/#dynamic-analysis_7)

在对应用程序进行黑盒测试时，导航到包含敏感信息的任何屏幕并单击主页按钮将应用程序发送到后台，然后按应用程序切换器按钮以查看快照。如下图，如果`FLAG_SECURE`设置了（左图），快照将为空；如果未设置标志（右图），将显示活动信息：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/2.png) ![img](https://mas.owasp.org/assets/Images/Chapters/0x05d/1.png)

在支持[基于文件的加密 (FBE) 的](https://source.android.com/security/encryption/file-based)设备上，快照存储在该`/data/system_ce/<USER_ID>/<IMAGE_FOLDER_NAME>`文件夹中。`<IMAGE_FOLDER_NAME>`取决于供应商，但最常见的名称是`snapshots`和`recent_images`。如果设备不支持 FBE，`/data/system/<IMAGE_FOLDER_NAME>`则使用该文件夹。

> 访问这些文件夹和快照需要 root。

