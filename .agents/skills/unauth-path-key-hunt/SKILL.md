---
name: unauth-path-key-hunt
description: 当未授权/零身份测试但路径不在主站 JS、禁止依赖登录 Network 截图、独立 H5/旧域名 NXDOMAIN/品牌迁域、兄弟域或同 IP Host 漏路径、网关 405 或 data 空数组、getRsaKey/JSEncrypt/前端加密被当成鉴权时调用。负责零身份公开面还原路径与密钥、响应指纹分流、加密证伪、迁域复查。JS 拆包见 recon-js-analysis；角色/IDOR 见 auth-access-control；路径已知后的全方法/BOLA 见 api-protocol-security。
---

# unauth-path-key-hunt — 零身份公开面：路径与密钥猎杀

编排型 skill。只解决「没有后台账号、路径不在当前前端时，如何独立还原接口并证伪加密=鉴权」。不替代 JS 拆包、越权矩阵、API 全方法。

## 何时调用

- 未授权 / 攻击者没有该业务账号（纯零身份）
- 路径不在主站 JS；用户要求不要用登录 Network 截图当发现源
- 独立 H5、旧子域 NXDOMAIN、品牌迁域（旧 Host 301/消失）
- 兄弟域、同 IP、`--resolve` 换 Host 漏出路径
- 网关 `405 Method Not Allowed`、`200 data:[]`、短文案「链接不存在」
- `getRsaKey` / JSEncrypt / SM2 / 前端 AES，怀疑只是传输混淆

**不要调用（交给别人）**

- 攻击面不清、要广撒网拆 webpack / 脏收集 → `recon-js-analysis`
- 路径已通，打角色/IDOR/JWT/验证码 → `auth-access-control`
- 路径已通，全方法、BOLA、Swagger、走私 → `api-protocol-security`
- 调试面板/中间件/对象存储未授权 → `cloud-infra-supply-chain`
- 路径在 APK/小程序包里 → `android-security-audit` / `miniprogram-security`
- 已验证要成稿 → `report`

## 与其它技能分工

```
怀疑隐藏未授权
    │
    ▼
unauth-path-key-hunt     找 Host/路径/钥，证伪加密
    ├─ 拆 webpack / 脏收集 / 提字符串     → recon-js-analysis
    ├─ 路径已通，角色墙 / IDOR            → auth-access-control
    ├─ 路径已通，全方法 / 旧版 / 网关协议  → api-protocol-security
    ├─ 路径在包里                         → android / miniprogram
    └─ 已验证成稿                         → report
```

拆 JS、Wayback、Packer 的细则以 `recon-js-analysis` 为准，此处不重复。
跨轮线索落盘以 `hunt-clueboard` 为准：开工先读 `hunts/<目标>/CLUEBOARD.md`，P2 指纹/405/`[]`/迁域结论当轮写回，禁止只写在对话里。

## 铁律

1. 发现阶段禁止把「已登录 Network」当路径出处。截图只作假设，公开面复原才是证据。
2. 主站 JS 没有 ≠ 接口不存在。
3. 客户端能拿到的 RSA/AES/uuid ≠ 鉴权。
4. SPA 的 404 不是接口的 404。没到失败升级 L4 不准写「无此接口」。
5. 旧 H5 / 旧 Host 下线 ≠ 后端方法下线。

---

## P0 零身份约束

**允许的发现源：** 未登录 HTML/JS/map；CT / urlscan / Wayback / GitHub；兄弟域与同 IP；301 Location；公开文档；未登录可下的 APP/小程序包。

**不允许当发现源：** 业务账号登录后的 DevTools；报告截图里的 URL（降级为待验证假设）。

口令：截图里的路径 = 假设；公开面复原 = 证据。

---

## P1 入口地图

分清四类 Host，标 DNS/IP，不要只盯主域：

| 类 | 典型 | 下一步 |
|---|---|---|
| C 端壳 | 主站 / m / 品牌新域 Next/Vue | 在此搜路径常失败，记录后换场 |
| API 网关 | appgw / apigw / qr / gateway | P2 指纹，不要当 SPA 扫目录 |
| 独立业务 H5 | invoice / vat / asp / mag / 活动 CDN | 优先拆 JS、打 `/gp` `/mag` 等前缀 |
| 后台/SSO | passport / admin / 服务商域 | 记下 sid；零身份只证「墙在哪」 |

品牌新域、301 目标必须列入地图。

**通过门：** 至少标出「C 端壳 / 疑似网关 / 疑似业务 H5」三类。

---

## P2 响应指纹（禁止 `-L` 跟着 302 再看 body）

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

## P3 路径发现五源（并行）

优先级从「更像零身份攻击者」到「更脏」。webpack/脏收集操作见 `recon-js-analysis`。

| 源 | 做什么 | 通过信号 |
|---|---|---|
| 1 现网 JS | 首页、buildManifest、异步 chunk、baseURL | 路径或方法名字符串有公开出处 |
| 2 历史旁路 | urlscan / Wayback / CT / 第三方脚本引用的 Host | 旧 URL、CDN 活动页、发票/售后等业务词 |
| 3 兄弟域 + 同 IP | 对未解析旧 Host `--resolve` 到网关 IP | 对 Host=业务 200；错 Host=网关 404/403 |
| 4 命名习惯 | 有第一段后续猜：`/{svc}/{module}/{method}/{id}`、`/gp/{ctx}/{action}`、`ForFree`/`open`/`anon` | 405 或业务 JSON |
| 5 包 | C 端 Web 没有的方法名 | 交给 android / miniprogram，产物回到本 skill 打 Host |

