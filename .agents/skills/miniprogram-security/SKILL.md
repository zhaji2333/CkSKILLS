---
name: miniprogram-security
description: 当目标为微信/支付宝/抖音/百度等小程序（含微信云开发/云函数）、需要小程序包获取与反编译、appid/appsecret/接口提取、微信登录链/支付/越权/WebView/rich-text 渲染/云开发漏洞挖掘时调用。负责小程序全生命周期深度挖掘：包还原 → 代码审计 → 接口与密钥提取 → 登录/支付/越权/渲染/云开发专项 → 验证要点。命中场景：openid 替换越权、code 登录绕过、支付金额篡改、云函数未授权、web-view/rich-text XSS。
---

# miniprogram-security — 小程序专项深度挖掘

> **与 `android-security-audit` 的分工**：本技能专注 **小程序（微信/支付宝/抖音/百度）与微信云开发**；Android APK 组件安全见 `android-security-audit`。小程序与 APP 后台接口常同源，两技能可联动：先从 APP/小程序提取后端域名，再统一测接口。

## 何时调用（触发条件）

- 目标是微信/支付宝/抖音/百度/QQ 小程序
- 拿到小程序包（.wxapkg / 分包 / 反编译产物），需要还原源码
- 需要提取接口清单、appid/appsecret、云开发配置、加密/签名逻辑
- 发现微信登录链（wx.login code）、支付、openid/用户 ID 可控、未授权接口
- 发现 web-view / rich-text / JSBridge / 分享跳转 等前端渲染点
- 目标是微信云开发（云函数/云数据库/云存储）

## 快速开始（5 分钟出第一个接口/凭证）

```bash
# Step 1: 定位小程序包（PC 微信缓存目录）
# 微信/WeChat Files/Applet/<appid>/ 下 *.wxapkg（含分包）
# 或开发者工具/手机抓包/第三方平台获取

# Step 2: 反编译
# wxappUnpacker / unveilr / CrackMinApp 解包，得到 app.js、app.json、pages/、utils/、cloudfunctions/

# Step 3: 提取敏感信息与接口（高优先级）
grep -rniE "appid|appsecret|secret|access_key|secret_key|token" <解包目录>/
grep -rEoh "https?://[a-zA-Z0-9._/-]+" <解包目录>/ | sort -u          # 后端/业务域名
grep -rn "wx.request|wx.cloud.callFunction|request\(" <解包目录>/ | head -50  # 接口与云函数

# Step 4: 优先验证
# openid 可控 → 替换他人 openid 测越权；登录 code → 重放/替换；支付参数 → 金额篡改
```

---

## 一、包获取与反编译

**获取途径**
- **PC 微信**：`WeChat Files/Applet/<appid>/` 下 `.wxapkg` 缓存（主包+分包），需先在小程序里打开过
- **微信开发者工具**：导入源码调试（拿到项目源码的场景）
- **手机抓包**：HTTP(S) 代理 + 小程序包下载接口（配合证书安装）
- **第三方平台**：小程序包下载站、GitHub 泄露、历史版本
- **其他平台**：支付宝（.axml）、抖音、百度（.swan）结构类似，解包工具对应适配

**反编译工具**
```
wxappUnpacker        # 经典解包，还原 app.js/pages 结构
unveilr              # 较新，支持分包/新版格式
CrackMinApp          # 微信小程序一键解包
```
- 解包产物结构：`app.js`（全局逻辑）、`app.json`（页面/权限配置）、`pages/*`（页面）、`utils/*`、`project.config.json`、`cloudfunctions/`（云函数目录）
- 新版分包需先解主包再按 `app.json` 的 `subpackages` 配置逐分包解
- 压缩混淆的 JS：先用 js-beautify/反混淆还原，再搜索关键字

**还原度确认**：解包后核对 `app.json` 页面数与线上功能是否对应，确认还原完整再开始审计。

---

## 二、静态审计重点（代码层面）

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

## 三、场景表（漏洞全景）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 微信登录链 | 登录绕过/任意用户登录 | code→session_key→凭证；openid 参数可控、code 重放、session_key 泄露 |
| 支付/订单/退款 | 金额篡改/重复支付/回调绕过 | 下单金额参数可控、回调验签缺失、重复回调、退款金额 |
| 越权/IDOR | openid/用户 ID 替换 | 接口凭证绑定不严、ID 可遍历 |
| 未授权接口 | 敏感数据批量泄露 | 接口无鉴权/鉴权可绕过 |
| web-view | 任意 URL 加载/钓鱼 | src 可控、无域名白名单 |
| rich-text | XSS | nodes 渲染 HTML 无净化（含 AI 输出，联动 `xss-frontend-security`） |
| JSBridge/postMessage | 敏感能力调用 | 无白名单校验 |
| 云开发 | 云函数未授权/数据越权 | callFunction 任意调用、云数据库权限过大、云存储公开 |
| 本地存储 | 敏感信息泄露 | wx.setStorage 明文 token/密钥/手机号 |
| 分享/跳转 | 开放重定向/钓鱼 | 分享参数可控、navigateToMiniProgram 参数注入 |
| 获取用户信息 | 凭证泄露 | getPhoneNumber/getUserProfile 返回值被滥用/回显 |
| 短信/验证码 | 轰炸/绕过 | 无频率限制、验证码可绕过（与 `auth-access-control` 联动） |

