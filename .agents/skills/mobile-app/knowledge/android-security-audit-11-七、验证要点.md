# 七、验证要点

> 来源：CkSKILLS v1 `android-security-audit` §七、验证要点（迁移至 v2 知识块）

- **🔴 密钥追踪链（最高优先级，见 一）**：提取密钥（DEX grep / SO Hook / H5 提取）→ 还原签名/加密逻辑（Python 重写）→ 未授权请求成功返回真实数据 = 直接成洞
- 每个导出组件（Activity/Service/Receiver/Provider）都要回答：能否被外部触发（exported？有权限保护？有来源校验？）→ 参数可控 → 流向敏感操作（startActivity/exec/文件/数据库/UI 渲染）。
- **远程优先**：能通过 Deep Link/恶意网页触发的漏洞，评级高于 ADB 触发；验证时优先构造 HTML PoC。
- **字符串匹配 ≠ 证明执行**：grep 命中后必须沿调用链确认参数可达性与校验缺失，并截图取证。
- 组件间组合：Deep Link → WebView → JSBridge → 命令执行/文件读取 是多技能组合链（见 AGENTS.md 4.4），不要停在单点。
- 报告评级与成稿：漏洞定级按 `../../../../rules/15-hunting-mindset.md` 可利用性六问 + `../../../../rules/40-evidence-report.md` 三档定级，正式报告按第 6 节 Markdown 四段式；本技能负责把证据链做扎实（截图、调用链、A/B 交叉证明）。
- **🔴 Native/内存安全链（见 三）**：JADX 定位 native 入口 → IDA 9.5 无头枚举 JNI 导出 → 缓解措施摸底 → 危险 Sink 扫描 → 可达性回溯到外部输入 → ADB 触发取证 = 成洞
- 小程序目标见 `miniprogram-security`；**so 层深度逆向在本技能内完成（三、Native/内存安全深挖）**，云端 Agent 容器逃逸另走 `agent-sandbox-takeover`，两者不要混淆。
