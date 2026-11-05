# 八、分享/跳转专项

> 来源：CkSKILLS v1 `miniprogram-security` §八、分享/跳转专项（迁移至 v2 知识块）

- 分享链接/卡片参数可控 → 开放重定向、钓鱼、参数注入
- 页面 `onShareAppMessage` 的 path 参数拼接 → 跳转内部功能（未授权页面）
- 扫码进入（scheme 参数）→ 与 Deep Link 类似，参数驱动内部跳转

---
