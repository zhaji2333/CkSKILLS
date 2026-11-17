# 字典索引（自动生成，勿手改）

> 生成：`python3 tools/kb_index.py`；数据目录：`kb/`。
> **用法**：先 grep 本表（路径 / 描述 / 用途 / 标签）定位文件，再只取需要的行段：`sed -n '1,100p' kb/dict/<路径>`、`shuf -n 50 kb/dict/<路径>`；**禁止把整文件读入上下文**。
> 行数取自各级 `_meta.yaml`；带 `*` 的行表示该文件 `_meta` 未收录、行数由 `wc -l` 实测。路径以 `/` 结尾的行是 `_meta` 里的目录汇总条目，其下明细见同前缀各行。
> 数据说明：渗透测试字典总集合，涵盖认证凭据、Web路径、端口服务、基础数据等各类字典

## 分类计数

| 分类 | 文件数 | 总行数 |
| --- | --- | --- |
| auth | 49 | 1,032,650 |
| network | 4 | 233 |
| port | 43 | 18,463 |
| regular | 30 | 1,327,384 |
| web | 110 | 1,304,824 |
| 根目录 | 1 | 94 |
| **合计** | **237** | 3,683,648 |

## auth（49 文件 / 1,032,650 行；子分类：device-default, flask, jwt, password, username）

