#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""线索板同步检查（rules/66 多 agent 回灌闸）。

用法：
    python3 tools/clueboard_sync_check.py hunts/<目标>
    python3 tools/clueboard_sync_check.py hunts/<目标> --strict

检查项：
  1. CLUEBOARD.md 存在，且 §0–§7 节标题齐全（§8 同步日志仅告警）
  2. dig/<角色>/ 有产物却没有 SYNC.md（子代理未回灌）
  3. 每份 SYNC.md 有 HOST/PATH/KEY/DEAD/NEXT 五行，且带证据路径或 N/A
  4. CLUEBOARD.md 的 mtime 必须晚于所有 dig/*/SYNC.md（回灌已合板）

退出码：0 通过（可含告警）；1 有 FAIL（--strict 时 WARN 也算 FAIL）；2 参数/路径错误。
"""
import argparse
import os
import re
import sys
import time

SKIP_DIG_DIRS = {"lead", "tool", "tools", "tmp"}
SYNC_KEYS = ("HOST", "PATH", "KEY", "DEAD", "NEXT")
KEY_RE = re.compile(r"(?m)^\s*(HOST|PATH|KEY|DEAD|NEXT)\s*[:：]")
PATH_HINT_RE = re.compile(r"(raw|dig|js|资产|报告|hunts)/")
EVIDENCE_RE = re.compile(r"(证据|依据)\s*[:：]")
SECTION_RE = re.compile(r"(?m)^##\s*(\d+)\.")


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def fmt_mtime(ts):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def digest_files(dig_role_dir):
    """该角色目录下除 SYNC/DONE 外是否还有产物。"""
    for root, _dirs, files in os.walk(dig_role_dir):
        for name in files:
            if name in ("SYNC.md", "DONE.md"):
                continue
            return True
    return False


def check(hunt_dir, strict=False):
    fails, warns, oks = [], [], []
    board = os.path.join(hunt_dir, "CLUEBOARD.md")
    if not os.path.isfile(board):
        fails.append(f"缺 CLUEBOARD.md：{board}")
        return fails, warns, oks

    text = read(board)
    sections = {int(n) for n in SECTION_RE.findall(text)}
    missing = [n for n in range(0, 8) if n not in sections]
    if missing:
        fails.append("CLUEBOARD 缺节：" + " ".join(f"§{n}" for n in missing))
    else:
        oks.append("CLUEBOARD §0–§7 齐全")
    if 8 not in sections:
        warns.append("CLUEBOARD 缺 §8 同步日志（多 agent 任务必须记）")
    if "当前焦点" not in text:
        warns.append("CLUEBOARD 缺「当前焦点」行")

    dig_dir = os.path.join(hunt_dir, "dig")
    sync_files = []
    if os.path.isdir(dig_dir):
        for name in sorted(os.listdir(dig_dir)):
            role_dir = os.path.join(dig_dir, name)
            if not os.path.isdir(role_dir) or name in SKIP_DIG_DIRS:
                continue
            sync_path = os.path.join(role_dir, "SYNC.md")
            if os.path.isfile(sync_path):
                sync_files.append(sync_path)
                continue
            if digest_files(role_dir):
                fails.append(f"dig/{name}/ 有产物但缺 SYNC.md（子代理未回灌，rules/66）")
        if not sync_files and not os.path.isdir(os.path.join(dig_dir, "lead")):
            warns.append("没有发现任何 dig/*/SYNC.md（若为单人任务可忽略）")

    for sync_path in sync_files:
        rel = os.path.relpath(sync_path, hunt_dir)
        body = read(sync_path)
        found = {m.group(1) for m in KEY_RE.finditer(body)}
        lacking = [k for k in SYNC_KEYS if k not in found]
        if lacking:
            fails.append(f"{rel} 缺回灌字段：{'/'.join(lacking)}")
            continue
        lines = []
        for line in body.splitlines():
            m = KEY_RE.match(line.strip())
            if m:
                lines.append(line.strip())
        bad = [ln for ln in lines if not (EVIDENCE_RE.search(ln) and PATH_HINT_RE.search(ln))
               and "N/A" not in ln.upper()]
        if bad:
            fails.append(f"{rel} 有 {len(bad)} 行既无证据路径也无 N/A：{bad[0][:60]}")
        else:
            oks.append(f"{rel} 回灌块完整")

    board_mtime = os.path.getmtime(board)
    stale = [(p, os.path.getmtime(p)) for p in sync_files if os.path.getmtime(p) > board_mtime]
    if stale:
        for p, ts in stale:
            fails.append(
                f"CLUEBOARD 早于 {os.path.relpath(p, hunt_dir)}（板 {fmt_mtime(board_mtime)} < SYNC {fmt_mtime(ts)}）"
                " → 回灌未合板"
            )
    elif sync_files:
        oks.append("CLUEBOARD 晚于全部 SYNC.md（已合板）")

    if strict:
        fails.extend(warns)
        warns = []
    return fails, warns, oks


def main():
    ap = argparse.ArgumentParser(description="线索板同步检查（rules/66）")
    ap.add_argument("hunt_dir", nargs="?", default=".", help="任务根目录，如 hunts/<目标>")
    ap.add_argument("--strict", action="store_true", help="告警也判失败")
    args = ap.parse_args()

    hunt_dir = os.path.abspath(args.hunt_dir)
    if not os.path.isdir(hunt_dir):
        print(f"[ERR] 目录不存在：{hunt_dir}", file=sys.stderr)
        return 2

    fails, warns, oks = check(hunt_dir, strict=args.strict)
    print(f"线索板同步检查 · {args.hunt_dir}")
    for msg in fails:
        print(f"  [FAIL] {msg}")
    for msg in warns:
        print(f"  [WARN] {msg}")
    for msg in oks:
        print(f"  [OK]   {msg}")
    if fails:
        print(f"结果：FAIL（{len(fails)} 错误 / {len(warns)} 告警）")
        return 1
    print(f"结果：PASS（0 错误 / {len(warns)} 告警）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
