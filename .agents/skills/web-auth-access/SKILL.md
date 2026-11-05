---
name: web-auth-access
description: 认证/会话/JWT/验证码/越权(IDOR)/前端权限绕过专项。当出现注册登录、找回密码、验证码、OAuth、JWT、2FA、角色参数、id 可替换、路由守卫时调用。
---

# web-auth-access — 认证/会话/JWT/验证码/越权(IDOR)/前端权限绕过专项

## 何时调用

- 登录/注册/找回密码/改密
- 验证码/2FA
- JWT/OAuth/SSO/设备码
- id/租户/角色参数可控
- 前端路由守卫做权限

## 30 秒分诊

1. 先判断要的是【会话】还是【越权】：未登录能拿会话优先拿会话
2. 会话：找发签/登录/token 泄露口（JS/配置/登录页）
3. 越权：换 id/租户/角色，做跨主体差分（有权限 vs 无权限）
4. JWT：先看 alg/kid/jku，再找密钥（文件/JS/弱口令）

## 首枪顺序

- 登录只校验用户名 → 任意用户进入后打业务接口
- 未登录发签/登录 URL 带 token → 直接当会话用
- 密文 id/JSEncrypt：找明文序号或重加密相邻 id
- 租户字段试 `0`/`-1`/空；附件 URL 只改租户
- 自定义身份头（User-Id/employeeId）当会话：换号打详情
- JWT HS256 + kid 指向文件 → kid 路径穿越读可读文件当密钥
- JWT alg=none/算法混淆/自签 JWKS(jku 可控)
- 验证码复用：同 session 连用；或发码口回显 dev_code
- 密码重置：改身份 id/验码可爆破/回显
- 前端权限不等于后端权限：直打管理 API

## 知识库索引（按需开小块，禁通读）

| 文件 | 用途 | 大小 |
|---|---|---|
| `knowledge/authbypass-test.md` | 真实 SRC 认证绕过全套（未登录取会话/发签口） | 0.2KB |
| `knowledge/idor-test.md` | IDOR/越权实战（密文 id、租户、哨兵、头身份） | 0.3KB |
| `knowledge/oauth-jwt-test.md` | OAuth/JWT/SAML 专题 | 0.4KB |
| `knowledge/auth-access-control-01-一、身份认证与会话安全.md` | 会话与认证基础 | 0.6KB |
| `knowledge/auth-access-control-03-三、验证码安全专项.md` | 验证码绕过 | 1.8KB |
| `knowledge/auth-access-control-04-四、JWT-Token-专项.md` | JWT 专项 | 0.4KB |
| `knowledge/auth-access-control-05-五、访问控制与越权.md` | 越权矩阵 | 0.7KB |
| `knowledge/401-403-bypass.md` | 401/403 绕过（业务 API 现场打，不磨登录 HTML） | 0.6KB |

其余 22 个知识块（按标题搜，禁止通读）：`ls knowledge/`；原始清单见 `../../../docs/MIGRATION.md`。

## 相关

- `web-recon` / `web-api-protocol` / `web-logic-race`

