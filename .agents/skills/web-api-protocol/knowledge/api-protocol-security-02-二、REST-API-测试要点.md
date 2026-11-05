# 二、REST API 测试要点

> 来源：CkSKILLS v1 `api-protocol-security` §二、REST API 测试要点（迁移至 v2 知识块）

- 每个接口测试全部 HTTP 方法（GET/POST/PUT/DELETE/PATCH/OPTIONS）
- 每个参数测试：正常值、空值、边界值、类型混淆、数组化、超长、特殊字符
- 鉴权测试：有 token/无 token/过期 token/其他用户 token
- 隐藏参数/调试参数全部尝试（debug=1、test=1、_method=PUT）
- BOLA（对象级授权）：遍历资源 ID、批量参数
- 速率限制：登录、验证码、短信、转账接口是否可绕过（IP/Header 伪造）
