---
name: deserialization-xxe
description: 当发现XML导入/SOAP/Office解析、序列化数据（Java/PHP/Python/.NET）、JSON深合并、yaml.load、不可信反序列化入口时调用。负责反序列化RCE链、XXE、原型污染、phpggc/ysoserial利用链构造与验证。
---

# deserialization-xxe — 反序列化与解析器漏洞专项深度挖掘

## 何时调用（触发条件）

- XML 导入/上传、SOAP 接口、Office/Excel 解析
- 序列化数据入口（Java readObject、PHP unserialize、Python pickle、.NET BinaryFormatter）
- JSON 深合并/深拷贝（Node.js 原型污染）
- yaml.load 未指定安全 Loader
- 代码审计发现危险函数（见 `source-code-audit`）

## 一、漏洞类型全景

| 类型 | 语言/场景 | 修复 |
|---|---|---|
| H1. 反序列化 | Java/PHP/Python/.NET | 禁用危险反序列化、白名单 |
| H2. XXE | XML导入、SOAP、Office解析 | 禁用外部实体 |
| H3. 原型污染 | Node.js对象合并 | 过滤危险键 |

## 二、反序列化专项

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

## 三、XXE 专项

### 基础 Payload
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<foo>&xxe;</foo>
```

### 进阶利用
- 无回显：外部 DTD + 带外（OOB）读取文件
- SSRF：`SYSTEM "http://169.254.169.254/latest/meta-data/"`
- 文件读取：`file:///etc/passwd`、`php://filter/read=convert.base64-encode/resource=config.php`
- 协议：http/ftp/gopher
- Office 文档 XXE：docx/xlsx 内 XML 注入外部实体

### 触发场景
- XML/Excel/CSV 导入
- SOAP 接口
- 文档预览/转换
- SVG 上传（图片上传点也测 XXE）

## 四、原型污染专项（Node.js）

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

## 五、验证要点

- 反序列化：先确认可控输入点与编码方式，再选 gadget 链验证 RCE
- XXE：先测回显（文件读取），无回显用 OOB DNSLog 验证
- 原型污染：控制台/接口验证 `Object.prototype` 被污染
- 每个 payload 至少尝试到 Level 4 绕过（编码/变形/协议）

## 六、修复建议

- 禁用危险反序列化或使用白名单/黑名单过滤
- XML 解析禁用外部实体（XXE 防护）
- yaml 使用 `SafeLoader`
- 深合并过滤 `__proto__`/`constructor` 键
- 输入校验：拒绝序列化对象格式（按业务白名单）

