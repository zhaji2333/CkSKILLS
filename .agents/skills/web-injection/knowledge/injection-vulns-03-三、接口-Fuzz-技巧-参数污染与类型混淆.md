# 三、接口 Fuzz 技巧（参数污染与类型混淆）

> 来源：CkSKILLS v1 `injection-vulns` §三、接口 Fuzz 技巧（参数污染与类型混淆）（迁移至 v2 知识块）

```
参数污染：
  ?id=1&id=2  → 看哪个生效
  ?id[]=1&id[]=2 → 数组化
  ?id=1,2,3 → 批量查询

类型混淆：
  id=1 → id="1" → id={"$gt":0} → id[]=1

编码绕过：
  Unicode: \u002e\u002e/ (../)
  双重URL编码: %252e%252e%252f

隐藏参数：
  debug=1 / test=1 / admin=1
  _method=PUT / X-HTTP-Method-Override

批量操作：
  ids=1,2,3,4,5 一次查多个
  page=-1 / limit=99999 绕过分页
```
