---
name: kb-security-data
description: 结构化安全数据检索（kb/）。当需要查 CVE 编号/影响版本/PoC、取密码/目录/子域/端口等字典、或取 XSS/SQLi/SSRF/上传等 payload 时调用。先查 INDEX 再开单条，禁止通读。
---

# kb-security-data — 结构化数据检索（kb/）

## 何时调用

- 要确认某产品/版本的 CVE、影响范围、公开 PoC
- 要口令/用户/目录/子域/端口/路径等字典
- 要 XSS / SQLi / SSRF / 上传 / 反序列化 / 命令注入等 payload
- 报告里要写 CVE 编号与版本区间，需要可追溯来源

## 30 秒分诊

| 你要什么 | 去哪 |
|---|---|
| CVE / 影响版本 / PoC | `../../../kb/vuln/INDEX.md` → 定位单条 → 读 `kb/vuln/<分类>/<ID>.md` |
| 字典（auth/port/web/regular…） | `../../../kb/dict/INDEX.md`（含每文件行数/用途/标签） |
| payload（xss/sqli/ssrf/upload/rce…） | `../../../kb/payload/INDEX.md` |
| 数据规模与更新方式 | `../../../kb/README.md` |

## 检索纪律（省上下文）

1. **先 INDEX 后单条**：INDEX 是压缩表，命中后再开文件；禁止通读 `kb/` 或整类目列表。
2. **只取需要的行段**：字典用 `sed -n '1,100p'` / `shuf -n 50` 切片，不要把大文件读入上下文。
3. **一条 CVE 只读该条**：不要一次开多个条目做"浏览"。
4. 同一轮不重复读同一文件；结论写进线索板。

## 证据纪律（写报告前必看）

- CVE 事实（编号/影响版本/修复版本）以**厂商公告/NVD**为准，`kb/` 只是线索源；两者冲突时以官方为准并记录差异。
- PoC 必须**本地复现**后才可写进报告；未复现的只能标"疑似/待验证"。
- 字典/载荷是工具原料，不是证据；报告里只写"用了哪类字典/载荷 + 命中结果"。

## 更新与校验

- 数据变更后跑：`python3 tools/kb_index.py`（重新生成 INDEX）
- 校验一致性：`python3 tools/kb_index.py --check`（CI/收工前可跑）

## 相关

- `web-injection` / `web-xss-frontend` / `web-file-path` / `web-deser-xxe`（payload 用到哪）
- `web-recon`（字典用到哪）、`cloud-infra`（产品 CVE 用到哪）
