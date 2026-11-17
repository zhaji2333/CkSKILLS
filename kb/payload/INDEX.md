# 载荷索引（自动生成，勿手改）

> 生成：`python3 tools/kb_index.py`；数据目录：`kb/`。
> **用法**：先 grep 本表（路径 / 描述 / 用途 / 标签）定位文件，再只取需要的行段：`sed -n '1,100p' kb/payload/<路径>`、`shuf -n 50 kb/payload/<路径>`；**禁止把整文件读入上下文**。
> 行数取自各级 `_meta.yaml`；带 `*` 的行表示该文件 `_meta` 未收录、行数由 `wc -l` 实测。路径以 `/` 结尾的行是 `_meta` 里的目录汇总条目，其下明细见同前缀各行。

## 分类计数

| 分类 | 文件数 | 总行数 |
| --- | --- | --- |
| access-bypass | 1 | 5 |
| cors | 3 | 68 |
| email | 1 | 12 |
| format | 5 | 1,388 |
| hpp | 1 | 37 |
| lfi | 8 | 2,955 |
| prompt-injection | 1 | 639 |
| rce | 6 | 951 |
| reverse-shell | 5 | 64 |
| sqli | 10 | 2,739 |
| ssi | 1 | 79 |
| ssrf | 1 | 94 |
| upload | 10 | 502 |
| xss | 14 | 12,291 |
| xxe | 2 | 207 |
| **合计** | **69** | 22,031 |

## access-bypass（1 文件 / 5 行）

> 访问控制绕过payload集合，包含通过XFF等HTTP头伪造IP地址绕过403限制的payload
> 标签：access bypass,access control,访问控制绕过,XFF,X-Forwarded-For,403绕过,IP伪造

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| access-bypass/xff-403.txt | 5 | 通过伪造内网IP地址（127.0.0.1/10.x/172.x/192.168.x）绕过403访问限制的XFF头值 | 遇到403禁止访问时，配合X-Forwarded-For等请求头逐个尝试这些IP地址绕过访问控制 | xff,X-Forwarded-For,403 bypass,内网IP,访问绕过,IP spoofing |

## cors（3 文件 / 68 行）

> CORS跨域资源共享错误配置利用payload集合，包含PoC页面和Origin绕过技巧
> 标签：cors,cross-origin,跨域,CORS misconfiguration,同源策略,origin绕过,凭据窃取

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| cors/cors.html | 25 | CORS漏洞PoC利用页面，通过XMLHttpRequest带凭据跨域读取目标API响应数据 | 验证CORS配置漏洞时，替换目标URL后在浏览器打开此HTML，观察是否能跨域获取敏感数据 | poc,XMLHttpRequest,withCredentials,跨域读取,漏洞验证 |
| cors/cors.md | 17 | CORS漏洞检测参考文档，包含curl检测命令和各类Origin绕过变体（null/子域/前缀等） | 作为CORS漏洞测试的速查手册，参考各种Origin头变体构造绕过请求 | reference,curl,origin bypass,参考文档,检测方法,绕过技巧 |
| cors/cors2.html | 26 | CORS漏洞PoC利用页面（提取SID版），通过alert弹出跨域响应内容 | 验证CORS漏洞是否可窃取会话ID等敏感信息时使用 | poc,session,SID,XMLHttpRequest,会话窃取,漏洞验证 |

## email（1 文件 / 12 行）

> 电子邮件格式Fuzz payload集合，包含XSS/SQLi/SMTP注入等各类邮箱地址变异
> 标签：email,邮件,email injection,邮箱格式,SMTP注入,邮件Fuzz,input validation

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| email/email.txt | 12 | 恶意构造的邮箱地址payload，涵盖XSS注入、SQL注入、模板注入、SMTP头注入和SSRF等多种攻击向量 | 测试邮箱输入框的安全过滤时，用这些变异邮箱地址检测是否存在注入漏洞 | fuzz,xss,sqli,smtp injection,SSRF,模板注入,邮箱注入,输入验证 |

