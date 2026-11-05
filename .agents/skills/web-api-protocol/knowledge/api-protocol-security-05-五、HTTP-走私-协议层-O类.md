# 五、HTTP 走私 / 协议层（O类）

> 来源：CkSKILLS v1 `api-protocol-security` §五、HTTP 走私 / 协议层（O类）（迁移至 v2 知识块）

- 反向代理解析差异（Content-Length vs Transfer-Encoding）
- 请求边界混淆 → 前置代理放行、后端走私
- 测试工具：`smuggler` / Burp 扩展
- 影响：缓存投毒、绕过鉴权、越权访问其他用户请求
