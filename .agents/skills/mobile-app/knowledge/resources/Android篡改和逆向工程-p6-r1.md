# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 6 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p6.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 6

> 分段 6/10。索引见 `Android篡改和逆向工程.md`。

# 0x401854 = Incorrect serial
found = simgr.found[0]

# Get the solution string from *(R11 - 0x20).

addr = found.memory.load(found.regs.r11 - 0x20, 1, endness="Iend_LE")
concrete_addr = found.solver.eval(addr)
solution = found.solver.eval(found.memory.load(concrete_addr,10), cast_to=bytes)
print(base64.b32encode(solution))
```

正如之前在“[动态二进制](https://mas.owasp.org/MASTG/General/0x04c-Tampering-and-Reverse-Engineering/#static-and-dynamic-binary-analysis)检测”部分中讨论的那样，符号执行引擎为给定的程序输入构建一个操作的二叉树，并为可能采用的每个可能路径生成一个数学方程式。在内部，Angr 探索我们指定的两点之间的所有路径，并将相应的数学方程传递给求解器以返回有意义的具体结果。我们可以通过`simulation_manager.found`列表访问这些解决方案，其中包含满足我们指定搜索条件的 Angr 探索的所有可能路径。

仔细查看正在检索最终解决方案字符串的脚本的后半部分。字符串的地址是从 address 中获得的`r11 - 0x20`。这乍一看似乎很神奇，但仔细分析 处的函数可以`0x00001760`找到线索，因为它确定给定的输入字符串是否是有效的Licenses（许可证）密钥。在上面的反汇编中，您可以看到函数的输入字符串（在寄存器 R0 中）是如何存储到局部堆栈变量中的`0x0000176c str r0, [var_20h]`。因此，我们决定使用此值来检索脚本中的最终解决方案。使用`found.solver.eval`你可以问求解器问题，比如“给定这个操作序列的输出（ 中的当前状态`found`），输入（`addr`）必须是什么？”）。

> 在 ARMv7 中，R11 称为 fp（*函数指针*），因此`R11 - 0x20`等同于`fp-0x20`：`var int32_t var_20h @ fp-0x20`

接下来，`endness`脚本中的参数指定数据以“小端”方式存储，几乎所有 Android 设备都是这种情况。

此外，它可能看起来好像脚本只是从脚本的内存中读取解决方案字符串。但是，它是从符号内存中读取的。字符串和指向字符串的指针都不存在。求解器确保它提供的解决方案与程序执行到该点时相同。

运行此脚本应返回以下输出：

```
$ python3 solve.py
WARNING | ... | cle.loader | The main binary is a position-independent executable. It is being loaded with a base address of 0x400000.