## format（5 文件 / 1,388 行）

> 数据格式Fuzz payload集合，包含十六进制编码、整数溢出、JSON畸形、空字节和特殊字符串
> 标签：format,格式化,fuzz,特殊字符,数据格式

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| format/hex.txt | 262 | URL编码的十六进制字符集（%00-%FF），覆盖全部256个单字节值 | 测试输入过滤和编码处理时，用完整十六进制字符集Fuzz检测哪些字节可绕过过滤 | hex,url encoding,十六进制,URL编码,字节,byte,编码绕过 |
| format/int.txt | 12 | 整数边界值payload，包含负数、零、常见溢出值（0x7fffffff/0xffffffff等） | 测试整数型参数时，检测整数溢出、类型转换错误和边界条件漏洞 | integer,overflow,boundary,整数溢出,边界值,类型转换,integer overflow |
| format/json.txt | 89 | JSON格式畸形payload，包含空值、特殊键名、嵌套结构和反序列化利用字段 | 测试JSON解析器和API接口时，用这些畸形JSON检测反序列化漏洞和解析异常 | json,deserialization,反序列化,畸形JSON,解析异常,API fuzz |
| format/nullbyte.txt | 122 | 空字节和格式化字符串payload，包含%00空字节、格式化字符串攻击向量（%s/%x/%n等）和超长空字节序列 | 测试空字节截断和格式化字符串漏洞时使用，检测C/C++程序的内存安全问题 | null byte,format string,空字节截断,格式化字符串,内存安全,%00,%n |
| format/string.txt | 903 | 通用特殊字符串Fuzz payload，包含SQL注入、XSS、命令注入、特殊字符和编码变体的综合集合 | 对任意文本输入框进行全面Fuzz测试，一次性覆盖多种常见注入攻击向量 | string,comprehensive,fuzz,综合测试,特殊字符,注入检测,通用payload |

## hpp（1 文件 / 37 行）

> HTTP参数污染payload集合，包含各种参数重复、编码和分隔符变体
> 标签：hpp,HTTP parameter pollution,HTTP参数污染,参数覆盖,参数注入,parameter tampering

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| hpp/hpp.txt | 37 | HTTP参数污染变体payload，包含参数重复(?id=1&id=2)、编码绕过、数组注入和多种分隔符格式 | 测试Web应用对重复参数的处理逻辑时，检测参数优先级差异和过滤绕过 | parameter duplicate,encoding bypass,参数重复,编码绕过,分隔符,优先级差异 |

## lfi（8 文件 / 2,955 行）

