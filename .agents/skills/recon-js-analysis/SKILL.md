---
name: recon-js-analysis
description: 当开始新目标、攻击面不清晰、需要资产测绘/信息收集/前端JS分析/接口与敏感信息提取时调用。负责webpack拆解、source map还原、API端点与密钥提取、历史资产发现、高价值入口定位。命中场景：找不到接口、需要找密钥/隐藏功能/旧版本接口、JS加密与签名逻辑需要还原。
---

# recon-js-analysis — 资产测绘与前端 JS 深度分析

## 何时调用（触发条件）

- 开始测试新目标，攻击面不清晰
- 需要提取 API 端点、参数结构、鉴权逻辑、隐藏功能
- 需要还原 webpack chunk / source map / 混淆代码
- 需要找硬编码密钥、AK/SK、内部域名、测试账号
- 需要发现、历史资产、旧版本接口
- 需要确定高价值入口点（用户中心/支付/后台/API）

## 一、资产测绘与信息收集

```
端口服务：nmap / masscan / 云资产API
目录扫描：dirsearch / ffuf / 403绕过
JS分析：LinkFinder / SecretFinder / API端点提取
APP逆向：jadx / frida / 抓包分析隐藏接口
```

## 二、信息收集要"脏"（历史与周边）

必须尝试的信息源：
- **Wayback Machine**：翻旧版本页面/JS（可能有已删除的接口和功能）
- **GitHub/GitLab搜索**：目标域名、内部接口、泄露的密钥/配置
- **Google Dork**：site:target.com filetype:pdf/xls/doc/sql/log/bak
- **证书透明度日志**：发现隐藏的子域名
- **招聘JD**：推断技术栈（用了什么框架→对应什么已知漏洞）
- **JS中的注释/TODO**：开发者留下的线索
- **robots.txt / sitemap.xml**：暴露的隐藏路径
- **前端source map**：还原完整前端源码
- **APK/IPA反编译**：提取硬编码的接口和密钥
- **更新日志/Changelog**：新功能=新攻击面

## 三、JS 分析方法论（必须吃透再动手）

**原则：JS不吃透，不发包。**

### 3.1 完整还原

- webpack chunk拆解、source map还原（如有）
- **自动化工具**：Packer-InfoFinder（开源 webpack 资产提取工具，可自动发现 JS、拆解 chunk、提取接口与敏感信息）

```bash
# 单目标扫描（自动发现JS、拆解chunk、提取接口和敏感信息）
python Packer-InfoFinder.py -u https://target.com --finder

# 批量扫描
python Packer-InfoFinder.py -l urls.txt --finder

# 指定JS文件分析（跳过HTML入口，直接分析JS）
python Packer-InfoFinder.py -j "https://target.com/app.js,https://target.com/chunk.js"

# 无头浏览器模式（捕获动态加载的JS）
python Packer-InfoFinder.py -u https://target.com --browser --finder

# 带代理扫描
python Packer-InfoFinder.py -u https://target.com --finder -p http://127.0.0.1:7890
```

- 格式化/美化混淆代码，逐模块阅读
- 优先定位：路由定义、API调用、请求拦截器、响应处理器

### 3.2 必须提取的信息

- 所有API端点（包括注释掉的、条件判断里的、环境变量控制的）
- 请求参数结构（必填/选填/隐藏参数/调试参数）
- 鉴权机制（token生成逻辑、签名算法、加密方式、刷新机制）
- 前端路由表（React Router / Vue Router / Angular Routes）
- 角色/权限判断逻辑（哪些功能对哪些角色开放）
- 硬编码的密钥、AK/SK、内部域名、测试账号
- **URL / IP / 域名清单**（webpack/app.js/抓包/反编译中所有请求地址）：API 网关、后台/管理端域名、CDN/OSS 存储桶、内网 IP、云服务端点、第三方回调地址——每一条都是**可扩展攻击面**，单独列出并进入资产测绘流程
- **appid / appkey / AppSecret / 推送密钥等应用凭证**：单独列出，作为重点深挖对象（见 3.3）
- Feature Flag / Debug开关 / 环境判断（dev/test/prod）
- WebSocket端点和消息格式
- 错误处理逻辑（哪些错误会泄露信息）

### 3.3 资产扩展与凭证上报（提取后必须做）

**① URL/IP/域名 → 资产扩展（可扩展分析内容）**

