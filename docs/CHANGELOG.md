# 更新记录（CHANGELOG）

> 只登记**结构性变更**：新增层/包/数据、路由与纪律改动、批量修复。技能正文的日常小改直接改对应 `SKILL.md` / `knowledge/`，不在这里登记。
> 版本写法：`v2.<minor> — 日期：一句话主题`。

---

## v2.1 — 2026-11-17：结构化数据层 + 内网/云扩包

### 一句话

新增 `kb/` 结构化数据层（664 CVE / 237 字典 / 69 载荷），新增内网/域技能包 `internal-network`（10 块）与数据检索包 `kb-security-data`，`cloud-infra` 扩充 10 块；全局路由、纪律、索引同步接线；顺手修掉 7 个超限知识块与存量死链。

### 1. 新增

#### 1.1 数据层 `kb/`

| 目录 | 内容 | 规模 | 索引 |
|---|---|---|---|
| `kb/vuln/` | CVE / 漏洞条目，5 分类（ai 24 / cloud 5 / middleware 436 / network 20 / web 179） | 664 条，1.76MB；CRITICAL 434 / HIGH 169 / MEDIUM 61 | `kb/vuln/INDEX.md` + `kb/vuln/INDEX-middleware.md` |
| `kb/dict/` | 口令 / 用户 / 目录 / 子域 / 端口 / 规则字典 | 237 个数据文件（+68 `_meta.yaml`），3,683,648 行，34.25MB | `kb/dict/INDEX.md`（含每文件行数/用途/标签） |
| `kb/payload/` | XSS / SQLi / SSRF / LFI / RCE / 上传等载荷，15 分类 | 69 个数据文件（+19 `_meta.yaml`），22,031 行，1.08MB | `kb/payload/INDEX.md` |

- 合计 1,062 个文件、约 37.1MB（磁盘占用约 40MB）。
- 生成/校验脚本：`tools/kb_index.py`（纯标准库）。生成 4 个索引；`--check` 校验索引与数据一致（不一致退出码 1）。
- 使用纪律：`rules/55-kb-usage.md` + 技能包 `kb-security-data`。**不参与默认加载**，先 INDEX 后单条/切片。
- 边界：CVE 事实以厂商公告/NVD 为准，PoC 必须本地复现；字典/载荷是原料不是证据。

#### 1.2 新技能包 `internal-network`（内网 / 域，10 块约 76KB）

| 块 | 覆盖 | 大小 |
|---|---|---|
| `.agents/skills/internal-network/knowledge/internal-01-域侦察与决策树.md` | 域环境判据、SRV/DNS、枚举工具、凭据决策树 | 5.2KB |
| `.agents/skills/internal-network/knowledge/internal-02-Kerberos与票据攻击.md` | Kerberoast / AS-REP / Timeroast / noPac / RODC | 7.6KB |
| `.agents/skills/internal-network/knowledge/internal-03-委派-ACL-ADCS.md` | 三类委派、RBCD、ACL 掩码与滥用、ADCS ESC1–ESC11 | 7.5KB |
| `.agents/skills/internal-network/knowledge/internal-04-凭据-中继-投毒.md` | 中继面判定、Responder/mitm6、强制认证、ntlmrelayx | 6.2KB |
| `.agents/skills/internal-network/knowledge/internal-05-横向移动.md` | PTH/PTT、psexec/wmiexec/dcomexec、跨库横向 | 5.5KB |
| `.agents/skills/internal-network/knowledge/internal-06-隧道与多层网络.md` | frp/chisel/SSH 多跳、SOCKS、proxychains 边界 | 6.5KB |
| `.agents/skills/internal-network/knowledge/internal-07-后渗透与提权.md` | Linux/Windows 后渗透与提权决策树、凭据提取 | 8.1KB |
| `.agents/skills/internal-network/knowledge/internal-08-持久化与痕迹.md` | Golden/Silver/DSRM/AdminSDHolder、主机持久化、痕迹处理 | 8.7KB |
| `.agents/skills/internal-network/knowledge/internal-09-内网基础设施打法.md` | 产品→默认弱点→验证动作总表（Exchange/SCCM/OA/DB/中间件/CI 平台） | 11.4KB |
| `.agents/skills/internal-network/knowledge/internal-10-工具投递与规避.md` | 工具投递全通道、落地隐蔽、免杀流程 | 8.8KB |

- 首枪表：`.agents/skills/ck-router/knowledge/战法索引-08-内网与域.md`（22 行「认什么｜打哪｜算成｜假点」）。
- 触发词：内网 / 域 / AD / Kerberos / 委派 / ACL / ADCS / 横向 / 隧道 / 后渗透。

