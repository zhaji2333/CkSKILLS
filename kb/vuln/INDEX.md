# 漏洞库索引（自动生成，勿手改）

> 生成：`python3 tools/kb_index.py`；数据目录：`kb/`。
> **用法**：先在本表按 ID / 产品 / 标题关键词定位，再只打开命中的单条 `kb/vuln/<相对路径>`；**禁止通读** `kb/vuln/`。
> **证据纪律**：CVE 编号 / 影响版本 / 修复版本以厂商公告或 NVD 为准；条目里的 PoC 必须本地复现后才可写进报告，未复现只能标「疑似/待验证」（详见 `kb/README.md`）。

## 分类计数

| 分类 | 条目数 | CRITICAL | HIGH | MEDIUM | 其它 | 索引 |
| --- | --- | --- | --- | --- | --- | --- |
| ai | 24 | 15 | 8 | 1 | 0 | 本页 |
| cloud | 5 | 0 | 4 | 1 | 0 | 本页 |
| middleware | 436 | 292 | 97 | 47 | 0 | [INDEX-middleware.md](INDEX-middleware.md) |
| network | 20 | 16 | 3 | 1 | 0 | 本页 |
| web | 179 | 111 | 57 | 11 | 0 | 本页 |
| **合计** | **664** | 434 | 169 | 61 | 0 | - |

## ai（24 条）

| ID | severity | product | 标题 | 相对路径 |
| --- | --- | --- | --- | --- |
| ANYTHINGLLM-RCE | CRITICAL | anythingllm | AnythingLLM 多个远程代码执行漏洞 | ai/anythingllm/ANYTHINGLLM-RCE.md |
| BROWSER-USE-PICKLE-RCE | CRITICAL | browser-use | browser-use WebUI Pickle 反序列化远程代码执行漏洞 | ai/browser-use/BROWSER-USE-PICKLE-RCE.md |
| CVE-2025-67303 | CRITICAL | comfyui | ComfyUI-Manager - 配置文件未授权读写导致RCE | ai/comfyui/CVE-2025-67303.md |
| CVE-2026-22777 | HIGH | comfyui | ComfyUI-Manager - CRLF注入降级安全级别导致RCE | ai/comfyui/CVE-2026-22777.md |
| CVE-2025-56520 | MEDIUM | dify | Dify - SSRF via RemoteFileUploadApi | ai/dify/CVE-2025-56520.md |
| DIFY-RSC-DESER-RCE | CRITICAL | dify | Dify 控制台 React Server Components 反序列化 RCE（CVE-2025-55182） | ai/dify/DIFY-RSC-DESER-RCE.md |
| DIFY-SSRF-RCE | CRITICAL | dify | Dify SSRF + 沙箱逃逸远程代码执行漏洞 | ai/dify/DIFY-SSRF-RCE.md |
| FLOWISE-AUTH-BYPASS-RCE | CRITICAL | flowise | Flowise 认证绕过与远程代码执行漏洞 | ai/flowise/FLOWISE-AUTH-BYPASS-RCE.md |
| CVE-2025-25295 | HIGH | label-studio | Label Studio SDK 路径遍历任意文件读取漏洞 | ai/label-studio/CVE-2025-25295.md |
| CVE-2025-3248 | CRITICAL | langflow | Langflow validate/code API 未授权RCE漏洞 (CVE-2025-3248) | ai/langflow/CVE-2025-3248.md |
| CVE-2025-68477 | HIGH | langflow | Langflow API Request 组件服务端请求伪造漏洞 | ai/langflow/CVE-2025-68477.md |
| CVE-2026-27966 | CRITICAL | langflow | Langflow CSV Agent 远程代码执行漏洞 | ai/langflow/CVE-2026-27966.md |
| LANGFLOW-UNAUTH-RCE | CRITICAL | langflow | Langflow 未授权远程代码执行与任意文件写入 | ai/langflow/LANGFLOW-UNAUTH-RCE.md |
| LOCALAI-RCE | CRITICAL | localai | LocalAI 模型加载远程代码执行漏洞 | ai/localai/LOCALAI-RCE.md |
| CVE-2024-39719 | HIGH | ollama | Ollama api/create 文件存在性泄露漏洞 | ai/ollama/CVE-2024-39719.md |
| CVE-2024-39722 | HIGH | ollama | Ollama api/push 路径遍历信息泄露漏洞 | ai/ollama/CVE-2024-39722.md |
| CVE-2024-45436 | CRITICAL | ollama | Ollama extractFromZipFile 目录穿越远程代码执行漏洞 | ai/ollama/CVE-2024-45436.md |
| OLLAMA-UNACC-RCE | CRITICAL | ollama | Ollama API 未授权访问导致模型窃取与命令执行 | ai/ollama/OLLAMA-UNACC-RCE.md |
| CVE-2026-22812 | CRITICAL | opencode | OpenCode HTTP 服务未授权远程代码执行漏洞 | ai/opencode/CVE-2026-22812.md |
| OPENWEBUI-SSRF | HIGH | openwebui | Open WebUI 路径穿越与认证绕过漏洞 | ai/openwebui/OPENWEBUI-SSRF.md |
| QDRANT-UNACC | HIGH | qdrant | Qdrant 向量数据库未授权访问漏洞 | ai/qdrant/QDRANT-UNACC.md |
| RAGFLOW-RCE-AND-ACCOUNT-TAKEOVER | CRITICAL | ragflow | RAGFlow 远程代码执行与账户接管漏洞 | ai/ragflow/RAGFLOW-RCE-AND-ACCOUNT-TAKEOVER.md |
| TGWUI-UNACC-RCE | CRITICAL | text-generation-webui | text-generation-webui 未授权访问与代码执行漏洞 | ai/text-generation-webui/TGWUI-UNACC-RCE.md |
| VLLM-UNACC | HIGH | vllm | vLLM API 未授权访问漏洞 | ai/vllm/VLLM-UNACC.md |

## cloud（5 条）

