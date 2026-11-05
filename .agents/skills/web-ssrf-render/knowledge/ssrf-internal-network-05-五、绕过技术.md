# 五、绕过技术

> 来源：CkSKILLS v1 `ssrf-internal-network` §五、绕过技术（迁移至 v2 知识块）

- IP 混淆：十进制/十六进制/八进制（`2130706433`、`0x7f000001`、`0177.0.0.1`）
- 短域名/URL 解析差异（`http://127.0.0.1@evil.com`）
- 重定向（`http://evil.com/redirect?to=169.254.169.254`）
- DNS 重绑定
- 编码（双重 URL 编码、Unicode）
- 协议差异（代理与后端解析不一致）