#### 1.3 新技能包 `kb-security-data`

- 30 秒分诊表：CVE/影响版本/PoC → `kb/vuln/INDEX.md`；字典 → `kb/dict/INDEX.md`；payload → `kb/payload/INDEX.md`。
- 检索纪律 4 条（先 INDEX、只取行段、单条只读、结论落板）+ 证据纪律 3 条（官方为准、本地复现、原料非证据）。

#### 1.4 `cloud-infra` 扩展（+10 块约 85KB）

| 块 | 覆盖 |
|---|---|
| `.agents/skills/cloud-infra/knowledge/cloud-01-多云资产与攻击面概览.md` | 六云对比（资产形态/指纹/元数据地址/凭据前缀/首枪） |
| `.agents/skills/cloud-infra/knowledge/cloud-02-AWS攻击面与IAM提权.md` | 凭据时间窗、策略危险模式、46 服务按 12 服务族归并的提权表、横向/持久化 |
| `.agents/skills/cloud-infra/knowledge/cloud-03-Azure与GCP.md` | Entra/ARM 两层授权、混合身份、云→本地 AD 穿越、GCP SA/Workspace |
| `.agents/skills/cloud-infra/knowledge/cloud-04-国内云.md` | 阿里/腾讯/华为：OSS/COS/OBS、元数据差异、AK/SK、RAM/CAM/IAM 提权 |
| `.agents/skills/cloud-infra/knowledge/cloud-05-云凭据-IAM-元数据.md` | 凭据格式、五云元数据与 Header、IMDSv2/SSRF 绕过、元数据→STS 横向 |
| `.agents/skills/cloud-infra/knowledge/cloud-06-K8s攻击面-逃逸与集群.md` | 逃逸判定矩阵、内核/运行时 CVE、集群端口、RBAC、CVE-2025-1974 |
| `.agents/skills/cloud-infra/knowledge/cloud-07-K8s攻击面-组件-网络-存储.md` | DNS 命名、策略引擎、NetworkPolicy 盲区、共享存储、Webhook |
| `.agents/skills/cloud-infra/knowledge/cloud-08-容器运行时与镜像.md` | Docker API/Registry/镜像层取证、服务网格（Envoy/Linkerd） |
| `.agents/skills/cloud-infra/knowledge/cloud-09-对象存储与Serverless.md` | 桶误配四问、版本/DeleteMarker 取证、云函数执行身份与触发器面 |
| `.agents/skills/cloud-infra/knowledge/cloud-10-CICD与供应链与IaC.md` | Jenkins/Actions/GitLab 凭据外带、tfstate、Harbor、ArgoCD |

- `.agents/skills/cloud-infra/SKILL.md` 同步更新：description、何时调用、30 秒分诊、首枪顺序、知识库索引（14 行）。

#### 1.5 其它新增

- `rules/55-kb-usage.md`：数据层使用纪律（何时查 / 检索 / 证据 / 维护 / 与线索板配合）。
- `templates/SEEDS.template.md`：自由跳模式的种子队列模板（此前 rules/60、65 只写了要求、没有模板）。

### 2. 变更（全局接线）

| 文件 | 变更 |
|---|---|
| `AGENTS.md` | 10 秒决策 +2 行（内网→`internal-network`、CVE/字典/payload→`kb-security-data`）；铁律 5 增 kb 指引；文件地图：rules 11→12、技能包 16→18、新增 `kb/` 行 |
| `rules/70-routing.md` | 触发路由 +2 行（内网/域、数据检索）；开局首读 +1 行（战法索引-08） |
| `docs/TRIGGER-MATRIX.md` | 触发矩阵 +2 行 |
| `.agents/skills/ck-router/SKILL.md` | 30 秒分诊 +2 行；开局动作 +1 步（先查 kb INDEX）；知识库索引 +战法索引-08；相关 +rules/55 与新包 |
| `.agents/skills/ck-router/knowledge/进站决策.md` | 物料表 +内网行；指纹分流 +内网；CTF 导向话术改为真实评估语境 |
| `.agents/skills/ck-router/knowledge/战法索引-04-云与内网.md` | 头部交叉引用：云细节→`cloud-01~10`，内网纵深→战法索引-08 |
| `README.md` | Skills 徽章 16→18；技能包表 +2 行；新增「数据层 `kb/`」小节；质量指标更新（知识块 501、rules 31.1KB、kb 行） |
| `docs/ARCHITECTURE.md` | 五层→**六层**（新增 L4 数据 `kb/`，L4 状态改 L5）；18 包全覆盖；质量表 +kb 索引校验 |

