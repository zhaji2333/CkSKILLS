# 七、CORS 错误配置专项

> 来源：CkSKILLS v1 `xss-frontend-security` §七、CORS 错误配置专项（迁移至 v2 知识块）

- 反射 Origin：`Access-Control-Allow-Origin: <攻击者Origin>` + `Allow-Credentials: true`
- 前缀匹配漏洞：`trusted.com.evil.com`
- 空 Origin / null Origin 反射
- 与凭证配合的敏感数据读取

> ⚠️ **CORS 定级前必须做的第一步（最高频误报来源）：确认凭据通道。**
> `Access-Control-Allow-Credentials: true` **只对浏览器自动携带的凭据有意义**（Cookie / TLS 客户端证书）。
> **判据**：攻击者能否让浏览器**自动**携带凭据？
> - 凭据在 **Cookie** 里 → CORS 配置缺陷 = **真实可利用**（反射 Origin/null + Allow-Credentials → 跨域读取用户数据）
> - 凭据在 **`localStorage` / `sessionStorage`，走自定义请求头**（如 `token: xxx`） → 攻击者跨域页面 ① 读不到目标域存储 ② 无法让浏览器自动附加该自定义头 → **`credentials:'include'` 也带不上凭据 → 401 → 无数据** → **不可利用，降级为信息性发现**
>
> **三步验证法**（实测，勿凭理论）：
> ```bash
> # ① 只带 Cookie（伪造业务 cookie 名）→ 若仍 401，说明 Cookie 不被采纳
> curl -s -X POST "$T/api/x" -H 'Content-Type: application/json' \
>      -H 'Cookie: SESSION=fake; JSESSIONID=fake; token=fake' -d '{}'
> # ② 只带自定义头 → 若报错点名该头，说明它才是凭据
> curl -s -X POST "$T/api/x" -H 'Content-Type: application/json' -H 'token: fake' -d '{}'
> # ③ 看登录/任意响应是否下发业务 Set-Cookie（只看到 CDN/WAF 标记如 acw_tc 即无 Cookie 会话）
> curl -s -i "$T/api/login" -X POST -H 'Content-Type: application/json' -d '{}' | grep -i '^set-cookie'
> ```
> 三者都指向"无 Cookie 通道"→ **不要立 CORS 案**，最多作为配置加固建议附带提及（并说明"若未来引入 Cookie 会话，此配置立即成为真实高危"）。
