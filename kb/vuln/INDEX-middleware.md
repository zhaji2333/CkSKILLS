# 漏洞索引：middleware（436 条）

> 生成：`python3 tools/kb_index.py`；数据目录：`kb/`。
> 路径相对于 `kb/vuln/`；返回 [INDEX.md](INDEX.md)。

| ID | severity | product | 标题 | 相对路径 |
| --- | --- | --- | --- | --- |
| CVE-2015-5254 | CRITICAL | activemq | Apache ActiveMQ 反序列化漏洞 (CVE-2015-5254) | middleware/activemq/CVE-2015-5254.md |
| CVE-2016-3088 | CRITICAL | activemq | Apache ActiveMQ 任意文件写入漏洞 (CVE-2016-3088) | middleware/activemq/CVE-2016-3088.md |
| CVE-2017-15709 | MEDIUM | activemq | Apache ActiveMQ 信息泄露（CVE-2017-15709） | middleware/activemq/CVE-2017-15709.md |
| CVE-2022-41678 | HIGH | activemq | Apache ActiveMQ Jolokia 后台远程代码执行漏洞 (CVE-2022-41678) | middleware/activemq/CVE-2022-41678.md |
| CVE-2023-46604 | CRITICAL | activemq | Apache ActiveMQ OpenWire 协议反序列化命令执行漏洞 (CVE-2023-46604) | middleware/activemq/CVE-2023-46604.md |
| CVE-2020-11978 | CRITICAL | airflow | Apache Airflow 示例DAG命令注入漏洞 (CVE-2020-11978) | middleware/airflow/CVE-2020-11978.md |
| CVE-2020-11981 | CRITICAL | airflow | Apache Airflow Celery 消息中间件命令执行 (CVE-2020-11981) | middleware/airflow/CVE-2020-11981.md |
| CVE-2020-17526 | HIGH | airflow | Apache Airflow 默认密钥权限绕过 (CVE-2020-17526) | middleware/airflow/CVE-2020-17526.md |
| APISIX-CVE-2022-29266 | HIGH | apisix | Apache APISIX JWT密钥泄露 (CVE-2022-29266) | middleware/apisix/APISIX-CVE-2022-29266.md |
| APISIX-DEFAULT-KEY-RCE | CRITICAL | apisix | Apache APISIX 默认密钥与Dashboard远程代码执行 | middleware/apisix/APISIX-DEFAULT-KEY-RCE.md |
| CVE-2020-13945 | CRITICAL | apisix | Apache APISIX 默认API Token远程Lua代码执行 (CVE-2020-13945) | middleware/apisix/CVE-2020-13945.md |
| CVE-2021-45232 | CRITICAL | apisix | Apache APISIX Dashboard API权限绕过导致RCE (CVE-2021-45232) | middleware/apisix/CVE-2021-45232.md |
| CVE-2018-8715 | HIGH | appweb | AppWeb 认证绕过漏洞 (CVE-2018-8715) | middleware/appweb/CVE-2018-8715.md |
| CVE-2022-29165 | HIGH | argocd | ArgoCD - SSO认证绕过 | middleware/argocd/CVE-2022-29165.md |
| CVE-2024-31989 | CRITICAL | argocd | ArgoCD - Redis未授权缓存投毒导致K8s集群接管 | middleware/argocd/CVE-2024-31989.md |
| ARIA2-RCE | CRITICAL | aria2 | Aria2 RPC 任意文件写入漏洞 | middleware/aria2/ARIA2-RCE.md |
| CVE-2019-9733 | CRITICAL | artifactory | JFrog Artifactory 认证绕过（CVE-2019-9733） | middleware/artifactory/CVE-2019-9733.md |
| CVE-2014-6271 | CRITICAL | bash | Bash Shellshock 远程命令注入漏洞 (CVE-2014-6271) | middleware/bash/CVE-2014-6271.md |
| CELERY-CELERY3_REDIS_UNAUTH | CRITICAL | celery | Celery Redis未授权访问+Pickle反序列化漏洞 | middleware/celery/CELERY-CELERY3_REDIS_UNAUTH.md |
| CVE-2016-5385 | MEDIUM | cgi | CGI环境变量注入漏洞 (HTTPoxy - CVE-2016-5385) | middleware/cgi/CVE-2016-5385.md |
| CLICKHOUSE-UNAUTH | HIGH | clickhouse | ClickHouse HTTP API 未授权访问漏洞 | middleware/clickhouse/CLICKHOUSE-UNAUTH.md |
| CVE-2010-2861 | CRITICAL | coldfusion | Adobe ColdFusion 目录穿越文件读取漏洞 (CVE-2010-2861) | middleware/coldfusion/CVE-2010-2861.md |
| CVE-2017-3066 | CRITICAL | coldfusion | Adobe ColdFusion 反序列化漏洞 (CVE-2017-3066) | middleware/coldfusion/CVE-2017-3066.md |
| CVE-2021-21087 | MEDIUM | coldfusion | Adobe ColdFusion XSS 漏洞（CVE-2021-21087） | middleware/coldfusion/CVE-2021-21087.md |
| CVE-2023-26360 | CRITICAL | coldfusion | Adobe ColdFusion 不安全反序列化漏洞 (CVE-2023-26360) | middleware/coldfusion/CVE-2023-26360.md |
| CVE-2023-29300 | CRITICAL | coldfusion | Adobe ColdFusion XML反序列化命令执行漏洞 (CVE-2023-29300) | middleware/coldfusion/CVE-2023-29300.md |
| CVE-2015-8399 | MEDIUM | confluence | Confluence 任意文件读取（CVE-2015-8399） | middleware/confluence/CVE-2015-8399.md |
| CVE-2019-3396 | CRITICAL | confluence | Atlassian Confluence 路径穿越+SSTI漏洞 (CVE-2019-3396) | middleware/confluence/CVE-2019-3396.md |
| CVE-2021-26084 | CRITICAL | confluence | Atlassian Confluence OGNL表达式注入漏洞 (CVE-2021-26084) | middleware/confluence/CVE-2021-26084.md |
| CVE-2022-26134 | CRITICAL | confluence | Atlassian Confluence OGNL远程代码执行漏洞 (CVE-2022-26134) | middleware/confluence/CVE-2022-26134.md |
| CVE-2023-22515 | CRITICAL | confluence | Atlassian Confluence 属性覆盖权限绕过漏洞 (CVE-2023-22515) | middleware/confluence/CVE-2023-22515.md |
| CVE-2023-22527 | CRITICAL | confluence | Atlassian Confluence OGNL模板注入RCE漏洞 (CVE-2023-22527) | middleware/confluence/CVE-2023-22527.md |
| CVE-2017-12635 | HIGH | couchdb | CouchDB 垂直权限绕过漏洞 (CVE-2017-12635) | middleware/couchdb/CVE-2017-12635.md |
| CVE-2017-12636 | CRITICAL | couchdb | CouchDB 任意命令执行漏洞 (CVE-2017-12636) | middleware/couchdb/CVE-2017-12636.md |
| CVE-2022-24706 | CRITICAL | couchdb | CouchDB Erlang分布式协议代码执行漏洞 (CVE-2022-24706) | middleware/couchdb/CVE-2022-24706.md |
| CVE-2019-11580 | CRITICAL | crowd | Atlassian Crowd pdkinstall 远程代码执行（CVE-2019-11580） | middleware/crowd/CVE-2019-11580.md |
| CVE-2017-12794 | MEDIUM | django | Django调试页面XSS漏洞 (CVE-2017-12794) | middleware/django/CVE-2017-12794.md |
| CVE-2018-14574 | MEDIUM | django | Django CommonMiddleware任意URL跳转漏洞 (CVE-2018-14574) | middleware/django/CVE-2018-14574.md |
| CVE-2019-14234 | HIGH | django | Django JSONField/HStoreField SQL注入漏洞 (CVE-2019-14234) | middleware/django/CVE-2019-14234.md |
| CVE-2020-9402 | HIGH | django | Django GIS SQL注入漏洞 (CVE-2020-9402) | middleware/django/CVE-2020-9402.md |
| CVE-2021-35042 | HIGH | django | Django QuerySet.order_by() SQL注入漏洞 (CVE-2021-35042) | middleware/django/CVE-2021-35042.md |
| CVE-2022-34265 | HIGH | django | Django Trunc/Extract SQL注入漏洞 (CVE-2022-34265) | middleware/django/CVE-2022-34265.md |
| DOCKER-PRIVILEGED-ESCAPE | CRITICAL | docker | Docker 特权容器逃逸 | middleware/docker/DOCKER-PRIVILEGED-ESCAPE.md |
| DOCKER-PROCFS-ESCAPE | HIGH | docker | Docker 挂载宿主机 procfs 逃逸 | middleware/docker/DOCKER-PROCFS-ESCAPE.md |
| DOCKER-SOCKET-ESCAPE | CRITICAL | docker | Docker Socket 挂载逃逸 | middleware/docker/DOCKER-SOCKET-ESCAPE.md |
| DOCKER-UNAUTHORIZED-RCE | CRITICAL | docker | Docker Remote API 未授权访问导致RCE | middleware/docker/DOCKER-UNAUTHORIZED-RCE.md |
| CVE-2019-17564 | CRITICAL | dubbo | Apache Dubbo HTTP 协议反序列化 RCE (CVE-2019-17564) | middleware/dubbo/CVE-2019-17564.md |
| CVE-2020-1948 | CRITICAL | dubbo | Apache Dubbo Hessian 反序列化远程代码执行漏洞 | middleware/dubbo/CVE-2020-1948.md |
| CVE-2014-3120 | CRITICAL | elasticsearch | Elasticsearch MVEL 脚本引擎远程代码执行（CVE-2014-3120） | middleware/elasticsearch/CVE-2014-3120.md |
| CVE-2015-1427 | CRITICAL | elasticsearch | Elasticsearch Groovy 沙盒绕过远程代码执行漏洞 | middleware/elasticsearch/CVE-2015-1427.md |
| CVE-2015-3337 | HIGH | elasticsearch | Elasticsearch 目录穿越任意文件读取漏洞 | middleware/elasticsearch/CVE-2015-3337.md |
| ES-UNAUTH | HIGH | elasticsearch | Elasticsearch 未授权访问漏洞 | middleware/elasticsearch/ES-UNAUTH.md |
| CVE-2025-32433 | CRITICAL | erlang-otp | Erlang/OTP SSH 未授权远程代码执行漏洞 | middleware/erlang-otp/CVE-2025-32433.md |
| CVE-2021-26855 | CRITICAL | exchange | Microsoft Exchange ProxyLogon SSRF 漏洞 | middleware/exchange/CVE-2021-26855.md |
| CVE-2021-27065 | CRITICAL | exchange | Microsoft Exchange ProxyLogon 任意文件写入 RCE | middleware/exchange/CVE-2021-27065.md |
| CVE-2020-5902 | CRITICAL | f5-bigip | F5 BIG-IP TMUI 远程代码执行漏洞 | middleware/f5-bigip/CVE-2020-5902.md |
| CVE-2021-22986 | CRITICAL | f5-bigip | F5 BIG-IP iControl REST 未授权远程代码执行漏洞 | middleware/f5-bigip/CVE-2021-22986.md |
| CVE-2022-1388 | CRITICAL | f5-bigip | F5 BIG-IP iControl REST 认证绕过远程代码执行漏洞 | middleware/f5-bigip/CVE-2022-1388.md |
| CVE-2022-25845 | HIGH | fastjson | Fastjson <1.2.83 反序列化漏洞 | middleware/fastjson/CVE-2022-25845.md |
| FASTJSON-1.2.47-RCE | CRITICAL | fastjson | Fastjson 1.2.47 远程命令执行漏洞 | middleware/fastjson/FASTJSON-1.2.47-RCE.md |
| Fastjson-RCE-1.2.24 | CRITICAL | fastjson | Fastjson 1.2.24 反序列化 RCE | middleware/fastjson/Fastjson-RCE-1.2.24.md |
| FLASK-SSTI | CRITICAL | flask | Flask Jinja2 服务端模板注入漏洞 (SSTI) | middleware/flask/FLASK-SSTI.md |
| CVE-2020-17518 | CRITICAL | flink | Apache Flink 任意文件写入漏洞 (CVE-2020-17518) | middleware/flink/CVE-2020-17518.md |
| CVE-2020-17519 | MEDIUM | flink | Apache Flink jobmanager/logs 路径穿越漏洞 (CVE-2020-17519) | middleware/flink/CVE-2020-17519.md |
| CVE-2021-40822 | HIGH | geoserver | GeoServer 未授权SSRF漏洞 (CVE-2021-40822) | middleware/geoserver/CVE-2021-40822.md |
| CVE-2022-24816 | CRITICAL | geoserver | GeoServer JAI-EXT Jiffle代码注入RCE漏洞 (CVE-2022-24816) | middleware/geoserver/CVE-2022-24816.md |
| CVE-2023-25157 | HIGH | geoserver | GeoServer OGC Filter SQL注入漏洞 (CVE-2023-25157) | middleware/geoserver/CVE-2023-25157.md |
| CVE-2024-36401 | CRITICAL | geoserver | GeoServer 属性名表达式RCE漏洞 (CVE-2024-36401) | middleware/geoserver/CVE-2024-36401.md |
| CVE-2025-58360 | CRITICAL | geoserver | GeoServer WMS SLD_BODY XXE任意文件读取/SSRF漏洞 (CVE-2025-58360) | middleware/geoserver/CVE-2025-58360.md |
| CVE-2018-16509 | CRITICAL | ghostscript | GhostScript 沙箱绕过命令执行漏洞 (CVE-2018-16509) | middleware/ghostscript/CVE-2018-16509.md |
| CVE-2018-19475 | CRITICAL | ghostscript | GhostScript 沙箱绕过命令执行漏洞 (CVE-2018-19475) | middleware/ghostscript/CVE-2018-19475.md |
| CVE-2019-6116 | CRITICAL | ghostscript | GhostScript 沙箱绕过命令执行漏洞 (CVE-2019-6116) | middleware/ghostscript/CVE-2019-6116.md |
| CVE-2017-8386 | CRITICAL | git | GIT-SHELL 沙盒绕过命令执行漏洞 (CVE-2017-8386) | middleware/git/CVE-2017-8386.md |
| GITEA-1.4-RCE | CRITICAL | gitea | Gitea 1.4.0 目录穿越命令执行漏洞 | middleware/gitea/GITEA-1.4-RCE.md |
| CVE-2016-9086 | MEDIUM | gitlab | GitLab 任意文件读取漏洞 (CVE-2016-9086) | middleware/gitlab/CVE-2016-9086.md |
| CVE-2020-26413 | MEDIUM | gitlab | GitLab GraphQL 用户邮箱信息泄露漏洞 (CVE-2020-26413) | middleware/gitlab/CVE-2020-26413.md |
| CVE-2021-22205 | CRITICAL | gitlab | GitLab 远程命令执行漏洞 (CVE-2021-22205) | middleware/gitlab/CVE-2021-22205.md |
| CVE-2021-22214 | HIGH | gitlab | GitLab CI Lint API 未授权 SSRF 漏洞 | middleware/gitlab/CVE-2021-22214.md |
| CVE-2018-1000533 | CRITICAL | gitlist | GitList 0.6.0 命令注入RCE漏洞 (CVE-2018-1000533) | middleware/gitlist/CVE-2018-1000533.md |
| CVE-2017-1000028 | MEDIUM | glassfish | GlassFish 任意文件读取漏洞 | middleware/glassfish/CVE-2017-1000028.md |
| CVE-2017-17562 | CRITICAL | goahead | GoAhead 远程命令执行漏洞 (CVE-2017-17562) | middleware/goahead/CVE-2017-17562.md |
| CVE-2021-42342 | CRITICAL | goahead | GoAhead 环境变量注入RCE漏洞 (CVE-2021-42342) | middleware/goahead/CVE-2021-42342.md |
| CVE-2018-18925 | HIGH | gogs | Gogs 任意用户登录漏洞 (CVE-2018-18925) | middleware/gogs/CVE-2018-18925.md |
| GOGS-LFS-OVERWRITE | CRITICAL | gogs | Gogs LFS 对象跨仓库覆写与符号链接 RCE | middleware/gogs/GOGS-LFS-OVERWRITE.md |
| CVE-2023-51449 | MEDIUM | gradio | Gradio 目录穿越任意文件读取漏洞 (CVE-2023-51449) | middleware/gradio/CVE-2023-51449.md |
| CVE-2024-1561 | MEDIUM | gradio | Gradio component_server 任意文件读取漏洞 (CVE-2024-1561) | middleware/gradio/CVE-2024-1561.md |
| CVE-2020-11110 | MEDIUM | grafana | Grafana Snapshot 存储型XSS漏洞 (CVE-2020-11110) | middleware/grafana/CVE-2020-11110.md |
| CVE-2021-39226 | CRITICAL | grafana | Grafana Snapshot 未授权访问/删除漏洞 (CVE-2021-39226) | middleware/grafana/CVE-2021-39226.md |
| CVE-2021-41174 | MEDIUM | grafana | Grafana AngularJS 表达式注入 XSS 漏洞（CVE-2021-41174） | middleware/grafana/CVE-2021-41174.md |
| CVE-2021-43798 | MEDIUM | grafana | Grafana 8.x 插件模块目录穿越漏洞 (CVE-2021-43798) | middleware/grafana/CVE-2021-43798.md |
| CVE-2022-32275 | HIGH | grafana | Grafana Snapshot 文件读取漏洞 (CVE-2022-32275) | middleware/grafana/CVE-2022-32275.md |
| CVE-2024-9264 | CRITICAL | grafana | Grafana SQL Expressions 远程代码执行漏洞 (CVE-2024-9264) | middleware/grafana/CVE-2024-9264.md |
| CVE-2025-4123 | HIGH | grafana | Grafana /public 路径穿越+开放重定向 SSRF/XSS（CVE-2025-4123） | middleware/grafana/CVE-2025-4123.md |
| GRAFANA-ADMIN-SSRF | HIGH | grafana | Grafana 管理后台SSRF漏洞 | middleware/grafana/GRAFANA-ADMIN-SSRF.md |
| CVE-2018-10054 | CRITICAL | h2database | H2 Database Web Console认证RCE漏洞 (CVE-2018-10054) | middleware/h2database/CVE-2018-10054.md |
| CVE-2021-42392 | CRITICAL | h2database | H2 Database Web Console未授权JNDI注入RCE漏洞 (CVE-2021-42392) | middleware/h2database/CVE-2021-42392.md |
| CVE-2022-23221 | CRITICAL | h2database | H2 Database Web Console JDBC攻击RCE漏洞 (CVE-2022-23221) | middleware/h2database/CVE-2022-23221.md |
| HADOOP-UNAUTHORIZED-YARN | CRITICAL | hadoop | Hadoop YARN ResourceManager 未授权RCE漏洞 | middleware/hadoop/HADOOP-UNAUTHORIZED-YARN.md |
| CVE-2019-16097 | MEDIUM | harbor | Harbor - 普通用户创建管理员权限提升 | middleware/harbor/CVE-2019-16097.md |
| CVE-2022-46463 | HIGH | harbor | Harbor - 未授权API访问与私有镜像泄露 | middleware/harbor/CVE-2022-46463.md |
| CVE-2026-4404 | CRITICAL | harbor | Harbor - 硬编码默认管理员凭据 | middleware/harbor/CVE-2026-4404.md |
| CVE-2024-42323 | CRITICAL | hertzbeat | Apache HertzBeat SnakeYaml反序列化RCE漏洞 (CVE-2024-42323) | middleware/hertzbeat/CVE-2024-42323.md |
| CVE-2017-15715 | CRITICAL | httpd | Apache HTTPD 换行符解析漏洞 (CVE-2017-15715) | middleware/httpd/CVE-2017-15715.md |
| CVE-2021-40438 | HIGH | httpd | Apache HTTP Server mod_proxy SSRF漏洞 (CVE-2021-40438) | middleware/httpd/CVE-2021-40438.md |
| CVE-2021-41773 | MEDIUM | httpd | Apache HTTP Server 2.4.49 路径穿越漏洞 (CVE-2021-41773) | middleware/httpd/CVE-2021-41773.md |
| CVE-2021-42013 | CRITICAL | httpd | Apache HTTP Server 2.4.50 路径穿越漏洞 (CVE-2021-42013) | middleware/httpd/CVE-2021-42013.md |
| HTTPD-APACHE_PARSING_VULNERABILITY | CRITICAL | httpd | Apache HTTP Server 多后缀解析漏洞 | middleware/httpd/HTTPD-APACHE_PARSING_VULNERABILITY.md |
| HTTPD-MOD-STATUS | MEDIUM | httpd | Apache mod_status 信息泄露 | middleware/httpd/HTTPD-MOD-STATUS.md |
| HTTPD-SSI-RCE | CRITICAL | httpd | Apache HTTP Server SSI 远程命令执行漏洞 | middleware/httpd/HTTPD-SSI-RCE.md |
| CVE-2024-27348 | CRITICAL | hugegraph | Apache HugeGraph Gremlin API远程代码执行漏洞 (CVE-2024-27348) | middleware/hugegraph/CVE-2024-27348.md |
| CVE-2024-43441 | CRITICAL | hugegraph | Apache HugeGraph JWT Token硬编码权限绕过漏洞 (CVE-2024-43441) | middleware/hugegraph/CVE-2024-43441.md |
| IIS-PARSING-VULNERABILITY | HIGH | iis | IIS 解析漏洞 | middleware/iis/IIS-PARSING-VULNERABILITY.md |
| IIS-SHORT-FILENAME | MEDIUM | iis | IIS 短文件名枚举漏洞 | middleware/iis/IIS-SHORT-FILENAME.md |
| IIS-WEBDAV-PUT | CRITICAL | iis | IIS WebDAV PUT+MOVE 文件上传漏洞 | middleware/iis/IIS-WEBDAV-PUT.md |
| CVE-2016-3714 | CRITICAL | imagemagick | ImageMagick Imagetragick 命令注入漏洞 (CVE-2016-3714) | middleware/imagemagick/CVE-2016-3714.md |
| CVE-2020-29599 | CRITICAL | imagemagick | ImageMagick PDF密码位置命令注入漏洞 (CVE-2020-29599) | middleware/imagemagick/CVE-2020-29599.md |
| CVE-2022-44268 | MEDIUM | imagemagick | ImageMagick 任意文件读取漏洞 (CVE-2022-44268) | middleware/imagemagick/CVE-2022-44268.md |
| CVE-2026-24061 | CRITICAL | inetutils | GNU InetUtils telnetd 参数注入认证绕过漏洞 (CVE-2026-24061) | middleware/inetutils/CVE-2026-24061.md |
| CVE-2019-20933 | HIGH | influxdb | InfluxDB JWT 认证绕过漏洞 (CVE-2019-20933) | middleware/influxdb/CVE-2019-20933.md |
| CVE-2025-1974 | CRITICAL | ingress-nginx | Kubernetes Ingress-NGINX Admission Controller 未授权 RCE (IngressNightmare) | middleware/ingress-nginx/CVE-2025-1974.md |
| CVE-2020-21224 | CRITICAL | inspur | 浪潮 ClusterEngine V4.0 远程命令执行漏洞 | middleware/inspur/CVE-2020-21224.md |
| CVE-2017-7525 | CRITICAL | jackson | Jackson-databind 反序列化RCE漏洞 (CVE-2017-7525) | middleware/jackson/CVE-2017-7525.md |
| CVE-2020-35728 | CRITICAL | jackson | Jackson-databind 反序列化远程代码执行（CVE-2020-35728） | middleware/jackson/CVE-2020-35728.md |
| CVE-2020-8840 | CRITICAL | jackson | Jackson-databind 反序列化远程代码执行（CVE-2020-8840） | middleware/jackson/CVE-2020-8840.md |
| JAVA-RMI-CODEBASE | CRITICAL | java | Java RMI Codebase 远程代码执行漏洞 | middleware/java/JAVA-RMI-CODEBASE.md |
| JAVA-RMI-REGISTRY-BIND-DESERIALIZATION | CRITICAL | java | Java RMI Registry 反序列化命令执行漏洞 | middleware/java/JAVA-RMI-REGISTRY-BIND-DESERIALIZATION.md |
| JAVA-RMI-REGISTRY-BIND-DESERIALIZATION-BYPASS | CRITICAL | java | Java RMI Registry 反序列化绕过漏洞 | middleware/java/JAVA-RMI-REGISTRY-BIND-DESERIALIZATION-BYPASS.md |
| JDWP-RCE | CRITICAL | java | JDWP 调试接口远程代码执行漏洞 | middleware/java/JDWP-RCE.md |
| CVE-2017-12149 | CRITICAL | jboss | JBoss 5.x/6.x HttpInvoker 反序列化RCE漏洞 (CVE-2017-12149) | middleware/jboss/CVE-2017-12149.md |
| CVE-2017-7504 | CRITICAL | jboss | JBoss 4.x JBossMQ JMS 反序列化RCE漏洞 (CVE-2017-7504) | middleware/jboss/CVE-2017-7504.md |
| JBOSS-JMXCONSOLE-UNAUTH | CRITICAL | jboss | JBoss JMX Console 未授权访问 WAR 部署 | middleware/jboss/JBOSS-JMXCONSOLE-UNAUTH.md |
| JBOSS-JMXINVOKERSERVLET-DESERIALIZATION | CRITICAL | jboss | JBoss JMXInvokerServlet 反序列化RCE漏洞 | middleware/jboss/JBOSS-JMXINVOKERSERVLET-DESERIALIZATION.md |
| CVE-2015-8103 | CRITICAL | jenkins | Jenkins CLI 反序列化远程代码执行漏洞 (CVE-2015-8103) | middleware/jenkins/CVE-2015-8103.md |
| CVE-2016-0792 | CRITICAL | jenkins | Jenkins XStream Groovy 反序列化漏洞 (CVE-2016-0792) | middleware/jenkins/CVE-2016-0792.md |
| CVE-2017-1000353 | CRITICAL | jenkins | Jenkins CLI 远程代码执行漏洞 (CVE-2017-1000353) | middleware/jenkins/CVE-2017-1000353.md |
| CVE-2018-1000861 | CRITICAL | jenkins | Jenkins - Groovy元编程无认证RCE | middleware/jenkins/CVE-2018-1000861.md |
| CVE-2019-1003000 | HIGH | jenkins | Jenkins Groovy 沙盒绕过远程代码执行漏洞 (CVE-2019-1003000) | middleware/jenkins/CVE-2019-1003000.md |
| CVE-2024-23897 | CRITICAL | jenkins | Jenkins - CLI任意文件读取 | middleware/jenkins/CVE-2024-23897.md |
| CVE-2024-23898 | HIGH | jenkins | Jenkins - WebSocket CLI跨站劫持(CSWSH) | middleware/jenkins/CVE-2024-23898.md |
| JENKINS-SCRIPT-CONSOLE-RCE | CRITICAL | jenkins | Jenkins - Script Console Groovy RCE | middleware/jenkins/JENKINS-SCRIPT-CONSOLE-RCE.md |
| CVE-2021-28164 | MEDIUM | jetty | Jetty %2e 路径穿越敏感信息泄露漏洞 (CVE-2021-28164) | middleware/jetty/CVE-2021-28164.md |
| CVE-2021-28169 | MEDIUM | jetty | Jetty ConcatServlet/WelcomeFilter 多重解码敏感信息泄露 (CVE-2021-28169) | middleware/jetty/CVE-2021-28169.md |
| CVE-2021-34429 | MEDIUM | jetty | Jetty %2e 路径穿越绕过敏感信息泄露漏洞 (CVE-2021-34429) | middleware/jetty/CVE-2021-34429.md |
| CVE-2023-1454 | HIGH | jimureport | JeecgBoot 积木报表 qurestSql 接口 apiSelectId 参数 SQL 注入漏洞 CVE-2023-1454 | middleware/jimureport/CVE-2023-1454.md |
| CVE-2023-4450 | CRITICAL | jimureport | JeecgBoot JimuReport FreeMarker SSTI命令执行漏洞 (CVE-2023-4450) | middleware/jimureport/CVE-2023-4450.md |
| CVE-2024-44893 | CRITICAL | jimureport | JimuReport dict/list 权限提升漏洞 (CVE-2024-44893) | middleware/jimureport/CVE-2024-44893.md |
| CVE-2017-9506 | MEDIUM | jira | Jira OAuth 插件 SSRF（CVE-2017-9506） | middleware/jira/CVE-2017-9506.md |
| CVE-2019-11581 | CRITICAL | jira | Atlassian Jira 模板注入RCE漏洞 (CVE-2019-11581) | middleware/jira/CVE-2019-11581.md |
| CVE-2019-3403 | MEDIUM | jira | Jira 用户名枚举信息泄露（CVE-2019-3403） | middleware/jira/CVE-2019-3403.md |
| CVE-2019-8442 | HIGH | jira | Jira 未授权敏感信息泄露（CVE-2019-8442） | middleware/jira/CVE-2019-8442.md |
| CVE-2019-8451 | HIGH | jira | Jira SSRF 漏洞（CVE-2019-8451） | middleware/jira/CVE-2019-8451.md |
| CVE-2020-14181 | MEDIUM | jira | Jira 用户名枚举漏洞（CVE-2020-14181） | middleware/jira/CVE-2020-14181.md |
| CVE-2022-26135 | HIGH | jira | Atlassian Jira Mobile Plugin SSRF 漏洞 (CVE-2022-26135) | middleware/jira/CVE-2022-26135.md |
| CVE-2018-1297 | CRITICAL | jmeter | Apache JMeter RMI 反序列化RCE漏洞 (CVE-2018-1297) | middleware/jmeter/CVE-2018-1297.md |
| CVE-2023-42820 | HIGH | jumpserver | Jumpserver 随机数种子泄露导致账户劫持漏洞 (CVE-2023-42820) | middleware/jumpserver/CVE-2023-42820.md |
| JUMPSERVER-UNAUTH-RCE | CRITICAL | jumpserver | JumpServer 未授权接口远程命令执行漏洞 | middleware/jumpserver/JUMPSERVER-UNAUTH-RCE.md |
| JUPYTER-NOTEBOOK-RCE | CRITICAL | jupyter | Jupyter Notebook 未授权访问RCE漏洞 | middleware/jupyter/JUPYTER-NOTEBOOK-RCE.md |
| CVE-2023-25194 | CRITICAL | kafka | Apache Kafka Clients JNDI注入RCE漏洞 (CVE-2023-25194) | middleware/kafka/CVE-2023-25194.md |
| CVE-2018-17246 | MEDIUM | kibana | Kibana Local File Inclusion漏洞 (CVE-2018-17246) | middleware/kibana/CVE-2018-17246.md |
| CVE-2019-7609 | CRITICAL | kibana | Kibana 原型链污染RCE漏洞 (CVE-2019-7609) | middleware/kibana/CVE-2019-7609.md |
| CVE-2020-7012 | CRITICAL | kibana | Kibana upgrade-assistant 原型链污染RCE漏洞 (CVE-2020-7012) | middleware/kibana/CVE-2020-7012.md |
| KIBANA-RCE | CRITICAL | kibana | Kibana 远程代码执行与SSRF漏洞 | middleware/kibana/KIBANA-RCE.md |
| KKFILEVIEW-4.3-ZIPSLIP-RCE | CRITICAL | kkfileview | kkFileView ZipSlip 远程命令执行漏洞 | middleware/kkfileview/KKFILEVIEW-4.3-ZIPSLIP-RCE.md |
| CVE-2020-11710 | CRITICAL | kong | Kong - Admin API 未授权访问 | middleware/kong/CVE-2020-11710.md |
| KONG-ADMIN-SSRF | CRITICAL | kong | Kong - Admin API SSRF 代理攻击 | middleware/kong/KONG-ADMIN-SSRF.md |
| CVE-2025-1087 | CRITICAL | kong-insomnia | Kong Insomnia - Nunjucks 模板注入 RCE | middleware/kong-insomnia/CVE-2025-1087.md |
| CVE-2021-42192 | HIGH | konga | Konga - 普通用户权限提升至管理员 | middleware/konga/CVE-2021-42192.md |
| K8S-APISERVER-UNAUTH | CRITICAL | kubernetes | Kubernetes API Server 未授权访问 | middleware/kubernetes/K8S-APISERVER-UNAUTH.md |
| K8S-ETCD-UNAUTH | CRITICAL | kubernetes | Kubernetes etcd 未授权访问数据泄露 | middleware/kubernetes/K8S-ETCD-UNAUTH.md |
| K8S-KUBELET-UNAUTH | CRITICAL | kubernetes | Kubernetes Kubelet 未授权访问RCE | middleware/kubernetes/K8S-KUBELET-UNAUTH.md |
| CVE-2020-13925 | CRITICAL | kylin | Apache Kylin 远程命令执行（CVE-2020-13925） | middleware/kylin/CVE-2020-13925.md |
| CVE-2021-3129 | CRITICAL | laravel | Laravel Ignition 代码执行漏洞 (CVE-2021-3129) | middleware/laravel/CVE-2021-3129.md |
| CVE-2022-40734 | HIGH | laravel | Laravel Filemanager 任意文件读取漏洞 (CVE-2022-40734) | middleware/laravel/CVE-2022-40734.md |
| LARAVEL-ENV-LEAK | HIGH | laravel | Laravel .env 配置文件泄露漏洞 | middleware/laravel/LARAVEL-ENV-LEAK.md |
| CVE-2023-38633 | MEDIUM | librsvg | librsvg XInclude 文件包含漏洞 (CVE-2023-38633) | middleware/librsvg/CVE-2023-38633.md |
| CVE-2018-10933 | CRITICAL | libssh | libssh 服务端权限认证绕过漏洞 (CVE-2018-10933) | middleware/libssh/CVE-2018-10933.md |
| CVE-2020-7961 | CRITICAL | liferay-portal | Liferay Portal CE 反序列化RCE漏洞 (CVE-2020-7961) | middleware/liferay-portal/CVE-2020-7961.md |
| CVE-2025-54068 | CRITICAL | livewire | Livewire 组件属性水合RCE漏洞 (CVE-2025-54068) | middleware/livewire/CVE-2025-54068.md |
| CVE-2017-5645 | CRITICAL | log4j | Apache Log4j TCP Server 反序列化RCE漏洞 (CVE-2017-5645) | middleware/log4j/CVE-2017-5645.md |
| CVE-2021-44228 | CRITICAL | log4j | Apache Log4j2 RCE (Log4Shell) | middleware/log4j/CVE-2021-44228.md |
| MAGENTO-2.2-SQLI | HIGH | magento | Magento 2.2 SQL注入漏洞 | middleware/magento/MAGENTO-2.2-SQLI.md |
| CVE-2021-45788 | HIGH | metersphere | MeterSphere v1.15.4 认证用户SQL注入漏洞（CVE-2021-45788） | middleware/metersphere/CVE-2021-45788.md |
| METERSPHERE-PLUGIN-RCE | CRITICAL | metersphere | MeterSphere 插件接口未授权访问及远程代码执行 | middleware/metersphere/METERSPHERE-PLUGIN-RCE.md |
| CVE-2018-18778 | MEDIUM | mini_httpd | mini_httpd 任意文件读取漏洞（CVE-2018-18778） | middleware/mini_httpd/CVE-2018-18778.md |
| CVE-2021-21287 | HIGH | minio | MinIO SSRF 漏洞 (CVE-2021-21287) | middleware/minio/CVE-2021-21287.md |
| CVE-2023-28432 | MEDIUM | minio | MinIO集群模式信息泄露漏洞（CVE-2023-28432） | middleware/minio/CVE-2023-28432.md |
| CVE-2023-28434 | HIGH | minio | MinIO PostPolicyBucket 元数据校验绕过导致越权对象写入（CVE-2023-28434） | middleware/minio/CVE-2023-28434.md |
| MOJARRA-JSF-VIEWSTATE-DESERIALIZATION | CRITICAL | mojarra | Mojarra JSF ViewState 反序列化漏洞 | middleware/mojarra/MOJARRA-JSF-VIEWSTATE-DESERIALIZATION.md |
| CVE-2019-10758 | CRITICAL | mongo-express | Mongo Express 远程代码执行漏洞（CVE-2019-10758） | middleware/mongo-express/CVE-2019-10758.md |
| MSSQL-CLR-RCE | CRITICAL | mssql | MSSQL - CLR Assembly 远程代码执行 | middleware/mssql/MSSQL-CLR-RCE.md |
| MSSQL-FILE-RW | HIGH | mssql | MSSQL - 文件读写操作 | middleware/mssql/MSSQL-FILE-RW.md |
| MSSQL-NTLM-RELAY | HIGH | mssql | MSSQL - NTLM Hash 窃取（xp_dirtree） | middleware/mssql/MSSQL-NTLM-RELAY.md |
| MSSQL-XPCMDSHELL-RCE | CRITICAL | mssql | MSSQL - xp_cmdshell/OLE Automation/Agent Job 命令执行 | middleware/mssql/MSSQL-XPCMDSHELL-RCE.md |
| CVE-2012-2122 | HIGH | mysql | Mysql 身份认证绕过漏洞（CVE-2012-2122） | middleware/mysql/CVE-2012-2122.md |
| MYSQL-UDF-RCE | CRITICAL | mysql | MySQL - UDF 提权与文件操作 | middleware/mysql/MYSQL-UDF-RCE.md |
| CVE-2025-68613 | CRITICAL | n8n | n8n表达式沙箱逃逸至RCE漏洞（CVE-2025-68613） | middleware/n8n/CVE-2025-68613.md |
| CVE-2026-21858 | CRITICAL | n8n | n8n Content-Type混淆任意文件读取至RCE漏洞（CVE-2026-21858） | middleware/n8n/CVE-2026-21858.md |
| N8N-AUTH-BYPASS-RCE | CRITICAL | n8n | n8n 认证绕过与代码执行漏洞 | middleware/n8n/N8N-AUTH-BYPASS-RCE.md |
| CVE-2021-29441 | CRITICAL | nacos | Nacos - User-Agent Authentication Bypass | middleware/nacos/CVE-2021-29441.md |
| CVE-2021-29442 | HIGH | nacos | Nacos - Derby SQL Unauthenticated Access | middleware/nacos/CVE-2021-29442.md |
| NACOS-AUTH-BYPASS | CRITICAL | nacos | Nacos 认证绕过漏洞 | middleware/nacos/NACOS-AUTH-BYPASS.md |
| NACOS-DESER-RCE | CRITICAL | nacos | Nacos Raft反序列化与Hessian2远程代码执行 | middleware/nacos/NACOS-DESER-RCE.md |
| QVD-2023-13065 | CRITICAL | nacos | Nacos - JRaft Hessian Deserialization RCE | middleware/nacos/QVD-2023-13065.md |
| QVD-2023-1655789 | CRITICAL | nacos | Nacos - JWT Default Secret Key Authentication Bypass | middleware/nacos/QVD-2023-1655789.md |
| QVD-2024-26473 | CRITICAL | nacos | Nacos - Derby Race Condition RCE | middleware/nacos/QVD-2024-26473.md |
| CVE-2016-9565 | CRITICAL | nagios | Nagios Core RSS 注入远程代码执行（CVE-2016-9565） | middleware/nagios/CVE-2016-9565.md |
| CVE-2021-34371 | CRITICAL | neo4j | Neo4j Shell Server 反序列化漏洞（CVE-2021-34371） | middleware/neo4j/CVE-2021-34371.md |
| CVE-2025-29927 | CRITICAL | next.js | Next.js 中间件鉴权绕过漏洞 (CVE-2025-29927) | middleware/next.js/CVE-2025-29927.md |
| CVE-2019-5475 | CRITICAL | nexus | Sonatype Nexus Repository Manager 远程命令执行漏洞（CVE-2019-5475） | middleware/nexus/CVE-2019-5475.md |
| CVE-2019-7238 | CRITICAL | nexus | Nexus Repository Manager 3 远程命令执行漏洞（CVE-2019-7238） | middleware/nexus/CVE-2019-7238.md |
| CVE-2020-10199 | CRITICAL | nexus | Nexus Repository Manager 3 远程命令执行漏洞（CVE-2020-10199） | middleware/nexus/CVE-2020-10199.md |
| CVE-2020-10204 | CRITICAL | nexus | Nexus Repository Manager 3 远程命令执行漏洞（CVE-2020-10204） | middleware/nexus/CVE-2020-10204.md |
| CVE-2020-11444 | HIGH | nexus | Nexus Repository Manager 3 权限提升（CVE-2020-11444） | middleware/nexus/CVE-2020-11444.md |
| CVE-2024-4956 | HIGH | nexus | Nexus Repository Manager 3 未授权目录穿越漏洞（CVE-2024-4956） | middleware/nexus/CVE-2024-4956.md |
| CVE-2013-4547 | CRITICAL | nginx | Nginx 文件名逻辑漏洞（CVE-2013-4547） | middleware/nginx/CVE-2013-4547.md |
| CVE-2017-7529 | MEDIUM | nginx | Nginx越界读取缓存漏洞（CVE-2017-7529） | middleware/nginx/CVE-2017-7529.md |
| CVE-2021-23017 | HIGH | nginx | Nginx DNS Resolver Off-by-One 堆溢出（CVE-2021-23017） | middleware/nginx/CVE-2021-23017.md |
| NGINX-ALIAS-TRAVERSAL | HIGH | nginx | Nginx Alias 目录穿越漏洞 | middleware/nginx/NGINX-ALIAS-TRAVERSAL.md |
| NGINX-CRLF-INJECTION | MEDIUM | nginx | Nginx CRLF 注入漏洞 | middleware/nginx/NGINX-CRLF-INJECTION.md |
| NGINX-INSECURE-CONFIGURATION | MEDIUM | nginx | Nginx 配置错误导致漏洞 | middleware/nginx/NGINX-INSECURE-CONFIGURATION.md |
| NGINX-PARSING-VULNERABILITY | CRITICAL | nginx | Nginx 解析漏洞 | middleware/nginx/NGINX-PARSING-VULNERABILITY.md |
| CVE-2026-27944 | CRITICAL | nginx-ui | Nginx UI 未授权备份下载与密钥泄露 (CVE-2026-27944) | middleware/nginx-ui/CVE-2026-27944.md |
| CVE-2026-33032 | CRITICAL | nginx-ui | Nginx UI 未授权 MCP 配置接管 (CVE-2026-33032) | middleware/nginx-ui/CVE-2026-33032.md |
| CVE-2017-14849 | MEDIUM | node | Node.js 8.5.0 目录穿越漏洞（CVE-2017-14849） | middleware/node/CVE-2017-14849.md |
| CVE-2017-16082 | CRITICAL | node | node-postgres 代码执行漏洞（CVE-2017-16082） | middleware/node/CVE-2017-16082.md |
| CVE-2017-5941 | CRITICAL | nodejs | Node.js node-serialize 反序列化远程代码执行（CVE-2017-5941） | middleware/nodejs/CVE-2017-5941.md |
| CVE-2021-21315 | HIGH | nodejs | Node.js systeminformation 命令注入（CVE-2021-21315） | middleware/nodejs/CVE-2021-21315.md |
| CVE-2019-16278 | CRITICAL | nostromo | Nostromo nhttpd 目录遍历远程代码执行（CVE-2019-16278） | middleware/nostromo/CVE-2019-16278.md |
| CVE-2018-16341 | CRITICAL | nuxeo | Nuxeo Platform SSTI 远程代码执行（CVE-2018-16341） | middleware/nuxeo/CVE-2018-16341.md |
| CVE-2018-8033 | HIGH | ofbiz | Apache OFBiz XXE 漏洞（CVE-2018-8033） | middleware/ofbiz/CVE-2018-8033.md |
| CVE-2020-9496 | CRITICAL | ofbiz | Apache OfBiz 反序列化命令执行漏洞（CVE-2020-9496） | middleware/ofbiz/CVE-2020-9496.md |
| CVE-2021-26295 | CRITICAL | ofbiz | Apache OFBiz RMI 反序列化远程代码执行漏洞 | middleware/ofbiz/CVE-2021-26295.md |
| CVE-2021-29200 | CRITICAL | ofbiz | Apache OFBiz RMI 反序列化绕过远程代码执行漏洞 | middleware/ofbiz/CVE-2021-29200.md |
| CVE-2021-30128 | CRITICAL | ofbiz | Apache OFBiz 反序列化远程代码执行漏洞 | middleware/ofbiz/CVE-2021-30128.md |
| CVE-2023-49070 | CRITICAL | ofbiz | Apache OfBiz 反序列化命令执行漏洞（CVE-2023-49070） | middleware/ofbiz/CVE-2023-49070.md |
| CVE-2023-51467 | CRITICAL | ofbiz | Apache OFBiz 鉴权绕过导致命令执行（CVE-2023-51467） | middleware/ofbiz/CVE-2023-51467.md |
| CVE-2024-36104 | CRITICAL | ofbiz | Apache OFBiz 目录遍历致代码执行漏洞 (CVE-2024-36104) | middleware/ofbiz/CVE-2024-36104.md |
| CVE-2024-38856 | CRITICAL | ofbiz | Apache OFBiz 身份验证绕过导致远程代码执行 (CVE-2024-38856) | middleware/ofbiz/CVE-2024-38856.md |
| CVE-2024-45195 | CRITICAL | ofbiz | Apache OFBiz 身份验证绕过导致远程代码执行（CVE-2024-45195） | middleware/ofbiz/CVE-2024-45195.md |
| CVE-2024-45507 | CRITICAL | ofbiz | Apache OFBiz SSRF 和远程代码执行漏洞（CVE-2024-45507） | middleware/ofbiz/CVE-2024-45507.md |
| CVE-2021-35464 | CRITICAL | openam | ForgeRock OpenAM Java 反序列化远程代码执行（CVE-2021-35464） | middleware/openam/CVE-2021-35464.md |
| CVE-2023-32315 | HIGH | openfire | Openfire管理后台认证绕过漏洞（CVE-2023-32315） | middleware/openfire/CVE-2023-32315.md |
| CVE-2020-7247 | CRITICAL | opensmtpd | OpenSMTPD 远程命令执行漏洞 (CVE-2020-7247) | middleware/opensmtpd/CVE-2020-7247.md |
| CVE-2018-15473 | MEDIUM | openssh | OpenSSH 用户名枚举漏洞（CVE-2018-15473） | middleware/openssh/CVE-2018-15473.md |
| CVE-2014-0160 | CRITICAL | openssl | OpenSSL 心脏出血内存泄露漏洞（CVE-2014-0160） | middleware/openssl/CVE-2014-0160.md |
| CVE-2022-0778 | MEDIUM | openssl | OpenSSL无限循环DOS漏洞（CVE-2022-0778） | middleware/openssl/CVE-2022-0778.md |
| CVE-2020-35476 | CRITICAL | opentsdb | OpenTSDB 命令注入漏洞（CVE-2020-35476） | middleware/opentsdb/CVE-2020-35476.md |
| CVE-2023-25826 | CRITICAL | opentsdb | OpenTSDB 命令注入漏洞（CVE-2023-25826） | middleware/opentsdb/CVE-2023-25826.md |
| CVE-2023-49103 | HIGH | owncloud | ownCloud graphapi信息泄露漏洞（CVE-2023-49103） | middleware/owncloud/CVE-2023-49103.md |
| CVE-2024-4367 | HIGH | pdfjs | PDF.js 任意JavaScript代码执行（CVE-2024-4367） | middleware/pdfjs/CVE-2024-4367.md |
| CVE-2022-4223 | CRITICAL | pgadmin | pgAdmin <= 6.16 无授权远程命令执行漏洞（CVE-2022-4223） | middleware/pgadmin/CVE-2022-4223.md |
| CVE-2023-5002 | CRITICAL | pgadmin | pgAdmin <= 7.6 后台远程命令执行漏洞（CVE-2023-5002） | middleware/pgadmin/CVE-2023-5002.md |
| CVE-2025-13780 | CRITICAL | pgadmin | pgAdmin4 <= 9.10 后台Restore工具命令注入漏洞（CVE-2025-13780） | middleware/pgadmin/CVE-2025-13780.md |
| CVE-2025-2945 | CRITICAL | pgadmin | pgAdmin4 <= 9.1 后台远程代码执行漏洞 (CVE-2025-2945) | middleware/pgadmin/CVE-2025-2945.md |
| CVE-2012-1823 | CRITICAL | php | PHP-CGI 远程代码执行漏洞（CVE-2012-1823） | middleware/php/CVE-2012-1823.md |
| CVE-2018-19518 | HIGH | php | PHP IMAP 远程命令执行漏洞（CVE-2018-19518） | middleware/php/CVE-2018-19518.md |
| CVE-2019-11043 | CRITICAL | php | PHP-FPM 远程代码执行漏洞（CVE-2019-11043） | middleware/php/CVE-2019-11043.md |
| CVE-2024-2961 | HIGH | php | PHP利用GNU C Iconv将文件读取变成RCE（CVE-2024-2961） | middleware/php/CVE-2024-2961.md |
| CVE-2024-4577 | CRITICAL | php | PHP CGI Windows 平台远程代码执行漏洞 (CVE-2024-4577) | middleware/php/CVE-2024-4577.md |
| PHP-8.1-BACKDOOR | CRITICAL | php | PHP 8.1.0-dev User-Agentt 后门导致远程代码执行漏洞 | middleware/php/PHP-8.1-BACKDOOR.md |
| PHP-FPM-FASTCGI-UNAUTHORIZED | CRITICAL | php | PHP-FPM FastCGI 未授权访问漏洞 | middleware/php/PHP-FPM-FASTCGI-UNAUTHORIZED.md |
| PHP-INCLUSION | CRITICAL | php | PHP文件包含漏洞（利用phpinfo） | middleware/php/PHP-INCLUSION.md |
| PHP-XDEBUG-RCE | HIGH | php | PHP XDebug远程调试导致代码执行漏洞 | middleware/php/PHP-XDEBUG-RCE.md |
| PHP-XXE | MEDIUM | php | PHP XML 外部实体注入漏洞（XXE） | middleware/php/PHP-XXE.md |
| CVE-2017-5223 | MEDIUM | phpmailer | PHPMailer 任意文件读取漏洞（CVE-2017-5223） | middleware/phpmailer/CVE-2017-5223.md |
| CVE-2016-5734 | CRITICAL | phpmyadmin | phpMyAdmin 4.0.x—4.6.2 远程代码执行漏洞（CVE-2016-5734） | middleware/phpmyadmin/CVE-2016-5734.md |
| CVE-2018-12613 | HIGH | phpmyadmin | phpmyadmin 4.8.1 远程文件包含漏洞（CVE-2018-12613） | middleware/phpmyadmin/CVE-2018-12613.md |
| PHPMYADMIN-WOOYUN-2016-199433 | CRITICAL | phpmyadmin | phpmyadmin scripts/setup.php 反序列化漏洞（WooYun-2016-199433） | middleware/phpmyadmin/PHPMYADMIN-WOOYUN-2016-199433.md |
| CVE-2017-9841 | CRITICAL | phpunit | phpunit 远程代码执行漏洞（CVE-2017-9841） | middleware/phpunit/CVE-2017-9841.md |
| CVE-2021-4034 | CRITICAL | polkit | Polkit `pkexec` 权限提升漏洞（CVE-2021-4034） | middleware/polkit/CVE-2021-4034.md |
| CVE-2018-12678 | CRITICAL | portainer | Portainer - CRLF注入Request Splitting SSRF至RCE | middleware/portainer/CVE-2018-12678.md |
| CVE-2024-29296 | MEDIUM | portainer | Portainer - 基于响应时间差的用户枚举 | middleware/portainer/CVE-2024-29296.md |
| PORTAINER-DEFAULT-CREDS | CRITICAL | portainer | Portainer - 默认凭据与弱口令 | middleware/portainer/PORTAINER-DEFAULT-CREDS.md |
| PORTAINER-DOCKER-API-RCE | CRITICAL | portainer | Portainer - 认证后Docker API特权容器逃逸RCE | middleware/portainer/PORTAINER-DOCKER-API-RCE.md |
| CVE-2018-1058 | HIGH | postgres | PostgreSQL 提权漏洞（CVE-2018-1058） | middleware/postgres/CVE-2018-1058.md |
| CVE-2019-9193 | CRITICAL | postgres | PostgreSQL 高权限命令执行漏洞（CVE-2019-9193） | middleware/postgres/CVE-2019-9193.md |
| POSTGRES-FILE-RW | HIGH | postgres | PostgreSQL - 文件读写操作 | middleware/postgres/POSTGRES-FILE-RW.md |
| POSTGRES-NTLM-RELAY | HIGH | postgres | PostgreSQL - NTLM Hash 窃取（UNC路径） | middleware/postgres/POSTGRES-NTLM-RELAY.md |
| POSTGRES-UDF-RCE | CRITICAL | postgres | PostgreSQL - UDF/PL扩展远程代码执行 | middleware/postgres/POSTGRES-UDF-RCE.md |
| PYDASH-CVE-2023-26145 | CRITICAL | pydash | PyDash 原型链污染命令注入漏洞 (CVE-2023-26145) | middleware/pydash/PYDASH-CVE-2023-26145.md |
| CVE-2024-23334 | MEDIUM | python | aiohttp 目录遍历漏洞（CVE-2024-23334） | middleware/python/CVE-2024-23334.md |
| PYTHON-PIL-CVE-2017-8291 | CRITICAL | python | Python PIL 远程命令执行漏洞（CVE-2017-8291/GhostButt） | middleware/python/PYTHON-PIL-CVE-2017-8291.md |
| PYTHON-PIL-CVE-2018-16509 | CRITICAL | python | Python PIL/Pillow 远程命令执行漏洞 (CVE-2018-16509) | middleware/python/PYTHON-PIL-CVE-2018-16509.md |
| PYTHON-UNPICKLE | CRITICAL | python | Python Unpickle 反序列化远程代码执行漏洞 | middleware/python/PYTHON-UNPICKLE.md |
| RABBITMQ-DEFAULT-CREDS | CRITICAL | rabbitmq | RabbitMQ - 默认凭据 guest/guest 未授权访问 | middleware/rabbitmq/RABBITMQ-DEFAULT-CREDS.md |
| RABBITMQ-ERLANG-COOKIE-RCE | CRITICAL | rabbitmq | RabbitMQ - Erlang Cookie 泄露远程代码执行 | middleware/rabbitmq/RABBITMQ-ERLANG-COOKIE-RCE.md |
| RABBITMQ-MGMT-API-UNAUTH | HIGH | rabbitmq | RabbitMQ - Management API 未授权访问 | middleware/rabbitmq/RABBITMQ-MGMT-API-UNAUTH.md |
| RABBITMQ-PROTOCOL-ATTACKS | HIGH | rabbitmq | RabbitMQ - MQTT匿名访问与Docker环境利用 | middleware/rabbitmq/RABBITMQ-PROTOCOL-ATTACKS.md |
| CVE-2018-3760 | MEDIUM | rails | Ruby On Rails 路径穿越漏洞（CVE-2018-3760） | middleware/rails/CVE-2018-3760.md |
| CVE-2019-5418 | MEDIUM | rails | Ruby on Rails 路径穿越与任意文件读取漏洞（CVE-2019-5418） | middleware/rails/CVE-2019-5418.md |
| CVE-2019-5420 | CRITICAL | rails | Ruby on Rails 开发模式远程代码执行（CVE-2019-5420） | middleware/rails/CVE-2019-5420.md |
| CVE-2025-55182 | CRITICAL | react | React Server Components Flight 协议反序列化代码执行（CVE-2025-55182） | middleware/react/CVE-2025-55182.md |
| CVE-2022-0543 | CRITICAL | redis | Redis Lua沙盒绕过命令执行（CVE-2022-0543） | middleware/redis/CVE-2022-0543.md |
| REDIS-MASTER-SLAVE-RCE | CRITICAL | redis | Redis 主从复制远程代码执行漏洞 | middleware/redis/REDIS-MASTER-SLAVE-RCE.md |
| REDIS-UNAUTH-WRITE-RCE | CRITICAL | redis | Redis - 未授权写文件RCE（Webshell/SSH密钥/Crontab） | middleware/redis/REDIS-UNAUTH-WRITE-RCE.md |
| CVE-2021-22911 | HIGH | rocketchat | Rocket Chat 前台 NoSQL 盲注漏洞（CVE-2021-22911） | middleware/rocketchat/CVE-2021-22911.md |
| CVE-2023-33246 | CRITICAL | rocketmq | Apache RocketMQ Broker 远程命令执行漏洞（CVE-2023-33246） | middleware/rocketmq/CVE-2023-33246.md |
| CVE-2023-37582 | CRITICAL | rocketmq | Apache RocketMQ NameServer 任意文件写入漏洞（CVE-2023-37582） | middleware/rocketmq/CVE-2023-37582.md |
| CVE-2022-31137 | CRITICAL | roxy-wi | Roxy-WI options.py 远程命令执行漏洞 | middleware/roxy-wi/CVE-2022-31137.md |
| RSYNC-COMMON | CRITICAL | rsync | Rsync 未授权访问漏洞 | middleware/rsync/RSYNC-COMMON.md |
| CVE-2017-17405 | CRITICAL | ruby | Ruby Net::FTP 模块命令注入漏洞（CVE-2017-17405） | middleware/ruby/CVE-2017-17405.md |
| CVE-2020-11651 | CRITICAL | saltstack | SaltStack 信息泄露导致权限提升漏洞（CVE-2020-11651） | middleware/saltstack/CVE-2020-11651.md |
| CVE-2020-11652 | HIGH | saltstack | SaltStack 任意文件读写漏洞（CVE-2020-11652） | middleware/saltstack/CVE-2020-11652.md |
| CVE-2020-16846 | CRITICAL | saltstack | SaltStack 命令注入漏洞（CVE-2020-16846） | middleware/saltstack/CVE-2020-16846.md |
| CVE-2021-25281 | CRITICAL | saltstack | SaltStack salt-api 未授权远程代码执行漏洞 | middleware/saltstack/CVE-2021-25281.md |
| CVE-2021-31607 | MEDIUM | saltstack | SaltStack Minion Snapper 命令注入漏洞 | middleware/saltstack/CVE-2021-31607.md |
| CVE-2017-7494 | CRITICAL | samba | Samba 远程命令执行漏洞（CVE-2017-7494） | middleware/samba/CVE-2017-7494.md |
| SCRAPY-SCRAPYD-UNACC | CRITICAL | scrapy | scrapyd 未授权访问导致远程代码执行漏洞 | middleware/scrapy/SCRAPY-SCRAPYD-UNACC.md |
| CVE-2020-1947 | CRITICAL | shardingsphere | Apache ShardingSphere SnakeYAML 反序列化远程代码执行（CVE-2020-1947） | middleware/shardingsphere/CVE-2020-1947.md |
| CVE-2010-3863 | HIGH | shiro | Apache Shiro 认证绕过漏洞（CVE-2010-3863） | middleware/shiro/CVE-2010-3863.md |
| CVE-2016-4437 | CRITICAL | shiro | Apache Shiro 1.2.4 反序列化漏洞（CVE-2016-4437） | middleware/shiro/CVE-2016-4437.md |
| CVE-2020-11989 | HIGH | shiro | Apache Shiro 权限绕过漏洞（CVE-2020-11989） | middleware/shiro/CVE-2020-11989.md |
| CVE-2020-13933 | HIGH | shiro | Apache Shiro 认证绕过漏洞 | middleware/shiro/CVE-2020-13933.md |
| CVE-2020-1957 | CRITICAL | shiro | Apache Shiro 认证绕过 | middleware/shiro/CVE-2020-1957.md |
| Shiro-550 | CRITICAL | shiro | Apache Shiro RememberMe 反序列化 RCE | middleware/shiro/Shiro-550.md |
| CNVD-2020-26585 | CRITICAL | showdoc | ShowDoc 前台任意文件上传漏洞（CNVD-2020-26585） | middleware/showdoc/CNVD-2020-26585.md |
| SHOWDOC-3.2.5-SQLI | HIGH | showdoc | ShowDoc SQL注入漏洞 | middleware/showdoc/SHOWDOC-3.2.5-SQLI.md |
| CVE-2020-9483 | HIGH | skywalking | Apache SkyWalking SQL 注入（CVE-2020-9483） | middleware/skywalking/CVE-2020-9483.md |
| SKYWALKING-8.3.0-SQLI | HIGH | skywalking | Apache SkyWalking SQL注入漏洞 | middleware/skywalking/SKYWALKING-8.3.0-SQLI.md |
| CNVD-2023-27598 | CRITICAL | solr | Apache Solr ConfigSets API 未授权上传导致远程代码执行 | middleware/solr/CNVD-2023-27598.md |
| CVE-2017-12629-RCE | CRITICAL | solr | Apache Solr 远程命令执行漏洞（CVE-2017-12629） | middleware/solr/CVE-2017-12629-RCE.md |
| CVE-2017-12629-XXE | HIGH | solr | Apache Solr XML外部实体注入漏洞（CVE-2017-12629） | middleware/solr/CVE-2017-12629-XXE.md |
| CVE-2019-0193 | CRITICAL | solr | Apache Solr DataImportHandler 远程命令执行漏洞（CVE-2019-0193） | middleware/solr/CVE-2019-0193.md |
| CVE-2019-12409 | CRITICAL | solr | Apache Solr JMX 服务远程代码执行漏洞 | middleware/solr/CVE-2019-12409.md |
| CVE-2019-17558 | CRITICAL | solr | Apache Solr Velocity 模板注入远程代码执行漏洞（CVE-2019-17558） | middleware/solr/CVE-2019-17558.md |
| CVE-2020-13957 | CRITICAL | solr | Apache Solr ConfigSet API 未授权上传远程代码执行漏洞 | middleware/solr/CVE-2020-13957.md |
| CVE-2021-27905 | HIGH | solr | Apache Solr Replication Handler SSRF 漏洞 | middleware/solr/CVE-2021-27905.md |
| CVE-2024-45216 | CRITICAL | solr | Apache Solr 认证绕过漏洞 | middleware/solr/CVE-2024-45216.md |
| SOLR-LOG4J-RCE | CRITICAL | solr | Apache Solr Log4j 组件远程代码执行漏洞 | middleware/solr/SOLR-LOG4J-RCE.md |
| SOLR-REMOTE-STREAMING-FILEREAD | HIGH | solr | Apache Solr RemoteStreaming 任意文件读取和SSRF漏洞 | middleware/solr/SOLR-REMOTE-STREAMING-FILEREAD.md |
| CVE-2020-27986 | HIGH | sonarqube | SonarQube API 敏感信息泄露漏洞 | middleware/sonarqube/CVE-2020-27986.md |
| CVE-2020-9480 | CRITICAL | spark | Apache Spark 远程代码执行漏洞（CVE-2020-9480） | middleware/spark/CVE-2020-9480.md |
| CVE-2022-33891 | CRITICAL | spark | Apache Spark doAs 远程命令执行漏洞 (CVE-2022-33891) | middleware/spark/CVE-2022-33891.md |
| SPARK-UNACC | CRITICAL | spark | Apache Spark 未授权访问导致远程代码执行漏洞 | middleware/spark/SPARK-UNACC.md |
| CVE-2016-4977 | CRITICAL | spring | Spring Security OAuth2 远程命令执行漏洞（CVE-2016-4977） | middleware/spring/CVE-2016-4977.md |
| CVE-2017-4971 | CRITICAL | spring | Spring WebFlow 远程代码执行漏洞（CVE-2017-4971） | middleware/spring/CVE-2017-4971.md |
| CVE-2017-8046 | CRITICAL | spring | Spring Data Rest 远程命令执行漏洞（CVE-2017-8046） | middleware/spring/CVE-2017-8046.md |
| CVE-2018-1270 | CRITICAL | spring | Spring Messaging 远程命令执行漏洞（CVE-2018-1270） | middleware/spring/CVE-2018-1270.md |
| CVE-2018-1273 | CRITICAL | spring | Spring Data Commons 远程命令执行漏洞（CVE-2018-1273） | middleware/spring/CVE-2018-1273.md |
| CVE-2019-3799 | HIGH | spring | Spring Cloud Config 目录遍历漏洞 (CVE-2019-3799) | middleware/spring/CVE-2019-3799.md |
| CVE-2020-5398 | HIGH | spring | Spring Framework RFD 反射型文件下载（CVE-2020-5398） | middleware/spring/CVE-2020-5398.md |
| CVE-2020-5410 | HIGH | spring | Spring Cloud Config Server 目录遍历（CVE-2020-5410） | middleware/spring/CVE-2020-5410.md |
| CVE-2022-22963 | CRITICAL | spring | Spring Cloud Function SpEL表达式命令注入（CVE-2022-22963） | middleware/spring/CVE-2022-22963.md |
| CVE-2022-22965 | CRITICAL | spring | Spring4Shell — Spring Framework ClassLoader RCE (CVE-2022-22965) | middleware/spring/CVE-2022-22965.md |
| CVE-2022-22978 | HIGH | spring | Spring Security RegexRequestMatcher 认证绕过漏洞（CVE-2022-22978） | middleware/spring/CVE-2022-22978.md |
| CVE-2023-34050 | CRITICAL | spring | Spring AMQP 反序列化远程代码执行（CVE-2023-34050） | middleware/spring/CVE-2023-34050.md |
| CVE-2024-38819 | HIGH | spring | Spring Framework WebMvc.fn/WebFlux.fn 目录遍历漏洞 (CVE-2024-38819) | middleware/spring/CVE-2024-38819.md |
| CVE-2021-21234 | HIGH | spring-boot | Spring Boot Actuator Logview 目录遍历漏洞 | middleware/spring-boot/CVE-2021-21234.md |
| SPRING-CLOUD-FUNCTION-SPEL | CRITICAL | spring-cloud | Spring Cloud Function SpEL 远程命令执行漏洞 (CVE-2022-22963) | middleware/spring-cloud/SPRING-CLOUD-FUNCTION-SPEL.md |
| S2-001 | CRITICAL | struts2 | Struts2 S2-001 远程代码执行漏洞 | middleware/struts2/S2-001.md |
| S2-005 | CRITICAL | struts2 | Struts2 S2-005 远程代码执行漏洞 | middleware/struts2/S2-005.md |
| S2-007 | CRITICAL | struts2 | Struts2 S2-007 远程代码执行漏洞 | middleware/struts2/S2-007.md |
| S2-008 | CRITICAL | struts2 | Struts2 S2-008 远程代码执行漏洞 | middleware/struts2/S2-008.md |
| S2-009 | CRITICAL | struts2 | Struts2 S2-009 远程代码执行漏洞 | middleware/struts2/S2-009.md |
| S2-012 | CRITICAL | struts2 | Struts2 S2-012 远程代码执行漏洞 | middleware/struts2/S2-012.md |
| S2-013 | CRITICAL | struts2 | Struts2 S2-013/S2-014 远程代码执行漏洞 | middleware/struts2/S2-013.md |
| S2-015 | CRITICAL | struts2 | Struts2 S2-015 远程代码执行漏洞 | middleware/struts2/S2-015.md |
| S2-016 | CRITICAL | struts2 | Struts2 S2-016 远程代码执行漏洞 | middleware/struts2/S2-016.md |
| S2-029 | HIGH | struts2 | Struts2 S2-029 OGNL 注入远程代码执行（CVE-2016-0785） | middleware/struts2/S2-029.md |
| S2-032 | CRITICAL | struts2 | Struts2 S2-032 远程代码执行漏洞（CVE-2016-3081） | middleware/struts2/S2-032.md |
| S2-033 | CRITICAL | struts2 | Struts2 S2-033 REST 插件 OGNL 注入远程代码执行（CVE-2016-3087） | middleware/struts2/S2-033.md |
| S2-037 | CRITICAL | struts2 | Struts2 S2-037 REST 插件 OGNL 注入远程代码执行（CVE-2016-4438） | middleware/struts2/S2-037.md |
| S2-045 | CRITICAL | struts2 | Struts2 S2-045 远程代码执行漏洞（CVE-2017-5638） | middleware/struts2/S2-045.md |
| S2-046 | CRITICAL | struts2 | Struts2 S2-046 远程代码执行漏洞（CVE-2017-5638） | middleware/struts2/S2-046.md |
| S2-048 | CRITICAL | struts2 | Struts2 S2-048 远程代码执行漏洞 | middleware/struts2/S2-048.md |
| S2-052 | CRITICAL | struts2 | Struts2 S2-052 远程代码执行漏洞 | middleware/struts2/S2-052.md |
| S2-053 | CRITICAL | struts2 | Struts2 S2-053 远程代码执行漏洞 | middleware/struts2/S2-053.md |
| S2-057 | CRITICAL | struts2 | Struts2 S2-057 远程命令执行漏洞（CVE-2018-11776） | middleware/struts2/S2-057.md |
| S2-059 | CRITICAL | struts2 | Struts2 S2-059 远程代码执行漏洞（CVE-2019-0230） | middleware/struts2/S2-059.md |
| S2-061 | CRITICAL | struts2 | Struts2 S2-061 远程命令执行漏洞（CVE-2020-17530） | middleware/struts2/S2-061.md |
| S2-066 | CRITICAL | struts2 | Struts2 S2-066 文件上传路径穿越漏洞（CVE-2023-50164） | middleware/struts2/S2-066.md |
| S2-067 | CRITICAL | struts2 | Struts2 S2-067 文件上传路径穿越漏洞（CVE-2024-53677） | middleware/struts2/S2-067.md |
| CVE-2023-27524 | CRITICAL | superset | Apache Superset 硬编码JWT密钥导致认证绕过漏洞（CVE-2023-27524） | middleware/superset/CVE-2023-27524.md |
| CVE-2023-37941 | CRITICAL | superset | Apache Superset Python Pickle 反序列化导致远程代码执行（CVE-2023-37941） | middleware/superset/CVE-2023-37941.md |
| CVE-2017-11610 | CRITICAL | supervisor | Supervisord XML-RPC 远程命令执行漏洞（CVE-2017-11610） | middleware/supervisor/CVE-2017-11610.md |
| CVE-2023-42793 | CRITICAL | teamcity | JetBrains TeamCity 认证绕过导致远程命令执行漏洞（CVE-2023-42793） | middleware/teamcity/CVE-2023-42793.md |
| CVE-2024-27198 | HIGH | teamcity | JetBrains TeamCity 认证绕过漏洞（CVE-2024-27198） | middleware/teamcity/CVE-2024-27198.md |
| CVE-2020-15906 | CRITICAL | tikiwiki | Tiki Wiki CMS Groupware 认证绕过漏洞（CVE-2020-15906） | middleware/tikiwiki/CVE-2020-15906.md |
| CVE-2017-12615 | CRITICAL | tomcat | Apache Tomcat PUT 方法任意文件写入 | middleware/tomcat/CVE-2017-12615.md |
| CVE-2017-12617 | CRITICAL | tomcat | Apache Tomcat JSP Upload Bypass 远程代码执行漏洞 | middleware/tomcat/CVE-2017-12617.md |
| CVE-2019-0232 | HIGH | tomcat | Apache Tomcat Windows CGI 远程代码执行 (CVE-2019-0232) | middleware/tomcat/CVE-2019-0232.md |
| CVE-2020-11996 | HIGH | tomcat | Apache Tomcat HTTP/2 DoS 漏洞（CVE-2020-11996） | middleware/tomcat/CVE-2020-11996.md |
| CVE-2020-1938 | CRITICAL | tomcat | Apache Tomcat AJP 文件包含漏洞（CVE-2020-1938） | middleware/tomcat/CVE-2020-1938.md |
| CVE-2020-9484 | HIGH | tomcat | Apache Tomcat Session 反序列化远程代码执行（CVE-2020-9484） | middleware/tomcat/CVE-2020-9484.md |
| CVE-2025-24813 | CRITICAL | tomcat | Tomcat 远程代码执行漏洞（CVE-2025-24813） | middleware/tomcat/CVE-2025-24813.md |
| TOMCAT-TOMCAT8 | CRITICAL | tomcat | Tomcat7+ 弱口令 && 后台Getshell漏洞 | middleware/tomcat/TOMCAT-TOMCAT8.md |
| CVE-2020-13942 | CRITICAL | unomi | Apache Unomi 表达式注入远程代码执行漏洞（CVE-2020-13942） | middleware/unomi/CVE-2020-13942.md |
| CVE-2018-7490 | MEDIUM | uwsgi | uWSGI PHP目录穿越漏洞（CVE-2018-7490） | middleware/uwsgi/CVE-2018-7490.md |
| UWSGI-UNACC | HIGH | uwsgi | uWSGI 未授权访问漏洞 | middleware/uwsgi/UWSGI-UNACC.md |
| V2BOARD-1.6-PRIVILEGE-ESCALATION | HIGH | v2board | V2board 1.6.1 提权漏洞 | middleware/v2board/V2BOARD-1.6-PRIVILEGE-ESCALATION.md |
| CVE-2021-21972 | CRITICAL | vcenter | VMware vCenter Server 远程代码执行漏洞 (CVE-2021-21972) | middleware/vcenter/CVE-2021-21972.md |
| CVE-2021-21973 | MEDIUM | vcenter | VMware vCenter Server SSRF 漏洞 (CVE-2021-21973) | middleware/vcenter/CVE-2021-21973.md |
| CVE-2021-22005 | CRITICAL | vcenter | VMware vCenter Server Analytics 任意文件上传 RCE (CVE-2021-22005) | middleware/vcenter/CVE-2021-22005.md |
| VCENTER-FILE-READ | HIGH | vcenter | VMware vCenter Server EAM 任意文件读取漏洞 | middleware/vcenter/VCENTER-FILE-READ.md |
| CNVD-2022-44615 | MEDIUM | vite | Vite开发服务器任意文件读取漏洞（CNVD-2022-44615） | middleware/vite/CNVD-2022-44615.md |
| CVE-2025-30208 | MEDIUM | vite | Vite开发服务器任意文件读取漏洞绕过（CVE-2025-30208） | middleware/vite/CVE-2025-30208.md |
| CVE-2021-21975 | HIGH | vmware | VMware vRealize Operations Manager SSRF 漏洞 | middleware/vmware/CVE-2021-21975.md |
| CVE-2021-21978 | CRITICAL | vmware | VMware View Planner 未授权远程代码执行漏洞 | middleware/vmware/CVE-2021-21978.md |
| CVE-2022-22954 | CRITICAL | vmware | VMware Workspace ONE Access SSTI 远程代码执行漏洞 | middleware/vmware/CVE-2022-22954.md |
| CVE-2014-4210 | HIGH | weblogic | WebLogic SSRF 漏洞 (uddiexplorer) | middleware/weblogic/CVE-2014-4210.md |
| CVE-2016-3510 | CRITICAL | weblogic | WebLogic T3 反序列化漏洞 | middleware/weblogic/CVE-2016-3510.md |
| CVE-2017-10271 | CRITICAL | weblogic | Weblogic wls-wsat XMLDecoder 反序列化漏洞（CVE-2017-10271） | middleware/weblogic/CVE-2017-10271.md |
| CVE-2017-3248 | CRITICAL | weblogic | WebLogic T3 协议反序列化远程代码执行（CVE-2017-3248） | middleware/weblogic/CVE-2017-3248.md |
| CVE-2018-2628 | CRITICAL | weblogic | Weblogic WLS Core Components 反序列化命令执行漏洞（CVE-2018-2628） | middleware/weblogic/CVE-2018-2628.md |
| CVE-2018-2893 | CRITICAL | weblogic | WebLogic T3 反序列化绕过远程代码执行（CVE-2018-2893） | middleware/weblogic/CVE-2018-2893.md |
| CVE-2018-2894 | CRITICAL | weblogic | Weblogic 任意文件上传漏洞（CVE-2018-2894） | middleware/weblogic/CVE-2018-2894.md |
| CVE-2018-3245 | CRITICAL | weblogic | WebLogic T3 反序列化绕过远程代码执行（CVE-2018-3245） | middleware/weblogic/CVE-2018-3245.md |
| CVE-2019-2725 | CRITICAL | weblogic | WebLogic XMLDecoder 反序列化远程代码执行漏洞 | middleware/weblogic/CVE-2019-2725.md |
| CVE-2019-2729 | CRITICAL | weblogic | WebLogic XMLDecoder 反序列化远程代码执行（CVE-2019-2729） | middleware/weblogic/CVE-2019-2729.md |
| CVE-2020-14750 | CRITICAL | weblogic | WebLogic 管理控制台认证绕过（CVE-2020-14750） | middleware/weblogic/CVE-2020-14750.md |
| CVE-2020-14756 | CRITICAL | weblogic | WebLogic Coherence 反序列化远程代码执行漏洞 | middleware/weblogic/CVE-2020-14756.md |
| CVE-2020-14825 | CRITICAL | weblogic | WebLogic T3/IIOP 反序列化远程代码执行（CVE-2020-14825） | middleware/weblogic/CVE-2020-14825.md |
| CVE-2020-14882 | CRITICAL | weblogic | Weblogic 管理控制台未授权远程命令执行漏洞（CVE-2020-14882） | middleware/weblogic/CVE-2020-14882.md |
| CVE-2020-14883 | HIGH | weblogic | WebLogic 管理控制台后台远程代码执行（CVE-2020-14883） | middleware/weblogic/CVE-2020-14883.md |
| CVE-2020-2551 | CRITICAL | weblogic | WebLogic IIOP 协议反序列化远程代码执行（CVE-2020-2551） | middleware/weblogic/CVE-2020-2551.md |
| CVE-2020-2555 | CRITICAL | weblogic | WebLogic Coherence 反序列化远程代码执行（CVE-2020-2555） | middleware/weblogic/CVE-2020-2555.md |
| CVE-2020-2883 | CRITICAL | weblogic | WebLogic Coherence 反序列化绕过远程代码执行（CVE-2020-2883） | middleware/weblogic/CVE-2020-2883.md |
| CVE-2021-2109 | CRITICAL | weblogic | WebLogic LDAP 远程代码执行漏洞 | middleware/weblogic/CVE-2021-2109.md |
| CVE-2021-2394 | CRITICAL | weblogic | WebLogic 二次反序列化漏洞 | middleware/weblogic/CVE-2021-2394.md |
| CVE-2022-21371 | HIGH | weblogic | WebLogic 本地文件包含漏洞 | middleware/weblogic/CVE-2022-21371.md |
| CVE-2023-21839 | CRITICAL | weblogic | WebLogic 未授权远程代码执行漏洞（CVE-2023-21839） | middleware/weblogic/CVE-2023-21839.md |
| WEBLOGIC-SSRF | HIGH | weblogic | Weblogic UDDI Explorer SSRF漏洞 | middleware/weblogic/WEBLOGIC-SSRF.md |
| WEBLOGIC-WEAK-UPLOAD | HIGH | weblogic | WebLogic 弱口令后台部署 War 包 getshell | middleware/weblogic/WEBLOGIC-WEAK-UPLOAD.md |
| WEBLOGIC-WEAK_PASSWORD | CRITICAL | weblogic | WebLogic 弱口令、任意文件读取与远程代码执行 | middleware/weblogic/WEBLOGIC-WEAK_PASSWORD.md |
| CVE-2019-15107 | CRITICAL | webmin | Webmin 远程命令执行漏洞（CVE-2019-15107） | middleware/webmin/CVE-2019-15107.md |
| CVE-2022-29464 | CRITICAL | wso2 | WSO2 任意文件上传远程代码执行漏洞 | middleware/wso2/CVE-2022-29464.md |
| CVE-2020-26258 | HIGH | xstream | XStream SSRF 漏洞（CVE-2020-26258） | middleware/xstream/CVE-2020-26258.md |
| CVE-2020-26259 | HIGH | xstream | XStream 任意文件删除漏洞（CVE-2020-26259） | middleware/xstream/CVE-2020-26259.md |
| CVE-2021-21351 | CRITICAL | xstream | XStream 反序列化命令执行漏洞（CVE-2021-21351） | middleware/xstream/CVE-2021-21351.md |
| CVE-2021-29505 | CRITICAL | xstream | XStream 反序列化命令执行漏洞（CVE-2021-29505） | middleware/xstream/CVE-2021-29505.md |
| YAPI-MONGODB-INJ | CRITICAL | yapi | YApi NoSQL注入导致远程命令执行漏洞 | middleware/yapi/YAPI-MONGODB-INJ.md |
| YAPI-UNACC | CRITICAL | yapi | YApi 开放注册导致RCE | middleware/yapi/YAPI-UNACC.md |
| CVE-2016-10134 | HIGH | zabbix | Zabbix latest.php SQL注入漏洞（CVE-2016-10134） | middleware/zabbix/CVE-2016-10134.md |
| CVE-2017-2824 | CRITICAL | zabbix | Zabbix Server Active Proxy Trapper 命令注入漏洞（CVE-2017-2824） | middleware/zabbix/CVE-2017-2824.md |
| CVE-2020-11800 | CRITICAL | zabbix | Zabbix Server Active Proxy Trapper 命令注入漏洞修复绕过（CVE-2020-11800） | middleware/zabbix/CVE-2020-11800.md |
| CVE-2022-23131 | CRITICAL | zabbix | Zabbix SAML SSO 认证绕过漏洞 | middleware/zabbix/CVE-2022-23131.md |
