# authbypass-test · part 1 · part 1 · part 1

> 分段 1/2。索引见 `authbypass-test-p1-r1.md`。

# authbypass-test · part 1 · part 1

> 分段 1/2。索引见 `authbypass-test-p1.md`。

# authbypass-test · part 1

> 分段 1/2。索引见 `authbypass-test.md`。

## 承接

> 来源：实战知识库（真实 SRC 战法沉淀，已并入 CkSKILLS_v2）。
> 与 `rules/` 冲突时以 rules 为准；CORS 按 `../../../../rules/20-min-harm.md` 与团队取舍不主动挖。

# authbypass-authentication-flaws

打开是登录页 / SSO → 表单壳听 `../../../../rules/60-scope-iteration.md` §4.1.1：找业务面；别按本文件从头跑字典 / 验证码 / 无限试密。  
发会话、重置、改绑、换票、2FA 按本文件 + `../../../../rules/60-scope-iteration.md` §4.2.2 探针打，不要因为 §4.1.1 整摊跳过。表是每站下限，不是只准打这几枪。  
中间件裸默认口可一眼。滑块 / 发码 / 没进号的试密 → 转认证链，别停半截。写不写只认 `../../../../rules/40-evidence-report.md`。
英文字典/验证码 20 法/重置矩阵已砍；战法索引指针用标题搜。Host 毒重置见 `../../web-api-protocol/knowledge/http-host-header-test.md`。扫码登录 CSRF 见 `../../web-xss-frontend/knowledge/csrf-test.md` §18。

# Authentication Bypass

### 未登录改密口

认：改密/首次设密/重置最后一步，未登录也能打到。body 常见旧密或验码字段（`old_pwd` / `sms_code` 一类）+ 新密 + 身份 id。官方页写着要短信/旧密，接口仍可能吃空串。

打：不登录。旧密/验码置空或省略，新密过复杂度。对照：填错验码应拦；不存在的身份 id 应查空。同一密再打若报「与历史密码重复」=已经写进库，不是空成功。过了立刻改回；改不回就停，不要再换别人、不要登进去。

出：未登录 Success，改掉别人的密。

假点：只回 0 没写库；必须真旧密/真短信；Success 但登录走另一套 IdP、密没跟过去。

### IDaaS 未占用密保题

认：IDaaS 忘记密码。匿名提交用户名就签发 JWT，且 `scope` 是 `_`（不是 reset）。密保题库 id 可枚举，已绑在该号上的 id 写会 409。常见 IDaaS 皮 的 path 是 `forget_password/v2/sq`，同形态换皮照打。

打：

1. 不登录 POST sq，body `{"username":"admin"}`（或存在性口先确认的号）。
2. 带 token GET question，记下已绑 id。
3. POST `update_question` 写**未占用** id 的答案（已绑 id 不要硬写）。
4. `verifyquestions?type=RESET_PASSWORD` 带自写的三道题，换 `self.password.expired.reset`。
5. `set_password`：过了立刻改回；改不回停在回包，不要把管理员密改掉留下。策略拒且密保没写上 → 半条，不按打穿进表。

出：密保答案写到别人号上（改绑），或用该令牌真改掉别人的密。

假点：sq token 直接 set_password 报 `scope is not expected`；只能写已占用题 409；verify 错答；策略拒且密保没写上。单站没中不删战法索引这行。


### 未登录培训绑定口（战法索引有指针）

认：培训 / 学院 H5 网关把账号绑定、查询 RPC 放进未登录的 client 前缀（`/spapi/v2/client/` 一类）。body 吃 C 端 uid（`mtUserId`）+ 商家号（`bAccountId`），不要 Cookie。

打（不登录）：

1. POST bind：uid 换成别人、商家号换成自编  
2. POST querybind：只带 uid 或只带商家号  

算成：出对方手机，或绑定成功改绑。

假点：只回未登录/参数异常；uid 一律未绑手机且写不进。单站没中不删战法索引这行。密钥实值、某次手机号不进库。

