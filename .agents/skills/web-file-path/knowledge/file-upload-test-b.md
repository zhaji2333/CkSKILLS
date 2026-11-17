# 文件上传漏洞测试手册（续）

> 接 [`file-upload-test.md`](file-upload-test.md) 的后半段（原块 >12KB 拆分）。

### 桶策略对匿名全开（战法索引有指针）

认：官网/控制台的图、使用指南、协议直接挂在 OSS / cloudrun 一类桶域名上；桶根或 `?policy` / GetBucketPolicy / 等价策略接口能拉开，语句是全 Allow。

打：

1. 策略能看就看；再对桶做 LIST（无 AK）  
2. 对官方引用对象所在**同前缀** PUT 自己的探测文件（新 key，如 `covers/zc-probe.txt`）；**不覆盖官方已有对象**，不要去改桶策略本身  
3. 同一探测 key PUT 两次、正文换一串标记，GET 对照验收  

算成：匿名 PUT 进官方引用的同前缀并 GET 回自己的探测文件（任意 key 匿名写权已证，官方对象不用真盖）。只证明匿名能 LIST、或官方前缀 PUT 403 → 假点。

假点：策略只读不能写；PUT 只能落自己前缀；下到的本来就是公开静态页。单站没中不删战法索引这行。

和 STS `*`（要先申请凭证、key 打成通配）、和 filename `../` 穿越租户目录、和 Azure 容器级 SAS 都不是一条：本条是 **桶策略对匿名放开，不用凭证**。

### 存储代理 sign key=/（战法索引有指针）

认：业务网关把对象存储代理成 `/api/storage/sign`（或同类 sign），query 只吃 `key`。`key=/` 或 `key=.` 回 S3 `ListBucketResult` XML，不是申请 STS。

打（不登录）：

1. GET `?key=/`（再试 `.`）。对照乱填 key 应 `NoSuchKey` / 400  
2. 列表里抄业务前缀（`images/` `editor-` 一类）再 GET 同一口  
3. 看对象是不是未公开素材，不要停在官网 Banner  

算成：列出并读到他人未公开对象原文。

假点：只有 app-static 公开静态；`filename=` 400 当没口。单站没中不删战法索引这行。和 STS 通配（先领钥）、桶策略匿名全开（直打桶域）不是一条：本条是 **业务网关自己当 List/Get 代理**。


### 制品下载详情把 uin 有无当登录闸（战法索引有指针）

认：软件/专有云/物料下载中心；详情 JSON 有 `DownloadURL`；前端从 Cookie 抄 `uin`/`skey` 拼 query。空身份时 URL 是空串、页面跳登录。

打：不登录 GET 详情，身份字段填非空假值（`uin=1`），不要 skey。对照空 uin。拿回的带签 URL Range GET 前几十字节看 ELF/PK。

算成：专有云安装包/内部部署文档真文件。空 uin 也出 URL → 完全无鉴权（另一条）。带签 403 / 只有公开说明书 → 没成。

### 入驻 JS 写死 fileKey（战法索引有指针）

认：入驻/资质 SPA 打包 JS 的 mock 或演示 formData 写死一长串密文 `fileKey`。站点根 301 到新域，**旧 host 下载口可能还活**。不要把 mock 当占位丢掉，也不要把 301 当整站废。

打（不登录）：

1. 跟新域 chunk 抄 `fileKey`  
2. 打旧 host `/json/view/file/downloadFile?fileKey=`（或同类）  
3. 对照：乱填 fileKey 应空/错，真 key 出图  

算成：私有桶执照/证件原图真下到。

假点：把 301 新域名当整站废；mock fileKey 当下占位且乱填也出同一张图。单站没中不删战法索引这行。密钥实值、完整 JS 不进本篇。

### 分享鉴权 false 仍下媒体（战法索引有指针）

认：云录制分享；鉴权接口有 `download_enable`/`view_minutes_enable`。或会议 JSON 网关根本没有 `permission/auth`（404 别停）。

打（不登录）：

1. `download-multi-record-file` **和** `sign-multi-record-file` 都打（要 `auth_share_id`+`resource_type`）。国际 JSON 网关缺 `sharing_id` 只回 `2710500 参数非法`，`auth_share_id` 和 `sharing_id` 一起带才签发 MP4；缺了会当没洞。**POST JSON 报「录制 id 不能为空」别停，改 GET query 把 record_id / auth_share_id 放进 URL。**  
2. 没有鉴权口不要当成没入口：直接打 `public/record-detail/download-multi-record-file`。  
3. 纪要/时间线 `get-full-summary` / `query-timeline` 只填 `record_id` 也试，不要默认必须带 share。  
4. COS 无 Referer 的 403 **不是终点**：带分享页 Referer 再 GET。  
5. `permission/get-cfg` 看会不会吐同会其它 record。  
6. 只拿到 url 没 GET 到 MP4 算半条，继续跟。  

算成：鉴权写 false 仍拉到真 MP4（ftypisom+体积）；或只要 record_id 出纪要全文（不是标题）。

假点：鉴权真拦了、下不到文件；只有公开说明书；纪要只要标题没有正文。单站没中不删战法索引这行。

### 密码分享回包带明文提取码（战法索引有指针）

认：分享详情 JSON 一边 `need_pwd` / `auth_level`（或同类）表示要提取码，一边 auth 对象把明文提取码放进 `pass_word`（或同类）。或落地 HTML / `syncData` 内联同一明文码。

打（不登录）：

1. 先空着提取码打查看口。对照：文件列表应空，闸字段应是要码。  
2. 同一份回包里抄明文码，填回查看口。对照：空密时列表空、填了才出 `file_id`。  
3. **落地 HTML / `syncData` 里已经有明文 `pass_word` 就直接抄**，不必先打 View CGI。  
4. 拿 `file_id` 和这份码打下载口，跟到真文件头（PDF/ZIP 一类正文），不要停在 JSON 有码。

算成：拿到提取码并下到密码分享正文，不是空密直接出文件列表。

假点：`pass_word` 是哈希抄了登不进；空密 View 已经出文件（那是无提取码分享，不是这枪）。单站没中不删战法索引这行。
密钥实值、完整 JS 不进本篇。


