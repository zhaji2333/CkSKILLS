---
name: api-protocol-security
description: 当目标存在REST/GraphQL/gRPC/WebSocket接口、Swagger/OpenAPI文档、调试端点（actuator/console）、旧版本API、内部接口、微服务网关，或需要测试HTTP走私、DoS、速率限制时调用。负责API全方法测试、BOLA越权、GraphQL深度攻击、协议层漏洞挖掘。
---

# api-protocol-security — API 与协议层安全专项深度挖掘

## 何时调用（触发条件）

- REST/GraphQL/gRPC/WebSocket 接口
- 接口文档暴露（Swagger/OpenAPI/api-docs）
- 调试端点（/actuator /debug /console /metrics）
- 旧版本接口（/api/v1 未下线）、内部接口外泄
- 微服务网关、反向代理
- HTTP 解析差异（走私）、缓存投毒
- 资源消耗类攻击（深层查询、巨型请求）

## 一、API/接口类场景表（全景）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| REST API | 越权/注入/信息泄露 | 全方法测试(GET/POST/PUT/DELETE/PATCH) |
| GraphQL | 内省泄露/深度攻击/批量查询 | __schema查询、嵌套查询DoS、别名批量 |
| gRPC | 反序列化/未授权 | protobuf解析、接口鉴权 |
| WebSocket | 鉴权缺失/注入/越权 | 连接无token验证、消息可伪造 |
| 接口文档(Swagger/OpenAPI) | 敏感接口泄露 | /swagger-ui /api-docs暴露 |
| 调试接口 | 未授权访问/RCE | /actuator /debug /console |
| 旧版本接口 | 鉴权缺失/逻辑差异 | /api/v1旧版本未下线 |
| 内部接口外泄 | 未授权/敏感操作 | 内部RPC接口可公网访问 |

## 二、REST API 测试要点

- 每个接口测试全部 HTTP 方法（GET/POST/PUT/DELETE/PATCH/OPTIONS）
- 每个参数测试：正常值、空值、边界值、类型混淆、数组化、超长、特殊字符
- 鉴权测试：有 token/无 token/过期 token/其他用户 token
- 隐藏参数/调试参数全部尝试（debug=1、test=1、_method=PUT）
- BOLA（对象级授权）：遍历资源 ID、批量参数
- 速率限制：登录、验证码、短信、转账接口是否可绕过（IP/Header 伪造）

## 三、GraphQL 专项

- **内省查询**：`{__schema{types{name}}}` 是否开放
- **深度攻击**：嵌套查询（friends 循环）造成 DoS
- **别名批量**：同一查询别名多次执行绕过速率限制
- **批量枚举**：`user(id:1)` 遍历获取数据
- **越权**：字段级权限缺失（隐藏字段可查）

## 四、WebSocket 专项

- 连接时是否验证 token（无鉴权直连）
- 消息伪造：他人会话/敏感操作
- 注入：SQL/命令注入点进入消息处理
- 越权：通过消息 ID 操作他人资源

## 五、HTTP 走私 / 协议层（O类）

- 反向代理解析差异（Content-Length vs Transfer-Encoding）
- 请求边界混淆 → 前置代理放行、后端走私
- 测试工具：`smuggler` / Burp 扩展
- 影响：缓存投毒、绕过鉴权、越权访问其他用户请求

## 六、资源消耗 DoS（P类）

- 正则灾难回溯（ReDoS）
- 巨型 JSON/XML 解析
- 图像炸弹（解压炸弹）
- 深度递归（GraphQL 嵌套）
- 无速率限制的批量接口

## 七、验证要点

- 全方法测试结果记录：每个方法的状态码/响应差异
- 未授权访问：直接调用管理接口/调试端点是否 200
- BOLA：A 用户 token 读取 B 用户数据即确认
- 走私：请求包能否污染下一个请求的响应
- 报告标注：接口文档暴露范围、可枚举数据量、速率限制缺失的影响

## 八、修复建议

- 统一网关鉴权，接口文档/调试端点仅内网开放
- 旧版本接口下线或同步鉴权
- GraphQL：关闭内省、深度/复杂度限制、别名限制
- WebSocket：连接鉴权 + 消息级权限校验
- 代理统一解析（规范 CL/TE）、禁止走私
- 速率限制：服务端按用户/IP，防 Header 伪造

