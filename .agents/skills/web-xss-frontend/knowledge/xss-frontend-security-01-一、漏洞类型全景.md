# 一、漏洞类型全景

> 来源：CkSKILLS v1 `xss-frontend-security` §一、漏洞类型全景（迁移至 v2 知识块）

| 类型 | 场景 | 修复 |
|---|---|---|
| D1. 反射型/存储型XSS | 搜索、评论、富文本 | 输出编码、CSP |
| D2. DOM XSS | location/hash/postMessage | 安全DOM API |
| D3. Clickjacking | iframe嵌套 | X-Frame-Options |
| D4. CORS错误配置 | `*`+凭证 | 严格白名单 |
| D5. 跳转型XSS（优先） | target/redirect 参数驱动 location 跳转、伪协议执行 | 协议+Host 白名单、HttpOnly |
| D6. AI/Markdown 渲染型存储XSS | AI 输出/聊天记录经 marked 渲染写 innerHTML 无净化 | DOMPurify 净化、服务端清洗、CSP |
