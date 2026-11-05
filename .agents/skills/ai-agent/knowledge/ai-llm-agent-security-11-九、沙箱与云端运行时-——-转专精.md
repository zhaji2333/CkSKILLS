# 九、沙箱与云端运行时 —— 转专精

> 来源：CkSKILLS v1 `ai-llm-agent-security` §九、沙箱与云端运行时 —— 转专精（迁移至 v2 知识块）

云端容器/微VM/云电脑的六问、组件未授权、凭据、提权、逃逸、跨租户、网关 L3 → **`agent-sandbox-takeover`**。  
本机 Python eval 黑名单绕过不是云端 Agent 主战场，有进程内 `exec` 无隔离时再按语言沙箱打。

运行时对抗（工具 description 注入、reasoning 通道劫持）进沙箱或 F12 后按 hijack 第五节 / takeover 8.8 打。
