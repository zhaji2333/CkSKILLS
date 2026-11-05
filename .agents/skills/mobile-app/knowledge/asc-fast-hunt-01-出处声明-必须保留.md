# 出处声明（必须保留）

> 来源：CkSKILLS v1 `asc-fast-hunt` §出处声明（必须保留）（迁移至 v2 知识块）

- 工具仓库：**https://github.com/MG1937/ASC**（Droid ASC，Black Hat Europe Arsenal 议题）
- 当前版本：**0.1.2.post4**（`7f25520`，2026-10-30，跟 `origin/main`）。以 `main` 为准：上游 Release 标签曾出现标签内 `pyproject` 版本号落后于 `main` 的情况
- Rust 版：上游已 1:1 重写为 [rust_ASC](https://github.com/MG1937/rust_ASC)（10× 速度、支持全量 APK 反编译）。Python 版继续平行维护；本技能工作流仍按 Python 版写，只有需要二进制或全量反编译时才评估切换
- 本 SKILL 只是对该工具的**封装与工作流编排**，工具算法与实现版权归原作者所有，未做任何代码修改
- 许可证：**Apache-2.0**（仓库根 `LICENSE`）。按该许可证使用；再分发必须保留许可证和版权声明。本技能不把上游源码打进技能包，也不声称自有
- 参考安装位置：`$HOME/tools/ASC/`（与 jadx、ida-mcp-server 并列）；如需重建见本文「环境安装与自检」
