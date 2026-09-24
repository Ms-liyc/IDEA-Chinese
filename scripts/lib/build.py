from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Any


def _copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        if item.name.startswith("."):
            continue
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
            continue
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
        "{{UNTIL_BUILD}}": config.get("untilBuild", ""),
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    return text


def _copy_plugin_icon(root: Path, staging_meta: Path) -> None:
    icon_src = root / "plugin" / "META-INF" / "pluginIcon.png"
    if icon_src.exists():
        shutil.copy2(icon_src, staging_meta / "pluginIcon.png")


def _write_jar(staging: Path, output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in staging.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(staging).as_posix()
                zf.write(file, arcname)


def build_plugin(
    root: Path,
    config: dict[str, Any],
    *,
    version: str,
    standalone: bool = True,
) -> dict[str, Path]:
    zh_root = root / config["targetDir"]
    if not zh_root.exists():
        raise FileNotFoundError(f"翻译目录不存在: {zh_root}，请先运行 sync 并完成翻译")

    out_dir = root / config.get("pluginOutDir", "dist")
    staging = out_dir / ".staging"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True, exist_ok=True)

    _copy_tree(zh_root, staging)

    meta_inf = staging / "META-INF"
    meta_inf.mkdir(parents=True, exist_ok=True)
    _copy_plugin_icon(root, meta_inf)

    template_name = "plugin-standalone.xml.template" if standalone else "plugin.xml.template"
    plugin_template = root / "plugin" / template_name
    plugin_xml = _render_plugin_xml(plugin_template, config, version)
    (meta_inf / "plugin.xml").write_text(plugin_xml, encoding="utf-8")

    plugin_id = config["pluginId"]
    jar_name = f"{plugin_id}-{version}.jar"
    jar_output = out_dir / jar_name
    _write_jar(staging, jar_output)

    outputs: dict[str, Path] = {"jar": jar_output}

    if standalone:
        plugin_dir_name = config.get("standalonePluginDir", "idea-chinese")
        bundle_root = out_dir / ".bundle" / plugin_dir_name
        if bundle_root.exists():
            shutil.rmtree(bundle_root.parent)
        lib_dir = bundle_root / "lib"
        lib_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(jar_output, lib_dir / "idea-chinese.jar")

        zip_output = out_dir / f"{plugin_dir_name}-standalone-{version}.zip"
        if zip_output.exists():
            zip_output.unlink()
        shutil.make_archive(str(zip_output.with_suffix("")), "zip", bundle_root.parent, plugin_dir_name)
        outputs["zip"] = zip_output
        shutil.rmtree(bundle_root.parent)

    shutil.rmtree(staging)
    return outputs
