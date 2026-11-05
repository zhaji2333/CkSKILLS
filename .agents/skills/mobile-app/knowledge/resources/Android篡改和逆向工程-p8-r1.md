# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 8 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p8.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 8

> 分段 8/10。索引见 `Android篡改和逆向工程.md`。

## 承接

0x0000007d10dee000 - 0x0000007d10e2b000 r-x /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d10e3a000 - 0x0000007d10e3b000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d10e3b000 - 0x0000007d10e3c000 rw- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
0x0000007d1c499000 - 0x0000007d1c49a000 r-x /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4a9000 - 0x0000007d1c4aa000 r-- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4aa000 - 0x0000007d1c4ab000 rw- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c516000 - 0x0000007d1c54d000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007dbd23c000 - 0x0000007dbd247000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007dc05db000 - 0x0000007dc05dc000 r-- /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.art
```

当您搜索或探索应用程序内存时，您始终可以在内存映射中验证您在每个时刻所处的位置（您当前的偏移量所在的位置）。您无需注意并搜索此列表中的内存地址，只需运行`\dm.`. 您将在下一节“内存中搜索”中找到示例。

如果您只对应用加载的模块（二进制文件和库）感兴趣，可以使用以下命令`\il`列出所有模块：

```
[0x00000000]> \il
0x000000558b1fd000 app_process64
0x0000007dbc859000 libandroid_runtime.so
0x0000007dbf5d7000 libbinder.so
0x0000007dbff4d000 libcutils.so
0x0000007dbfd13000 libhwbinder.so
0x0000007dbea00000 liblog.so
0x0000007dbcf17000 libnativeloader.so
0x0000007dbf21c000 libutils.so
0x0000007dbde4b000 libc++.so
0x0000007dbe09b000 libc.so
...
0x0000007d10dd0000 base.odex
0x0000007d1c499000 libnative-lib.so
0x0000007d2354e000 frida-agent-64.so
0x0000007dc065d000 linux-vdso.so.1
0x0000007dc065f000 linker64
```

如您所料，您可以将库的地址与内存映射相关联：例如，应用程序的Native库(NATIVE LIBRARIES)位于 ，`0x0000007d1c499000`优化的 dex (base.odex) 位于`0x0000007d10dd0000`。

您也可以使用objection来显示相同的信息。

```
$ objection --gadget sg.vantagepoint.helloworldjni explore

sg.vantagepoint.helloworldjni on (google: 8.1.0) [usb] # memory list modules
Save the output by adding `--json modules.json` to this command

Name                                             Base          Size                  Path
-----------------------------------------------  ------------  --------------------  --------------------------------------------------------------------
app_process64                                    0x558b1fd000  32768 (32.0 KiB)      /system/bin/app_process64
libandroid_runtime.so                            0x7dbc859000  1982464 (1.9 MiB)     /system/lib64/libandroid_runtime.so
libbinder.so                                     0x7dbf5d7000  557056 (544.0 KiB)    /system/lib64/libbinder.so
libcutils.so                                     0x7dbff4d000  77824 (76.0 KiB)      /system/lib64/libcutils.so
libhwbinder.so                                   0x7dbfd13000  163840 (160.0 KiB)    /system/lib64/libhwbinder.so
base.odex                                        0x7d10dd0000  442368 (432.0 KiB)    /data/app/sg.vantagepoint.helloworldjni-1/oat/arm64/base.odex
libnative-lib.so                                 0x7d1c499000  73728 (72.0 KiB)      /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
```

您甚至可以直接在 Android 文件系统中查看该二进制文件的大小和路径。

##### 内存搜索[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#in-memory-search)

内存中搜索是一种非常有用的技术，可用于测试应用程序内存中可能存在的敏感数据。

请参阅 r2frida 的搜索命令帮助 ( `\/?`) 以了解搜索命令并获取选项列表。以下仅显示其中的一个子集：

```
[0x00000000]> \/?
 /      search
 /j     search json
 /w     search wide
 /wj    search wide json
 /x     search hex
 /xj    search hex json