> 认证相关字典集合，包含用户名密码对、凭据组合
> 标签：auth,authentication,认证,凭据,credential,登录,用户名密码

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| auth/credential-pair.txt | 701 | 常见的用户名:密码组合对（冒号分隔） | 批量凭据填充攻击、多服务默认账密快速验证 | credential-pair,凭据对,用户名密码组合,默认账密 |
| auth/device-default/README.md | 25* | （_meta 未收录，行数由 wc -l 实测） | — | — |
| auth/device-default/oa-system-default.txt | 5 | 政务/企业 OA 系统默认口令（致远OA、泛微OA 等） | 授权范围内 OA 系统默认口令核验 | oa,致远,泛微,办公系统,默认口令,default-credential |
| auth/device-default/security-appliance-default.txt | 34 | 防火墙/VPN/安全审计/日志审计等安全设备默认口令（天融信、华为、H3C、启明星辰、深信服、安恒、绿盟、网神、联想网御等） | 授权范围内安全设备默认口令快速核验、登录爆破初筛 | firewall,防火墙,vpn,审计,日志,绿盟,天融信,华为,H3C,启明星辰,深信服,安恒,网神,联想网御,默认口令,default-credential |
| auth/flask/flask-secret-key.txt | 12 | 常见 Flask SECRET_KEY 示例（flask secret key wordlist） | 使用 flask-unsign 或 hashcat 离线爆破 Flask session cookie 的 SECRET_KEY | flask,flask secret key,flask secret key wordlist,secret_key,SECRET_KEY |
| auth/jwt/jwt-secret.txt | 42 | 常见默认 JWT HMAC 密钥（jwt secret wordlist） | 使用 jwt_tool、hashcat 或 john 离线爆破 HS256/HS384/HS512 密钥 | jwt secret wordlist,jwt,secret,hmac,hs256 |
| auth/password/complex/alphanum-6char.txt | 76905 | 6位字母数字混合密码（含大小写和数字） | 针对6位最低复杂度策略的密码爆破 | 6char,alphanumeric,字母数字,混合密码 |
| auth/password/complex/alphanum-8char.txt | 60850 | 8位字母数字混合密码（含大小写和数字） | 针对8位最低复杂度策略的密码爆破 | 8char,alphanumeric,字母数字,混合密码 |
| auth/password/complex/complex-6char-all-four-rules.txt | 2972 | 6位密码，满足大写+小写+数字+特殊字符四种规则 | 绕过严格密码策略（四种字符类型必须包含）的爆破 | 6char,four-rules,四种字符,最强策略 |
| auth/password/complex/complex-6char-alpha-digit-special.txt | 27563 | 6位密码，含字母+数字+特殊字符 | 针对要求字母数字特殊字符组合的密码策略爆破 | 6char,alpha-digit-special,字母数字特殊 |
| auth/password/complex/complex-6char-three-of-four.txt | 107960 | 6位密码，满足四种字符类型中的任意三种 | 针对"四选三"复杂度策略的密码爆破 | 6char,three-of-four,四选三,复杂度策略 |
| auth/password/complex/complex-6char-upper-lower-digit-no-repeat.txt | 76905 | 6位密码，含大小写+数字且无重复字符 | 针对禁止重复字符的密码策略爆破 | 6char,no-repeat,无重复,大小写数字 |
| auth/password/complex/complex-6char-upper-lower-digit.txt | 75945 | 6位密码，含大写+小写+数字 | 针对要求大小写和数字的密码策略爆破 | 6char,upper-lower-digit,大小写数字 |
| auth/password/complex/complex-8char-all-four-rules.txt | 2548 | 8位密码，满足大写+小写+数字+特殊字符四种规则 | 绕过8位严格密码策略（四种字符类型必须包含）的爆破 | 8char,four-rules,四种字符,最强策略 |
| auth/password/complex/complex-8char-alpha-digit-special.txt | 26857 | 8位密码，含字母+数字+特殊字符 | 针对8位要求字母数字特殊字符组合的密码策略爆破 | 8char,alpha-digit-special,字母数字特殊 |
| auth/password/complex/complex-8char-three-of-four.txt | 91281 | 8位密码，满足四种字符类型中的任意三种 | 针对8位"四选三"复杂度策略的密码爆破 | 8char,three-of-four,四选三,复杂度策略 |
| auth/password/complex/complex-8char-upper-lower-digit-no-repeat.txt | 60850 | 8位密码，含大小写+数字且无重复字符 | 针对8位禁止重复字符的密码策略爆破 | 8char,no-repeat,无重复,大小写数字 |
| auth/password/complex/complex-8char-upper-lower-digit.txt | 59995 | 8位密码，含大写+小写+数字 | 针对8位要求大小写和数字的密码策略爆破 | 8char,upper-lower-digit,大小写数字 |
| auth/password/complex/complex-top100.txt | 104 | 最常见的100个复杂密码 | 快速测试常见复杂密码组合 | top100,常见复杂密码,快速筛查 |
| auth/password/complex/complex-top1000.txt | 1299 | 最常见的1000个复杂密码 | 中等规模复杂密码爆破 | top1000,常见复杂密码,中等规模 |
| auth/password/complex/complex-top30.txt | 35 | 最常见的30个复杂密码 | 极速验证最常用的复杂密码 | top30,常见复杂密码,极速筛查 |
| auth/password/complex/readme.md | 19 | 复杂密码字典的生成规则说明文档 | 了解各字典文件的生成规则与适用场景 | documentation,说明文档,readme |
| auth/password/pass-admin.txt | 586 | 以admin为前缀的管理员常用密码组合 | 后台管理员账户密码爆破 | admin,管理员,admin-password,后台密码 |
| auth/password/password-top10.txt | 10 | 最常见的10个弱口令，覆盖常见密码与 rockyou 高频口令子集 | 快速验证默认密码、登录初筛 | top10,common,weak,极简弱口令,top,wordlist,password top,常见密码,rockyou |
| auth/password/password-top100.txt | 173 | 最常见的约100个弱口令，覆盖常见密码与 rockyou 高频口令子集 | 登录爆破初筛、快速验证默认口令 | top100,common,weak,弱口令,top,wordlist,password top,常见密码,rockyou |
| auth/password/password-top1000.txt | 1888 | 约1000个常见弱口令集合，覆盖常见密码与 rockyou 高频口令子集 | 中等规模登录爆破 | top1000,medium,弱口令,常用密码,top,wordlist,password top,常见密码,rockyou |
| auth/password/password-top100000.txt | 94123 | 约100000个密码的超大字典，可替代 rockyou 常见密码字典 | 全面密码爆破、离线哈希碰撞 | top100000,exhaustive,密码字典,大字典,top,wordlist,password top,常见密码,rockyou |
| auth/password/password-top20000.txt | 19315 | 约20000个常用密码集合，可替代 rockyou 做常见密码爆破 | 大规模登录爆破、深度密码猜测 | top20000,large,弱口令,密码字典,top,wordlist,password top,常见密码,rockyou |
| auth/password/sql.txt | 121 | SQL注入认证绕过用的密码Payload | 登录框SQL注入绕过测试 | sqli,injection,注入绕过,万能密码 |
| auth/password/wpa/top200000-wpa.txt | 203806 | 约20万个最常见的WPA/WiFi密码 | 大规模WiFi握手包离线破解 | top200000,大字典,wifi-crack,离线破解 |
| auth/password/wpa/top447-wpa.txt | 447 | 最常见的447个WiFi密码 | WiFi密码快速猜测验证 | top447,快速验证,常见WiFi密码 |
| auth/password/wpa/top4800-wpa.txt | 4800 | 最常见的4800个WiFi密码 | 中等规模WiFi密码爆破 | top4800,中等规模,WiFi密码 |
| auth/password/wpa/top62-wpa.txt | 62 | 最常见的62个WiFi密码 | WiFi密码极速初筛 | top62,极速筛查,WiFi弱口令 |
| auth/username/cn-email.txt | 309 | 中国常见测试邮箱地址格式的用户名（含163/qq/gmail等后缀） | 中国目标的测试邮箱账户枚举与登录爆破 | email,邮箱,中国邮箱,cn-email,chinese,china |
| auth/username/cn-phone.txt | 345 | 中国常见测试手机号码格式 | 以测试手机号为用户名的系统登录爆破 | phone,手机号,中国手机,mobile |
| auth/username/pinyin/cn-firstname.txt | 128 | 中国常见名字（中文汉字） | 生成中文姓名组合、社工字典基础数据 | firstname,名字,中文名,given-name |
| auth/username/pinyin/cn-fullname-14k.txt | 14391 | 大规模中文全名集合（汉字，约14000个） | 大规模中文全名用户名枚举 | fullname,中文全名,大字典,large |
| auth/username/pinyin/cn-fullname-1k.txt | 1068 | 常见中文全名（汉字，约1000个） | 国内系统以中文全名为用户名的枚举 | fullname,中文全名,汉字姓名,chinese-name |
| auth/username/pinyin/cn-surname.txt | 117 | 中国常见姓氏（中文汉字，含复姓） | 生成中文姓名组合、社工字典基础数据 | surname,姓氏,百家姓,family-name |
| auth/username/pinyin/lastname.txt | 189 | 中国常见姓氏的拼音格式 | 拼音用户名枚举的姓氏部分 | lastname,姓氏拼音,surname-pinyin |
| auth/username/pinyin/pinyin-abbrev.txt | 1443 | 姓氏全拼+名字首字母缩写格式（如zhangj、caijh） | 缩写格式用户名枚举 | abbreviation,缩写,姓全拼+名首字母 |
| auth/username/pinyin/pinyin-dot-fullname.txt | 1133 | 点分全名拼音格式（如zhang.wei、w.zhang） | 邮箱/企业系统常见的点分拼音用户名枚举 | dot-separated,点分格式,email-style,企业用户名 |
| auth/username/pinyin/pinyin-firstname.txt | 1402 | 中文名字的拼音（如anqi、anyang） | 拼音名字部分的用户名枚举 | firstname,名字拼音,given-name-pinyin |
| auth/username/pinyin/pinyin-fullname.txt | 991 | 中文姓名全拼连写格式（如anwenran、baihonglu） | 全拼连写格式的用户名枚举 | pinyin,全拼连写,中文名,fullname |
| auth/username/pinyin/pinyin-initials.txt | 217 | 中文姓名首字母缩写格式（如cb、cf） | 首字母缩写格式的用户名枚举 | initials,首字母,缩写,initials-only |
| auth/username/user-mail.txt | 59 | 常见的邮件系统管理员用户名 | 邮件服务器用户名枚举 | mail,邮件,管理员,mail-admin |
| auth/username/user-us.txt | 2092 | 英文常见用户名集合 | 英文系统/国际化目标的用户名枚举 | english,英文用户名,us,international |
| auth/username/user-web.txt | 113 | Web应用常见用户名及数字ID | Web应用用户名枚举与账户爆破 | web,网站用户名,数字ID,web-app |
| auth/username/username-top10000.txt | 10415 | 约10000个通用用户名集合 | 大规模用户名枚举与爆破 | large,大字典,通用用户名,枚举 |

## network（4 文件 / 233 行；子分类：subdomain）

