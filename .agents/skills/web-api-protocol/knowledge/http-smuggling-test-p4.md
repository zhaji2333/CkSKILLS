# http-smuggling-test · part 4

> 分段 4/4。完整索引见 `http-smuggling-test.md`。

## 8. TESTING METHODOLOGY

### 8.1 Safe Probe Sequence

```
1. Identify architecture:
   - Check Via, Server, X-Served-By headers
   - Detect CDN (Cloudflare cf-ray, CloudFront x-amz-cf-id, etc.)

2. HTTP version probing:
   - curl --http2 https://target.com -v
   - Check if ALPN negotiation includes h2

3. Time-based desync detection:
   a. CL.TE probe:
      POST / HTTP/1.1
      Content-Length: 4
      Transfer-Encoding: chunked

      1
      A
      0

   b. If response is delayed → back-end is waiting for chunked end → CL.TE likely

4. H2 desync:
   - Send H2 request with content-length: 0 + body containing smuggled prefix
   - Follow with normal request; observe if response matches smuggled path

5. CL.0 detection:
   - Find endpoints returning without consuming body (redirects, static files)
   - Send POST with excess body, follow with normal GET
```

### 8.2 Tools

| Tool | Purpose |
|---|---|
| **Burp Suite HTTP Request Smuggler** | Automated variant scanning |
| **h2csmuggler** (GitHub) | HTTP/2 cleartext smuggling |
| **smuggler.py** (defparam) | CL.TE, TE.CL, TE.TE automation |
| **http2smugl** (GitHub) | H2-specific desync testing |
| **curl** with `--http2` / `--http1.1` | Manual H2/H1 probing |
| **hyper** (Python) | Low-level H2 frame crafting |

### 8.3 Impact Escalation Checklist

```
□ Confirmed desync variant (CL.TE / TE.CL / H2.CL / H2.TE / CL.0)
□ Can smuggle full request? (not just prefix)
□ Connection pooling enabled? (affects other users → critical)
□ Cacheable endpoints exist? (→ cache poisoning)
□ Authenticated endpoints reachable? (→ auth bypass, data theft)
□ Can reflect content in response? (→ stored XSS via cache)
□ Admin/internal paths accessible? (→ privilege escalation)
□ Client-side desync possible? (→ per-user attacks)
```
