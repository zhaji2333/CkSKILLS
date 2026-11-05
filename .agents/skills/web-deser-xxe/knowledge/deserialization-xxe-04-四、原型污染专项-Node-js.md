# 四、原型污染专项（Node.js）

> 来源：CkSKILLS v1 `deserialization-xxe` §四、原型污染专项（Node.js）（迁移至 v2 知识块）

```
__proto__ / constructor.prototype / constructor.prototype.__proto__
```

### 触发场景
- JSON.parse 后深合并（lodash.merge、Object.assign 递归合并）
- 配置合并、查询参数合并

### 利用思路
- 污染 `__proto__.isAdmin=true` / `__proto__.shell=...`
- 污染 `__proto__.env`（pug/ejs 模板引擎 RCE）
- 污染 `Object.prototype` 影响全局校验逻辑
