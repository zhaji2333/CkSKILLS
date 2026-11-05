# 六、CSRF 专项

> 来源：CkSKILLS v1 `xss-frontend-security` §六、CSRF 专项（迁移至 v2 知识块）

### 场景
- 资金操作、绑定账号、敏感配置

### 挖掘
- CSRF Token 缺失
- Referer/Origin 可绕过（空 Referer、跨子域、`https://evil.com.trusted.com`）
- Token 不绑定会话（固定 token 可重用）
- GET 请求执行敏感操作

### 修复
- Token、SameSite、二次确认
