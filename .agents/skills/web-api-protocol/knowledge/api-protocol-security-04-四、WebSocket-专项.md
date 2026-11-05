# 四、WebSocket 专项

> 来源：CkSKILLS v1 `api-protocol-security` §四、WebSocket 专项（迁移至 v2 知识块）

- 连接时是否验证 token（无鉴权直连）
- 消息伪造：他人会话/敏感操作
- 注入：SQL/命令注入点进入消息处理
- 越权：通过消息 ID 操作他人资源
