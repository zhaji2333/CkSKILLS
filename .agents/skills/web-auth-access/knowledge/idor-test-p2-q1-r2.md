# idor-test · part 2 · part 1 · part 2

> 分段 2/3。索引见 `idor-test-p2-q1.md`。

20. **收集表/问卷填报详情 JSON 的 relative / 关联表挂着答卷 sheet 别停。** 人打开的是填报页，答卷表可能另有 id。不登录打答卷表详情/opendoc。对照：填报页只是题目，答卷表才出身份证/手机单元格。
21. **内容预览口只要数字 contentId，回包 `isDelete=1` / 已删除 / 未发布别停。** 对照公开橱窗应没有这篇。出整页 H5 或编辑器 JSON 才算，不要只看标题。
22. **畅课 / Neptune `api.do?no=` 缺 flag 回 -8 别停。** 列表方法加上 `flag=course` / `news`（JS 里课程列表请求抄）。详情 `show!play.do` 请登录也别当没洞，看列表行 `description` HTML 是不是内部课/培训简介正文。登录白名单里的租户列表方法（常见 `no=4000`）同样打。

算成：未公开业务正文从列表出来（不是公开橱窗标题）；或他主体手机 / 证件；或证照图注册人行印着身份证号；或未发布/已下架作品源码正文。

假点：加了可见性参仍只出公开稿；只有标题没有正文；列表 401 就当没洞；edit 和 publish 出同一份已上架正文；空数组和缺参出同一份上架稿；`materialType` 仍只出公开橱窗；只带业务 id 出空壳就当没洞、没再加审核状态；只打了公开搜索/橱窗详情就当没洞；浏览页写请登录就当没洞；数字 item 仍是那几本公开文档。打错 Color 域当没口不是假点。单站没中不删战法索引这行。

### 过网关无需鉴权头（战法索引有指针）

认：物流 / 开放网关（`lop-proxy` 一类）前端 JS 写死 `Auth-Control: no-auth` + `LOP-DN`（业务域）。其它业务口请登录，带着这组头名单/运单口仍出数。

打（不登录）：

1. 抄 JS 里的 `LOP-DN` 和 `Auth-Control: no-auth`（或同类过网关鉴权头）  
2. 空翻页打站点/名单口；再换可枚举 `siteId` 打运单/详情  
3. 对照：不带头应请登录或 Host 未注册  

算成：出他人手机 / 住址 / 站点联系人，不是公开轨迹。

假点：头过了业务仍请登录；只有公开轨迹没有 PII。单站没中不删战法索引这行。

### 匿名会话读报名表（战法索引有指针）

认：BaaS 匿名 session；列表口不验管理员。页面写死几个管理员 ID，后台跳登录。Appwrite / Weavefox / TablesDB 是常见皮，没有这名仍打。前端常见 `Client().setEndpoint`、`X-Appwrite-Project`、`POST /v1/account/sessions/anonymous`；报名/活动表走 `tablesDB.listRows`。

打（不登录、不要管理员号）：

1. 无 Cookie 先打 `GET /v1/tablesdb/{db}/tables/{table}/rows` —— 基线应是 `total=0` / 空 rows（系统其实会拦游客）  
2. `POST /v1/account/sessions/anonymous` body `{}`，头带同一 `X-Appwrite-Project`，拿 `Set-Cookie: a_session_…`  
3. 带着这条匿名会话再打同一 listRows  

算成：匿名会话后 `total` 相对空会话暴涨，rows 里是**别人**的手机 / 邮箱 / 报名正文。管理员白名单只写在浏览器里、没套到列表口。

假点：无会话已经是全表（那是完全无鉴权，另记）；匿名会话仍空或只有自己刚填的一条；DELETE 别人行 401 只说明写没开，读仍算；公开运营展示名单。单站没中不删战法索引这行。

和「无 Project key、连匿名会话都不用就能 CRUD」不是同一枪：本条关键是 **匿名 session 被当成已登录，且不验管理员**。

### 云开发匿名用户表（战法索引有指针）

