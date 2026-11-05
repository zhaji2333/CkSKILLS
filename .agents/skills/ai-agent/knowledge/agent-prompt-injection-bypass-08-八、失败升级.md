# 八、失败升级

> 来源：CkSKILLS v1 `agent-prompt-injection-bypass` §八、失败升级（迁移至 v2 知识块）

```
改措辞 → 加理由 → 换角色 → 拆步骤 → 换包装 → 编码 → 换工具 → 换入口(F12) → 放弃 A
```

放弃 A 之后：
- 路径 B → `agent-execution-channel-hijack`
- 路径 C / 已有执行 → `agent-sandbox-takeover`
- 间接注入 → 本节第七节  

输出 XSS（AI 只当解码器）→ `xss-frontend-security`，不要报成 Agent 洞。
