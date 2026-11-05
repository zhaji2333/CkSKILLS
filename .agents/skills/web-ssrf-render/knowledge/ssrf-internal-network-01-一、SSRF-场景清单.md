# 一、SSRF 场景清单

> 来源：CkSKILLS v1 `ssrf-internal-network` §一、SSRF 场景清单（迁移至 v2 知识块）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 二维码生成 | SSRF/XSS/钓鱼 | URL参数可控、二维码内容可控 |
| 短链服务 | 重定向/SSRF/遍历 | 短链可预测、目标URL可控 |
| 代理/转发服务 | SSRF/内网穿透 | 目标地址可控、协议可控 |
| 爬虫/采集功能 | SSRF/RCE | 采集URL可控、解析引擎漏洞 |
| 在线预览(文档/代码) | SSRF/XSS/RCE | 远程URL加载、渲染引擎漏洞 |
| 模板/报表生成 | SSTI/任意文件读取 | 用户输入进入模板引擎 |
| Webhook/回调配置 | SSRF/信息泄露 | 回调URL可控、内网探测 |
| 文件预览（PDF/Office） | SSRF/XXE/RCE | 远程URL加载、OLE对象 |
| 图片处理 | SSRF | url:协议（ImageMagick） |
| 视频/音频处理 | SSRF/文件读取 | concat协议、HLS playlist（FFmpeg） |
| 网页截图/快照/存档 | SSRF/RCE | 后端无头浏览器渲染任意 URL；内核 N-day |
| HTML→PDF/长图导出 | SSRF/LFI/RCE | 用户 HTML/URL 进渲染器；file://、内网、渲染引擎漏洞 |
| 链接预览/卡片生成 | SSRF/信息泄露 | 抓取任意 URL；内网探测、云元数据、OG 字段外带 |
| 云浏览器/RBI/浏览器自动化 | RCE/逃逸 | 用户可控页面在云端浏览器执行；容器后利用 |
