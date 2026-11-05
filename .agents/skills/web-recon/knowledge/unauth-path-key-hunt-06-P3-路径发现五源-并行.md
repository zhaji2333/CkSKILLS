# P3 路径发现五源（并行）

> 来源：CkSKILLS v1 `unauth-path-key-hunt` §P3 路径发现五源（并行）（迁移至 v2 知识块）

优先级从「更像零身份攻击者」到「更脏」。webpack/脏收集操作见 `recon-js-analysis`。

| 源 | 做什么 | 通过信号 |
|---|---|---|
| 1 现网 JS | 首页、buildManifest、异步 chunk、baseURL | 路径或方法名字符串有公开出处 |
| 2 历史旁路 | urlscan / Wayback / CT / 第三方脚本引用的 Host | 旧 URL、CDN 活动页、发票/售后等业务词 |
| 3 兄弟域 + 同 IP | 对未解析旧 Host `--resolve` 到网关 IP | 对 Host=业务 200；错 Host=网关 404/403 |
| 4 命名习惯 | 有第一段后续猜：`/{svc}/{module}/{method}/{id}`、`/gp/{ctx}/{action}`、`ForFree`/`open`/`anon` | 405 或业务 JSON |
| 5 包 | C 端 Web 没有的方法名 | 交给 android / miniprogram，产物回到本 skill 打 Host |

主站源1 为空是常态，进入源2/3，不要结案。

**通过门：** 路径字符串能指出公开出处（JS 行 / urlscan / 兄弟域指纹）。没有出处仍是假设。

---
