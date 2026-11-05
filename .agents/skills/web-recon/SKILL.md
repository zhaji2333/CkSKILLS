---
name: web-recon
description: 资产/JS/接口发现与未授权路径、密钥还原专项。当开始新目标、找不到接口、需要从 JS 提取 API/密钥/隐藏功能、或需要零身份找路径与密钥时调用。
---

# web-recon — 资产/JS/接口发现与未授权路径、密钥还原专项

## 何时调用

- 新目标/攻击面不清晰
- 找接口/隐藏功能/密钥
- JS/webpack/source map 分析
- 零身份未授权路径
- 子域/历史资产/备份泄露

## 30 秒分诊

1. 先收集：域名/IP/端口/指纹/证书/历史快照/JS 文件
2. JS 全量下载 → 提取接口、参数、密钥、隐藏路由
3. 零身份：按 5 源找路径，按指纹分流（302/405/空数组/NXDOMAIN）
4. 密钥/加密参：还原公钥/盐/签名算法后重打

## 首枪顺序

- JS 拆包：webpack chunk/source map 还原，提 API 与硬编码密钥
- 目录 fuzz：备份/`.git`/`/db`/`/admin`/`/actuator`
- 未授权路径：从同 IP 兄弟域/旧版本/移动端 API 还原
- 加密参数：getRsaKey/JSEncrypt → 取公钥自己加密
- 子域接管：CNAME 指向未占用服务
- 公开面找 key：GitHub/文档/招聘/公开 S3
- JS 里注释/atob/base64 藏口令与隐藏路由

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/recon-js-analysis-03-三、JS-分析方法论-必须吃透再动手.md` | JS 分析方法论 | 4.2KB |
| `knowledge/js-reverse-guide.md` | JS 逆向实战指南 | 5.3KB |
| `knowledge/recon-methodology.md` | 资产测绘/历史/周边 | 13.4KB |
| `knowledge/unauth-path-key-hunt-06-P3-路径发现五源-并行.md` | 零身份路径五源 | 1.1KB |
| `knowledge/subdomain-takeover-test.md` | 子域接管 | 9.6KB |
| `knowledge/insecure-scm-test.md` | 源码/备份泄露 | 5.2KB |
| `knowledge/recon-js-analysis-04-四、高价值入口点定位.md` | 高价值入口点 | 0.4KB |

其余 16 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-auth-access` / `web-file-path` / `web-waf-bypass`

