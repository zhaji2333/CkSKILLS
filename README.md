# CK-Skills

> 基于 Claude Code / Codex 的 SRC 漏洞挖掘 Agent 技能体系 —— 将顶尖安全研究员的方法论沉淀为可调度、可复用的 Skill 知识资产。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-13-green.svg)](.agents/skills)

## 📌 项目简介

CK-Skills 是一套面向 SRC 漏洞挖掘的 **Agent 提示词工程与技能知识体系**,以 Claude Code / Codex 等通用 Agent 框架为运行时,通过 **系统级提示词(AGENTS.md)+ 13 个专项技能知识库(Skills)**,让通用 Agent 在垂直安全领域达到专家级表现。

针对通用 Agent 在垂直领域的三大痛点:

- 方法论散、覆盖不全
- 浅尝辄止、不按专家流程执行
- 业务逻辑 / 越权 / WAF 绕过等经验型漏洞难以自动化

## 🏗 架构设计

四层架构,各司其职:

```
┌──────────────────────────────────────────────┐
│  Agent 运行时(Claude Code / Codex)           │  推理与工具调用
├──────────────────────────────────────────────┤
│  系统级提示词 AGENTS.md                        │  身份 / 约束 / 纪律 / 调度
├──────────────────────────────────────────────┤
│  13 个专项 Skills(知识层)                     │  方法论 / 场景表 / 步骤
├──────────────────────────────────────────────┤
│  触发路由(场景→技能 / 漏洞类型→技能)         │  专家知识按需加载
└──────────────────────────────────────────────┘
```

- **AGENTS.md**:六段式总纲(身份-约束-纪律-调度-评估-输出),定义 Agent 人格、Extended Thinking 推理链、十条测试执行纪律、结构化输出标准
- **Skill**:用 Markdown DSL 编写,frontmatter(触发语义)+ 六要素(触发条件 / 方法论 / 场景表 / 挖掘步骤 / 验证要点 / 修复建议)
- **路由表**:场景→技能 / 漏洞类型→技能 / 优先级 / 组合场景,借鉴 MoE 思想实现专家知识按需加载

## 📚 Skills 列表

| 技能 | 覆盖范围 |
|---|---|
| `recon-js-analysis` | 资产测绘、webpack / source map 还原、API 与密钥提取 |
| `auth-access-control` | 认证绕过、越权、IDOR、多租户隔离、密码重置、JWT |
| `injection-vulns` | SQL / NoSQL / 命令 / SSTI / 表达式注入 |
| `business-logic-race` | 支付逻辑、状态机建模、金额篡改、竞态条件 |
| `file-handling` | 文件上传 getshell、路径穿越、Zip Slip、CSV 注入 |
| `ssrf-internal-network` | SSRF、云元数据、内网探测、DNS 重绑定 |
| `deserialization-xxe` | 反序列化 RCE、XXE、原型污染、利用链构造 |
| `xss-frontend-security` | XSS、CSRF、CORS、Clickjacking |
| `api-protocol-security` | BOLA、GraphQL、WebSocket、HTTP 走私 |
| `mobile-iot-device-security` | Android / iOS 逆向、WebView、固件安全 |
| `cloud-infra-supply-chain` | 云配置错误、K8s、CI/CD、SBOM、供应链 |
| `source-code-audit` | 输入点 → 传播链 → Sink 静态审计 |
| `waf-bypass-techniques` | Level 1-7 对抗升级框架 |

## 🚀 快速开始

### 1. 安装

将本项目 `.agents/` 目录与 `AGENTS.md` 放入你的工作目录,Agent 会自动加载 `AGENTS.md` 作为系统提示词,并根据触发信号加载对应 Skill。

### 2. 目录结构

```
CK-Skills/
├── AGENTS.md                      # 系统级提示词总纲
├── .agents/
│   └── skills/                    # 13 个专项技能
│       ├── recon-js-analysis/
│       │   └── SKILL.md
│       ├── auth-access-control/
│       │   └── SKILL.md
│       └── ...                    # 其余专项技能
```

### 3. 使用

在 Claude Code / Codex 中直接描述测试场景,Agent 会根据触发信号自动加载对应 Skill 并按方法论执行:

```
目标:https://example.com,已登录普通用户,需要测试越权
→ 自动加载 auth-access-control,按"权限三问"执行
```

## 🎯 设计理念

- **JS 不吃透,不发包**:信息收集先行,吃透前端再动手
- **覆盖度自检**:✅已测 / ❌未测 / 🔄变种 / 💡关联
- **失败升级**:Level 1-7,至少到 Level 4 才能下"无漏洞"结论
- **业务建模**:状态机 + 角色矩阵 + 非法路径 + 一致性校验 + 并发
- **跨接口关联**:信息流 / 凭证 / 状态 / 权限 / 时序五问

## 🤝 贡献

欢迎提交 Issue / PR 补充 Skill 或完善方法论。新增 Skill 只需按现有 DSL 编写 `SKILL.md` 并在 AGENTS.md 路由表注册。

## ⚠️ 免责声明

本项目仅用于**授权安全测试、安全研究与教学**。使用者需遵守所在国家/地区的法律法规,在获得目标所有者明确书面授权的前提下使用。禁止用于任何非法用途。使用者自行承担因不当使用产生的一切法律责任。

## 📄 License

[MIT](LICENSE)
