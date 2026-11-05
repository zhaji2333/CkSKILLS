# 五、命令注入绕过技术

> 来源：CkSKILLS v1 `injection-vulns` §五、命令注入绕过技术（迁移至 v2 知识块）

```
分隔符：| / || / & / && / ; / %0a
空格：${IFS} / $IFS$9 / %09 / {cat,/etc/passwd}
通配符：/???/??t /etc/passwd
```
