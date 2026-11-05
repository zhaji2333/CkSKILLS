# 三、GraphQL 专项

> 来源：CkSKILLS v1 `api-protocol-security` §三、GraphQL 专项（迁移至 v2 知识块）

- **内省查询**：`{__schema{types{name}}}` 是否开放
- **深度攻击**：嵌套查询（friends 循环）造成 DoS
- **别名批量**：同一查询别名多次执行绕过速率限制
- **批量枚举**：`user(id:1)` 遍历获取数据
- **越权**：字段级权限缺失（隐藏字段可查）
