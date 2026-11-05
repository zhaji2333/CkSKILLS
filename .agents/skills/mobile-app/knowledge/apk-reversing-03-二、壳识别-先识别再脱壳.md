# 二、壳识别（先识别再脱壳）

> 来源：CkSKILLS v1 `apk-reversing` §二、壳识别（先识别再脱壳）（迁移至 v2 知识块）

**快速判断**：
```bash
unzip -l origin.apk | grep -iE "\.so$|stub|wrapper"
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
