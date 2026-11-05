# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 8 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p8.md`。

或者你可以使用 Fridump。这一次，我们将输入一个字符串，看看能否在内存转储中找到它。为此，打开[MASTG Hacking Playground](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#mastg-hacking-playground)应用程序，导航至“OMTG_DATAST_002_LOGGING”并在密码字段中输入“owasp-mstg”。接下来，运行 Fridump：

```
python3 fridump.py -U sg.vp.owasp_mobile.omtg_android -s

Current Directory: /Users/foo/git/fridump
Output directory is set to: /Users/foo/git/fridump/dump
Starting Memory dump...
Oops, memory access violation!-------------------------------] 0.28% Complete
Progress: [##################################################] 99.58% Complete
Running strings on all files:
Progress: [##################################################] 100.0% Complete

Finished!
```

> `-v`提示：如果您想查看更多详细信息（例如引发内存访问冲突的区域），请通过包含标志来启用详细信息。

它需要一段时间才能完成，您将在转储文件夹中获得一组 *.data 文件。添加`-s`标志时，所有字符串都从转储的原始内存文件中提取并添加到文件`strings.txt`中，该文件也存储在转储目录中。

```
ls dump/
dump/1007943680_dump.data dump/357826560_dump.data  dump/630456320_dump.data ... strings.txt
```

最后，在转储目录中搜索输入字符串：

```
$ grep -nri owasp-mstg dump/
Binary file dump//316669952_dump.data matches
Binary file dump//strings.txt matches
```

“owasp-mstg”字符串可以在其中一个转储文件以及已处理的字符串文件中找到。

##### Runtime(运行时)逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#runtime-reverse-engineering)

Runtime(运行时)逆向工程可以看作是实时版本的逆向工程，您没有主机的二进制数据。相反，您将直接从应用程序的内存中分析它。

我们将继续使用 HelloWorld JNI 应用程序，使用 r2frida 打开一个会话，`r2 frida://usb//sg.vantagepoint.helloworldjni`您可以使用以下`\i`命令显示目标二进制信息：

```
[0x00000000]> \i
arch                arm
bits                64
os                  linux
pid                 13215
uid                 10096
objc                false
runtime             V8
java                true
cylang              false
pageSize            4096
pointerSize         8
codeSigningPolicy   optional
isDebuggerAttached  false
cwd                 /
dataDir             /data/user/0/sg.vantagepoint.helloworldjni
codeCacheDir        /data/user/0/sg.vantagepoint.helloworldjni/code_cache
extCacheDir         /storage/emulated/0/Android/data/sg.vantagepoint.helloworldjni/cache
obbDir              /storage/emulated/0/Android/obb/sg.vantagepoint.helloworldjni
filesDir            /data/user/0/sg.vantagepoint.helloworldjni/files
noBackupDir         /data/user/0/sg.vantagepoint.helloworldjni/no_backup
codePath            /data/app/sg.vantagepoint.helloworldjni-1/base.apk
packageName         sg.vantagepoint.helloworldjni
androidId           c92f43af46f5578d
cacheDir            /data/local/tmp
jniEnv              0x7d30a43c60
```

搜索某个模块的所有符号`\is <lib>`，例如`\is libnative-lib.so`。

```
[0x00000000]> \is libnative-lib.so

[0x00000000]>
```

在这种情况下是空的。或者，您可能更愿意查看导入/导出。例如，列出导入`\ii <lib>`：

```
[0x00000000]> \ii libnative-lib.so
0x7dbe1159d0 f __cxa_finalize /system/lib64/libc.so
0x7dbe115868 f __cxa_atexit /system/lib64/libc.so
```

并列出出口`\iE <lib>`：

```
[0x00000000]> \iE libnative-lib.so
0x7d1c49954c f Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI
```

> 对于大型二进制文件，建议通过附加 , 将输出传输到内部 less 程序`~..`，即`\ii libandroid_runtime.so~..`（如果不是，对于此二进制文件，您将在终端上打印近 2500 行）。

接下来您可能想要查看的是**当前加载**的Java 类：

```
[0x00000000]> \ic~sg.vantagepoint.helloworldjni
sg.vantagepoint.helloworldjni.MainActivity
```

列出类字段：

```
[0x00000000]> \ic sg.vantagepoint.helloworldjni.MainActivity~sg.vantagepoint.helloworldjni
public native java.lang.String sg.vantagepoint.helloworldjni.MainActivity.stringFromJNI()
public sg.vantagepoint.helloworldjni.MainActivity()
```

请注意，我们已按包名称进行过滤，因为`MainActivity`它包含 Android`Activity`类中的所有方法。

您还可以显示有关类加载器的信息：

```
[0x00000000]> \icL
dalvik.system.PathClassLoader[
 DexPathList[
  [
   directory "."]
  ,
  nativeLibraryDirectories=[
   /system/lib64,
    /vendor/lib64,
    /system/lib64,
    /vendor/lib64]
  ]
 ]
java.lang.BootClassLoader@b1f1189dalvik.system.PathClassLoader[
 DexPathList[
  [
   zip file "/data/app/sg.vantagepoint.helloworldjni-1/base.apk"]
  ,
  nativeLibraryDirectories=[
   /data/app/sg.vantagepoint.helloworldjni-1/lib/arm64,
