#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IDEA 汉化组工具集入口。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from lib.config import load_config
from lib.extract import extract_resources
from lib.import_official import import_official_zh
from lib.build import build_plugin
from lib.validate import validate_translations
from lib.report import build_gap_report, write_gap_report


def main() -> int:
    parser = argparse.ArgumentParser(description="IntelliJ IDEA 汉化组工具")
    sub = parser.add_subparsers(dest="command", required=True)

    extract_cmd = sub.add_parser("extract", help="全量扫描 lib/ + plugins/ 提取英文资源")
    extract_cmd.add_argument("--idea-path", help="IDEA 安装目录，默认自动探测")
    extract_cmd.add_argument("--force", action="store_true", help="覆盖已有提取结果")

    import_cmd = sub.add_parser("import-zh", help="从官方 localization-zh.jar 导入中文基线")
    import_cmd.add_argument("--idea-path", help="IDEA 安装目录，默认自动探测")
    import_cmd.add_argument("--force", action="store_true", help="覆盖已有 zh-CN 目录")

    report_cmd = sub.add_parser("report", help="生成汉化缺口报告（对比 en 与 zh-CN）")
    report_cmd.add_argument("--output", action="store_true", help="写入 reports/gap-report.json")

    build_cmd = sub.add_parser("build", help="将 zh-CN 资源打包为语言包插件")
    build_cmd.add_argument("--version", default="1.0.0", help="插件版本号")

    validate_cmd = sub.add_parser("validate", help="校验翻译完整性与格式")
    validate_cmd.add_argument("--strict", action="store_true", help="缺失翻译时返回非零退出码")

    sync_cmd = sub.add_parser("sync", help="将英文新增键同步到 zh-CN（保留已有翻译）")
    sync_cmd.add_argument("--force", action="store_true", help="覆盖 zh-CN 中已存在的英文占位")

    init_cmd = sub.add_parser("init", help="一键初始化：extract + import-zh + sync + report")
    init_cmd.add_argument("--idea-path", help="IDEA 安装目录，默认自动探测")
    init_cmd.add_argument("--force", action="store_true", help="强制覆盖已有数据")

    args = parser.parse_args()
    config = load_config(ROOT)

    if args.command == "extract":
        path = extract_resources(ROOT, config, idea_path=args.idea_path, force=args.force)
        print(f"提取完成: {path}")
        return 0

    if args.command == "import-zh":
        path = import_official_zh(ROOT, config, idea_path=args.idea_path, force=args.force)
        print(f"导入完成: {path}")
        return 0

    if args.command == "report":
        report = build_gap_report(ROOT, config)
        print(report.summary())
        if args.output:
            out = write_gap_report(ROOT, config, report)
            print(f"\n报告已写入: {out}")
        return 0

    if args.command == "build":
        output = build_plugin(ROOT, config, version=args.version)
        print(f"构建完成: {output}")
        return 0

    if args.command == "validate":
        report = validate_translations(ROOT, config, strict=args.strict)
        print(report.summary())
        return 1 if report.has_errors else 0

    if args.command == "sync":
        from lib.sync import sync_translations

        stats = sync_translations(ROOT, config, force=args.force)
        print(
            f"同步完成: 新增 {stats['added']} 键, "
            f"保留 {stats['kept']} 键, "
            f"新文件 {stats['new_files']} 个, "
            f"扫描 {stats['files']} 个文件"
        )
        return 0

    if args.command == "init":
        idea_path = args.idea_path
        extract_resources(ROOT, config, idea_path=idea_path, force=args.force)
        import_official_zh(ROOT, config, idea_path=idea_path, force=args.force)
        from lib.sync import sync_translations

        sync_translations(ROOT, config, force=False)
        report = build_gap_report(ROOT, config)
        print("\n" + report.summary())
        out = write_gap_report(ROOT, config, report)
        print(f"\n报告已写入: {out}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
