# 三、云环境专项（14.4）

> 来源：CkSKILLS v1 `cloud-infra-supply-chain` §三、云环境专项（14.4）（迁移至 v2 知识块）

### 3.1 云元数据 → 实例角色 → STS 凭据 → 云服务横向（重点）

> 入口（SSRF/无头浏览器渲染/容器 RCE）的完整手法见 `ssrf-internal-network` 三；这里负责“拿到凭据之后”。

| 云 | 元数据/角色路径 |
|---|---|
| AWS | `169.254.169.254/latest/meta-data/iam/security-credentials/` |
| 阿里云 | `100.100.100.200/latest/meta-data/ram/security-credentials/` |
| 腾讯云 | `metadata.tencentyun.com/latest/meta-data/cam/security-credentials/` |
| K8s | `/var/run/secrets/kubernetes.io/serviceaccount/token` |

1. **取角色名**：请求 `.../security-credentials/` 返回角色名 → `.../security-credentials/<role>` 拿 STS 凭据
2. **STS 字段**：`AccessKeyId` / `AccessKeySecret`（AWS 为 `SecretAccessKey`）/ `SecurityToken` / `Expiration`；临时凭据，注意过期
3. **验身份**：阿里云 `aliyun sts GetCallerIdentity`；AWS `aws sts get-caller-identity`（只读）
4. **权限探测**：只读试探 OSS/ECS/RAM/日志等 API，找到可写/可执行权限即升级
5. **云助手横向（常见提权终点）**：角色带 `ecs:RunCommand`（阿里云助手）/ `ssm:SendCommand`（AWS SSM）/ `tat:RunCommand`（腾讯云 TAT）类权限 → 对目标或其他实例执行命令；实例 ID 从 ECS API/元数据/内网枚举
6. **可达性判定**：IMDSv1 免 token；IMDSv2/加固模式需先 `PUT /latest/api/token` 取 token；容器网络策略可能只放行元数据，先测 169.254.169.254 / 100.100.100.200 超时或 403
7. **记录**：元数据可达性、角色名（报告脱敏）、STS 权限面、横向实例清单

**定级**：元数据可读 = 高；读到 STS 且角色可横向（云助手/ECS/OSS 写）= 严重。

### 3.2 K8s / Serverless / 对象存储

| 场景 | 检查点 |
|---|---|
| Kubernetes | ServiceAccount Token 泄露、etcd 未授权、Dashboard 弱口令 |
| Serverless | 函数环境变量泄露、临时凭证获取、事件注入 |
| 对象存储 | Bucket 公开可读/写、预签名 URL 泄露、ACL 配置错误 |
| 容器 | Docker API 暴露、逃逸/提权（入口与后利用见 `agent-sandbox-takeover`） |

> 无头浏览器/截图渲染容器的典型链路：渲染器 RCE → 容器内读元数据 → 本节 3.1。入口发现与内核指纹见 `ssrf-internal-network` 三。