认：云开发开了匿名登录；有低代码数据源函数。控制台或前端能抄到环境 id。不是战法索引已有的 proxy `targetUrl`，也不是 BaaS `sessions/anonymous`。

打（不登录）：

1. `POST https://{envId}.api.云开发网关/auth/v1/signin/anonymously`，头 `x-device-id`，body `{}`，拿 JWT  
2. `POST /v1/functions/lowcode-datasource`，`Authorization: Bearer` 那张票，body `dataSourceName=sys_user`、`methodName=wedaGetRecords`（`getRecords` 同源）  
3. 对照：同一网关 `GET /auth/v1/user/query` 应拦匿名；数据源名 `users` 常行权限失败，**不要停**，`sys_user` 才是系统用户表  
4. HTTP 网关（常见 `/web?env=`）回 `LOGIN_TYPE_DISABLED` **别停**：改 `POST /web?env=`，`auth.signInAnonymously` → `auth.getUserInfo` 拿 `jwt;expire`（**不要去掉分号后缀**）→ `functions.invokeFunction`，同样打 `sys_user` / `wedaGetRecords`  
5. 旧 HS256 票丢 `/v1/functions` 报 `KID_INVALID` → 这枪没成，换第 4 步网关票，不要当「数据源不存在」  
6. `sys_user` 行权限失败 **别停**：同一张 `/web` 匿名票改 `database.countDocument` / `database.queryDocument`，`collectionName=users`（互联登录落库的用户表，不是数据源名 `users`）  

算成：records 里是**他人**手机 / 邮箱 / uin / 超管标记，不是自己刚匿名建的空号。

假点：行权限拒匿名且 `/web` users 集合也空；数据源不存在；只出演示 todo/sales；旧 HS256 票 `KID_INVALID` 当没洞。HTTP 网关 `LOGIN_TYPE_DISABLED` 不是假点。数据源名 `users` 失败不算假点。单站没中不删战法索引这行。密钥实值、某次 JWT 不进库。

### 详情抄 openid 再打信箱（战法索引有指针）

认：招募/指定用户详情带 `specifyUsers` 或 openid；H5 写死 SHA256 请求签名；或邀请页地址已有 `?openid=`。

打（不登录）：

1. 调详情抄 openid  
2. 钥算 Signature 再打 `/msg/message/list/`  
3. URL 上已有 openid 则再打无签名的 `get_invite_code` / `count` / `detail`，名单 `uid` 可再填回去  

算成：换 openid 信箱或邀请码/名单变，出现对方积分过期通知或打码手机昵称。

假点：列表人人一样只是全站广播；接口要真登录/签名；假 openid 没有邀请码；公开运营名单。单站没中不删战法索引这行。

### 资料库 nodeId 未授权读全文（战法索引有指针）

认：发布页 conversation-data 的 artifactMap 有资料库 `nodeId`；主站 `/space/d/` 要登录。

打（不登录）：打发布域 `POST /space/api/page/share/query/pagechunk`（body=`pageId=nodeId`）。对照：分享页自己的 pageId 应是「不可分享」。

算成：拉到他人文档全文（标题/角色卡/大纲，`role=editor`）。

假点：只读到已发布 HTML 快照；pagechunk 对资料库也 12607；正文已在对话快照里。单站没中不删战法索引这行。

### 匿名 CSRF 头读详情（战法索引有指针）

认：匿名 CSRF/临时 token 口直接出 token；业务详情只验这个头不验登录；query 的数字 id 和回包 `data.id` 可以不是同一个号。不是助手 `GetHistoryList` 可选登录头（那枪见「助手历史未授权读他人任务」）。

打（不登录）：

1. 打 csrf/token 口拿头  
2. 详情换数字 id（1、2、13），**query id 对不上回包 id 别停**  
3. 对照：不带头应失败；不存在的 id 应「不存在」

算成：未上架/测试训练脚本或内部会话正文（cardMap/对白全文，不是标题）。

假点：只有公开广场；token 过了仍空。单站没中不删战法索引这行。

