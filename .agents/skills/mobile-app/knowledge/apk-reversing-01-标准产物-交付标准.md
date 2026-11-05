# 标准产物（交付标准）

> 来源：CkSKILLS v1 `apk-reversing` §标准产物（交付标准）（迁移至 v2 知识块）

```
reversing/<package>/
├── jadx_out/          # Java 源码（JADX 反编译，必须是真实代码而非 stub）
├── apktool_out/       # smali + 资源 + AndroidManifest（apktool）
├── dex/               # 脱壳后的 dex（未合并进 jadx 时单独留档）
├── lib/               # 全部 so（arm64-v8a 优先，交 IDA 9.5 无头模式分析）
├── assets/            # H5/JS/证书/密钥/配置等资源
├── origin.apk         # 原始 APK 存档
└── report.md          # 壳类型 / 脱壳方式 / 产物清单 / 未还原项
```

**交付检查**：`jadx_out` 里能 grep 到真实特征串（appKey/secret/接口域名）、`lib/` 的 so 可被 **IDA 9.5 无头模式**打开并搜导出表、`assets/` 的 H5 完整——满足即交付 `android-security-audit`。

---
