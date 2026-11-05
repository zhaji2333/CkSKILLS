# 十六、开工 5 分钟分诊（没有工具 = 没有 Agent 运行时洞）

> 来源：CkSKILLS v1 `ai-llm-agent-security` §十六、开工 5 分钟分诊（没有工具 = 没有 Agent 运行时洞）（迁移至 v2 知识块）

> **没有工具 = 没有跨租户执行 / 沙箱 / 网关这类洞**，无论护栏多花。只剩 LLM01/05/07 和常规 Web。

```
1. 问：「你能执行代码 / 读文件 / 访问网址吗？」
   明确不能 → Agent 运行时方向降级
2. grep 前端 JS：exec / code_interpreter / tool_call / sandbox / mcp
3. 接口有没有执行语义：上传下载、URL 抓取、终端、沙箱会话
4. 有 session/知识库 → 仍可打 RAG/记忆/越权读对话（LLM 类）
5. 有工具 → 转三子；无工具 → 只打本技能 LLM 类 + Web
```

正面特征（命中两条才按 takeover 深挖）：产品自称能跑代码/操作云电脑；JS 有 tool_call；有沙箱/网关接口。无工具却堆越狱 = 空转。
