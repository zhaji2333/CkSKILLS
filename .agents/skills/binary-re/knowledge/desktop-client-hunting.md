# 桌面客户端攻击面与漏洞链（Windows 为主）

> 面向真实授权评估：企业 IM / 网盘 / OA 客户端 / 浏览器 / 安全软件 / 播放器 / 更新器。
> 工具：PowerShell、`curl`、`npx asar`、`rabin2 -zz`、`strings`、IDA/Ghidra、dnSpy、Procmon/API Monitor。
> 只读不写目标机：枚举、抓包、单次验证；**证明层用 `calc` / `%TEMP%` 落标记 / DNSLog**，不下后门、不动用户数据（`../../../../rules/20-min-harm.md`）。
> 报告口径只认 `../../../../rules/40-evidence-report.md`；本节只写形态与方法，不收录密钥实值。

## 一、30 秒攻击面测绘（先出清单，再挑一条打）

产出：一张「攻击面 → 类型 → 可能漏洞」清单，落线索板 §1；**不读全量安装目录**（`../../../../rules/50-token-economy.md`）。

| 面 | 怎么取 | 看什么 |
|---|---|---|
| 进程 | `Get-Process \| ? {$_.Path -like "*<vendor>*"} \| select Name,Path,Id`；`where.exe <exe>` | 主进程 + 常驻子进程（更新器/助手/守护）；哪个跑在 `SYSTEM` |
| 安装目录 | `Get-ChildItem <dir> -Recurse -Include *.exe,*.dll \| select FullName,@{n='Ver';e={$_.VersionInfo.ProductVersion}}` | 公司名/签名/内部版本；`libcef.dll`、`app.asar`、`*.pak`、`WebView2Loader.dll`、`Qt5Core.dll` |
| 框架 | 目录特征：`app.asar`/`resources/`→Electron；`libcef.dll`→CEF；`WebView2Loader.dll`→WebView2/Tauri；`*.exe.config`+`PresentationFramework`→WPF；`*.dll` 里 `mscorlib`→WinForms/.NET；`Qt5*.dll`→QT；`*.pak`→Chromium 资源 | 决定 §2/§3 哪条先打 |
| 自定义协议 | `reg query HKCR /f "URL Protocol" /s`；按产品 `reg query "HKCR\<scheme>" /s` | `shell\open\command` 完整命令行、是否带 `%1`、卸载后是否残留 |
| 回环端口 | `netstat -ano \| findstr LISTENING`；再按 PID 对进程 | bind `127.0.0.1`、端口固定、有无 `/json` |
| 版本 | `(Get-Item libcef.dll).VersionInfo.ProductVersion`；请求 UA 里的 `Chrome/<xx>` | 内嵌内核版本（§4.2） |
| 关键文件 | 安装目录内 `.config/.json/.xml/.js/.pak` 搜 `http`、`ws://`、`token`、`secret`、`api` | 明文端点、内置账号、签名盐、更新地址 |
| 服务/计划任务 | `Get-CimInstance Win32_Service \| ? PathName -like "*<vendor>*"`；`schtasks /query /fo list` | 服务路径未加引号、可写路径、以 SYSTEM 运行 |

Electron/CEF 存量资产（只解一次，结果进 `hunts/<目标>/dig/`）：

```powershell
npx asar extract app.asar out                 # Electron 解包，看主进程/预加载脚本
strings -n 6 app.asar | findstr /i "http token secret"
rabin2 -zz <exe> | findstr /i "http api key"  # PE 字符串快摸
```

- .NET 直接 dnSpy/ILSpy；原生上 IDA/Ghidra；只跟「输入点 → 危险函数」那条链，不通读。
- 安装目录里优先看：`updater*`（更新器）、`*helper*`（助手进程）、`resources/`（前端资产）、`*.pak`（内核资源）。

## 二、自定义协议（Deep Link）

- 触发面：浏览器地址栏、任意网页 `<a href>`、`start <scheme>://...`、其它应用跳转。用户点一次「打开应用」算合理交互，不需要中间人。
- 找参数：`shell\open\command` 的命令行 + 客户端 JS 里搜 `setAsDefaultProtocolClient` / `open-url` / `second-instance` / 协议白名单。
- 危险参数名：`url` `open` `openUrl` `urlType` `webview` `path` `file` `cmd` `folder` `id`。
- 打法（按现场选，不要死抄一种形态）：
  - 外站页塞进内嵌浏览器 → 再探特权上下文（§3.2/§3.3）
  - `file://`、UNC `\\host\share`（NTLM 外带）、本地 html
  - 路径参数穿越到启动目录/可执行同目录（§4.1）
  - 命令参数 `|` `&` `;` `%PATH%` `$(...)`，按拼接点（`CreateProcess`/`ShellExecute`/`system`）试
- 假点：协议只允许自家域；只弹「是否打开」不加载外站；参数进入 handler 前已白名单（过滤在前 → 假点）。

## 三、内嵌浏览器与回环端口（客户端自己起的 HTTP 服务）

### 3.1 回环端口

```bash
netstat -ano | findstr LISTENING          # 找 127.0.0.1:<p>，再按 PID 对进程
curl -s -i http://127.0.0.1:<p>/          # 逐口摸路由
curl -s http://127.0.0.1:<p>/json          # Electron/CEF 远程调试面
```

功能面 → 对应打法：

