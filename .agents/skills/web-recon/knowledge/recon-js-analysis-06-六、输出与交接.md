# 六、输出与交接

> 来源：CkSKILLS v1 `recon-js-analysis` §六、输出与交接（迁移至 v2 知识块）

完成本技能后，将提取的接口清单、参数结构、鉴权机制、隐藏功能整理为可测试清单，按类型分发给对应专项技能；**同时按 `hunt-clueboard` 写入 `hunts/<目标>/CLUEBOARD.md`**（Host/路径/钥/否定证据当轮落盘，不只放在对话里）：
- 零身份、路径不在当前前端、加密当鉴权、迁域/兄弟域漏路径 → `unauth-path-key-hunt`
- 接口/鉴权问题 → `api-protocol-security` / `auth-access-control`
- 参数拼接/注入点 → `injection-vulns`
- 文件相关功能 → `file-handling`
- URL可控功能 / 网页截图/预览/HTML→PDF/链接卡片等渲染接口 → `ssrf-internal-network` 三（渲染专项）
- 提取的 URL/IP/域名清单 → 资产测绘扩展（新子域/新端口/新后台），APP 来源的提醒用户关注后台接口域名
- 提取的 appid/appkey/AK/SK 等凭证 → **上报用户并深入挖掘**（验证有效性、打云资产/后端接口，联动 `cloud-infra-supply-chain`）
