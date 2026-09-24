from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Any

from .config import resolve_idea_path
from .scan import find_official_zh_jar, is_localizable_entry


def import_official_zh(
    root: Path,
    config: dict[str, Any],
    *,
    idea_path: str | None = None,
    force: bool = False,
) -> Path:
    idea = resolve_idea_path(config, idea_path)
    zh_jar = find_official_zh_jar(idea)
    if zh_jar is None:
        raise FileNotFoundError(
            "未找到官方简体中文语言包（plugins/localization-zh/lib/localization-zh.jar）。"
            "请确认 IDEA 版本 >= 2024.2 且未删除内置语言包。"
        )

    target_dir = root / config["targetDir"]
    marker = target_dir / ".import-meta.txt"

    if target_dir.exists() and marker.exists() and not force:
        print(f"已存在官方导入结果，跳过（使用 --force 覆盖）: {target_dir}")
        return target_dir

    print(f"从官方语言包导入: {zh_jar.relative_to(idea)}")

    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    stats = {"files": 0, "properties": 0, "html": 0, "xml": 0}
    with zipfile.ZipFile(zh_jar, "r") as zf:
        for name in zf.namelist():
            if not is_localizable_entry(name):
                continue
            out = target_dir / name
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(name))
            stats["files"] += 1
            if name.endswith(".properties"):
                stats["properties"] += 1
            elif name.endswith(".html"):
                stats["html"] += 1
            elif name.endswith(".xml"):
                stats["xml"] += 1

    marker.write_text(
        "\n".join(
            [
                f"source={zh_jar}",
                f"idea_path={idea}",
                f"files={stats['files']}",
                f"properties={stats['properties']}",
                f"html={stats['html']}",
                f"xml={stats['xml']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"导入完成: {stats['files']} 个文件 "
        f"({stats['properties']} properties, {stats['html']} HTML, {stats['xml']} XML)"
    )
    return target_dir