### 自定义身份头当会话（战法索引有指针）

认：管理后台 SPA 请求拦截器把自定义头（`User-Id` / `employeeId` / `X-User-Id` 一类）当登录身份，不要 Cookie。未登录名单口往往只出数字员工/BD 号，没有手机。

打（不登录）：

1. 抄 JS 拦截器里的头名  
2. 未登录打名单（空参/总部筛）。只有数字号**别停**  
3. 把头换成这个号打当前人信息口。对照：不带头或填 `1` 应查空  

算成：出他人姓名+11 位手机。

假点：头过了仍空；名单已经出手机（那是另一条）。单站没中不删战法索引这行。

和「匿名 CSRF 头读详情」不是一条：那条是临时 token 头，这条是**身份数字号进头**。和「入驻 H5 空参出招商通讯录」也不是一条：那条类目空着整表出手机，这条名单没手机还要再把头当身份打一枪。

### 客户详情口还吃 phone（战法索引有指针）

认：CRM / 企业 IM 客户详情口前端只写了外部联系人 id（`externalUserId` / `contactId`）。只带这个 id 回空壳。后端还吃 `phone`，常还要 `tagShow` / `udfShow` 才出内部字段。

打（不登录）：

1. 对照只带外部联系人 id 应空壳  
2. body 加 11 位 `phone`，并把 `tagShow` / `udfShow`（或同类展开字段）打开  
3. 空号 / 乱填应空壳；换号必须换人  

算成：出他人姓名 / 公司 / 内部 UDF，且查的就是这个完整号。

假点：phone 一律空或只出同一条测试号。身份证槽位空不算假点。单站没中不删战法索引这行。

### 助手历史未授权读他人任务（战法索引有指针）

认：助手/Agent 前端有 `GetHistoryList`；登录态只在可选头里。不是对话口工具执行（那枪见 `../../ai-agent/knowledge/agent-tool-exec-test.md`）。

打（不登录）：调列表，换 guid 对照是否同一批；再把 `session_id` 丢给 `GetHistory`。翻页 `last_ts`+`direct=back`。

算成：列表/详情出现**他人**任务原文（下载、订阅、对话卡片），不是公开广场。

假点：只出广场 `GetSquareTasks`/`share_id`；换 guid 列表变空或只剩自己的。单站没中不删战法索引这行。

### 写死 appKey 打业务表（战法索引有指针）

认：前端 `AV.init` / LeanCloud 写死 `appId`+`appKey`（或 `X-LC-Id`/`X-LC-Key`）；或 nocode/supabase 落地页写死 `role=anon` JWT。

打（不登录）：带这两头打 `/1.1/classes/*`：先 `_User` 对照应 403，再扫业务表 count/limit，能写就改探测字段再删回。supabase 带 `apikey`+`Authorization: Bearer` 打 `/rest/v1/` swagger 列出的表。**rest 表 403 / 只有公开运营配置别停**：改打 `POST /storage/v1/object/{桶}/{官方前缀}`，头 `x-upsert:true`（见 `../../web-file-path/knowledge/file-upload-test.md` STS 第 9 步）。

算成：业务表 `count` 海量或出现**他人**稿/邮箱/电话；PUT 改别人 `objectId` 成功。

假点：`_User` 和业务表都 403；只能读自己刚建的；只能 LIST 公开运营配置。单站没中不删战法索引这行。密钥实值不进库。

### 填表模型带标准答案（战法索引有指针）

认：问卷/测验填表模型口；前端写死业务 id 或白名单（`FORM_WHITE_LISTS` / 演示 encryptFormId 一类）；回包 schema 带 `answer` 标准答案或内部审核题干/样图。不是公开报名表标题，也不是已经交过的答卷列表。

打（不登录）：

1. 从 JS 白名单/演示 id 打 getModel / schema / getFormModel，别停在表单标题  
2. schema 里的样图 preview/imgUrl 跟着打开  
3. 管理 list/export/fillList 另打；没有填写记录不要编答卷  

