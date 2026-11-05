---
name: web-api-protocol
description: REST/GraphQL/gRPC/WebSocket/网关/HTTP 走私/缓存/请求头专项。当出现 Swagger/开放 API、GraphQL、WebSocket、反向代理/网关、缓存、调试端点时调用。
---

# web-api-protocol — REST/GraphQL/gRPC/WebSocket/网关/HTTP 走私/缓存/请求头专项

## 何时调用

- REST/JSON API/Swagger/OpenAPI
- GraphQL/gRPC/WebSocket
- 反向代理/API 网关/CDN
- 缓存/请求头/Host
- 调试端点/actuator/console

## 30 秒分诊

1. 先导出接口清单（Swagger/JS/GraphQL introspection/wsdl）
2. 全方法测试：GET/POST/PUT/PATCH/DELETE/OPTIONS
3. BOLA：换 id/租户做跨主体差分
4. 协议层：走私/缓存/Host 看前后端解析差异

## 首枪顺序

- Swagger/`/openapi.json` → 全接口 + 隐藏参数
- BOLA：同接口换 id/tenant 拿他人对象
- GraphQL：introspection、字段级越权、批量查询
- WebSocket：未授权订阅/消息越权/CSWSH
- HTTP 走私：CL.TE/TE.CL、分块体绕过 WAF
- 缓存欺骗：个人页加 `.css`/`;.jpg` 后缀偷会话页
- Host 头：重置链接/密码找回指向你的域
- CRLF/响应头注入；HPP 参数污染

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/http-smuggling-test.md` | HTTP 走私 | 0.7KB |
| `knowledge/cache-poisoning-test.md` | 缓存投毒/欺骗 | 0.6KB |
| `knowledge/graphql-test.md` | GraphQL | 9.9KB |
| `knowledge/websocket-test.md` | WebSocket | 0.5KB |
| `knowledge/http-host-header-test.md` | Host 头攻击 | 11.8KB |
| `knowledge/api-gateway-test.md` | API 网关 | 10.0KB |
| `knowledge/api-protocol-security-02-二、REST-API-测试要点.md` | REST 测试要点 | 0.6KB |
| `knowledge/crlf-injection-test.md` | CRLF 注入 | 0.4KB |

其余 26 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-auth-access` / `web-waf-bypass` / `web-recon`

