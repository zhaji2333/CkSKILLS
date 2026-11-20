# CK-Skills

> 基于 Claude Code / Codex / DeepSeek Harness 的 SRC 漏洞挖掘 Agent 技能体系 —— 将顶尖安全研究员的方法论沉淀为可调度、可复用的 Skill 知识资产。

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/Skills-18-green.svg)](.agents/skills)
[![v1 skills](https://img.shields.io/badge/v1-20%2B-blue.svg)](https://github.com/zhaji2333/CkSKILLS/tree/v1)

**语言：** **中文** · [English（v1）](https://github.com/zhaji2333/CkSKILLS/blob/v1/README_EN.md)

> 📦 **版本说明**：当前 `main` 分支为 **v2**（薄常驻层 + 16 技能包，适用于 **DeepSeek Harness**）；旧版 [**v1 分支**](https://github.com/zhaji2333/CkSKILLS/tree/v1) 保留完整技能体系（20+ 技能包）与 Claude Code / Codex 传统工作流。
>
> 本 README 以 v1 的完整介绍为底稿；v2 的分层结构、18 个技能包与多 Agent 机制见文末《CkSKILLS v2》章节。

> [!TIP]
> 🚢 **强烈推荐：[Flotilla](https://github.com/zhaji2333/Flotilla) —— Super Agent 架构的自主渗透测试平台**，多图 + 多智能体在授权范围内自主完成侦察、验证与证据收集。

## 📌 项目简介

CK-Skills 是一套面向 SRC 漏洞挖掘的 **Agent 提示词工程与技能知识体系**,以 Claude Code / Codex / DeepSeek Harness 等通用 Agent 框架为运行时,通过 **系统级提示词(AGENTS.md)+ 20+ 个专项技能知识库(Skills)**（v1 划分，v2 重组为 18 个技能包）,让通用 Agent 在垂直安全领域达到专家级表现。

针对通用 Agent 在垂直领域的三大痛点:

- 方法论散、覆盖不全
- 浅尝辄止、不按专家流程执行
- 业务逻辑 / 越权 / WAF 绕过等经验型漏洞难以自动化

## 🏗 架构设计

五层架构,各司其职（下图为 v1 结构示意；v2 在此基础上增加 `rules/` 纪律层与多 Agent 回灌约束，详见文末）:

```
┌──────────────────────────────────────────────┐
│  Agent 运行时(Claude Code / Codex)           │  推理与工具调用
├──────────────────────────────────────────────┤
│  系统级提示词 AGENTS.md                        │  身份 / 约束 / 纪律 / 调度
├──────────────────────────────────────────────┤
│  20 个专项 Skills(知识层)                     │  方法论 / 场景表 / 步骤
├──────────────────────────────────────────────┤
│  触发路由(场景→技能 / 漏洞类型→技能)         │  专家知识按需加载
├──────────────────────────────────────────────┤
│  hunts/<目标>/CLUEBOARD.md                    │  共享黑板（跨轮工作记忆）
└──────────────────────────────────────────────┘
```

- **AGENTS.md**:六段式总纲(身份-约束-纪律-调度-评估-输出),定义 Agent 人格、Extended Thinking 推理链、十条测试执行纪律、结构化输出标准
- **Skill**:用 Markdown DSL 编写,frontmatter(触发语义)+ 六要素(触发条件 / 方法论 / 场景表 / 挖掘步骤 / 验证要点 / 修复建议)
- **路由表**:场景→技能 / 漏洞类型→技能 / 优先级 / 组合场景,借鉴 MoE 思想实现专家知识按需加载
- **线索板**:当前目标一份 Markdown 台账；各专项 Skill 往同一块板读写。低配黑板架构——Skill 是知识源，板是黑板，`AGENTS.md` 路由是控制，不是多 Agent 并行抢写
- **v2 纪律层**:`rules/` 11 篇（不误拒 / 最小伤害 / 证据交付 / 多 Agent 回灌……）；常驻层只留每轮必须生效的铁律，细节按需加载
- **v2 多 Agent**:线索板只由 Lead 写，子代理开工读板、收工交 `dig/<角色>/SYNC.md` 回灌块；`tools/clueboard_sync_check.py` 做合板机械闸

## 📚 Skills 列表

> 下表为 v1 的技能划分（对应 [v1 分支](https://github.com/zhaji2333/CkSKILLS/tree/v1)）；v2 已重组为 18 个技能包，见文末《CkSKILLS v2 · 技能包》。

| 技能 | 覆盖范围 |
|---|---|
| `recon-js-analysis` | 资产测绘、webpack / source map 还原、API 与密钥提取、URL/IP/域名资产扩展、appid/appkey 凭证上报深挖 |
| `unauth-path-key-hunt` | 零身份公开面还原路径与密钥：响应指纹分流、加密证伪（RSA/JSEncrypt 不是鉴权）、迁域/兄弟域复查 |
| `hunt-clueboard` | 当前目标 Markdown 线索板（跨轮工作记忆：读→挖→写回），不替代挖洞 skill |
| `auth-access-control` | 认证绕过、前端鉴权/路由守卫绕过、验证码安全、越权、IDOR、多租户隔离、密码重置、JWT |
| `injection-vulns` | SQL / NoSQL / 命令 / SSTI / 表达式注入 |
| `business-logic-race` | 支付逻辑、状态机建模、金额篡改、竞态条件 |
| `file-handling` | 文件上传 getshell、路径穿越、Zip Slip、CSV 注入 |
| `ssrf-internal-network` | SSRF、云元数据、内网探测、DNS 重绑定 |
| `deserialization-xxe` | 反序列化 RCE、XXE、原型污染、利用链构造 |
| `xss-frontend-security` | XSS（含跳转型/开放重定向）、CSRF、CORS、Clickjacking |
| `api-protocol-security` | BOLA、GraphQL、WebSocket、HTTP 走私 |
| `miniprogram-security` | 微信/支付宝/抖音小程序、包反编译、接口与密钥提取、微信登录/支付/越权/渲染/云开发深挖 |
| `cloud-infra-supply-chain` | 云配置错误、K8s、CI/CD、SBOM、供应链 |
| `source-code-audit` | 输入点 → 传播链 → Sink 静态审计 |
| `waf-bypass-techniques` | Level 1-7 对抗升级框架 |
| `ai-llm-agent-security` | 提示词注入、越狱逃逸、System Prompt 泄露、RAG/记忆污染、Agent 工具滥用致 RCE/SSRF、沙箱逃逸、模型供应链 |
| `windows-reverse-engineering` | Windows PE 逆向、.NET/内核组件、缓冲区溢出、协议逆向、反调试对抗、shellcode 与 PoC 验证 |
| `android-security-audit` | Android APK 组件安全深度审计、Intent/WebView/Provider/Binder/Deep Link、无 Frida/无 Root 漏洞验证、HyperOS 收录标准报告 |
| `apk-reversing` | APK 壳识别、脱壳还原 dex、JADX/apktool 全量反编译、so/H5/assets 提取，产出 android-security-audit 可直接开挖的源码产物 |
| `asc-fast-hunt` | APK 零预处理快速定位（基于 Droid ASC）：秒级全局交叉引用搜索（字符串/类型/方法/字段）、按需反编译单类、Manifest 秒读——大包不必等全量反编译即可定位密钥/签名/隐藏接口 |
| `report` | 漏洞报告成稿收口——分层验证门把关、DOCX 提交稿（模板 + Step 式 PoC + 真实截图）、语义化命名归档 |

## 🚀 怎么使用（30 秒上手）

### 方式一：一键安装（推荐）

把下面这段提示词整段复制，粘贴给你的 Agent（DeepSeek Harness / Claude Code / Codex 等，不同框架会自动适配自己的技能加载规范），Agent 会替你完成**下载 → 安装 → 加载 → 自检**：

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

### v2（当前 main）

- **v2 成为默认主分支**：20+ 专项技能重组为 **18 个技能包**，适配 **DeepSeek Harness**；旧版 v1 保留在 [v1 分支](https://github.com/zhaji2333/CkSKILLS/tree/v1)，细节见文末《CkSKILLS v2》。
- **新增 `rules/` 纪律层**：不误拒 / 最小伤害 / 证据交付 / 多 Agent 回灌等 11 篇细则，常驻层只留每轮必须生效的铁律。
- **新增线索板 + 多 Agent 回灌约束**：`hunts/<目标>/CLUEBOARD.md` 单写者（Lead），子代理用 `dig/<角色>/SYNC.md` 五行回灌。
- **新增合板机械闸**：`tools/clueboard_sync_check.py` —— 未回灌/缺块/SYNC 晚于板 → 非零退出。

### v1 历史更新（旧版技能体系，保留在 v1 分支）

- **新增 `asc-fast-hunt`**：APK 零预处理快速定位（基于 [Droid ASC](https://github.com/MG1937/ASC)，Black Hat Europe Arsenal 工具）——秒级全局交叉引用搜索 + 按需反编译单类 + Manifest 秒读，大包不必等 JADX 全量反编译即可定位硬编码密钥/签名函数/隐藏接口；与 `apk-reversing`（脱壳还原）、`android-security-audit`（深挖验证）构成三段式 Android 链路
- **新增 `unauth-path-key-hunt`**：零身份公开面还原路径与密钥（响应指纹、加密证伪、迁域/兄弟域复查）
- **新增 `hunt-clueboard`**：当前目标 Markdown 线索板（跨轮工作记忆：读→挖→写回）
- **新增英文 README**：[`README_EN.md`](https://github.com/zhaji2333/CkSKILLS/blob/v1/README_EN.md)
- **新增 `windows-reverse-engineering`**：Windows PE 逆向与二进制漏洞深度挖掘（反汇编/反编译、内存破坏漏洞、协议逆向、反调试对抗、漏洞利用链构造）
- **新增 `android-security-audit`**：Android APK 组件安全深度审计——JADX 静态分析 + ADB 动态验证，无 Frida/无 Root 漏洞验证，对标小米 HyperOS 漏洞收录标准
- **新增 `report`**：写报告验证收口技能——分层验证门把关、按模板生成可提交 SRC/0day 平台的 DOCX 报告（Step 式 PoC + 真实截图）
- **重构 `miniprogram-security`**：原 `mobile-iot-device-security` 拆分为小程序专项（微信/支付宝/抖音 + 云开发），消除与 `android-security-audit` 的 Android 内容重复
- **新增 `apk-reversing`**：APK 脱壳与全量反编译还原（壳识别 → 脱壳 → JADX/apktool → so/H5/assets），为 `android-security-audit` 提供可直接开挖的标准源码产物
- **扩充信息收集相关 SKILLS**：
  - `recon-js-analysis` 新增 **URL/IP/域名资产扩展**（webpack/app.js/抓包中提取的地址全部进入资产测绘，APP 来源的提醒关注后台接口域名）与 **appid/appkey 凭证上报深挖**（验证有效性、打后端/云资产）
  - `android-security-audit` 支持从 APK 反编译产物中提取**后端接口域名与应用凭证**并联动深挖

## 📦 CkSKILLS v2（当前 main 分支）

> v2 把 v1 的 20+ 专项技能重组为 **18 个技能包**，并新增 `rules/` 纪律层、线索板与多 Agent 回灌约束，面向真实授权安全评估、适配 **DeepSeek Harness**。

### 结构

```
AGENTS.md                # 常驻层（4.8KB）：身份/铁律/10 秒决策/加载纪律/文件地图
rules/                   # 纪律层（11 篇，按需读；rules/40 报告规范为单篇例外 ≤8KB）
 00-priority 10-anti-refusal 15-hunting-mindset 20-min-harm 30-no-idle
 40-evidence-report 50-token-economy 60-scope-iteration
 65-task-dir 66-agent-teams  # 66 = 多 agent：单写者 + SYNC 回灌块 + Lead 合板
 70-routing
.agents/skills/          # 技能层：18 个技能包（短 SKILL.md + knowledge/ 小块）
kb/                      # 数据层：Vuln/Dic/Payload + INDEX（rules/55、kb-security-data；非技能正文）
 ck-router/              # 总入口：分诊 + 战法索引 + 线索板 + 失败升级 + 挖什么矩阵 + 范围迭代 + 线索表 + 心法
 web-injection/ web-auth-access/ web-file-path/ web-ssrf-render/
 web-xss-frontend/ web-api-protocol/ web-logic-race/ web-deser-xxe/
 web-recon/ web-waf-bypass/ cloud-infra/ ai-agent/ binary-re/
 mobile-app/ source-audit/
templates/CLUEBOARD.template.md   # 单目标线索板模板（含 §8 同步日志）
templates/TEAMMATE-SYNC.template.md # 子代理回灌块模板（HOST/PATH/KEY/DEAD/NEXT）
tools/clueboard_sync_check.py     # 合板闸：未回灌/缺块/SYNC 晚于板 → 非零退出
hunts/<目标>/CLUEBOARD.md         # 运行时生成：线索板（跨轮记忆）
docs/                    # ARCHITECTURE / MIGRATION / TRIGGER-MATRIX
```

### 技能包（16 个）

| 技能包 | 覆盖范围 |
|---|---|
| `ck-router` | 总入口：30 秒分诊、战法索引、线索板、失败换层 |
| `web-recon` | 资产 / JS / 接口发现、未授权路径、密钥还原 |
| `web-auth-access` | 认证 / 会话 / JWT / 验证码 / 越权（IDOR）/ 前端权限绕过 |
| `web-injection` | SQL / NoSQL / 命令 / SSTI / 表达式注入与参数 fuzz |
| `web-file-path` | 文件上传 / 下载 / 导入导出 / 预览 / 路径穿越 / 任意读写 |
| `web-ssrf-render` | SSRF / 内网 / 云元数据 / 服务端无头浏览器渲染 |
| `web-xss-frontend` | XSS / CSRF / Clickjacking / Markdown 渲染 |
| `web-api-protocol` | REST / GraphQL / gRPC / WebSocket / 网关 / HTTP 走私 / 缓存 |
| `web-logic-race` | 业务逻辑与并发竞态 |
| `web-deser-xxe` | 反序列化 / XXE / 原型污染 / JNDI / XSLT / EL / 沙箱脚本注入 |
| `web-waf-bypass` | WAF / 过滤 / 检测绕过与失败升级 |
| `cloud-infra` | 云 / 容器 / 中间件 / 运维面板 / 供应链 |
| `ai-agent` | AI / LLM / Agent / Chatbot / RAG / 沙箱 / 代码执行 |
| `binary-re` | 二进制 / 固件 / ELF / PE / 内存破坏逆向 / 桌面客户端（安装目录、协议、回环端口、CDP） |
| `mobile-app` | Android / APK / 小程序 / 移动端逆向与组件安全 |
| `internal-network` | 内网/域：域侦察、Kerberos、委派/ACL/ADCS、NTLM 中继、横向移动、隧道多跳、后渗透、持久化、内网基础设施 |
| `kb-security-data` | 结构化数据检索：CVE/影响版本/PoC、字典、载荷（数据在 `kb/`，先查 INDEX） |
| `source-audit` | 白盒代码审计与反编译产物审计 |

### 两个核心资产（不要混用）

| 资产 | 是什么 | 位置 | 用途 |
|---|---|---|---|
| **战法索引** | 全局可复用战法：认什么→打哪→怎么算成→假点 | `.agents/skills/ck-router/knowledge/战法索引-01~07` | 开局选首枪、卡住换层 |
| **线索板** | 单目标状态台账：Host/路径/密钥/证伪/焦点 | `hunts/<目标>/CLUEBOARD.md` | 开工读板、挖中写板、收工更新焦点 |

### 数据层 `kb/`（按需检索，不进默认加载）

| 目录 | 内容 | 用法 |
|---|---|---|
| `kb/vuln/` | 664 条 CVE（ai/cloud/middleware/network/web） | `kb/vuln/INDEX.md` → 单条 md |
| `kb/dict/` | 237 个字典（口令/用户/目录/子域/端口/规则，含 `_meta.yaml`） | `kb/dict/INDEX.md` → 切片读 |
| `kb/payload/` | 69 个载荷（XSS/SQLi/SSRF/上传/RCE…） | `kb/payload/INDEX.md` → 切片读 |

- 检索纪律见 `rules/55-kb-usage.md`；CVE 事实以官方公告为准、PoC 必须本地复现才进报告。
- 索引由 `python3 tools/kb_index.py` 生成，一致性校验 `--check`。

### 加载纪律（省上下文的关键）

```
线索板（开工必读 0/1/4/6 节）
 → 战法索引-0X
   → 主包 SKILL.md
     → knowledge/ 小分块
```

### 多 agent 并行（Agent Teams）——线索板怎么同步

单 agent 时靠自觉写板；多 agent 时**只靠自觉必然丢**，所以改成结构约束（`rules/66-agent-teams.md`）：

- **写者唯一**：`CLUEBOARD.md` 只由 Lead 写。子代理并发写板会互相覆盖，且没人负责判断哪条已证实。
- **子代理三动作**：开工读板（§0/§1/§4/§6）→ 干活只写 `dig/<角色>/` → 收工写 `dig/<角色>/SYNC.md`（回灌块五行）并 `send_message` 给 Lead。
- **回灌块固定五行**：`HOST / PATH / KEY / DEAD / NEXT`，每行必须带证据相对路径；没新信息写 `N/A — 原因`。
- **Lead 合板三闸**：抽查证据 → 写板 §0/§1/§2/§3/§4/§6/§7 → `§8 同步日志`记账。
- **机械闸**：`python3 tools/clueboard_sync_check.py hunts/<目标>` —— 子代理有产物没 `SYNC.md`、回灌块缺字段、或板 mtime 早于 `SYNC.md`（回灌未合板）都会非零退出。

### v2 快速使用

**方式一（推荐）**：把本目录作为工作区，DSH / Claude Code 会自动发现 `AGENTS.md` 与 `.agents/skills/`。

**方式二**：只复制技能目录：
```bash
cp -r .agents/skills ~/.claude/skills   # 或目标工作区的 .agents/skills/
```
Claude Code 若只认 `.claude/skills/`，建软链：`mkdir -p .claude && ln -s ../.agents/skills .claude/skills`

**方式三（受控评估）**：把 `AGENTS.md` + `rules/` 作为项目规则（AGENTS.md/CLAUDE.md），技能放 `.agents/skills/`。

### 更新记录

- 结构性变更（新增层/包/数据、路由与纪律改动）见 [`docs/CHANGELOG.md`](docs/CHANGELOG.md)。

### 内容维护

- 直接编辑对应技能包的 `SKILL.md` 或 `knowledge/` 小块；单块控制在 ≤12KB，超限拆成「索引 + 分段」。
- 新增/移动文件后，同步更新对应 `SKILL.md` 的知识库索引与相关引用路径。
- 保持 `AGENTS.md` ≤6.5KB、`rules/` 单篇 ≤3.3KB（`rules/40` 报告规范例外，≤8KB）、`SKILL.md` ≤4KB；技能包数量保持精简。多 agent 任务收工前必须过 `tools/clueboard_sync_check.py`。

### 当前质量指标

| 项 | 值 |
|---|---|
| 技能包 | 18 |
| 知识块 | 501（按需加载，单块 ≤12KB） |
| 数据层 `kb/` | 664 CVE + 236 字典 + 69 payload（37MB；先 INDEX 后单条，`rules/55`） |
| AGENTS.md（常驻） | 4.8KB |
| rules 总/单篇 | 31.1KB / 1.2–3.3KB（rules/40 例外 7.4KB） |
| SKILL.md | 1.5–3.3KB（全 ≤4KB） |
| 引用/体积 | 已人工核对：无死链、无超限块、无竞赛/评分语境 |
| 多 agent 合板 | `tools/clueboard_sync_check.py`（示例任务实测 PASS） |

## 🎯 设计理念

- **JS 不吃透,不发包**:信息收集先行,吃透前端再动手
- **线索板当黑板**:假设 / Host / 路径 / 密钥 / 否定证据落盘；先读后挖、当轮写回。压缩或换会话以板为准，不从主站 JS 重开一局（`hunt-clueboard`）
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
