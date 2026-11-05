# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 7 · part 1

> 分段 1/2。索引见 `Android篡改和逆向工程-p7.md`。

# Android篡改和逆向工程[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#android-tampering-and-reverse-engineering) · part 7

> 分段 7/10。索引见 `Android篡改和逆向工程.md`。

## 承接

    _methods: Object.getOwnPropertyNames(jClass.__proto__).filter(function(m) {
      return !m.startsWith('$') // filter out Frida related special properties
        || m == 'class' || m == 'constructor' // optional
    }),
    _fields: jClass.class.getFields().map(function(f) {
      return( f.toString());
    })
  }, null, 2));
}
```

将脚本保存到名为 java_class_listing.js 的文件后，您可以告诉 Frida CLI 使用标志加载它，`-l`并将其注入到指定的进程 ID 中`-p`。

```
frida -U -l java_class_listing.js -p <pid>

// Output
[Huawei Nexus 6P::sg.vantagepoint.helloworldjni]->
...

com.scottyab.rootbeer.sample.MainActivity
{
  "_name": "com.scottyab.rootbeer.sample.MainActivity",
  "_methods": [
  ...
    "beerView",
    "checkRootImageViewList",
    "floatingActionButton",
    "infoDialog",
    "isRootedText",
    "isRootedTextDisclaimer",
    "mActivity",
    "GITHUB_LINK"
  ],
  "_fields": [
    "public static final int android.app.Activity.DEFAULT_KEYS_DIALER",
...
```

考虑到输出的冗长，可以通过编程方式过滤掉系统类，使输出更具可读性并与用例相关。

##### 获取加载的库[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#getting-loaded-libraries)

您可以使用`Process`命令直接从 Frida CLI 检索进程相关信息。在`Process`命令中，该函数`enumerateModules`列出了加载到进程内存中的库。

```
[Huawei Nexus 6P::sg.vantagepoint.helloworldjni]-> Process.enumerateModules()
[
    {
        "base": "0x558a442000",
        "name": "app_process64",
        "path": "/system/bin/app_process64",
        "size": 32768
    },
    {
        "base": "0x78bc984000",
        "name": "libandroid_runtime.so",
        "path": "/system/lib64/libandroid_runtime.so",
        "size": 2011136
    },
...
```

#### 方法Hook[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#method-hooking)

##### XPOSED[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#xposed)

假设您正在测试一个应用程序，该应用程序在您的 root 设备上顽固地退出。您反编译应用程序并发现以下高度可疑的方法：

```
package com.example.a.b

public static boolean c() {
  int v3 = 0;
  boolean v0 = false;

  String[] v1 = new String[]{"/sbin/", "/system/bin/", "/system/xbin/", "/data/local/xbin/",
    "/data/local/bin/", "/system/sd/xbin/", "/system/bin/failsafe/", "/data/local/"};

    int v2 = v1.length;

    for(int v3 = 0; v3 < v2; v3++) {
      if(new File(String.valueOf(v1[v3]) + "su").exists()) {
         v0 = true;
         return v0;
      }
    }

    return v0;
}
```

此方法遍历目录列表，如果在其中任何目录中找到二进制文件，则返回`true`（设备已根目录） 。`su`像这样的检查很容易停用所有你需要做的就是用返回“false”的东西替换代码。使用 Xposed 模块Hook方法是一种方法（有关 Xposed 安装和基础知识的更多详细信息，请参阅“Android 基本安全测试”）。

该方法 `XposedHelpers.findAndHookMethod`允许您覆盖现有的类方法。通过查看反编译后的源码，可以发现执行检查的方法是`c`. 此方法位于类中`com.example.a.b`。下面是一个 Xposed 模块，它覆盖了函数，因此它总是返回 false：

```
package com.awesome.pentestcompany;

import static de.robv.android.xposed.XposedHelpers.findAndHookMethod;
import de.robv.android.xposed.IXposedHookLoadPackage;
import de.robv.android.xposed.XposedBridge;
import de.robv.android.xposed.XC_MethodHook;
import de.robv.android.xposed.callbacks.XC_LoadPackage.LoadPackageParam;

public class DisableRootCheck implements IXposedHookLoadPackage {

    public void handleLoadPackage(final LoadPackageParam lpparam) throws Throwable {
        if (!lpparam.packageName.equals("com.example.targetapp"))
            return;

        findAndHookMethod("com.example.a.b", lpparam.classLoader, "c", new XC_MethodHook() {
            @Override

            protected void beforeHookedMethod(MethodHookParam param) throws Throwable {
                XposedBridge.log("Caught root check!");
                param.setResult(false);
            }

        });
    }
}
```

就像常规的 Android 应用程序一样，Xposed 模块是使用 Android Studio 开发和部署的。Xposed模块的编写、编译、安装等更多细节，可参考其作者[rovo89](https://www.xda-developers.com/rovo89-updates-on-the-situation-regarding-xposed-for-nougat/)提供的教程。

##### Frida[¶](https://mas.owasp.org/MASTG/Android/0x05c-Reverse-Engineering-and-Tampering/#frida)

我们将使用 Frida 解决[UnCrackable App for Android Level 1](https://mas.owasp.org/MASTG/Tools/0x08b-Reference-Apps/#android-uncrackable-l1)，并演示我们如何轻松绕过 root 检测并从应用程序中提取秘密数据。

当您在模拟器或已获得 root 权限的设备上启动 crackme 应用程序时，您会发现它会显示一个对话框并在您按下“确定”后立即退出，因为它检测到 root：

![img](https://mas.owasp.org/assets/Images/Chapters/0x05c/crackme-frida-1.png)

让我们看看如何防止这种情况发生。

主要方法（使用 CFR 反编译）如下所示：

```
package sg.vantagepoint.uncrackable1;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.os.Bundle;
import android.text.Editable;
import android.view.View;
import android.widget.EditText;
import sg.vantagepoint.a.b;
import sg.vantagepoint.a.c;
import sg.vantagepoint.uncrackable1.a;

public class MainActivity
extends Activity {
    private void a(String string) {
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        alertDialog.setTitle((CharSequence)string);
        alertDialog.setMessage((CharSequence)"This is unacceptable. The app is now going to exit.");
        alertDialog.setButton(-3, (CharSequence)"OK", new DialogInterface.OnClickListener(){

            public void onClick(DialogInterface dialogInterface, int n) {
                System.exit((int)0);
            }
        });
        alertDialog.setCancelable(false);
        alertDialog.show();
    }

    protected void onCreate(Bundle bundle) {
        if (c.a() || c.b() || c.c()) {
            this.a("Root detected!");
        }
        if (b.a(this.getApplicationContext())) {
            this.a("App is debuggable!");
        }
        super.onCreate(bundle);
        this.setContentView(2130903040);
    }

    /*
     * Enabled aggressive block sorting
     */
    public void verify(View object) {
        object = ((EditText)this.findViewById(2130837505)).getText().toString();
        AlertDialog alertDialog = new AlertDialog.Builder((Context)this).create();
        if (a.a((String)object)) {
            alertDialog.setTitle((CharSequence)"Success!");
            object = "This is the correct secret.";
        } else {
            alertDialog.setTitle((CharSequence)"Nope...");
            object = "That's not it. Try again.";
        }
        alertDialog.setMessage((CharSequence)object);
        alertDialog.setButton(-3, (CharSequence)"OK", new DialogInterface.OnClickListener(){

            public void onClick(DialogInterface dialogInterface, int n) {
                dialogInterface.dismiss();
            }
        });
        alertDialog.show();
    }
}
```

请注意方法中的“Root detected”消息`onCreate`和前面语句中调用的各种方法`if`（执行实际的根检查）。还要注意来自类的第一个方法的“这是不可接受的...”消息`private void a`。显然，这个方法显示对话框。方法调用中有一个`alertDialog.onClickListener`回调集，它在成功检测`setButton`到根后关闭应用程序。使用 Frida，您可以通过Hook方法或其中的回调`System.exit`来防止应用程序退出。`MainActivity.a`下面的示例显示了如何Hook`MainActivity.a`并防止它结束应用程序。

```
setImmediate(function() { //prevent timeout
    console.log("[*] Starting script");

    Java.perform(function() {
      var mainActivity = Java.use("sg.vantagepoint.uncrackable1.MainActivity");
      mainActivity.a.implementation = function(v) {
         console.log("[*] MainActivity.a called");
      };
      console.log("[*] MainActivity.a modified");

    });
});
```

将您的代码包装在函数`setImmediate`中以防止超时（您可能需要也可能不需要这样做），然后调用`Java.perform`以使用 Frida 的方法来处理 Java。然后检索类的包装器`MainActivity`并覆盖其`a`方法。与原始版本不同，新版本`a`仅写入控制台输出并且不会退出应用程序。另一种解决方案是Hook接口`onClick`的方法`OnClickListener`。您可以覆盖该`onClick`方法并防止它通过`System.exit`调用结束应用程序。如果您想注入自己的 Frida 脚本，它应该`AlertDialog`完全禁用或更改该`onClick`方法的行为，以便在您单击“确定”时应用程序不会退出。

将上面的脚本另存为`uncrackable1.js`并加载它：

```
frida -U -f owasp.mstg.uncrackable1 -l uncrackable1.js --no-pause
```

在您看到“MainActivity.a modified”消息后，应用程序将不再退出。

您现在可以尝试输入“秘密字符串”。但是你从哪里得到它？

如果您查看 class `sg.vantagepoint.uncrackable1.a`，您可以看到与您的输入进行比较的加密字符串：

```
package sg.vantagepoint.uncrackable1;

import android.util.Base64;
import android.util.Log;

public class a {
    public static boolean a(String string) {

        byte[] arrby = Base64.decode((String)"5UJiFctbmgbDoLXmpL12mkno8HT4Lv8dlat8FxR2GOc=", (int)0);

        try {
            arrby = sg.vantagepoint.a.a.a(a.b("8d127684cbc37c17616d806cf50473cc"), arrby);
        }
        catch (Exception exception) {
            StringBuilder stringBuilder = new StringBuilder();
            stringBuilder.append("AES error:");
            stringBuilder.append(exception.getMessage());
            Log.d((String)"CodeCheck", (String)stringBuilder.toString());
            arrby = new byte[]{};
        }
        return string.equals((Object)new String(arrby));
    }

    public static byte[] b(String string) {
        int n = string.length();
        byte[] arrby = new byte[n / 2];
        for (int i = 0; i < n; i += 2) {
            arrby[i / 2] = (byte)((Character.digit((char)string.charAt(i), (int)16) << 4) + Character.digit((char)string.charAt(i + 1), (int)16));
        }
        return arrby;
    }
}
```

