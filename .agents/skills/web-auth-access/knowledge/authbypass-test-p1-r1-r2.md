# authbypass-test · part 1 · part 1 · part 2

> 分段 2/2。索引见 `authbypass-test-p1-r1.md`。

2. 换票口：code 填假串。对照：secret 改成等长假值应「业务参数非法」；真密钥变成「授权码过期/无效 code」。本站没有 `/proxy`、换票口在另一棵业务域不打时，同产品独立 oauth `/oauth/v2/token` 直接 POST `grant_type=client_credentials`（对照假钥 `invalid_client`）
3. 分销/开放查询口：按文档 HMAC（key 小写字典序拼接，有 `test=test` 一类联调参就带上）。对照：假 secret 签名失败，真钥出该应用下的供给名单
4. 官方 CLI 改调试包/正式包口（`package/changeDebugVersion`、`changeVersion` 一类）。对照：假钥「密钥错误」，真钥过鉴权变成「游戏包资源不存在」也算钥活了，不要停在没上传真包。**改包口不要只打 upload/换版本**，WASM 分包 `packageBind` / `build` / `queryBuildResult` 也打；假钥密钥错误、真钥能绑到该应用名下算出写上
5. 网关写了服务器 IP 白名单：试 `X-Forwarded-For: 127.0.0.1`。无头应无权，加上后真钥出供给
6. 供给查询过签后别停在名单：打下单前校验（check），回真卖价/结算价再 booking。对照假钥签名失败。下出订单号立刻取消；改不回停在回包，禁止批量真下
7. GitHub/SDK 公开演示 RSA+3DES：生产 XML pay-gate 仍认时，现签 `POST /service/query` 解开返回密文。对照假钥验签失败。邻号共用同一把演示 RSA 时回业务错（订单号有误）不是验签失败，钥仍活。禁止真下单/退款
8. 开放文档对象存储超长预签名 SDK zip：解开 `prod/config.properties`（及国密配置）+ pfx，用配置密码开证书，抄商户号/signKey 打**生产查单**。对照假钥 SIGN_ERROR。只查单，禁止真转账
9. 游戏 MSDK：wiki encode=2 时 `sig=md5(msdkKey+timestamp)`（不绑 path/body、无时间窗）现签生产/测试 `/auth/*`。对照假签 `sig error`；真签过闸转到身份供应商 `access_token expired` / 手Q `0x711` 一类业务错也算钥活，别当没洞。V3 `/auth/guest_register`：`reqid` 明文 uuid 会 `decrypt faild`，用 msdkKey **前 16 个 ASCII** 做 QQ TEA（16 轮大端 `oi_symmetry_encrypt2`）再 hex；开出 guestid 再打 `/auth/guest_check_token`。没有玩家有效社交 token 就停，禁止为进号磨登录
10. 官方接入 HTML 示例 `MSDKConfig.json` 明文 `MSDK_SDK_KEY`：`source=0` 时 `sig=md5(path+"?"+除 sig 外字典序 query+body+钥)`；decrypt 用 `md5(ts+密文+钥)`（文档示例 ts/密文/签能对上再拿到生产打）。对照假签 `invalid sig`；真签过闸后打游客登录，`channel_info` 只放自编 uuid 仍签发 openid/token/jwt 就算用户票。禁止为进别人号磨渠道 code
11. npm 历史包写死 `developerId`+`signKey`：合作中心网关假签活号回「签名错误」、死号回「开发者数据异常」，可枚举活号。真签 `sign=SHA1(signKey+按 key 排序的 key+value)`。隐私号批量拉取口不带门店 `appAuthToken` 也能 `OP_SUCCESS`；换票口真签过闸转到「入驻状态不正确」也算钥活。空数组不是假点（当前没降级单）。**别停**：同套更高版本 npm 把 `appAuthToken` 写死别当联调丢掉，带令牌现签 `queryPoiInfo`，换 `ePoiId` 出他商户店名+11 位手机。禁止真下单/磨授权码
12. 充值/企业支付 Demo HTML（`enterprise_client` 一类）输入框写死 AppId+AppKey：别当联调占位。不登录抄出来，HMAC-SHA1 源串 `GET&urlencode(path)&urlencode(按 key 排序的 kv)`，密钥 `AppKey+'&'`，Base64 得 sig。对照假签 `sig error`。真签打生产 `/v1/r/{appid}/open_order` 出 `token_id`。只下未支付单，禁止走收银台付款/退款。实值只进报告
13. 登录页 JS 把钉钉 ISV `suiteKey`+`suiteSecret` 写成 `clientId`/`clientSecret`（值 `suited` 开头）：别当 OAuth 占位。不登录 POST `https://oapi.dingtalk.com/service/get_suite_token`，`suite_ticket` 填假值。对照假 secret 回「不合法的套件key或secret」。真钥出 `suite_access_token`。实值只进报告
14. 控制台 webpack/Vuex 默认地图 key 别当占位。假钥对照后不要只打逆地理：打地点云/图层 `table/list`，有表再 `data/list`。只逆地理通、表是空的 → 假点。实值只进报告
15. 官方文档/接入 HTML 示例 curl 写死 Gamekey：别当占位。不登录抄 AppID+Gamekey，`sign=md5(mod,func,appid,time,postdata,key)` 现签生产排队网关 `getZoneListCount`。对照假钥 `req sign error`。真签 `ret=0` 出区服在线。只查排队/在线，禁止往队列插人、禁止把人退出排队。实值只进报告

