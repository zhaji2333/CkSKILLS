---
name: cloud-infra
description: 云/容器/中间件/运维面板/供应链专项。当涉及云资产、对象存储、云元数据、K8s、服务器面板、中间件、CI-CD、依赖供应链或配置泄露时调用。
---

# cloud-infra — 云/容器/中间件/运维面板/供应链专项

## 何时调用

- 云主机/对象存储/云函数/STS/元数据
- K8s/容器/Docker API
- 运维面板（宝塔/1Panel/Grafana/Jenkins）
- 中间件未授权（Redis/OFBiz/HugeGraph 等）
- CI-CD/制品库/依赖供应链/配置泄露

## 30 秒分诊

1. 先枚举未授权面：面板/中间件/对象存储/元数据接口
2. 凭据优先：配置/环境变量/tfstate/CI secret
3. 云元数据：IMDS → role → STS → 云 API 横向
4. 中间件按产品 CVE 对号（见知识库）

## 首枪顺序

- 对象存储匿名 LIST → README 找内部桶 → 读内部对象
- 云函数 `/api/functions` → 读 config 环境变量
- IMDS：`169.254.169.254/iam/security-credentials/` → role 凭据
- 1Panel EntranceCode/OFBiz 默认口令/HugeGraph Gremlin 改线程名/GeoServer exec
- Redis 未授权/2375 Docker API/K8s sa token
- tfstate/.env/CI secret → 云或仓库凭据
- 面板文件 API/计划任务/终端 → 读取敏感配置/执行命令

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/对象存储与云元数据实战.md` | v2 实战：S3/SAS/IMDS/云函数/联邦 | 3.1KB |
| `knowledge/中间件与产品CVE实战.md` | v2 实战：面板/中间件/产品 CVE | 2.3KB |
| `knowledge/cloud-infra-supply-chain-03-三、云环境专项-14-4.md` | 云环境（元数据/K8s/Serverless） | 2.4KB |
| `knowledge/cloud-infra-supply-chain-01-一、运维-管理类场景表-全景.md` | 运维管理面全景 | 0.9KB |
| `knowledge/cloud-infra-supply-chain-05-五、供应链安全-L类.md` | 供应链安全 | 0.8KB |
| `knowledge/info-leak-test.md` | 真实 SRC 信息泄露/中间件暴露 | 10.2KB |
| `knowledge/cloud-infra-supply-chain-02-二、第三方集成类场景表-全景.md` | 第三方集成 | 0.9KB |

其余 4 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-ssrf-render` / `web-auth-access` / `ai-agent`

