# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 9 · part 2

> 分段 2/2。索引见 `Android篡改和逆向工程-p9.md`。

### 使用内核模块Hook系统调用[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#system-call-hooking-with-kernel-modules)

系统调用Hook允许您攻击任何依赖于内核提供的功能的反逆向防御。自定义内核就位后，您现在可以使用 LKM 将其他代码加载到内核中。您还可以访问 /dev/kmem 接口，您可以使用该接口即时修补内核内存。这是一种经典的 Linux rootkit 技术，由 Dong-Hoon You 在 Phrack Magazine - “Android platform based linux kernel rootkit”2011 年 4 月 4 日针对 Android 进行了描述。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/syscall_hooking.jpg)

您首先需要 sys_call_table 的地址。幸运的是，它在 Android 内核中作为符号导出（iOS 逆向器就没那么幸运了）。您可以在 /proc/kallsyms 文件中查找地址：

```
$ adb shell "su -c echo 0 > /proc/sys/kernel/kptr_restrict"
$ adb shell cat /proc/kallsyms | grep sys_call_table
c000f984 T sys_call_table
```

这是编写内核模块所需的唯一内存地址。您可以使用从内核头文件中获取的偏移量来计算其他所有内容（希望您还没有删除它们）。

#### 示例：文件隐藏[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#example-file-hiding)

在本指南中，我们将使用内核模块来隐藏文件。在设备上创建一个文件，以便稍后隐藏它：

```
$ adb shell "su -c echo ABCD > /data/local/tmp/nowyouseeme"
$ adb shell cat /data/local/tmp/nowyouseeme
ABCD
```

是时候编写内核模块了。对于文件隐藏，您需要Hook用于打开（或检查文件是否存在）的系统调用之一。其中有很多：`open`, `openat`, `access`, `accessat`, `facessat`, `stat`,`fstat`等。现在，您将只Hook`openat`系统调用。这是 /bin/cat 程序在访问文件时使用的系统调用，因此该调用应该适合演示。

您可以在内核头文件 arch/arm/include/asm/unistd.h 中找到所有系统调用的函数原型。使用以下代码创建一个名为 kernel_hook.c 的文件：

```
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/moduleparam.h>
#include <linux/unistd.h>
#include <linux/slab.h>
#include <asm/uaccess.h>

asmlinkage int (*real_openat)(int, const char __user*, int);

void **sys_call_table;

int new_openat(int dirfd, const char \__user* pathname, int flags)
{
  char *kbuf;
  size_t len;

  kbuf=(char*)kmalloc(256,GFP_KERNEL);
  len = strncpy_from_user(kbuf,pathname,255);

  if (strcmp(kbuf, "/data/local/tmp/nowyouseeme") == 0) {
    printk("Hiding file!\n");
    return -ENOENT;
  }

  kfree(kbuf);

  return real_openat(dirfd, pathname, flags);
}

int init_module() {

  sys_call_table = (void*)0xc000f984;
  real_openat = (void*)(sys_call_table[\__NR_openat]);

return 0;

}
```

要构建内核模块，您需要内核源代码和可用的工具链。由于您已经构建了一个完整的内核，所以一切就绪。创建一个包含以下内容的 Makefile：

```
KERNEL=[YOUR KERNEL PATH]
TOOLCHAIN=[YOUR TOOLCHAIN PATH]

obj-m := kernel_hook.o

all:
        make ARCH=arm CROSS_COMPILE=$(TOOLCHAIN)/bin/arm-eabi- -C $(KERNEL) M=$(shell pwd) CFLAGS_MODULE=-fno-pic modules

clean:
        make -C $(KERNEL) M=$(shell pwd) clean
```

运行`make`以编译代码，这将创建文件 kernel_hook.ko。将 kernel_hook.ko 复制到设备并使用`insmod`命令加载它。使用该`lsmod`命令验证模块是否已成功加载。

```
$ make
(...)
$ adb push kernel_hook.ko /data/local/tmp/
[100%] /data/local/tmp/kernel_hook.ko
$ adb shell su -c insmod /data/local/tmp/kernel_hook.ko
$ adb shell lsmod
kernel_hook 1160 0 [permanent], Live 0xbf000000 (PO)
```

现在您将访问 /dev/kmem 以`sys_call_table`用您新注入的函数的地址覆盖原始函数指针（这可以直接在内核模块中完成，但 /dev/kmem 提供了一种简单的方法来切换您的钩子和关闭）。为此，我们改编了 Dong-Hoon You 的 Phrack 文章中的代码。但是，您可以使用文件接口而不是`mmap`因为后者可能会导致内核崩溃。使用以下代码创建一个名为 kmem_util.c 的文件：

```
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <asm/unistd.h>
#include <sys/mman.h>

#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)

int kmem;
void read_kmem2(unsigned char *buf, off_t off, int sz)
{
  off_t offset; ssize_t bread;
  offset = lseek(kmem, off, SEEK_SET);
  bread = read(kmem, buf, sz);
  return;
}

void write_kmem2(unsigned char *buf, off_t off, int sz) {
  off_t offset; ssize_t written;
  offset = lseek(kmem, off, SEEK_SET);
  if (written = write(kmem, buf, sz) == -1) { perror("Write error");
    exit(0);
  }
  return;
}

int main(int argc, char *argv[]) {

  off_t sys_call_table;
  unsigned int addr_ptr, sys_call_number;

  if (argc < 3) {
    return 0;
  }

  kmem=open("/dev/kmem",O_RDWR);

  if(kmem<0){
    perror("Error opening kmem"); return 0;
  }

  sscanf(argv[1], "%x", &sys_call_table); sscanf(argv[2], "%d", &sys_call_number);
  sscanf(argv[3], "%x", &addr_ptr); char buf[256];
  memset (buf, 0, 256); read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("Original value: %02x%02x%02x%02x\n", buf[3], buf[2], buf[1], buf[0]);
  write_kmem2((void*)&addr_ptr,sys_call_table+(sys_call_number*4),4);
  read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("New value: %02x%02x%02x%02x\n", buf[3], buf[2], buf[1], buf[0]);
  close(kmem);

  return 0;
}
```

从 Android 5.0（API 级别 21）开始，所有可执行文件都必须使用 PIE 支持进行编译。使用预构建的工具链构建 kmem_util.c 并将其复制到设备：

```
/tmp/my-android-toolchain/bin/arm-linux-androideabi-gcc -pie -fpie -o kmem_util kmem_util.c
adb push kmem_util /data/local/tmp/
adb shell chmod 755 /data/local/tmp/kmem_util
```

在开始访问内核内存之前，您仍然需要知道系统调用表中的正确偏移量。系统调用在内核源代码中的`openat`unistd.h 中定义：

```
$ grep -r "__NR_openat" arch/arm/include/asm/unistd.h
\#define __NR_openat            (__NR_SYSCALL_BASE+322)
```

拼图的最后一块是您的替换地址 - `openat`。同样，您可以从 /proc/kallsyms 中获取此地址。

```
$ adb shell cat /proc/kallsyms | grep new_openat
bf000000 t new_openat    [kernel_hook]
```

现在您拥有覆盖`sys_call_table`条目所需的一切。kmem_util 的语法是：

```
./kmem_util <syscall_table_base_address> <offset> <func_addr>
```

以下命令修补`openat`系统调用表，使其指向您的新函数。

```
$ adb shell su -c /data/local/tmp/kmem_util c000f984 322 bf000000
Original value: c017a390
New value: bf000000
```

