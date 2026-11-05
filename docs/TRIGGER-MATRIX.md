# TRIGGER-MATRIX — 触发 → 技能包

命中即加载对应主包（必要时 +1 辅包）；不确定先 `ck-router`。

| 触发信号（真实业务语境） | 主包 | 辅包 | 先读战法索引 |
|---|---|---|---|
| 参数拼 SQL/排序筛选/JSON 查询/命令执行点/模板渲染 | `web-injection` | `web-waf-bypass` | 03-注入与协议 |
| 登录/注册/找回密码/验证码/OAuth/JWT/2FA/角色/IDOR/前端鉴权 | `web-auth-access` | `web-recon` | 01-鉴权与越权 |
| 上传/下载/导出/导入/预览/压缩包/路径穿越/任意读写 | `web-file-path` | `web-injection` | 02-存储与上传 |
| URL 抓取/代理/回调/图片预览/网页截图/PDF 渲染/云元数据 | `web-ssrf-render` | `cloud-infra` | 03/04 |
| 评论/富文本/搜索回显/Markdown 渲染/跳转页/postMessage/CSRF | `web-xss-frontend` | `web-api-protocol` | 05-客户端与前端 |
| REST/GraphQL/gRPC/WebSocket/Swagger/网关/HTTP 走私/缓存/Header | `web-api-protocol` | `web-recon` | 03-注入与协议 |
| 支付/订单/退款/优惠券/积分/库存/审批/并发重放/状态机 | `web-logic-race` | `web-auth-access` | 06-业务与逻辑 |
| XML/SOAP/序列化/yaml/JSON 深合并/JNDI/表达式/原型污染 | `web-deser-xxe` | `web-injection` | 03-注入与协议 |
| 新目标/找接口/JS 分析/子域名/未授权路径/密钥还原 | `web-recon` | `web-auth-access` | 01/05 |
| payload 被拦/403/WAF/过滤器/检测规避 | `web-waf-bypass` | 当前题型包 | 03-注入与协议 |
| 云资产/对象存储/K8s/运维面板/中间件/CI-CD/供应链 | `cloud-infra` | `web-ssrf-render` | 04-云与内网 |
| LLM/Chatbot/RAG/AI 助手/Agent/代码解释器/沙箱/工具执行 | `ai-agent` | `web-auth-access` | 07-跨域 |
| PE/ELF/固件/SO/驱动/二进制漏洞/逆向/内存破坏 | `binary-re` | `source-audit` | 07-跨域 |
| APK/Android/预装应用/小程序/移动端逆向 | `mobile-app` | `binary-re` | 07-跨域 |
| 有源码/反编译产物/代码审计/白盒 | `source-audit` | 对应业务包 | — |

## 多域题

主域 + 辅域（≤2）。切换前把已得结论写入线索板；不把两套知识正文同时留在上下文。

## 路由不命中

1. 读 `.agents/skills/ck-router/knowledge/进站决策.md` 做 30 秒分诊；
2. 仍不命中 → 按目标形态就近选包，并在线索板记"路由未命中，按 X 包处理"。
