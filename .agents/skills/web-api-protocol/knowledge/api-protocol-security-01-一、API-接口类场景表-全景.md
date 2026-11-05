# 一、API/接口类场景表（全景）

> 来源：CkSKILLS v1 `api-protocol-security` §一、API/接口类场景表（全景）（迁移至 v2 知识块）

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
