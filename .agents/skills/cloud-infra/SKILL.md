---
name: cloud-infra
description: 云/容器/中间件/运维面板/供应链专项。当涉及多云资产（AWS/Azure/GCP/阿里/腾讯/华为）、云凭据与元数据、K8s/容器与逃逸、对象存储、服务器面板、中间件、CI-CD/IaC、依赖供应链或配置泄露时调用。
---

# cloud-infra — 云/容器/中间件/运维面板/供应链专项

## 何时调用

- 多云资产：S3/OSS/COS/OBS 桶、ECS/VM/云函数、控制台/STS/元数据
- 云凭据：AK/SK 泄露、环境变量/.env/tfstate/CI secret 中的云凭据
- K8s：容器内立足点、逃逸条件、集群组件（kubelet/etcd/Ingress/Istio）、SA token
- 容器运行时：Docker API/Registry/镜像层/Compose 边界
- 运维面板（宝塔/1Panel/Grafana/Jenkins）与中间件未授权
- CI-CD/制品库/IaC（tfstate、Argo、Harbor）/依赖供应链

## 30 秒分诊

1. 先判**厂商与身份**：域名/元数据地址/凭据前缀（AKIA、LTAI、AKID）→ 开对应云块
2. 拿到凭据先确认身份与权限：`aws sts get-caller-identity`、`gcloud auth list`、云厂商 CLI 等价命令
3. 再枚举 IAM → 提权路径（`cloud-02`/`cloud-05`）
4. K8s 场景：容器内先判逃逸条件 → SA token → 集群组件面（`cloud-06`/`cloud-07`）
5. 未授权面：面板/中间件/对象存储/元数据接口（既有块）
6. CI/IaC/供应链：Jenkins/Actions/GitLab/tfstate/Argo/Harbor（`cloud-10`）

## 首枪顺序

- 对象存储匿名 LIST → README 找内部桶 → 读内部对象
- 云函数 `/api/functions` → 读 config 环境变量
- IMDS：`169.254.169.254/latest/meta-data/iam/security-credentials/`（AWS）、`100.100.100.200`（阿里）、`metadata.tencentyun.com`（腾讯）、`169.254.169.254` OpenStack 风格（华为）
- 凭据前缀：`AKIA`/`ASIA`（AWS）、`LTAI`（阿里）、`AKID`（腾讯）→ `sts get-caller-identity` 确认
- K8s：`kubectl auth can-i --list`、读 `/var/run/secrets/kubernetes.io/serviceaccount/token`、6443/10250/2379 探测
- 容器逃逸判定：`CapEff` 全能力/`docker.sock`/可写 hostPath/`hostPID`/`hostNetwork`
- 1Panel EntranceCode/OFBiz 默认口令/HugeGraph Gremlin 改线程名/GeoServer exec
- Redis 未授权/2375 Docker API/K8s sa token
- Jenkins `/script`、Actions secrets、tfstate/.env/CI secret → 云或仓库凭据
- 面板文件 API/计划任务/终端 → 读取敏感配置/执行命令

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/cloud-01-多云资产与攻击面概览.md` | 六云对比/指纹/首枪顺序 | 7.6KB |
| `knowledge/cloud-02-AWS攻击面与IAM提权.md` | AWS 凭据→IAM→提权→后渗透 | 9.0KB |
| `knowledge/cloud-03-Azure与GCP.md` | Azure AD/混合穿越、GCP SA/Workspace | 9.0KB |
| `knowledge/cloud-04-国内云.md` | 阿里/腾讯/华为：OSS/COS/OBS、元数据、AK/SK | 8.9KB |
| `knowledge/cloud-05-云凭据-IAM-元数据.md` | AK/SK 全链、IAM 审计、IMDSv2 | 8.3KB |
| `knowledge/cloud-06-K8s攻击面-逃逸与集群.md` | 逃逸判定、CVE、集群端口、RBAC | 8.8KB |
| `knowledge/cloud-07-K8s攻击面-组件-网络-存储.md` | DNS/策略引擎/存储/sidecar | 7.1KB |
| `knowledge/cloud-08-容器运行时与镜像.md` | Docker API/Registry/镜像/服务网格 | 8.6KB |
| `knowledge/cloud-09-对象存储与Serverless.md` | 桶误配四问/版本取证/云函数 | 7.5KB |
| `knowledge/cloud-10-CICD与供应链与IaC.md` | Jenkins/Actions/tfstate/Argo/Harbor | 8.1KB |
| `knowledge/对象存储与云元数据实战.md` | 入门实战：S3/SAS/IMDS/云函数/联邦 | 3.1KB |
| `knowledge/中间件与产品CVE实战.md` | 面板/中间件/产品 CVE | 2.3KB |
| `knowledge/info-leak-test.md` | 真实 SRC 信息泄露/中间件暴露 | 10.2KB |
| `knowledge/cloud-infra-supply-chain-03-三、云环境专项-14-4.md` | 云环境（元数据/K8s/Serverless）全景 | 2.4KB |

其余 7 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-ssrf-render`（SSRF→元数据）/ `web-auth-access`（云身份/OIDC）/ `ai-agent`
- `internal-network`（云上内网/横向/隧道）/ `kb-security-data`（产品 CVE）
