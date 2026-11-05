# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 9 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p9.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 9

> 分段 9/10。索引见 `Android篡改和逆向工程.md`。

## 承接

    /data/app/sg.vantagepoint.helloworldjni-1/base.apk!/lib/arm64-v8a,
    /system/lib64,
    /vendor/lib64]
  ]
 ]
```

接下来，假设您对 libnative-lib.so 导出的方法感兴趣`0x7d1c49954c f Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI`。您可以使用 查找该地址`s 0x7d1c49954c`，分析该函数`af`并打印其反汇编的 10 行`pd 10`：

```
[0x7d1c49954c]> pdf
            ;-- sym.fun.Java_sg_vantagepoint_helloworldjni_MainActivity_stringFromJNI:
╭ (fcn) fcn.7d1c49954c 18
│   fcn.7d1c49954c (int32_t arg_40f942h);
│           ; arg int32_t arg_40f942h @ x29+0x40f942
│           0x7d1c49954c      080040f9       ldr x8, [x0]
│           0x7d1c499550      01000090       adrp x1, 0x7d1c499000
│           0x7d1c499554      21801591       add x1, x1, 0x560         ; hit0_4
│           0x7d1c499558      029d42f9       ldr x2, [x8, 0x538]       ; [0x538:4]=-1 ; 1336
│           0x7d1c49955c      4000           invalid
```

请注意，标记为 的行`; hit0_4`对应于我们之前找到的字符串：`0x7d1c499560 hit0_4 Hello from C++`。

要了解更多信息，请参阅[r2frida wiki](https://github.com/enovella/r2frida-wiki/blob/master/README.md)。

## 为逆向工程定制 Android[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-android-for-reverse-engineering)

在真实设备上工作具有优势，特别是对于交互式、调试器支持的静态/动态分析。例如，在真实设备上工作会更快。此外，在真实设备上运行目标应用程序不太可能触发防御。在战略点检测实时环境可为您提供有用的跟踪功能和操纵环境的能力，这将帮助您绕过应用程序可能实施的任何防篡改防御措施。

### 自定义 RAMDisk[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-the-ramdisk)

Initramfs 是存储在引导映像中的小型 CPIO 存档。它包含一些在启动时需要的文件，在安装实际的根文件系统之前。在 Android 上，initramfs 会无限期地挂载。它包含一个重要的配置文件 default.prop，它定义了一些基本的系统属性。更改此文件可以使 Android 环境更容易进行逆向工程。出于我们的目的，default.prop 中最重要的设置是`ro.debuggable`和`ro.secure`。

```
$ cat /default.prop
#
# ADDITIONAL_DEFAULT_PROPERTIES
#
ro.secure=1
ro.allow.mock.location=0
ro.debuggable=1
ro.zygote=zygote32
persist.radio.snapshot_enabled=1
persist.radio.snapshot_timer=2
persist.radio.use_cc_names=true
persist.sys.usb.config=mtp
rild.libpath=/system/lib/libril-qc-qmi-1.so
camera.disable_zsl_mode=1
ro.adb.secure=1
dalvik.vm.dex2oat-Xms=64m
dalvik.vm.dex2oat-Xmx=512m
dalvik.vm.image-dex2oat-Xms=64m
dalvik.vm.image-dex2oat-Xmx=64m
ro.dalvik.vm.native.bridge=0
```

设置`ro.debuggable`为“1”使所有正在运行的应用程序都可调试（即，调试器线程将在每个进程中运行），而不管`android:debuggable`Android Manifest 中的属性值。设置`ro.secure`为“0”会导致 adbd 以 root 身份运行。要在任何 Android 设备上修改 initrd，请使用 TWRP 备份原始引导映像或使用以下命令转储它：

```
adb shell cat /dev/mtd/mtd0 >/mnt/sdcard/boot.img
adb pull /mnt/sdcard/boot.img /tmp/boot.img
```

要提取引导映像的内容，请使用 Krzysztof Adamski 的操作指南中所述的 abootimg 工具：

```
mkdir boot
cd boot
../abootimg -x /tmp/boot.img
mkdir initrd
cd initrd
cat ../initrd.img | gunzip | cpio -vid
```

注意写入bootimg.cfg的引导参数；引导新内核和 ramdisk 时需要它们。

```
$ ~/Desktop/abootimg/boot$ cat bootimg.cfg
bootsize = 0x1600000
pagesize = 0x800
kerneladdr = 0x8000
ramdiskaddr = 0x2900000
secondaddr = 0xf00000
tagsaddr = 0x2700000
name =
cmdline = console=ttyHSL0,115200,n8 androidboot.hardware=hammerhead user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1
```

修改 default.prop 并打包你的新 ramdisk：

```
cd initrd
find . | cpio --create --format='newc' | gzip > ../myinitd.img
```

### 自定义 Android 内核[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#customizing-the-android-kernel)

Android 内核是逆向工程师的强大盟友。尽管常规的 Android 应用程序受到无可救药的限制和沙盒化，但作为逆向者，您可以按照自己的意愿自定义和更改操作系统和内核的行为。这给您带来了优势，因为大多数完整性检查和防篡改功能最终都依赖于内核执行的服务。部署一个滥用这种信任并且毫不掩饰地对自身和环境撒谎的内核，对于击败恶意软件作者（或普通开发人员）可以向您发起的大多数逆向防御大有帮助。

Android 应用程序有多种方式与操作系统交互。通过 Android 应用程序框架的 API 进行交互是标准的。然而，在最低层，许多重要的功能（例如分配内存和访问文件）被转换为老式的 Linux 系统调用。在 ARM Linux 上，系统调用是通过触发软件中断的 SVC 指令调用的。此中断调用`vector_swi`内核函数，然后内核函数使用系统调用编号作为函数指针表（在 Android 上称为 sys_call_table）的偏移量。

拦截系统调用最直接的方法就是将自己的代码注入内核内存，然后覆盖系统调用表中原有的函数，重定向执行。不幸的是，当前的 Android 内核会强制执行内存限制来防止这种情况发生。具体来说，库存棒棒糖和棉花糖内核是在启用 CONFIG_STRICT_MEMORY_RWX 选项的情况下构建的。这可以防止写入标记为只读的内核内存区域，因此任何修补内核代码或系统调用表的尝试都会导致分段错误并重新启动。要解决这个问题，请构建您自己的内核。然后您可以停用此保护并进行许多其他有用的自定义以简化逆向工程。如果您定期对 Android 应用程序进行逆向，那么构建您自己的逆向工程沙箱是轻而易举的事。

对于黑客攻击，我推荐支持 AOSP 的设备。谷歌的 Nexus 智能手机和平板电脑是最合乎逻辑的候选者，因为从 AOSP 构建的内核和系统组件可以毫无问题地运行在它们上面。索尼的Xperia系列也以开放着称。要构建 AOSP 内核，您需要一个工具链（一组用于交叉编译源代码的程序）和相应版本的内核源代码。按照 Google 的说明为给定的设备和 Android 版本识别正确的 git 存储库和分支。

https://source.android.com/source/building-kernels.html#id-version

例如，要获得与 Nexus 5 兼容的 Lollipop 的内核源代码，您需要克隆`msm`存储库并检查其中一个`android-msm-hammerhead`分支（hammerhead 是 Nexus 5 的代号，找到正确的分支是一件令人困惑的事情）。下载源代码后，使用命令创建默认内核配置`make hammerhead_defconfig`（将“hammerhead”替换为目标设备）。

```
git clone https://android.googlesource.com/kernel/msm.git
cd msm
git checkout origin/android-msm-hammerhead-3.4-lollipop-mr1
export ARCH=arm
export SUBARCH=arm
make hammerhead_defconfig
vim .config
```

我建议使用以下设置来添加可加载模块支持，启用最重要的跟踪功能，并打开内核内存以进行修补。

```
CONFIG_MODULES=Y
CONFIG_STRICT_MEMORY_RWX=N
CONFIG_DEVMEM=Y
CONFIG_DEVKMEM=Y
CONFIG_KALLSYMS=Y
CONFIG_KALLSYMS_ALL=Y
CONFIG_HAVE_KPROBES=Y
CONFIG_HAVE_KRETPROBES=Y
CONFIG_HAVE_FUNCTION_TRACER=Y
CONFIG_HAVE_FUNCTION_GRAPH_TRACER=Y
CONFIG_TRACING=Y
CONFIG_FTRACE=Y
CONFIG KDB=Y
```

完成编辑后保存 .config 文件，构建内核。

```
export ARCH=arm
export SUBARCH=arm
export CROSS_COMPILE=/path_to_your_ndk/arm-eabi-4.8/bin/arm-eabi-
make
```

您现在可以创建一个独立的工具链来交叉编译内核和后续任务。要为 Android 7.0（API 级别 24）创建工具链，请从 Android NDK 包运行 make-standalone-toolchain.sh：

```
cd android-ndk-rXXX
build/tools/make-standalone-toolchain.sh --arch=arm --platform=android-24 --install-dir=/tmp/my-android-toolchain
```

将 CROSS_COMPILE 环境变量设置为指向您的 NDK 目录并运行“make”来构建内核。

```
export CROSS_COMPILE=/tmp/my-android-toolchain/bin/arm-eabi-
make
```

### 引导自定义环境[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#booting-the-custom-environment)

在启动到新内核之前，请复制您设备的原始启动映像。找到引导分区：

```
root@hammerhead:/dev # ls -al /dev/block/platform/msm_sdcc.1/by-name/
lrwxrwxrwx root     root              1970-08-30 22:31 DDR -> /dev/block/mmcblk0p24
lrwxrwxrwx root     root              1970-08-30 22:31 aboot -> /dev/block/mmcblk0p6
lrwxrwxrwx root     root              1970-08-30 22:31 abootb -> /dev/block/mmcblk0p11
lrwxrwxrwx root     root              1970-08-30 22:31 boot -> /dev/block/mmcblk0p19
(...)
lrwxrwxrwx root     root              1970-08-30 22:31 userdata -> /dev/block/mmcblk0p28
```

然后将整个东西转储到一个文件中：

```
adb shell "su -c dd if=/dev/block/mmcblk0p19 of=/data/local/tmp/boot.img"
adb pull /data/local/tmp/boot.img
```

接下来，提取 ramdisk 和有关引导映像结构的信息。有多种工具可以做到这一点；我使用了 Gilles Grandou 的 abootimg 工具。安装该工具并在启动映像上运行以下命令：

```
abootimg -x boot.img
```

这应该在本地目录中创建文件 bootimg.cfg、initrd.img 和 zImage（您的原始内核）。

您现在可以使用 fastboot 来测试新内核。该`fastboot boot`命令允许您运行内核而无需实际刷新它（一旦您确定一切正常，您可以使用 fastboot flash 使更改永久生效，但您不必这样做）。使用以下命令以快速启动模式重启设备：

```
adb reboot bootloader
```

然后使用`fastboot boot`命令使用新内核启动 Android。除了新构建的内核和原始 ramdisk 之外，还指定内核偏移量、ramdisk 偏移量、标签偏移量和命令行（使用您提取的 bootimg.cfg 中列出的值）。

```
fastboot boot zImage-dtb initrd.img --base 0 --kernel-offset 0x8000 --ramdisk-offset 0x2900000 --tags-offset 0x2700000 -c "console=ttyHSL0,115200,n8 androidboot.hardware=hammerhead user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1"
```

系统现在应该正常启动。要快速验证正确的内核是否正在运行，请导航至**设置**->**关于手机**并检查**内核版本**字段。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/custom_kernel.jpg)

