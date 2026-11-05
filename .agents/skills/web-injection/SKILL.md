---
name: web-injection
description: SQL/NoSQL/命令/SSTI/表达式注入与参数 fuzz 专项。当参数拼接查询、排序筛选、JSON 查询可控、模板渲染、命令执行点、搜索/导出/自动补全接口出现时调用。
---

# web-injection — SQL/NoSQL/命令/SSTI/表达式注入与参数 fuzz 专项

## 何时调用

- 搜索/筛选/排序/分页/导出条件
- JSON 查询条件可控
- 命令拼接（ping/curl/文件名）
- 模板渲染（Jinja2/Twig/Freemarker）
- 表达式（SpEL/OGNL/EL/MVEL）

## 30 秒分诊

1. 先看回包是否随输入变化（错误/长度/时间/total）
2. 构造合法基线 → 单引号/布尔假 → 布尔真（恒真只打一枪）
3. 确认注入类型：报错/布尔/时间/UNION/堆叠
4. WAF 拦截 → 切 web-waf-bypass 的 Level 1–7

## 首枪顺序

- SQLi：`'` 报错 → `AND 1=2/1=1` 布尔 → `SLEEP()` 时间 → UNION 列数对齐
- 登录页恒 500 时优先时间盲注（SLEEP 对比）
- 列表 OR+total：假条件应空，恒真看 total 是否海量且首条是他人数据
- NoSQL：`{"$gt":0}`/`{"$ne":null}`/数组绕过
- 命令注入：`;`被拦换 `$(...)`/反引号/`%0a`/`&`/`||`
- SSTI：`{{7*7}}`→49 后打 `config.__class__.__init__.__globals__`
- 参数名未知：候选 key 一次性塞同一 JSON body / 逐 key 二分
- 固定格式参数：JSON 深合并/类型混淆/数组多值

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/injection-vulns-01-一、漏洞类型全景.md` | 全景与类型判定 | 0.6KB |
| `knowledge/injection-vulns-02-二、常见场景清单-搜索-查询类.md` | 搜索/列表场景与 total 差分 | 0.6KB |
| `knowledge/injection-vulns-03-三、接口-Fuzz-技巧-参数污染与类型混淆.md` | 参数 fuzz 与类型混淆 | 0.6KB |
| `knowledge/injection-vulns-04-四、SQL-注入绕过技术.md` | SQLi 手法与绕过 | 0.3KB |
| `knowledge/injection-vulns-05-五、命令注入绕过技术.md` | 命令注入分隔符/编码绕过 | 0.3KB |
| `knowledge/injection-test.md` | 真实 SRC 注入打法（OR+total、订阅 iframe 等） | 4.2KB |
| `knowledge/type-juggling-test.md` | 类型混淆/弱比较 | 10.8KB |

其余 1 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-waf-bypass` / `web-deser-xxe` / `web-api-protocol`