> 本地文件包含与路径遍历payload集合，覆盖Linux/Windows/Java平台的敏感文件路径和遍历技巧
> 标签：lfi,local file inclusion,本地文件包含,path traversal,路径遍历,目录穿越,文件读取

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| lfi/java-path.txt | 8 | Java Web应用敏感目录路径（WEB-INF/META-INF），用于读取配置和类文件 | 测试Java Web应用的LFI漏洞时，尝试读取WEB-INF下的web.xml、class文件和Spring配置 | java,WEB-INF,META-INF,Java Web,敏感目录,配置泄露 |
| lfi/java-properties.txt | 1739 | Java应用常见配置文件路径大全，包含Spring/MyBatis/Hibernate/数据库等各类框架配置文件 | 大规模扫描Java应用可能泄露的配置文件，发现数据库连接信息、密钥等敏感数据 | java,properties,Spring,配置文件,框架配置,敏感信息泄露,大字典 |
| lfi/linux-path.txt | 6 | Linux Web服务器常见根目录路径（/tmp/www/html等），含路径遍历到Tomcat目录 | 确定Web应用在Linux系统上的文件根目录位置，辅助构造精确的LFI路径 | linux,web root,根目录,Tomcat,文件路径定位 |
| lfi/linux.txt | 682 | Linux系统敏感文件绝对路径大全，覆盖Apache/Nginx/SSH/系统配置/日志等文件 | 通过LFI漏洞批量测试Linux服务器上的敏感文件是否可读取 | linux,sensitive files,apache,nginx,ssh,passwd,系统配置,敏感文件,大字典 |
| lfi/log.txt | 47 | 常见Web应用和系统日志文件名字典（access.log/error.log/debug.log等） | 扫描目标服务器是否存在可直接访问的日志文件，获取敏感信息或用于日志注入 | log,access log,error log,日志文件,日志泄露,信息收集 |
| lfi/properties.txt | 203 | 通用Web应用配置文件路径字典（.properties/.xml/.yml），涵盖多种框架 | 扫描目标是否存在可读取的配置文件，发现数据库密码、API密钥等敏感信息 | properties,config,xml,yml,配置文件,敏感信息,Actuator,Spring Boot |
| lfi/traversal.txt | 64 | 路径遍历编码变体集合，包含%5c、%252f双重编码、Unicode编码等各种绕过WAF的遍历序列 | LFI测试中用各种编码变体的../序列绕过路径过滤和WAF规则 | traversal,encoding bypass,双重编码,Unicode,WAF绕过,路径遍历变体 |
| lfi/windows.txt | 206 | Windows系统敏感文件绝对路径大全，覆盖Apache/IIS/系统配置/日志等文件（C:/路径格式） | 通过LFI漏洞批量测试Windows服务器上的敏感文件是否可读取 | windows,IIS,apache,sensitive files,boot.ini,系统配置,敏感文件,大字典 |

## prompt-injection（1 文件 / 639 行）

> AI/LLM提示词注入payload集合，包含各类绕过大模型安全限制的攻击提示词模板
> 标签：prompt injection,提示词注入,AI安全,LLM,大模型,jailbreak,越狱,安全绕过

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| prompt-injection/prompt.md | 639 | LLM提示词注入技巧参考文档，包含蒸馏攻击、语义相变、角色扮演、DAN越狱等多种绕过安全对齐的提示词模板 | 测试AI/LLM应用的安全性时，参考这些提示词模板检测模型是否可被诱导输出违规内容 | reference,jailbreak,DAN,蒸馏攻击,角色扮演,安全对齐,越狱模板,参考文档 |

## rce（6 文件 / 951 行）

> 远程代码/命令执行payload集合，覆盖Java/PHP/Unix/Windows/PowerShell多平台的命令注入和RCE利用
> 标签：rce,remote code execution,远程代码执行,command injection,命令注入,命令执行,代码执行

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| rce/java.txt | 2 | Java OGNL/EL表达式注入RCE payload，通过ScriptEngine执行系统命令 | 测试Struts2/Spring等Java框架的表达式注入漏洞时使用 | java,OGNL,expression injection,Struts2,表达式注入,ScriptEngine |
| rce/php.txt | 19 | PHP代码执行payload，包含system/exec/eval等函数调用和模板注入向量 | 测试PHP应用的代码注入和模板注入漏洞时，检测是否可执行系统命令 | php,system,exec,eval,template injection,代码注入,模板注入,函数调用 |
| rce/powershell.txt | 164 | PowerShell命令/cmdlet名称字典，覆盖文件操作、系统管理、网络等常用cmdlet | 测试Windows系统命令注入时，枚举可用的PowerShell cmdlet构造利用链 | powershell,cmdlet,windows,命令字典,cmdlet枚举,系统管理 |
| rce/rce.txt | 39 | 通用命令注入特殊字符和分隔符payload，包含管道符、重定向、命令连接符等 | 快速测试输入点是否存在命令注入，通过各种shell特殊字符触发命令执行 | special chars,pipe,redirect,命令分隔符,特殊字符,shell元字符,命令连接 |
| rce/unix.txt | 569 | Unix/Linux系统命令名称大全，覆盖系统管理、网络、文件操作等常用命令 | 命令注入利用阶段，枚举目标Linux系统上可用的命令，构造信息收集和提权利用链 | unix,linux,system commands,命令字典,系统命令,命令枚举,信息收集 |
| rce/windows.txt | 158 | Windows CMD命令名称字典，覆盖系统管理、网络、文件操作等常用命令 | 命令注入利用阶段，枚举目标Windows系统上可用的CMD命令 | windows,cmd,system commands,命令字典,系统命令,命令枚举 |