### 联合登录只吃 uin（战法索引有指针）

认：云活动 / 黑客松 / 伙伴门户的签发口 body 只有 `provider` + 云账号 `uin`（或同类 uid），不验 OAuth `code` / `ticket` / `id_token`。公开列表或 by-code 能问出别人的 UIN。

打（不登录）：

1. 从公开伙伴/用户列表抄 `uin` 或先打 by-code  
2. `POST` 签发口，只带 `provider` + 对方 `uin`  
3. 拿 JWT 打 `me` / 用户信息  

算成：me 是**对方** UIN，能当这个号用。只出游客空号 → 没成。

假点：必须真 OAuth code；uin 未注册直接拒；票发了但 me 仍是自己。单站没中不删战法索引这行。密钥实值、某次 JWT 不进库。

### 活动实验室 login 不校验互联票（战法索引有指针）

认：活动页 login 吃互联 `openid`+`acctype`+`access_token`，服务端**不去互联校验**这张票。对照闸：同一套参数 `acctype=wx` 或 `access_token` 留空会登陆失败；`acctype=qq`/`qc`/`pt` 加假 token 仍发票。不是空密/omit 通用枪，也不是云活动只吃 uin 那条。前端 `fx_act_helper.js` / Milo 登录助手是常见皮，没有这名仍打。

打（不登录）：

1. POST `/api/login`（活动前缀跟页面，不要只认某一条 path），`access_token` 填假值、`acctype` 填 qq（qc/pt 再各一枪），`openid` 填可枚举号  
2. 拿 JWT 打 getRoles（按区服）/ bindRole 一类角色口。对照：不带头应要登录；wx/空票应失败  
3. 角色列表空别当没洞，换区服、换邻号；绑口跟到能绑上再停。过了能改回的改回  

算成：票里是对方 openid，角色列表出现他名下角色名/`charac_no`，或能绑上。

假点：只签发空号且角色列表全空、绑不上游戏角色；必须真互联票。密钥实值、某次 JWT 不进库。单站没中不删战法索引这行。

### 运营配置深链里的会话票（战法索引有指针）

认：未登录就能打的首页/运营配置 JSON，banner 跳转 URL（skipPath / jumpUrl / schema）query 里带着 `token` / `apptoken` / `access_token` 这类能当会话的串。对照闸：不带这串打 me 应登录过期。

打（不登录）：

1. 抄配置里整段跳转 URL，把 query 里的票放到 Token / Authorization 头  
2. 打 me / user info / 钱包  
3. 对照：同一口不带这串应过期  

算成：me 是别人的手机/角色，会话能当这个号用。

假点：票过期或占位串登不进去；配置只出运营文案没有票。密钥实值不进库。单站没中不删战法索引这行。

### 验签失败 302 回显算出的签（战法索引有指针）

认：支付/开放网关信封有 `sign_data`/`sign` + 商户号。假签时 **GET / DELETE / OPTIONS / HEAD 都可能 302**，Location 或 `msg` 里带服务端刚算的合法签（`calculateSign is:` 一类）。有的网关 GET 只 HTML/ILLEGAL_SIGN，换 METHOD 才漏；有的网关 **GET 自己就会 302 漏签**，不要只认 DELETE/OPTIONS。

打（不登录）：

1. 假签打签约/下单口，**GET 先看 Location** 有没有 `calculateSign`  
2. GET 没带签再换 DELETE/OPTIONS/HEAD，从 Location URL 解码抄签  
3. 填回 `sign_data` 打查询/订单。对照：假签仍失败，真签出他商户单  

算成：过签查出**他商户**未公开订单/账户正文（金额、关单原因、卡种）。

假点：所有 METHOD 都只报验签失败、没有算出的签；抄回去仍拒签。密钥实值不进库。单站没中不删战法索引这行。

### 身份供应商代调报错回显 token（战法索引有指针）

