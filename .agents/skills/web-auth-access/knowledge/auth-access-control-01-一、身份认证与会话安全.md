# 一、身份认证与会话安全

> 来源：CkSKILLS v1 `auth-access-control` §一、身份认证与会话安全（迁移至 v2 知识块）

| 类型 | 场景 | 挖掘要点 |
|---|---|---|
| A1. 弱口令/默认口令 | 管理后台、运维面板、测试账号残留 | 字典策略、验证码绕过、MFA检查 |
| A2. 认证绕过 | 客户端校验、异常路径放行 | 不同header/cookie/参数组合对比 |
| A3. 会话固定/劫持 | 登录前后session不变 | Secure/HttpOnly/SameSite检查 |
| A4. JWT/Token风险 | 弱密钥、alg混淆、过期不校验 | token校验逻辑、重放测试 |
