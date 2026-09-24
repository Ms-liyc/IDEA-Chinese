from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(root: Path) -> dict[str, Any]:
    config_path = root / "config" / "project.json"
    with config_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def resolve_idea_path(config: dict[str, Any], override: str | None = None) -> Path:
    if override:
        path = Path(override)
        if not path.exists():
            raise FileNotFoundError(f"指定的 IDEA 路径不存在: {path}")
        return path

    for candidate in config.get("ideaPaths", []):
        path = Path(candidate)
        if path.exists():
            return path

    raise FileNotFoundError(
        "未找到 IDEA 安装目录。请通过 --idea-path 指定，"
        "或在 config/project.json 的 ideaPaths 中添加路径。"
    )
