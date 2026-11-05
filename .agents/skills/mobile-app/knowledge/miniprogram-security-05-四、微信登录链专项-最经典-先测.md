# 四、微信登录链专项（最经典，先测）

> 来源：CkSKILLS v1 `miniprogram-security` §四、微信登录链专项（最经典，先测）（迁移至 v2 知识块）

**正常流程**：`wx.login()` 拿 `code` → 后端调 `code2session` 换 `openid/session_key` → 返回自定义 token。

**攻击面（按优先级）**
1. **openid 参数可控**（最常出洞）：后端把 `openid` 当请求参数接收（`{"openid":"xxx"}` 直接换 token）→ 填他人 openid = **任意用户登录**
2. **code 重放**：同一 code 可多次换取 token；code 未绑定会话/设备
3. **session_key 泄露**：后端把 session_key 返回给前端 → 可解密手机号等敏感数据
4. **token 可篡改**：自定义 token 里含 openid/user_id 明文可改（JWT 弱密钥/无签名，联动 `auth-access-control`）
5. **注册即登录**：注册接口直接返回已登录态，可批量注册撞已有 openid

**验证方法**
```
正常：自己的 code 登录 → 拿 token
A/B：把请求里的 openid 换成 B 的 → 若拿到 B 的会话/数据 → 任意用户登录/越权成立
重放：同一个 code 发两次 → 两次都能拿 token → 重放成立
```

---
