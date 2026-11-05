# idor-test · part 2 · part 2

> 分段 2/2。索引见 `idor-test-p2.md`。

## 承接

打（不登录）：对照 `queryUserInfo`/`queryFeedbackList` 应 deny。列表 `categoryId` 从 1 试，再把 `id` 丢给 Info。**没有 json 列表也打 HTML 详情**（`showKnowledgeInfo.htm?knowledgeId=` / `help_detail.htm?help_id=`），用现代 UA（IE 可能触 netd）。公告口：页面公开菜单对照条数很少时，把 `callname` 换成 `getKnowledgeList`（`callcontent` 带翻页），再 `getKnowledge` 打详情 id。CMS：先 `siteList` 抄非官网 siteId，再 `contentList` 看频道名，换 siteId 打 `content` 详情；默认官网 Banner 不是这枪。网关报 `loginMode is null` 别停，头加 `loginMode: 0`；siteList 仍缺 siteId 失败时，直接带内部 siteId 打 contentList。content 也要带 siteId，缺了会当没正文。chatbot：`chat_dir_id` 一类目录口 401 别停，改打检索口（`search_recommend` 一类），`searchText` 填常用字、`id` 填菜单号；正文看 `behavior.value`。

算成：列表 `pager.items` 上千或 count 海量，且 Info/HTML/详情/`behavior.value` 出**内部**话术/协查/短信/运营知识库正文，不是公开 FAQ / 对外协议。

假点：只有公开帮助稿/错误码/对外协议/官网 Banner；Info 只要标题；工单口也放行（那是另一条）；只打了默认官网站点；dir 节点 401 就停；检索口只出标题 content。单站没中不删战法索引这行。

### 开放支付假签枚举 appId（战法索引有指针）

认：开放支付 / 进件网关 body 有 `appId`+`sign`（可再加 `random`/`merchantId`）。假签时活应用回 `MERCHANT_NOT_EXIST` 或 `SUCCESS`，死应用回 `SIGN_ERROR` / `APP_NOT_FOUND`。不是「JS 写死盐自己算」那一行，也不是文档里抄出真 AppSecret。

打（不登录）：

1. `sign` 填一串假值（32 个 `a` 一类），扫 `appId`，对照回码  
2. 活的再打商户查询（`query` / `query/v2`）换 `merchantId`（文档示例号、邻号）  
3. 同一套假签再点签订/协议口，只看回包是否接受；不要批量签、不要改结算卡  

4. **ST / 演示收银台预下单**假签或 node 代签也能进生产网关时：不登录 POST `/api/precreate` 或 `/demoapi/precreate`，sign 填假值 + 活 appId + 他人 merchantId。本站查单 404 别停，打生产 `/api/pay/query`。

算成：出他人商户身份证 / 银行卡 / 手机；或生产查单 `ORDER_NEW` 且有他商户交易号。

假点：假签一律 `SIGN_ERROR`；`SUCCESS` 但证件卡号全空；文档示例 appId 已死；只回 `channelPayerNo` 且生产查单不存在；只能给演示店挂。单站没中不删战法索引这行。密钥实值不进库。

### 短链 302 query 带手机（战法索引有指针）

认：短信/运营短链解析站；猜中的短码 302 到落地页，query 明文带 `phone` / `name` / 金额。首页可能是 OpenResty 欢迎页、302 到品牌官网、或 `index.html` 只有 Hello，**不要只看 `/` 当整站证伪**。

打（不登录）：

1. `/open` `/app` `/s/` `/www` 加短字典（`aaaaa`、`1`、`1234`）  
2. 只看 302 目标 query，不要跟到落地业务域  
3. 对照：对不上的码应失效页、没有手机号  

算成：跳转地址里是**别人**的手机/姓名。

假点：失效页；公开营销无 PII；短码要真短信才解析。单站没中不删战法索引这行。首页 Welcome / 302 官网 / Hello 壳不是假点。

### 隐私号失败回真实号（战法索引有指针）

