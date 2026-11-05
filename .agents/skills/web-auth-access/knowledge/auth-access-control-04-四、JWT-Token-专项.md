# 四、JWT/Token 专项

> 来源：CkSKILLS v1 `auth-access-control` §四、JWT/Token 专项（迁移至 v2 知识块）

- 弱密钥爆破（`jwt_tool` / hashcat）
- alg 混淆：`RS256→HS256`，用公钥当私钥签名
- 过期 token 是否仍可用、注销是否失效
- 重放测试：同 token 多端使用、跨环境使用
- 签名算法是否强制校验（none 算法）
