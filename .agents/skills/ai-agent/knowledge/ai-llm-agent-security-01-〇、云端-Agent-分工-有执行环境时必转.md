# 〇、云端 Agent 分工（有执行环境时必转）

> 来源：CkSKILLS v1 `ai-llm-agent-security` §〇、云端 Agent 分工（有执行环境时必转）（迁移至 v2 知识块）

目标口径：跨租户影响全用户、网关劫持无感 RCE 全在线用户、客户端当肉鸡、组件未授权、凭据、提权、逃逸、集群/内网横移。

| 阶段 | 技能 |
|---|---|
| 还不知道有没有工具 | 本技能第十六节 5 分钟分诊 |
| 对话当遥控器 / 被拒后绕护栏 | `agent-prompt-injection-bypass` |
| F12 打平台 API、HTTP 换 sandbox_id | `agent-execution-channel-hijack` |
| 已在云沙箱里 | `agent-sandbox-takeover` |
| 平台架构对照 | `agent-sandbox-takeover` 六问 + 《AI-Agent漏洞挖掘教程.md》第 5 章 |

本机 IDE 编码 Agent 不在本体系深挖。具体平台细节不写进 SKILL。
