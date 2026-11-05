# 二、前端鉴权绕过 / 路由守卫绕过

> 来源：CkSKILLS v1 `auth-access-control` §二、前端鉴权绕过 / 路由守卫绕过（迁移至 v2 知识块）

> 适用场景：Vue / React / Angular 等前后端分离应用，前端通过 `router.beforeEach`、`AuthGuard`、本地 role 字段、localStorage/sessionStorage 中的登录态控制页面访问；服务端接口未做二次校验或校验可被绕过。

### 2.1 常见前端鉴权模式与绕过点

| 模式 | 绕过思路 | 验证方法 |
|---|---|---|
| 前端路由守卫（Vue Router / React Router） | 直接请求后端 API 或构造 URL 访问目标页，绕过守卫 | 拦截 `/login` 后的跳转，直接访问 `/admin#/dashboard` |
| localStorage/sessionStorage 存储登录态 | 修改/伪造 `token`、`role`、`isAdmin` 等字段 | 控制台 `localStorage.setItem('role','admin')` 后刷新 |
| 前端 role/admin 字段控制菜单/按钮 | 接口返回 `role` 字段，前端仅隐藏入口；直接调用后端管理接口 | 抓包改 role，观察后端是否真正校验 |
| JS 源码中硬编码角色/权限 | source map/解包后搜索 `admin`、`role`、`permission` | webpack/source map 还原、Chrome Sources 定位 |
| 路由异常路径 / Hash 模式差异 | 未定义路由、404、错误分支被放行；Hash 模式 `#/admin` 绕过服务端路径限制 | 对比 `/admin` 与 `/#/admin`；构造 `#/admin/不存在路径` 观察是否放行 |

### 2.2 挖掘步骤

1. **识别前端框架**：查看 JS bundle、路由库（vue-router、react-router-dom）、构建产物（webpack、vite、umi）。
2. **提取路由表**：从 `router.js`、JS map、反编译产物中提取所有路由路径，特别是 `/admin`、`/manage`、`/console`、`/system` 等管理路由（JS/source map 还原详见 `recon-js-analysis`）。
3. **分析路由守卫逻辑**：定位 `beforeEach`、`onEnter`、`AuthGuard`、`PrivateRoute`，确认校验依赖的是前端存储还是后端接口。
4. **绕过验证**：按 2.1 表格验证方法逐项执行；另测删除/篡改路由守卫 JS（Chrome Overrides、Burp 替换响应体）。
5. **后端接口二次校验**：即使绕过前端页面，也要测试对应 API 是否真正鉴权；前端绕过 ≠ 后端未授权，后者才是有效漏洞。
