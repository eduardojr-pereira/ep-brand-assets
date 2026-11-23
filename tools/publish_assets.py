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
    "scripts/theme-init.js", "scripts/theme.js", "scripts/i18n.js", "scripts/header.js",
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