### 3. 修复（存量问题）

**3.1 超 12KB 知识块拆分（7 个 → 14 个文件，索引保留原文件名 + `-b` 分段）**

| 原块 | 拆分后：原文件 + `-b` 分段（字节） |
|---|---|
| `.agents/skills/web-recon/knowledge/recon-methodology.md` | 8059 + 5985（`-b`） |
| `.agents/skills/web-auth-access/knowledge/oauth-jwt-test-p1.md` | 8519 + 5196（`-b`） |
| `.agents/skills/web-api-protocol/knowledge/http-smuggling-test-p1.md` | 7410 + 6219（`-b`） |
| `.agents/skills/web-api-protocol/knowledge/http-smuggling-test-p2.md` | 7422 + 5242（`-b`） |
| `.agents/skills/web-file-path/knowledge/file-upload-test.md` | 8263 + 5664（`-b`） |
| `.agents/skills/web-deser-xxe/knowledge/prototype-pollution-test-p2.md` | 7583 + 5450（`-b`） |
| `.agents/skills/web-deser-xxe/knowledge/xxe-test-p1.md` | 7401 + 5286（`-b`） |

原文件末尾留指向分段的指针，外部引用保持不变；父索引（如 `http-smuggling-test.md`）已补分段行。

**3.2 引用修复**

- kb 路径（`kb/vuln/INDEX.md` 等）在 README 与 `kb-security-data` 中补全相对路径；
- `rules/66-agent-teams.md`、`rules/40-evidence-report.md`、战法索引-08 的 `internal-*` 引用改为可解析相对路径；
- 各包 `其余 N 个知识块` 兜底行按实际未列举数重算；
- `.agents/skills/ck-router/knowledge/进站决策.md` 中 CTF 导向表述（flag/题面/平台任务）改为真实授权评估语境。

### 4. 验收数据

| 项 | 结果 |
|---|---|
| 技能包 | 18（原 16） |
| 知识块 | 501（原 473；新增内网 10 + 云 10 + 拆分 7） |
| 单块 ≤12KB | 0 超限（原 7 个超限） |
| SKILL.md 体积 | 全部 ≤ 限值（`ck-router` 7KB 内，其余 4.5KB 内） |
| frontmatter | 18/18 name 与目录一致、description 30–360 字 |
| 死链（文件相对 / 仓库根双基准） | 0 |
| kb 索引一致性 | `python3 tools/kb_index.py --check` → OK（664 / 237 / 69） |
| 常驻层 | `AGENTS.md` 5.4KB（限 6.5KB） |
| 规则层 | 12 篇 31.1KB，单篇 ≤3.3KB（`rules/40` 例外） |

复跑验收：

```bash
python3 tools/kb_index.py --check
python3 - <<'PY'   # 体积/死链自检（可选，放 CI 或收工前跑）
import os,re
for dp,_,fs in os.walk(".agents/skills"):
    if os.path.basename(dp)=="knowledge":
        for f in fs:
            if f.endswith(".md") and os.path.getsize(os.path.join(dp,f))>12288:
                print("超大块:",os.path.join(dp,f))
PY
```

### 5. 怎么用（本次更新后的三条路径）

1. **新目标**：仍从 `ck-router` 分诊。内网/域 → `internal-network`；云/容器/K8s → `cloud-infra`；要 CVE/字典/payload → `kb-security-data`。
2. **查 CVE / 取字典**：先 `grep` 对应 INDEX 定位，再只读单条或切片（`sed -n` / `shuf -n`）；CVE 写进报告前必须本地复现。
3. **更新数据**：替换 `kb/` 对应目录内容（保留结构与 `_meta.yaml`）→ `python3 tools/kb_index.py` → `--check` 通过即完成。

### 6. 已知限制 / 待办

- `kb/` 约 37MB（仓库总计约 43MB）；仓库要瘦身时优先评估 `kb/dict` 下 9 个 >1MB 大表（删除后须重跑索引脚本）。
- 内网/云知识块做的是**方法论收敛**，各专题的深层参考未逐篇落入本库；需要时按块内提示继续深挖。
- 每个技能包的评测集（evals）尚未建立。
- 仓库暂无 CI；体积/死链/索引一致性目前靠本地脚本与人工复核。

### 7. 兼容性

- 旧技能包、旧路径全部保留；`kb/`、`internal-network`、`kb-security-data` 为纯增量。
- 常驻层加载体积与单轮 ≤25KB 预算不变。
- `AGENTS.md` 规则数 11→12（新增 `rules/55`），原有编号不变。