## reverse-shell（5 文件 / 64 行）

> 反弹Shell/Bind Shell payload集合，覆盖Bash/Python/PowerShell/Perl/PHP/Ruby/Java等多语言，包含Shell升级和稳定化命令
> 标签：reverse shell,反弹shell,回连,shell

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| reverse-shell/bash.txt | 14 | Bash/sh反弹Shell一行命令，包含/dev/tcp、mkfifo+nc、ncat、ncat --ssl、socat等多种方式 | 获取命令执行权限后，建立反弹Shell回连到攻击机，支持TCP和UDP | bash,sh,/dev/tcp,mkfifo,nc,ncat,socat,tcp,udp,netcat |
| reverse-shell/others.txt | 15 | 多语言反弹Shell payload，覆盖Perl/PHP/Ruby/Java/Lua/Go/OpenSSL/Awk/xterm | 根据目标可用的编程语言环境，选择对应的反弹Shell方式 | perl,php,ruby,java,lua,go,openssl,awk,xterm,多语言,nc,netcat,socat |
| reverse-shell/powershell.txt | 6 | PowerShell反弹Shell一行命令，使用TCPClient建立连接，支持Base64编码和下载执行方式 | Windows目标环境下，通过PowerShell建立反弹Shell，绕过cmd限制 | powershell,windows,TCPClient,base64,powercat,download cradle |
| reverse-shell/python.txt | 7 | Python反弹Shell一行命令，使用socket+subprocess或socket+pty实现，兼容Python2和Python3 | 目标存在Python环境时，通过socket建立反弹Shell连接 | python,python3,socket,pty,subprocess,os.dup2 |
| reverse-shell/upgrade.txt | 22 | Shell升级和稳定化命令，将简单反弹Shell提升为完整交互式TTY终端 | 获取反弹Shell后，升级为完整PTY以支持Tab补全、Ctrl+C、vim等交互操作 | tty,pty,upgrade,stabilize,stty,交互式,终端升级,rlwrap,pwncat,shell升级,交互式shell |

## sqli（10 文件 / 2,739 行）

