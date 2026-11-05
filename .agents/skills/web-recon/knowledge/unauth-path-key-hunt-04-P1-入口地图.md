# P1 入口地图

> 来源：CkSKILLS v1 `unauth-path-key-hunt` §P1 入口地图（迁移至 v2 知识块）

分清四类 Host，标 DNS/IP，不要只盯主域：

| 类 | 典型 | 下一步 |
|---|---|---|
| C 端壳 | 主站 / m / 品牌新域 Next/Vue | 在此搜路径常失败，记录后换场 |
| API 网关 | appgw / apigw / qr / gateway | P2 指纹，不要当 SPA 扫目录 |
| 独立业务 H5 | invoice / vat / asp / mag / 活动 CDN | 优先拆 JS、打 `/gp` `/mag` 等前缀 |
| 后台/SSO | passport / admin / 服务商域 | 记下 sid；零身份只证「墙在哪」 |

品牌新域、301 目标必须列入地图。

**通过门：** 至少标出「C 端壳 / 疑似网关 / 疑似业务 H5」三类。

---
