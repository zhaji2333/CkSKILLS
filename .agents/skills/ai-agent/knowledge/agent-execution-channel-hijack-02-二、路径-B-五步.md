# 二、路径 B 五步

> 来源：CkSKILLS v1 `agent-execution-channel-hijack` §二、路径 B 五步（迁移至 v2 知识块）

**1. 抓接口**

打开云端网页 Agent → F12 → Network → 发一句、让它读文件或跑代码。过滤 Fetch/XHR。路径关键词：

```
exec shell command code interpreter sandbox terminal tool tools invoke
file files upload gateway llm mcp session conversation share
```

Copy as cURL (bash) / HAR。

**2. 鉴权**

| 看到 | 意味着 |
|---|---|
| `Authorization: Bearer` / 业务 Cookie | 拿了就能自己发 |
| `X-Sign` / `X-Timestamp` 等 | 前端 JS 还原（`recon-js-analysis`） |
| **什么都没有** | **直接打** |

**3. curl 复现（不过模型）**
```bash
curl -X POST 'https://target/api/sandbox/exec' \
  -H 'Authorization: Bearer <F12>' \
  -H 'Content-Type: application/json' \
  -d '{"cmd":"echo hello"}'
```
SSE 用 `curl -N`。通了换真正要的命令。

**4. 「绕过模型」本身就是洞**
```
对话框让它跑 → 被拒
同一条 curl 打 API → 成功
→ 信任客户端，可交
```

**5. 换 id（跨租户，最高价值）** — 见第三节。
