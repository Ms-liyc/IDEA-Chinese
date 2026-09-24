from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

LOCALIZABLE_PREFIXES = (
    "messages/",
    "inspectionDescriptions/",
    "intentionDescriptions/",
    "fileTemplates/",
    "postfixTemplates/",
    "tips/",
)

LOCALE_SUFFIX_RE = re.compile(
    r"_(?:zh_CN|zh_TW|zh|ja|ko|en)(?:\.(?:properties|html|xml))?$",
    re.IGNORECASE,
)


@dataclass
class BundleIndex:
    """按语言包路径聚合的资源索引。"""

    files: dict[str, bytes] = field(default_factory=dict)
    sources: dict[str, list[str]] = field(default_factory=dict)
    key_conflicts: dict[str, list[str]] = field(default_factory=dict)

    def add_file(self, rel_path: str, content: bytes, source: str) -> None:
        rel_path = rel_path.replace("\\", "/")
        if rel_path.endswith(".properties"):
            self._merge_properties(rel_path, content, source)
            return
        if rel_path in self.files and self.files[rel_path] != content:
            self.key_conflicts.setdefault(rel_path, []).append(source)
        self.files.setdefault(rel_path, content)
        self.sources.setdefault(rel_path, []).append(source)

    def _merge_properties(self, rel_path: str, content: bytes, source: str) -> None:
        new_props = parse_properties(content.decode("utf-8", errors="replace"))
        if rel_path not in self.files:
            self.files[rel_path] = content
            self.sources[rel_path] = [source]
            return

        existing = parse_properties(self.files[rel_path].decode("utf-8", errors="replace"))
        for key, value in new_props.items():
            if key not in existing:
                existing[key] = value
            elif existing[key] != value:
                conflict_key = f"{rel_path}::{key}"
                self.key_conflicts.setdefault(conflict_key, []).append(source)
        self.files[rel_path] = serialize_properties(existing).encode("utf-8")
        self.sources[rel_path].append(source)


def is_localizable_entry(name: str) -> bool:
    name = name.replace("\\", "/")
    if name.endswith("/"):
        return False
    if not any(name.startswith(prefix) for prefix in LOCALIZABLE_PREFIXES):
        return False
    if LOCALE_SUFFIX_RE.search(name):
        return False
    if name.endswith(".properties") or name.endswith(".html") or name.endswith(".xml"):
        return True
    return False


def parse_properties(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("!") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value
    return result


def serialize_properties(props: dict[str, str]) -> str:
    lines = [f"{key}={value}" for key, value in sorted(props.items())]
    return "\n".join(lines) + ("\n" if lines else "")


def iter_installation_jars(idea_path: Path, *, include_plugins: bool = True) -> Iterable[tuple[Path, Path]]:
    lib_dir = idea_path / "lib"
    if lib_dir.exists():
        for jar in sorted(lib_dir.glob("*.jar")):
            yield jar, jar.relative_to(idea_path)

    if not include_plugins:
        return

    plugins_dir = idea_path / "plugins"
    if not plugins_dir.exists():
        return

    for jar in sorted(plugins_dir.rglob("*.jar")):
        rel = jar.relative_to(idea_path)
        if "localization-zh" in rel.as_posix():
            continue
        yield jar, rel


def find_official_zh_jar(idea_path: Path) -> Path | None:
    candidates = [
        idea_path / "plugins" / "localization-zh" / "lib" / "localization-zh.jar",
        idea_path / "plugins" / "chinese-simplified-language-pack" / "lib" / "chinese-simplified-language-pack.jar",
    ]
    for path in candidates:
        if path.exists():
            return path
    for path in idea_path.rglob("localization-zh.jar"):
        return path
    return None


def scan_jar_index(jar_path: Path, source_label: str) -> BundleIndex:
    index = BundleIndex()
    with zipfile.ZipFile(jar_path, "r") as zf:
        for name in zf.namelist():
            if is_localizable_entry(name):
                index.add_file(name, zf.read(name), source_label)
    return index


def scan_installation(idea_path: Path) -> BundleIndex:
    merged = BundleIndex()
    for jar_path, rel in iter_installation_jars(idea_path):
        part = scan_jar_index(jar_path, rel.as_posix())
        for rel_path, content in part.files.items():
            merged.add_file(rel_path, content, rel.as_posix())
        merged.key_conflicts.update(part.key_conflicts)
    return merged


def write_index(index: BundleIndex, target_dir: Path) -> dict[str, int]:
    if target_dir.exists():
        import shutil

        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)

    stats = {"files": 0, "properties": 0, "html": 0, "xml": 0, "keys": 0}
    for rel_path, content in sorted(index.files.items()):
        out = target_dir / rel_path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(content)
        stats["files"] += 1
        if rel_path.endswith(".properties"):
            stats["properties"] += 1
            stats["keys"] += len(parse_properties(content.decode("utf-8", errors="replace")))
        elif rel_path.endswith(".html"):
            stats["html"] += 1
        elif rel_path.endswith(".xml"):
            stats["xml"] += 1
    return stats


def load_tree_index(root: Path) -> BundleIndex:
    index = BundleIndex()
    if not root.exists():
        return index
    for path in root.rglob("*"):
        if not path.is_file() or path.name.startswith("."):
            continue
        rel = path.relative_to(root).as_posix()
        index.add_file(rel, path.read_bytes(), rel)
    return index
