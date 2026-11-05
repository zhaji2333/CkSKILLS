# Android 代码质量和构建设置[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-code-quality-and-build-settings) · part 2 · part 2

> 分段 2/2。索引见 `Android代码质量和构建设置-p2.md`。

该应用程序的[NDK 原生库](https://mas.owasp.org/MASTG/Android/0x05b-Basic-Security_Testing/#native-libraries)也[使用 ELF 格式](https://developer.android.com/ndk/guides/abis)。

- [**PIE（位置独立可执行文件）**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#position-independent-code)：
- 从 Android 7.0（API 级别 24）开始，主要可执行文件[默认启用PIC 编译。](https://source.android.com/devices/tech/dalvik/configure)
- [在 Android 5.0（API 级别 21）中，不再](https://source.android.com/security/enhancements/enhancements50)支持非 PIE 启用的Native库(NATIVE LIBRARIES)，从那时起，PIE[由链接器强制执行](https://cs.android.com/android/platform/superproject/+/master:bionic/linker/linker_main.cpp;l=430)。
- [**内存管理**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#memory-management)：
- 垃圾收集将只针对主要二进制文件运行，二进制文件本身无需检查任何内容。
- 垃圾收集不适用于 Android Native库(NATIVE LIBRARIES)。开发人员负责进行适当的[手动内存管理](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#manual-memory-management)。请参阅[“内存损坏错误 (MSTG-CODE-8)”](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#memory-corruption-bugs-mstg-code-8)。
- [**堆栈粉碎保护**](https://mas.owasp.org/MASTG/General/0x04h-Testing-Code-Quality/#stack-smashing-protection)：
- Android 应用程序被编译为 Dalvik 字节码，这被认为是内存安全的（至少用于缓解缓冲区溢出）。其他框架（例如 Flutter）不会使用堆栈金丝雀进行编译，因为它们的语言（在本例中为 Dart）会减轻缓冲区溢出。
- 必须为 Android Native库(NATIVE LIBRARIES)启用它，但可能很难完全确定它。
  - NDK 库应该启用它，因为编译器默认启用它。
  - 其他自定义 C/C++ 库可能未启用它。

学到更多：

- [Android可执行格式](https://lief-project.github.io/doc/latest/tutorials/10_android_formats.html)
- [Android Runtime(运行时) (ART)](https://source.android.com/devices/tech/dalvik/configure#how_art_works)
- [AndroidNDK](https://developer.android.com/ndk/guides)
- [NDK 开发人员的 Android 链接器更改](https://android.googlesource.com/platform/bionic/+/master/android-changes-for-ndk-developers.md)

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#static-analysis_7)

测试应用原生库以确定它们是否启用了 PIE 和堆栈粉碎保护。

您可以使用[radare2 的 rabin2](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#radare2)来获取二进制信息。我们将使用[UnCrackable App for Android Level 4](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l4) v1.0 APK 作为示例。

所有Native库(NATIVE LIBRARIES)都必须具有`canary`并且`pic`都设置为`true`.

情况就是这样`libnative-lib.so`：

```
rabin2 -I lib/x86_64/libnative-lib.so | grep -E "canary|pic"
canary   true
pic      true
```

但不是为了`libtool-checker.so`：

```
rabin2 -I lib/x86_64/libtool-checker.so | grep -E "canary|pic"
canary   false
pic      true
```

在此示例中，`libtool-checker.so`必须使用堆栈粉碎保护支持重新编译。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#references)

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#owasp-masvs)

- MSTG-CODE-1：“该应用程序已签名并使用有效证书进行配置，其中的私钥受到适当保护。”
- MSTG-CODE-2：“该应用程序已在发布模式下构建，具有适用于发布构建的设置（例如不可调试）。”
- MSTG-CODE-3：“调试符号已从Native二进制文件中删除。”
- MSTG-CODE-4：“调试代码和开发人员帮助代码（例如测试代码、后门、隐藏设置）已被删除。该应用程序不会记录详细错误或调试消息。”
- MSTG-CODE-5：“移动应用程序使用的所有第三方组件，例如库和框架，都被识别并检查已知漏洞。”
- MSTG-CODE-6：“应用程序捕获并处理可能的异常。”
- MSTG-CODE-7：“安全控制中的错误处理逻辑默认拒绝访问。”
- MSTG-CODE-8：“在非托管代码中，安全地分配、释放和使用内存。”
- MSTG-CODE-9：“工具链提供的免费安全功能已激活，例如字节码缩小、堆栈保护、PIE 支持和自动引用计数。”

### 内存分析参考[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#memory-analysis-references)

- Android 反序列化漏洞简史 - https://securitylab.github.com/research/android-deserialization-vulnerabilities
- 在 Android 中避免内存泄漏的 9 种方法 - https://android.jlelse.eu/9-ways-to-avoid-memory-leaks-in-android-b6d81648e35e
- Android 中的内存泄漏模式 - https://android.jlelse.eu/memory-leak-patterns-in-android-4741a7fcb570

### Android文档[¶](https://mas.owasp.org/MASTG/Android/0x05i-Testing-Code-Quality-and-Build-Settings/#android-documentation)

- 带密钥轮换的 APK 签名方案 - https://developer.android.com/about/versions/pie/android-9.0#apk-key-rotation