| ID | severity | product | 标题 | 相对路径 |
| --- | --- | --- | --- | --- |
| APIGW-CONTENT-TYPE-BYPASS | HIGH | aws-apigateway | API Gateway 请求验证绕过 — Content-Type 欺骗 | cloud/aws-apigateway/APIGW-CONTENT-TYPE-BYPASS.md |
| LAMBDA-PRINCIPAL-STAR | HIGH | aws-lambda | Lambda 资源策略 Principal:* 未授权调用 | cloud/aws-lambda/LAMBDA-PRINCIPAL-STAR.md |
| S3-ACCOUNT-ID-ENUM | MEDIUM | aws-s3 | S3 Bucket Account ID 侧信道枚举 (s3:ResourceAccount) | cloud/aws-s3/S3-ACCOUNT-ID-ENUM.md |
| S3-PATH-TRAVERSAL-OSPATH | HIGH | aws-s3 | S3 路径穿越 — Python os.path.join 绝对路径绕过 | cloud/aws-s3/S3-PATH-TRAVERSAL-OSPATH.md |
| SNS-SUBSCRIBE-PROTOCOL-BYPASS | HIGH | aws-sns | SNS 订阅条件绕过 — HTTPS 协议 Endpoint 构造 | cloud/aws-sns/SNS-SUBSCRIBE-PROTOCOL-BYPASS.md |

## middleware（436 条）

> 条目过多（> 200 行），独立成表：**[INDEX-middleware.md](INDEX-middleware.md)**

## network（20 条）

| ID | severity | product | 标题 | 相对路径 |
| --- | --- | --- | --- | --- |
| ANHENG-GATEWAY-RCE | CRITICAL | anheng | 安恒明御安全网关 aaa_portal_auth_local_submit 远程命令执行漏洞 | network/anheng/ANHENG-GATEWAY-RCE.md |
| CVE-2020-3331 | CRITICAL | cisco | Cisco RV110W/RV215W 缓冲区溢出远程代码执行（CVE-2020-3331） | network/cisco/CVE-2020-3331.md |
| CVE-2020-3452 | HIGH | cisco | Cisco ASA/FTD 任意文件读取漏洞 | network/cisco/CVE-2020-3452.md |
| CVE-2021-1497 | CRITICAL | cisco | Cisco HyperFlex HX 远程命令执行漏洞 | network/cisco/CVE-2021-1497.md |
| CVE-2019-19781 | CRITICAL | citrix | Citrix ADC/NetScaler Gateway 远程代码执行漏洞 | network/citrix/CVE-2019-19781.md |
| CVE-2023-4966 | CRITICAL | citrix | Citrix NetScaler ADC/Gateway 信息泄露漏洞（Citrix Bleed） | network/citrix/CVE-2023-4966.md |
| DAHUA-SMART-PARK-UPLOAD | CRITICAL | dahua | 大华智慧园区综合管理平台 user_save.action 未授权用户创建及文件上传漏洞 | network/dahua/DAHUA-SMART-PARK-UPLOAD.md |
| DNS-DNS-ZONE-TRANSFER | MEDIUM | dns | DNS 域传送漏洞 | network/dns/DNS-DNS-ZONE-TRANSFER.md |
| CVE-2022-40684 | CRITICAL | fortinet | Fortinet FortiOS 认证绕过远程命令执行漏洞 | network/fortinet/CVE-2022-40684.md |
| H3C-SECPATH-LOGIN | CRITICAL | h3c | H3C SecPath 堡垒机 任意用户登录漏洞 | network/h3c/H3C-SECPATH-LOGIN.md |
| H3C-SECPATH-RCE | CRITICAL | h3c | H3C SecPath 堡垒机 data_provider.php 远程命令执行漏洞 | network/h3c/H3C-SECPATH-RCE.md |
| CVE-2021-36260 | CRITICAL | hikvision | 海康威视摄像头命令注入漏洞 | network/hikvision/CVE-2021-36260.md |
| CVE-2017-17215 | CRITICAL | huawei | 华为 HG532 远程命令执行（CVE-2017-17215） | network/huawei/CVE-2017-17215.md |
| NSFOCUS-SAS-LOGIN | CRITICAL | nsfocus | 绿盟 SAS 堡垒机 任意用户登录漏洞 | network/nsfocus/NSFOCUS-SAS-LOGIN.md |
| NSFOCUS-SAS-RCE | CRITICAL | nsfocus | 绿盟 SAS 堡垒机 Exec 远程命令执行漏洞 | network/nsfocus/NSFOCUS-SAS-RCE.md |
| CVE-2021-28073 | HIGH | ntopng | ntopng权限绕过漏洞（CVE-2021-28073） | network/ntopng/CVE-2021-28073.md |
| RUIJIE-EG-FILE-READ | HIGH | ruijie | 锐捷 EG 易网关 download.php 任意文件读取漏洞 | network/ruijie/RUIJIE-EG-FILE-READ.md |
| RUIJIE-EG-RCE | CRITICAL | ruijie | 锐捷 EG 易网关 cli.php 远程命令执行漏洞 | network/ruijie/RUIJIE-EG-RCE.md |
| SANGFOR-NGAF-RCE | CRITICAL | sangfor-ngaf | 深信服 NGAF 下一代防火墙 login.cgi 远程命令执行漏洞 | network/sangfor-ngaf/SANGFOR-NGAF-RCE.md |
| CVE-2019-12725 | CRITICAL | zeroshell | ZeroShell 3.9.0 远程命令执行漏洞 | network/zeroshell/CVE-2019-12725.md |

## web（179 条）

