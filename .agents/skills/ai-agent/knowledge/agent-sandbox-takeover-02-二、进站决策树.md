# 二、进站决策树

> 来源：CkSKILLS v1 `agent-sandbox-takeover` §二、进站决策树（迁移至 v2 知识块）

```
有云端执行环境？
  否 → 不是本技能（本地客户端薄打：agent-execution-channel-hijack 客户端节）
  是 ↓
进门身份是 root 还是低权？
  root     → 厂商赌在逃逸边界 → 先打组件 / 凭据 / 网关 / 跨租户，不先提权
  低权     → 厂商常省掉提权治理 → 先 sudo -n -l / CapBnd / setuid
Q2 是真 VM / 云电脑（PID1=systemd、无 kubepods）？
  是 → 没有「容器逃逸」问题，当主机打横向/凭据/内网
  否 → 才走逃逸判定树（第七节）
```

**0day-free 优先级（不写内核 exploit）**
```
回环被抬到 0.0.0.0 的敏感服务 > 未授权内部服务 > 凭据
> 跨租户（换 id / 共享可写内部服务）> 网关劫持 > IMDS
> 块设备 debugfs（不需 SYS_ADMIN）> 内核/运行时逃逸
```
