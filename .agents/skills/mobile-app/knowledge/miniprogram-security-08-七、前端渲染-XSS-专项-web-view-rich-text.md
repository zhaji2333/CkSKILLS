# 七、前端渲染 XSS 专项（web-view / rich-text）

> 来源：CkSKILLS v1 `miniprogram-security` §七、前端渲染 XSS 专项（web-view / rich-text）（迁移至 v2 知识块）

**web-view**
- `src` 可控 → 加载任意 URL（钓鱼/恶意页面）；`src` 域名白名单可绕过（相似域名、URL 解析差异）
- 与 APP 内 WebView 同源风险：加载官方域页面 + JSBridge 注入（联动 `xss-frontend-security` 跳转型 XSS）

**rich-text**
- `nodes` 属性渲染 HTML 无净化 → `<img onerror>` / `<a href="javascript:">` 在 webview 内执行
- AI 输出/聊天记录进 rich-text 渲染 → AI 输出型存储 XSS（联动 `xss-frontend-security` 四 + `ai-llm-agent-security` 3.6）

**JSBridge / postMessage**
- `wx.miniProgram.postMessage` 到 App 端消息处理无白名单
- `navigateToMiniProgram` 参数注入（跳转任意小程序）

---
