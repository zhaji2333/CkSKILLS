# Android 平台 API[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#android-platform-apis) · part 7 · part 2

> 分段 2/2。索引见 `Android平台API-p7.md`。

#### 可包裹[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#parcelable_1)

当敏感信息通过包含 Parcelable 的 Bundle 存储在 Intent 中时，请确保采取适当的安全措施。使用应用程序级 IPC（例如，签名验证、意图权限、加密）时，使用显式意图并验证适当的附加安全控制。

### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_8)

有几种执行动态分析的方法：

1. 对于实际的持久性：使用数据存储一章中描述的技术。
2. 对于基于反射的方法：使用 Xposed Hook到反序列化方法或向序列化对象添加不可处理的信息以查看它们是如何处理的（例如，应用程序是否崩溃或可以通过丰富对象来提取额外信息）。

### 测试 WebViews 清理 (MSTG-PLATFORM-10)[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#testing-webviews-cleanup-mstg-platform-10)

#### 概述[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#overview_10)

当应用程序访问 WebView 中的任何敏感数据时，清除 WebView 资源是至关重要的一步。这包括本地存储的任何文件、RAM 缓存和任何加载的 JavaScript。

作为一项附加措施，您可以使用服务器端标头（例如`no-cache`）来防止应用程序缓存特定内容。

> 从 Android 10（API 级别 29）开始，应用程序能够检测 WebView 是否变得[无响应](https://developer.android.com/about/versions/10/features?hl=en#webview-hung)。如果发生这种情况，操作系统将自动调用该`onRenderProcessUnresponsive`方法。

[在Android Developers](https://developer.android.com/training/articles/security-tips?hl=en#WebView)上使用 WebView 时，您可以找到更多安全最佳实践。

#### 静态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#static-analysis_9)

应用程序可以在几个区域删除 WebView 相关数据。您应该检查所有相关的 API 并尝试全面跟踪数据删除。

- **Web 视图 API**：

- **初始化**`setDomStorageEnabled`：应用程序可能会以某种方式初始化 WebView ，以避免使用`setAppCacheEnabled`或`setDatabaseEnabled`from存储某些信息[`android.webkit.WebSettings`](https://developer.android.com/reference/android/webkit/WebSettings)。默认情况下禁用 DOM 存储（用于使用 HTML5 本地存储）、应用程序缓存和数据库存储 API，但应用程序可能会将这些设置明确设置为“true”。

- **缓存**：Android 的 WebView 类提供了[`clearCache`](https://developer.android.com/reference/android/webkit/WebView#clearCache(boolean))可用于清除应用程序使用的所有 WebView 的缓存的方法。它接收一个布尔输入参数 ( `includeDiskFiles`)，它将擦除所有存储的资源，包括 RAM 缓存。但是，如果它设置为 false，它只会清除 RAM 缓存。检查源代码以了解该`clearCache`方法的用法并验证其输入参数。此外，您还可以检查应用程序是否覆盖`onRenderProcessUnresponsive`了 WebView 可能变得无响应的情况，因为该`clearCache`方法也可能从那里调用。

- **WebStorage APIs**：[`WebStorage.deleteAllData`](https://developer.android.com/reference/android/webkit/WebStorage#deleteAllData)也可用于清除当前被 JavaScript 存储 APIs 使用的所有存储，包括 Web SQL 数据库和 HTML5 Web Storage APIs。

  > 一些应用程序*需要*启用 DOM 存储才能显示一些使用本地存储的 HTML5 网站。这应该仔细调查，因为这可能包含敏感数据。

- **Cookies**：可以使用[CookieManager.removeAllCookies](https://developer.android.com/reference/android/webkit/CookieManager#removeAllCookies(android.webkit.ValueCallback))删除任何现有的 cookies 。

- **文件 API**：在某些目录中正确删除数据可能不是那么简单，一些应用程序使用实用的解决方案，即*手动*删除已知保存用户数据的选定目录。这可以使用`java.io.File`API 来完成，例如[`java.io.File.deleteRecursively`](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io/java.io.-file/delete-recursively.html).

**例子：**

这个来自[开源 Firefox Focus](https://github.com/mozilla-mobile/focus-android/blob/v8.17.1/app/src/main/java/org/mozilla/focus/webview/SystemWebView.kt#L220)应用程序的 Kotlin 示例显示了不同的清理步骤：

```
override fun cleanup() {
        clearFormData() // Removes the autocomplete popup from the currently focused form field, if present. Note this only affects the display of the autocomplete popup, it does not remove any saved form data from this WebView's store. To do that, use WebViewDatabase#clearFormData.
        clearHistory()
        clearMatches()
        clearSslPreferences()
        clearCache(true)

        CookieManager.getInstance().removeAllCookies(null)

        WebStorage.getInstance().deleteAllData() // Clears all storage currently being used by the JavaScript storage APIs. This includes the Application Cache, Web SQL Database and the HTML5 Web Storage APIs.

        val webViewDatabase = WebViewDatabase.getInstance(context)
        // It isn't entirely clear how this differs from WebView.clearFormData()
        @Suppress("DEPRECATION")
        webViewDatabase.clearFormData() // Clears any saved data for web forms.
        webViewDatabase.clearHttpAuthUsernamePassword()

        deleteContentFromKnownLocations(context) // calls FileUtils.deleteWebViewDirectory(context) which deletes all content in "app_webview".
    }
```

该函数以一些额外的*手动*文件删除结束，`deleteContentFromKnownLocations`其中从[`FileUtils`](https://github.com/mozilla-mobile/focus-android/blob/v8.17.1/app/src/main/java/org/mozilla/focus/utils/FileUtils.kt). 这些函数使用[`java.io.File.deleteRecursively`](https://kotlinlang.org/api/latest/jvm/stdlib/kotlin.io/java.io.-file/delete-recursively.html)方法递归地从指定目录中删除文件。

```
private fun deleteContent(directory: File, doNotEraseWhitelist: Set<String> = emptySet()): Boolean {
    val filesToDelete = directory.listFiles()?.filter { !doNotEraseWhitelist.contains(it.name) } ?: return false
    return filesToDelete.all { it.deleteRecursively() }
}
```

#### 动态分析[¶](https://mas.owasp.org/MASTG/Android/0x05h-Testing-Platform-Interaction/#dynamic-analysis_9)

