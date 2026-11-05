# 一、三层（只有一层会拒绝）

> 来源：CkSKILLS v1 `agent-execution-channel-hijack` §一、三层（只有一层会拒绝）（迁移至 v2 知识块）

```
层3 运行时   bash / 各端口服务     → 没有拒绝，只有鉴权  → agent-sandbox-takeover
层2 平台/网关 会话 / 工具调用 / 下发 → 没有拒绝，只有 token
层1 模型     「我不能帮你做这个」   → 唯一会拒绝
```

| 路径 | 过模型 | 会拒绝 | 入口 |
|---|---|---|---|
| A 对话 | 是 | 是 | 对话框（`agent-prompt-injection-bypass`） |
| **B 平台 API** | 否 | 否 | **F12 → Network（本技能）** |
| **C 运行时** | 否 | 否 | `ss -tlnp`（takeover） |

**跨租户、影响全用户，常见来源就是路径 B 的换 id。** 网关劫持无感 RCE 全用户是 takeover 第八节 L3，本技能负责把网关 HTTP 口抓出来并做 L1/L2。
