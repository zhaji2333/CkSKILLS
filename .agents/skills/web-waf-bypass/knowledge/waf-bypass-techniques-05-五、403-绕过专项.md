# 五、403 绕过专项

> 来源：CkSKILLS v1 `waf-bypass-techniques` §五、403 绕过专项（迁移至 v2 知识块）

```
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
路径变体：/admin/、//admin、/./admin、/admin%2f、/ADMIN
方法替换：GET→POST→OPTIONS→X-HTTP-Method-Override
分号截断：/admin;.css、/admin;.js
```
