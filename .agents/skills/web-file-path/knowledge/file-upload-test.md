> 来源：实战知识库（真实 SRC 战法沉淀，已并入 CkSKILLS_v2）。
> 与 `rules/` 冲突时以 rules 为准；CORS 按 `../../../../rules/20-min-harm.md` 与团队取舍不主动挖。

> 写不写只认 `../../../../rules/40-evidence-report.md`。本篇是测法：别停在能传能下，跟可执行/路径/SSRF/跨用户业务对象。
> 战法索引指针用标题搜。PHP 马 / GIFAR / ImageTragick / 英文附件已砍；没对象存储不要空打跨桶。

# 文件上传漏洞测试手册

## 测试流程（开场）

找上传点（头像/附件/导入/富文本）→ 先传正常文件看路径、是否重命名、落 CDN/OSS 还是本机、能不能直接打开。别停在能传能下：跟覆盖他人对象、带签读、可执行/路径/SSRF。后缀/Content-Type/解析绕过现场按栈自己变。

### STS / 对象 key 通配覆盖（战法索引有指针）

认：对象存储（BOS/OSS/S3/TOS 一类）上传先申请 STS/预签名；对象 key 常是文件 md5；桶名按日期或批次递增。或 assumerole 一类领钥匙口，请求里的 `filename` / `Action` 会被拿去拼 Policy。下面 xluser / AES / `1.jpg` 是常见皮，**没有这字仍打通配**。

打：

1. 申请凭证的 `identifier` / `key` / `object` / `prefix` / `filename` **长度不校验**时，试 `*`、`**`，再试**置空**和 `/`（有的实现空前缀 = 整桶）  
2. 一个 `*` 可能落到空桶；**两个以上**可能命中当前业务桶，凭证 `key` 变成通配当前桶  
3. path / `actionName` / 拼进 Policy 的路径参试 `../../../`、`../../../&/../../`，看签出来的范围是不是扩到根  
4. 别人文件的对象 key 往往是 md5：打开文档页，在 JS/接口里搜 `md5sum` / `md5`，不用下载、不用付费  
5. 用刚领到的 STS：先 GET 对方那个 md5 下原文（跨用户读）；写权只打自己刚传的探测 key 或对方同前缀下的新 key，正文换一串标记 GET 对照。**不要把对方已有 md5 当覆盖目标**  
6. assumerole 另打一枪：`filename=*-*`（或 `*`）、`Action=*`。有的实现是**后段 Policy 盖前段**，钥匙变成整桶。通了先 `list_objects`（列出他人 key 已证可见；**删/盖只打自己刚传的探测 key**，列出来的真实对象不碰）。**List/Delete 403 别停**：对任意 key GET/PUT。领钥 XHR 不带登录头也打。**sibling drive 匿名票 `illegal user id` 不等于本网关也拒**：匿名 xluser 票过闸的 STS 口照打。query `upload_dir`/`dir` 原样进 OSS Policy 时填 `*`。页面走 CDN 时，强制刷新或等缓存过完再验收  
7. PUT 时头里试 `x-cos-acl: public-read`、`x-cos-grant-full-control: id="你的UIN"`（OSS/S3 对等头一样）。**对象真变成公有读、或控制权到你的 UIN** 才算；只 200 不算接管
8. 没有「文件已存在」预言时仍猜短原文件名（`1.jpg`/`2.png`/`5.jpg`）匿名 GET CDN。token 口若前端写死 AES/盐，未登录自己算 sign，`filename=*` 常直接下发 appId+bucket，CDN 前缀拼出来就能下**他人证件照**  
9. **落地页写死 supabase / nocode `role=anon` JWT 时，rest 表 CRUD 不是终点。** 带 `apikey` + `Authorization: Bearer` 打 `POST /storage/v1/object/{桶}/{官方前缀/探测key}`。官方封面/案例图常在 `use-cases/`、`covers/` 一类前缀。第一次 POST 自己的探测文件；同一对象名再 POST，头加 `x-upsert: true`，正文改成另一串标记。公开 `GET /storage/v1/object/public/{桶}/{key}` 对照两次正文。**不要真盖官方运营图**，同前缀能盖自己刚传的 = 官方同前缀同样能盖。打完 DELETE 探测文件。rest `/rest/v1/` 403 别停，存储 REST 常另开。

算成：再打开/下载**对方那篇/那张图**（跨用户读）；或 list 出别人的 key 且同一把钥对自己刚传的探测 key 可删/盖；或官方前缀上 `x-upsert` 把探测文件盖成第二串标记（同前缀官方对象同一把钥）。只证明自己能传到自己的 key → 假点。