> SQL注入payload集合，覆盖MySQL/MSSQL/Oracle/LDAP多种数据库的注入向量，以及表名列名字典
> 标签：sqli,SQL injection,SQL注入,注入

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| sqli/column.txt | 1101 | 常见数据库列名/字段名字典，包含username/password/email/id等高频字段 | SQL注入确认后枚举目标数据库的列名，快速定位包含敏感数据的字段 | column,field name,列名,字段枚举,数据库枚举,字典 |
| sqli/database.txt | 21 | 常见数据库名称字典，包含MySQL默认库名和常用业务数据库名 | SQL注入时枚举目标服务器上的数据库名称 | database name,数据库名,库名枚举,MySQL,information_schema |
| sqli/payload-blind.txt | 41 | 基于时间的SQL盲注payload，使用sleep()函数通过响应延迟判断条件真假 | 目标无回显时进行时间盲注测试，通过延迟差异提取数据 | blind,time-based,sleep,时间盲注,延迟注入,无回显,盲注 |
| sqli/payload-ldap.txt | 14 | LDAP注入payload，包含逻辑运算符和通配符查询构造 | 测试LDAP认证和查询接口时检测注入漏洞 | ldap,LDAP injection,LDAP注入,目录服务,认证绕过,通配符 |
| sqli/payload-mssql.txt | 99 | MSSQL专用注入payload，包含waitfor delay时间盲注、版本探测和错误注入 | 针对MSSQL数据库进行SQL注入测试，利用MSSQL特有语法提取信息 | mssql,SQL Server,waitfor,xp_cmdshell,MSSQL注入,时间盲注 |
| sqli/payload-mysql.txt | 109 | MySQL专用注入payload，包含sleep/benchmark时间盲注和各类闭合变体 | 针对MySQL数据库进行SQL注入测试，利用MySQL特有函数和语法 | mysql,sleep,benchmark,MySQL注入,时间盲注,联合查询 |
| sqli/payload-oracle.txt | 55 | Oracle专用注入payload，包含utl_http/utl_inaddr带外数据提取和系统信息查询 | 针对Oracle数据库进行SQL注入测试，利用Oracle特有包和函数 | oracle,utl_http,utl_inaddr,Oracle注入,带外通道,OOB,系统信息 |
| sqli/payload.txt | 344 | 通用SQL注入payload集合，包含各种编码、Unicode字符和逻辑绕过的or/and注入变体 | 对任意SQL注入点进行全面Fuzz测试，覆盖多种编码和绕过技巧 | generic,universal,通用注入,编码绕过,Unicode,逻辑注入,综合payload |
| sqli/sql-inj.md | 442 | SQL注入技巧参考文档，包含LDAP注入、MySQL/MSSQL/Oracle语法、WAF绕过技巧等 | 作为SQL注入测试的综合速查手册，快速查阅各数据库的注入语法和绕过方法 | reference,cheatsheet,参考文档,速查手册,WAF绕过,注入技巧,MySQL,MSSQL,Oracle,LDAP,blind,盲注,联合注入 |
| sqli/table.txt | 513 | 常见数据库表名字典，包含users/accounts/orders等高频业务表名 | SQL注入确认后枚举目标数据库的表名，定位存储用户凭据和敏感数据的表 | table,table name,表名,表名枚举,数据库枚举,字典 |

## ssi（1 文件 / 79 行）

> 服务端包含注入(SSI)payload集合，包含exec命令执行、echo信息泄露和include文件包含指令
> 标签：ssi,server-side includes,服务端包含,SSI注入,命令执行,文件包含,信息泄露

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| ssi/payload.txt | 79 | SSI注入payload，涵盖exec命令执行、echo变量泄露、config错误信息、fsize文件探测和include远程包含 | 测试支持SSI的Web服务器时，检测是否可通过SSI指令执行命令或读取文件 | exec,echo,include,config,命令执行,变量泄露,文件包含,远程包含 |

## ssrf（1 文件 / 94 行）

> 服务端请求伪造(SSRF)payload集合，包含各种编码格式的localhost/内网地址绕过变体
> 标签：ssrf,server-side request forgery,服务端请求伪造,内网探测,localhost,回环地址,IP绕过

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| ssrf/payload.txt | 94 | SSRF地址绕过payload，包含127.0.0.1的十六进制/八进制/十进制/IPv6/URL编码等多种表示形式 | 绕过SSRF防护的IP黑名单过滤时，用各种等价的localhost表示方式尝试访问内网服务 | bypass,localhost,127.0.0.1,IPv6,octal,hex,decimal,编码绕过,地址变体,黑名单绕过 |

## upload（10 文件 / 502 行）

