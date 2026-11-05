# 🔴 一、密钥追踪 → 未授权接口专项（最高优先级）

> 来源：CkSKILLS v1 `android-security-audit` §🔴 一、密钥追踪 → 未授权接口专项（最高优先级）（迁移至 v2 知识块）

> **为什么排第一**：厂商 App 把签名密钥/加密公钥写死在客户端是普遍现状，命中率远高于组件安全；直接调云端 API 还绕开 Web 入口的 WAF/风控。核心链：**客户端密钥/签名逻辑硬编码（DEX/SO/H5 三层）→ 服务端只验签名不验会话（伪鉴权）或未鉴权 → 离线还原签名，未授权调接口拿全量业务数据**。

### 1.1 攻击模型与三层追踪总览

**攻击链一句话**：拿到 1 个公开 uid/ID → 反编译提取 appId/appKey/签名密钥 → 还原 sign 拼接（如 `md5(appId+appKey+ts)`）→ 直接 POST 业务接口 → 未授权批量拉数据（聊天/订单/发票/用户信息）。

| 层 | 场景 | 手段 | 典型产物 |
|---|---|---|---|
| DEX（Java/Kotlin） | 核心算法在 Java 层 | JADX 全局搜特征串 | 硬编码 appKey/secret，签名拼接可 Python 重写 |
| SO（Native） | `System.loadLibrary` + native 方法 | **IDA 9.5 无头（idalib + MCP）静态定位** → 抓包兜底 → Frida 取证 | 拼好的明文/算好的签名；底线 Hook 网络库截 HTTP 明文 |
| H5/JS（WebView 动态加载） | 热更新业务走远程 H5 | assets 提取 JS / chrome://inspect 断点 | JS 里 RSA 公钥/密钥，Python 构造同构 payload |

### 1.2 DEX 层追踪（静态最快，先做这个）

**特征 grep**（反编译产物）：
```bash
grep -rniE "appKey|appSecret|secret|sign|signature|md5|encrypt|aes|rsa" /tmp/jadx_out/sources/
```
> ⚡ **还没反编译？** 大包直接走 `asc-fast-hunt` 的秒级路径（ASC 路径见该技能一、环境安装；无需全量反编译）：
>
> ```bash
> $ASC/asc findrefs <apk> string appKey      # 逐关键词扫，输出「dex | 类->方法 | matched」
> $ASC/asc getclass <apk> <命中类>            # 读签名类实现（141–303ms，DAD 类型不可信，只定逻辑与常量）
> $ASC/asc disassemble <apk> <命中类> --method '<完整签名>'   # smali 核验拼接顺序（裸方法名会被拒）
> ```
>
> 命中后先定位签名函数与常量；要跨类数据流、确切类型或报告取证，再回 `apk-reversing` 全量产物。
- 命中后**追调用链**：找到签名函数（`sign = md5(appId + appKey + ts)` 之类），确认参数来源（uid、时间戳、固定盐）
- **Python 重写**拼接与加密逻辑，离线可算任意请求签名
- 常见形态：appId/appKey 是 IM/云服务凭证（网易云信/融云等）→ 可伪造签名调该服务接口

**案例模板（聊天记录泄露链，匿名化）**：
```bash
```
→ 数据泄露/越权，中高危。

### 1.3 SO 层追踪（静态优先 → 抓包兜底 → Frida 最后可选）

> **优先顺序**：① **IDA 9.5 无头模式（idalib）+ 官方 IDA MCP 纯静态**（无需设备/root，最稳，主路径）→ ② **抓包截明文**（无需 root，模拟器稳定）→ ③ **Frida Hook**（仅静态读不动时的最后手段，且只作取证）。
> **抄近路**：大包只想确认 native 算法/实现、Java 调用点已明确时，可先用 `asc-fast-hunt` 的 `findrefs`/`getclass` 定位 Java 调用点，然后**直接进本节 ① 或 三、Native 深挖**，不付 JADX 全量成本（见 `../../../../AGENTS.md` 3.1）。
> 本节的定位是**密钥追踪视角**；so 库的完整漏洞挖掘（RCE/提权/溢出/沙箱逃逸/DoS）见 **三、Native/内存安全深挖**。

