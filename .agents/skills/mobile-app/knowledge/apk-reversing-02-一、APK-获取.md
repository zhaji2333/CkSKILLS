# 一、APK 获取

> 来源：CkSKILLS v1 `apk-reversing` §一、APK 获取（迁移至 v2 知识块）

```bash
adb shell pm list packages | grep <关键词>            # 找包名
adb shell pm path <package>                           # 拿到 APK 路径
adb pull <路径> origin.apk                            # 拉取

```

- 优先取**最新版本**（厂商 SRC 要求应用商店最新版）
- 同一 App 多渠道包（小米/华为/Google Play）差异可能影响脱壳难度，可换渠道试

---
