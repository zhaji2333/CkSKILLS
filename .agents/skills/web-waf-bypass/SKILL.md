---
name: web-waf-bypass
description: WAF/过滤/检测绕过与失败升级专项。当 payload 被 403/拦截、需要多编码/变形/协议层绕过、或需要构造规避检测的制品时调用。
---

# web-waf-bypass — WAF/过滤/检测绕过与失败升级专项

## 何时调用

- payload 被 WAF/过滤/403 拦截
- 多编码/变形/分块/压缩
- 检测规避（YARA/行为检测）
- 连续多枪不中需要换层

## 30 秒分诊

1. 先定位防御层（WAF/网关/应用过滤/正则）
2. 按 Level 维度换层（编码→变形→逻辑→协议→换入口→组合→时间，可按现场跳层）
3. 每次换层记录否定证据（回包特征）
4. 别在同一层原地反复重试：主要变体走完、无新信号就升级

## 首枪顺序

- 编码：URL/HTML/Unicode/UTF-16/双重/八进制
- 变形：大小写/双写/分隔符/空白/等价函数/截断
- 逻辑：参数污染/顺序/类型/边界/多值
- 协议：分块/压缩体/HTTP2/头部/路径规范化差异
- 换入口：同业务另一个接口/Host/旧版本/移动端 API
- 换实现：短标签/动态函数/拼接关键字绕过字符串黑名单
- 制品规避：polyglot（PNG+GIF+ZIP+PHP）、合法指令序列绕 YARA
- 隐蔽通道：DNS/ICMP/HTTP 头外带

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/waf-bypass.md` | 真实 SRC WAF 绕过战法大全 | 0.4KB |
| `knowledge/waf-bypass-techniques-02-二、失败升级路径-Level-1-7.md` | Level 1–7 升级路径 | 0.8KB |
| `knowledge/waf-bypass-techniques-03-三、通用绕过技术库.md` | 通用绕过技术库 | 0.9KB |
| `knowledge/waf-bypass-techniques-04-四、分类绕过速查.md` | 分类绕过速查（SQL/XSS/命令） | 1.0KB |
| `knowledge/waf-bypass-techniques-05-五、403-绕过专项.md` | 403 绕过 | 0.4KB |

其余 5 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-injection` / `web-xss-frontend` / `web-api-protocol`

