# 三、HTTP 跨租户（必须三态 + 对照）

> 来源：CkSKILLS v1 `agent-execution-channel-hijack` §三、HTTP 跨租户（必须三态 + 对照）（迁移至 v2 知识块）

圈人圈沙箱的参数都换，不限字段名：`sandbox_id` / `session_id` / `user_id` / `workspace_id` / `conversation_id` / `chat_id` / `shareId` / `tenant_id` / 路径里的 id。

```bash
curl -s -X POST "$API/exec" -H "Authorization: Bearer $MY" \
  -d '{"sandbox_id":"'$MINE'","cmd":"id"}'

curl -s -X POST "$API/exec" -H "Authorization: Bearer $MY" \
  -d '{"sandbox_id":"'$OTHER'","cmd":"id"}'

curl -s "$API/sandbox/$OTHER/files?path=/etc/hostname" -H "Authorization: Bearer $MY"
```

**三态对照（每个执行/文件/任务口都做）**
```bash
```
| 无 token | 判定 | 动作 |
|---|---|---|
| 401 / 「请先登录」 | 鉴权在 | 仍要换 id（有会话越权） |
| **400 / 缺参** | **参数校验在鉴权前** | **补参立刻重测** |
| 与真 token **相同业务 JSON** | 完全无鉴权 | 用真实他人 id 打数据面 |
| 403 整前缀都一样 | 前缀门禁，不能用状态码证明端点存在 | 改从 JS 确认路径 |

**铁律**
1. 能进业务逻辑 ≠ 能拿到他人数据。必须用 **他人真实 id** 对数据面。  
2. 配置枚举 / 空数组不算洞。  
3. **「缺少必需参数」不要当垃圾滤掉** — 这是 IDOR 最强信号。  
4. 同一服务列表有鉴权、详情没有 = 常态，逐口独立判。

**算成**：出现另一个人的正文 / PII / 命令输出 / 文件。对象空间无租户绑定 → 危害按全用户写。  
**假点**：只证明缺参 400；只读到自己的沙箱；公开目录。

运行时层（JWT 文件、NFS 前缀、CDP、共享 Artifactory）→ `agent-sandbox-takeover` 8.5。
