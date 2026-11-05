# 九、挖掘步骤

> 来源：CkSKILLS v1 `auth-access-control` §九、挖掘步骤（迁移至 v2 知识块）

1. **收集凭证流转**：注册→登录→找回密码→绑定→解绑，记录每个步骤的凭证传递
2. **对比测试**：A用户 token 访问 B用户资源；无 token/过期 token/伪 token 访问
3. **角色篡改**：注册时或请求中注入 role=admin / isAdmin=true / group_id
4. **对象绑定**：遍历资源 ID（订单号、用户ID、uuid），观察归属校验
5. **租户切换**：修改 tenant_id/org_id，验证跨租户访问
6. **验证码专项**：按「三、验证码安全专项」3.2 十一条手法逐项测试
7. **密码重置链**：验证码绕过 → token 预测 → 任意用户重置 → 登录目标账号
8. **OAuth/SSO**：redirect_uri 白名单绕过、state 缺失/可预测、绑定覆盖
