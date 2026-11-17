# kb/ — 结构化安全数据层

> 本库自带的数据层：CVE / 字典 / 载荷，供 Agent **按需检索**。
> **不是技能正文、不参与默认加载**：先读对应 `INDEX.md`，再开单条/单文件。
> 检索纪律另见 `rules/55-kb-usage.md` 与 `kb-security-data` 技能。

## 1. 目录与规模

| 目录 | 内容 | 数据文件 | 附带 | 条目/行数 | 体积 | 索引 |
| --- | --- | --- | --- | --- | --- | --- |
| `vuln/` | CVE / 漏洞条目，5 分类（ai / cloud / middleware / network / web） | 664 个 md | — | 664 条 | 1.76 MiB | `vuln/INDEX.md`（228 行表项）+ `vuln/INDEX-middleware.md`（436 行表项） |
| `dict/` | 口令 / 用户 / 目录 / 子域 / 端口 / 规则等字典 | 237 个 | 68 个 `_meta.yaml` | 3,683,648 行 | 34.25 MiB | `dict/INDEX.md`（253 行表项） |
| `payload/` | XSS / SQLi / SSRF / LFI / RCE / 上传等载荷，15 分类 | 69 个 | 19 个 `_meta.yaml` | 22,031 行 | 1.08 MiB | `payload/INDEX.md`（69 行表项） |
| **合计** | 970 个数据文件 + 87 个 `_meta` + 4 个生成索引 + 本说明 | 970 个 | 87 个 | — | **约 37.1 MiB**（`du` 磁盘占用约 40 MB） | — |

- `vuln/` 分类计数：ai 24 / cloud 5 / middleware 436 / network 20 / web 179；severity：CRITICAL 434 / HIGH 169 / MEDIUM 61。
- `dict/` 行数取自各级 `_meta.yaml`；`payload/` 同。`*` 标记的行表示该文件 `_meta` 未收录、行数由 `wc -l` 实测（仅 2 个）。
- `INDEX*` 由 `tools/kb_index.py` 生成，**禁止手改**；数据变了就重跑脚本。

## 2. 检索纪律（必须遵守）

1. **先 INDEX 再开单条，禁止通读 `kb/`**。禁止 `ls -R kb/`、禁止一次打开多个 CVE 条目「浏览」；INDEX 是压缩表，命中后再按路径打开单个文件。
2. **CVE 证据红线**：条目里的 PoC / 影响版本必须先在授权环境**本地复现**，才可写进报告；CVE 编号、影响版本、修复版本以**厂商公告 / NVD** 为准，与条目冲突时按官方写并记录差异。未复现只能标「疑似 / 待验证」。
3. **字典 / 载荷只取需要的行段**：用 `sed -n '1,100p'`、`head`、`shuf -n 50` 分页 / 切片，不要把大文件整篇读入上下文；报告里只写「用了哪类字典 / 载荷 + 命中结果」，字典和载荷本身不是证据。
4. **结论落盘**：查到的 CVE / 字典结论写进线索板或报告，并带 `kb/vuln/<分类>/<ID>.md` 这类相对路径作证据指针；未命中记一行「查过 kb：<关键词> 无结果」，避免下轮重复查。

## 3. 常用检索命令

```bash
# 1) 找 CVE / 产品（先 INDEX）
grep -i "weblogic" kb/vuln/INDEX.md kb/vuln/INDEX-middleware.md
grep -i "CVE-2023-46604" kb/vuln/INDEX*.md

# 2) 读单条（只读该条，别浏览）
sed -n '1,80p' kb/vuln/middleware/activemq/CVE-2023-46604.md

# 3) 找字典 / 载荷（按路径、描述、用途、标签都可 grep）
grep -i "shiro" kb/dict/INDEX.md
grep -i -E "ssrf|云元数据" kb/payload/INDEX.md

# 4) 切片使用字典
sed -n '1,100p' kb/dict/web/directory/common.txt
shuf -n 50 kb/dict/auth/password/password-top1000.txt

# 5) 全库关键词（只用 grep，不通读）
grep -ril "nacos" kb/vuln/
```

## 4. 大文件：只切片，别整读

`dict/` 里 9 个 >1 MiB 的字典（行数取自 INDEX）：

| 文件（相对 `kb/dict/`） | 大小 | 行数 |
| --- | --- | --- |
| `web/webshell/webshell-pass.txt` | 3.33 MiB | 437,951 |
| `web/middleware/shiro/key.txt` | 2.41 MiB | 101,148 |
| `regular/letter/upper-4char.txt` | 2.18 MiB | 456,976 |
| `regular/letter/lower-4char.txt` | 2.18 MiB | 456,976 |
| `auth/password/wpa/top200000-wpa.txt` | 2.02 MiB | 203,806 |
| `web/directory/asp/asp-directory.txt` | 1.41 MiB | 60,721 |
| `web/directory/aspx/aspx-directory.txt` | 1.39 MiB | 46,191 |
| `web/dns/dns.txt` | 1.18 MiB | 151,548 |
| `auth/password/complex/complex-6char-three-of-four.txt` | 1.04 MiB | 107,960 |

> 所有字典 / 载荷都按行段读；如仓库需要瘦身，优先评估这些大表（删除后必须重跑生成脚本）。

## 5. 更新方式（替换数据 + 重建索引）

```bash
# 1) 替换三个数据目录内容（保留目录结构与 _meta.yaml）：可手工增改，也可从外部语料同步
# 2) 重建索引（仅标准库；macOS 自带 python3 可直接跑）
python3 tools/kb_index.py

# 3) 校验（数据/INDEX 不一致时退出码 1，可加进 CI 或收工校验链）
python3 tools/kb_index.py --check
```

- 覆盖替换会删掉旧 `INDEX.md`，第 2 步会重建；第 3 步通过即完成。
- 新增或删除数据文件、修改 `_meta.yaml` 后同样必须重跑脚本；`--check` 失败说明「索引过期」或「`_meta.yaml` 引用了不存在的文件」，按提示处理。

## 6. 维护约定

- `vuln/INDEX.md`、`vuln/INDEX-*.md`、`dict/INDEX.md`、`payload/INDEX.md` 均为生成物，勿手改；
- 单分类漏洞条目 >200 行时脚本自动拆成 `vuln/INDEX-<分类>.md`，主 INDEX 只留计数与链接；
