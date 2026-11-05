# 快速开始（5 分钟产出第一个漏洞）

> 来源：CkSKILLS v1 `android-security-audit` §快速开始（5 分钟产出第一个漏洞）（迁移至 v2 知识块）

### Step 1：反编译 APK

```bash
jadx -d /tmp/jadx_out --show-bad-code <path/to/target.apk>
apktool d <path/to/target.apk> -o /tmp/apktool_out
```

> ⚠️ APK 有加固壳（JADX 打开是 stub/空壳、入口类是 `com.stub.StubApp` 等）时，**先调 `apk-reversing` 技能脱壳还原真实代码**，拿到 `jadx_out/`/`lib/`/`assets/` 全量产物后再回到本技能挖掘。
>
> 💡 **大包先快筛**：APK > 100MB 时不必先等 JADX 全量反编译——先调 `asc-fast-hunt` 秒级定位密钥/签名/接口并读 Manifest 组件面，确认值得深挖后再付全量成本（无壳小包直接走本 Step 即可）。

### Step 2：查找高危漏洞（按优先级 grep）

```bash
grep -rniE "appKey|appSecret|secret|sign|signature|md5|encrypt|aes|rsa" /tmp/jadx_out/sources/

grep -rn "getParcelableExtra.*Intent\|startActivity.*getParcelable" /tmp/jadx_out/sources/

grep -rn "Runtime.getRuntime().exec\|ProcessBuilder" /tmp/jadx_out/sources/

grep -rn "loadUrl.*getData\|getIntent().getData" /tmp/jadx_out/sources/

grep -rn "openFile\|openAssetFile\|ParcelFileDescriptor.open" /tmp/jadx_out/sources/

grep -rn "setTitle.*getIntent\|setMessage.*getIntent\|setText.*getIntent" /tmp/jadx_out/sources/

grep -rn "System.loadLibrary\|System.load\|native " /tmp/jadx_out/sources/ | grep -v "^.*://"
ls -la /tmp/apktool_out/lib/arm64-v8a/        # so 清单
```

### Step 3：提取资产凭证（APP 中拿到的要上报用户）

反编译产物中优先提取并向**用户上报**以下内容——这些可能是 APP 后台接口或业务接口域名，鉴权往往弱于前端接口：

```bash
grep -rEoh "https?://[a-zA-Z0-9._/-]+" /tmp/jadx_out/sources/ | sort -u
grep -rEoh "([0-9]{1,3}\.){3}[0-9]{1,3}" /tmp/jadx_out/sources/ | sort -u

grep -rniE "appid|appkey|app_secret|apikey|access_key|secret_key" /tmp/jadx_out/sources/
```

- **URL/IP/域名 → 提醒用户关注**：很可能是 APP 后台接口或业务接口域名，作为可扩展攻击面进入资产测绘与接口测试（联动 `recon-js-analysis`）
- **appid/appkey 等凭证 → 上报用户并深入挖掘**：验证有效性、调用对应后端接口/云服务、越权面测试（联动 `cloud-infra-supply-chain`）

### Step 4：验证漏洞（ADB 快速验证）

```bash
adb shell am start -n com.victim/.ExportedActivity --es redirect_intent "com.victim/.PrivateActivity"

adb shell am start -n com.victim/.VulnActivity --es command "id"
adb logcat | grep "uid="

adb shell am start -n com.victim/.VulnActivity \
  --es "title" "⚠️ 系统安全警告" --es "content" "您的账户存在异常"
```

### Step 5：判断是否值得报告

- ✅ 成功启动未导出组件 → **高危** → 报告
- ✅ 成功执行任意命令 → **高危/严重** → 报告
- ✅ 成功读取沙箱任意文件 → **高危** → 报告
- ✅ 系统级 App 弹窗内容可控 → **中危** → 报告
- ❌ 仅能启动自身导出组件 / allowBackup=True / 缺少证书绑定 → **忽略** → 不报告（见 五）

---
