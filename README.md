# CK-Skills

> 基于 Claude Code / Codex 的 SRC 漏洞挖掘 Agent 技能体系 —— 将顶尖安全研究员的方法论沉淀为可调度、可复用的 Skill 知识资产。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-17-green.svg)](.agents/skills)

## 📌 项目简介

CK-Skills 是一套面向 SRC 漏洞挖掘的 **Agent 提示词工程与技能知识体系**,以 Claude Code / Codex 等通用 Agent 框架为运行时,通过 **系统级提示词(AGENTS.md)+ 17 个专项技能知识库(Skills)**,让通用 Agent 在垂直安全领域达到专家级表现。

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
│  17 个专项 Skills(知识层)                     │  方法论 / 场景表 / 步骤
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
| `recon-js-analysis` | 资产测绘、webpack / source map 还原、API 与密钥提取、URL/IP/域名资产扩展、appid/appkey 凭证上报深挖 |
| `auth-access-control` | 认证绕过、越权、IDOR、多租户隔离、密码重置、JWT |
| `injection-vulns` | SQL / NoSQL / 命令 / SSTI / 表达式注入 |
| `business-logic-race` | 支付逻辑、状态机建模、金额篡改、竞态条件 |
| `file-handling` | 文件上传 getshell、路径穿越、Zip Slip、CSV 注入 |
| `ssrf-internal-network` | SSRF、云元数据、内网探测、DNS 重绑定 |
| `deserialization-xxe` | 反序列化 RCE、XXE、原型污染、利用链构造 |
| `xss-frontend-security` | XSS、CSRF、CORS、Clickjacking |
| `api-protocol-security` | BOLA、GraphQL、WebSocket、HTTP 走私 |
| `miniprogram-security` | 微信/支付宝/抖音小程序、包反编译、接口与密钥提取、微信登录/支付/越权/渲染/云开发深挖 |
| `cloud-infra-supply-chain` | 云配置错误、K8s、CI/CD、SBOM、供应链 |
| `source-code-audit` | 输入点 → 传播链 → Sink 静态审计 |
| `waf-bypass-techniques` | Level 1-7 对抗升级框架 |
| `ai-llm-agent-security` | 提示词注入、越狱逃逸、System Prompt 泄露、RAG/记忆污染、Agent 工具滥用致 RCE/SSRF、沙箱逃逸、模型供应链 |
| `windows-reverse-engineering` | Windows PE 逆向、.NET/内核组件、缓冲区溢出、协议逆向、反调试对抗、shellcode 与 PoC 验证 |
| `android-security-audit` | Android APK 组件安全深度审计、Intent/WebView/Provider/Binder/Deep Link、无 Frida/无 Root 漏洞验证、HyperOS 收录标准报告 |
| `report` | 漏洞报告成稿收口——分层验证门把关、DOCX 提交稿（模板 + Step 式 PoC + 真实截图）、语义化命名归档 |

## 🚀 怎么使用（30 秒上手）

### 方式一：一键安装（推荐）

把下面这段提示词整段复制，粘贴给你的 Agent（Claude Code / Codex 等，不同框架会自动适配自己的技能加载规范），Agent 会替你完成**下载 → 安装 → 加载 → 自检**：

```
我将用你进行 SRC 漏洞挖掘。请立即按以下步骤执行：

1. 下载并安装这个SKILLS https://github.com/zhaji2333/CkSKILLS.git 
2. 加载：确认 AGENTS.md 已作为系统提示词生效、技能路由表可用
3. 自检：列出已安装的全部专项技能清单，确认各自的触发描述可被识别
4. 报告：输出「技能库已安装并加载」+ 技能清单，然后等待我提供测试目标

之后我会直接给出目标域名 / APK / 源码，你按 AGENTS.md 路由表自动调用对应技能深度挖掘。
```

### 方式二：手动安装

```bash
git clone https://github.com/zhaji2333/CkSKILLS.git
# 将 CkSKILLS 中的 AGENTS.md 与 .agents/ 目录放入你的工作目录，重启 Agent 即自动加载
```

### 使用示例（安装后）

```
目标：https://example.com，已登录普通用户，需要测试越权
→ 自动加载 auth-access-control，按"权限三问"执行
```

### 卸载

删除工作目录下的 `AGENTS.md` 与 `.agents/` 目录即可（或按你的 Agent 框架规范移除）。

> ⚠️ 使用前请阅读文末免责声明，仅用于授权安全测试。

## 🆕 最近更新

- **新增 `windows-reverse-engineering`**：Windows PE 逆向与二进制漏洞深度挖掘（反汇编/反编译、内存破坏漏洞、协议逆向、反调试对抗、漏洞利用链构造）
- **新增 `android-security-audit`**：Android APK 组件安全深度审计——JADX 静态分析 + ADB 动态验证，无 Frida/无 Root 漏洞验证，对标小米 HyperOS 漏洞收录标准
- **新增 `report`**：写报告验证收口技能——分层验证门把关、按模板生成可提交 SRC/0day 平台的 DOCX 报告（Step 式 PoC + 真实截图）
- **重构 `miniprogram-security`**：原 `mobile-iot-device-security` 拆分为小程序专项（微信/支付宝/抖音 + 云开发），消除与 `android-security-audit` 的 Android 内容重复
- **扩充信息收集相关 SKILLS**：
  - `recon-js-analysis` 新增 **URL/IP/域名资产扩展**（webpack/app.js/抓包中提取的地址全部进入资产测绘，APP 来源的提醒关注后台接口域名）与 **appid/appkey 凭证上报深挖**（验证有效性、打后端/云资产）
  - `android-security-audit` 支持从 APK 反编译产物中提取**后端接口域名与应用凭证**并联动深挖

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
