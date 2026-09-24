from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .scan import parse_properties


def _parse_properties(text: str) -> tuple[list[str], dict[str, str]]:
    header: list[str] = []
    props: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("!") or "=" not in line:
            header.append(line)
            continue
        key, value = line.split("=", 1)
        props[key.strip()] = value
    return header, props


def _serialize_properties(header: list[str], props: dict[str, str]) -> str:
    lines = list(header)
    if lines and lines[-1] != "":
        lines.append("")
    for key in sorted(props):
        lines.append(f"{key}={props[key]}")
    return "\n".join(lines) + "\n"


def _looks_untranslated(en_val: str, zh_val: str) -> bool:
    return zh_val.strip() == en_val.strip()


def sync_translations(
    root: Path,
    config: dict[str, Any],
    *,
    force: bool = False,
) -> dict[str, int]:
    en_root = root / config["sourceDir"]
    zh_root = root / config["targetDir"]

    if not en_root.exists():
        raise FileNotFoundError(f"英文资源不存在: {en_root}，请先运行 extract")

    stats = {
        "added": 0,
        "kept": 0,
        "skipped": 0,
        "files": 0,
        "new_files": 0,
    }

    for en_file in en_root.rglob("*"):
        if en_file.name.startswith("."):
            continue
        if not en_file.is_file():
            continue

        rel = en_file.relative_to(en_root)
        zh_file = zh_root / rel
        stats["files"] += 1

        if en_file.suffix != ".properties":
            if zh_file.exists() and not force:
                stats["kept"] += 1
                continue
            zh_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(en_file, zh_file)
            stats["added"] += 1
            if not zh_file.exists():
                stats["new_files"] += 1
            continue

        en_text = en_file.read_text(encoding="utf-8", errors="replace")
        en_header, en_props = _parse_properties(en_text)

        if zh_file.exists():
            zh_header, zh_props = _parse_properties(
                zh_file.read_text(encoding="utf-8", errors="replace")
            )
        else:
            zh_header, zh_props = en_header, {}
            stats["new_files"] += 1

        changed = False
        for key, en_val in en_props.items():
            if key not in zh_props:
                zh_props[key] = en_val
                stats["added"] += 1
                changed = True
            elif force and _looks_untranslated(en_val, zh_props[key]):
                zh_props[key] = en_val
                stats["added"] += 1
                changed = True
            else:
                stats["kept"] += 1

        if changed or not zh_file.exists():
            zh_file.parent.mkdir(parents=True, exist_ok=True)
            zh_file.write_text(_serialize_properties(zh_header, zh_props), encoding="utf-8")

    return stats
