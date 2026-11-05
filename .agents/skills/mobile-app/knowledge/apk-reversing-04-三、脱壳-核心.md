# 三、脱壳（核心）

> 来源：CkSKILLS v1 `apk-reversing` §三、脱壳（核心）（迁移至 v2 知识块）

### 方式 1：模拟器 + Frida dump（最通用，推荐）

```bash
adb push frida-server /data/local/tmp/
adb shell "chmod 755 /data/local/tmp/frida-server && /data/local/tmp/frida-server &"
adb install origin.apk
frida-dexdump -U -f <package> -o dex/
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
unzip -o origin.apk -d apktool_out && ls apktool_out/assets/apps/*/www/
```

---