b'JACE6ACIARNAAIIA'
```

现在您可以在您的 Android 设备中运行验证二进制文件来验证[此处](https://mas.owasp.org/MASTG/Android/Crackmes/README.md#android-license-validator)所示的解决方案。

> 您可能会使用脚本获得不同的解决方案，因为可能有多个有效的Licenses（许可证）密钥。

总而言之，学习符号执行一开始可能看起来有点吓人，因为它需要深刻的理解和广泛的实践。然而，考虑到与手动分析复杂的反汇编指令相比可以节省宝贵的时间，这种努力是合理的。通常您会使用混合技术，如上例所示，我们对反汇编代码进行手动分析，为符号执行引擎提供正确的标准。有关 Angr 用法的更多示例，请参阅 iOS 章节。

## 篡改和Runtime(运行时)检测[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#tampering-and-runtime-instrumentation)

首先，我们将了解一些修改和检测移动应用程序的简单方法。*篡改*意味着对应用程序进行补丁或Runtime(运行时)更改以影响其行为。例如，您可能想要停用阻碍测试过程的 SSL 固定或二进制保护。*Runtime Instrumentation*包括添加Hook和Runtime(运行时)补丁以观察应用程序的行为。然而，在移动应用程序安全性中，该术语泛指各种Runtime(运行时)操作，包括覆盖方法以更改行为。

### 修补、重新打包和重新签名[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-repackaging-and-re-signing)

对 Android 清单或字节码进行小的更改通常是修复阻止您测试或逆向工程应用程序的小烦恼的最快方法。在 Android 上，两个问题尤其经常发生：

1. 您无法使用代理拦截 HTTPS 流量，因为该应用程序使用 SSL 固定。
2. 您无法将调试器附加到应用程序，因为该`android:debuggable`标志未`"true"`在 Android 清单中设置。

在大多数情况下，这两个问题都可以通过对应用程序进行微小更改（也称为打补丁）然后重新签名和重新打包来解决。在默认 Android 代码签名之外运行额外完整性检查的应用程序是一个例外。在这些情况下，您还必须修补额外的检查。

第一步是使用以下命令解压和反汇编 APK `apktool`：

```
apktool d target_apk.apk
```

> `--no-src`注意：为了节省时间，如果您只想解压 APK 而不想反汇编代码，则可以使用该标志。例如，当您只想修改 Android Manifest 并立即重新打包时。

#### 修补示例：禁用证书固定[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-example-disabling-certificate-pinning)

对于出于正当理由想要拦截 HTTPS 通信的安全测试人员来说，证书固定是一个问题。修补字节码以停用 SSL 固定可以帮助解决这个问题。为了演示绕过证书固定，我们将在一个示例应用程序中完成一个实现。

解压和反汇编 APK 后，就可以在 Smali 源代码中找到证书固定检查了。在代码中搜索诸如“X509TrustManager”之类的关键字应该会为您指明正确的方向。

在我们的示例中，搜索“X509TrustManager”会返回一个实现自定义 TrustManager 的类。派生类实现方法`checkClientTrusted`、`checkServerTrusted`和`getAcceptedIssuers`。

要绕过固定检查，请将`return-void`操作码添加到每个方法的第一行。此操作码导致检查立即返回。通过此修改，不执行证书检查，并且应用程序接受所有证书。

```
.method public checkServerTrusted([LJava/security/cert/X509Certificate;Ljava/lang/String;)V
  .locals 3
  .param p1, "chain"  # [Ljava/security/cert/X509Certificate;
  .param p2, "authType"   # Ljava/lang/String;

  .prologue
  return-void      # <-- OUR INSERTED OPCODE!
  .line 102
  iget-object v1, p0, Lasdf/t$a;->a:Ljava/util/ArrayList;

  invoke-virtual {v1}, Ljava/util/ArrayList;->iterator()Ljava/util/Iterator;

  move-result-object v1

  :goto_0
  invoke-interface {v1}, Ljava/util/Iterator;->hasNext()Z
```

此修改将破坏 APK 签名，因此您还必须在重新打包后重新签署更改后的 APK 存档。

#### 修补示例：使应用程序可调试[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#patching-example-making-an-app-debuggable)

每个启用调试器的进程都运行一个额外的线程来处理 JDWP 协议数据包。此线程仅针对`android:debuggable="true"`在其清单文件`<application>`元素中设置了标志的应用程序启动。这是交付给最终用户的 Android 设备的典型配置。

在对应用程序进行逆向工程时，您通常只能访问目标应用程序的发布版本。发布版本并不意味着要调试，这就是*调试版本*的目的。如果系统属性`ro.debuggable`设置为“0”，Android 将不允许发布版本的 JDWP 和Native调试。虽然这很容易绕过，但您仍然可能会遇到限制，例如缺少行断点。*尽管如此，即使是一个不完美的调试器仍然是一个非常*宝贵的工具，能够检查程序的Runtime(运行时)状态使得理解程序变得容易得多。

要将发布版本*转换*为可调试版本，您需要修改 Android 清单文件 (AndroidManifest.xml) 中的标志。解压应用程序（例如`apktool d --no-src UnCrackable-Level1.apk`）并解码 Android Manifest 后，`android:debuggable="true"`使用文本编辑器将其添加：

```
<application android:allowBackup="true" android:debuggable="true" android:icon="@drawable/ic_launcher" android:label="@string/app_name" android:name="com.xxx.xxx.xxx" android:theme="@style/AppTheme">
```

即使我们没有更改源代码，此修改也会破坏 APK 签名，因此您还必须重新签署更改后的 APK 存档。

#### 重新包装[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#repackaging)

您可以通过执行以下操作轻松地重新打包应用程序：

```
cd UnCrackable-Level1
apktool b
zipalign -v 4 dist/UnCrackable-Level1.apk ../UnCrackable-Repackaged.apk
```

请注意，Android Studio 构建工具目录必须在路径中。它位于`[SDK-Path]/build-tools/[version]`。`zipalign`和`apksigner`工具都在这个目录中。

#### 重签[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#re-signing)

在重新签名之前，您首先需要一个代码签名证书。如果您之前在 Android Studio 中构建过项目，则 IDE 已经在`$HOME/.android/debug.keystore`. 此 KeyStore 的默认密码为“android”，密钥称为“androiddebugkey”。

标准 Java 发行版包括`keytool`用于管理 KeyStore 和证书的内容。您可以创建自己的签名证书和密钥，然后将其添加到调试密钥库：

```
keytool -genkey -v -keystore ~/.android/debug.keystore -alias signkey -keyalg RSA -keysize 2048 -validity 20000
```

证书可用后，您可以使用它重新签署 APK。确保它`apksigner`在路径中，并且您从重新打包的 APK 所在的文件夹运行它。

```
apksigner sign --ks  ~/.android/debug.keystore --ks-key-alias signkey UnCrackable-Repackaged.apk
```

注意：如果您在使用 时遇到 JRE 兼容性问题`apksigner`，可以`jarsigner`改为使用。执行此操作时，`zipalign`必须**在**签名后调用。

```
jarsigner -verbose -keystore ~/.android/debug.keystore ../UnCrackable-Repackaged.apk signkey
zipalign -v 4 dist/UnCrackable-Level1.apk ../UnCrackable-Repackaged.apk
```

现在您可以重新安装该应用程序：

```
adb install UnCrackable-Repackaged.apk
```

#### “等待调试器”功能[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#the-wait-for-debugger-feature)

[Android 级别 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)的UnCrackable 应用程序并不愚蠢：它注意到它已在可调试模式下运行，并通过关闭做出反应。立即显示模式对话框，点击“确定”后 crackme 终止。

