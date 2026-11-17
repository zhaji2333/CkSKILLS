# 对象存储与 Serverless：进阶判定

> 适用：已确认目标使用 S3/OSS/COS/OBS 或云函数，需要把"疑似公开"判成"可复现的越权读写"的授权评估。入门枚举（匿名 LIST→README→内部桶、SAS/STS、`/api/functions` 读 config）见 `./对象存储与云元数据实战.md`，本块只写判定粒度与取证细节，不重复入门内容。

## 认什么

### 1. 四家指纹

| 线索 | 云 | URL 形态 |
|---|---|---|
| `x-amz-*`、`Server: AmazonS3` | AWS S3 | `BUCKET.s3.amazonaws.com` 或 `s3.REGION.amazonaws.com/BUCKET` |
| `x-oss-*`、`.aliyuncs.com` | 阿里云 OSS | `BUCKET.oss-cn-REGION.aliyuncs.com` |
| `x-cos-*`、`Server: tencent-cos`、`.myqcloud.com` | 腾讯云 COS | `BUCKET-APPID.cos.REGION.myqcloud.com`（APPID 必带） |
| `x-obs-*`、`.myhuaweicloud.com` | 华为云 OBS | `BUCKET.obs.REGION.myhuaweicloud.com` |

```bash
curl -sI https://TARGET_URL | grep -iE 'x-amz|x-oss|x-cos|x-obs|AmazonS3|aliyuncs|myqcloud|tencent-cos'
```

### 2. 把"桶公开"拆成四问

| 问题 | 判定请求 | 结论口径 |
|---|---|---|
| 能否匿名 LIST | `GET /?list-type=2` | 200 且 XML 含 `<Key>` = 可枚举 |
| 能否匿名 READ | 对已知 Key `GET /<key>` | 200 + 内容才对 |
| 能否匿名 WRITE | PUT canary 对象 | 200 且回读一致才算 |
| 根因在哪 | `GET /?acl`、`GET /?policy` | `AllUsers` / `Principal: "*"` |

- **LIST 与 READ 必须分开写**：常见形态是桶不可列，但前端 JS、日志、报错页里泄露的对象名可直读——影响表述为"已知对象未授权读取"，不是"桶公开"。
- 版本与删除标记：`GET /?versions`（ListObjectVersions）。存在 `DeleteMarker` 而旧 `versionId` 仍 `GET /<key>?versionId=` 200，说明逻辑删除未销毁数据，是高价值取证点。
- 附带面：CORS（放宽来源）、加密配置、日志配置（日志桶常是第二个弱点）、静态站点托管，分别对应 `get_bucket_cors`、`get_bucket_encryption`、`get_bucket_logging` 与站点托管配置。
- 接管前提严格：`dig +short <sub>` 指向云端点 **且**响应 `NoSuchBucket`；COS 还要求同名 `BUCKET-APPID`，只有原 APPID 能建，条件更强，别轻易写"可接管"。

### 3. Serverless 的判定维度

- **执行身份优先于函数代码**：Lambda 运行时的 `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`/`AWS_SESSION_TOKEN`、SCF 的 `TENCENTCLOUD_SECRET_ID`/`SECRET_KEY`/`TOKEN` 就是执行角色凭据，权限常高于泄露的静态 AK。
- 环境变量明文：`Environment.Variables`（SCF 为 `[{Key,Value}]`）里的 `DB_PASSWORD`、`DATABASE_URL`、`MONGODB_URI`、`SECRET_KEY`、`JWT_SECRET`、`REDIS_URL`。
- 触发器即输入面：API Gateway（`queryStringParameters`/`body`/`headers`/`pathParameters`）、对象存储（`Records[].s3.object.key` → 路径拼接）、消息队列（`Records[].body`）。
- 冷热启动：`/tmp` 是唯一可写目录且热启动保留，只算临时立足点，不当作持久化。

## 打哪（命令）

匿名判定（三家并列，S3 用 `--no-sign-request` 即"无凭据"）：

```bash
curl -s "https://BUCKET.s3.amazonaws.com/?list-type=2" | xmllint --format - | head -40
aws s3api get-bucket-acl --bucket BUCKET --no-sign-request
aws s3api get-bucket-policy --bucket BUCKET --no-sign-request
aws s3api get-bucket-versioning --bucket BUCKET --no-sign-request
curl -s "https://BUCKET.s3.amazonaws.com/?versions" | xmllint --format - | head -20
curl -s "https://BUCKET.oss-cn-REGION.aliyuncs.com/?list-type=2"
curl -s "https://BUCKET-APPID.cos.ap-guangzhou.myqcloud.com/?acl"
coscli get-bucket-acl cos://BUCKET-APPID
coscli get-bucket-policy cos://BUCKET-APPID
coscli get-bucket-cors cos://BUCKET-APPID
```