| ID | severity | product | 标题 | 相对路径 |
| --- | --- | --- | --- | --- |
| 1PANEL-FILE-READ | HIGH | 1panel | 1Panel - 任意文件读取（路径遍历） | web/1panel/1PANEL-FILE-READ.md |
| CVE-2024-39907 | HIGH | 1panel | 1Panel - 后台 orderBy SQL 注入任意文件写入 | web/1panel/CVE-2024-39907.md |
| CVE-2024-39911 | CRITICAL | 1panel | 1Panel - 前台 User-Agent SQL 注入写 Webshell | web/1panel/CVE-2024-39911.md |
| CVE-2025-54424 | CRITICAL | 1panel | 1Panel - 客户端证书绕过 WebSocket 终端 RCE | web/1panel/CVE-2025-54424.md |
| CVE-2021-21311 | HIGH | adminer | Adminer ElasticSearch/ClickHouse SSRF漏洞 (CVE-2021-21311) | web/adminer/CVE-2021-21311.md |
| CVE-2021-43008 | HIGH | adminer | Adminer 远程文件读取漏洞 (CVE-2021-43008) | web/adminer/CVE-2021-43008.md |
| CNVD-2024-15077 | CRITICAL | aj-report | AJ-Report 认证绕过与远程代码执行漏洞 (CNVD-2024-15077) | web/aj-report/CNVD-2024-15077.md |
| CVE-2024-28752 | HIGH | apache-cxf | Apache CXF Aegis DataBinding SSRF漏洞 (CVE-2024-28752) | web/apache-cxf/CVE-2024-28752.md |
| CVE-2021-25646 | CRITICAL | apache-druid | Apache Druid 任意JavaScript代码执行漏洞 (CVE-2021-25646) | web/apache-druid/CVE-2021-25646.md |
| CVE-2021-36749 | HIGH | apache-druid | Apache Druid LoadData HTTP InputSource 任意文件读取漏洞 | web/apache-druid/CVE-2021-36749.md |
| QVD-2023-9629 | CRITICAL | apache-druid | Apache Druid Kafka JNDI 注入远程代码执行漏洞 | web/apache-druid/QVD-2023-9629.md |
| APEREO-CAS-4.1-RCE | CRITICAL | apereo-cas | Apereo CAS 4.1 反序列化命令执行漏洞 | web/apereo-cas/APEREO-CAS-4.1-RCE.md |
| BUDIBASE-UNAUTH-RCE | CRITICAL | budibase | Budibase 未授权 Webhook RCE | web/budibase/BUDIBASE-UNAUTH-RCE.md |
| CVE-2026-31816 | HIGH | budibase | Budibase Webhook查询参数认证绕过漏洞 (CVE-2026-31816) | web/budibase/CVE-2026-31816.md |
| CVE-2022-46169 | CRITICAL | cacti | Cacti remote_agent.php 命令注入漏洞 (CVE-2022-46169) | web/cacti/CVE-2022-46169.md |
| CVE-2023-39361 | CRITICAL | cacti | Cacti graph_view.php SQL注入导致RCE漏洞 (CVE-2023-39361) | web/cacti/CVE-2023-39361.md |
| CVE-2025-24367 | HIGH | cacti | Cacti RRDTool参数注入导致RCE漏洞 (CVE-2025-24367) | web/cacti/CVE-2025-24367.md |
| CVE-2026-25887 | CRITICAL | chartbrew | Chartbrew MongoDB查询远程代码执行漏洞 (CVE-2026-25887) | web/chartbrew/CVE-2026-25887.md |
| CVE-2019-9053 | HIGH | cmsms | CMS Made Simple SQL注入漏洞 (CVE-2019-9053) | web/cmsms/CVE-2019-9053.md |
| CVE-2021-26120 | CRITICAL | cmsms | CMS Made Simple Smarty SSTI代码执行漏洞 (CVE-2021-26120) | web/cmsms/CVE-2021-26120.md |
| COREMAIL-INFO-LEAK | MEDIUM | coremail | Coremail 邮件系统配置信息泄露漏洞 | web/coremail/COREMAIL-INFO-LEAK.md |
| CVE-2023-41892 | CRITICAL | craftcms | CraftCMS ConditionsController 远程代码执行漏洞 (CVE-2023-41892) | web/craftcms/CVE-2023-41892.md |
| CVE-2024-56145 | CRITICAL | craftcms | CraftCMS register_argc_argv 远程代码执行漏洞 (CVE-2024-56145) | web/craftcms/CVE-2024-56145.md |
| CVE-2025-32432 | CRITICAL | craftcms | CraftCMS Yii类注入远程代码执行漏洞 (CVE-2025-32432) | web/craftcms/CVE-2025-32432.md |
| CVE-2024-47176 | CRITICAL | cups-browsed | CUPS cups-browsed 链式漏洞：未授权远程命令执行（CVE-2024-47176 + CVE-2024-47175 + CVE-2024-47076） | web/cups-browsed/CVE-2024-47176.md |
| DEDECMS-5.8-SHOWMSG-RCE | CRITICAL | dedecms | DedeCMS 5.8.1 ShowMsg 模板注入远程命令执行漏洞 | web/dedecms/DEDECMS-5.8-SHOWMSG-RCE.md |
| DISCUZ-DOWNREMOTEIMG-SSRF | HIGH | discuz | Discuz! X2/X3 前台 downremoteimg 远程图片下载 SSRF 漏洞 | web/discuz/DISCUZ-DOWNREMOTEIMG-SSRF.md |
| DISCUZ-WOOYUN-2010-080723 | CRITICAL | discuz | Discuz 7.x/6.x 全局变量防御绕过导致RCE漏洞 | web/discuz/DISCUZ-WOOYUN-2010-080723.md |
| DISCUZ-X3.4-ARBITRARY-FILE-DELETION | MEDIUM | discuz | Discuz!X 任意文件删除漏洞 | web/discuz/DISCUZ-X3.4-ARBITRARY-FILE-DELETION.md |
| CVE-2014-3704 | CRITICAL | drupal | Drupal Drupalgeddon SQL注入漏洞 (CVE-2014-3704) | web/drupal/CVE-2014-3704.md |
| CVE-2017-6920 | CRITICAL | drupal | Drupal PECL YAML反序列化RCE漏洞 (CVE-2017-6920) | web/drupal/CVE-2017-6920.md |
| CVE-2018-7600 | CRITICAL | drupal | Drupal Drupalgeddon 2 RCE漏洞 (CVE-2018-7600) | web/drupal/CVE-2018-7600.md |
| CVE-2018-7602 | CRITICAL | drupal | Drupal Drupalgeddon 3 RCE漏洞 (CVE-2018-7602) | web/drupal/CVE-2018-7602.md |
| CVE-2019-6339 | CRITICAL | drupal | Drupal PHAR反序列化RCE漏洞 (CVE-2019-6339) | web/drupal/CVE-2019-6339.md |
| CVE-2019-6340 | CRITICAL | drupal | Drupal 8 REST 反序列化远程代码执行（CVE-2019-6340） | web/drupal/CVE-2019-6340.md |
| ECSHOP-SQLi-RCE | CRITICAL | ecshop | ECShop 2.x/3.x SQL注入导致任意代码执行漏洞 | web/ecshop/ECSHOP-SQLi-RCE.md |
| EPOINT-INFO-LEAK | MEDIUM | epoint-oa | 新点OA ExcelExport 用户信息泄露漏洞 | web/epoint-oa/EPOINT-INFO-LEAK.md |
| ESAFENET-DATAIMPORT-RCE | CRITICAL | esafenet | 亿赛通电子文档安全管理系统 Solr dataimport 远程命令执行漏洞 | web/esafenet/ESAFENET-DATAIMPORT-RCE.md |
| EYOU-MONI-RCE | CRITICAL | eyou | 亿邮电子邮件系统 moni_detail.do 远程命令执行漏洞 | web/eyou/EYOU-MONI-RCE.md |
| CNVD-2018-04757 | HIGH | finereport | 帆软FineReport V8 任意文件读取 | web/finereport/CNVD-2018-04757.md |
| FINEREPORT-CHANNEL-RCE | CRITICAL | finereport | 帆软FineReport channel 远程命令执行 | web/finereport/FINEREPORT-CHANNEL-RCE.md |
| FINEREPORT-DIRECTORY-TRAVERSAL | HIGH | finereport | 帆软FineReport 目录遍历任意文件读取漏洞 | web/finereport/FINEREPORT-DIRECTORY-TRAVERSAL.md |
| FINEREPORT-RCE | CRITICAL | finereport | 帆软FineReport V9 后台远程代码执行 | web/finereport/FINEREPORT-RCE.md |
| FINEREPORT-SSRF | HIGH | finereport | 帆软FineReport SSRF 漏洞 | web/finereport/FINEREPORT-SSRF.md |
| FINEREPORT-V9-UPLOAD | CRITICAL | finereport | 帆软FineReport V9 任意文件覆盖上传 | web/finereport/FINEREPORT-V9-UPLOAD.md |
| FUELCMS-1.4-RCE | CRITICAL | fuelcms | Fuel CMS 1.4.1 远程代码执行漏洞 | web/fuelcms/FUELCMS-1.4-RCE.md |
| CVE-2022-35914 | CRITICAL | glpi | GLPI htmLawed 远程命令执行漏洞 | web/glpi/CVE-2022-35914.md |
| HEXIN-UPLOAD-RCE | CRITICAL | hexin | 和信创天云桌面系统 upload_file.php 任意文件上传 RCE | web/hexin/HEXIN-UPLOAD-RCE.md |
| HONGFAN-FILE-READ | HIGH | hongfan-oa | 红帆OA ioffice ioFileExport.aspx 任意文件读取漏洞 | web/hongfan-oa/HONGFAN-FILE-READ.md |
| HUATIAN-SQLI | HIGH | huatian-oa | 华天动力OA 8000 workFlowService SQL注入漏洞 | web/huatian-oa/HUATIAN-SQLI.md |
| HUIJIETONG-FILE-READ | HIGH | huijietong | 会捷通云视讯 fileDownload 任意文件读取漏洞 | web/huijietong/HUIJIETONG-FILE-READ.md |
| IMO-MULTI-RCE | CRITICAL | imo | imo 云办公室多接口远程命令执行漏洞 | web/imo/IMO-MULTI-RCE.md |
| CVE-2024-48307 | CRITICAL | jeecgboot | JeecgBoot onlDragDatasetHead getTotalData 未授权 SQL 注入漏洞（CVE-2024-48307） | web/jeecgboot/CVE-2024-48307.md |
| CVE-2026-5616 | HIGH | jeecgboot | JeecgBoot AI 聊天模块 /airag/chat/send 未授权工具调用漏洞（CVE-2026-5616） | web/jeecgboot/CVE-2026-5616.md |
| CVE-2026-58377 | HIGH | jeecgboot | JeecgBoot OpenAPI 凭证管理端点缺失授权漏洞（CVE-2026-58377） | web/jeecgboot/CVE-2026-58377.md |
| JINHER-FILE-READ | HIGH | jinher-oa | 金和OA C6 download.asp 任意文件读取漏洞 | web/jinher-oa/JINHER-FILE-READ.md |
| JIXIAN-FILE-READ | HIGH | jixian-oa | 极限OA video_file.php 任意文件读取漏洞 | web/jixian-oa/JIXIAN-FILE-READ.md |
| CVE-2015-8562 | CRITICAL | joomla | Joomla 反序列化RCE漏洞 (CVE-2015-8562) | web/joomla/CVE-2015-8562.md |
| CVE-2017-8917 | HIGH | joomla | Joomla 3.7.0 com_fields SQL注入漏洞 (CVE-2017-8917) | web/joomla/CVE-2017-8917.md |
| CVE-2023-23752 | HIGH | joomla | Joomla 权限绕过漏洞 (CVE-2023-23752) | web/joomla/CVE-2023-23752.md |
| KINGDEE-CLOUD-FILE-READ | HIGH | kingdee | 金蝶云星空 CommonFileServer 任意文件读取 | web/kingdee/KINGDEE-CLOUD-FILE-READ.md |
| KINGDEE-CLOUD-UPLOAD | CRITICAL | kingdee | 金蝶云星空 ScpSupRegHandler/ImpReportFile 任意文件上传 | web/kingdee/KINGDEE-CLOUD-UPLOAD.md |
| KINGDEE-EAS-DESER | CRITICAL | kingdee | 金蝶EAS 反序列化/文件上传 RCE | web/kingdee/KINGDEE-EAS-DESER.md |
| KINGDEE-EAS-TRAVERSAL | HIGH | kingdee | 金蝶EAS Apusic server_file 目录遍历/uploadLogo 文件上传 | web/kingdee/KINGDEE-EAS-TRAVERSAL.md |
| KINGDEE-K3CLOUD-DESER | CRITICAL | kingdee | 金蝶 K3Cloud BinaryFormatter 反序列化 RCE | web/kingdee/KINGDEE-K3CLOUD-DESER.md |
| KINGSOFT-V8-MULTI-RCE | CRITICAL | kingsoft-v8 | 金山 V8/V9 终端安全系统 多接口远程命令执行及文件上传漏洞 | web/kingsoft-v8/KINGSOFT-V8-MULTI-RCE.md |
| LANDRAY-ADMIN-JNDI-RCE | CRITICAL | landray-oa | 蓝凌OA admin.do JNDI远程命令执行 | web/landray-oa/LANDRAY-ADMIN-JNDI-RCE.md |
| LANDRAY-EIS-UPLOAD | CRITICAL | landray-oa | 蓝凌EIS api.aspx 任意文件上传 | web/landray-oa/LANDRAY-EIS-UPLOAD.md |
| LANDRAY-OA-RCE | CRITICAL | landray-oa | 蓝凌OA custom.jsp SSRF/JNDI 远程代码执行 | web/landray-oa/LANDRAY-OA-RCE.md |
| LANDRAY-SEARCHMAIN-RCE | CRITICAL | landray-oa | 蓝凌OA sysSearchMain.do 远程命令执行 | web/landray-oa/LANDRAY-SEARCHMAIN-RCE.md |
| LANDRAY-TREEXML-RCE | CRITICAL | landray-oa | 蓝凌OA treexml.tmpl 远程命令执行（Tomcat回显） | web/landray-oa/LANDRAY-TREEXML-RCE.md |
| CVE-2021-3019 | HIGH | lanproxy | Lanproxy 目录遍历任意文件读取（CVE-2021-3019） | web/lanproxy/CVE-2021-3019.md |
| CNVD-2020-62256 | HIGH | leagsoft | 联软入网身份认证系统任意文件上传漏洞（CNVD-2020-62256） | web/leagsoft/CNVD-2020-62256.md |
| CNVD-2024-25489 | HIGH | leagsoft | 联软安全数据交换系统 poserver.zz 任意文件读取漏洞（CNVD-2024-25489） | web/leagsoft/CNVD-2024-25489.md |
| CVE-2021-41277 | MEDIUM | metabase | Metabase 任意文件读取漏洞 (CVE-2021-41277) | web/metabase/CVE-2021-41277.md |
| CVE-2023-38646 | CRITICAL | metabase | Metabase 未授权JDBC远程代码执行漏洞 (CVE-2023-38646) | web/metabase/CVE-2023-38646.md |
| NEWCAPEC-SSTI-RCE | CRITICAL | newcapec | 新开普前置服务管理平台 service.action FreeMarker SSTI 远程命令执行漏洞 | web/newcapec/NEWCAPEC-SSTI-RCE.md |
| REACT2SHELL-CVE-2025-55182 | CRITICAL | nextjs | Next.js React Flight 反序列化 RCE (React2Shell) | web/nextjs/REACT2SHELL-CVE-2025-55182.md |
| CVE-2023-2901 | MEDIUM | nfine | NFine快速开发平台 User/GetGridJson 未授权访问漏洞（CVE-2023-2901） | web/nfine/CVE-2023-2901.md |
| CVE-2023-2902 | MEDIUM | nfine | NFine快速开发平台 Organize/GetTreeGridJson 未授权访问漏洞（CVE-2023-2902） | web/nfine/CVE-2023-2902.md |
| CVE-2023-2903 | MEDIUM | nfine | NFine快速开发平台 Role/GetGridJson 未授权访问漏洞（CVE-2023-2903） | web/nfine/CVE-2023-2903.md |
| NOCOBASE-SANDBOX-RCE | CRITICAL | nocobase | NocoBase 工作流脚本 VM 沙箱逃逸 RCE | web/nocobase/NOCOBASE-SANDBOX-RCE.md |
| OPENSNS-SHARE-RCE | CRITICAL | opensns | OpenSNS ShareController 远程命令执行漏洞 | web/opensns/OPENSNS-SHARE-RCE.md |
| PBOOTCMS-RCE | CRITICAL | pbootcms | PbootCMS V3.1.2 正则绕过远程命令执行漏洞 | web/pbootcms/PBOOTCMS-RCE.md |
| CVE-2018-14399 | CRITICAL | phpcms | PHPCMS 9.6.0 前台任意文件上传漏洞（CVE-2018-14399） | web/phpcms/CVE-2018-14399.md |
| CVE-2019-10027 | MEDIUM | phpcms | PHPCMS 9.6.x 个人信息邮箱字段跨站脚本漏洞（CVE-2019-10027） | web/phpcms/CVE-2019-10027.md |
| PHPCMS-9.6.0-WAP-SQLI | HIGH | phpcms | PHPCMS 9.6.0 前台 WAP/Content 模块 SQL 注入漏洞 | web/phpcms/PHPCMS-9.6.0-WAP-SQLI.md |
| CVE-2015-2208 | CRITICAL | phpmoadmin | phpMoAdmin 远程代码执行（CVE-2015-2208） | web/phpmoadmin/CVE-2015-2208.md |
| CVE-2020-5504 | HIGH | phpmyadmin | phpMyAdmin SQL 注入远程代码执行（CVE-2020-5504） | web/phpmyadmin/CVE-2020-5504.md |
| PIGCMS-UPLOAD | CRITICAL | pigcms | PigCMS action_flashUpload 任意文件上传漏洞 | web/pigcms/PIGCMS-UPLOAD.md |
| QILAI-SQLI | HIGH | qilai-oa | 启莱OA 多接口 SQL注入漏洞 | web/qilai-oa/QILAI-SQLI.md |
| REALFRIEND-AGENTBOARD-RCE | CRITICAL | realfriend | 瑞友天翼应用虚拟化系统 AgentBoard.XGI SQL注入写 Webshell RCE | web/realfriend/REALFRIEND-AGENTBOARD-RCE.md |
| RUOYI-SHIRO-DESER | CRITICAL | ruoyi | 若依CMS Shiro反序列化远程代码执行漏洞 | web/ruoyi/RUOYI-SHIRO-DESER.md |
| RUOYI-SQLI | HIGH | ruoyi | 若依CMS 后台SQL注入漏洞 | web/ruoyi/RUOYI-SQLI.md |
| SANGFOR-AD-LOGIN-RCE | CRITICAL | sangfor | 深信服应用交付管理系统 login 远程命令执行漏洞 | web/sangfor/SANGFOR-AD-LOGIN-RCE.md |
| SANGFOR-EDR-RCE | CRITICAL | sangfor | 深信服 EDR c.php 远程命令执行漏洞 (CNVD-2020-46552) | web/sangfor/SANGFOR-EDR-RCE.md |
| CNVD-2019-19299 | CRITICAL | seeyon-oa | 致远OA A8 htmlofficeservlet 任意文件上传导致远程代码执行（CNVD-2019-19299） | web/seeyon-oa/CNVD-2019-19299.md |
| CNVD-2020-62422 | HIGH | seeyon-oa | 致远OA webmail.do 任意文件下载 | web/seeyon-oa/CNVD-2020-62422.md |
| SEEYON-A6-INFO-LEAK | HIGH | seeyon-oa | 致远OA A6 信息泄露（数据库配置/Session） | web/seeyon-oa/SEEYON-A6-INFO-LEAK.md |
| SEEYON-A6-SQLI-RCE | CRITICAL | seeyon-oa | 致远OA A6 test.jsp/setextno.jsp SQL注入写入Webshell | web/seeyon-oa/SEEYON-A6-SQLI-RCE.md |
| SEEYON-AJAX-UPLOAD-RCE | CRITICAL | seeyon-oa | 致远OA ajax.do 未授权文件上传 RCE | web/seeyon-oa/SEEYON-AJAX-UPLOAD-RCE.md |
| SEEYON-M1SERVER-DESER-RCE | CRITICAL | seeyon-oa | 致远OA M1Server userTokenService 反序列化 RCE | web/seeyon-oa/SEEYON-M1SERVER-DESER-RCE.md |
| SEEYON-PASSWORD-RESET | CRITICAL | seeyon-oa | 致远OA 未授权短信验证码绕过重置密码 | web/seeyon-oa/SEEYON-PASSWORD-RESET.md |
| SEEYON-SESSION-LEAK | CRITICAL | seeyon-oa | 致远OA Session 泄露导致任意管理员登录 | web/seeyon-oa/SEEYON-SESSION-LEAK.md |
| SEEYON-WPSASSIST-UPLOAD | CRITICAL | seeyon-oa | 致远OA wpsAssistServlet 任意文件上传 | web/seeyon-oa/SEEYON-WPSASSIST-UPLOAD.md |
| SHIZIYUCMS-MULTI-UPLOAD | CRITICAL | shiziyucms | 狮子鱼CMS 多接口任意文件上传漏洞 | web/shiziyucms/SHIZIYUCMS-MULTI-UPLOAD.md |
| SHOPXO-FILE-READ | HIGH | shopxo | ShopXO 任意文件读取漏洞 (CNVD-2021-15822) | web/shopxo/SHOPXO-FILE-READ.md |
| SMARTBI-RCE | CRITICAL | smartbi | Smartbi 大数据分析平台 RMIServlet 远程命令执行漏洞 | web/smartbi/SMARTBI-RCE.md |
| SMARTOA-FILE-READ | HIGH | smartoa | 智明SmartOA EmailDownload.ashx 任意文件下载漏洞 | web/smartoa/SMARTOA-FILE-READ.md |
| SPIDERFLOW-RCE | CRITICAL | spiderflow | SpiderFlow save 远程命令执行漏洞 | web/spiderflow/SPIDERFLOW-RCE.md |
| CVE-2022-22947 | CRITICAL | spring | Spring Cloud Gateway Actuator SpEL 代码注入远程代码执行漏洞 CVE-2022-22947 | web/spring/CVE-2022-22947.md |
| CNVD-2022-10270 | CRITICAL | sunlogin | 向日葵远程控制软件 远程命令执行漏洞 | web/sunlogin/CNVD-2022-10270.md |
| TAIJI-GOV-SERVICE-CENTER-IDOR | HIGH | taiji | 深圳太极政府服务中心系统通用多处越权漏洞（wooyun-2014-066231） | web/taiji/TAIJI-GOV-SERVICE-CENTER-IDOR.md |
| CVE-2020-25540 | HIGH | thinkadmin | ThinkAdmin 目录遍历漏洞（CVE-2020-25540） | web/thinkadmin/CVE-2020-25540.md |
| CNVD-2018-24942 | CRITICAL | thinkphp | ThinkPHP 5.x 远程代码执行 | web/thinkphp/CNVD-2018-24942.md |
| THINKPHP-2-RCE | CRITICAL | thinkphp | ThinkPHP 2.x 任意代码执行漏洞 | web/thinkphp/THINKPHP-2-RCE.md |
| THINKPHP-5-RCE | CRITICAL | thinkphp | ThinkPHP5 5.0.22/5.1.29 远程代码执行漏洞 | web/thinkphp/THINKPHP-5-RCE.md |
| THINKPHP-5.0.23-RCE | CRITICAL | thinkphp | ThinkPHP5 5.0.23 远程代码执行漏洞 | web/thinkphp/THINKPHP-5.0.23-RCE.md |
| THINKPHP-IN-SQLINJECTION | HIGH | thinkphp | ThinkPHP5 SQL注入漏洞 | web/thinkphp/THINKPHP-IN-SQLINJECTION.md |
| THINKPHP-LANG-RCE | CRITICAL | thinkphp | ThinkPHP 多语言本地文件包含漏洞 | web/thinkphp/THINKPHP-LANG-RCE.md |
| CNVD-2019-34895 | CRITICAL | tongda-oa | 通达OA 前台文件上传+文件包含 RCE | web/tongda-oa/CNVD-2019-34895.md |
| TONGDA-API-ALI-UPLOAD | CRITICAL | tongda-oa | 通达OA v11.8 api.ali.php 任意文件上传 | web/tongda-oa/TONGDA-API-ALI-UPLOAD.md |
| TONGDA-LOGIN-BYPASS | CRITICAL | tongda-oa | 通达OA 多版本认证绕过任意用户登录 | web/tongda-oa/TONGDA-LOGIN-BYPASS.md |
| TONGDA-SWFUPLOAD-SQLI | HIGH | tongda-oa | 通达OA v11.5 swfupload_new.php SQL注入漏洞 | web/tongda-oa/TONGDA-SWFUPLOAD-SQLI.md |
| TONGDA-V116-PRINT-DELETE-RCE | CRITICAL | tongda-oa | 通达OA v11.6 print.php 文件删除+未授权上传 RCE | web/tongda-oa/TONGDA-V116-PRINT-DELETE-RCE.md |
| TONGDA-V118-GETWAY-RFI | CRITICAL | tongda-oa | 通达OA v11.8 getway.php 远程文件包含 | web/tongda-oa/TONGDA-V118-GETWAY-RFI.md |
| TONGDA-V119-GETDATA-RCE | CRITICAL | tongda-oa | 通达OA v11.9 getdata 接口任意命令执行 | web/tongda-oa/TONGDA-V119-GETDATA-RCE.md |
| TONGDA-V2017-FILE-READ | HIGH | tongda-oa | 通达OA v2017 video_file.php 任意文件下载漏洞 | web/tongda-oa/TONGDA-V2017-FILE-READ.md |
| TOPSEC-TOPAPP-RCE | CRITICAL | topsec | 天融信 TopApp-LB 负载均衡系统远程命令执行漏洞 | web/topsec/TOPSEC-TOPAPP-RCE.md |
| TRS-TEST-RCE | CRITICAL | trs | 拓尔思 TRS 媒资管理系统 testCommandExecutor.jsp 远程命令执行漏洞 | web/trs/TRS-TEST-RCE.md |
| TRS-WCM-READ_IMAGE-DOWNLOAD | HIGH | trs-wcm | TRS WCM read_image.jsp 任意文件下载漏洞（SSV-94688） | web/trs-wcm/TRS-WCM-READ_IMAGE-DOWNLOAD.md |
| TRS-WCM-WEBSERVICE-FILE-WRITE | CRITICAL | trs-wcm | TRS WCM 6.X WebService templateservicefacade 任意文件写入漏洞（wooyun-2013-034315 / SSV-62530） | web/trs-wcm/TRS-WCM-WEBSERVICE-FILE-WRITE.md |
| UEDITOR-NET-UPLOAD | CRITICAL | ueditor | UEditor .NET 版 catchimage 远程文件上传漏洞 | web/ueditor/UEDITOR-NET-UPLOAD.md |
| UEDITOR-SSRF | HIGH | ueditor | UEditor catchimage SSRF 漏洞 | web/ueditor/UEDITOR-SSRF.md |
| CVE-2019-16759 | CRITICAL | vbulletin | vBulletin 预授权远程代码执行（CVE-2019-16759） | web/vbulletin/CVE-2019-16759.md |
| WANHU-FILE-READ | HIGH | wanhu-oa | 万户OA ezOFFICE 多接口任意文件读取漏洞 | web/wanhu-oa/WANHU-FILE-READ.md |
| WANHU-FILE-UPLOAD | CRITICAL | wanhu-oa | 万户OA ezOFFICE 多接口任意文件上传漏洞 | web/wanhu-oa/WANHU-FILE-UPLOAD.md |
| WANHU-SQLI | HIGH | wanhu-oa | 万户OA ezOFFICE DocumentEdit.jsp SQL注入漏洞 | web/wanhu-oa/WANHU-SQLI.md |
| WANHU-XXE | HIGH | wanhu-oa | 万户OA ezOFFICE TeleConferenceService XXE注入漏洞 | web/wanhu-oa/WANHU-XXE.md |
| CNVD-2021-01603 | CRITICAL | weaver-oa | 泛微OA E-Bridge 任意文件上传漏洞 | web/weaver-oa/CNVD-2021-01603.md |
| CNVD-2021-33202 | HIGH | weaver-oa | 泛微OA LoginSSO.jsp SQL注入漏洞 | web/weaver-oa/CNVD-2021-33202.md |
| QVD-2026-14149 | CRITICAL | weaver-oa | 泛微 E-cology10（E10）未授权远程代码执行漏洞（QVD-2026-14149） | web/weaver-oa/QVD-2026-14149.md |
| WEAVER-DBCONFIG-LEAK | HIGH | weaver-oa | 泛微OA DBconfigReader.jsp 数据库配置泄露 | web/weaver-oa/WEAVER-DBCONFIG-LEAK.md |
| WEAVER-ECOLOGY-BSH-RCE | CRITICAL | weaver-oa | 泛微OA E-Cology BshServlet 远程代码执行漏洞 | web/weaver-oa/WEAVER-ECOLOGY-BSH-RCE.md |
| WEAVER-ECOLOGY-FILEREAD | HIGH | weaver-oa | 泛微OA E-Cology 任意文件读取漏洞 | web/weaver-oa/WEAVER-ECOLOGY-FILEREAD.md |
| WEAVER-ECOLOGY-GETFILEVIEWURL-SSRF | MEDIUM | weaver-oa | 泛微 E-Cology getFileViewUrl 接口 SSRF 漏洞 | web/weaver-oa/WEAVER-ECOLOGY-GETFILEVIEWURL-SSRF.md |
| WEAVER-ECOLOGY-SQLI | HIGH | weaver-oa | 泛微OA E-Cology WorkflowServiceXml SQL注入漏洞 | web/weaver-oa/WEAVER-ECOLOGY-SQLI.md |
| WEAVER-ECOLOGY-UPLOAD-RCE | CRITICAL | weaver-oa | 泛微OA E-Cology 多接口任意文件上传 | web/weaver-oa/WEAVER-ECOLOGY-UPLOAD-RCE.md |
| WEAVER-EOFFICE-UPLOAD-RCE | CRITICAL | weaver-oa | 泛微 E-Office 多路径任意文件上传 | web/weaver-oa/WEAVER-EOFFICE-UPLOAD-RCE.md |
| WEAVER-ETEAMS-IDOR-USERINFO | MEDIUM | weaver-oa | 泛微 eteams OA 越权修改任意用户信息漏洞（wooyun-2014-072571） | web/weaver-oa/WEAVER-ETEAMS-IDOR-USERINFO.md |
| WEAVER-OA-AUTH-BYPASS | CRITICAL | weaver-oa | 泛微OA ofsLogin/VerifyQuickLogin 任意用户登录 | web/weaver-oa/WEAVER-OA-AUTH-BYPASS.md |
| WEAVER-WORKFLOWSERVICE-RCE | CRITICAL | weaver-oa | 泛微OA E-Cology WorkflowServiceXml XStream反序列化RCE | web/weaver-oa/WEAVER-WORKFLOWSERVICE-RCE.md |
| CVE-2020-35606 | CRITICAL | webmin | Webmin 远程命令执行（CVE-2020-35606） | web/webmin/CVE-2020-35606.md |
| CVE-2021-31760 | HIGH | webmin | Webmin CSRF 到远程代码执行（CVE-2021-31760） | web/webmin/CVE-2021-31760.md |
| WEIPHP-FILE-READ | HIGH | weiphp | WeiPHP 5.0 前台任意文件读取漏洞 (CNVD-2020-68596) | web/weiphp/WEIPHP-FILE-READ.md |
| WEWORK-AGENTINFO-LEAK | MEDIUM | wework | 企业微信 agentinfo 接口敏感信息泄露 | web/wework/WEWORK-AGENTINFO-LEAK.md |
| CVE-2016-10033 | CRITICAL | wordpress | WordPress PHPMailer 远程代码执行（CVE-2016-10033） | web/wordpress/CVE-2016-10033.md |
| CVE-2020-11738 | HIGH | wordpress | WordPress Duplicator 插件任意文件读取漏洞 | web/wordpress/CVE-2020-11738.md |
| CVE-2020-25213 | CRITICAL | wordpress | WordPress File Manager 插件未授权文件上传 RCE | web/wordpress/CVE-2020-25213.md |
| CVE-2022-1119 | HIGH | wordpress | WordPress Simple File List 插件任意文件读取漏洞 | web/wordpress/CVE-2022-1119.md |
| WORDPRESS-PWNSCRIPTUM | CRITICAL | wordpress | WordPress 4.6 任意命令执行漏洞（PwnScriptum） | web/wordpress/WORDPRESS-PWNSCRIPTUM.md |
| WP-3DPRINT-UPLOAD | CRITICAL | wordpress | WordPress 3DPrint Lite 插件未授权文件上传漏洞 | web/wordpress/WP-3DPRINT-UPLOAD.md |
| CVE-2022-43183 | HIGH | xxl-job | XXL-JOB SSRF 漏洞泄露 accessToken 导致 RCE (CVE-2022-43183) | web/xxl-job/CVE-2022-43183.md |
| XXL-JOB-DEFAULT-TOKEN | CRITICAL | xxl-job | XXL-JOB 默认 accessToken 身份认证绕过漏洞 | web/xxl-job/XXL-JOB-DEFAULT-TOKEN.md |
| XXL-JOB-UNACC | CRITICAL | xxl-job | XXL-JOB executor 未授权访问漏洞 | web/xxl-job/XXL-JOB-UNACC.md |
| YIMI-FILE-READ | HIGH | yimi-oa | 一米OA getfile.jsp 任意文件读取漏洞 | web/yimi-oa/YIMI-FILE-READ.md |
| CHANJET-TPLUS-RCE | CRITICAL | yongyou | 畅捷通 T+ SQL注入/文件上传 RCE (QVD-2023-13615) | web/yongyou/CHANJET-TPLUS-RCE.md |
| CNVD-2021-01627 | CRITICAL | yongyou | 用友 NC BshServlet 远程代码执行漏洞 | web/yongyou/CNVD-2021-01627.md |
| YONGYOU-GRP-U8-RCE | CRITICAL | yongyou | 用友 GRP-U8 SQL注入/任意文件上传 RCE | web/yongyou/YONGYOU-GRP-U8-RCE.md |
| YONGYOU-KSOA-UPLOAD | CRITICAL | yongyou | 用友时空 KSOA ImageUpload 任意文件上传漏洞 | web/yongyou/YONGYOU-KSOA-UPLOAD.md |
| YONGYOU-MOBILE-UPLOAD | CRITICAL | yongyou | 用友移动管理系统 uploadApk.do 任意文件上传漏洞 | web/yongyou/YONGYOU-MOBILE-UPLOAD.md |
| YONGYOU-NC-DESER-RCE | CRITICAL | yongyou | 用友 NC FileReceiveServlet/XbrlPersistence 反序列化 RCE | web/yongyou/YONGYOU-NC-DESER-RCE.md |
| YONGYOU-NC-JSINVOKE-RCE | CRITICAL | yongyou | 用友 NC Cloud jsinvoke JNDI/EL表达式注入 RCE | web/yongyou/YONGYOU-NC-JSINVOKE-RCE.md |
| YONGYOU-U8-CLOUD-UPLOAD | CRITICAL | yongyou | 用友 U8 Cloud upload.jsp 任意文件上传漏洞 | web/yongyou/YONGYOU-U8-CLOUD-UPLOAD.md |
| YONGYOU-U8-CRM-RCE | CRITICAL | yongyou | 用友 U8 CRM getemaildata.php 任意文件上传/读取漏洞 | web/yongyou/YONGYOU-U8-CRM-RCE.md |
| ZENTAO-RCE | CRITICAL | zentao | 禅道项目管理系统远程代码执行漏洞 | web/zentao/ZENTAO-RCE.md |
| ZENTAO-SQLI | HIGH | zentao | 禅道项目管理系统SQL注入漏洞 | web/zentao/ZENTAO-SQLI.md |
| ZHIXIANG-SQLI | HIGH | zhixiang-oa | 致翔OA msglog.aspx SQL注入漏洞 | web/zhixiang-oa/ZHIXIANG-SQLI.md |
| ZZZCMS-SSTI-RCE | CRITICAL | zzzcms | zzzcms v1.7.5 前台模板注入远程命令执行漏洞 | web/zzzcms/ZZZCMS-SSTI-RCE.md |
