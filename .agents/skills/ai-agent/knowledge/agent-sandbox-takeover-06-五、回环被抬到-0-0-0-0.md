# 五、回环被抬到 0.0.0.0

> 来源：CkSKILLS v1 `agent-sandbox-takeover` §五、回环被抬到 0.0.0.0（迁移至 v2 知识块）

`ss -tlnp` 里「用途敏感 + 听 `0.0.0.0`/`::` + 进程是 socat/websockify/novnc/nginx/cdp-proxy」→ 回推它抬出了哪个 `127.0.0.1` 服务。

CDP 打通 = 读 `--user-data-dir` 的 Cookie/已登录会话 = **以该用户身份操作**（跨租户现实落点）。有 `browser_guard` 类看门狗则动作要快且可逆。