认：订单/门店/物流 H5 调隐私号或虚拟号（AXB）口；未登录只要业务 appid + 可遍历对象号。失败时回包把真实 11 位手机当下发，文案还写获取隐私号失败、将用真实号码拨打。不要只当虚拟号口丢掉。

打（不登录）：

1. 前端抄 functionId / 隐私号 path，对象号从 0、2、邻号打  
2. 对照：非数字对象号应参数错、没有手机  
3. 换号号码变才算批量  
4. 网关空 Origin 或本站 Origin 回 `cross-origin 403` **别停**，改业务域 Origin（订单 / 购物车 / H5 域，不钉某一家 host）再打  

算成：回包是**他人**真实手机。

假点：只出虚拟号/中间号；必须登录；换号号码不变；空 Origin 403 当没口。单站没中不删战法索引这行。

### 入驻 H5 空参出招商通讯录（战法索引有指针）

认：入驻 H5 有招商电话页；同套其它 settle 口 302 未登录。JS 里按品类查 BD 的 RPC（queryBd / bdInfo 一类），industry/类目空时 body 空。页面上可能只摆 400 热线。

打（不登录）：

1. 从招商电话页 JS 抄网关 `/api` 和 functionId  
2. 类目字段空着打（`body={}`）。对照：填死数字类目号常回空数组  
3. 同套其它 settle 口 302 别当整站没口  

算成：内部 BD 姓名+11 位手机+企业邮箱整表。

假点：类目填死数字出空数组就当没口；把页面公开 400 热线当这枪。单站没中不删战法索引这行。

### 入驻 H5 写死 token 换 pin（战法索引有指针）

认：入驻 H5 / 小程序打包 JS 把 OCR / 企业信息口 token 写死。JSON 口只要 pin（或同类账号）+ 非空 token，不要 Cookie。对照：token 留空或省略只回空 data。

打（不登录）：

1. 从入驻 chunk 抄写死 token 和企业信息 path  
2. 空 token 对照应空 data  
3. 带写死 token，pin 用 `admin` / `test` / `0` / 短账号再打  
4. 写死那串过了，再填任意非空串对照（过了说明不校验 token 内容）  

算成：换 pin 出对应真实手机。

假点：空 token 也出数（完全无鉴权，另一条）；token 过了仍只出自己刚入驻的。单站没中不删战法索引这行。密钥实值不进库。

### 公司名/抬头自动完成（战法索引有指针）

认：报名/入驻/发票抬头自动完成；页上下拉只出公司名；接口走工商/邓白氏 Match 或抬头 suggest。前端可能把该口标 `auth:true`，服务端仍不验登录。

打（不登录）：

1. POST 名称+国家码，或抬头口。suggest 字段可能是 `prefix`（填 `title` 会报「关键词不能为空」像没入口）  
2. suggest 报关键词空别停：同产品还有专票/工商补全口，字段就是 `title`，前端标 `auth:true` 仍打  
3. 对照页面下拉：页上只有公司名，回包多出手机/卡/住址才算  

算成：回包出现负责人或开票手机/住址/银行账号，且对得上人。

假点：下拉和接口都只有公司名；必须登录；公开企业名录没有电话；前端标 auth 就当没洞。单站没中不删战法索引这行。


### Mass Assignment / 隐藏可写字段（战法索引有指针）

认：注册 / 改资料 / 建用户的 JSON 比页面控件多；Swagger、管理员「建用户」或前端注释里多出 `role` / `isAdmin` / `verified` / `tenantId` / `balance` / `permissions`。

打：

1. 对照管理员建用户 vs 自己注册/改资料，差出来的字段才塞。没有对照就从 Swagger / JS 抄。
2. 只对自己的号塞一次；过了立刻改回。不要改别人已有账号的角色。
3. `__proto__` / 嵌套 `user.role` 也试；这和 PP 模板 RCE 不是一条（PP 见 `../../web-deser-xxe/knowledge/prototype-pollution-test.md`）。

算成：自己号变成高权，或余额/认证状态真变。字段吃了、权限没变 → 没成。

假点：只能改展示名；公开运营开关；服务端白名单吞掉多余键。单站没中不删战法索引这行。没注册/改资料口不要发明字段。
