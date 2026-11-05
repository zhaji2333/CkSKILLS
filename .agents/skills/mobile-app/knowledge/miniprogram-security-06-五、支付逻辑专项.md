# 五、支付逻辑专项

> 来源：CkSKILLS v1 `miniprogram-security` §五、支付逻辑专项（迁移至 v2 知识块）

- **下单金额**：`total_fee`/`amount` 参数可控、负数、0.01、类型混淆
- **回调验签**：支付回调 `notify` 是否验签（MD5/签名比对）；不验签 → 伪造支付成功通知
- **重复回调**：同订单重复通知、幂等缺失 → 重复发货/重复入账
- **退款**：退款金额/次数可控、退款到他人账户
- **签名机制**：参数拼接 + appsecret 签名，参数顺序/编码差异绕过（与 `business-logic-race` / `auth-access-control` 联动）

---
