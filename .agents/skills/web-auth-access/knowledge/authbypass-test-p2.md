# authbypass-test · part 2

> 分段 2/2。索引见 `authbypass-test.md`。

## 承接

3. 带会话打合同列表 / 支付进件 / 身份口。对照：不带 Cookie 应未登录；不存在的合作方 id 应查空  

算成：身份口登录成功，或能当这个号读未公开合同。

假点：签发口要已登录；code 必须从邮件点开；setCookies 不下会话；只出公开招商页。单站没中不删战法索引这行。密钥实值、某次 Cookie 不进库。

### 未登录合作方直连配置查询（战法索引有指针）

认：运营台 / 供应链前端把供应商直连配置查询挂成未登录。body 只有可枚举合作方数字 id（partnerId 一类），不要 Cookie。回包 `partnerInfos`（或同类）里带 clientId+clientSecret。

打（不登录）：

1. 运营台 JS 抄查询口（getV2 / tech/partner 一类）
2. partnerId 用邻号。对照：未配置的 id 应回查空/未配置，不是登录闸
3. 算出是完整 clientSecret，不是空成功码

算成：回包里是完整 clientId+clientSecret，能当这把直连钥用。

假点：接口已下线；clientSecret 空或占位；必须登录；只出公司名没有钥。单站没中不删战法索引这行。密钥实值不进库。

### 未登录签发回跳外域（战法索引有指针）

认：未登录签发 SSO / 回跳；callback 只判断字符串里有没有官方 host，或不校验、任意外域也能签。

打（不登录）：callback/redirect 填外域：夹官方 host（query/子域/userinfo）和**不夹**都试。回包有票/签再交给自家 SSO。通行证页看会不会 `location.replace(回跳+"?"+token名+"="+session)`。对照：不含官方字应被改空或拦。必须真机登录才出票且前端不会把 token 拼进回跳 → 半条，停在签单，不算打穿。

算成：SSO 成功且回跳仍是外域；或登完通行证出现在外域 query。

假点：callback 被改空；SSO 缺回调参数。单站没中不删战法索引这行。

### 缺参字段改头换票（战法索引有指针）

认：未登录业务口 JSON 报「缺少 xxx」；query/body 带了仍报缺少。或 Spring 400 HTML/`message` 写 `Required String parameter 'os' is not present` 一类，点名的是 **Cookie 名** 不是 query。

打：把这个字段放到 **HTTP 头**再打 SSO/换票/login。头没吃别停，改打 Cookie（设备 `uuid`/`os`/`platform` 一类自己编）。未登录写口（绑店/改状态）同样试，不要只打换票。对照：只放 query 应仍报缺少。

算成：出别人的登录票/姓名；或写上他人门店/对象。

假点：query 有该字段仍报缺少（头和 Cookie 都没吃）不算过；只出自己的票。单站没中不删战法索引这行。

### SSO 壳后面的账密登录口（战法索引有指针）

认：管理后台人打开只跳 SSO / 统一认证，页面没有账密框；后端仍暴露账密登录 API。别把 SSO 壳当成整摊没登录口。常见后台骨架 `/admin-api/system/auth/login` 是常见皮，没有这名仍打。

打（不登录）：

1. POST `/admin-api/system/auth/login`，body `{"username":"admin","password":"123456"}`（不要去磨 SSO 验证码）
2. 把 `data.accessToken` 放到 `Authorization: Bearer` 打 `/admin-api/system/tenant/page` 或 `/system/user/page`
3. 对照：错密应失败；默认口出 `userId=1` 一类平台票

算成：进了平台管理员号，且租户/用户列表出他人手机/姓名。

假点：登录口 404 或默认口已改；票只能进空租户没有联系人。密钥实值、某次 Token 不进库。单站没中不删战法索引这行。

### 刷新票空包发管理员票（战法索引有指针）

认：JSON 网关有刷新票口（`/api/auth/refresh` 一类）。不登录、空包 `{}` 就发票，票里身份是 `admin`（不是游客）。管理后台和前台走同一套云开发/网关。

打（不登录）：POST 刷新口；把 `data.token` 放到 `Authorization: Bearer` 打 `/api/admin/me/permissions` 和申请/用户名单。对照：不带这张票应未登录。

算成：me 是超级管理员（权限 `*`），或名单出现**他人**手机/姓名。

假点：只出游客/过期票；refresh 必须带旧 refresh token；me 仍是自己。密钥实值不进库。单站没中不删战法索引这行。

### 空 openId 进已有号（战法索引有指针）

认：小程序 / H5 的 GET 登录口吃 `openId`（`loginByOpenId` 一类）。缺参报缺字段，假 openId 登录失败，空串仍 200 出**已有商家号**和手机，不是游客空号。

打（不登录）：

1. 缺参一枪，确认这是登录口  
2. 假值一枪，应失败  
3. `openId=` 空串再打；GET query 没吃再试 POST JSON `{"openId":""}`  
4. 对照：空串出的店名/登录手机，和假值失败、缺参报缺，不是同一套游客号  

算成：进已有商家号且出手机（能当这个号用）。

假点：空串只出游客空号。密钥实值、某次 Cookie 不进库。单站没中不删战法索引这行。


