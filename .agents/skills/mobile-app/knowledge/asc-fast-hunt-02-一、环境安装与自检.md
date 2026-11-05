# 一、环境安装与自检

> 来源：CkSKILLS v1 `asc-fast-hunt` §一、环境安装与自检（迁移至 v2 知识块）

**Python ≥ 3.10**（`pyproject` 的下限）。3.11+ 用原子分组正则做指令校验快路径；3.10 编译失败会自动退回普通正则，不再因为 `?>` 整条挂死。3.9 及以下不在支持范围。参考环境：**Python 3.11.14**。0.1.2 起**不再依赖 androguard**：反编译器 DAD 抽成仓库内置 `dadguard`，Manifest 解码走 `axml`，字符串/类名解码走 `mutf8`（`requirements.txt`：`axml==0.0.2`、`mutf8==1.1.0`）。`--gui` 需要 tkinter（本机 Python 未带，只影响 GUI，CLI 正常）。

```bash
ASC=$HOME/tools/ASC
$ASC/asc -h                                 # 看到 getclass/disassemble/listclass/getmanifest/findrefs = 环境正常
$ASC/asc --version                          # 期望 0.1.2.post4
$ASC/asc getmanifest <任意.apk> | head -3   # 打出 <manifest = axml 正常

git clone https://github.com/MG1937/ASC $ASC
cd $ASC && python3.11 -m venv .venv && ./.venv/bin/pip install -e .

pip install droidasc==0.1.2.post4
```

`$ASC/asc` 是薄封装，等价于 `$ASC/.venv/bin/droidasc`。旧的 `asc_manifest` 还在，只是 `getmanifest` 的别名。**本机推荐源码树 + venv**（跟 `main`、依赖可审计、升级可控）；PyPI 包适合"只想快速拿到 `droidasc` 命令"的场景，注意 pin 版本防漂移。

**自检**（开工前确认，有无命中都要无报错）：

```bash
$ASC/asc getmanifest <target.apk> | head -3
$ASC/asc listclass <target.apk> --prefix <包名> | head -3
$ASC/asc findrefs <target.apk> string token | head -3
```

---
