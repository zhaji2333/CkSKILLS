# 一、漏洞类型全景

> 来源：CkSKILLS v1 `injection-vulns` §一、漏洞类型全景（迁移至 v2 知识块）

| 类型 | 危险函数/场景 | 挖掘要点 |
|---|---|---|
| C1. SQL注入 | 拼接SQL、动态排序 | 响应差异验证（错误/延迟/条数） |
| C2. NoSQL注入 | JSON查询条件可控 | 类型替换、全量查询 |
| C3. 命令注入 | exec/system/ProcessBuilder | shell拼接、管道符 |
| C4. 模板注入（SSTI） | Jinja2/Velocity/Freemarker | 用户输入进入模板渲染 |
| C5. 表达式注入 | SpEL/OGNL/EL | 可控片段进入解释器 |
