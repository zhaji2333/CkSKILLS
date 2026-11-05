# 二、静态分析 · part 1 · part 2

> 分段 2/2。索引见 `android-security-audit-06-二、静态分析-r1.md`。

**漏洞判定**
- 成功调用系统级方法（读写系统数据、修改设置）→ **高危**
- 成功调用特权操作（安装应用、访问受保护资源）→ **严重**

**导出 Service 的 Bound 模式**
- 搜索 exported Service 的 `onBind()` 返回的 IBinder，从受害 App 提取 AIDL，在 PoC App 中 `bindService()` 后逐个调用接口方法（攻击面远大于 Started Service）。

**SELinux 域感知**
- 审计系统 App 时检查 SELinux domain：`system_app` / `platform_app` / `priv_app` / `untrusted_app`，不同 domain 的 allow 规则差异直接影响漏洞利用范围。

```bash
adb shell ps -Z | grep <package>
```

---

### 2.10 Deep Link 安全（可产出中危~高危）

```bash
grep -A5 "android:scheme\|android:host\|android:autoVerify" /tmp/apktool_out/AndroidManifest.xml
grep -rn "getIntent().getData\|getScheme\|getHost\|getQueryParameter" /tmp/jadx_out/sources/
```

**Deep Link → 内部功能触发**
- URI 的 host、path、query 参数是否有白名单校验。

**验证步骤**
```bash
adb shell am start -a android.intent.action.VIEW -d "myapp://path?param=payload"
```

**Deep Link → WebView URL 注入链（远程攻击，评级更高）**
- Deep Link 处理中是否将 URI 参数传给 `WebView.loadUrl()` → 攻击者通过浏览器点击链接远程触发 WebView 加载任意页面。
- 典型链路：`myapp://webview?url=https://attacker.com` → 取出 `url` 参数 → `webView.loadUrl(url)`。

**验证步骤**
```bash
adb shell am start -a android.intent.action.VIEW \
  -d "myapp://webview?url=file:///data/data/com.victim/databases/private.db"
```

**漏洞判定**
- 远程触发 WebView 加载任意 URL / 远程读取沙箱文件 → **高危**
- 本地触发内部功能 → **中危**

**Deep Link → Intent 重定向**
- Deep Link 处理中是否根据 URI 参数构造 Intent 并 `startActivity()` → 成功启动未导出组件 → **高危**。

**App Links 配置**
- `android:autoVerify="true"` 未配置时可被恶意 App 抢注相同 scheme+host → **低危**。

**远程验证（恶意 HTML，无需额外脚本）**
```html
<!-- deeplink_poc.html：发送到目标手机，浏览器打开即可 -->
<a href="myapp://path?param=payload">点击触发</a>
<script>location.href = "myapp://webview?url=file:///data/data/com.victim/databases/private.db";</script>
```

---

### 2.11 SSRF 与网络请求安全（可产出中危~高危）

```bash
grep -rn "URL()\|HttpURLConnection\|OkHttpClient\|Retrofit\|openConnection" /tmp/jadx_out/sources/ | \
  grep -i "getIntent\|getExtra\|getData\|getQueryParam"
```

**SSRF**
- 请求 URL 来自外部输入（Intent extras、Deep Link 参数）时，攻击者可指向 `http://127.0.0.1`、`http://10.0.0.1`、云元数据 `http://169.254.169.254`。

**验证步骤**
```bash
adb shell am start -n com.victim/.VulnActivity --es url "http://169.254.169.254/latest/meta-data/"
```

**漏洞判定**
- 成功访问云元数据 → **高危**
- 成功访问内网服务 → **中危**

**内网地址过滤绕过**
- 十六进制 IP `0x7f000001`、八进制 `0177.0.0.1`、IPv6 `[::1]`、DNS rebinding、302 重定向到内网地址。

**WebView 中的 SSRF**
- WebView 加载 URL 可控 + 自定义 `shouldInterceptRequest()` → 检查拦截逻辑是否将请求转发到 App 后端。

---

### 2.12 WebView JSBridge 安全（可产出中危~严重）

```bash
