# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 3 · part 1

> 分段 1/2。索引见 `Android平台API-p3.md`。

# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 3

> 分段 3/8。索引见 `Android平台API.md`。

## 承接

public class MainActivity extends PreferenceActivity {
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
```

我的片段类

```
public class MyFragment extends Fragment {
    public void onCreate (Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
    public View onCreateView(LayoutInflater inflater, ViewGroup container, Bundle savedInstanceState) {
        View v = inflater.inflate(R.layout.fragmentLayout, null);
        WebView myWebView = (WebView) wv.findViewById(R.id.webview);
        myWebView.getSettings().setJavaScriptEnabled(true);
        myWebView.loadUrl(this.getActivity().getIntent().getDataString());
        return v;
    }
}
```

要利用此易受攻击的 Activity，您可以使用以下代码创建一个应用程序：

```
Intent i = new Intent();
i.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK);
i.setClassName("pt.claudio.insecurefragment","pt.claudio.insecurefragment.MainActivity");
i.putExtra(":android:show_fragment","pt.claudio.insecurefragment.MyFragment");
i.setData(Uri.parse("https://security.claudio.pt"));
startActivity(i);
```

[Vulnerable App](https://github.com/clviper/android-fragment-injection/raw/master/vulnerableapp.apk)和Exploit [PoC App](https://github.com/clviper/android-fragment-injection/blob/master/exploit.apk)可供下载。

## 在 WebView 中测试 URL 加载 (MSTG-PLATFORM-2)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-for-url-loading-in-webviews-mstg-platform-2)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_3)

WebView 是 Android 的嵌入式组件，允许您的应用程序在您的应用程序中打开网页。除了与移动应用程序相关的威胁之外，WebViews 还可能使您的应用程序面临常见的网络威胁（例如 XSS、Open Redirect 等）。

测试 WebView 时要做的最重要的事情之一是确保只能在其中加载受信任的内容。任何新加载的页面都可能具有潜在的恶意，请尝试利用任何 WebView 绑定或尝试对用户进行网络钓鱼。除非您正在开发浏览器应用程序，否则通常您希望将加载的页面限制在您的应用程序的域中。一个好的做法是阻止用户甚至有机会在 WebViews 中输入任何 URL（这是 Android 上的默认设置）或导航到受信任的域之外。即使在受信任的域上导航时，仍然存在用户可能会遇到并单击指向不可信内容的其他链接的风险（例如，如果该页面允许其他用户发表评论）。此外，一些开发人员甚至可能会覆盖一些对用户有潜在危险的默认行为。有关详细信息，请参阅下面的静态分析部分。

#### 安全浏览 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#safebrowsing-api)

为了提供更安全的网络浏览体验，Android 8.1（API 级别 27）引入了[`SafeBrowsing API`](https://developers.google.com/safe-browsing/v4)，它允许您的应用程序检测 Google 已归类为已知威胁的 URL。

默认情况下，WebView 会向用户显示有关安全风险的警告，并提供加载 URL 或停止加载页面的选项。使用 SafeBrowsing API，您可以通过向 SafeBrowsing 报告威胁或执行特定操作（例如每次遇到已知威胁时返回安全状态）来自定义应用程序的行为。请查看[Android 开发者文档](https://developer.android.com/about/versions/oreo/android-8.1#safebrowsing)以获取使用示例。

您可以使用[SafetyNet 库](https://developer.android.com/training/safetynet/safebrowsing)独立于 WebView 使用 SafeBrowsing API ，该库实现了安全浏览网络协议 v4 的客户端。SafetyNet 允许您分析您的应用程序应该加载的所有 URL。您可以检查具有不同方案（例如 http、文件）的 URL，因为 SafeBrowsing 不了解 URL 方案`TYPE_POTENTIALLY_HARMFUL_APPLICATION`以及`TYPE_SOCIAL_ENGINEERING`威胁类型。

#### Virus Total API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#virus-total-api)

Virus Total 提供了一个 API，用于分析已知威胁的 URL 和本地文件。API 参考在[Virus Total 开发者页面](https://developers.virustotal.com/reference#getting-started)上可用。

> 发送要检查已知威胁的 URL 或文件时，请确保它们不包含可能危及用户隐私或暴露应用程序敏感内容的敏感数据。

### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_2)

正如我们之前提到的，应该仔细分析[处理页面导航](https://developer.android.com/guide/webapps/webview#HandlingNavigation)，尤其是当用户可能能够离开受信任的环境时。Android 上默认且最安全的行为是让默认网络浏览器打开用户可能在 WebView 中单击的任何链接。但是，可以通过配置`WebViewClient`允许导航请求由应用程序本身处理的 a 来修改此默认逻辑。如果是这种情况，请务必搜索并检查以下拦截回调函数：

- `shouldOverrideUrlLoading`允许您的应用程序通过返回来中止加载带有可疑内容`true`的 WebView，或者通过返回来允许 WebView 加载 URL `false`。注意事项：
- POST 请求不会调用此方法。
- 不会为 XmlHttpRequests、iFrames、HTML 或`<script>`标记中包含的“src”属性调用此方法。相反，`shouldInterceptRequest`应该注意这一点。
- `shouldInterceptRequest`允许应用程序从资源请求中返回数据。如果返回值为 null，WebView 将照常继续加载资源。否则，使用该`shouldInterceptRequest`方法返回的数据。注意事项：
- 为各种 URL 方案（例如 、 、 等）调用此回调，`http(s):`而不仅仅是那些通过网络发送请求的方案。`data:``file:`
- 这不是针对URL`javascript:`或通过 URL 访问的`blob:`资产。在重定向的情况下，这只会为初始资源 URL 调用，而不是任何后续的重定向 URL。`file:///android_asset/``file:///android_res/`
- 启用安全浏览后，这些 URL 仍会接受安全浏览检查，但开发人员可以通过回调允许 URL`setSafeBrowsingWhitelist`甚至忽略警告。`onSafeBrowsingHit`

如您所见，在测试配置了 WebViewClient 的 WebView 的安全性时需要考虑很多要点，因此请务必通过查看[`WebViewClient`文档](https://developer.android.com/reference/android/webkit/WebViewClient)仔细阅读并理解所有这些要点。

虽然默认值为`EnableSafeBrowsing`，`true`但某些应用程序可能会选择禁用它。要验证 SafeBrowsing 是否已启用，请检查 AndroidManifest.xml 文件并确保不存在以下配置：

```
<manifest>
    <application>
        <meta-data android:name="android.webkit.WebView.EnableSafeBrowsing"
                   android:value="false" />
        ...
    </application>
</manifest>
```

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_2)

动态测试深度链接的一种便捷方法是使用 Frida 或 frida-trace 并在使用应用程序并单击 WebView 中的链接时挂接`shouldOverrideUrlLoading`,方法。`shouldInterceptRequest`确保还Hook其他相关[`Uri`](https://developer.android.com/reference/android/net/Uri)方法，例如`getHost`，`getScheme`或`getPath`通常用于检查请求并匹配已知模式或拒绝列表的方法。

## 测试深层链接 (MSTG-PLATFORM-3)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links-mstg-platform-3)

### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_4)

*深层链接*是将用户直接带到应用程序中特定内容的任何方案的 URI。应用程序可以通过在 Android Manifest 上添加*意图过滤器*并从传入的意图中提取数据来将用户导航到正确的活动来[设置深层链接。](https://developer.android.com/training/app-links/deep-linking)

Android 支持两种类型的深层链接：

- **自定义 URL 方案**，它们是使用任何自定义 URL 方案的深层链接，例如`myapp://`（未经操作系统验证）。
- **Android 应用程序链接**（Android 6.0（API 级别 23）及更高版本），它们是使用`http://`和`https://`方案并包含`autoVerify`属性（触发操作系统验证）的深层链接。

#### 深度链接冲突[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#deep-link-collision)

使用未经验证的深层链接可能会导致严重问题 - 安装在用户设备上的任何其他应用程序都可以声明并尝试处理相同的意图，这被称为**深层链接冲突**。任何任意应用程序都可以声明对属于另一个应用程序的完全相同的深层链接的控制权。

在最新版本的 Android 中，这会导致向用户显示一个所谓的*消歧对话框*，要求他们选择应该处理深层链接的应用程序。用户可能会错误地选择恶意应用程序而不是合法应用程序。

![img](https://mas.owasp.org/assets/Images/Chapters/0x05h/app-disambiguation.png)

#### Android应用链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-links)

为了解决深度链接冲突问题，Android 6.0（API 级别 23）引入了[**Android App Links**](https://developer.android.com/training/app-links)，这是基于开发者明确注册的网站 URL[验证的深度链接。](https://developer.android.com/training/app-links/verify-site-associations)单击应用程序链接将立即打开已安装的应用程序。

与未经验证的深层链接有一些关键区别：

- App Links 仅使用`http://`和`https://`方案，不允许任何其他自定义 URL 方案。
- 应用程序链接需要一个实时域才能通过 HTTPS提供[数字资产链接文件。](https://developers.google.com/digital-asset-links/v1/getting-started)
- 应用链接不会遭受深度链接冲突，因为当用户打开它们时它们不会显示消歧对话框。

#### 测试深层链接[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-deep-links)

任何现有的深层链接（包括应用链接）都可能增加应用的攻击面。这[包括许多风险](https://people.cs.vt.edu/gangwang/deep17.pdf)，例如链接劫持、敏感功能暴露等。应用程序运行的 Android 版本也会影响风险：

