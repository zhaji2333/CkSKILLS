# 七、逃逸判定树

> 来源：CkSKILLS v1 `agent-sandbox-takeover` §七、逃逸判定树（迁移至 v2 知识块）

```
Q2 = 真 VM / 云电脑？ ── 是 → 无容器逃逸，打主机横向
                         否 ↓
docker.sock / containerd.sock？ ── 有 → 宿主起容器挂 /
宿主块设备 / /.rootfs / /.oldroot？
        可读写 → debugfs / 直接读写（不需 SYS_ADMIN）
        不可写 → 先提权
sudo -n -l / setuid / file cap（按 CapBnd）
seccomp=0 且内核旧 → 内核 CVE 才考虑
全不行 → 转组件 / 凭据 / 跨租户 / 网关（不要为逃逸空转）
```
