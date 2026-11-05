# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 10

> 分段 10/10。索引见 `Android篡改和逆向工程.md`。

## 承接

假设一切正常，/bin/cat 应该*看不到*该文件。

```
$ adb shell su -c cat /data/local/tmp/nowyouseeme
tmp-mksh: cat: /data/local/tmp/nowyouseeme: No such file or directory
```

瞧！文件“nowyouseeme”现在对所有*用户模式*进程有点隐藏。请注意，可以使用其他系统调用轻松找到该文件，并且您需要执行更多操作才能正确隐藏文件，包括Hook`stat`、`access`和其他系统调用。

文件隐藏当然只是冰山一角：您可以使用内核模块完成很多工作，包括绕过许多Root检测措施、完整性检查和反调试措施。您可以在 Bernhard Mueller 的 Hacking Soft Tokens 论文 [#mueller] 的“案例研究”部分找到更多示例。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#references)

- Bionic - https://github.com/android/platform_bionic
- 使用调试器攻击 Android 应用程序（2015 年 1 月 19 日）- https://blog.netspi.com/attacking-android-applications-with-debuggers/
- [#josse] Sébastien Josse，动态恶意软件重新编译（2014 年 1 月 6 日）- http://ieeexplore.ieee.org/document/6759227/
- Xposed for Nougat 开发更新 - https://www.xda-developers.com/rovo89-updates-on-the-situation-regarding-xposed-for-nougat/
- 基于 Android 平台的 Linux 内核 rootkit（2011 年 4 月 4 日 - Phrack 杂志）
- [#mueller] Bernhard Mueller，黑客软令牌。Android 上的高级逆向工程（2016 年）- https://packetstormsecurity.com/files/138504/HITB_Hacking_Soft_Tokens_v1.2.pdf