> 网络扫描相关字典，含DNS服务器、排除网段和本地IP变体
> 标签：network,网络,扫描,scanning,信息收集

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| network/dns-servers.txt | 10 | 常用公共DNS服务器IP地址（含国内外） | DNS查询时指定可靠的DNS服务器 | dns,dns-server,公共DNS,resolver,域名解析 |
| network/exclude.txt | 18 | 扫描时应排除的保留IP网段（内网、环回等） | 网络扫描时排除非目标网段 | ip,exclude,排除,reserved,保留网段,内网 |
| network/local-ip.txt | 55 | 本地回环地址的各种编码和表示变体 | SSRF漏洞测试中绕过IP过滤 | localhost,回环地址,ssrf-bypass,ip-bypass |
| network/subdomain/subdomain-common.txt | 150 | 常见子域名字典（业务/环境/基础设施关键字，如 api、admin、oa、vpn、mail、test、dev 等） | 授权范围内子域名枚举、域名爆破、子域接管排查 | subdomain,子域,子域名,domain,域名,wordlist,字典,dictionary,枚举,爆破,dns,brute,content discovery,api,admin,oa,vpn,mail,test,dev |

## port（43 文件 / 18,463 行；子分类：db2, esxi, ftp, memcached, mongodb, mysql, oracle, pop3, postgresql, rdp, redis, smtp, snmp, sqlserver, ssh, svn, telnet, vnc, weblogic）

> 各类网络服务端口的默认凭据字典集合，含端口列表
> 标签：port,端口,service,服务,credential,凭据,默认口令,服务爆破

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| port/db2/pass.txt | 2 | DB2数据库常见默认密码 | DB2数据库密码爆破 | password,密码,db2-pass |
| port/db2/user.txt | 4 | DB2数据库常见默认用户名 | DB2数据库用户名爆破 | username,用户名,db2-user |
| port/esxi/pass.txt | 46 | ESXi常见密码 | ESXi管理平台密码爆破 | password,密码,esxi-pass |
| port/esxi/user.txt | 5 | ESXi常见用户名 | ESXi管理平台用户名爆破 | username,用户名,esxi-user |
| port/ftp/pass.txt | 114 | FTP服务常见密码 | FTP服务密码爆破 | password,密码,ftp-pass |
| port/ftp/user.txt | 12 | FTP服务常见用户名 | FTP服务用户名爆破 | username,用户名,ftp-user |
| port/memcached/pass.txt | 33 | Memcached常见密码 | Memcached认证密码爆破 | password,密码,memcached-pass |
| port/memcached/user.txt | 4 | Memcached常见用户名 | Memcached认证用户名爆破 | username,用户名,memcached-user |
| port/mongodb/pass.txt | 62 | MongoDB常见密码 | MongoDB数据库密码爆破 | password,密码,mongodb-pass |
| port/mongodb/user.txt | 4 | MongoDB常见用户名 | MongoDB数据库用户名爆破 | username,用户名,mongodb-user |
| port/mysql/pass.txt | 233 | MySQL常见密码 | MySQL数据库密码爆破 | password,密码,mysql-pass |
| port/mysql/user.txt | 7 | MySQL常见默认用户名 | MySQL数据库用户名爆破 | username,用户名,mysql-user |
| port/oracle/pass.txt | 511 | Oracle数据库常见密码 | Oracle数据库密码爆破 | password,密码,oracle-pass |
| port/oracle/sid.txt | 575 | Oracle数据库常见SID名称 | Oracle SID枚举与发现 | sid,实例名,oracle-sid,枚举 |
| port/oracle/user-common.txt | 10 | Oracle最常见的默认用户名（精简版） | Oracle数据库快速用户名验证 | username,用户名,oracle-user,精简 |
| port/oracle/user-extended.txt | 479 | Oracle数据库用户名大字典 | Oracle数据库全面用户名枚举 | username,用户名,oracle-user,大字典 |
| port/pop3/pass.txt | 27 | POP3邮件服务常见密码 | POP3邮件服务密码爆破 | password,密码,pop3-pass |
| port/pop3/user.txt | 1502 | POP3邮件服务用户名大字典 | POP3邮箱账户枚举与爆破 | username,用户名,pop3-user,邮箱账户 |
| port/port-list.md | 5939 | 常见端口号与对应服务的详细对照表 | 端口识别、服务判断参考 | port-list,端口列表,服务对照,参考文档 |
| port/port.txt | 2087 | 常用端口号列表 | 端口扫描目标范围指定 | port-scan,端口扫描,端口号,nmap |
| port/postgresql/pass.txt | 38 | PostgreSQL常见密码 | PostgreSQL数据库密码爆破 | password,密码,postgres-pass |
| port/postgresql/user.txt | 3 | PostgreSQL常见默认用户名 | PostgreSQL数据库用户名爆破 | username,用户名,postgres-user |
| port/rdp/pass.txt | 264 | RDP远程桌面常见密码 | RDP远程桌面密码爆破 | password,密码,rdp-pass |
| port/rdp/user.txt | 27 | RDP远程桌面常见用户名 | RDP远程桌面用户名爆破 | username,用户名,rdp-user |
| port/redis/pass.txt | 38 | Redis常见认证密码 | Redis未授权/弱口令爆破 | password,密码,redis-pass,弱口令 |
| port/smtp/cn-email-username.txt | 1959 | 中国常见邮箱用户名集合 | 国内邮件服务器用户名枚举 | cn-email,中国邮箱,用户名,枚举 |
| port/smtp/pass.txt | 27 | SMTP邮件服务常见密码 | SMTP邮件服务密码爆破 | password,密码,smtp-pass |
| port/smtp/us-email-username.txt | 2092 | 英文常见邮箱用户名集合 | 国外邮件服务器用户名枚举 | us-email,英文邮箱,用户名,枚举 |
| port/smtp/user.txt | 1502 | SMTP邮件服务通用用户名大字典 | SMTP邮件服务用户名全面枚举 | username,用户名,smtp-user,大字典 |
| port/snmp/pass.txt | 119 | SNMP常见社区字符串（Community String） | SNMP社区字符串爆破与信息获取 | community,社区字符串,snmp-community |
| port/sqlserver/pass.txt | 198 | SQL Server常见密码 | SQL Server数据库密码爆破 | password,密码,mssql-pass |
| port/sqlserver/user.txt | 6 | SQL Server常见默认用户名 | SQL Server数据库用户名爆破 | username,用户名,mssql-user,sa |
| port/ssh/pass-common.txt | 107 | SSH常见密码精简版 | SSH密码快速爆破 | password,密码,ssh-pass,精简 |
| port/ssh/pass-extended.txt | 300 | SSH常见密码扩展版 | SSH密码中等规模爆破 | password,密码,ssh-pass,扩展 |
| port/ssh/user-common.txt | 6 | SSH最常见默认用户名（精简版） | SSH用户名快速验证 | username,用户名,ssh-user,精简 |
| port/ssh/user-extended.txt | 26 | SSH常见用户名扩展版 | SSH用户名枚举 | username,用户名,ssh-user,扩展 |
| port/svn/pass.txt | 22 | SVN服务常见密码 | SVN服务密码爆破 | password,密码,svn-pass |
| port/svn/user.txt | 5 | SVN服务常见用户名 | SVN服务用户名爆破 | username,用户名,svn-user |
| port/telnet/pass.txt | 28 | Telnet服务常见密码 | Telnet服务密码爆破 | password,密码,telnet-pass |
| port/telnet/user.txt | 5 | Telnet服务常见用户名 | Telnet服务用户名爆破 | username,用户名,telnet-user |
| port/vnc/pass.txt | 31 | VNC远程桌面常见密码 | VNC服务密码爆破 | password,密码,vnc-pass,弱口令 |
| port/weblogic/pass.txt | 3 | WebLogic常见默认密码 | WebLogic控制台密码爆破 | password,密码,weblogic-pass |
| port/weblogic/user.txt | 1 | WebLogic默认用户名 | WebLogic控制台用户名验证 | username,用户名,weblogic-user |