| 路由特征 | 打法 |
|---|---|
| `exec/run/shell/ping/cmd` | 参数命令注入（`ip=0.0.0.0\|calc`、`cmd=whoami`） |
| `download/export/save/import` | `folder`/`path`/`filename` 穿越（§4.1） |
| `openurl/go-to/navigate/webview` | 外站页进特权窗（§3.2/§3.3） |
| `get/log/config/version` | 信息泄露（token、路径、内部端点） |
| 任意路径 `../` | 本地任意文件读（配置、`win.ini`、浏览器 cookie 库） |
| 超长参数 | 崩溃/溢出 → 转 `windows-reverse-engineering-05-五、缓冲区溢出专项挖掘.md`；有 GS/DEP/ASLR 先别写 RCE |

- 从网页侧打本地口：外站页 `fetch('http://127.0.0.1:<p>/api/...', {mode:'no-cors'})` 做 CSRF-to-localhost；表单 `text/plain` 可绕预检。
- 端口只 bind 随机值且每次变 → 基本没浏览器侧攻击面，改走本机进程/客户端内触发。

### 3.2 CDP（Electron/CEF 远程调试）

```
GET /json  →  [{ "webSocketDebuggerUrl": "ws://127.0.0.1:<p>/devtools/page/<id>" }]
```

- 连上发 `Runtime.evaluate`：`require('child_process').exec('calc')`、读 `process.env`、`process.mainModule`。
- `Target.getTargets` 找特权 page（`devtools://`、`file://`、官方域）；`Page.navigate` 把外站页开进特权窗再 evaluate。
- 页面上也可直接探桥：`typeof process` → `typeof require`（`require.toString()` 含 `native` 才当真）→ `window.require` → 预加载桥 `window.electron.ipcRenderer`。
- 算成：本机执行了指定无害命令 / 回显 `process.env` 里会话与密钥；**只回 target 列表不算**。

### 3.3 特权域（假点高发）

"只能在官方域执行"的桥/API，先证能不能跨域调：

- 外站页 iframe 官方域、`window.open` 后拿引用、`document.domain` 差异；
- 协议/参数里的域用 `official.com@evil.com`（userinfo）、`official.com.evil.com`、`official.com\@evil.com`、`//evil.com` 试解析差异；
- 协议把外站页拉进客户端后，看桥挂在哪一层 frame（顶层/iframe/preload 注入到哪个 context）。

桥只挂官方 frame 且入口 origin 严格 → **假点，不报**；外站页能执行 → 才写客户端洞。

## 四、下载/更新链与内嵌内核版本

### 4.1 落盘点（下载器/更新器类客户端必查）

| 落点 | 打法 | 算成 |
|---|---|---|
| `Start Menu\Programs\Startup\` | `folder=..%2f..%2f...%2fStart Menu/Programs/Startup` | 下载的 exe 下次登录执行 |
| 可执行同目录（覆盖 exe/dll） | `filename=..\updater.exe` | 替换后下次启动加载 |
| 用户目录下同名 dll | 落盘触发搜索顺序劫持 | 以主进程权限加载 |

- 域白名单绕过：`official@attacker`、`official.evil.com`、`official.com.evil.com`、302 跳转、`http`→`https` 协议差、大小写与 `\`。
- 更新器：明文 http、签名校验缺失、版本号可控 → 可替换更新包；真实评估**停在证明层**（替换内容用无害标记，不投持久化后门）。
- 假点：路径被 `Path.GetFullPath` 归一化并限定根；下载后校验签名；落点不可执行。

### 4.2 内嵌内核版本 → 已知 CVE

- 取版本：`libcef.dll` 文件属性 / `app.asar` 里 electron 版本 / 请求 UA 的 `Chrome/<xx>`。
- 版本 → 内核 CVE（渲染 RCE、沙箱逃逸）：先查 `kb/vuln/INDEX.md` 与厂商公告，**核对影响版本再打**，不照抄 CVE 号。
- 看沙箱开关：`--no-sandbox`、`--disable-web-security`、`nodeIntegration: true` 会让链路更短。
- 算成：外站页在内嵌浏览器拿到代码执行并升到本机 → 客户端 RCE；只弹框/只渲染不算，按存储 XSS 归位。

## 五、假点清单与证明口径

开工先自检（每条都能否掉一批误报）：

1. 参数是不是在入口就被严格过滤/白名单了？（过滤在前 → 假点）
2. 是否只能在官方特权域/特权 frame 调用？（跨域证不出 → 假点）
3. 落盘路径是否被归一化并限定根？下载是否校验签名？
4. 端口是否随机、是否 `127.0.0.1` + 本机 token 双保险？
5. 内核版本/CVE 是否对得上影响版本、是否已修？

证明口径（按 `rules/40` 落报告）：

- 本机执行：`calc` / `%TEMP%` 落标记 / DNSLog 回连，一条即可；
- CDP/桥：回显 `Runtime.evaluate` 结果或 `process.env` 片段；
- 文件/落盘：`dir` 出目标路径 + 内容；
- 描述写"谁的客户端 + 什么操作 + 做成什么影响"，不写"攻击者可以……"；抄到的凭证按认钥闸。

## 六、与现有知识块的接缝

| 需要什么 | 去哪 |
|---|---|
| 溢出 / DoS / 利用构造 | `windows-reverse-engineering-05`、`-09`、`-11` |
| 静态 / 动态 / 反调试 | `windows-reverse-engineering-03`、`-04`、`-10` |
| 存储 XSS → 客户端 RCE 投递 | `../../web-xss-frontend/knowledge/xss-test.md` §8 |
| 路径穿越 / 任意文件读 | `../../web-file-path/knowledge/path-traversal-lfi-test.md` |
| 客户端提权（服务/劫持/令牌） | `windows-reverse-engineering-07-七、权限提升专项.md` |
| 报告 / 线索板 | `../../../../rules/40-evidence-report.md`；`hunts/<目标>/CLUEBOARD.md` |