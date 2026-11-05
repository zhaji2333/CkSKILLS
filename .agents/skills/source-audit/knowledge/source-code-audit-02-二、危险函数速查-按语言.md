# 二、危险函数速查（按语言）

> 来源：CkSKILLS v1 `source-code-audit` §二、危险函数速查（按语言）（迁移至 v2 知识块）

### PHP
```
eval / assert / system / exec / passthru / shell_exec / popen
include / require / file_get_contents / unserialize
preg_replace(e修饰符) / create_function / $$变量覆盖
```

### Java
```
Runtime.exec / ProcessBuilder / readObject / XMLDecoder
SpEL / OGNL / MVEL / EL表达式
JNDI lookup / JdbcRowSetImpl / TemplatesImpl
```

### Python
```
eval / exec / os.system / subprocess / pickle.loads
yaml.load(Loader=Loader) / __import__ / compile
```

### Node.js
```
eval / Function() / child_process / vm.runInContext
__proto__ / constructor.prototype（原型污染）
```

### Go
```
os/exec.Command / text/template（SSTI）
sql拼接 / 不安全的反序列化
```
