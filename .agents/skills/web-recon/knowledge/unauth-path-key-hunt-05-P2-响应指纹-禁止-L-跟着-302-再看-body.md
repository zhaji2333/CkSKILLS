# P2 响应指纹（禁止 `-L` 跟着 302 再看 body）

> 来源：CkSKILLS v1 `unauth-path-key-hunt` §P2 响应指纹（禁止 `-L` 跟着 302 再看 body）（迁移至 v2 知识块）

记录四元组：`状态码 / Content-Type / Server / body 形态`。

| 指纹 | 含义 | 动作 |
|---|---|---|
| SPA HTML 404（Next `X-Powered-By`，几十 KB index） | 前端路由吞路径，不是这个后端 | 换 Host |
| 网关 JSON：`no api` / `Route Not Found` / `divide: selector` | 网关活着，这条 route 没挂 | 换 Host 或前缀 |
| 业务 JSON：`success/code/message`，path 出现在 body | 真应用 | 进入 P4/P5 |
| 短 body 业务文案（「链接不存在」）vs 统一 404 页 | 路径存在、资源不存在 | 保留前缀，补 module/method |
| 302 → SSO | 有鉴权墙，不是「没有服务」 | 记下 Location 的 sid/应用名 |
| 405 `Request method 'GET' not supported` | 控制器在，方法不对 | 立刻 POST |
| 200 + `data:[]` | 已进控制器，只是没命中数据 | 补参数/加密/字段名 |
| 同 IP 换 Host → 403 / `404 Route Not Found` | 虚拟主机隔离 | 继续找对的 ServerName |

**通过门：** 每个候选路径都归入上表。禁止再写「404 所以没有」。

---
