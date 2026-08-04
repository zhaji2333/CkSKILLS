---
name: ssrf-internal-network
description: 当发现URL参数可控的抓取/代理/转发/爬虫/文档预览/图片预览/二维码/短链/Webhook/回调/在线解压等功能时调用。负责SSRF探测、云元数据利用、内网资产发现、DNS重绑定、协议绕过（file/gopher/dict）、Redis等内网服务攻击。
---

# ssrf-internal-network — SSRF 与内网横向专项深度挖掘

## 何时调用（触发条件）

- 请求中存在 URL 参数（url、link、img、redirect、callback、webhook、notify_url）
- 服务端抓取/代理/转发功能（爬虫、采集、预览、转码）
- 回调类功能（支付回调、Webhook 配置、回调验证）
- 二维码/短链生成、在线解压（远程 URL）
- 图片/文档/音视频在线预览

## 一、SSRF 场景清单

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

## 二、云元数据（打内网核心）

```
AWS:     http://169.254.169.254/latest/meta-data/
阿里云:  http://100.100.100.200/latest/meta-data/
腾讯云:  http://metadata.tencentyun.com/latest/meta-data/
```

目标：获取临时凭证（IAM Role）、实例元数据、网络配置，进一步接管云资产。

## 三、内网探测思路

1. **先验证可控性**：请求外网可控地址（Burp Collaborator / DNSLog / 自己的 VPS）确认请求发出
2. **内网网段探测**：扫描 127.0.0.1、10.x、172.16-31.x、192.168.x 常见端口
3. **Redis 未授权**：`gopher://` 写入 crontab/SSH key/主从复制 RCE
4. **管理面板**：内网 Jenkins/ES/Grafana/MySQL 等
5. **协议利用**：
   ```
   file:///etc/passwd
   gopher://127.0.0.1:6379/_<redis命令>
   dict://127.0.0.1:6379/info
   ```
6. **DNS 重绑定**：注册域名解析到 127.0.0.1/内网 IP，绕过 IP 校验
7. **重定向绕过**：302 跳转至内网/云元数据，绕过 URL 白名单

## 四、绕过技术

- IP 混淆：十进制/十六进制/八进制（`2130706433`、`0x7f000001`、`0177.0.0.1`）
- 短域名/URL 解析差异（`http://127.0.0.1@evil.com`）
- 重定向（`http://evil.com/redirect?to=169.254.169.254`）
- DNS 重绑定
- 编码（双重 URL 编码、Unicode）
- 协议差异（代理与后端解析不一致）

## 五、验证要点

- 先证明出网（DNSLog 外带），再证明内网可达
- 云元数据：能读取即为严重（临时凭证可能接管云账号）
- 内网 Redis/数据库：未授权可交互即为严重
- 响应差异：端口开放/关闭、服务指纹、错误信息
- 报告标注：网络位置、出网方向、可达内网网段

## 六、修复建议

- URL 白名单（协议+域名+端口），禁止私网地址
- 禁用重定向跟随、禁用危险协议（file/gopher/dict）
- DNS 解析后二次校验 IP，防 DNS 重绑定
- 出口流量隔离、最小权限网络策略
- 云元数据服务：IMDSv2 + 限制访问

