---
name: apk-reversing
description: 当需要获取目标 APK、识别加固壳类型、脱壳还原 dex、反编译得到 Java/so/H5 全量源码产物，或 android-security-audit 需要可直接开挖的输入时调用。负责 APK → 全量可审计产物（壳识别 → 脱壳 → JADX 反编译 + apktool 资源 + so 提取 + H5/assets 提取）→ 标准目录交付。命中场景：JADX 打开是 stub/空壳、入口类是 com.stub.StubApp、lib 下只有壳 so、需要还原真实代码后再挖洞。
---

# apk-reversing — APK 脱壳与全量反编译还原

> **定位**：这是 `android-security-audit` 的**上游准备技能**——把 APK 变成"可挖的全量源码"，交付标准目录后 `android-security-audit` 直接开挖（密钥追踪/组件安全）。本技能只负责还原，**不挖洞**；漏洞挖掘见 `android-security-audit`。
>
> 只有 APK 有加固壳时才必须完整走本技能；无壳 APK 直接 JADX 反编译即可开工。

## 何时调用（触发条件）

- 拿到 APK 但 JADX 打开是 **stub/空壳**、看不到真实代码
- 入口类是 `com.stub.StubApp` / `com.secneo.apkwrapper` 等加固特征类
- `lib/` 下只有壳 so（libshella、libjiagu、libSecShell 等）
- 需要提取 so、H5/assets、资源、签名等全量产物
- 为 `android-security-audit` 准备标准输入（`jadx_out/` + `apktool_out/` + `lib/` + `assets/`）

## 标准产物（交付标准）

```
reversing/<package>/
├── jadx_out/          # Java 源码（JADX 反编译，必须是真实代码而非 stub）
├── apktool_out/       # smali + 资源 + AndroidManifest（apktool）
├── dex/               # 脱壳后的 dex（未合并进 jadx 时单独留档）
├── lib/               # 全部 so（arm64-v8a 优先，可 IDA/Ghidra 打开）
├── assets/            # H5/JS/证书/密钥/配置等资源
├── origin.apk         # 原始 APK 存档
└── report.md          # 壳类型 / 脱壳方式 / 产物清单 / 未还原项
```

**交付检查**：`jadx_out` 里能 grep 到真实特征串（appKey/secret/接口域名）、`lib/` 的 so 可被 IDA/Ghidra 打开搜导出表、`assets/` 的 H5 完整——满足即交付 `android-security-audit`。

---

## 一、APK 获取

```bash
# 已安装设备上提取
adb shell pm list packages | grep <关键词>            # 找包名
adb shell pm path <package>                           # 拿到 APK 路径
adb pull <路径> origin.apk                            # 拉取

# 模拟器/真机均可；也可应用商店、官网、第三方平台、抓包拦截下载地址
```

- 优先取**最新版本**（厂商 SRC 要求应用商店最新版）
- 同一 App 多渠道包（小米/华为/Google Play）差异可能影响脱壳难度，可换渠道试

---

## 二、壳识别（先识别再脱壳）

**快速判断**：
```bash
# 1. 解压看 lib 与入口
unzip -l origin.apk | grep -iE "\.so$|stub|wrapper"
# 2. JADX 打开看 Application/入口类
jadx -d /tmp/quick origin.apk && grep -rn "StubApp\|class.*Application" /tmp/quick/sources/
```

**常见壳特征表**：

| 加固 | 特征（lib/入口类） | 脱壳方式 |
|---|---|---|
| 腾讯乐固 | `libshella-*.so` / `libtprt.so` / `com.stub.StubApp` | frida-dexdump / 模拟器运行 dump |
| 梆梆 | `libSecShell.so` / `SecShell` | frida-dexdump / 反射大师 |
| 爱加密 | `libexec.so` / `libexecmain.so` / `com.secneo.apkwrapper` | frida-dexdump |
| 360 | `libjiagu.so` / `libjiagu_x86.so` | 360 脱壳 / 反射大师 |
| 娜迦/顶象 | `libchaosvmp.so` / `libddog.so` | 内存 dump + dex 修复 |
| 腾讯御安全/其他 | `libtosprotection.so` 等 | frida-dexdump / 运行 dump |
| **DCloud uni-app** | 无壳 so，`assets/apps/<appid>/www/` | **无需脱壳**，直接提取 www/ 即前端源码 |

> 关键判断：JADX 打开后全是 stub 包装类 = 有壳，必须脱壳；能直接看到业务类 = 无壳，跳过脱壳直接反编译。