主站源1 为空是常态，进入源2/3，不要结案。

**通过门：** 路径字符串能指出公开出处（JS 行 / urlscan / 兄弟域指纹）。没有出处仍是假设。

---

## P4 密钥还原与鉴权证伪

目标不是解密，是判断密码学有没有替代鉴权。

从 JS 必须对齐 6 项（提取步骤走 `recon-js-analysis`）：

1. 取钥接口（`getRsaKey` / `getPublicKey` / ticket）
2. 算法与填充（JSEncrypt 默认 PKCS#1 v1.5）
3. **POST 字段名**（响应里的 `uuid` 可能要改名为 `rsaUuid`）
4. 密钥生命周期（多次 GET 是否同一 uuid/公钥 → 静态密钥 ID）
5. 加密范围（只加密关键字，还是整包）
6. 无 Cookie 能否取钥

口令：

- 客户端能取的「密钥」，对攻击者不是密钥。
- 加密查询字 ≠ 证明你是谁。
- 字段名以 JS 为准，猜错会假阴性（空数组）。

### T0–T3 对照（详细越权矩阵见 `auth-access-control`）

| 编号 | 条件 | 仍业务成功则 |
|---|---|---|
| T0 | 无 Cookie、无 Authorization | 未授权 |
| T1 | 错误/过期 Token | 鉴权没校验 |
| T2 | 有登录但无该业务角色 | SSO 与 ACL 分离，记录「能进门不能办事」 |
| T3 | 去掉加密或改错绑定字段 | 加密是协议还是装饰 |

T0 成功 + 敏感字段 → 未授权成立。T0 仅 302/ACL、业务接口已下线 → 路径存在但利用链断，分开写。

---

## P5 字段对齐（空结果最易误判）

1. GET 目标方法 → 吃 405，改 POST
2. POST `{}` → `data:[]` 说明已进控制器
3. 明文关键字 / 错字段名 / 对字段名+密文 三组对照
4. 从**同类加密接口**抄字段名（改密用 `rsaUuid`，查询多半同一个）

示例（字段名错了会像没洞）：

| body | 常见结果 |
|---|---|
| `{}` | 200 `[]`（无鉴权） |
| `{title: 密文}` | `[]`（缺绑定） |
| `{title, uuid}` | `[]`（名错） |
| `{title, rsaUuid}` | 非空列表 |

**通过门：** 至少一种变体能把 `[]` 变成非空，或错误信息给出参数名。否则只写「接口暴露，危害未证实」。

路径对齐之后的全方法/BOLA/分页遍历交给 `api-protocol-security`。

---

## P6 迁域复查

旧站下线必须四问：

1. 旧 Host 是 NXDOMAIN 还是 301？301 的 Location 是新战场。
2. 新品牌域有没有把 API 一起搬走，还是只搬了 C 端壳？
3. 同 IP 上哪个 ServerName 还在反代这套前缀（`/gp` `/mag`）？
4. 前端 chunk 删了方法名，网关上方法还在不在？（405/200 比 JS 诚实）

---

## P7 失败升级

没到 L4 不准写「无此接口」：

| Level | 动作 |
|---|---|
| L1 | 主站 JS 全文搜 |
| L2 | 异步 chunk / 独立 H5 JS |
| L3 | 兄弟域、CDN、urlscan、CT |
| L4 | 网关 Host 探测 + 405 / 业务 JSON |
| L5 | 换入口：APP、小程序、开放文档 |
| L6 | 旧方法名 + 新 Host |
| L7 | Wayback 旧 JS 的 baseURL 打现网 |

---

## P8 危害落地与输出

- 列表类：公开公司简称作关键字；统计条数与含账号/税号字段数；正文只出脱敏样本。
- ID 类：先解决 ID 从哪来（公开格式、C 端自己的单、枚举）。没有合法 ID 不能宣称可打任意用户。
- 复现用 **curl**，证明请求无登录 Cookie。
- 覆盖度必填：✅已测 / ❌未测 / 🔄变种 / 💡关联；同步写进线索板第 7 节。
- 评估表走总纲第 5 节。成稿走 `report`（只读板上「已证实」行）。

---

## 对照（决策句，不是只打这两个目标）

1. 主站没有，去兄弟域和历史域。
2. SPA 的 404 不是接口的 404。
3. 「链接不存在」/405/空数组，往往比统一 404 更值钱。
4. 路径跟 Host 走，不跟品牌官网走。
5. 前端能取的 RSA/AES/uuid 只是协议，不是登录。
6. 加密字段名以 JS 为准，猜错就假阴性。
7. H5 下线只删了壳，旧 method 可能还在网关上。
8. 截图证明利用，公开面证明发现。

类型对照：角色隔离后台（C 端无路径）/ 专项独立 H5 / 换皮迁域 / 前端已删后端未下。四类可叠加。

---

## 修复（未授权接口）

- 网关统一鉴权；`ForFree`/`open`/`anon` 默认视为危险命名，必须有身份或强频控+最小字段。
- 前端加密不能替代登录；取钥接口同样要鉴权或只对已登录会话下发。
- 下线 H5 必须同时下线路由/控制器，不能只删 DNS。
- 企业抬头等财务身份禁止对未登录返回完整银行账号。
