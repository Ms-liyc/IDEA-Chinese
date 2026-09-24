from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .config import resolve_idea_path
from .scan import scan_installation, write_index


def extract_resources(
    root: Path,
    config: dict[str, Any],
    *,
    idea_path: str | None = None,
    force: bool = False,
) -> Path:
    idea = resolve_idea_path(config, idea_path)
    source_dir = root / config["sourceDir"]
    marker = source_dir / ".extract-meta.txt"

    if source_dir.exists() and marker.exists() and not force:
        print(f"已存在提取结果，跳过（使用 --force 覆盖）: {source_dir}")
        return source_dir

    print(f"扫描 IDEA 安装目录: {idea}")
    print("正在扫描 lib/ 与 plugins/ 下全部 JAR（2024.2+ 模块化结构）...")

    index = scan_installation(idea)
    stats = write_index(index, source_dir)

    meta_lines = [
        f"idea_path={idea}",
        f"scan_mode=full",
        f"files={stats['files']}",
        f"properties={stats['properties']}",
        f"property_keys={stats['keys']}",
        f"html={stats['html']}",
        f"xml={stats['xml']}",
        f"conflicts={len(index.key_conflicts)}",
    ]
    marker.write_text("\n".join(meta_lines) + "\n", encoding="utf-8")

    if index.key_conflicts:
        conflict_log = source_dir / ".key-conflicts.log"
        lines = [f"{key} <- {', '.join(sources)}" for key, sources in sorted(index.key_conflicts.items())]
        summary = f"# 共 {len(lines)} 处值冲突，仅展示前 500 条\n"
        conflict_log.write_text(summary + "\n".join(lines[:500]) + "\n", encoding="utf-8")
        print(f"发现 {len(index.key_conflicts)} 处键值冲突，详见 {conflict_log.relative_to(root)}")

    print(
        f"提取统计: {stats['files']} 个文件, "
        f"{stats['properties']} 个 properties ({stats['keys']} 键), "
        f"{stats['html']} 个 HTML, {stats['xml']} 个 XML"
    )
    return source_dir
