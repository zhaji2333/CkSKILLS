# 六、云开发/云函数专项

> 来源：CkSKILLS v1 `miniprogram-security` §六、云开发/云函数专项（迁移至 v2 知识块）

- **云函数未鉴权**：`wx.cloud.callFunction({name:"任意函数名"})` 直接调用，函数内无 `cloud.getWXContext().OPENID` 身份校验 → 任意用户调管理员逻辑
- **云数据库权限**：默认权限（所有用户可读/可写）、`where` 条件可控 → 读他人数据、改他人记录
- **云存储**：公开读桶、可列举对象
- **环境切换**：env ID 可控 → 跨环境访问
- 验证：`wx.cloud.callFunction` 用他人 openid 上下文调用敏感函数，看是否拒绝

---
