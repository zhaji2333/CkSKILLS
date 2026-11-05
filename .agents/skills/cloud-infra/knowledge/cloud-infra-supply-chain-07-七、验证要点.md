# 七、验证要点

> 来源：CkSKILLS v1 `cloud-infra-supply-chain` §七、验证要点（迁移至 v2 知识块）

- 未授权访问：默认路径/默认端口直接访问是否 200
- 弱口令：先试默认凭证（admin:admin、root:root）
- 云配置：公开桶可读/写、预签名 URL 可遍历
- 信息泄露：泄露的数据能否用于下一步（密码、AK/SK、内部域名）
- 供应链：版本 → CVE 匹配 → 可利用性验证
- 云凭据：STS 只用只读 API 验证有效性（GetCallerIdentity/列举），不执行破坏性操作
