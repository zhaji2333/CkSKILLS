# 九、验证要点

> 来源：CkSKILLS v1 `miniprogram-security` §九、验证要点（迁移至 v2 知识块）

- 反编译还原度确认后再审计，防漏接口
- 接口全方法测试（GET/POST/PUT/DELETE）+ 无 token / 伪造 token / 他人 token 对比
- **登录链 A/B 交叉证明**：A 凭证访问 B 数据才算越权成立（只读自己数据不报）
- 支付回调重放/验签缺失：真实回调触发一次 → 重放 → 观察状态变化
- 云函数：换 openid 上下文调用敏感函数
- 渲染 XSS：真实触发（web-view 加载恶意 URL / rich-text 弹窗截图）
- 证据链：Burp 请求块 + 截图 + 影响证明；正式报告按 `../../../../rules/40-evidence-report.md`
