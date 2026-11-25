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
    "assets/logos/logo_initials.png",
    "assets/logos/favicon.png",
    "assets/logos/webclip.png",
    "components/web/references.css", "scripts/references.js",
    "assets/icons/data_source_icon.svg",
    "assets/icons/knowledge_base_icon.svg",
    "assets/icons/reproducibility_icon.svg",
    "assets/icons/copy_icon.svg",
    "assets/icons/check_icon.svg",
)


SHARED_ANIMATIONS = (
    "lottie_about_copper.json",
    "lottie_about_graphite.json",
    "lottie_about_white.json",
    "lottie_discord_copper.json",
    "lottie_discord_graphite.json",
    "lottie_discord_white.json",
    "lottie_github_copper.json",
    "lottie_github_graphite.json",
    "lottie_github_white.json",
    "lottie_gmail_copper.json",
    "lottie_gmail_graphite.json",
    "lottie_gmail_white.json",
    "lottie_home_copper.json",
    "lottie_home_graphite.json",
    "lottie_home_white.json",
    "lottie_knowledge_copper.json",
    "lottie_knowledge_graphite.json",
    "lottie_knowledge_white.json",
    "lottie_linkedin_copper.json",
    "lottie_linkedin_graphite.json",
    "lottie_linkedin_white.json",
    "lottie_projects_copper.json",
    "lottie_projects_graphite.json",
    "lottie_projects_white.json",
    "lottie_initials.json",
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
    for filename in SHARED_ANIMATIONS:
        source = ROOT / "assets" / "animations" / filename
        if not source.is_file():
            raise FileNotFoundError(f"Missing approved EP animation: {source}")
        target = dest / "animations" / filename
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
