#!/usr/bin/env python3
"""Publish approved EP Brand assets into a static-site output directory.

Reusable module, independent of the portfolio's projects and its site builder.
"""
from __future__ import annotations
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
SHARED_FILES = (
    "styles/theme-tokens.css", "styles/typography-v2.css", "styles/portfolio-theme.css",
    "styles/report-navigation.css", "styles/report-theme.css", "components/web/header.css",
    "components/web/footer.css", "components/web/cards.css", "components/web/buttons.css",
    "scripts/theme-init.js", "scripts/theme.js", "scripts/i18n.js", "scripts/header.js",
    "scripts/report-navigation.js", "scripts/report-language.js", "scripts/footer.js",
    "scripts/plotly-i18n.js", "scripts/plotly-theme.js",
    "styles/plotly-theme.css", "styles/colormaps.css",
    "components/web/project-intro.css", "scripts/project-links.js",
    "components/web/links.css", "components/web/outputs.css", "scripts/outputs.js",
    "assets/icons/flag_us.svg", "assets/icons/flag_br.svg",
    "components/web/references.css", "scripts/references.js",
    "assets/icons/data_source_icon.svg",
    "assets/icons/knowledge_base_icon.svg",
    "assets/icons/reproducibility_icon.svg",
    "assets/icons/copy_icon.svg",
    "assets/icons/check_icon.svg",
)


def copy_shared_assets(output: Path) -> None:
    output = Path(output)
    dest = output / "assets"
    for relative in SHARED_FILES:
        source = ROOT / relative
        if not source.is_file():
            raise FileNotFoundError(f"Missing canonical EP shared asset: {source}")
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    animations = ROOT / "assets" / "animations"
    if animations.is_dir():
        shutil.copytree(animations, dest / "animations", dirs_exist_ok=True)