## regular（30 文件 / 1,327,384 行；子分类：address, keyword, letter, number, seo）

> 通用基础数据字典，含字母、数字、地址、关键词等规则化数据
> 标签：regular,基础数据,regular-data,通用,辅助字典

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| regular/address/area-code.txt | 4072 | 全国行政区划代码（省/市/区/县） | 身份证号码生成、行政区划数据参考 | area-code,行政区划代码,身份证前缀 |
| regular/address/cn-areas.txt | 2995 | 中国区/县级行政区名称 | 地址信息枚举、社工信息收集 | area,区县,行政区名,county |
| regular/address/cn-cities.txt | 342 | 中国城市名称列表 | 城市信息枚举、社工信息收集 | city,城市,城市名,municipality |
| regular/address/cn-pcas.json | 1 | 中国省市区街道四级联动JSON数据 | 完整地址数据参考、地址生成 | pcas,省市区,json,四级联动 |
| regular/eicar.txt | 1 | EICAR防病毒测试文件标准字符串 | 测试杀毒软件是否正常工作 | eicar,antivirus,防病毒测试,安全检测 |
| regular/keyword/keyword-common.txt | 22 | 配置文件中的敏感关键词（数据库连接、密码等） | 代码审计和配置文件中的敏感信息搜索 | sensitive-keyword,敏感词,配置泄露,代码审计 |
| regular/letter/lower-1char.txt | 26 | 单个小写字母a到z | 单字母枚举基础数据 | single,单字母,lowercase,小写,a-z |
| regular/letter/lower-2char.txt | 676 | 两位小写字母全排列（aa到zz） | 两位字母组合枚举 | 2char,两位字母,lowercase,排列组合 |
| regular/letter/lower-3char.txt | 17576 | 三位小写字母全排列（aaa到zzz） | 三位字母组合枚举 | 3char,三位字母,lowercase,排列组合 |
| regular/letter/lower-4char.txt | 456976 | 四位小写字母全排列（aaaa到zzzz） | 四位字母组合枚举 | 4char,四位字母,lowercase,排列组合 |
| regular/letter/misc.txt | 67 | 数字和常见短字符串混合集合 | 简单ID和短字符串枚举 | misc,混合,数字字母,短字符串 |
| regular/letter/upper-1char.txt | 26 | 单个大写字母A到Z | 单字母枚举基础数据（大写） | single,单字母,uppercase,大写,A-Z |
| regular/letter/upper-2char.txt | 676 | 两位大写字母全排列（AA到ZZ） | 两位字母组合枚举（大写） | 2char,两位字母,uppercase,排列组合 |
| regular/letter/upper-3char.txt | 17576 | 三位大写字母全排列（AAA到ZZZ） | 三位字母组合枚举（大写） | 3char,三位字母,uppercase,排列组合 |
| regular/letter/upper-4char.txt | 456976 | 四位大写字母全排列（AAAA到ZZZZ） | 四位字母组合枚举（大写） | 4char,四位字母,uppercase,排列组合 |
| regular/number/birthday.txt | 110912 | 日期格式数字集合（19800101-20201231等） | 生日密码爆破、日期参数枚举 | birthday,生日,日期,date,密码 |
| regular/number/num-0-10.txt | 11 | 数字0到10 | 小范围数字参数枚举 | basic,基础数字,0-10 |
| regular/number/num-0-100.txt | 101 | 数字0到100 | 百以内数字参数枚举 | basic,基础数字,0-100 |
| regular/number/num-0-1000.txt | 1001 | 数字0到1000 | 千以内数字参数枚举 | basic,基础数字,0-1000 |
| regular/number/num-0-10000.txt | 10001 | 数字0到10000 | 万以内数字参数枚举 | medium,中等范围,0-10000 |
| regular/number/num-0-100000.txt | 100001 | 数字0到100000 | 十万以内数字参数枚举 | large,大范围,0-100000 |
| regular/number/num-0-5000.txt | 5001 | 数字0到5000 | 五千以内数字参数枚举 | medium,中等范围,0-5000 |
| regular/number/num-00-99.txt | 100 | 两位数字00到99（补零格式） | 两位数字枚举 | 2digit,两位数,补零,00-99 |
| regular/number/num-000-999.txt | 1000 | 三位数字000到999（补零格式） | 三位数字枚举 | 3digit,三位数,补零,000-999 |
| regular/number/num-0000-1000.txt | 1001 | 四位数字0000到1000（补零格式） | 四位数字枚举（验证码等） | 4digit,四位数,补零,验证码 |
| regular/number/num-000000-010000.txt | 10001 | 六位数字000000到010000 | 六位数字验证码枚举 | 6digit,六位数,验证码,010000 |
| regular/number/num-000000-100000.txt | 100001 | 六位数字000000到100000 | 六位数字验证码全面枚举 | 6digit,六位数,验证码,100000 |
| regular/number/num-1000-9999.txt | 9000 | 四位数字1000到9999 | 四位纯数字密码/验证码爆破 | 4digit,四位数,密码,验证码 |
| regular/readme.md | 44 | 规则化数据字典的说明文档 | 了解各基础数据字典的生成规则 | documentation,说明文档,readme |
| regular/seo/seo-word.txt | 21201 | 黑帽SEO/博彩/棋牌等违规关键词集合 | 网站篡改检测、黑链识别、违规内容排查 | blackhat-seo,黑帽SEO,博彩关键词,违规检测 |

