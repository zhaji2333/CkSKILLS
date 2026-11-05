# 二、反序列化专项

> 来源：CkSKILLS v1 `deserialization-xxe` §二、反序列化专项（迁移至 v2 知识块）

### 各语言危险入口
```
Java:   readObject / XMLDecoder / JNDI lookup / JdbcRowSetImpl / TemplatesImpl
PHP:    unserialize / phar反序列化
Python: pickle.loads / yaml.load(Loader=Loader)
.NET:   BinaryFormatter / XMLSerializer
```

### 利用工具
| 语言 | 工具 |
|---|---|
| Java | ysoserial / marshalsec（RMI/LDAP 起服务） |
| PHP | phpggc |
| Python | pickle 手工构造 |

### 利用链思路
- Java：Gadget 链（CommonsCollections、CommonsBeanutils 等）→ RMI/LDAP 打 JNDI
- PHP：POP 链（Laravel/ThinkPHP/Yii 框架 gadget）+ phar 协议触发
- Python：pickle 反序列化执行命令
- 入口识别：base64/hex 编码的序列化流、`rO0AB`（Java）、`a:{}`（PHP）、`O:8:`（PHP对象）