假点：`*` 只签发废桶；对探测 key 再盖 403；钥匙只通自己前缀没通配；策略服务端写死盖不掉；CDN 一直不刷新看起来没盖上。单站没中不删战法索引这行。

和 S3 预签名「改自己的 Content-Type」、和「带签 URL 改租户读他文件」、和下面「桶策略对匿名全开」「签名没绑 Host」「签名覆盖 Content-Type」都不是一条：本条是 **凭证范围被通配成整桶，覆盖或清掉他人对象**。

### 签名没绑 Host（战法索引有指针）

认：COS / OSS / S3 带签 URL；query 里 `q-header-list`、`SignedHeaders`、`X-Amz-SignedHeaders` **没有 host**。有对象存储带签才打，没有不要空换域名。

打：

1. 看签名参数里签了哪些头。没有 `host` 再往下。  
2. 把 URL 的主机换成**同账号另一个桶**的域名（证书 SAN、报错、控制台、JS 里抄），path 和签名 query 先不动。  
3. 再加 `?uploads`（或已有 query 后 `&uploads`）打 ListMultipartUploads；能 GET 对象也打。

算成：列出或读到**别的桶**里的对象。只换域还是自己这个桶 → 没成。

假点：签名罩住 Host；换域 403；只有自己这个桶。单站没中不删战法索引这行。

和 STS `*`（钥匙范围被通配）、和带签 URL 只改租户字段 **不是一条**：本条是 **Host 没进签名，同一把签能打到别的桶**。

### 签名覆盖 Content-Type（战法索引有指针）

认：对象内容你能控（自己传的或 STS 能盖的）；对象上的 Content-Type 被卡死（image/jpeg 一类）；手里有临时钥或能再出预签名。

打：

1. 上传时改 CT 那一枪还打（`text/HtMl`、`text/html,image/png`）。那是「签的时候没把 CT 签进去」。  
2. **事后再签**：用临时钥给**已有对象**出一枪带 `response-content-type=text/html`（COS/OSS 支持签名覆盖响应头）的 GET。  
3. 用这把新签 URL 在浏览器打开，不要只看 curl 的 Content-Type。

算成：浏览器当 HTML 执行（存储 XSS）。下载仍是附件/原 CT → 没成。

假点：签名接口拒这个参；只能改自己不可达的对象；`X-Content-Type-Options: nosniff` 且 CT 仍是图。单站没中不删战法索引这行。没对象存储、没临时钥不要空签。

和「上传 PUT 时改 Content-Type」不是一条：那条改的是**写入时**的类型；本条是 **读的时候用签名把响应头盖成 HTML**。

### webpack 明文对象存储永久钥（战法索引有指针）

认：管理台 / 运营后台 webpack 把生产 `accessKeyId`+`secretAccessKey`（MSS / S3 一类永久钥）打进 JS。或 Weblogic `/console/login/LoginForm.jsp` 内联 `_reportCfg` 一类的 `SRV_` 钥。上传签 `getUploadSign` 是前端 HMAC-SHA1 算 policy，不是走登录后的 STS 口。policy 里 `starts-with $key` 经常是空串。

打（不登录）：

1. 抄 online/prod 的 AK/SK（实值只进报告）  
2. 自己算 POST policy，expiration 拉长，`starts-with $key` 按 JS 原样（空就空）  
3. POST 桶：对照假签 `SignatureDoesNotMatch`、无签 `conditions has no signature`  
4. 任意 key PUT 后 CDN GET；DELETE 自己刚传的证明钥能写。官方已引用对象**不盖**：对自己的探测 key 可 PUT/DELETE 已证任意 key 写权  
5. List/PUT 403 别停：先 `GetBucketLocation`。对照假 AK `InvalidAccessKeyId`。页面桶名拼错（staic/static）试邻近  

算成：完整永久云钥能签（真签 PUT 200 或 GetBucketLocation 出地域），且对自己刚传的探测 key 可盖/删。

假点：InvalidAccessKeyId；只能传到固定前缀；getUploadSign 其实是 SSO 接口没有本地钥；钥过期。密钥实值不进库。单站没中不删战法索引这行。

和 STS 通配（先申请临时票）、和桶策略对匿名全开（不用钥）、和 viewer XOR 藏 COS 永久钥（要解开再问 AccountId）都不是一条：本条是 **webpack 明文永久钥 + 前端自己算签**。

> 本块超过 12KB，已拆分：后半部分见 [`file-upload-test-b.md`](file-upload-test-b.md)（从「桶策略对匿名全开（战法索引有指针）」起），按需只读该分段。