---

## 四、微信登录链专项（最经典，先测）

**正常流程**：`wx.login()` 拿 `code` → 后端调 `code2session` 换 `openid/session_key` → 返回自定义 token。

**攻击面（按优先级）**
1. **openid 参数可控**（最常出洞）：后端把 `openid` 当请求参数接收（`{"openid":"xxx"}` 直接换 token）→ 填他人 openid = **任意用户登录**
2. **code 重放**：同一 code 可多次换取 token；code 未绑定会话/设备
3. **session_key 泄露**：后端把 session_key 返回给前端 → 可解密手机号等敏感数据
4. **token 可篡改**：自定义 token 里含 openid/user_id 明文可改（JWT 弱密钥/无签名，联动 `auth-access-control`）
5. **注册即登录**：注册接口直接返回已登录态，可批量注册撞已有 openid

**验证方法**
```
正常：自己的 code 登录 → 拿 token
A/B：把请求里的 openid 换成 B 的 → 若拿到 B 的会话/数据 → 任意用户登录/越权成立
重放：同一个 code 发两次 → 两次都能拿 token → 重放成立
```

---

## 五、支付逻辑专项

- **下单金额**：`total_fee`/`amount` 参数可控、负数、0.01、类型混淆
- **回调验签**：支付回调 `notify` 是否验签（MD5/签名比对）；不验签 → 伪造支付成功通知
- **重复回调**：同订单重复通知、幂等缺失 → 重复发货/重复入账
- **退款**：退款金额/次数可控、退款到他人账户
- **签名机制**：参数拼接 + appsecret 签名，参数顺序/编码差异绕过（与 `business-logic-race` / `auth-access-control` 联动）

---

## 六、云开发/云函数专项

- **云函数未鉴权**：`wx.cloud.callFunction({name:"任意函数名"})` 直接调用，函数内无 `cloud.getWXContext().OPENID` 身份校验 → 任意用户调管理员逻辑
- **云数据库权限**：默认权限（所有用户可读/可写）、`where` 条件可控 → 读他人数据、改他人记录
- **云存储**：公开读桶、可列举对象
- **环境切换**：env ID 可控 → 跨环境访问
- 验证：`wx.cloud.callFunction` 用他人 openid 上下文调用敏感函数，看是否拒绝

---

## 七、前端渲染 XSS 专项（web-view / rich-text）

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

## 八、分享/跳转专项

- 分享链接/卡片参数可控 → 开放重定向、钓鱼、参数注入
- 页面 `onShareAppMessage` 的 path 参数拼接 → 跳转内部功能（未授权页面）
- 扫码进入（scheme 参数）→ 与 Deep Link 类似，参数驱动内部跳转

---

## 九、验证要点

- 反编译还原度确认后再审计，防漏接口
- 接口全方法测试（GET/POST/PUT/DELETE）+ 无 token / 伪造 token / 他人 token 对比
- **登录链 A/B 交叉证明**：A 凭证访问 B 数据才算越权成立（只读自己数据不报）
- 支付回调重放/验签缺失：真实回调触发一次 → 重放 → 观察状态变化
- 云函数：换 openid 上下文调用敏感函数
- 渲染 XSS：真实触发（web-view 加载恶意 URL / rich-text 弹窗截图）
- 证据链：Burp 请求块 + 截图 + 影响证明；正式报告走 `report` 技能

## 十、修复建议

- **openid/session_key 一律服务端获取**，不信任前端传参；接口按服务端解析的身份鉴权
- code 一次性绑定会话、防重放；token 强签名、短时效
- 支付回调强制验签 + 幂等；金额服务端定价，不信任客户端参数
- 云函数入口做 `getWXContext().OPENID` 身份校验；云数据库按最小权限配置 + openid 过滤
- rich-text 渲染白名单净化（DOMPurify 适配小程序）；web-view src 白名单严格校验
- 本地存储不存明文 token/密钥；敏感接口加频率限制
- appsecret/云密钥严禁进前端包，扫描泄露并回收

---

## 联动

- 接口/鉴权/越权 → `api-protocol-security` / `auth-access-control`
- 支付/竞态 → `business-logic-race`
- 后端域名/appid/appsecret 提取 → `recon-js-analysis`
- rich-text/AI 输出渲染 XSS → `xss-frontend-security`（四）+ `ai-llm-agent-security`（3.6）
- 正式报告 DOCX → `report`
