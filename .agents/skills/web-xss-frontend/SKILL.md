---
name: web-xss-frontend
description: XSS（反射/存储/DOM/跳转型）/CSRF/Clickjacking/Markdown 渲染专项。当出现评论昵称富文本、搜索回显、跳转页、postMessage、前端 DOM 操作、AI 输出渲染时调用。
---

# web-xss-frontend — XSS（反射/存储/DOM/跳转型）/CSRF/Clickjacking/Markdown 渲染专项

## 何时调用

- 评论/昵称/私信/工单/富文本
- 搜索/筛选回显
- 跳转页/开放重定向/target 参数
- postMessage/跨域配置
- Markdown/AI 输出渲染

## 30 秒分诊

1. 先找回显点与渲染上下文（HTML/属性/JS/URL）
2. 跳转类优先测 `javascript:` 伪协议（比反射更容易升级）
3. 存储型找 bot/管理员访问路径（举报/反馈/客服）
4. 有 CSP 时看能否 JSONP/同源上传外链

## 首枪顺序

- 跳转页 `target/url/redirect_uri` → `javascript:`/`data:`
- 白名单绕过：`@`、`\`、`//`、子域后缀、大小写/编码
- 存储型：评论/昵称/工单 → 管理员 bot 会话窃取
- DOM XSS：`innerHTML`/`location`/`eval` 的 sources/sinks
- Markdown/AI 渲染：`[x](javascript:)`、`<img onerror>`
- postMessage：无 origin 校验 → 构造消息触发
- CSRF：无 token/GET 写/SameSite 宽松
- CORS：真实 SRC 默认不单独立项（见 rules/20）

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/xss-frontend-security-03-三、跳转型-XSS-专项-🔴-优先测试.md` | 跳转型 XSS（优先） | 5.3KB |
| `knowledge/xss-frontend-security-04-四、AI-Markdown-渲染型存储-XSS-专项.md` | AI/Markdown 渲染 XSS | 3.9KB |
| `knowledge/xss-frontend-security-05-五、XSS-绕过技术.md` | XSS 绕过 | 0.7KB |
| `knowledge/xss-test.md` | 真实 SRC XSS/客户端链（存储 XSS→RCE） | 10.8KB |
| `knowledge/csrf-test.md` | CSRF 专题 | 0.4KB |
| `knowledge/open-redirect-test.md` | 开放重定向 | 11.6KB |
| `knowledge/xss-frontend-security-02-二、内容-社交类场景表-存储型重点.md` | 存储型场景表 | 1.0KB |

其余 11 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-api-protocol` / `web-auth-access` / `mobile-app`

