---
name: waf-bypass-techniques
description: 当payload被拦截、请求被WAF/过滤/403拒绝、连续多次payload失败、需要绕过黑名单/白名单/正则/语义分析防御时调用。负责编码/变形/逻辑/协议层绕过、换入口、组合利用与时间维度攻击的完整升级路径。
---

# waf-bypass-techniques — 绕过与对抗专项深度挖掘

## 何时调用（触发条件）

- payload 被 WAF/过滤器/防火墙拦截
- 403 拒绝、请求被改写/丢弃
- 连续 3 次 payload 失败（停止同方向硬刚）
- 黑名单/白名单/正则/语义分析防御
- 需要跨层绕过（代理与后端解析差异）

## 一、对抗意识框架（先定位再绕过）

遇到防御时的思考框架：
1. 这个防御是在**哪一层**做的？（WAF/应用层/框架层/数据库层）
2. 防御的**规则是什么**？（黑名单/白名单/正则/语义分析）
3. 规则的**边界在哪**？（哪些情况没覆盖到）
4. 能否通过**协议差异**绕过？（代理和后端解析不一致）
5. 能否通过**编码差异**绕过？（不同层对编码的处理不同）
6. 能否通过**逻辑差异**绕过？（校验和执行不是同一段代码）

## 二、失败升级路径（Level 1-7）

```
Level 1: 编码绕过
  → URL编码/双重编码/Unicode/十六进制/HTML实体/Base64

Level 2: 变形绕过
  → 大小写混合/双写/注释插入/空白符替换/等价函数

Level 3: 逻辑绕过
  → 换HTTP方法/换Content-Type/换参数位置/利用解析差异

Level 4: 协议层绕过
  → HTTP走私/分块传输/管道化/WebSocket升级

Level 5: 换入口点
  → 同功能的其他接口/旧版本接口/移动端接口/内部接口

Level 6: 组合利用
  → A接口的信息泄露 + B接口的弱校验 = 完整攻击链

Level 7: 时间维度
  → 并发/竞态/延时/定时任务触发
```

**硬性规则：至少尝试到 Level 4 才能下"无漏洞"结论。**

## 三、通用绕过技术库

### 编码类
- URL 编码 / 双重编码（%252e）
- Unicode（\u002e、全角字符）
- 十六进制 / 八进制 / 十进制 IP
- HTML 实体 / Base64 / 分块编码

### 变形类
- 大小写混合（SeLeCt）
- 双写（selselectect）
- 注释插入（/**/、/*!*/）
- 空白符替换（%09、%0a、${IFS}）
- 等价函数/等价标签

### 逻辑类
- 换 HTTP 方法（POST↔GET、PUT、PATCH）
- 换 Content-Type（JSON↔form↔multipart）
- 参数位置迁移（参数名→参数值→Header→Cookie→Path）
- 参数污染（重复参数、数组化）

### 协议类
- HTTP 走私（CL/TE 差异）
- 分块传输（Transfer-Encoding: chunked）
- 管道化、WebSocket 升级
- 路径标准化差异（//、/./、/../、%2e）

## 四、分类绕过速查

### SQL 注入绕过
```
大小写：SeLeCt / 双写：selselectect
注释：/**/、/*!*/、--+、#
编码：URL编码、十六进制、Unicode
等价函数：substr→mid、ascii→ord
```

### XSS 绕过
```
HTML实体：&#60;script&#62;
事件：onerror/onload/onfocus/onmouseover
标签：<svg>、<img>、<iframe>、<math>
伪协议：javascript:、data:
```

### 命令注入绕过
```
分隔符：| / || / & / && / ; / %0a
空格：${IFS} / $IFS$9 / %09 / {cat,/etc/passwd}
通配符：/???/??t /etc/passwd
```

### 文件上传绕过
```
扩展名：.php5/.phtml/.phar/.htaccess/.user.ini
双扩展：shell.php.jpg / shell.jpg.php
%00截断：shell.php%00.jpg
内容：GIF89a头、图片马
```

### SSRF 绕过
```
IP混淆：十进制/十六进制/八进制
重定向：302跳转、DNS重绑定
协议差异：@符号、URL解析差异
```

## 五、403 绕过专项

```
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Original-URL: /admin
X-Rewrite-URL: /admin
路径变体：/admin/、//admin、/./admin、/admin%2f、/ADMIN
方法替换：GET→POST→OPTIONS→X-HTTP-Method-Override
分号截断：/admin;.css、/admin;.js
```

## 六、验证要点

- 每次绕过尝试保留基线请求（被拦的原始请求）对比
- 确认拦截层：WAF/网关/应用层过滤（响应头/错误页差异）
- 绕过成功标准：响应恢复为业务正常响应（非拦截页）
- 多维度组合：编码+变形+协议同时使用
- 换入口优先尝试：移动端接口、旧版本接口、内部接口通常防护更弱

## 七、注意事项

- 绕过成功 ≠ 漏洞成立：仍须验证业务影响
- 保留证据链：拦截响应 + 绕过后响应
- 不无限硬刚同一方向：连续 3 次失败即升级 Level

