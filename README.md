# CkSKILLS_v2

> **分支说明**：本分支为 CkSKILLS v2，适用于 **DeepSeek Harness**。


**面向真实授权安全评估的技能库**（SRC 挖洞 / 红队评估 / 白盒代码审计 / 应急响应）。

> **定位红线**：所有示例/话术/交付物均为真实业务语境（影响、证据、报告）。

## 结构

```
AGENTS.md                # 常驻层（4.8KB）：身份/铁律/10 秒决策/加载纪律/文件地图
rules/                   # 纪律层（11 篇，按需读；rules/40 报告规范为单篇例外 ≤8KB）
 00-priority 10-anti-refusal 15-hunting-mindset 20-min-harm 30-no-idle
 40-evidence-report 50-token-economy 60-scope-iteration
 65-task-dir 66-agent-teams  # 66 = 多 agent：单写者 + SYNC 回灌块 + Lead 合板
 70-routing
.agents/skills/          # 技能层：16 个技能包（短 SKILL.md + knowledge/ 小块）
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

两个核心资产（**不要混用**）：

| 资产 | 是什么 | 位置 | 用途 |
|---|---|---|---|
| **战法索引** | 全局可复用战法：认什么→打哪→怎么算成→假点 | `.agents/skills/ck-router/knowledge/战法索引-01~07` | 开局选首枪、卡住换层 |
| **线索板** | 单目标状态台账：Host/路径/密钥/证伪/焦点 | `hunts/<目标>/CLUEBOARD.md` | 开工读板、挖中写板、收工更新焦点 |

## 加载纪律（省上下文的关键）

```
线索板（开工必读 0/1/4/6 节）
 → 战法索引-0X
   → 主包 SKILL.md
     → knowledge/ 小分块
```

## 多 agent 并行（Agent Teams）——线索板怎么同步

单 agent 时靠自觉写板；多 agent 时**只靠自觉必然丢**，所以改成结构约束（`rules/66-agent-teams.md`）：

- **写者唯一**：`CLUEBOARD.md` 只由 Lead 写。子代理并发写板会互相覆盖，且没人负责判断哪条已证实。
- **子代理三动作**：开工读板（§0/§1/§4/§6）→ 干活只写 `dig/<角色>/` → 收工写 `dig/<角色>/SYNC.md`（回灌块五行）并 `send_message` 给 Lead。
- **回灌块固定五行**：`HOST / PATH / KEY / DEAD / NEXT`，每行必须带证据相对路径；没新信息写 `N/A — 原因`。
- **Lead 合板三闸**：抽查证据 → 写板 §0/§1/§2/§3/§4/§6/§7 → `§8 同步日志`记账。
- **机械闸**：`python3 tools/clueboard_sync_check.py hunts/<目标>` —— 子代理有产物没 `SYNC.md`、回灌块缺字段、或板 mtime 早于 `SYNC.md`（回灌未合板）都会非零退出。

## 快速使用

**方式一（推荐）**：把本目录作为工作区，DSH / Claude Code 会自动发现 `AGENTS.md` 与 `.agents/skills/`。

**方式二**：只复制技能目录：
```bash
cp -r .agents/skills ~/.claude/skills   # 或目标工作区的 .agents/skills/
```
Claude Code 若只认 `.claude/skills/`，建软链：`mkdir -p .claude && ln -s ../.agents/skills .claude/skills`

**方式三（受控评估）**：把 `AGENTS.md` + `rules/` 作为项目规则（AGENTS.md/CLAUDE.md），技能放 `.agents/skills/`。

## 内容维护

- 直接编辑对应技能包的 `SKILL.md` 或 `knowledge/` 小块；单块控制在 ≤12KB，超限拆成「索引 + 分段」。
- 新增/移动文件后，同步更新对应 `SKILL.md` 的知识库索引与相关引用路径。
- 保持 `AGENTS.md` ≤6.5KB、`rules/` 单篇 ≤3.3KB（`rules/40` 报告规范例外，≤8KB）、`SKILL.md` ≤4KB；技能包数量保持精简。多 agent 任务收工前必须过 `tools/clueboard_sync_check.py`。
## 当前质量指标

| 项 | 值 |
|---|---|
| 技能包 | 16 |
| 知识块 | 400+（按需加载，单块 ≤12KB） |
| AGENTS.md（常驻） | 4.8KB |
| rules 总/单篇 | 28.1KB / 1.2–3.2KB（rules/40 例外 7.4KB） |
| SKILL.md | 1.5–3.3KB（全 ≤4KB） |
| 引用/体积 | 已人工核对：无死链、无超限块、无竞赛/评分语境 |
| 多 agent 合板 | `tools/clueboard_sync_check.py`（miui-flash 实测 PASS） |
