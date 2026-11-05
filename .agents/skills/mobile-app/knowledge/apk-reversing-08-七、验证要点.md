# 七、验证要点

> 来源：CkSKILLS v1 `apk-reversing` §七、验证要点（迁移至 v2 知识块）

- JADX 打开核心类确认真实代码（截图存证）
- 交付给 `android-security-audit` 后，其快速开始 Step 2 的 grep 应能直接命中
- 壳 so 无法静态分析时，如实记录"该模块需动态追踪"，不硬编