## web（110 文件 / 1,304,824 行；子分类：api-param, cms, ctf, directory, dns, errors, file-backup, http, middleware, service, upload, webshell）

> Web方向字典总集合，按用途细分为目录扫描、API参数、文件上传、备份文件、HTTP头、Webshell、DNS、报错指纹、CMS、中间件与服务等子字典
> 标签：web,字典,wordlist,渗透测试,信息收集

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| web/api-param/ | 51156 | Web API参数名和参数值Fuzz字典，按漏洞类型分类 | 接口参数发现与参数级漏洞Fuzz | parameter,参数,api,接口,fuzz,参数发现 |
| web/api-param/api.txt | 28 | API路径分隔符和特殊编码字符 | API路径Fuzz、WAF绕过测试 | api-path,路径分隔,特殊字符,waf-bypass |
| web/api-param/param-callback.txt | 9 | JSONP回调函数常见参数名及测试值 | JSONP劫持漏洞检测 | jsonp,callback,回调劫持,跨域 |
| web/api-param/param-captcha.txt | 50 | 验证码绕过用的常见测试值 | 验证码逻辑绕过测试 | captcha,验证码,bypass,绕过 |
| web/api-param/param-common.txt | 70 | 常见敏感信息相关参数名（身份证、手机号、用户ID等） | 敏感接口参数枚举、越权漏洞测试 | sensitive-param,敏感参数,idor,越权 |
| web/api-param/param-extended.txt | 50360 | 大规模通用HTTP参数名字典 | 全面参数发现与隐藏参数枚举 | large,大字典,通用参数,param-discovery |
| web/api-param/param-findpassword.txt | 57 | 找回密码功能相关的接口路径和参数名 | 密码重置功能枚举与逻辑漏洞测试 | password-reset,找回密码,逻辑漏洞,密码重置 |
| web/api-param/param-imagesize.txt | 18 | 图片尺寸相关参数名及大数值Payload | 图片处理DoS漏洞测试（超大尺寸触发资源耗尽） | image-size,图片处理,dos,资源耗尽 |
| web/api-param/param-json.txt | 12 | JSON格式的分页请求Payload模板 | JSON接口分页参数Fuzz | json,分页,pagination,json-body |
| web/api-param/param-lfi.txt | 25 | 本地文件包含（LFI）常见参数名 | LFI漏洞参数发现与测试 | lfi,文件包含,file-inclusion,本地文件读取 |
| web/api-param/param-login.txt | 14 | 登录接口常见路径和参数名 | 登录入口发现与认证接口枚举 | login,登录,signin,认证接口 |
| web/api-param/param-rce.txt | 25 | 远程命令执行（RCE）常见参数名 | RCE漏洞参数发现与命令注入测试 | rce,命令执行,command-injection,命令注入 |
| web/api-param/param-redirect.txt | 89 | URL重定向绕过Payload集合 | 开放重定向漏洞的绕过测试 | redirect,重定向,open-redirect,url-bypass |
| web/api-param/param-register.txt | 38 | 用户注册功能相关的接口路径和参数名 | 注册接口发现与枚举 | register,注册,signup,用户注册 |
| web/api-param/param-sqli.txt | 25 | SQL注入常见参数名 | SQL注入漏洞参数发现 | sqli,sql注入,injection,注入点 |
| web/api-param/param-ssrf.txt | 25 | SSRF常见参数名 | SSRF漏洞参数发现 | ssrf,服务端请求伪造,url-param,请求伪造 |
| web/api-param/param-xss.txt | 27 | XSS常见参数名 | XSS漏洞参数发现与反射测试 | xss,跨站脚本,反射型,参数注入 |
| web/api-param/top100-param-cookie.txt | 100 | 最常见的100个Cookie参数名 | Cookie参数分析与会话安全测试 | cookie,会话,session,top100 |
| web/api-param/top100-param-get.txt | 99 | 最常见的100个GET请求参数名 | GET参数枚举与隐藏接口发现 | get,get-param,top100,参数枚举 |
| web/api-param/top100-param-post.txt | 85 | 最常见的100个POST请求参数名 | POST参数枚举与表单接口分析 | post,post-param,top100,表单参数 |
| web/cms/ | 248 | CMS框架路径和控制器字典（WordPress、ThinkPHP） | CMS指纹识别与敏感路径探测 | cms,内容管理,wordpress,thinkphp,框架路径 |
| web/cms/thinkphp-controller.txt | 58 | ThinkPHP框架控制器和类名集合 | ThinkPHP RCE漏洞利用时的控制器枚举 | thinkphp,controller,控制器,rce利用 |
| web/cms/wordpress.txt | 190 | WordPress核心文件和管理路径集合 | WordPress站点指纹识别与敏感路径发现 | wordpress,wp,核心文件,管理路径 |
| web/ctf/ | 363 | CTF Web常用payload与源码泄露路径字典 | CTF Web题目快速解题与payload试错 | ctf,竞赛,payload,源码泄露,文件包含,命令执行 |
| web/ctf/param.txt | 45 | CTF常用的文件包含和命令执行Payload | CTF Web题目中的文件读取和RCE利用 | payload,文件包含,命令执行,php-filter |
| web/ctf/sql.txt | 95 | CTF SQL注入常用数字和测试值 | CTF SQL注入题目的基础测试 | sqli,sql注入,数字,基础测试 |
| web/ctf/uri.txt | 223 | CTF常用的备份文件和源码泄露路径 | CTF Web题目的源码泄露探测 | backup,源码泄露,备份文件,信息收集 |
| web/directory/ | 445001 | Web目录和路径扫描字典集合，按语言和用途分类 | 目录爆破、后台与敏感路径发现 | directory,目录扫描,路径发现,dirsearch,gobuster,内容发现 |
| web/directory/admin-dir.txt | 2167 | 后台管理目录路径集合 | 网站后台入口发现 | admin,后台,管理目录,admin-panel |
| web/directory/api.txt | 342 | API接口路径和Spring Actuator端点 | API端点发现、Actuator未授权访问探测 | api,actuator,接口发现,endpoint,endpoints,controller,控制器,路径,字典,爆破,fuzz,api paths wordlist,paths,wordlist |
| web/directory/asp/asp-directory.txt | 60721 | ASP网站目录路径大字典 | ASP网站全面目录扫描 | asp-dir,大字典,目录扫描,全面 |
| web/directory/asp/asp.txt | 70848 | ASP文件路径大字典（含.asp后缀） | ASP网站文件路径枚举 | asp-file,大字典,文件扫描,asp路径 |
| web/directory/asp/top100-asp.txt | 87 | 最常见的100个ASP页面路径 | ASP网站快速扫描 | top100,快速扫描,常见asp页面 |
| web/directory/aspx/ashx.txt | 26263 | ASHX处理程序路径字典 | .NET网站ASHX处理程序枚举 | ashx,handler,处理程序,dotnet |
| web/directory/aspx/aspx-directory.txt | 46191 | ASPX网站目录路径大字典 | ASPX网站全面目录扫描 | aspx-dir,大字典,目录扫描,全面 |
| web/directory/aspx/aspx.txt | 26334 | ASPX文件路径字典 | ASPX网站文件路径枚举 | aspx-file,文件扫描,aspx路径 |
| web/directory/aspx/top100-ashx.txt | 162 | 最常见的ASHX处理程序路径 | .NET网站ASHX快速扫描 | top100,ashx,快速扫描,常见路径 |
| web/directory/aspx/top100-aspx.txt | 96 | 最常见的100个ASPX页面路径 | ASPX网站快速扫描 | top100,快速扫描,常见aspx页面 |
| web/directory/common.txt | 5379 | 通用Web目录和文件路径 | 通用Web目录扫描 | common,通用,目录扫描,常见路径,common paths,paths,directory fuzz wordlist,fuzz,wordlist |
| web/directory/js/js.txt | 266 | 常见JS文件路径集合 | JS文件发现、前端信息泄露检测 | javascript,js-file,前端文件,信息泄露 |
| web/directory/jsp/action.txt | 269 | Struts的.action路径集合 | Struts框架Action接口枚举 | struts,action,框架路径,java-web |
| web/directory/jsp/do-directory.txt | 4004 | .do后缀的目录路径字典 | Java Web的.do路径目录扫描 | do-dir,java-web,目录扫描 |
| web/directory/jsp/do.txt | 41954 | .do后缀的文件路径大字典 | Java Web的.do路径全面扫描 | do-file,大字典,java-web |
| web/directory/jsp/jsp-directory.txt | 4218 | JSP网站目录路径字典 | JSP网站目录扫描 | jsp,tomcat,jsp-dir,目录扫描,java-web |
| web/directory/jsp/jsp.txt | 42015 | JSP文件路径大字典 | JSP网站文件路径全面枚举 | jsp,tomcat,jsp-file,大字典,全面扫描 |
| web/directory/jsp/top100-do.txt | 88 | 最常见的100个.do路径 | Java Web .do路径快速扫描 | top100,do,快速扫描,常见路径 |
| web/directory/jsp/top100-jsp.txt | 88 | 最常见的100个JSP页面路径 | JSP网站快速扫描 | jsp,tomcat,top100,快速扫描,常见路径 |
| web/directory/login.txt | 1443 | 登录页面路径集合 | 登录入口发现 | login,登录页,认证入口,signin |
| web/directory/main.txt | 35004 | 大规模综合目录扫描字典 | 全面目录扫描、深度路径发现 | main,comprehensive,大字典,全面扫描 |
| web/directory/payment-callback.txt | 73 | 微信支付、支付宝异步通知与支付回调路径 | 支付回调接口发现、微信/支付宝 notify 与 callback 枚举 | wechat,pay,alipay,notify,callback,微信支付,支付宝,支付回调,异步通知 |
| web/directory/php/php-directory.txt | 3392 | PHP网站目录路径字典 | PHP网站目录扫描 | php-dir,目录扫描,php路径 |
| web/directory/php/php.txt | 48095 | PHP文件路径大字典 | PHP网站文件路径全面枚举 | php-file,大字典,全面扫描 |
| web/directory/php/top100-php.txt | 94 | 最常见的100个PHP页面路径 | PHP网站快速扫描 | top100,快速扫描,常见php页面 |
| web/directory/redteam-config.txt | 65 | 红队常用的敏感配置文件路径（.aws、.git、.env等） | 信息泄露检测、敏感配置文件发现 | redteam,config,配置泄露,敏感文件,信息泄露,sensitive,file,path |
| web/directory/redteam-file-suffix.txt | 38 | 红队常用的敏感文件后缀名 | 配合文件名生成备份文件扫描路径 | suffix,后缀,backup,备份文件后缀 |
| web/directory/redteam-file.txt | 251 | 红队常用的敏感文件名（不含后缀） | 配合后缀名生成敏感文件扫描路径 | redteam,filename,敏感文件名,信息收集,sensitive,file |
| web/directory/secondary/secondary-common.txt | 718 | 常见二级目录路径精简版 | 二级目录快速枚举 | secondary,二级目录,精简版,快速 |
| web/directory/secondary/secondary-extended.txt | 24336 | 二级目录路径大字典 | 二级目录全面枚举 | secondary,二级目录,大字典,全面 |
| web/dns/ | 151749 | 子域名与DNS相关字典，含子域名前缀、OOB平台域名、顶级域名后缀 | 子域名爆破、DNS枚举、无回显漏洞OOB域名选择 | dns,子域名,subdomain,枚举,oob |
| web/dns/dns.txt | 151548 | 超大规模子域名前缀字典 | 全面子域名枚举爆破 | subdomain,子域名,域名枚举,子域名爆破,大字典,全面枚举 |
| web/dns/oob.txt | 24 | 常见OOB（带外数据）DNS平台域名 | 漏洞验证时选择可用的DNSLog/OOB平台 | oob,dnslog,带外,漏洞验证平台 |
| web/dns/top-dns.txt | 177 | 最常见的子域名前缀 | 子域名快速枚举 | subdomain,子域名,域名枚举,top,常见子域名,快速枚举,精简 |
| web/errors/ | 97 | 各类Web报错信息指纹集合 | 报错回显识别与框架指纹辅助判断 | error,报错,指纹,错误回显 |
| web/errors/top100-errors.txt | 97 | 最常见的100个Web应用错误信息特征 | 数据库类型识别、框架指纹识别、报错注入判断 | error-message,报错特征,数据库识别,框架识别 |
| web/file-backup/ | 58673 | 备份文件与敏感文件路径字典，含文件名与目录两类 | 备份文件与源码泄露探测 | backup,备份文件,源码泄露,敏感文件,信息泄露 |
| web/file-backup/bak-directory.txt | 1576 | 备份文件目录路径字典 | 网站备份文件目录扫描 | backup,备份文件,bak,备份目录,目录扫描,backup-dir |
| web/file-backup/bak.txt | 1444 | 常见备份文件路径（.bak等） | 网站备份文件发现 | backup,bak,备份文件,bak-file |
| web/file-backup/cfm-directory.txt | 248 | ColdFusion CFM文件目录路径 | ColdFusion站点目录扫描 | cfm,coldfusion,目录扫描 |
| web/file-backup/cfm.txt | 56 | ColdFusion CFM敏感文件路径 | ColdFusion敏感文件发现 | cfm,coldfusion,敏感文件 |
| web/file-backup/cgi-directory.txt | 97 | CGI脚本目录路径 | CGI脚本目录扫描 | cgi,cgi-bin,脚本目录 |
| web/file-backup/cgi.txt | 80 | CGI脚本文件路径 | CGI敏感脚本发现 | cgi,脚本文件,cgi-script |
| web/file-backup/db-directory.txt | 944 | 数据库文件目录路径（.mdb等） | Web数据库文件泄露扫描 | database,数据库文件,mdb,目录扫描 |
| web/file-backup/db.txt | 868 | 数据库文件路径（.mdb等） | Web数据库文件下载检测 | database,数据库文件,mdb,文件泄露 |
| web/file-backup/misc.txt | 51505 | 综合杂项文件扫描大字典 | 全面的Web文件扫描 | misc,综合,大字典,全面扫描 |
| web/file-backup/py.txt | 131 | Python脚本文件路径 | Python Web应用敏感文件发现 | python,py,脚本文件,源码泄露 |
| web/file-backup/suffix.txt | 403 | 备份文件后缀变体集合（.bak、.swp等编辑器临时文件） | 配合文件名批量生成备份文件扫描路径 | backup,备份文件,suffix,后缀,临时文件,编辑器备份 |
| web/file-backup/txt.txt | 1321 | TXT文本文件路径 | 敏感文本文件发现（robots.txt、readme等） | txt,文本文件,信息泄露,robots |
| web/http/ | 2750 | HTTP请求头与协议相关字典，含User-Agent、MIME、认证头、HTTP方法等 | 请求头伪造与WAF绕过测试 | http,header,请求头,user-agent,mime,绕过 |
| web/http/header-auth.txt | 8 | 常见认证相关的HTTP请求头（Token、Authorization等） | 认证头Fuzz、未授权访问测试 | header,请求头,auth-header,认证头,token,authorization |
| web/http/header-mimetypes.txt | 1864 | 完整的MIME类型（Content-Type）列表 | 文件上传Content-Type绕过、响应头分析 | header,请求头,mime,content-type,文件类型,上传绕过 |
| web/http/header-redteam.txt | 66 | 红队工具和扫描器的User-Agent特征 | 识别常见安全工具的请求特征、WAF规则编写 | header,请求头,user-agent,指纹,redteam,scanner,扫描器特征,工具指纹 |
| web/http/header-refer-ip.txt | 7 | IP伪造相关的HTTP请求头（X-Forwarded-For等） | 源IP伪造绕过访问控制 | header,请求头,ip-spoof,xff,ip伪造,访问控制绕过 |
| web/http/header-refer.txt | 114 | 常见HTTP请求头名称集合 | 请求头Fuzz、隐藏参数发现 | header,请求头,header-name,请求头名,fuzz,枚举 |
| web/http/header-sessionid.txt | 11 | 常见Session ID的Cookie名称 | 会话标识识别、Session劫持测试 | header,请求头,session,sessionid,会话,cookie |
| web/http/header-spider.txt | 25 | 主流搜索引擎爬虫的User-Agent | 伪装搜索引擎爬虫绕过访问限制 | header,请求头,user-agent,指纹,spider,爬虫,搜索引擎 |
| web/http/methods.txt | 32 | HTTP请求方法集合（含标准和非标准方法） | HTTP方法枚举、PUT/DELETE等危险方法检测 | method,请求方法,http-verb,危险方法 |
| web/http/proxifier-filter.txt | 176 | Proxifier代理过滤规则域名列表 | 配置Proxifier代理工具的过滤规则 | proxifier,proxy,代理,过滤规则 |
| web/http/top500-user-agent.txt | 447 | 最常见的500个User-Agent字符串 | User-Agent轮换、反爬虫绕过 | header,请求头,user-agent,指纹,ua,浏览器指纹,反爬绕过 |
| web/middleware/ | 103700 | Web中间件默认凭据和配置字典集合 | 中间件默认口令验证与配置探测 | middleware,中间件,默认口令,default-credential |
| web/middleware/cas/pass.txt | 1 | CAS系统默认密码 | CAS单点登录系统密码验证 | password,密码,cas-pass |
| web/middleware/cas/user.txt | 1 | CAS系统默认用户名 | CAS单点登录系统用户名验证 | username,用户名,cas-user |
| web/middleware/middleware-pass.txt | 24 | 各类中间件的默认用户名密码对照表 | 快速查阅各中间件默认凭据 | default-password,默认密码,对照表,汇总 |
| web/middleware/rabbitmq/pass.txt | 37 | RabbitMQ常见密码 | RabbitMQ管理控制台密码爆破 | password,密码,rabbitmq-pass |
| web/middleware/rabbitmq/user.txt | 6 | RabbitMQ常见用户名 | RabbitMQ管理控制台用户名爆破 | username,用户名,rabbitmq-user |
| web/middleware/shiro/key.txt | 101148 | Shiro RememberMe加密密钥（AES Key）大字典 | Shiro反序列化漏洞利用时的密钥爆破 | aes-key,shiro-key,rememberme,反序列化利用 |
| web/middleware/spring/spring-configuration-metadata.txt | 1713 | Spring Boot配置属性名集合 | Spring Boot配置属性枚举、Actuator env端点信息提取 | config-property,配置属性,metadata,spring-env |
| web/middleware/tomcat/basic.txt | 228 | Tomcat Manager的用户名:密码组合对（Basic认证格式） | Tomcat Manager控制台Basic认证爆破 | basic-auth,凭据对,manager,控制台 |
| web/middleware/tomcat/pass.txt | 38 | Tomcat常见密码 | Tomcat Manager密码爆破 | password,密码,tomcat-pass |
| web/middleware/tomcat/tomcat.txt | 90 | Tomcat敏感路径和管理接口 | Tomcat管理接口发现与路径枚举 | path,路径,管理接口,tomcat-path |
| web/middleware/tomcat/user.txt | 6 | Tomcat常见用户名 | Tomcat Manager用户名爆破 | username,用户名,tomcat-user |
| web/middleware/weblogic/pass.txt | 44 | WebLogic控制台常见密码 | WebLogic管理控制台密码爆破 | password,密码,weblogic-pass |
| web/middleware/weblogic/user.txt | 11 | WebLogic控制台常见用户名 | WebLogic管理控制台用户名爆破 | username,用户名,weblogic-user |
| web/middleware/weblogic/weblogic.txt | 349 | WebLogic敏感路径和管理接口集合 | WebLogic管理接口和敏感路径发现 | path,路径,管理接口,weblogic-path |
| web/middleware/zabbix/pass.txt | 1 | Zabbix默认密码 | Zabbix监控系统密码验证 | password,密码,zabbix-pass |
| web/middleware/zabbix/user.txt | 3 | Zabbix常见用户名 | Zabbix监控系统用户名爆破 | username,用户名,zabbix-user |
| web/service/ | 310 | 常见Web服务与运维平台字典（Druid、Jira、phpMyAdmin、XXL-JOB） | 运维平台默认口令与敏感路径探测 | service,服务,管理平台,信息泄露 |
| web/service/druid/ | 8 | Druid监控平台默认用户名和密码字典 | Druid监控页面默认口令验证与爆破 | druid,alibaba,数据库监控,默认口令 |
| web/service/druid/pass.txt | 4 | Druid监控平台常见密码 | Druid监控平台密码爆破 | password,密码,druid-pass |
| web/service/druid/user.txt | 4 | Druid监控平台常见用户名 | Druid监控平台用户名爆破 | username,用户名,druid-user |
| web/service/jira/ | 22 | Jira敏感接口与信息泄露路径字典 | Jira未授权访问与信息泄露探测 | jira,atlassian,项目管理,敏感路径,信息泄露 |
| web/service/jira/jira.txt | 22 | Jira敏感接口和信息泄露路径 | Jira未授权访问和信息泄露探测 | jira-path,敏感路径,未授权,信息泄露 |
| web/service/phpmyadmin/ | 269 | phpMyAdmin默认用户名和密码字典 | phpMyAdmin登录界面口令爆破 | phpmyadmin,mysql,数据库管理,默认口令 |
| web/service/phpmyadmin/pass.txt | 267 | phpMyAdmin常见密码 | phpMyAdmin管理界面密码爆破 | password,密码,phpmyadmin-pass |
| web/service/phpmyadmin/user.txt | 2 | phpMyAdmin常见用户名 | phpMyAdmin管理界面用户名验证 | username,用户名,phpmyadmin-user,root |
| web/service/xxljob/ | 11 | XXL-JOB任务调度平台部署路径字典 | XXL-JOB管理平台入口发现 | xxl-job,scheduler,任务调度,路径发现 |
| web/service/xxljob/xxl-path.txt | 11 | XXL-JOB管理平台常见部署路径 | XXL-JOB调度平台入口发现 | xxl-path,部署路径,管理入口,任务调度 |
| web/upload/ | 414 | 文件上传绕过字典，含扩展名变形、Content-Type、.htaccess | 上传黑名单绕过与扩展名Fuzz | upload,文件上传,绕过,bypass,扩展名 |
| web/upload/asp.txt | 30 | ASP文件上传后缀绕过变体 | ASP环境下的文件上传黑名单绕过 | asp,后缀绕过,大小写,截断 |
| web/upload/content-type.txt | 253 | Content-Type MIME类型集合 | 文件上传Content-Type白名单绕过 | content-type,mime,白名单绕过 |
| web/upload/htaccess.txt | 37 | .htaccess文件名大小写变体 | Apache .htaccess上传绕过 | htaccess,apache,配置覆盖,大小写 |
| web/upload/jsp.txt | 30 | JSP文件上传后缀绕过变体 | JSP环境下的文件上传黑名单绕过 | jsp,后缀绕过,大小写,截断 |
| web/upload/php.txt | 30 | PHP文件上传后缀绕过变体 | PHP环境下的文件上传黑名单绕过 | php,后缀绕过,大小写,phtml |
| web/upload/upload-suffix.txt | 34 | 通用文件上传后缀名集合 | 文件上传功能测试的后缀名枚举 | suffix,后缀,后缀名,黑名单,通用,文件类型 |
| web/webshell/ | 490363 | Webshell路径扫描与连接密码爆破字典 | Webshell落地路径选择与连接密码爆破 | webshell,木马,后门,路径扫描,密码爆破 |
| web/webshell/dir.txt | 52412 | 常见Webshell文件路径大字典 | 服务器Webshell后门文件扫描 | webshell-path,路径扫描,后门路径,文件扫描,大字典 |
| web/webshell/webshell-pass.txt | 437951 | Webshell连接密码超大字典 | 已知Webshell的连接密码爆破 | webshell-password,连接密码,超大字典,密码爆破 |

## 根目录（1 文件 / 94 行）

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| readme.md | 94 | 字典目录结构和使用说明文档 | 了解字典分类结构和各目录用途 | documentation,说明文档,readme,目录说明 |
