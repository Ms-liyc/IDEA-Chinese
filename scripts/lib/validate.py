from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .scan import load_tree_index, parse_properties

PLACEHOLDER = re.compile(r"\{(\d+)\}")


@dataclass
class ValidationReport:
    missing_files: list[str] = field(default_factory=list)
    missing_keys: list[str] = field(default_factory=list)
    orphan_keys: list[str] = field(default_factory=list)
    placeholder_mismatches: list[str] = field(default_factory=list)
    empty_values: list[str] = field(default_factory=list)
    untranslated_keys: list[str] = field(default_factory=list)
    encoding_issues: list[str] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return bool(
            self.missing_files
            or self.missing_keys
            or self.placeholder_mismatches
            or self.empty_values
            or self.encoding_issues
        )

    def summary(self) -> str:
        lines = ["=== 翻译校验报告 ==="]
        lines.append(f"缺失文件: {len(self.missing_files)}")
        lines.append(f"缺失键: {len(self.missing_keys)}")
        lines.append(f"仍为英文: {len(self.untranslated_keys)}")
        lines.append(f"多余键: {len(self.orphan_keys)}")
        lines.append(f"占位符不一致: {len(self.placeholder_mismatches)}")
        lines.append(f"空译文: {len(self.empty_values)}")
        lines.append(f"编码问题: {len(self.encoding_issues)}")

        def preview(title: str, items: list[str], limit: int = 20) -> None:
            if not items:
                return
            lines.append("")
            lines.append(title)
            for item in items[:limit]:
                lines.append(f"  - {item}")
            if len(items) > limit:
                lines.append(f"  ... 还有 {len(items) - limit} 项")

        preview("缺失文件示例:", self.missing_files)
        preview("缺失键示例:", self.missing_keys)
        preview("仍为英文示例:", self.untranslated_keys)
        preview("占位符不一致示例:", self.placeholder_mismatches)
        preview("空译文示例:", self.empty_values)
        preview("编码问题示例:", self.encoding_issues)
        return "\n".join(lines)


def _looks_untranslated(en_val: str, zh_val: str) -> bool:
    en = en_val.strip()
    zh = zh_val.strip()
    if not zh:
        return False
    return en == zh and any(ch.isalpha() for ch in en)


def validate_translations(
    root: Path,
    config: dict[str, Any],
    *,
    strict: bool = False,
) -> ValidationReport:
    report = ValidationReport()
    en_root = root / config["sourceDir"]
    zh_root = root / config["targetDir"]

    if not en_root.exists():
        report.missing_keys.append("请先运行 extract 提取英文资源")
        return report

    if not zh_root.exists():
        report.missing_keys.append("zh-CN 目录不存在，请先运行 import-zh 或 sync")
        return report

    en_index = load_tree_index(en_root)
    zh_index = load_tree_index(zh_root)

    for rel, en_content in sorted(en_index.files.items()):
        if not rel.endswith(".properties"):
            if rel not in zh_index.files:
                report.missing_files.append(rel)
            continue

        if rel not in zh_index.files:
            report.missing_files.append(rel)
            continue

        en_props = parse_properties(en_content.decode("utf-8", errors="replace"))
        zh_text = zh_index.files[rel].decode("utf-8", errors="replace")
        zh_props = parse_properties(zh_text)

        if "\\u" in zh_text and any(ord(ch) > 127 for ch in zh_text):
            report.encoding_issues.append(f"{rel}: 同时包含 Unicode 转义与中文原文")

        for key, en_val in en_props.items():
            if key not in zh_props:
                report.missing_keys.append(f"{rel} :: {key}")
                continue
            zh_val = zh_props[key].strip()
            if not zh_val:
                report.empty_values.append(f"{rel} :: {key}")
            elif _looks_untranslated(en_val, zh_val):
                report.untranslated_keys.append(f"{rel} :: {key}")
            en_ph = PLACEHOLDER.findall(en_val)
            zh_ph = PLACEHOLDER.findall(zh_val)
            if en_ph != zh_ph:
                report.placeholder_mismatches.append(
                    f"{rel} :: {key} ({en_ph} -> {zh_ph})"
                )

        for key in zh_props:
            if key not in en_props:
                report.orphan_keys.append(f"{rel} :: {key}")

    if strict and (report.missing_files or report.missing_keys):
        pass

    return report
