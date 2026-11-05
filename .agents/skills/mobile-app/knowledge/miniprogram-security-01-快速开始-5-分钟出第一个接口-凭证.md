# 快速开始（5 分钟出第一个接口/凭证）

> 来源：CkSKILLS v1 `miniprogram-security` §快速开始（5 分钟出第一个接口/凭证）（迁移至 v2 知识块）

```bash


grep -rniE "appid|appsecret|secret|access_key|secret_key|token" <解包目录>/
grep -rEoh "https?://[a-zA-Z0-9._/-]+" <解包目录>/ | sort -u          # 后端/业务域名
grep -rn "wx.request|wx.cloud.callFunction|request\(" <解包目录>/ | head -50  # 接口与云函数

```

---
