# authbypass-test · part 1 · part 2

> 分段 2/2。索引见 `authbypass-test-p1.md`。

打（不登录）：用该 sig 登 `IM 接入域`：`openim/login`、`getmsg`、`friend_get`、`get_joined_group_list`、群资料/消息。体验页再打 login_token 看 `data.phone`。对照闸：其它业务口应请登录；发签口只加 trace 头、userId 换成 interviewer_/candidate_ 一类；拿 authorization/signature 打群历史/进房。匿名 appkey 发票后，access/get 把 uId 换成 interviewer_/admin，看回包 userID。v2 `by_app_name` 回 IP not allowed **别停**，改打 v3 同 path，只要 `appName`。官方 Demo：抄 JS 里的 UserSigService URL 和 pwd，identifier 填已有用户编号；pwd 空串再打一枪。拿 userSig 打 friend_get，对照游客空号。

算成：拉到**他人**会话/群成员/好友，或明文手机。

假点：只能登游客 `null`、空会话、只有自己建的空群；换别人 UserID=70013；`none_auth` 只新开空号；演示号没绑手机不算。单站没中不删战法索引这行。

### 写死产品号发共享 JWT（战法索引有指针）

认：AIGC/小工具 H5 或落地页把产品号 / `qbid` 写死在脚本里。发签口（`account/qb` 一类）不登录就给**共享产品号** JWT，票里 name 是产品名不是游客。JS 往往只有 create / GET by id，没有 list。

打（不登录）：

1. 抄页面写死的产品号打发签口  
2. 带着票 POST 同源 `.../task/list`（或 workflow/history 一类 JS 没写的 list）。对照：不带票应未登录；空包 list 仍出 total  
3. 跟 `userImages` / 原图 CDN，确认真下到人脸/证件照  

算成：list total 海量且带**他人**原图/证件照。

假点：票只能建空任务；list total=0 或只有自己刚传的。密钥实值、某次 JWT 不进库。单站没中不删战法索引这行。

### 官方客服链签发外站（战法索引有指针）

认：企业客服 H5 签发链；内联有 `getXcxLink`/`get_wx_open_link`。不是通用跳转页。

打（不登录）：POST `queryStr=caUrl=外站&urlType=2`。打开返回的 `客服落地链`。

算成：落地页正式名是官方客服号，`base64Decode` 出的 query 是你填的网址。

假点：只签发本站 `/ca/`；落地页不带 query；必须登录。单站没中不删战法索引这行。

### 演示号领云钥（战法索引有指针）

认：云厂商产品 Demo / 体验页 / 控制台代理 / 供应商后台；领 STS、联合身份、建任务只要业务 id 或空 body，不要 Cookie。领 STS 口缺参只报字段校验不是登录闸，不一定有演示号。不是对象存储 STS 通配覆盖（那枪见 `../../web-file-path/knowledge/file-upload-test.md`）。

打（不登录）：有演示号抄客户编号再打领钥 / 建任务 / 联合身份。没有演示号也打领钥口：缺参报字段校验别当登录闸。空 body 报缺 `AppId`/`Uin` 也别当没口，带能解析的数字 Uin 就可能发联邦 STS；bucket+file_name 仍打。领钥口可能在独立 demo CDN 的 `/openapi/`（页面 JS 跟过去）。分享域前端 HMAC 过网关后，对照其它口「token 不合法 / Token校验失败」，`/share/token/info` 一类领 STS 口不带分享页 token 仍打。换 bucket 用 PUT/NoSuchBucket 探活桶。钥拿去 GetCallerIdentity 对主账号；有启动、检索一类 Action 再签（余量不够别停，看能不能问出账号或出账单）。Epaas 过 HMAC `SC-SIGN` 后对照名单仍 UserNotLogin，专找 GetUploadURL/FileName 不校验 token（过签≠出数）。

算成：临时钥匙能问出 AccountId/角色名；同一身份下列表出现刚建的任务；或检索出口径出账单/实例/他主体业务字段；或活桶 PUT 200。

假点：钥匙调业务 API 全 Unauthorized；领钥口请登录/401；create 200 但列表没有。没有演示号/客户编号不是假点。单站没中不删战法索引这行。密钥实值不进库。

### 未登录签发合作方登录链（战法索引有指针）

认：电子合同 / 供应商门户人打开是登录页，框里只填可枚举合作方数字 id（partnerId / supplierId 一类），没有密码。未登录 `getUrl`（或同类签发登录链）直接回 `partnerId`+`generate`+`code`。旁边有 `setCookies` / 换票口吃这三项下会话。

打（不登录）：

1. 登录页 JS 抄签发口，合作方 id 用页上提示的数字或邻号  
2. 把回包三项 POST 给 setCookies / 换票口，抄 Set-Cookie  
