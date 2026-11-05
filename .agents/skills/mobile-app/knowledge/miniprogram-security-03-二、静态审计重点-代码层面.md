# 二、静态审计重点（代码层面）

> 来源：CkSKILLS v1 `miniprogram-security` §二、静态审计重点（代码层面）（迁移至 v2 知识块）

**app.js / 全局逻辑**
- 全局接口封装、请求拦截器（看统一鉴权头怎么带的：token？openid？自定义签名？）
- 登录流程：`wx.login()` → code → 后端换 session/token 的完整链路
- 全局变量：appid、环境 env、后台域名、加密密钥

**敏感信息（重点上报项，联动 `recon-js-analysis`）**
- `appid`（正常）、**`appsecret` 出现在前端 = 配置错误/泄露**（后端才应持有）→ 上报并深挖（可换取 access_token 调接口）
- 云开发 env ID、腾讯云 SecretId/SecretKey、OSS/存储桶密钥、内网/后台域名
- 提取的 URL/IP/域名 → 提醒用户关注：可能是 APP/小程序后台接口，进入资产测绘

**接口清单提取**
- `wx.request({url: ...})` / `wx.cloud.callFunction({name: ...})` / `request(` 全部列出
- 参数结构、鉴权方式（header 里的 token/自定义头）、加密参数
- 隐藏接口：注释掉的、条件分支里的、旧版本接口

**渲染与组件**
- `web-view` 组件的 `src` 是否可控
- `rich-text` 组件的 `nodes` 是否渲染用户/AI 输入（XSS）
- 自定义 JSBridge / `wx.miniProgram.postMessage`、`navigateToMiniProgram` 跳转参数

---
