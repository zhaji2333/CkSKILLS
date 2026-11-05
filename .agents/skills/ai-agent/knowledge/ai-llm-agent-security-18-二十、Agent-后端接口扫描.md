# 二十、Agent 后端接口扫描

> 来源：CkSKILLS v1 `ai-llm-agent-security` §二十、Agent 后端接口扫描（迁移至 v2 知识块）

三态对照（真/无/假 token）、缺参 400 = IDOR 信号、换 sandbox_id → **`agent-execution-channel-hijack` 第三节**。此处不重复。

懒加载 chunk 是接口富矿：主包只有核心口，管理/详情/上传多在 chunk。顺着 `import` 找 `*Api.js` 抽 `url:`。
