# 三、标准工作流（快筛循环）

> 来源：CkSKILLS v1 `asc-fast-hunt` §三、标准工作流（快筛循环）（迁移至 v2 知识块）

### Step 0：壳预检（30 秒，决定要不要转 apk-reversing）

```bash
unzip -l <apk> | grep -iE "libshella|libjiagu|libSecShell|libexec|libtprt|com/stub"
$ASC/asc getmanifest <apk> | grep -oE 'android:name="[A-Za-z0-9._]*Application[A-Za-z0-9._]*"'
$ASC/asc getclass <apk> <上一步的入口类> | head -30     # 是 stub 包装类 = 有壳
```

- **判定**：`lib/` 有壳 so、或入口类是 stub（`com.stub.StubApp` 等）、或 getclass 读到的 Application 是空壳 → **有壳，转 `apk-reversing` 脱壳**，脱壳产物再回到本技能快筛
- **无壳** → 直接进 Step 1，全程不需要全量反编译

### Step 1：Manifest 秒读（攻击面清单）

```bash
$ASC/asc getmanifest <apk> > /tmp/manifest.xml
grep -B3 -A8 'exported="true"' /tmp/manifest.xml                     # 导出组件
grep -oE 'android:scheme="[^"]+"' /tmp/manifest.xml | sort -u        # Deep Link scheme
grep -oE 'android:name="android.permission.[^"]+"' /tmp/manifest.xml | sort -u  # 权限面
grep -iE 'android:process|sharedUserId|allowBackup|debuggable' /tmp/manifest.xml
```

产出：导出 Activity/Service/Receiver/Provider 清单 + scheme 清单 → **交棒 `android-security-audit` 二、静态分析**（组件安全部分）；本技能继续做密钥/接口定位。

### Step 2：关键词矩阵搜索（核心，一波流）

按组批量搜索，每组存盘通读：

```bash
ASC=$HOME/tools/ASC
APK=<target.apk>

for kw in appkey appKey app_secret appSecret secret_key access_key api_key ak_sk client_secret; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

for kw in sign signature signKey md5 sha1 sha256 hmac RSA AES PUBLIC.CRYPTO_PUBLIC; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

for kw in https:// http:// /api/ /v1/ /v2/ Authorization Bearer Cookie userToken; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw -o /tmp/refs_$(echo $kw|tr -d '/:.').txt >/dev/null
done

for kw in debug test internal backdoor admin bypass __dev__ mock; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done

for kw in appId appid AK SK push_key map_key accessKeyId endpoint bucket; do
  echo "### $kw"; $ASC/asc findrefs $APK string $kw
done
```

**关键技巧**：
- 命中收敛不了（如 `secret` 几百条）→ 换更长的特征串（`app_secret`、`client_secret`）或加限定词（`secret_key`）
- 关注**方法名异常**的命中：`LA8/m$a;->b` 这种混淆单字母类 + 命中 `appkey` = 签名工具类，直接进 Step 3
- **URL 类命中最有价值**：拿到接口域名/路径清单后，`recon-js-analysis` 测绘资产、`api-protocol-security` 打接口
- 命中即存档：`-o /tmp/refs_xxx.txt >/dev/null`，后续读文件，避免重复搜索，也避免 stdout 把命中再打一遍

### Step 3：按需读实现（getclass）

```bash
$ASC/asc getclass $APK LA8/m\$a\; -o /tmp/A8_m_a.java
```

读的时候盯四件事：
1. **加密调用**：`MessageDigest.getInstance("MD5"/"SHA-1")`、`Cipher.getInstance("AES/ECB"...)`、`java.security.Signature`、`KeyGenerator`
2. **拼接顺序**：`md5(appId + appKey + ts)` 这类参数拼接 → 直接决定能否 Python 重写
3. **常量来源**：密钥是硬编码字符串常量、还是从 `Build`/`SharedPreferences`/`native` 取（后者要转 SO 层追踪）
4. **参数来源**：是否为外部可控（Intent extra / Deep Link 参数 / 网络响应）

> ⚠️ 第 4 点要克制：DAD 会给出错误类型（见 2.3），**别拿这里的类型声明确认"这个值是什么、从哪来"**。此步只建立"疑似外部可控"的假设，确认可达性与数据流必须用 JADX 产物复核。

⚠️ **shell 转义**：Dalvik 类名含 `$`（内部类）时必须转义或加引号——`LA8/m\$a\;` 或 `'LA8/m$a;'`。

> 需要**指令级细节**（混淆/内联/寄存器操作，Java 反编译失真时）用 0.1.2 的 `disassemble` 出 smali：`$ASC/asc disassemble $APK <类> [--debuginfo] [--method '<签名>']`。它比 `getclass` 更接近真实字节码，但仍无类型/数据流语义。

### Step 4：追引用链（找调用方与数据流）

```bash
$ASC/asc findrefs $APK method <方法名> --class <类> --fuzzy-class

$ASC/asc findrefs $APK field <字段名>

$ASC/asc findrefs $APK type com.x.net.ApiService
```

沿"密钥常量 → 签名方法 → 业务接口调用"三跳走完，就能拼出**完整攻击链**。每一跳都记录 `dex | 类->方法`，这是后续复现与报告的证据。

### Step 5：出链归档与交棒

```
1. 线索写入 CLUEBOARD：hunts/<目标>/CLUEBOARD.md（调用 hunt-clueboard）
   - 记录: APK 路径与版本、包名、命中类/方法、命中关键词、dex 分片名
   - 否定证据也要写（"搜 appkey 无硬编码命中，疑为动态下发"）
2. 拿到「密钥 + 签名算法 + 接口」→ 交棒 android-security-audit 一、密钥追踪专项：
   - Python 重写签名 → curl 未授权调接口 → 拉真实业务数据 = 成洞
3. 拿到「接口域名清单」→ 交棒 recon-js-analysis（资产测绘）+ api-protocol-security（接口测试）
4. 命中「命令执行/文件读取/JSBridge」类字符串与类 → 交棒 android-security-audit 二/三 深挖验证
5. 需要精读混淆逻辑或跨类数据流 → 交棒 apk-reversing 全量反编译
6. **native 算法/实现确认（大包、Java 调用点已明确）→ 直接交棒 android-security-audit 三（IDA 9.5 无头），跳过 JADX 全量**（ASC→IDA 抄近路，见 AGENTS.md 3.1）
```

---
