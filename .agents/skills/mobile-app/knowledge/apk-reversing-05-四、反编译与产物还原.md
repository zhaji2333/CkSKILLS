# 四、反编译与产物还原

> 来源：CkSKILLS v1 `apk-reversing` §四、反编译与产物还原（迁移至 v2 知识块）

```bash
jadx -d jadx_out origin.apk
jadx -d jadx_out dex/

apktool d origin.apk -o apktool_out

cp -r apktool_out/lib lib/

cp -r apktool_out/assets assets/
```

- **so 层**：`lib/arm64-v8a/` 优先；**交给 IDA 9.5 无头模式（idalib + 官方 MCP）分析**（`open_database` 打开 → `execute_python` 枚举 JNI 导出 → 反编译拿伪 C）；导出表搜 `Java_` 前缀（静态注册）或 `JNI_OnLoad`/`RegisterNatives`（动态注册）——对应 `android-security-audit` 一、1.3 与 三、Native/内存安全深挖
- **H5 层**：`assets/` 下 HTML/JS 搜加密库（JSEncrypt/CryptoJS）与密钥常量；动态加载的远程 H5 记录加载 URL——对应 `android-security-audit` 一、1.4 H5/JS 层追踪
- **签名/证书**：`META-INF/*.RSA`、`res/raw/` 下的证书与密钥，供重打包/校验分析

---
