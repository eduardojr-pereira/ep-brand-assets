"""Render canonical EP badges in standalone HTML documents."""

import base64
import json
import re
from functools import lru_cache
from html import escape
from pathlib import Path
from render_badges import render

ROOT = Path(__file__).resolve().parents[1]


def normalize(value):
    return re.sub(r"[^a-z0-9]", "", str(value).casefold())


@lru_cache(maxsize=1)
def entries():
    data = json.loads(
        (ROOT / "config/badges.json").read_text(encoding="utf-8")
    )
    return {entry["id"]: entry for entry in data["entries"]}


def image(ident, locale=None):
    entry = entries()[ident]
    label = escape((entry.get("prefix", "") + " " + entry["label"]).strip(), quote=True)
    lang = f' data-badge-locale="{locale}"' if locale else ""
    def tag(raw, theme=None):
        encoded = base64.b64encode(raw).decode("ascii")
        attr = f' data-badge-theme="{theme}"' if theme else ""
        return (f'<img class="ep-badge"{lang}{attr} '
                f'src="data:image/svg+xml;base64,{encoded}" '
                f'alt="{label}" width="{entry["width"]}" height="20">')
    if entry.get("theme_colors") or entry.get("theme_prefix"):
        return tag(render(entry, "dark").encode(), "dark") + tag(render(entry, "light").encode(), "light")
    return tag((ROOT / entry["path"]).read_bytes())


def localized(ident):
    return (
        image(ident + "_en", "en")
        + image(ident + "_pt_br", "pt-BR")
    )


def technology_id(label):
    key = normalize(label)
    aliases = {"html": "html5", "css3": "css"}
    if key in aliases:
        return aliases[key]
    for ident, entry in entries().items():
        if entry["category"] == "technologies" and key in (normalize(ident), normalize(entry["label"])):
            return ident
    raise ValueError(f"No canonical technology badge: {label}")


def technology(label):
    return image(technology_id(label))


def technologies(labels):
    ids = list(dict.fromkeys(technology_id(label) for label in labels))
    ids.sort(key=lambda ident: not bool(entries()[ident].get("icon")))
    return "".join(image(ident) for ident in ids)


def topic(label):
    key = normalize(label)
    if key in ("dataanalytics", "dataanalysisvisualization"):
        return localized("data_analytics")
    for ident, entry in entries().items():
        if entry["category"] == "topics" and key in (normalize(ident.removesuffix("_en").removesuffix("_pt_br")), normalize(entry["label"])):
            return localized(ident.removesuffix("_en").removesuffix("_pt_br"))
    raise ValueError(f"No canonical topic badge: {label}")
