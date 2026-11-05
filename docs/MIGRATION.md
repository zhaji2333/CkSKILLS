# 迁移说明

v2 由两部分构成：

1. **v1 技能拆分**：`CkSKILLS-main/.agents/skills/` 的 23 个技能 → 按章节拆为 v2 各包的 `knowledge/` 小块（报告 `docs/migration-v1-report.json`）。
2. **实战胜法并入**：`实战知识库/skills/skill/知识库/` 的实战知识库 → 按主题并入对应包（报告 `docs/migration-field-kb-report.json`）；原始战法总表保留为 `.agents/skills/ck-router/knowledge/参考-实战战法总表.md`。

## 命名与定位

- **战法索引**：全局可复用战法（认什么→打哪→怎么算成→假点），v2 自建主题索引（01–07）。
- **线索板**：单目标状态台账（`hunts/<目标>/CLUEBOARD.md`，模板 `templates/CLUEBOARD.template.md`），来自 v1 hunt-clueboard。
- **定位**：真实授权安全评估（SRC/红队/白盒审计），不面向竞赛/评分/演练演示类场景。

## 说明

迁移为一次性离线操作，脚本不随库分发；本目录只保留迁移结果与来源说明，日常直接使用与维护 `knowledge/` 与 `SKILL.md` 即可。
