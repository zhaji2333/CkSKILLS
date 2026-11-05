# Android 反逆向防御[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#android-anti-reversing-defenses) · part 2 · part 2

> 分段 2/2。索引见 `Android反逆向防御-p2.md`。

要绕过此问题，我们必须稍微修改应用程序的行为（最简单的方法是使用 NOP 修补对 的调用`_exit`并将函数挂接到`_exit`中`libc.so`）。在这一点上，我们已经进入了众所周知的“军备竞赛”：实施更复杂的这种防御形式以及绕过它总是可能的。

### 绕过调试器检测[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-debugger-detection)

没有绕过反调试的通用方法：最好的方法取决于用于防止或检测调试的特定机制以及整体保护方案中的其他防御措施。例如，如果没有完整性检查或您已经停用了它们，则为应用程序打补丁可能是最简单的方法。在其他情况下，Hook框架或内核模块可能更可取。以下方法描述了绕过调试器检测的不同方法：

- 修补反调试功能：通过简单地用 NOP 指令覆盖它来禁用不需要的行为。请注意，如果反调试机制设计良好，可能需要更复杂的补丁。
- `isDebuggable`使用 Frida 或 Xposed 在 Java 和Native层上挂接 API：操纵函数的返回值，例如`isDebuggerConnected`隐藏调试器。
- 改变环境：Android 是一个开放的环境。如果实在不行，可以修改操作系统，颠覆开发者在设计反调试技巧时的假设。

#### 绕过示例：UnCrackable App for Android Level 2[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#bypassing-example-uncrackable-app-for-android-level-2)

在处理经过混淆的应用程序时，您经常会发现开发人员故意将数据和功能“隐藏”在Native库(NATIVE LIBRARIES)中。您将[在“UnCrackable App for Android”的第 2 级中](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l2)找到这方面的示例。

乍一看，代码看起来像之前的挑战。一个名为的类`CodeCheck`负责验证用户输入的代码。实际检查似乎发生在`bar`声明为本*机*方法的方法中。

```
package sg.vantagepoint.uncrackable2;

public class CodeCheck {
    public CodeCheck() {
        super();
    }

    public boolean a(String arg2) {
        return this.bar(arg2.getBytes());
    }

    private native boolean bar(byte[] arg1) {
    }
}

    static {
        System.loadLibrary("foo");
    }
```

请在 GitHub 中[查看针对 Android Crackme Level 2 的不同建议解决方案。](https://mas.owasp.org/crackmes/Android#android-uncrackable-l2)

### 成效评估[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#effectiveness-assessment_1)

检查反调试机制，包括以下标准：

- 附加基于 jdb 和 ptrace 的调试器失败或导致应用程序终止或出现故障。
- 多种检测方法分散在整个应用程序的源代码中（而不是它们都在一个方法或函数中）。
- 反调试防御在多个 API 层（Java、Native库(NATIVE LIBRARIES)函数、汇编器/系统调用）上运行。
- 这些机制在某种程度上是原创的（而不是从 StackOverflow 或其他来源复制和粘贴）。

努力绕过反调试防御并回答以下问题：

- 是否可以轻松绕过这些机制（例如，通过Hook单个 API 函数）？
- 通过静态和动态分析识别反调试代码有多难？
- 您是否需要编写自定义代码来禁用防御？你需要多少时间？
- 您对绕过这些机制的难度的主观评估是什么？

如果反调试机制缺失或太容易被绕过，请根据上述有效性标准提出建议。这些建议可能包括添加更多检测机制以及将现有机制与其他防御措施更好地集成。

## 测试文件完整性检查 (MSTG-RESILIENCE-3)[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#testing-file-integrity-checks-mstg-resilience-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#overview_2)

有两个与文件完整性相关的主题：

1. *代码完整性检查：*在“ [Android 上的篡改和逆向工程](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/)”一章中，我们讨论了Android 的APK 代码签名检查。我们还看到坚定的逆向工程师可以通过重新打包和重新签名应用程序轻松绕过此检查。为了使这个绕过过程更加复杂，可以通过对应用程序字节码、Native库(NATIVE LIBRARIES)和重要数据文件进行 CRC 检查来增强保护方案。这些检查可以在 Java 和Native层上实现。这个想法是要有额外的控制，这样即使代码签名有效，应用程序也只能在未修改的状态下正确运行。
2. *文件存储完整性检查：*应保护应用程序存储在SD卡或公共存储中的文件的完整性和存储的键值对的完整性`SharedPreferences`。

#### 示例实现 - 应用程序源代码[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#sample-implementation-application-source-code)

完整性检查通常会计算所选文件的校验和或哈希值。通常受保护的文件包括

- AndroidManifest.xml,
- 类文件 *.dex,
- Native库(NATIVE LIBRARIES) (*.so)。

以下[来自 Android 破解博客的示例实现](https://androidcracking.blogspot.com/2011/06/anti-tampering-with-crc-check.html)计算了一个 CRC `classes.dex`，并将其与预期值进行比较。

```
private void crcTest() throws IOException {
 boolean modified = false;
 // required dex crc value stored as a text string.
 // it could be any invisible layout element
 long dexCrc = Long.parseLong(Main.MyContext.getString(R.string.dex_crc));

 ZipFile zf = new ZipFile(Main.MyContext.getPackageCodePath());
 ZipEntry ze = zf.getEntry("classes.dex");

 if ( ze.getCrc() != dexCrc ) {
  // dex has been modified
  modified = true;
 }
 else {
  // dex not tampered with
  modified = false;
 }
}
```

#### 示例实施 - 存储[¶](https://mas.owasp.org/MASTG/Android/0x05j-Testing-Resiliency-Against-Reverse-Engineering/#sample-implementation-storage)

当在存储本身上提供完整性时，您可以在给定的键值对（对于 Android `SharedPreferences`）上创建 HMAC 或在文件系统提供的完整文件上创建 HMAC。

