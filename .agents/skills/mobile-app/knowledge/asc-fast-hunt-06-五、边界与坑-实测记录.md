# 五、边界与坑（实测记录）

> 来源：CkSKILLS v1 `asc-fast-hunt` §五、边界与坑（实测记录）（迁移至 v2 知识块）

1. **Python ≥ 3.10**：3.9 会在原子分组处直接挂。3.10 能跑，只是指令校验退回普通正则。建议用 3.11+。
2. **裸 `.dex` 不能直接喂**：报 `EOCD not found`（只认 zip/APK 容器）。脱壳产物（frida-dexdump 出的 dex）先打包：
   ```bash
   cd <dex目录> && zip -q dumped.zip classes*.dex && cp dumped.zip dumped.zip.apk
   $ASC/asc findrefs dumped.zip.apk string appkey
   ```
3. **split APK / XAPK**：工具按 zip 内的 `.dex` 条目扫描，`split_config.*.apk` 这类分片需先用 apkeditor 合并，或用 base.apk（业务 dex 通常在 base）。
4. **加固壳包搜不到东西是正常现象**：DEX 里只有壳的 stub 类，命中无意义 → 转 `apk-reversing` 脱壳，不要误判为"没有密钥"。
5. **`--debug` / `--threads` 位置**：挂在 `getclass` / `disassemble` / `listclass` / `getmanifest` / `findrefs` 这一层，写在 apk 前面。`findrefs` 还要写在 `string|type|extends|impl|method|field` 前面：`findrefs --debug <apk> string kw`。写到末尾会报 `unrecognized arguments`。`--threads` 默认 8。
6. **`$` 转义**：Dalvik 内部类名 `LA8/m$a;` 在 shell 里要转义或用单引号包裹。
7. **findrefs 搜引用点非定义**（见 2.2），别把它当"方法列表"用。
8. **别猜类名**：R8 会重命名/裁剪类，猜 `com.x.y.R` 这类名字大概率报 `Class ... not found in APK.`（报错本身是正常信号）。知道包名时先 `listclass --prefix`；从字符串追到类时走 **findrefs → getclass**。类名不存在即说明该类被裁剪（常是资源类/构建期类）。
9. **许可证是 Apache-2.0**：详见「出处声明」。上游历史 force-push 过，更新用 `git fetch origin && git merge --ff-only origin/main`（有本地改动先 stash；被强推覆盖则 `git reset --hard origin/main`），然后 `./.venv/bin/pip install -e .`（0.1.2 依赖变了，必须重装）。不要直接 `git pull`。
10. **Agent 不走 GUI**：0.1.2 GUI 已重构（类树/搜索/多标签编辑器，`--gui`；需 tkinter，本机 Python 未带）。注意 `--gui` 默认**后台子进程**启动——无 tkinter 时子进程静默失败，父进程仍 `exit 0` 且无输出，**不能拿它判断 GUI 可用**。本技能一律走 CLI。
11. **`-o` 关不掉 stdout**：上游 README 写 "`-o` writes results instead of stdout"，**实测 0.1.2.post4 仍会同时打 stdout**（以实测为准）。只要文件就加 `>/dev/null`。`getmanifest` 没有旧脚本的 `--raw`，输出固定是 pretty XML。
12. **`disassemble --method` 要完整签名**：方法名+参数+**返回类型**，如 `--method 'm(Lb1/g;Landroid/os/CancellationSignal;)Landroid/database/Cursor;'`；只给裸方法名（`--method run`）会报 `method not found or signature is not defined`。不确定签名就先不带参数跑一次，从输出 `.method` 行复制。
13. **`--threads` 建议**：默认 8；大包/批量建议 16（上游基准用 10 线程）。多包并行时优先加 `xargs -P` 而不是无限拉高单包线程。

---