**① 静态分析（IDA 9.5 无头 + MCP，主路径，无需设备）**
- 定位入口：`System.loadLibrary("xxx")` 确认加载的 so → 导出表搜 `Java_包名_类名_方法名`（静态注册）；无则找 `JNI_OnLoad` 追 `RegisterNatives` 交叉引用（动态注册）
- 侦察前置：`strings lib.so | grep -iE "key|secret|sign|aes|md5"`（轻量无头，先扫一遍再进 IDA）
- **IDA MCP（Agent 直接驱动，主路径）**：`open_database` 打开 so → `execute_python` 跑 IDAPython 枚举 `Java_*` 导出与 `JNI_OnLoad` → 反编译拿伪 C → `reference` 查 API 用法
  - 环境已就绪：`<你的 Agent> mcp doctor` 应显示 `ida` = `✓ handshake OK ✓ 6 tools discovered`
  - 完整工具链、脚本模板、可复制的 IDAPython 片段 → **references/IDA95-native-audit.md**
- **AI 读伪 C 重写**：识别标准算法（MD5/SHA/AES）与拼接顺序（如 `md5(appId+appKey+ts)`）→ Python 重写签名，无需读懂全部汇编
- **Domain API 优先**：`execute_python` 里 `db`（Domain API 句柄）与 `ida_domain` 全局开箱可用，`db.functions` / `db.pseudocode.decompile()` / `db.xrefs.get_callers()` 比裸 IDAPython 简洁；地址属性是 `f.start_ea`（**不是 `f.address`**），反编译返回值要 `str()`。完整 schema 见 references/IDA95-native-audit.md 1.3
- ⚠️ 坑：`ida_funcs.getn_func()` 在 9.5 已弃用（改用 `get_func_ea_by_num()`）；`ida_domain` 需 `pip install ida-domain`，缺失时回退标准 IDAPython

**② 抓包兜底（无 root，模拟器稳定）**
- 模拟器设 adb 代理 + Burp/mitmproxy 装证书（免 root 可做）
- 正常操作 App → 直接看到**最终 HTTP 请求结构与签名值**
- 与静态伪 C 对比验证签名逻辑，确定拼接细节

**③ Frida Hook（最后可选，仅静态读不动时）**
- 触发条件：静态伪 C 因混淆（ollvm 控制流平坦化 / VMP / 字符串加密）读不动，且抓包不足以还原算法时才用
- Hook 导出函数打印入参出参：
```js
// Frida 脚本：Hook 导出函数，打印入参出参，直接拿明文与签名
Java.perform(function(){
  var target = Module.findExportByName("libxxx.so", "Java_com_example_xxx_sign");
  Interceptor.attach(target, {
    onEnter: function(args){ console.log("入参:", Memory.readCString(args[2])); },
    onLeave: function(ret){ console.log("返回值:", Memory.readCString(ret)); }
  });
});
```
- **底线追踪法**：函数都找不到时，Hook 底层网络库——`libc.so` 的 `send`/`sendto`、SSL 库的 `SSL_write`——在发包前一瞬间从内存截获**最终 HTTP 明文请求**，直接得到完整请求结构
- 模拟器注入崩溃时：优先换回静态分析路径，Frida 不作为必选项

**⚠️ Frida 边界规则（强制）**：
- ✅ Frida 仅作**密钥/签名逻辑的取证工具**；最终 PoC 用提取的密钥直接构造签名请求（Python/curl），**不依赖 Frida**
- ❌ 禁止把"用 Frida Hook"写成漏洞本身或利用依赖（厂商官方标记为忽略类）
- 报告口径：写「密钥硬编码于客户端 + 服务端接口仅验签名未验会话/未鉴权」，全程不写 Frida

### 1.4 H5/JS 层追踪（WebView 动态加载）

- **本地提取**：解压 APK，`assets/` 目录提取 HTML/JS，直接搜加密库（`JSEncrypt`、`CryptoJS`）与密钥常量
- **远程调试**：动态加载的远程 JS → BurpSuite 注入 JS 断点代码，或 `chrome://inspect` 连接手机 WebView 前端断点，内存中直接看加密函数入参与密钥
- **密钥复用**：拿到 RSA 公钥或取密钥接口后，用 Python 构造相同加密 payload 发请求

**案例模板（H5 企业数据泄露链，匿名化）**：
```bash
```
→ 注意：**RSA 公钥只做"传输混淆"，不是鉴权**——拿到公钥即可构造合法密文，无需私钥；接口无 Token/登录校验 = 未授权数据泄露，高危。

### 1.5 验证要点与报告口径

- **取证链**：① 反编译/JADX 定位硬编码密钥（截图+路径）② 签名/加密逻辑还原（Python 脚本）③ 未授权请求成功返回真实数据（Burp 请求块+响应截图）
- 影响证明：拉到的数据必须是**他人/全量**数据（非自己账号、非样例）
- 定级：聊天/隐私/财务数据批量泄露 → 中高危；可写可删 = 高危/严重
- 正式报告按 `../../../../rules/40-evidence-report.md`；不写 Frida、不写逆向工具名，只写密钥硬编码 + 接口鉴权缺失
