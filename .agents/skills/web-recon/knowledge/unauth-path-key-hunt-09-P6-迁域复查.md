# P6 迁域复查

> 来源：CkSKILLS v1 `unauth-path-key-hunt` §P6 迁域复查（迁移至 v2 知识块）

旧站下线必须四问：

1. 旧 Host 是 NXDOMAIN 还是 301？301 的 Location 是新战场。
2. 新品牌域有没有把 API 一起搬走，还是只搬了 C 端壳？
3. 同 IP 上哪个 ServerName 还在反代这套前缀（`/gp` `/mag`）？
4. 前端 chunk 删了方法名，网关上方法还在不在？（405/200 比 JS 诚实）

---
