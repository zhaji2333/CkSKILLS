# 四、网关 / 控制面 HTTP（L1/L2）

> 来源：CkSKILLS v1 `agent-execution-channel-hijack` §四、网关 / 控制面 HTTP（L1/L2）（迁移至 v2 知识块）

F12 或 JS 里出现 gateway / llm 路由 / invoke / tools 调用 / mcp 时：

1. 原样 curl 管理面、模型列表、会话下发  
2. 无 token / 假 token / 真 token  
3. body 里若有 `sandbox_id` / 会话归属字段（`owner`/`isOwner` 之类）/ `Host`：改这些再打  
4. **Host 头当「是不是本机」**、客户端自报 owner = 控制面经典洞，换 Host / 改 flag 测  

L1 未授权或 L2 认钥成功 → 记线索，进沙箱后按 takeover 8.8 追 L3（另一会话真执行才报无感 RCE）。本技能不把「网关 200」写成全用户 RCE。
