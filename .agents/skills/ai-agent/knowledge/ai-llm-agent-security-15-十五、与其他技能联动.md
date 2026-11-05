# 十五、与其他技能联动

> 来源：CkSKILLS v1 `ai-llm-agent-security` §十五、与其他技能联动（迁移至 v2 知识块）

- 注入驱动工具执行 RCE / SQL → `injection-vulns`
- Agent HTTP 工具打内网 / 云元数据 → `ssrf-internal-network`
- Agent 文件工具任意读写 → `file-handling`
- LLM 输出致前端 XSS → `xss-frontend-security`
- 模型 API / 向量库接口 BOLA / 速率限制 → `api-protocol-security`
- 模型供应链 / 向量库未授权 / CI-CD → `cloud-infra-supply-chain`
- Payload 被过滤拦截 → `waf-bypass-techniques`（第十一章升级路径）
- LLM 应用源码审计 → `source-code-audit`
- 云端 Agent 对话/拒绝 → `agent-prompt-injection-bypass`
- 云端平台 API / HTTP 跨租户 → `agent-execution-channel-hijack`
- 云端沙箱七大危害面 → `agent-sandbox-takeover`

---
