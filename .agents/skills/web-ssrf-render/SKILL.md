---
name: web-ssrf-render
description: SSRF/内网探测/云元数据/服务端无头浏览器渲染专项。当出现 URL 可控的抓取、代理、回调、webhook、图片/文档预览、网页截图、HTML→PDF、链接预览时调用。
---

# web-ssrf-render — SSRF/内网探测/云元数据/服务端无头浏览器渲染专项

## 何时调用

- URL 抓取/代理/转发/爬虫
- 回调/webhook/回调通知
- 图片/文档预览/在线解压
- 网页截图/快照/HTML→PDF/链接预览
- 云主机上的远程内容获取

## 30 秒分诊

1. 找入口并确认请求是否真的发出（监听器回连/DNS/时间差）
2. 先用公网 URL 确认回显，再打内网
3. 私网被拦 → 十进制 IP/解析差异/302/重定向/DNS 重绑定
4. 内网到手 → 先读 /api/status、/debug/config 找下一跳

## 首枪顺序

- 内网 IP：`169.254.169.254`、`100.100.100.200`、`imds:8080`、`internal-api:5000`
- 十进制 IP：127.0.0.1→`2130706433`；172.19.0.2→`2886926338`
- 解析差异：`http://internal-api:5000\@x/../debug/config`
- 302 跳转/短链/DNS 重绑定绕过白名单
- 协议：`file://`、`gopher://`（打 Redis/FastCGI）
- 无回显：DNS/HTTP 外带到监听器
- 渲染：注入 `<script>fetch(...)</script>`/`<img>` 确认真浏览器
- 渲染升级：`file://` 读文件、Chromium N-day、容器内横向（转 ai-agent）

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/SSRF内网实战.md` | v2 实战：入口词表/绕过/内网/渲染 | 2.7KB |
| `knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md` | 云元数据 | 0.5KB |
| `knowledge/ssrf-internal-network-03-三、服务端无头浏览器渲染专项-截图-快照-HTML→PDF-链接预览.md` | 无头浏览器渲染 | 5.1KB |
| `knowledge/ssrf-test.md` | 真实 SRC SSRF 战法（GOPROXY/代理/元数据路径差） | 7.1KB |
| `knowledge/ssrf-internal-network-05-五、绕过技术.md` | 绕过技术 | 0.4KB |
| `knowledge/dns-rebinding-test.md` | DNS 重绑定 | 0.3KB |

其余 3 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `cloud-infra` / `ai-agent` / `web-waf-bypass`

