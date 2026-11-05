---
name: ai-agent
description: AI/LLM/Agent 安全专项。当目标是 Chatbot/RAG/AI 助手、AI 应用平台、在线代码执行沙箱、云端 Agent 沙箱/工具执行/网关时调用。
---

# ai-agent — AI/LLM/Agent 安全专项

## 何时调用

- Chatbot/RAG/AI 助手/提示词
- AI 平台（Langflow/ComfyUI/Dify/Gradio 等）
- 在线代码执行/沙箱逃逸
- Agent 工具执行/平台 API/跨租户
- AI 输出渲染（转 xss）

## 30 秒分诊

1. 先建信任边界：谁调模型、模型能调哪些工具、检索源是否可控
2. 对话口当遥控器：合法请求让它执行命令
3. 平台 API 直打：F12 抓 exec/files/tool，换 sandbox_id 测跨租户
4. 沙箱内按七大面：组件未授权→凭据→提权→逃逸→跨租户→集群/内网→网关

## 首枪顺序

- 产品指纹：Langflow `validate/code` exec；ComfyUI userdata 写配置；Dify/Next RSC；Gradio component_server 读文件
- Python pyjail：`__subclasses__`/`_wrap_close.__globals__`/`chr(95)` 拼 dunder
- Node vm：`this.constructor.constructor('return process')()`；vm2 用 Proxy/Error.stack
- 提示词注入：直接/间接（文档/邮件/网页）；System Prompt 泄露
- RAG 投毒：可写知识库/检索源
- Agent 平台直打 `/exec` `/files` `/tool`，三态对照换 id
- 沙箱内凭据：env、`/proc/1/environ`、k8s sa token、配置文件
- 网关/控制面：伪造或下发响应，另一会话真执行才算（L3）

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/AI平台漏洞实战.md` | v2 实战：产品指纹/沙箱逃逸/Agent 运行时 | 3.7KB |
| `knowledge/agent-tool-exec-test.md` | 真实 SRC 对话口工具真执行 | 3.3KB |
| `knowledge/agent-sandbox-takeover-02-二、进站决策树.md` | Agent 沙箱进站决策树 | 0.9KB |
| `knowledge/agent-execution-channel-hijack-03-三、HTTP-跨租户-必须三态-+-对照.md` | 平台 API 跨租户 | 1.7KB |
| `knowledge/agent-prompt-injection-bypass-03-三、第一枪-未拒绝时.md` | 提示词注入第一枪 | 0.9KB |
| `knowledge/ai-llm-agent-security-04-三、提示词注入-Prompt-Injection-——-LLM01.md` | LLM 提示词注入全景 | 8.1KB |
| `knowledge/cloud-ide-codex-rce-chain.md` | 云 IDE/Codex RCE 链 | 7.9KB |

其余 44 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-auth-access` / `cloud-infra` / `web-xss-frontend`

