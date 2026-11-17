#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""kb 数据层索引生成 / 一致性校验（仅标准库，macOS 自带 Python3 可直接跑）。

用法：
    python3 tools/kb_index.py            # 扫描 kb/，重新生成三个索引
    python3 tools/kb_index.py --check    # 只校验现有索引与数据是否一致；不一致退出码 1

生成物：
    kb/vuln/INDEX.md            CVE/漏洞条目总表（分类计数 + 分节条目表）
    kb/vuln/INDEX-<分类>.md     分类条目 >200 行时拆出的独立表（当前为 middleware）
    kb/dict/INDEX.md            字典索引（路径 | 行数 | 描述 | 用途 | 标签）
    kb/payload/INDEX.md         载荷索引（同上）

"""

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_KB_ROOT = REPO_ROOT / "kb"

GENERATOR = "python3 tools/kb_index.py"

# 单个分类的条目表超过该行数就拆到 kb/vuln/INDEX-<分类>.md
VULN_INLINE_MAX_ROWS = 200

META_FILENAME = "_meta.yaml"
INDEX_NAME_RE = re.compile(r"^INDEX(-[A-Za-z0-9_-]+)?\.md$")
FRONTMATTER_RE = re.compile(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.S)


# ---------------------------------------------------------------------------
# 通用小工具
# ---------------------------------------------------------------------------


def read_text(path):
    """按 UTF-8 读取文本；坏字节用替换字符兜底，不让单个文件打断索引生成。"""
    return path.read_text(encoding="utf-8", errors="replace")


def fmt_int(value):
    return "{:,}".format(int(value))


def human_size(num_bytes):
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024.0 or unit == "GB":
            if unit == "B":
                return "{} B".format(int(size))
            return "{:.1f} {}".format(size, unit)
        size /= 1024.0
    return "{:.1f} GB".format(size)


def unquote(value):
    """去掉 YAML/前端 matter 里值的成对引号。只处理最简的单双引号。"""
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        quote = text[0]
        inner = text[1:-1]
        if quote == '"':
            inner = inner.replace('\\"', '"').replace("\\\\", "\\")
        return inner
    return text


def md_cell(value):
    """Markdown 表格单元格：压平空白、转义竖线、空值统一为破折号。"""
    text = " ".join(str(value).split())
    text = text.replace("|", "\\|")
    return text if text else "—"


def count_newlines(path):
    """等同 `wc -l`（数 \\n 字节），用于 _meta 未收录的文件。"""
    try:
        return path.read_bytes().count(b"\n")
    except OSError:
        return 0


def looks_binary(path):
    try:
        with open(str(path), "rb") as handle:
            return b"\x00" in handle.read(8192)
    except OSError:
        return False


def split_table_row(line):
    """把 `| a | b |` 拆成单元格列表，尊重 `\\|` 转义。"""
    cells = []
    current = []
    index = 0
    while index < len(line):
        char = line[index]
        if char == "\\" and index + 1 < len(line):
            current.append(line[index:index + 2])
            index += 2
            continue
        if char == "|":
            cells.append("".join(current))
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    cells.append("".join(current))
    return cells


def count_table_rows(text):
    """统计明细表（表头首列为 ID / 路径）的数据行，分类计数表不计入。"""
    rows = 0
    header = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = None
            continue
        if re.match(r"^\|\s*-+\s*\|", stripped):
            continue
        cells = [cell.strip() for cell in split_table_row(stripped)[1:-1]]
        if not cells:
            continue
        if header is None:
            header = cells
            continue
        if header[0] in ("ID", "路径"):
            rows += 1
    return rows


# ---------------------------------------------------------------------------
# 漏洞库（kb/vuln）
# ---------------------------------------------------------------------------


def parse_frontmatter(text):
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    fields = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = unquote(value)
    return fields


def collect_vuln_records(vuln_root):
    records = []
    for category_dir in sorted(
        (path for path in vuln_root.iterdir() if path.is_dir()),
        key=lambda path: path.name.lower(),
    ):
        for path in sorted(category_dir.rglob("*.md"), key=lambda item: item.as_posix()):
            rel = path.relative_to(vuln_root).as_posix()
            fields = parse_frontmatter(read_text(path))
            records.append(
                {
                    "category": category_dir.name,
                    "id": fields.get("id") or path.stem,
                    "severity": (fields.get("severity") or "UNKNOWN").strip().upper(),
                    "product": fields.get("product") or path.parent.name,
                    "title": fields.get("title") or path.stem,
                    "rel": rel,
                }
            )
    return records


def vuln_table(records):
    lines = [
        "| ID | severity | product | 标题 | 相对路径 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for record in records:
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                md_cell(record["id"]),
                md_cell(record["severity"]),
                md_cell(record["product"]),
                md_cell(record["title"]),
                md_cell(record["rel"]),
            )
        )
    return lines


def vuln_header_note():
    return [
        "# 漏洞库索引（自动生成，勿手改）",
        "",
        "> 生成：`{}`；数据目录：`kb/`。".format(GENERATOR),
        "> **用法**：先在本表按 ID / 产品 / 标题关键词定位，再只打开命中的单条 "
        "`kb/vuln/<相对路径>`；**禁止通读** `kb/vuln/`。",
        "> **证据纪律**：CVE 编号 / 影响版本 / 修复版本以厂商公告或 NVD 为准；"
        "条目里的 PoC 必须本地复现后才可写进报告，未复现只能标「疑似/待验证」"
        "（详见 `kb/README.md`）。",
        "",
    ]


def build_vuln_indexes(kb_root, problems):
    """返回 (索引文件名 -> 内容, 统计 dict)。"""
    vuln_root = kb_root / "vuln"
    if not vuln_root.is_dir():
        raise SystemExit("找不到 {}，未找到 kb/vuln 数据目录。".format(vuln_root))

    records = collect_vuln_records(vuln_root)
    categories = sorted({record["category"] for record in records}, key=str.lower)
    by_category = {}
    for category in categories:
        rows = [record for record in records if record["category"] == category]
        rows.sort(
            key=lambda record: (
                record["product"].lower(),
                record["id"].lower(),
                record["rel"],
            )
        )
        by_category[category] = rows

    expected = {}
    main_lines = vuln_header_note()
    main_lines.extend(
        [
            "## 分类计数",
            "",
            "| 分类 | 条目数 | CRITICAL | HIGH | MEDIUM | 其它 | 索引 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    split_categories = {}
    total_severity = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "OTHER": 0}
    for category in categories:
        rows = by_category[category]
        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "OTHER": 0}
        for record in rows:
            if record["severity"] in ("CRITICAL", "HIGH", "MEDIUM"):
                severity_counts[record["severity"]] += 1
            else:
                severity_counts["OTHER"] += 1
        for key in severity_counts:
            total_severity[key] += severity_counts[key]
        if len(rows) > VULN_INLINE_MAX_ROWS:
            split_categories[category] = rows
            index_cell = "[INDEX-{}.md](INDEX-{}.md)".format(category, category)
        else:
            index_cell = "本页"
        main_lines.append(
            "| {} | {} | {} | {} | {} | {} | {} |".format(
                md_cell(category),
                len(rows),
                severity_counts["CRITICAL"],
                severity_counts["HIGH"],
                severity_counts["MEDIUM"],
                severity_counts["OTHER"],
                index_cell,
            )
        )
    main_lines.append(
        "| **合计** | **{}** | {} | {} | {} | {} | - |".format(
            len(records),
            total_severity["CRITICAL"],
            total_severity["HIGH"],
            total_severity["MEDIUM"],
            total_severity["OTHER"],
        )
    )
    main_lines.append("")

    for category in categories:
        rows = by_category[category]
        if category in split_categories:
            main_lines.extend(
                [
                    "## {}（{} 条）".format(category, len(rows)),
                    "",
                    "> 条目过多（> {} 行），独立成表："
                    "**[INDEX-{}.md](INDEX-{}.md)**".format(
                        VULN_INLINE_MAX_ROWS, category, category
                    ),
                    "",
                ]
            )
            split_lines = [
                "# 漏洞索引：{}（{} 条）".format(category, len(rows)),
                "",
                "> 生成：`{}`；数据目录：`kb/`。".format(GENERATOR),
                "> 路径相对于 `kb/vuln/`；返回 [INDEX.md](INDEX.md)。",
                "",
            ]
            split_lines.extend(vuln_table(rows))
            split_lines.append("")
            expected["vuln/INDEX-{}.md".format(category)] = "\n".join(split_lines)
        else:
            main_lines.extend(
                [
                    "## {}（{} 条）".format(category, len(rows)),
                    "",
                ]
            )
            main_lines.extend(vuln_table(rows))
            main_lines.append("")

    expected["vuln/INDEX.md"] = "\n".join(main_lines)
    stats = {
        "records": len(records),
        "categories": {category: len(by_category[category]) for category in categories},
        "split": sorted(split_categories),
        "severity": total_severity,
    }
    return expected, stats


# ---------------------------------------------------------------------------
# 字典 / 载荷（kb/dict、kb/payload）
# ---------------------------------------------------------------------------


def parse_meta(path):
    """最小 _meta.yaml 解析器：只认 category/subcategory/description/tags/authorization
    与 files[name,lines,description,usage,tags] 这套结构，不依赖 PyYAML。"""
    top = {}
    entries = []
    current = None
    try:
        lines = read_text(path).splitlines()
    except OSError:
        return top, entries

    for raw in lines:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("- name:"):
            current = {"name": unquote(line.split(":", 1)[1])}
            entries.append(current)
            continue
        if line[:2] in ("  ", "\t") and current is not None:
            body = line.strip()
            if ":" in body:
                key, value = body.split(":", 1)
                current[key.strip()] = unquote(value)
            continue
        if not line.startswith((" ", "-")) and ":" in line:
            key, value = line.split(":", 1)
            top[key.strip()] = unquote(value)
            current = None
    return top, entries


def collect_metas(root):
    metas = {}
    for dirpath, _dirnames, filenames in os.walk(str(root)):
        if META_FILENAME in filenames:
            directory = Path(dirpath)
            metas[directory] = parse_meta(directory / META_FILENAME)
    return metas


def section_of(rel_path):
    return rel_path.split("/", 1)[0] if "/" in rel_path else ""


def row_line_cell(row):
    text = str(row["lines"])
    if row["lines_source"] == "wc":
        text += "*"
    return text


def catalog_table(rows):
    lines = [
        "| 路径 | 行数 | 描述 | 用途 | 标签 |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {} | {} | {} | {} | {} |".format(
                md_cell(row["path"]),
                md_cell(row_line_cell(row)),
                md_cell(row["description"]),
                md_cell(row["usage"]),
                md_cell(row["tags"]),
            )
        )
    return lines


def build_catalog_index(kb_root, name, problems):
    """name 为 dict / payload。返回 (索引文件名 -> 内容, 统计 dict)。"""
    root = kb_root / name
    if not root.is_dir():
        raise SystemExit("找不到 {}，未找到对应数据目录。".format(root))

    metas = collect_metas(root)
    rows = []
    referenced = set()
    seen = set()
    subcategories = {}

    for meta_dir in sorted(metas, key=lambda path: path.as_posix()):
        meta_top = metas[meta_dir][0]
        rel_dir = meta_dir.relative_to(root).as_posix()
        section_key = "" if rel_dir == "." else rel_dir.split("/", 1)[0]
        subcategory = (meta_top.get("subcategory") or "").strip()
        if subcategory and subcategory.lower() != section_key.lower():
            subcategories.setdefault(section_key, set()).add(subcategory)
        for entry in metas[meta_dir][1]:
            entry_name = (entry.get("name") or "").strip()
            if not entry_name:
                continue
            target = meta_dir / entry_name
            try:
                rel = target.relative_to(root).as_posix()
            except ValueError:
                problems.append("{}：_meta 条目越界（{}）".format(meta_dir, entry_name))
                continue
            if target in seen:
                # 同一文件被多处 _meta 重复声明时只保留先出现的条目
                continue
            seen.add(target)
            is_dir = entry_name.endswith("/")
            exists = target.is_dir() if is_dir else target.is_file()
            if not exists:
                problems.append(
                    "{}：_meta 声明的{}不存在".format(
                        rel, "目录" if is_dir else "文件"
                    )
                )
                continue
            display_rel = rel + "/" if is_dir and not rel.endswith("/") else rel
            declared = (entry.get("lines") or "").strip()
            if declared.isdigit():
                row_lines = int(declared)
                lines_source = "meta"
            elif is_dir:
                row_lines = 0
                lines_source = "meta"
            else:
                row_lines = count_newlines(target)
                lines_source = "wc"
            rows.append(
                {
                    "path": display_rel,
                    "is_dir": is_dir,
                    "lines": row_lines,
                    "lines_source": lines_source,
                    "description": entry.get("description", ""),
                    "usage": entry.get("usage", ""),
                    "tags": entry.get("tags", ""),
                    "binary": (not is_dir) and looks_binary(target),
                }
            )
            if not is_dir:
                referenced.add(target)

    # _meta 未收录的数据文件：用 wc -l 补行数，并在索引里标 *
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        if not path.is_file():
            continue
        if path.parent == root and INDEX_NAME_RE.match(path.name):
            continue
        if path.name == META_FILENAME:
            continue
        if path in referenced or path in seen:
            continue
        rel = path.relative_to(root).as_posix()
        binary = looks_binary(path)
        rows.append(
            {
                "path": rel,
                "is_dir": False,
                "lines": count_newlines(path),
                "lines_source": "wc",
                "description": (
                    "（_meta 未收录；二进制文件，行数无实际意义）"
                    if binary
                    else "（_meta 未收录，行数由 wc -l 实测）"
                ),
                "usage": "",
                "tags": "",
                "binary": binary,
            }
        )

    sections = {}
    for row in rows:
        sections.setdefault(section_of(row["path"]), []).append(row)
    for section_rows in sections.values():
        section_rows.sort(key=lambda item: item["path"])

    root_top = metas.get(root, ({}, []))[0]
    label = "字典" if name == "dict" else "载荷"
    index_name = "{}/INDEX.md".format(name)

    content = [
        "# {}索引（自动生成，勿手改）".format(label),
        "",
        "> 生成：`{}`；数据目录：`kb/`。".format(GENERATOR),
        "> **用法**：先 grep 本表（路径 / 描述 / 用途 / 标签）定位文件，再只取需要的行段："
        "`sed -n '1,100p' kb/{}/<路径>`、`shuf -n 50 kb/{}/<路径>`；"
        "**禁止把整文件读入上下文**。".format(name, name),
        "> 行数取自各级 `_meta.yaml`；带 `*` 的行表示该文件 `_meta` 未收录、行数由 "
        "`wc -l` 实测。路径以 `/` 结尾的行是 `_meta` 里的目录汇总条目，"
        "其下明细见同前缀各行。",
    ]
    if root_top.get("description"):
        content.append("> 数据说明：{}".format(root_top["description"]))
    if root_top.get("authorization"):
        content.append("> 授权说明：{}".format(root_top["authorization"]))
    content.append("")

    section_names = sorted(sections, key=lambda key: (key == "", key.lower()))
    content.extend(
        [
            "## 分类计数",
            "",
            "| 分类 | 文件数 | 总行数 |",
            "| --- | --- | --- |",
        ]
    )
    total_files = 0
    total_lines = 0
    section_stats = {}
    for section in section_names:
        section_rows = sections[section]
        file_rows = [row for row in section_rows if not row["is_dir"]]
        dir_rows = len(section_rows) - len(file_rows)
        lines = sum(row["lines"] for row in file_rows)
        total_files += len(file_rows)
        total_lines += lines
        section_stats[section] = {
            "files": len(file_rows),
            "dir_rows": dir_rows,
            "lines": lines,
        }
        content.append(
            "| {} | {} | {} |".format(
                md_cell(section or "根目录"), len(file_rows), fmt_int(lines)
            )
        )
    content.append(
        "| **合计** | **{}** | {} |".format(total_files, fmt_int(total_lines))
    )
    content.append("")

    for section in section_names:
        section_rows = sections[section]
        # 根目录的说明已在页首写过，这里不再重复
        section_top = (
            {} if section == "" else metas.get(root / section, ({}, []))[0]
        )
        stats = section_stats[section]
        heading = section or "根目录"
        subcat_text = "；子分类：" + ", ".join(sorted(subcategories.get(section, set())))
        content.append(
            "## {}（{} 文件 / {} 行{}）".format(
                heading,
                stats["files"],
                fmt_int(stats["lines"]),
                subcat_text if subcategories.get(section) else "",
            )
        )
        content.append("")
        if section_top.get("description"):
            content.append("> {}".format(section_top["description"]))
        if section_top.get("tags"):
            content.append("> 标签：{}".format(section_top["tags"]))
        if section_top.get("authorization"):
            content.append("> 授权说明：{}".format(section_top["authorization"]))
        if section_top.get("description") or section_top.get("tags"):
            content.append("")
        content.extend(catalog_table(section_rows))
        content.append("")

    stats = {
        "name": name,
        "files": total_files,
        "lines": total_lines,
        "dir_rows": sum(item["dir_rows"] for item in section_stats.values()),
        "rows": len(rows),
        "sections": len(section_names),
        "meta_count": len(metas),
        "sections_detail": section_stats,
    }
    return {index_name: "\n".join(content)}, stats


# ---------------------------------------------------------------------------
# 校验（--check）
# ---------------------------------------------------------------------------


def check_referenced_paths(kb_root, rel_index, text, failures):
    """校验某个索引里表格引用的路径是否都还在（防索引指向已删文件）。"""
    if rel_index.startswith("vuln/"):
        base = kb_root / "vuln"
        path_cell = -1
    elif rel_index.startswith("dict/"):
        base = kb_root / "dict"
        path_cell = 0
    elif rel_index.startswith("payload/"):
        base = kb_root / "payload"
        path_cell = 0
    else:
        return
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|\s*-+\s*\|", stripped):
            continue
        cells = [cell.strip() for cell in split_table_row(stripped)[1:-1]]
        if not cells or cells[0] in ("ID", "路径", "分类"):
            continue
        target_rel = cells[path_cell].replace("\\|", "|")
        if target_rel in ("—", "-", "本页") or col_is_link(target_rel):
            continue
        # 分类计数表不是文件清单：只处理像路径的单元格
        if "/" not in target_rel and "." not in target_rel:
            continue
        if not (base / target_rel).exists():
            failures.append(
                "{}：索引引用的路径不存在（{}）".format(rel_index, target_rel)
            )


def col_is_link(cell):
    return cell.startswith("[") and "](" in cell


def run_check(kb_root, expected, builder_problems, stats):
    failures = []
    for problem in builder_problems:
        failures.append("数据不一致：{}".format(problem))

    print("[kb-index] 校验 kb/ 数据层索引…")
    for rel in sorted(expected):
        target = kb_root / rel
        if not target.is_file():
            failures.append("缺少索引文件：{}".format(rel))
            print("  [MISS] {}".format(rel))
            continue
        actual = read_text(target)
        wanted = expected[rel]
        if actual == wanted:
            print(
                "  [ OK ] {}（{} 行表项 / {} 行文件）".format(
                    rel, count_table_rows(actual), len(actual.splitlines())
                )
            )
        else:
            failures.append(
                "索引过期：{}（期望 {} 行表项，实际 {}；"
                "运行 {} 重新生成）".format(
                    rel,
                    count_table_rows(wanted),
                    count_table_rows(actual),
                    GENERATOR,
                )
            )
            print(
                "  [STALE] {}（期望 {} 行表项 / 实际 {}）".format(
                    rel, count_table_rows(wanted), count_table_rows(actual)
                )
            )
            check_referenced_paths(kb_root, rel, actual, failures)

    expected_names = set(expected)
    for sub in ("vuln", "dict", "payload"):
        for path in sorted((kb_root / sub).glob("INDEX*.md")):
            rel = path.relative_to(kb_root).as_posix()
            if rel not in expected_names:
                failures.append(
                    "多余的索引文件（数据里已无对应分类）：{}".format(rel)
                )
                print("  [EXTRA] {}".format(rel))

    print()
    print(
        "数据规模：vuln {records} 条 / dict {dict_files} 文件 / payload {payload_files} 文件".format(
            records=stats["vuln"]["records"],
            dict_files=stats["dict"]["files"],
            payload_files=stats["payload"]["files"],
        )
    )
    if failures:
        print()
        print("[FAIL] 发现 {} 个一致性问题：".format(len(failures)))
        for failure in failures:
            print("  - {}".format(failure))
        return 1
    print("[OK] 全部索引与数据一致。")
    return 0


# ---------------------------------------------------------------------------
# 生成（默认模式）
# ---------------------------------------------------------------------------


def data_volume(root):
    files = 0
    total = 0
    for dirpath, _dirnames, filenames in os.walk(str(root)):
        for filename in filenames:
            path = Path(dirpath) / filename
            try:
                total += path.stat().st_size
                files += 1
            except OSError:
                pass
    return files, total


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="生成 / 校验 kb/ 数据层索引（CVE、字典、载荷）"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只校验现有 INDEX 与数据是否一致；不一致时退出码 1",
    )
    parser.add_argument(
        "--kb",
        default=str(DEFAULT_KB_ROOT),
        help="kb 根目录（默认仓库根下的 kb/）",
    )
    args = parser.parse_args(argv)

    kb_root = Path(args.kb).resolve()
    if not kb_root.is_dir():
        print("[kb-index] 找不到 kb 目录：{}".format(kb_root), file=sys.stderr)
        return 2

    builder_problems = []
    expected = {}
    stats = {}

    vuln_files, vuln_stats = build_vuln_indexes(kb_root, builder_problems)
    expected.update(vuln_files)
    stats["vuln"] = vuln_stats

    dict_files, dict_stats = build_catalog_index(kb_root, "dict", builder_problems)
    expected.update(dict_files)
    stats["dict"] = dict_stats

    payload_files, payload_stats = build_catalog_index(
        kb_root, "payload", builder_problems
    )
    expected.update(payload_files)
    stats["payload"] = payload_stats

    if args.check:
        return run_check(kb_root, expected, builder_problems, stats)

    print("[kb-index] 生成 kb/ 数据层索引…")
    for rel in sorted(expected):
        target = kb_root / rel
        content = expected[rel]
        target.parent.mkdir(parents=True, exist_ok=True)
        old = read_text(target) if target.is_file() else None
        if old == content:
            print("  [=] {}（未变化，{} 行表项）".format(rel, count_table_rows(content)))
            continue
        target.write_text(content, encoding="utf-8")
        print(
            "  [+] {}（{} 行表项 / {} 行文件）".format(
                rel, count_table_rows(content), len(content.splitlines())
            )
        )

    category_counts = stats["vuln"]["categories"]
    print()
    print(
        "vuln    : {} 条（{}）".format(
            stats["vuln"]["records"],
            " / ".join(
                "{} {}".format(category, count)
                for category, count in category_counts.items()
            ),
        )
    )
    if stats["vuln"]["split"]:
        print(
            "         拆分独立表：{}".format(
                "、".join(
                    "INDEX-{}.md".format(category)
                    for category in stats["vuln"]["split"]
                )
            )
        )
    print(
        "dict    : {} 个数据文件 / {} 行；{} 个 _meta.yaml；{} 行表项".format(
            stats["dict"]["files"],
            fmt_int(stats["dict"]["lines"]),
            stats["dict"]["meta_count"],
            stats["dict"]["rows"],
        )
    )
    print(
        "payload : {} 个数据文件 / {} 行；{} 个 _meta.yaml；{} 行表项".format(
            stats["payload"]["files"],
            fmt_int(stats["payload"]["lines"]),
            stats["payload"]["meta_count"],
            stats["payload"]["rows"],
        )
    )
    files, size = data_volume(kb_root)
    print("kb/     : {} 个文件 / {}".format(files, human_size(size)))
    if builder_problems:
        print()
        print("[WARN] {} 个数据一致性问题：".format(len(builder_problems)))
        for problem in builder_problems:
            print("  - {}".format(problem))
    return 0


if __name__ == "__main__":
    sys.exit(main())
