---
name: web-deser-xxe
description: 反序列化/XXE/原型污染/JNDI/XSLT/EL/沙箱脚本注入专项。当出现 XML/SOAP/序列化对象/JSON 深合并/yaml.load/不可信反序列化入口时调用。
---

# web-deser-xxe — 反序列化/XXE/原型污染/JNDI/XSLT/EL/沙箱脚本注入专项

## 何时调用

- XML 导入/SOAP/Office/Excel 解析
- Java/PHP/Python/.NET 反序列化
- JSON 深合并/`__proto__`/原型污染
- JNDI/LDAP/EL/XSLT 表达式
- sandbox 脚本（Groovy/JS）

## 30 秒分诊

1. 确认数据格式与解析库（报错栈/响应头/JS 特征）
2. 先打 XXE（最简单）：外部实体读文件
3. 反序列化：找 gadget 链与白名单边界
4. 原型污染：找 merge/set 的可控路径

## 首枪顺序

- XXE：`<!ENTITY x SYSTEM "file:///etc/passwd">` → 回显字段
- XXE 被 WAF 拦 → UTF-16/BOM、参数实体、SVG/Office 包装
- Java 反序列化：ysoserial gadget / TemplatesImpl / SignedObject
- PHP：phar 反序列化 + 文件操作触发；Python：pickle `__reduce__`
- 原型污染：`__proto__`/`constructor.prototype` 污染配置/模板
- JNDI：`${jndi:ldap://...}` 打 log4j 类
- 表达式/模板：SpEL `T(java.lang.Runtime)`、EL `${...}`、XSLT 扩展函数
- 沙箱脚本（Groovy/JS）：逃逸后命令执行（见 ai-agent）

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/deserialization-xxe-02-二、反序列化专项.md` | 反序列化总览与链 | 0.8KB |
| `knowledge/deserialization-xxe-03-三、XXE-专项.md` | XXE 专项 | 0.7KB |
| `knowledge/deserialization-test.md` | 真实 SRC 反序列化实战大全 | 0.6KB |
| `knowledge/xxe-test.md` | XXE 进阶（盲打/带外/OOB） | 0.4KB |
| `knowledge/prototype-pollution-test.md` | 原型链污染 | 0.5KB |
| `knowledge/jndi-injection-test.md` | JNDI 注入 | 8.2KB |
| `knowledge/el-injection-test.md` | EL 表达式注入 | 7.2KB |
| `knowledge/groovy-sandbox-exec-test.md` | Groovy 沙箱逃逸 | 2.2KB |

其余 13 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-injection` / `ai-agent` / `source-audit`