---

## 三、脱壳（核心）

### 方式 1：模拟器 + Frida dump（最通用，推荐）

```bash
# 1. 准备 root 模拟器（MuMu/夜神/雷电）并安装 frida-server（架构匹配）
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &"
# 2. 安装目标 App 并启动（dex 解密加载后才能 dump）
adb install origin.apk
# 3. dump 内存中的 dex
frida-dexdump -U -f <package> -o dex/
# 4. 或 frida-unpack 脚本（hook DEX 加载点，dump 更全）
```

- **脱壳时机**：App 启动后 dex 才在内存解密，必须**先运行再 dump**
- 多个 dex 分片 → 合并后统一交给 JADX
- dump 的 dex 可能头部损坏 → 用 dex 修复工具（如 dexfixer）修复后再反编译

### 方式 2：在线脱壳服务（快速，适合简单壳）

- 上传 APK 到在线脱壳平台拿还原后的 dex（**仅限自有授权目标**，注意上传合规）

### 方式 3：非 root 场景（真机/普通模拟器）

- 部分旧壳可 `adb backup -f app.ab <package>` 提取（API 23- 适用）
- 或换 root 模拟器走方式 1

### 方式 4：H5 / uni-app 类（无需脱壳）

```bash
# DCloud uni-app：assets/apps/<appid>/www/ 直接是前端源码
unzip -o origin.apk -d apktool_out && ls apktool_out/assets/apps/*/www/
# 微信小程序内嵌：见 miniprogram-security
```

---

## 四、反编译与产物还原

```bash
# JADX（无壳：直接反编译 APK；有壳：反编译脱壳后的 dex）
jadx -d jadx_out origin.apk
# 或
jadx -d jadx_out dex/

# apktool（Manifest / smali / 资源 / lib）
apktool d origin.apk -o apktool_out

# so 提取（apktool_out/lib/ 或直接解压）
cp -r apktool_out/lib lib/

# H5/assets 提取
cp -r apktool_out/assets assets/
```

- **so 层**：`lib/arm64-v8a/` 优先；**Ghidra + GhidraMCP 静态优先**（`list_functions` 定位 JNI 导出 → `decompile_function` 拿伪 C），Radare2（`izz`/`afl`）做轻量侦察；导出表搜 `Java_` 前缀（静态注册）或 `JNI_OnLoad`/`RegisterNatives`（动态注册）——对应 `android-security-audit` 一、1.3 SO 层追踪
- **H5 层**：`assets/` 下 HTML/JS 搜加密库（JSEncrypt/CryptoJS）与密钥常量；动态加载的远程 H5 记录加载 URL——对应 `android-security-audit` 一、1.4 H5/JS 层追踪
- **签名/证书**：`META-INF/*.RSA`、`res/raw/` 下的证书与密钥，供重打包/校验分析

---

## 五、质量检查（保证"拿全部"）

- [ ] **入口类真实**：JADX 打开 Application/入口 Activity 是业务代码，非 stub
- [ ] **特征串可命中**：`grep -rniE "appKey|secret|sign|接口域名" jadx_out/sources/` 有结果
- [ ] **so 完整**：`lib/arm64-v8a/` 下 so 齐全，IDA 可打开、导出表可搜
- [ ] **H5 完整**：assets/www 或远程加载地址已记录
- [ ] **dex 合并**：多分片 dex 已合并，无遗漏
- [ ] **report.md 已写**：壳类型、脱壳方式、产物清单、未还原项（如实记录，不编造）

## 六、验证要点

- JADX 打开核心类确认真实代码（截图存证）
- 交付给 `android-security-audit` 后，其快速开始 Step 2 的 grep 应能直接命中
- 壳 so 无法静态分析时，如实记录"该模块需动态追踪"，不硬编

## 七、注意与边界

- 脱壳/反编译仅用于**授权目标**；在线脱壳上传前确认目标已授权
- 加固对抗在升级，新壳（VMP/混淆壳）可能需要针对性方案：先跑起来抓 dex 加载点，或结合 `windows-reverse-engineering` 思路分析壳 so
- 本技能产出的是**审计输入**，不直接定级漏洞——定级与成稿交给 `android-security-audit` + `report`

---

## 联动

- 下游挖洞：产物直接交给 `android-security-audit`（密钥追踪→未授权接口 / 组件安全）
- H5 内嵌小程序：`miniprogram-security`
- 提取的密钥/域名上报深挖：`recon-js-analysis`
- 正式报告：`report`
