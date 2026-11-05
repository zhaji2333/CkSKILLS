# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 7 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p7.md`。

查看方法`string.equals`末尾的比较和上面块`a`中字符串的创建`arrby`。是函数的返回值。comparison 将您的输入与 进行比较。所以我们想要的返回值`try``arrby``sg.vantagepoint.a.a.a``string.equals``arrby``sg.vantagepoint.a.a.a.`

无需逆向解密例程来重建密钥，您可以简单地忽略应用程序中的所有解密逻辑并Hook`sg.vantagepoint.a.a.a`函数以捕获其返回值。这是防止在 root 上退出并拦截秘密字符串解密的完整脚本：

```
setImmediate(function() { //prevent timeout
    console.log("[*] Starting script");

    Java.perform(function() {
        var mainActivity = Java.use("sg.vantagepoint.uncrackable1.MainActivity");
        mainActivity.a.implementation = function(v) {
           console.log("[*] MainActivity.a called");
        };
        console.log("[*] MainActivity.a modified");

        var aaClass = Java.use("sg.vantagepoint.a.a");
        aaClass.a.implementation = function(arg1, arg2) {
        var retval = this.a(arg1, arg2);
        var password = '';
        for(var i = 0; i < retval.length; i++) {
            password += String.fromCharCode(retval[i]);
        }

        console.log("[*] Decrypted: " + password);
            return retval;
        };
        console.log("[*] sg.vantagepoint.a.a.a modified");
    });
});
```

在 Frida 中运行脚本并在控制台中看到“[*] sg.vantagepoint.aaa modified”消息后，为“secret string”输入一个随机值并按验证。您应该得到类似于以下内容的输出：

```
$ frida -U -f owasp.mstg.uncrackable1 -l uncrackable1.js --no-pause

[*] Starting script
[USB::Android Emulator 5554::sg.vantagepoint.uncrackable1]-> [*] MainActivity.a modified
[*] sg.vantagepoint.a.a.a modified
[*] MainActivity.a called.
[*] Decrypted: I want to believe
```

钩子函数输出解密的字符串。您提取了秘密字符串，而不必深入研究应用程序代码及其解密例程。

您现在已经了解了 Android 上静态/动态分析的基础知识。当然，*真正*学习它的唯一方法是亲身体验：在 Android Studio 中构建您自己的项目，观察您的代码如何被翻译成字节码和原生代码，并尝试破解我们的挑战。

在其余部分中，我们将介绍一些高级主题，包括进程探索、内核模块和动态执行。

#### 过程探索[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#process-exploration)

在测试应用程序时，进程探索可以让测试人员深入了解应用程序进程内存。它可以通过Runtime(运行时)检测来实现，并允许执行以下任务：

- 检索内存映射和加载的库。
- 搜索特定数据的出现。
- 经过查找，得到内存映射中某个偏移量的位置。
- 执行内存转储并*离线*检查或反向工程二进制数据。
- 在Runtime(运行时)对Native库(NATIVE LIBRARIES)进行逆向工程。

如您所见，这些被动任务帮助我们收集信息。此信息通常用于其他技术，例如方法Hook。

在以下部分中，您将使用[r2frida](https://mas.owasp.org/MASTG/Tools/0x08a-Testing-Tools/#r2frida)直接从应用程序Runtime(运行时)检索信息。请参考[r2frida官方安装说明](https://github.com/nowsecure/r2frida/blob/master/README.md#installation)。首先打开一个 r2frida 会话到目标应用程序（例如[HelloWorld JNI](https://github.com/OWASP/owasp-mastg/raw/master/Samples/Android/01_HelloWorld-JNI/HelloWord-JNI.apk) APK），该应用程序应该在您的 Android 手机上运行（通过 USB 连接）。使用以下命令：

```
r2 frida://usb//sg.vantagepoint.helloworldjni
```

> 查看所有选项`r2 frida://?`。

一旦进入 r2frida 会话，所有命令都以`\`. 例如，在 radare2 中你会运行`i`以显示二进制信息，但在 r2frida 中你会使用`\i`.

##### 内存映射和检查[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-maps-and-inspection)

您可以通过运行检索应用程序的内存映射`\dm`，Android 中的输出可能会很长（例如 1500 到 2000 行之间），以缩小搜索范围并仅查看直接属于应用程序的内容`~`，按包名称应用 grep () `\dm~<package_name>`：

```
[0x00000000]> \dm~sg.vantagepoint.helloworldjni
0x000000009b2dc000 - 0x000000009b361000 rw- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x000000009b361000 - 0x000000009b36e000 --- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x000000009b36e000 - 0x000000009b371000 rw- /dev/ashmem/dalvik-/data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art (deleted)
0x0000007d103be000 - 0x0000007d10686000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.vdex
0x0000007d10dd0000 - 0x0000007d10dee000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
