from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Any


def _escape_properties(text: str) -> str:
    """将 UTF-8 中文转为 properties 常用的 \\uXXXX 形式（兼容旧版 JVM）。"""
    out: list[str] = []
    for ch in text:
        code = ord(ch)
        if ch in ("\n", "\r", "\t"):
            if ch == "\n":
                out.append("\\n")
            elif ch == "\r":
                out.append("\\r")
            else:
                out.append("\\t")
        elif code < 32 or code > 126:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out)


def _write_properties(path: Path, content: str, *, escape_unicode: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if escape_unicode:
        lines: list[str] = []
        for raw_line in content.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                lines.append(raw_line)
                continue
            if "=" in raw_line:
                key, value = raw_line.split("=", 1)
                lines.append(f"{key}={_escape_properties(value)}")
            else:
                lines.append(raw_line)
        path.write_text("\n".join(lines) + "\n", encoding="ascii", errors="strict")
    else:
        path.write_text(content, encoding="utf-8")


def _copy_tree(src: Path, dst: Path, *, escape_properties: bool = True) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if item.suffix == ".properties":
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)


def _render_plugin_xml(template: Path, config: dict[str, Any], version: str) -> str:
    text = template.read_text(encoding="utf-8")
    replacements = {
        "{{PLUGIN_ID}}": config["pluginId"],
        "{{PLUGIN_NAME}}": config["pluginName"],
        "{{VENDOR}}": config["vendor"],
        "{{VENDOR_URL}}": config.get("vendorUrl", ""),
        "{{VENDOR_EMAIL}}": config.get("vendorEmail", ""),
        "{{VERSION}}": version,
        "{{LOCALE}}": config["locale"],
        "{{MIN_BUILD}}": config["minBuild"],
        "{{UNTIL_BUILD}}": config["untilBuild"],
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def _copy_plugin_assets(root: Path, staging: Path) -> None:
    meta_src = root / "plugin" / "META-INF"
    if meta_src.exists():
        meta_dst = staging / "META-INF"
        meta_dst.mkdir(parents=True, exist_ok=True)
        for item in meta_src.iterdir():
            if item.is_file():
                shutil.copy2(item, meta_dst / item.name)

    assets_src = root / "plugin" / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, staging / "assets", dirs_exist_ok=True)


def build_plugin(root: Path, config: dict[str, Any], *, version: str) -> Path:
    zh_root = root / config["targetDir"]
    if not zh_root.exists():
        raise FileNotFoundError(f"翻译目录不存在: {zh_root}，请先运行 sync 并完成翻译")

    out_dir = root / config.get("pluginOutDir", "dist")
    staging = out_dir / ".staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    _copy_tree(zh_root, staging)
    _copy_plugin_assets(root, staging)

    meta_inf = staging / "META-INF"
    meta_inf.mkdir(parents=True, exist_ok=True)
    plugin_template = root / "plugin" / "plugin.xml.template"
    plugin_xml = _render_plugin_xml(plugin_template, config, version)
    (meta_inf / "plugin.xml").write_text(plugin_xml, encoding="utf-8")

    jar_name = f"{config['pluginId']}-{version}.jar"
    output = out_dir / jar_name
    output.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in staging.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(staging).as_posix()
                zf.write(file, arcname)

    shutil.rmtree(staging)
    return output
