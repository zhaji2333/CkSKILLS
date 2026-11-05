# 一、漏洞类型全景

> 来源：CkSKILLS v1 `deserialization-xxe` §一、漏洞类型全景（迁移至 v2 知识块）

| 类型 | 语言/场景 | 修复 |
|---|---|---|
| H1. 反序列化 | Java/PHP/Python/.NET | 禁用危险反序列化、白名单 |
| H2. XXE | XML导入、SOAP、Office解析 | 禁用外部实体 |
| H3. 原型污染 | Node.js对象合并 | 过滤危险键 |
