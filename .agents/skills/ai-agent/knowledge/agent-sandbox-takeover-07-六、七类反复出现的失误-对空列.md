# 六、七类反复出现的失误（对空列）

> 来源：CkSKILLS v1 `agent-sandbox-takeover` §六、七类反复出现的失误（对空列）（迁移至 v2 知识块）

进门后按隔离形态逐项对照下面清单。按隔离形态对下列，**空列 = 本台打点**。不把厂商名当清单抄进报告标题。

1. `Seccomp: 0`（cap 收了，syscall 面全开）  
2. 块设备 / 宿主 rootfs 挂载未收敛  
3. 内部服务无认证  
4. 凭据在 env / `/etc/*-config` / 全局共享 SA Token  
5. CapEff=0 但 NOPASSWD sudo 或 CapBnd 留 SETUID  
6. 出网过宽、网关 HTTP 明文、IMDS 可达  
7. 回环被转发器抬到全网卡  

同源栈指纹（命中即复用打法，不是点名某厂）：`openclaw-gateway` `18789/18791`、`envd:49983`（加固=token+签名，未加固=`/envs` 无认证）、`169.254.1.1` 当平台对端。

强防御（HIDS / otelcol / Istio / `memfd:a (deleted)` / 凭证每 10s 重注入 / mTLS+方法签名）→ 只读、凭据面，禁止「自己打自己」大动作。
