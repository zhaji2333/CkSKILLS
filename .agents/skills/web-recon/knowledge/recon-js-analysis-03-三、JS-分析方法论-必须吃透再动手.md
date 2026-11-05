# 三、JS 分析方法论（必须吃透再动手）

> 来源：CkSKILLS v1 `recon-js-analysis` §三、JS 分析方法论（必须吃透再动手）（迁移至 v2 知识块）

**原则：JS不吃透，不发包。**

### 3.1 完整还原

- webpack chunk拆解、source map还原（如有）
- **自动化工具**：Packer-InfoFinder（开源 webpack 资产提取工具，可自动发现 JS、拆解 chunk、提取接口与敏感信息）

```bash
python Packer-InfoFinder.py -u https://target.com --finder

python Packer-InfoFinder.py -l urls.txt --finder

python Packer-InfoFinder.py -j "https://target.com/app.js,https://target.com/chunk.js"

python Packer-InfoFinder.py -u https://target.com --browser --finder

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
- **渲染类接口**：`screenshot`/`snapshot`/`capture`/`preview`/`unfurl`/`pdf`/`export`/`render`/`print` + `url`/`link`/`target` 参数 + 异步任务轮询接口；命中即交 `ssrf-internal-network` 三（无头浏览器渲染专项）
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