> 文件上传测试样本集合，包含各种格式的测试文件和任意文件上传 getshell 用的上传表单 PoC 页面
> 标签：upload,file upload,文件上传,任意文件上传,上传绕过,上传漏洞,文件类型,测试样本

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| upload/1.doc | 1 | DOC格式测试文件样本，用于文件上传功能的格式验证测试 | 测试文件上传接口对DOC文档类型的处理和过滤逻辑 | doc,word,文档,格式测试,文件样本 |
| upload/1.html | 1 | 含XSS payload的HTML测试文件（img onerror触发alert） | 上传HTML文件测试服务器是否允许上传并执行HTML，检测存储型XSS | html,xss,存储型XSS,img onerror,脚本执行 |
| upload/1.pdf | 428 | PDF格式测试文件样本，用于文件上传功能的格式验证测试 | 测试文件上传接口对PDF文件类型的处理和过滤逻辑 | pdf,文档,格式测试,文件样本 |
| upload/1.png | 3* | （_meta 未收录；二进制文件，行数无实际意义） | — | — |
| upload/1.svg | 6 | 含XSS payload的SVG测试文件（内嵌script标签执行alert） | 上传SVG文件测试服务器是否允许上传并解析SVG中的JavaScript代码 | svg,xss,script injection,SVG注入,脚本执行,矢量图 |
| upload/1.txt | 1 | 最简纯文本测试文件，内容为单个字符 | 作为基准测试文件验证上传功能的基本可用性 | txt,plaintext,纯文本,基准测试 |
| upload/1.xlsx | 49 | XLSX格式测试文件样本，用于文件上传功能的格式验证测试 | 测试文件上传接口对Excel文件类型的处理和过滤逻辑 | xlsx,excel,电子表格,格式测试,文件样本 |
| upload/1.zip | 1 | ZIP压缩包测试文件样本，用于文件上传功能的格式验证测试 | 测试文件上传接口对压缩包类型的处理，检测解压炸弹或路径遍历风险 | zip,archive,压缩包,格式测试,解压安全 |
| upload/upload.html | 8 | 通用文件上传HTML表单 PoC，用于任意文件上传/getshell 测试 | 当目标上传接口无前端页面时，用此表单快速构造任意文件上传 getshell 请求 | form,multipart,上传表单,PoC,poc,getshell,辅助工具 |
| upload/upload2.html | 4 | 精简版 PHP 文件上传 HTML 表单 PoC，用于任意文件上传/getshell | 快速构造针对 PHP 上传接口的任意文件上传 getshell 请求 | form,php,multipart,上传表单,PoC,poc,getshell,辅助工具 |

## xss（14 文件 / 12,291 行；子分类：html, pdf, svg, xml）