...
```

您可以使用搜索设置调整搜索`\e~search`。例如，`\e search.quiet=true;`将只打印结果并隐藏搜索进度：

```
[0x00000000]> \e~search
e search.in=perm:r--
e search.quiet=false
```

现在，我们将继续使用默认值并专注于字符串搜索。这个应用程序实际上非常简单，它从其Native库(NATIVE LIBRARIES)中加载字符串“Hello from C++”并将其显示给我们。您可以从搜索“Hello”开始，然后查看 r2frida 找到的内容：

```
[0x00000000]> \/ Hello
Searching 5 bytes: 48 65 6c 6c 6f
...
hits: 11
0x13125398 hit0_0 HelloWorldJNI
0x13126b90 hit0_1 Hello World!
0x1312e220 hit0_2 Hello from C++
0x70654ec5 hit0_3 Hello
0x7d1c499560 hit0_4 Hello from C++
0x7d1c4a9560 hit0_5 Hello from C++
0x7d1c51cef9 hit0_6 HelloWorldJNI
0x7d30ba11bc hit0_7 Hello World!
0x7d39cd796b hit0_8 Hello.java
0x7d39d2024d hit0_9 Hello;
0x7d3aa4d274 hit0_10 Hello
```

现在您想知道这些地址实际上在哪里。您可以通过为匹配 glob`\dm.`的所有命中运行命令来执行此操作：`@@``hit0_*`

```
[0x00000000]> \dm.@@ hit0_*
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x00000000703c2000 - 0x00000000709b5000 rw- /data/dalvik-cache/arm64/system@framework@boot-framework.art
0x0000007d1c499000 - 0x0000007d1c49a000 r-x /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c4a9000 - 0x0000007d1c4aa000 r-- /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64/libnative-lib.so
0x0000007d1c516000 - 0x0000007d1c54d000 r-- /data/app/sg.vantagepoint.helloworldjni-1/base.apk
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d396bc000 - 0x0000007d3a998000 r-- /system/framework/arm64/boot-framework.vdex
0x0000007d396bc000 - 0x0000007d3a998000 r-- /system/framework/arm64/boot-framework.vdex
0x0000007d3a998000 - 0x0000007d3aa9c000 r-- /system/framework/arm64/boot-ext.vdex
```

此外，您可以搜索出现的[宽版本字符串](https://en.wikipedia.org/wiki/Wide_character)( `\/w`)，并再次检查它们的内存区域：

```
[0x00000000]> \/w Hello
Searching 10 bytes: 48 00 65 00 6c 00 6c 00 6f 00
hits: 6
0x13102acc hit1_0 480065006c006c006f00
0x13102b9c hit1_1 480065006c006c006f00
0x7d30a53aa0 hit1_2 480065006c006c006f00
0x7d30a872b0 hit1_3 480065006c006c006f00
0x7d30bb9568 hit1_4 480065006c006c006f00
0x7d30bb9a68 hit1_5 480065006c006c006f00

[0x00000000]> \dm.@@ hit1_*
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000000013100000 - 0x0000000013140000 rw- /dev/ashmem/dalvik-main space (region space) (deleted)
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
0x0000007d30a00000 - 0x0000007d30c00000 rw-
```

它们与前面的字符串之一 ( `0x0000007d30a00000`) 位于相同的 rw- 区域中。请注意，搜索宽版本的字符串有时是找到它们的唯一方法，您将在下一节中看到。

内存中搜索对于快速了解某些数据是否位于主应用程序二进制文件、共享库或其他区域中非常有用。您还可以使用它来测试应用程序关于数据如何保存在内存中的行为。例如，您可以分析一个执行登录并搜索用户密码的应用程序。另外，您可以在登录完成后检查您是否仍然可以在内存中找到密码，以验证该敏感数据是否在使用后从内存中擦除。

此外，您可以使用这种方法来定位和提取加密密钥。例如，在应用程序加密/解密数据和处理内存中的密钥的情况下，而不是使用 AndroidKeyStore API。有关详细信息，请参阅“ [Android 加密 API](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/) ”一章中的“[测试密钥管理](https://mas.owasp.org/MASTG/Android/0x05e-Testing-Cryptography/#testing-key-management-mstg-storage-1-mstg-crypto-1-and-mstg-crypto-5)”部分。

##### 内存转储[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#memory-dump)

[您可以使用objection](https://github.com/sensepost/objection)和[Fridump](https://github.com/Nightbringer21/fridump)转储应用程序的进程内存。要在非 root 设备上利用这些工具，Android 应用程序必须重新打包`frida-gadget.so`并重新签名。这个过程的详细解释在“[非 Root 设备上的动态分析](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#dynamic-analysis-on-non-rooted-devices)”部分。要在 Root 手机上使用这些工具，只需安装并运行 frida-server。

> 注意：使用这些工具时，您可能会遇到一些通常可以忽略的内存访问冲突错误。这些工具会注入 Frida 代理并尝试转储应用程序的所有映射内存，而不管访问权限（读/写/执行）如何。因此，当注入的 Frida 代理试图读取一个不可读的区域时，它会返回相应的*memory access violation errors*。有关更多详细信息，请参阅上一节“内存映射和检查”。

如果反对，可以使用命令转储设备上正在运行的进程的所有内存`memory dump all`。

```
$ objection --gadget sg.vantagepoint.helloworldjni explore

sg.vantagepoint.helloworldjni on (google: 8.1.0) [usb] # memory dump all /Users/foo/memory_Android/memory

Will dump 719 rw- images, totalling 1.6 GiB
Dumping 1002.8 MiB from base: 0x14140000  [------------------------------------]    0%  00:11:03(session detach message) process-terminated
Dumping 8.0 MiB from base: 0x7fc753e000  [####################################]  100%
Memory dumped to file: /Users/foo/memory_Android/memory
```

> 在这种情况下，出现了一个错误，这可能是由于我们已经预料到的内存访问冲突。只要我们能够在文件系统中看到提取的转储，就可以安全地忽略此错误。如果您有任何问题，第一步是`-d`在运行反对时启用调试标志，或者，如果这没有帮助，请在[反对的 GitHub](https://github.com/sensepost/objection/issues)中提出问题。

接下来，我们可以使用 radare2 找到“Hello from C++”字符串：

```
$ r2 /Users/foo/memory_Android/memory
[0x00000000]> izz~Hello from
1136 0x00065270 0x00065270  14  15 () ascii Hello from C++
```

