# 三、场景表（漏洞全景）

> 来源：CkSKILLS v1 `miniprogram-security` §三、场景表（漏洞全景）（迁移至 v2 知识块）

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
