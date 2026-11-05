# 联动

> 来源：CkSKILLS v1 `asc-fast-hunt` §联动（迁移至 v2 知识块）

- 上游输入：APK 获取与壳识别/脱壳 → `apk-reversing`（有壳必走）
- 下游挖洞：密钥追踪→未授权接口、组件安全深挖、动态验证 → `android-security-audit`
- 接口域名清单 → `recon-js-analysis`（资产测绘）、`api-protocol-security`（API 测试）
- 云服务凭证（AK/SK/bucket）→ `cloud-infra-supply-chain`
- SO 层密钥（native 取密钥时）→ `apk-reversing` 五、IDA 9.5 无头 + MCP 路径 + `android-security-audit` 1.3 / 三、Native 深挖
- **ASC→IDA 抄近路**：大包已明确 Java 调用点、只需确认 native 算法/实现 → 定位后**直接转 `android-security-audit` 三、Native 深挖（IDA 9.5 无头）**，不付 JADX 全量成本（分流规则见 `../../../../AGENTS.md` 3.1）
- 跨轮线索留存 → `hunt-clueboard`（`hunts/<目标>/CLUEBOARD.md`）
- 正式报告 → 按 `../../../../rules/40-evidence-report.md`输出
