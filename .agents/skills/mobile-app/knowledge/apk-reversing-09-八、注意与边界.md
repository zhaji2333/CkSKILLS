# 八、注意与边界

> 来源：CkSKILLS v1 `apk-reversing` §八、注意与边界（迁移至 v2 知识块）

- 脱壳/反编译仅用于**授权目标**；在线脱壳上传前确认目标已授权
- 加固对抗在升级，新壳（VMP/混淆壳）可能需要针对性方案：先跑起来抓 dex 加载点，或结合 `windows-reverse-engineering` 思路分析壳 so
- 本技能产出的是**审计输入**，不直接定级漏洞——定级交给 `android-security-audit`，成稿按 `../../../../rules/40-evidence-report.md`

---