匿名写判定（最小、单对象、可回滚；动手前先存原始 ACL/Policy）：

```bash
curl -X PUT "https://BUCKET-APPID.cos.ap-guangzhou.myqcloud.com/canary-$(date +%s).txt" \
  -H 'Content-Type: text/plain' -d 'authorized-canary'
aws s3 cp canary.txt s3://BUCKET/ --no-sign-request
```

ACL/Policy 放开后的验证（授权内才做）：`aws s3api put-bucket-acl --access-control-policy file://acl.json --no-sign-request`、`aws s3api put-bucket-policy --policy file://policy.json --no-sign-request`、`coscli put-bucket-acl cos://BUCKET-APPID --grant-read anyone`。

接管链（只在确认 `NoSuchBucket` 之后）：

```bash
dig +short assets.example.com        # → xxx.s3.amazonaws.com
curl -sI https://assets.example.com  # → NoSuchBucket
aws s3 mb s3://assets.example.com --region us-east-1
```

Serverless 取证：

```bash
aws lambda list-functions --query 'Functions[].FunctionName'
aws lambda get-function-configuration --function-name F --query 'Environment.Variables'
aws lambda get-function --function-name F --query 'Code.Location' --output text   # 再 curl 下载 zip
tccli scf ListFunctions --Namespace default --Limit 100
tccli scf ListNamespaces
tccli scf GetFunction --FunctionName F --query 'Environment.Variables'
tccli scf ListTriggers --FunctionName F --Namespace default
```

写侧（`UpdateFunctionCode` / `UpdateFunctionConfiguration` / `publish-layer-version` 后 `update-function-configuration --layers`）属"变更"：授权内只做到证明层，先记录原代码 hash 与变量快照以便回滚；Lambda Layer 是不可变快照，发布同名 Layer 只新增版本，必须显式把函数指向新 Layer 版本才生效。

## 什么算成

- 匿名 LIST：200 且 XML 有 `<Key>`，并补一条对象 GET 200 的内容——两步都做，才算"可枚举且可读"。
- 匿名 READ：从 JS/日志取到的对象名直接 GET 200，内容是配置/备份/凭据，且与前端引用或报错信息对得上。
- 匿名 WRITE：PUT 200 + GET 回读字节一致 + DELETE 成功（三步齐全），并指出 ACL 中 `AllUsers` 的授权或 Policy 的 `Principal: "*"`。
- 版本面：`GET /?versions` 返回里有 `DeleteMarker`，同 key 旧 `versionId` GET 200 且内容敏感。
- Serverless：`Environment.Variables` 出现真实凭据，并用它做一次只读校验成功；或 Invoke 后回显我们传入参数对应的命令输出。

## 假点

- LIST 403 但某对象 200：只报"已知对象可读"，不报桶公开。
- 403 `AccessDenied` 带 RequestId：正常拒绝，属预期行为。
- `NoSuchBucket` 只在当前 endpoint 出现：S3 桶可能挂在别的 region，换 endpoint/region 再判。
- ACL 只给 `READ_ACP`：能看 ACL 不等于能读对象。
- 版本控制未开启：`/?versions` 返回空，别写"可恢复删除数据"。
- 匿名 PUT 返回 200 但对象没落地（XML 里带内部错误）：必须回读验证。
- 环境变量只有占位符/空串：未取到可用凭据，停在"配置暴露"。
- `/tmp` 残留随冷启动消失，不算持久化；函数代码里出现 `password` 字样也不等于凭据泄露。
- 接管只停在 `NoSuchBucket`：没建桶并验证内容归属前不算接管。

## 与其他包联动

- 入门枚举、SAS/STS、IMDS 到云 API 的链路：`./对象存储与云元数据实战.md`。
- 桶里的 tfstate / CI 产物：`./cloud-10-CICD与供应链与IaC.md`。
- 容器里拿到的云身份与节点 IMDS：`./cloud-06-K8s攻击面-逃逸与集群.md`、`./cloud-08-容器运行时与镜像.md`。
- 走 Web SSRF 才摸到元数据：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`。
- 证据与定级：`../../../../rules/40-evidence-report.md`；写操作边界：`../../../../rules/20-min-harm.md`。
