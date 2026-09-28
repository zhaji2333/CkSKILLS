#!/usr/bin/env bash
# Droid ASC (droidasc) 自举脚本 —— 幂等，可重复执行。
# 用法: "$TOOLS/bootstrap.sh"  （TOOLS = 本脚本所在目录）
# 成功后运行环境位于 $TOOLS/env/bin/droidasc。
set -euo pipefail

TOOLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_DIR="$TOOLS_DIR/env"
DROIDASC="$ENV_DIR/bin/droidasc"

if [ -x "$DROIDASC" ]; then
  echo "[asc-bootstrap] ready: $DROIDASC"
  exit 0
fi

# Python >= 3.11 硬门槛（工具用了原子分组正则，3.9/3.10 报 unknown extension ?>）
PY=python3.11
command -v "$PY" >/dev/null 2>&1 || PY=python3
"$PY" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)' || {
  echo "[asc-bootstrap] 需要 Python >= 3.11，当前 $("$PY" -V 2>&1)" >&2
  exit 1
}

# ASC 源码解析：随技能分发的 tools/ASC 优先，开发者本机布局 <cwd>/tools/ASC 兜底
ASC_SRC="$TOOLS_DIR/ASC"
if [ ! -d "$ASC_SRC" ] && [ -d "$PWD/tools/ASC" ]; then
  ASC_SRC="$PWD/tools/ASC"
fi

echo "[asc-bootstrap] 初始化运行环境 -> $ENV_DIR"
"$PY" -m venv "$ENV_DIR"
"$ENV_DIR/bin/pip" -q install --upgrade pip
# 优先安装随技能分发的源码副本；不可用时回退 PyPI 同名包
if ! "$ENV_DIR/bin/pip" -q install "$ASC_SRC" 2>/dev/null; then
  echo "[asc-bootstrap] 本地源码安装失败，回退 PyPI ..."
  "$ENV_DIR/bin/pip" -q install droidasc
fi

"$DROIDASC" --help >/dev/null
echo "[asc-bootstrap] ready: $DROIDASC"
