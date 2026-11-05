# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 8 · part 2

> 分段 2/2。索引见 `Android平台API-p8.md`。

为了测试是否正确更新：尝试下载具有安全漏洞的旧版本应用程序，可以通过开发人员发布的版本或使用第三方应用程序商店。接下来，验证您是否可以在不更新应用程序的情况下继续使用该应用程序。如果给出了更新提示，请通过取消提示或以其他方式通过正常的应用程序使用来规避它来验证您是否仍然可以使用该应用程序。这包括验证后端是否会停止调用易受攻击的后端和/或易受攻击的应用程序版本本身是否被后端阻止。最后，看看您是否可以使用中间人应用程序的版本号，看看后端如何对此做出响应（例如，它是否被记录下来）。

## 参考[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#references)

### Android App Bundle 和更新[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-bundles-and-updates)

- https://developer.android.com/guide/app-bundle/in-app-updates

### Android片段注入[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-fragment-injection)

- https://www.synopsys.com/blogs/software-security/fragment-injection/
- https://securityintelligence.com/wp-content/uploads/2013/12/android-collapses-into-fragments.pdf

### Android权限文档[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-permissions-documentation)

- https://developer.android.com/training/permissions/usage-notes
- https://developer.android.com/training/permissions/requesting#java
- https://developer.android.com/guide/topics/permissions/overview#permission-groups
- https://developer.android.com/guide/topics/manifest/provider-element#gprmsn
- [https://developer.android.com/reference/android/content/Context#revokeUriPermission(android.net.Uri,%20int)](https://developer.android.com/reference/android/content/Context#revokeUriPermission(android.net.Uri, int))
- [https://developer.android.com/reference/android/content/Context#checkUriPermission(android.net.Uri,%20int,%20int,%20int)](https://developer.android.com/reference/android/content/Context#checkUriPermission(android.net.Uri, int, int, int))
- https://developer.android.com/guide/components/broadcasts#restricting_broadcasts_with_permissions
- https://developer.android.com/guide/topics/permissions/overview
- https://developer.android.com/guide/topics/manifest/manifest-intro#filestruct

### Android 捆绑包和即时应用[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-bundles-and-instant-apps)

- https://developer.android.com/topic/google-play-instant/getting-started/instant-enabled-app-bundle
- https://developer.android.com/topic/google-play-instant/guides/multiple-entry-points
- https://developer.android.com/studio/projects/dynamic-delivery

### Android 8 中的 Android 权限更改[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-permissions-changes-in-android-8)

- https://developer.android.com/about/versions/oreo/android-8.0-changes

### Android WebViews 和安全浏览[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-webviews-and-safebrowsing)

- https://developer.android.com/training/articles/security-tips#WebView
- https://developer.android.com/guide/webapps/managing-webview#safe-browsing
- https://developer.android.com/about/versions/oreo/android-8.1#safebrowsing
- https://support.virustotal.com/hc/en-us/articles/115002146549-Mobile-Apps

### Android 自定义 URL 方案[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-custom-url-schemes)

- https://developer.android.com/training/app-links/
- https://developer.android.com/training/app-links/deep-linking
- https://developer.android.com/training/app-links/verify-site-associations
- https://developers.google.com/digital-asset-links/v1/getting-started
- https://pdfs.semanticscholar.org/0415/59c01d5235f8cf38a3c69ccee7e1f1a98067.pdf

### Android应用程序通知[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-app-notifications)

- https://developer.android.com/guide/topics/ui/notifiers/notifications
- https://developer.android.com/training/notify-user/build-notification
- https://developer.android.com/reference/android/service/notification/NotificationListenerService
- https://medium.com/csis-techblog/analysis-of-joker-a-spy-premium-subscription-bot-on-googleplay-9ad24f044451

### OWASP MASVS[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#owasp-masvs)

- MSTG-PLATFORM-1：“该应用程序仅请求必要的最少权限集。”
- MSTG-PLATFORM-2：“来自外部来源和用户的所有输入都经过验证，并在必要时进行清理。这包括通过 UI、IPC 机制（如意图、自定义 URL 和网络来源）接收的数据。”
- MSTG-PLATFORM-3：“该应用程序不会通过自定义 URL 方案导出敏感功能，除非这些机制得到适当保护。”
- MSTG-PLATFORM-4：“该应用程序不会通过 IPC 设施导出敏感功能，除非这些机制得到适当保护。”
- MSTG-PLATFORM-5：“除非明确要求，否则 JavaScript 在 WebView 中被禁用。”
- MSTG-PLATFORM-6：“WebViews 配置为仅允许所需的最小协议处理程序集（理想情况下，仅支持 https）。禁用潜在危险的处理程序，例如文件、电话和应用程序 ID。”
- MSTG-PLATFORM-7：“如果应用程序的Native方法暴露给 WebView，请验证 WebView 仅呈现应用程序包中包含的 JavaScript。”
- MSTG-PLATFORM-8：“对象序列化（如果有的话）是使用安全序列化 API 实现的。”
- MSTG-PLATFORM-10：“在销毁 WebView 之前，应清除 WebView 的缓存、存储和加载的资源（JavaScript 等）。”
- MSTG-ARCH-9：“存在强制更新移动应用程序的机制。”
