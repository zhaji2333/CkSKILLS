# rules/70 — 题型路由（触发 → 技能包 → 知识块）

> 命中即加载对应技能包；不确定先 `ck-router`。只加载主包（必要时 +1 辅包）。

## 一、触发路由表

| 触发信号 | 主包 | 辅包 |
|---|---|---|
| 参数拼 SQL / 排序筛选 / JSON 查询 / 命令执行点 / 模板渲染 | `web-injection` | `web-waf-bypass` |
| 登录/注册/找回密码/验证码/OAuth/JWT/2FA/角色参数/IDOR/前端权限 | `web-auth-access` | `web-recon` |
| 上传/下载/导出/导入/预览/压缩包/路径穿越/任意读写 | `web-file-path` | `web-injection` |
| URL 抓取/代理/回调/图片预览/网页截图/PDF 渲染/云元数据 | `web-ssrf-render` | `cloud-infra` |
| 评论/富文本/搜索回显/Markdown 渲染/跳转页/postMessage/CORS/CSRF | `web-xss-frontend` | `web-api-protocol` |
| REST/GraphQL/gRPC/WebSocket/Swagger/网关/HTTP 走私/缓存/Header | `web-api-protocol` | `web-recon` |
| 支付/订单/退款/优惠券/积分/库存/审批/并发重放/状态机 | `web-logic-race` | `web-auth-access` |
| XML/SOAP/序列化数据/yaml/JSON 深合并/JNDI/表达式/原型污染 | `web-deser-xxe` | `web-injection` |
| 新目标/找接口/JS 分析/子域名/未授权路径/密钥还原 | `web-recon` | `web-auth-access` |
| payload 被拦/403/WAF/过滤器/检测规避 | `web-waf-bypass` | 当前题型包 |
| 云资产/对象存储/K8s/运维面板/中间件/CI-CD/供应链 | `cloud-infra` | `web-ssrf-render` |
| LLM/Chatbot/RAG/AI 助手/Agent/代码解释器/沙箱逃逸/工具执行 | `ai-agent` | `web-auth-access` |
| PE/ELF/固件/SO/驱动/二进制漏洞/逆向/内存破坏 | `binary-re` | `source-audit` |
| APK/Android/预装应用/小程序/移动端逆向 | `mobile-app` | `binary-re` |
| 有源码/反编译产物/代码审计/白盒 | `source-audit` | 对应业务包 |

## 二、开局首读哪个战法索引

| 题型 | 先读 |
|---|---|
| Web 鉴权/越权/未授权/凭证 | `.agents/skills/ck-router/knowledge/战法索引-01-鉴权与越权.md` |
| 上传/存储/文件/分享/下载 | `.agents/skills/ck-router/knowledge/战法索引-02-存储与上传.md` |
| 注入/SSRF/协议/Header/缓存 | `.agents/skills/ck-router/knowledge/战法索引-03-注入与协议.md` |
| 云/内网/Agent/工具执行 | `.agents/skills/ck-router/knowledge/战法索引-04-云与内网.md` |
| 客户端/小程序/前端/H5 | `.agents/skills/ck-router/knowledge/战法索引-05-客户端与前端.md` |
| 业务逻辑/支付/竞态 | `.agents/skills/ck-router/knowledge/战法索引-06-业务与逻辑.md` |
| 二进制/移动/逆向/AI 模型 | `.agents/skills/ck-router/knowledge/战法索引-07-跨域-二进制移动AI.md` |

## 三、多域题

主域包 + 辅域包（最多 2 个）；例如"AI 平台 + 文件读取" → `ai-agent` + `web-file-path`。
跨域切换时把已得结论写入线索板再加载，不把两套正文同时留在上下文。

## 四、路由不命中

- 先读 `.agents/skills/ck-router/knowledge/进站决策.md` 做 30 秒分诊；
- 仍不命中 → 按目标形态就近选包，并在线索板记"路由未命中，按 X 包处理"。
