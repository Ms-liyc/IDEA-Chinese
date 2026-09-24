from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .scan import load_tree_index, parse_properties


@dataclass
class GapReport:
    missing_files: list[str] = field(default_factory=list)
    partial_files: list[tuple[str, int, list[str]]] = field(default_factory=list)
    untranslated_keys: list[str] = field(default_factory=list)
    orphan_files: list[str] = field(default_factory=list)
    en_stats: dict[str, int] = field(default_factory=dict)
    zh_stats: dict[str, int] = field(default_factory=dict)

    @property
    def total_missing_keys(self) -> int:
        return sum(count for _, count, _ in self.partial_files)

    def summary(self) -> str:
        missing_key_count = sum(c for _, c, _ in self.partial_files)
        lines = [
            "=== 汉化缺口报告 ===",
            f"英文资源: {self.en_stats.get('files', 0)} 文件 / {self.en_stats.get('keys', 0)} 键",
            f"中文资源: {self.zh_stats.get('files', 0)} 文件 / {self.zh_stats.get('keys', 0)} 键",
            f"完全缺失的文件: {len(self.missing_files)}",
            f"部分缺失的文件: {len(self.partial_files)}（共 {missing_key_count} 个键）",
            f"与英文相同的未译键: {len(self.untranslated_keys)}",
            f"中文多余文件: {len(self.orphan_files)}",
        ]

        if self.missing_files:
            lines.append("")
            lines.append("完全缺失的文件（前 20）:")
            for rel in self.missing_files[:20]:
                lines.append(f"  - {rel}")

        if self.partial_files:
            lines.append("")
            lines.append("部分缺失最多的文件（前 20）:")
            for rel, count, _ in sorted(self.partial_files, key=lambda x: -x[1])[:20]:
                lines.append(f"  - {rel}: 缺 {count} 键")

        if self.untranslated_keys:
            lines.append("")
            lines.append("仍为英文的键（前 20）:")
            for item in self.untranslated_keys[:20]:
                lines.append(f"  - {item}")

        coverage = 0.0
        en_keys = self.en_stats.get("keys", 0)
        if en_keys:
            missing_in_partial = sum(c for _, c, _ in self.partial_files)
            still_english = len(self.untranslated_keys)
            translated = en_keys - missing_in_partial - still_english
            coverage = max(0.0, min(100.0, translated / en_keys * 100))
        lines.append("")
        lines.append(f"估算覆盖率: {coverage:.1f}%（按 properties 键计）")
        return "\n".join(lines)


def _index_stats(index) -> dict[str, int]:
    keys = 0
    props = 0
    html = 0
    for rel, content in index.files.items():
        if rel.endswith(".properties"):
            props += 1
            keys += len(parse_properties(content.decode("utf-8", errors="replace")))
        elif rel.endswith(".html"):
            html += 1
    return {"files": len(index.files), "properties": props, "keys": keys, "html": html}


def _looks_untranslated(en_val: str, zh_val: str) -> bool:
    en = en_val.strip()
    zh = zh_val.strip()
    if not zh:
        return False
    return en == zh and any(ch.isalpha() for ch in en)


def build_gap_report(root: Path, config: dict[str, Any]) -> GapReport:
    en_root = root / config["sourceDir"]
    zh_root = root / config["targetDir"]
    report = GapReport()

    if not en_root.exists():
        report.missing_files.append("请先运行 extract 提取英文资源")
        return report

    en_index = load_tree_index(en_root)
    zh_index = load_tree_index(zh_root) if zh_root.exists() else load_tree_index(Path("__missing__"))

    report.en_stats = _index_stats(en_index)
    report.zh_stats = _index_stats(zh_index)

    for rel, en_content in sorted(en_index.files.items()):
        if not rel.endswith(".properties"):
            if rel not in zh_index.files:
                report.missing_files.append(rel)
            continue

        en_props = parse_properties(en_content.decode("utf-8", errors="replace"))
        if rel not in zh_index.files:
            report.missing_files.append(rel)
            continue

        zh_props = parse_properties(zh_index.files[rel].decode("utf-8", errors="replace"))
        missing = [k for k in en_props if k not in zh_props or not zh_props[k].strip()]
        untranslated = [
            k for k in en_props
            if k in zh_props and _looks_untranslated(en_props[k], zh_props[k])
        ]

        if missing:
            report.partial_files.append((rel, len(missing), missing[:5]))
        for key in untranslated:
            report.untranslated_keys.append(f"{rel} :: {key}")

    for rel in sorted(zh_index.files):
        if rel not in en_index.files:
            report.orphan_files.append(rel)

    return report


def write_gap_report(root: Path, config: dict[str, Any], report: GapReport) -> Path:
    out_dir = root / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / "gap-report.json"

    payload = {
        "missing_files": report.missing_files,
        "partial_files": [
            {"file": rel, "missing_count": count, "sample_keys": sample}
            for rel, count, sample in report.partial_files
        ],
        "untranslated_keys": report.untranslated_keys,
        "orphan_files": report.orphan_files,
        "en_stats": report.en_stats,
        "zh_stats": report.zh_stats,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    out_md = out_dir / "gap-report.md"
    out_md.write_text(report.summary(), encoding="utf-8")
    return out_json
