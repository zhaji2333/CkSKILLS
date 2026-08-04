---
name: xss-frontend-security
description: 当目标存在评论/昵称/富文本/私信/工单/搜索反射/Markdown解析/前端DOM操作/postMessage/跨域配置等功能时调用。负责反射型/存储型/DOM XSS、CSRF、CORS错误配置、Clickjacking 的深度挖掘与绕过。
---

# xss-frontend-security — XSS 与前端安全专项深度挖掘

## 何时调用（触发条件）

- 评论、留言、昵称、签名、富文本、私信、工单等存储型输入点
- 搜索框、报错页、参数反射
- 前端 DOM 操作：location、hash、innerHTML、document.write、eval
- postMessage 消息处理、iframe 嵌套
- 跨域配置：Access-Control-Allow-Origin、CORS 预检
- 敏感操作无 Token/Referer 校验（CSRF）

## 一、漏洞类型全景

| 类型 | 场景 | 修复 |
|---|---|---|
| D1. 反射型/存储型XSS | 搜索、评论、富文本 | 输出编码、CSP |
| D2. DOM XSS | location/hash/postMessage | 安全DOM API |
| D3. Clickjacking | iframe嵌套 | X-Frame-Options |
| D4. CORS错误配置 | `*`+凭证 | 严格白名单 |

## 二、内容/社交类场景表（存储型重点）

| 场景 | 漏洞类型 | 挖掘要点 |
|---|---|---|
| 评论/留言 | 存储XSS/CSRF | 富文本过滤不严、HTML标签逃逸 |
| 私信/聊天 | XSS/越权查看聊天记录 | 消息ID遍历、会话鉴权缺失 |
| 用户昵称/签名 | 存储XSS/SQL注入 | 特殊字符未过滤、后台展示触发 |
| 文章/帖子发布 | XSS/SSRF（远程图片） | Markdown解析、外链加载 |
| @提及/通知 | 用户枚举/消息轰炸 | @任意用户、批量触发通知 |
| 举报/投诉 | 信息泄露/XSS | 举报详情含敏感信息、客服后台触发XSS |
| 分享/邀请链接 | 链接可遍历/信息泄露 | 分享token可预测、权限过大 |

> 存储型 XSS 的关键：**受害者视角**（客服后台、管理员预览、其他用户打开）决定危害等级。

## 三、XSS 绕过技术

```
HTML实体：&#60;script&#62;
事件：onerror/onload/onfocus/onmouseover
标签：<svg>、<img>、<iframe>、<math>
伪协议：javascript:、data:
```

进阶思路：
- 过滤绕过：大小写、双写、编码嵌套、空白符/换行注入
- 富文本过滤逃逸：事件属性、svg/math 命名空间、style 表达式
- 服务端 vs 客户端过滤差异
- 存储点污染 → 多个触发点（后台/导出/邮件）

## 四、CSRF 专项

### 场景
- 资金操作、绑定账号、敏感配置

### 挖掘
- CSRF Token 缺失
- Referer/Origin 可绕过（空 Referer、跨子域、`https://evil.com.trusted.com`）
- Token 不绑定会话（固定 token 可重用）
- GET 请求执行敏感操作

### 修复
- Token、SameSite、二次确认

## 五、CORS 错误配置专项

- 反射 Origin：`Access-Control-Allow-Origin: <攻击者Origin>` + `Allow-Credentials: true`
- 前缀匹配漏洞：`trusted.com.evil.com`
- 空 Origin / null Origin 反射
- 与凭证配合的敏感数据读取

## 六、Clickjacking 专项

- 敏感操作页面是否可被 iframe 嵌套
- 检查 X-Frame-Options / CSP frame-ancestors
- 配合诱导点击（按钮覆盖）

## 七、验证要点

- 每个输入点测：反射位置、存储位置、输出上下文（HTML属性/标签内/JS字符串）
- 浏览器执行验证（无头浏览器截图/DOM 变化）
- 存储型确认触发链条：注入 → 存储 → 受害者页面加载 → 执行
- XSS 影响评估：能否打 Cookie（HttpOnly？）、能否打后台、能否打管理员
- 组合拳：Self-XSS + CSRF → 存储型 XSS 攻击他人；XSS → 钓鱼/接管会话

## 八、修复建议

- 输出编码（上下文相关：HTML/属性/JS/URL）
- CSP 严格策略、禁用内联
- 富文本使用白名单解析器
- CSRF：Token + SameSite + 敏感操作二次确认
- CORS：严格白名单，禁止反射 Origin 与通配符+凭证