> XSS跨站脚本攻击payload集合，包含事件属性、HTML标签、JS函数和各类绕过payload
> 标签：xss,cross-site scripting,跨站脚本,payload

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| xss/html/1.html | 1 | 含img onerror XSS payload的HTML文件，上传后触发JavaScript执行 | 测试文件上传功能是否允许上传HTML文件并在浏览器中执行脚本 | img,onerror,上传XSS,存储型XSS,文件上传 |
| xss/js-event.txt | 210 | JavaScript事件属性名称完整列表（onload/onerror/onfocus等210个事件） | 构造XSS payload时枚举所有可用的事件处理属性，寻找未被过滤的事件触发点 | event,事件属性,onload,onerror,onfocus,事件枚举,属性名,事件 |
| xss/js-function.txt | 5 | JavaScript弹窗函数调用变体（self/parent/frames/content/window对象的alert调用） | 绕过alert关键词过滤时，使用不同window对象引用方式调用弹窗函数 | function,alert,弹窗变体,关键词绕过,window对象 |
| xss/js-tag-full.txt | 157 | 完整闭合的HTML标签列表（带尖括号<tag>格式），涵盖157种标签 | XSS Fuzz测试时枚举所有HTML标签，寻找未被过滤可注入事件属性的标签 | tag,html tag,完整标签,标签枚举,闭合标签,Fuzz,标签,HTML标签 |
| xss/js-tag-half.txt | 157 | 半闭合HTML标签列表（仅左尖括号<tag格式），涵盖157种标签 | XSS Fuzz测试时使用半闭合标签探测解析器行为和过滤规则 | tag,html tag,半闭合标签,标签枚举,未闭合,解析器测试,标签,HTML标签 |
| xss/pdf/1.pdf | 428 | 含JavaScript代码的恶意PDF文件样本，可在PDF阅读器或浏览器中触发脚本执行 | 测试PDF上传和在线预览功能是否会执行PDF内嵌的JavaScript代码 | pdf javascript,PDF注入,在线预览,脚本执行,文件上传 |
| xss/readme.md | 620 | XSS攻击技巧综合参考文档，涵盖基础payload、各种绕过技巧、编码方式和利用场景 | 作为XSS渗透测试的速查手册，快速查阅各种XSS攻击向量和绕过方法 | reference,cheatsheet,参考文档,速查手册,绕过技巧,编码方式,反射型,存储型,DOM,事件,标签 |
| xss/svg/1.svg | 6 | 含script标签的SVG文件，在正常SVG图片中嵌入JavaScript代码执行alert | 上传SVG文件测试服务器是否过滤SVG中的script标签，检测SVG XSS漏洞 | script,embedded,内嵌脚本,图片上传,script标签 |
| xss/svg/2.svg | 1 | 使用onload事件的单行SVG XSS payload，最精简的SVG XSS向量 | 快速验证SVG上传是否存在XSS，使用最简payload减少干扰因素 | onload,minimal,精简payload,事件触发,快速验证 |
| xss/svg/sanitised.svg | 45 | 经过清洗处理的合法SVG文件样本，不含恶意代码，作为对照基准 | 作为安全SVG文件的对照样本，验证上传过滤是否能正确区分恶意和正常SVG | sanitised,clean,safe,安全样本,对照基准,过滤验证 |
| xss/xml/xml.txt | 16 | 基于XML特性的XSS payload，包含XPath注入、CDATA绕过、XML实体和DOCTYPE利用 | 测试XML解析器或接受XML输入的接口时，检测通过XML特性触发XSS的可能性 | xpath,cdata,entity,DOCTYPE,XML解析,CDATA绕过,实体注入 |
| xss/xml/xss.xml | 4 | 含JavaScript的恶意XML文件样本，利用XHTML命名空间嵌入script标签 | 上传XML文件或测试XML解析时，检测是否可通过命名空间嵌入脚本执行 | xhtml,namespace,script,命名空间,文件上传,脚本嵌入 |
| xss/xss-payload1.txt | 2148 | XSS综合payload集合，包含各类script/img/svg标签注入、编码绕过和特殊字符变体 | 对目标进行XSS自动化Fuzz扫描，覆盖多种标签和编码绕过方式 | comprehensive,fuzz,script,img,encoding,综合payload,自动化扫描,编码变体,反射型,存储型,DOM |
| xss/xss-payload2.txt | 8493 | 按HTML标签+事件属性全组合的XSS payload大字典，覆盖各种标签与事件的完整组合 | 大规模Fuzz测试，全面覆盖所有标签/事件组合以发现被遗漏的XSS攻击面 | fuzz,tag,event,comprehensive,全组合,标签事件,大字典,完整覆盖,事件,标签 |

## xxe（2 文件 / 207 行）

> XML外部实体注入(XXE)payload集合，包含各种DTD实体声明和利用技巧
> 标签：xxe,XML external entity,XML外部实体,XXE注入,DTD,实体注入,文件读取,SSRF

| 路径 | 行数 | 描述 | 用途 | 标签 |
| --- | --- | --- | --- | --- |
| xxe/xml.txt | 91 | XXE攻击payload集合，包含XPath注入、CDATA绕过、DOCTYPE实体声明读取系统文件等 | 测试XML解析接口时，检测是否存在XXE漏洞可读取服务器文件或发起SSRF | xpath,cdata,DOCTYPE,ENTITY,文件读取,passwd,系统文件,SSRF |
| xxe/xxe.md | 116 | XXE漏洞攻击技巧参考文档，涵盖基础实体、外部实体、Blind XXE、带外数据提取和各种利用场景 | 作为XXE渗透测试的速查手册，快速查阅各种XXE攻击模式和利用方法 | reference,cheatsheet,参考文档,速查手册,Blind XXE,OOB,带外提取,利用技巧 |
