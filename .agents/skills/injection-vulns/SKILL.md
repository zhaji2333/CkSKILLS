---
name: injection-vulns
description: 当发现参数拼接SQL、动态排序/筛选、JSON查询条件可控、模板渲染、命令执行点、搜索/统计/自动补全接口时调用，进行SQL/NoSQL/命令/SSTI/表达式注入的深度挖掘。命中场景：搜索框、排序参数、登录绕过、导出条件、文件名参数、模板/报表生成、爬虫URL参数。
---

# injection-vulns — 注入类漏洞专项深度挖掘

## 何时调用（触发条件）

- 参数直接拼接到 SQL / NoSQL 查询（搜索、筛选、排序、分页、导出条件）
- JSON 查询条件可控（`{"$gt":0}` 等 MongoDB 风格）
- 用户输入进入 shell 命令（exec/system/ProcessBuilder、ping/curl/文件名拼接）
- 用户输入进入模板引擎（Jinja2/Velocity/Freemarker/Thymeleaf）
- 用户输入进入表达式解释器（SpEL/OGNL/EL/MVEL）
- 危险函数出现在代码审计结果中（见 `source-code-audit`）

## 一、漏洞类型全景

| 类型 | 危险函数/场景 | 挖掘要点 |
|---|---|---|
| C1. SQL注入 | 拼接SQL、动态排序 | 响应差异验证（错误/延迟/条数） |
| C2. NoSQL注入 | JSON查询条件可控 | 类型替换、全量查询 |
| C3. 命令注入 | exec/system/ProcessBuilder | shell拼接、管道符 |
| C4. 模板注入（SSTI） | Jinja2/Velocity/Freemarker | 用户输入进入模板渲染 |
| C5. 表达式注入 | SpEL/OGNL/EL | 可控片段进入解释器 |

## 二、常见场景清单（搜索/查询类）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 站内搜索 | SQL注入/XSS/信息泄露 | 搜索词拼接、搜索结果反射 |
| 高级筛选/排序 | SQL注入/NoSQL注入 | order by注入、筛选条件可控 |
| 自动补全/联想 | 信息泄露/用户枚举 | 补全接口泄露敏感数据 |
| 数据统计/图表 | SQL注入/越权 | 统计维度可控、跨权限聚合 |
| ES/Solr搜索 | 查询注入/未授权 | DSL注入、搜索接口暴露 |

## 三、接口 Fuzz 技巧（参数污染与类型混淆）

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

## 四、SQL 注入绕过技术

```
大小写：SeLeCt / 双写：selselectect
注释：/**/、/*!*/、--+、#
编码：URL编码、十六进制、Unicode
等价函数：substr→mid、ascii→ord
```

## 五、命令注入绕过技术

```
分隔符：| / || / & / && / ; / %0a
空格：${IFS} / $IFS$9 / %09 / {cat,/etc/passwd}
通配符：/???/??t /etc/passwd
```

## 六、验证要点

- **响应差异对比**：基线请求 vs 注入请求的状态码/响应大小/错误信息/响应时间
- **时间盲注**：`SLEEP(5)` / `pg_sleep(5)` / `WAITFOR DELAY '0:0:5'` 验证
- **报错注入**：`updatexml` / `extractvalue` / 类型转换错误
- **NoSQL**：`{"$ne":null}`、`{"$where":"1==1"}`、数组/类型替换
- **SSTI**：`{{7*7}}`、`${7*7}`、`<%= 7*7 %>` 探测
- **命令注入**：`id`、`whoami`、DNSLog 外带
- 所有注入点至少尝试到 Level 4 绕过（见 CLAUDE.md 1.1 第五节）

## 七、修复建议

- SQL：预编译/参数化查询，动态排序用白名单映射
- NoSQL：禁止 `$` 运算符进入查询条件，类型强校验
- 命令：白名单命令 + 参数数组传递，禁止 shell 拼接
- SSTI：模板引擎关闭危险特性（Jinja2 禁用 `__class__` 链）
- 表达式：禁止用户可控片段进入 SpEL/OGNL/EL 解释器

## 八、输出与报告要点

- 完整 PoC（curl 命令），标注注入点参数与 payload
- 差异对比证据（基线响应 vs 注入响应）
- 影响面：可读取的库表、可执行的命令、可拿到的数据量
- 根因分析：输入点 → 传播链 → Sink