- 将提取的每个 URL、IP、域名单独成行，标注来源（`webpack 提取` / `app.js` / `source map` / `APP 抓包` / `APK 反编译`），便于交接与复盘
- 全部进入资产测绘流程：子域名枚举、端口扫描、目录扫描、指纹识别
- **APP 中抓取的 URL/IP/域名要提醒用户关注**：很可能是 APP 后台接口或业务接口域名，鉴权往往弱于前端接口，是比前端接口更高价值的测试目标（联动 `android-security-audit` / `miniprogram-security`）

**② appid/appkey 等凭证 → 上报并深入挖掘**

- 提取到 appid/appkey/AppSecret/AK/SK/推送密钥后，**必须上报给用户并单独列出**，作为重点深挖对象，不允许只放在接口清单里带过
- 深挖方向：
  - **验证有效性**：用 appid/appkey 直接调用对应后端接口/云服务 API——云厂商 AK/SK 可致云资产接管（联动 `cloud-infra-supply-chain`）
  - **定位归属**：凭证书透明度日志、代码仓库搜索、目标域名对比，确认凭证对应的域名与服务
  - **越权面**：appid/appkey 对应的管理接口、统计接口、推送接口是否可越权调用、是否缺少鉴权
  - **泄漏面**：多渠道验证（历史版本 JS、Wayback、日志、错误信息、GitHub 泄露）

### 3.4 分析输出格式

```
[JS分析报告]
接口清单：(列出所有发现的API端点)
参数结构：(每个接口的完整参数)
鉴权逻辑：(签名/加密/token机制)
隐藏功能：(debug接口/未启用功能/旧版接口)
可测试点：(按优先级排序)
```

### 3.5 测试执行

- 每个接口必须测试全部HTTP方法（GET/POST/PUT/DELETE/PATCH/OPTIONS）
- 每个参数必须测试：正常值、空值、边界值、类型混淆、数组化、超长、特殊字符
- 鉴权接口：有token测、无token测、过期token测、其他用户token测
- 发现的隐藏参数/调试参数全部尝试

## 四、高价值入口点定位

- 用户中心：注册/登录/找回密码/绑定手机/实名认证
- 支付流程：下单→支付→回调→退款→提现
- 文件功能：头像上传/附件上传/导入导出/报表下载
- 管理后台：/admin /manager /console /backstage
- API接口：/api/v1 /graphql /swagger /actuator

## 五、冷门但高价值的漏洞点（攻击面速查）

| 场景 | 漏洞类型 | 挖掘思路 |
|---|---|---|
| 客服/工单系统 | 存储XSS→钓鱼客服 | 提交工单内容含XSS，客服后台触发 |
| 邮件/消息通知 | 邮件头注入/SMTP注入 | 收件人、主题可控时注入换行符 |
| 二维码/短链生成 | SSRF/重定向 | URL参数可控，探测内网或钓鱼 |
| 地图/定位服务 | 信息泄露 | 泄露内部POI、员工位置 |
| 日志/监控接口 | 未授权+敏感信息 | /actuator /metrics /debug |
| 第三方登录 | OAuth劫持 | redirect_uri校验不严 |
| 分享/邀请功能 | 越权/信息泄露 | 分享链接可遍历、权限过大 |
| 数据导出 | 注入/越权 | 导出条件可控、无归属校验 |

## 六、输出与交接

完成本技能后，将提取的接口清单、参数结构、鉴权机制、隐藏功能整理为可测试清单，按类型分发给对应专项技能；**同时按 `hunt-clueboard` 写入 `hunts/<目标>/CLUEBOARD.md`**（Host/路径/钥/否定证据当轮落盘，不只放在对话里）：
- 零身份、路径不在当前前端、加密当鉴权、迁域/兄弟域漏路径 → `unauth-path-key-hunt`
- 接口/鉴权问题 → `api-protocol-security` / `auth-access-control`
- 参数拼接/注入点 → `injection-vulns`
- 文件相关功能 → `file-handling`
- URL可控功能 → `ssrf-internal-network`
- 提取的 URL/IP/域名清单 → 资产测绘扩展（新子域/新端口/新后台），APP 来源的提醒用户关注后台接口域名
- 提取的 appid/appkey/AK/SK 等凭证 → **上报用户并深入挖掘**（验证有效性、打云资产/后端接口，联动 `cloud-infra-supply-chain`）