算成：钥是活的，能换成该应用的用户票，或业务查询出该应用下的供给名单，或给该应用绑上 WASM 分包版本，或 booking 下出该应用订单号，或解开**他商户**未公开支付订单持卡人；或假签验签失败、真签过生产闸转到下游身份供应商业务错（证明生产仍认这把完整钥）；或生产 `open_order` 出未支付 `token_id`；或钉钉 `get_suite_token` 出 `suite_access_token`；或生产排队 `getZoneListCount` `ret=0` 出区服在线。

假点：文档是占位符；真假密钥同一句错；钥过期调不通；联调钥只能打测试环境、生产拒；wiki 打码就当 zip/Demo 也打码。密钥实值不进库。单站没中不删战法索引这行。

### 门户 CMS 写死站点钥（战法索引有指针）

认：门户/开放平台前端（不是调试文档 zip）写死 门户 CMS 的 `accessKey`+`secretKey`。有 `GET /api/v1/cms/login`，回 JWT，头名常见 `cms-token`。首页可能只是 CMS 欢迎页，钥在另一个门户 JS 里。

打（不登录）：

1. 抄 AK/SK 打 login（实值只进报告）
2. 带票打 `channel/list`、`content/list|detail|search`、`attachment/list`
3. 不要停在官网轮播频道。跟开发者/测试/后台频道，GET `attachments.url`

算成：内部测试报告/未对公开展示频道的稿件正文（xlsx 表字段也算）。

假点：只有公开运营 Banner/客户端下载地址。密钥实值不进库。单站没中不删战法索引这行。

### 发签 nonce 是私钥（战法索引有指针）

认：企业 IM/业务 **unlogin** 发签口（`queryAppSignature` / `queryCorpSignature` 一类）。其它业务口请登录，这条不要 Cookie。回包 `nonceStr`/`nonce` 以 `MIIE` 或 `-----BEGIN` 开头，能当 PKCS8 私钥 load。常见前面还有未登录渠道/活码口漏 `corpId`。

打（不登录）：

1. 未登录渠道/活码漏 `corpId` 就抄  
2. POST 发签口带 url + corpId  
3. 把 `nonceStr` 当私钥 load（Python `load_der_private_key` / openssl）。对照：假 corpId 应业务错、没有 PEM  

算成：能 load 成 RSA 私钥。

假点：nonce 只是短随机串；假 corpId 一直业务错。密钥实值不进库。单站没中不删战法索引这行。

### 未登录发 IM/体验票（战法索引有指针）

认：未登录 `im/getConfig` 下发 TIM `userSig` 且 `identifier=null`；或云产品体验中心/apaas 发签口按请求里的**已有 userId** 发票（对照游客 `none_auth` 会新开号）；或同一后台其它业务口请登录，发签口只要自定义 trace 头 + 客户端传入的 userId 就发 IM/RTC userSig；或自建 IM 网关发签口只吃 appkey，票里没 userId，接入口 body 的 uId 才是身份；或 JS 写的 v2 inner 发签被 IP 白名单；或官方音视频/IM Web Demo 前端写死发签口和固定 pwd，identifier 跟请求走，空密也给已有用户发票。