认：业务口帮前端调身份供应商。常见三皮：① 小程序码/跳转码口，`path`/`page`/`pagepath` 你能填，非法页时 message **原样带回** `access_token=`；② QQ/OAuth 换票口把 `client_secret` 拼进上游 URL，`redirect_uri` 改外域让下游 HTTP 5xx，报错 URL 把 `client_secret=` 吐给前端；③ 未登录业务口 `GET /api/business/access-token`（或同类领票 path）直接 200 出票，不必等报错回显。假码打本域回调往往只回业务错码、不带钥，**别停**。清单里有领票口，别只打签发码口。

打（不登录）：

1. 清单有领票口先 GET，200 且 `data` 是 `access_token` 就当已经抄到，不必再走非法 pagepath  
2. 没有领票口：path 填外站或明显非法页；换票口先假码+本域 `redirect_uri` 对照  
3. 换票口再把 `redirect_uri` 改外域，从报错 URL/message 抄 `access_token=` 或 `client_secret=`  
4. 身份票打 `身份供应商 API/cgi-bin/account/getaccountbasicinfo`，再 `/wxa/generatescheme`；QQ AppSecret 拿授权码换该应用 access_token / 打本站换票  

算成：能问出官方号主体/appid，或签发官方正式跳转码；或完整 AppSecret 能换成该应用 access_token。

假点：报错只有 ErrCode 没有 token/secret；假码本域回调不带钥；token 调身份接口无效；secret 换不了票。密钥实值不进库。单站没中不删战法索引这行。

### 开通页 RPC 下发 signKey（战法索引有指针）

认：支付 UISDK/开通页。未登录打配置或 thrift 口，body 只有可枚举 `appId`。死应用 `APP_NOT_FOUND` 且无钥，活应用回完整 `signKey`/`signMethod`。不是文档/webpack 写死（那枪见下一节）。

打（不登录）：

1. 换 `appId`。对照死号应无钥  
2. 抄活号 `signKey`，按回的 `signMethod`（常见 MD5，参按字典序拼 `&key=`）现签  
3. 打支付查询。对照假钥 `SIGN_ERROR`，真钥过签  
4. 过签别停在查询。打改结算卡 `change/card`：支行号差分出 `changeId`，原值报未变更才算写上。SUCCESS 但 `changeId=null` / 费率没变不算。过了立刻改回  

算成：完整 AppSecret 且真钥过生产验签；或查出他商户身份证/卡/挂单；或建出虚拟门店 poiId；或改掉他商户结算卡/开户行（`changeId` 有值）。

假点：回的是占位钥过不了验签；死活都 `APP_NOT_FOUND` 且无钥。密钥实值不进库。单站没中不删战法索引这行。

### 调试文档写死 AppSecret（战法索引有指针）

认：文档 / Demo / 官方包 / 接入 HTML / npm 历史包写死**完整** AppSecret（appId+appSecret、signKey、商户 pfx、SDK 钥），不是 `your-secret` / `YOUR_ACCESS_KEY` 占位。**wiki 把钥打成星号，同一套官方 zip / Demo / HTML 示例仍明文，别停。npm 旧版别当下架。** 常见皮：调试指南 `config.js`、FAQ 链到的 GitHub `properties`、文档操作截图 PNG、SDK zip 里 `prod/config.properties` / Demo Java `baseInfo`、接入 HTML 的 `MSDKConfig.json`、公网 npm `index.js`。旁边有换票口或按文档现签的生产口。算法在下面打哪，不钉某一家产品。

打（不登录）：

1. 从文档、FAQ 链过去的 GitHub、**或文档页操作截图**抄 appId/accessKey、appSecret/secretKey（实值只进报告，不进本库）。截图 OCR/看图即可，别停在 config.js
1b. 企业 IM/开放通讯录：换票后 `user/get` 或 `user/list` 的 mobile 是空串**别停**，打 `linkedcorp/user/get`（body `userid`）。对照通讯录口无手机、互联企业口出 11 位手机才算升链
