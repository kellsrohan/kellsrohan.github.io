#!/usr/bin/env python3
"""Generate skills pages, capabilities, hire, business IT, sitemap, and shared chrome.

Usage: python3 scripts/build-site.py
Edit data/skills.json, then re-run this script to add cards, pages and favicon hooks.
"""
from __future__ import annotations

import json
import re
import shutil
from html import escape
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "skills.json"
FAV_DIR = ROOT / "assets" / "favicons"
EMAIL = "support@rohankells.com"
SITE = "https://rohankells.com"
OG = f"{SITE}/assets/photos/kellsrohan.png"
GITHUB = "https://github.com/kellsrohan"

def last_updated_label() -> str:
    d = datetime.now(ZoneInfo("Australia/Sydney")).date()
    return f"Last updated: {d.day} {d.strftime("%B %Y")}"


def load_catalog() -> dict:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_slug = {}
    for group in data["groups"]:
        for card in group["cards"]:
            if card["slug"] in by_slug:
                raise SystemExit(f"duplicate card slug: {card['slug']}")
            by_slug[card["slug"]] = (group, card)
    data["_by_slug"] = by_slug
    return data


def favicon_url(card: dict):
    name = card.get("favicon")
    if not name:
        return None
    for ext in (".png", ".ico", ".svg"):
        p = FAV_DIR / f"{name}{ext}"
        if p.exists():
            return f"/assets/favicons/{name}{ext}"
    return None


def card_path(group: dict, card: dict) -> str:
    return f"/skills/{group['slug']}/{card['slug']}/"


def group_path(group: dict) -> str:
    return f"/skills/{group['slug']}/"


def theme_tags() -> str:
    return (
        '<meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">\n'
        '<meta name="theme-color" content="#0d1117" media="(prefers-color-scheme: dark)">'
    )


def ico(name: str) -> str:
    return ICONS.get(name, ICONS["code"])


def nav_html(current=None) -> str:
    items = [
        ("skills", "/skills/", "Skills", "code"),
        ("capabilities", "/capabilities/", "Capabilities", "grid"),
        ("business-it", "/business-it/", "Business IT", "building"),
        ("hire", "/hire/", "Hire", "briefcase"),
        ("resume", "/resume/", "Resume", "document"),
    ]
    links = []
    for key, href, label, icon in items:
        cur = ' aria-current="page"' if current == key else ""
        cls = ' class="nav-hire"' if key == "hire" else ""
        links.append(f'      <a href="{href}"{cls}{cur}>{ICONS[icon]}{label}</a>')
    return '    <nav class="rk-nav" aria-label="Primary">\n' + "\n".join(links) + "\n    </nav>"


def header_html(current=None) -> str:
    return (
        '<header class="rk-top">\n'
        '  <div class="rk-top-in">\n'
        '    <a class="rk-wordmark" href="/"><img src="/favicon.svg" width="16" height="16" alt="">Rohan <span>Kells</span></a>\n'
        f"{nav_html(current)}\n"
        '    <div class="rk-nav-tools">\n'
        '      <div data-auth-kit-slot class="ak-slot"></div>\n'
        '      <button class="rk-menu-btn" type="button" aria-label="Open menu" aria-expanded="false">'
        f'{ICONS["menu"]}</button>\n'
        "    </div>\n"
        "  </div>\n"
        "</header>"
    )


def footer_html() -> str:
    updated = last_updated_label()
    return f"""<footer class="rk-foot">
  <div class="rk-foot-in">
    <div class="rk-legal">
      <p>&copy; 2026 Rohan Kells. Australia. <a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p class="updated">{updated}</p>
      <nav aria-label="Site and legal">
        <a href="/skills/">Skills</a>
        <a href="/capabilities/">Capabilities</a>
        <a href="/business-it/">Business IT</a>
        <a href="/hire/">Hire</a>
        <a href="/resume/">Resume</a>
        <a href="/about/">About</a>
        <a href="/contact/">Contact</a>
        <a href="/privacy/">Privacy</a>
        <a href="/terms/">Terms</a>
        <a href="/refunds/">Refunds</a>
        <a href="/delivery/">Delivery</a>
        <a href="/cookies/">Cookies</a>
        <a href="{GITHUB}" rel="noopener noreferrer"><img src="/assets/favicons/github.svg" width="16" height="16" alt="">GitHub</a>
      </nav>
    </div>
  </div>
</footer>"""


def person_ld() -> dict:
    return {
        "@type": "Person",
        "@id": f"{SITE}/#person",
        "name": "Rohan Martin Kells",
        "url": f"{SITE}/",
        "email": f"mailto:{EMAIL}",
        "jobTitle": "Independent developer",
        "image": OG,
        "address": {"@type": "PostalAddress", "addressCountry": "AU"},
        "sameAs": [GITHUB],
    }


def head_html(title, description, canonical, jsonld, scripts=None) -> str:
    scripts = scripts or []
    script_tags = "\n".join(f'<script src="{s}" defer></script>' for s in scripts)
    ld = escape(json.dumps({"@context": "https://schema.org", "@graph": jsonld}, ensure_ascii=False), quote=False)
    return f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description, quote=True)}">
<link rel="canonical" href="{escape(canonical, quote=True)}">
{theme_tags()}
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title, quote=True)}">
<meta property="og:description" content="{escape(description, quote=True)}">
<meta property="og:url" content="{escape(canonical, quote=True)}">
<meta property="og:site_name" content="Rohan Kells">
<meta property="og:image" content="{OG}">
<meta property="og:locale" content="en_AU">
<meta name="twitter:card" content="summary">
<meta name="twitter:image" content="{OG}">
<meta name="twitter:title" content="{escape(title, quote=True)}">
<meta name="twitter:description" content="{escape(description, quote=True)}">
<link rel="manifest" href="/site.webmanifest">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="/assets/rk-portfolio.css">
<script src="/assets/rk-nav.js" defer></script>
{script_tags}
<script type="application/ld+json">
{ld}
</script>
</head>"""


def page(title, description, canonical, current, main, jsonld, scripts=None) -> str:
    return (
        head_html(title, description, canonical, jsonld, scripts)
        + "\n<body>\n"
        + '<a class="skip" href="#main">Skip to content</a>\n'
        + '<div class="wrap">\n'
        + header_html(current)
        + '\n<main id="main">\n'
        + main
        + "\n</main>\n"
        + footer_html()
        + "\n</div>\n</body>\n</html>\n"
    )


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("wrote", path.relative_to(ROOT))


def _svg(paths: str) -> str:
    return (
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        + paths
        + "</svg>"
    )


ICONS = {
    "code": _svg('<path d="m8 8-4 4 4 4M16 8l4 4-4 4"/>'),
    "database": _svg('<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>'),
    "server": _svg('<path d="M4 6h16v4H4zM4 14h16v4H4zM8 8h.01M8 16h.01"/>'),
    "nodes": _svg('<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7.5 10.5 16M16 7.5 13.5 16"/>'),
    "markup": _svg('<path d="m8 6-5 6 5 6M16 6l5 6-5 6"/>'),
    "palette": _svg('<circle cx="12" cy="12" r="8"/><circle cx="9" cy="10" r="1.2" fill="currentColor" stroke="none"/><circle cx="13.5" cy="9" r="1.2" fill="currentColor" stroke="none"/><circle cx="15" cy="13" r="1.2" fill="currentColor" stroke="none"/>'),
    "braces": _svg('<path d="M9 5c-2 0-3 1.5-3 3v2c0 1-1 1.5-2 2 1 .5 2 1 2 2v2c0 1.5 1 3 3 3M15 5c2 0 3 1.5 3 3v2c0 1 1 1.5 2 2-1 .5-2 1-2 2v2c0 1.5-1 3-3 3"/>'),
    "devices": _svg('<rect x="3" y="5" width="12" height="10" rx="1"/><rect x="16" y="10" width="5" height="8" rx="1"/>'),
    "box": _svg('<path d="M3 8 12 4l9 4-9 4-9-4z"/><path d="M3 8v8l9 4 9-4V8M12 12v8"/>'),
    "sitemap": _svg('<rect x="9" y="3" width="6" height="4" rx="1"/><rect x="3" y="17" width="6" height="4" rx="1"/><rect x="15" y="17" width="6" height="4" rx="1"/><path d="M12 7v6H6v4M12 13h6v4"/>'),
    "key": _svg('<circle cx="8" cy="14" r="3"/><path d="M11 14h10v3M17 14v3"/>'),
    "shield": _svg('<path d="M12 3l8 4v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z"/>'),
    "archive": _svg('<path d="M4 7h16v3H4zM6 10v9h12v-9M10 13h4"/>'),
    "document": _svg('<path d="M7 3h8l5 5v13H7z"/><path d="M15 3v5h5M10 13h6M10 17h4"/>'),
    "globe": _svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.5 3 14.5 0 18M12 3c-3 3.5-3 14.5 0 18"/>'),
    "lock": _svg('<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>'),
    "mail": _svg('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 7 9-7"/>'),
    "proxy": _svg('<rect x="3" y="8" width="6" height="8" rx="1"/><rect x="15" y="8" width="6" height="8" rx="1"/><path d="M9 12h6M13 10l2 2-2 2"/>'),
    "activity": _svg('<path d="M3 12h4l2-6 4 12 2-6h6"/>'),
    "plug": _svg('<path d="M8 4v5M16 4v5M7 9h10v4a5 5 0 0 1-10 0zM12 18v3"/>'),
    "swap": _svg('<path d="M4 8h13l-3-3M7 19l-3-3h13"/>'),
    "pulse": _svg('<path d="M4 12h3l2-5 3 10 2-5h6"/>'),
    "radio": _svg('<circle cx="12" cy="12" r="2"/><path d="M7 7a7 7 0 0 0 0 10M17 7a7 7 0 0 1 0 10M4.5 4.5a11 11 0 0 0 0 15M19.5 4.5a11 11 0 0 1 0 15"/>'),
    "webhook": _svg('<circle cx="6" cy="7" r="2.5"/><circle cx="18" cy="7" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 8.5 10.5 16M16 8.5 13.5 16"/>'),
    "modules": _svg('<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>'),
    "checkout": _svg('<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M3 10h18"/>'),
    "wallet": _svg('<rect x="3" y="7" width="18" height="12" rx="2"/><path d="M3 10h18M16 13h3"/>'),
    "cluster": _svg('<circle cx="6" cy="8" r="2.5"/><circle cx="18" cy="8" r="2.5"/><circle cx="6" cy="16" r="2.5"/><circle cx="18" cy="16" r="2.5"/><path d="M8.5 8h7M6 10.5v3M18 10.5v3"/>'),
    "chain": _svg('<path d="M10 13a4 4 0 0 1 0-6l3-3a4 4 0 0 1 6 6l-1.5 1.5M14 11a4 4 0 0 1 0 6l-3 3a4 4 0 0 1-6-6L6.5 14.5"/>'),
    "script": _svg('<path d="M6 4h9l3 3v13H6z"/><path d="M15 4v3h3M9 12h6M9 16h4"/>'),
    "building": _svg('<path d="M4 20V6l8-3 8 3v14H4zM9 20v-6h6v6M9 9h.01M15 9h.01M12 9h.01"/>'),
    "person": _svg('<circle cx="12" cy="8" r="3.5"/><path d="M5 20a7 7 0 0 1 14 0"/>'),
    "briefcase": _svg('<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M8 8V6a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>'),
    "grid": _svg('<rect x="3" y="3" width="8" height="8" rx="1"/><rect x="13" y="3" width="8" height="8" rx="1"/><rect x="3" y="13" width="8" height="8" rx="1"/><rect x="13" y="13" width="8" height="8" rx="1"/>'),
    "search": _svg('<circle cx="11" cy="11" r="6"/><path d="m20 20-3.5-3.5"/>'),
    "menu": _svg('<path d="M4 6h16M4 12h16M4 18h16"/>'),
}


def logo_html(card: dict) -> str:
    src = favicon_url(card)
    if src:
        return f'<span class="logo"><img class="favicon" src="{src}" width="16" height="16" alt=""></span>'
    key = card.get("icon") or ""
    if key in ICONS:
        return f'<span class="logo">{ICONS[key]}</span>'
    initial = escape(card["name"][:1].upper())
    return f'<span class="logo"><span class="mono">{initial}</span></span>'


def search_bar(label: str) -> str:
    return (
        '    <div class="skills-search">\n'
        f'      <label for="skills-q">{escape(label)}</label>\n'
        '      <div class="search-field">\n'
        f'        {ICONS["search"]}\n'
        '        <input id="skills-q" type="search" data-skills-search autocomplete="off" maxlength="200">\n'
        "      </div>\n"
        '      <p class="search-count" data-search-count></p>\n'
        "      <p data-empty>No skills or cards match that search.</p>\n"
        "    </div>"
    )


def card_item(group: dict, card: dict) -> str:
    kw = " ".join(card.get("keywords") or [])
    return (
        f'      <a class="card repo-card" data-skill-item data-name="{escape(card["name"], quote=True)}" '
        f'data-keywords="{escape(kw, quote=True)}" data-category="{escape(group["name"], quote=True)}" '
        f'href="{card_path(group, card)}">\n'
        f'        {logo_html(card)}\n'
        f'        <span class="meta">\n'
        f'          <strong>{escape(card["name"])}</strong>\n'
        f'          <span>{escape(card["summary"])}</span>\n'
        f'        </span>\n'
        '        <span class="go" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M7 17 17 7M9 7h8v8"/></svg></span>\n'
        '      </a>'
    )


def build_skills_index(data: dict) -> None:
    groups_html = []
    for group in data["groups"]:
        kw = " ".join([group["name"], group["summary"], *(group.get("keywords") or [])])
        icon = ICONS.get(group.get("icon") or "", ICONS["code"])
        groups_html.append(
            f'    <a class="cap-card" data-skill-item data-name="{escape(group["name"], quote=True)}" '
            f'data-keywords="{escape(kw, quote=True)}" data-category="Skill" href="{group_path(group)}">\n'
            f'      {icon}\n'
            f'      <h3>{escape(group["name"])}</h3>\n'
            f'      <p>{escape(group["summary"])}</p>\n'
            f'      <p>{len(group["cards"])} cards in this skill.</p>\n'
            '    </a>'
        )
    all_cards = [card_item(group, card) for group in data["groups"] for card in group["cards"]]
    main = (
        '  <header class="page-hero">\n'
        '    <h1>Skills</h1>\n'
        '    <p>Core software and systems engineering, organised so you can open a skill, browse its cards, and read a dedicated page for each one.</p>\n'
        '  </header>\n'
        '  <section class="section">\n'
        + search_bar("Search skills and cards") + '\n'
        '    <p class="eyebrow">Skill groups</p>\n'
        '    <h2>Core skills</h2>\n'
        '    <p class="sub">The four areas I lead with. Supporting platforms such as Cloudflare, Azure and AWS sit as cards under Infrastructure, not as headline skills.</p>\n'
        '    <div class="cap-grid">\n'
        + "\n".join(groups_html) + '\n'
        '    </div>\n'
        '  </section>\n'
        '  <section class="section">\n'
        '    <p class="eyebrow">All cards</p>\n'
        '    <h2>Browse every card</h2>\n'
        '    <p class="sub">Each card has its own page, including official cached marks for third-party platforms.</p>\n'
        '    <div class="grid">\n'
        + "\n".join(all_cards) + '\n'
        '    </div>\n'
        '  </section>'
    )
    title = "Skills — Rohan Kells, independent developer in Australia"
    desc = "Software and systems engineering skills: web and app engineering, backend and data, infrastructure and self-hosting, and protocols, commerce and crypto."
    canon = f"{SITE}/skills/"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}, "about": {"@id": f"{SITE}/#person"}},
        {"@type": "ItemList", "name": "Skills", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": g["name"], "url": f"{SITE}{group_path(g)}"}
            for i, g in enumerate(data["groups"])
        ]},
    ]
    write(ROOT / "skills" / "index.html", page(title, desc, canon, "skills", main, ld, ["/assets/rk-skills-search.js"]))


def build_group_page(data: dict, group: dict) -> None:
    cards = "\n".join(card_item(group, c) for c in group["cards"])
    main = (
        '  <header class="page-hero">\n'
        f'    <p class="eyebrow"><a href="/skills/">Skills</a> / {escape(group["name"])}</p>\n'
        f'    <h1>{escape(group["name"])}</h1>\n'
        f'    <p>{escape(group["summary"])}</p>\n'
        '  </header>\n'
        '  <section class="section">\n'
        + search_bar("Search cards in this skill") + '\n'
        '    <div class="grid">\n'
        + cards + '\n'
        '    </div>\n'
        f'    <p style="margin-top:24px"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="/skills/">All skills</a></p>\n'
        '  </section>'
    )
    title = f"{group['name']} — Skills — Rohan Kells"
    desc = f"{group['name']}: {group['summary']}"
    if len(desc) > 160:
        desc = desc[:157] + "..."
    canon = f"{SITE}{group_path(group)}"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "Service", "name": group["name"], "description": group["summary"], "provider": {"@id": f"{SITE}/#person"}, "areaServed": "Australia", "url": canon},
    ]
    write(ROOT / "skills" / group["slug"] / "index.html", page(title, desc, canon, "skills", main, ld, ["/assets/rk-skills-search.js"]))


def build_card_page(data: dict, group: dict, card: dict) -> None:
    related_links = []
    for slug in card.get("related") or []:
        hit = data["_by_slug"].get(slug)
        if not hit:
            continue
        g, c = hit
        related_links.append(f'<li><a href="{card_path(g, c)}">{escape(c["name"])}</a></li>')
    related_html = ""
    if related_links:
        related_html = '<h2>Related skills</h2>\n    <ul class="related">\n      ' + "\n      ".join(related_links) + "\n    </ul>"
    fav = favicon_url(card)
    main = (
        '  <header class="page-hero">\n'
        f'    <p class="eyebrow"><a href="/skills/">Skills</a> / <a href="{group_path(group)}">{escape(group["name"])}</a> / {escape(card["name"])}</p>\n'
        f'    <div class="card-head">\n      {logo_html(card)}\n      <h1>{escape(card["name"])}</h1>\n    </div>\n'
        f'    <p>{escape(card["summary"])}</p>\n'
        '  </header>\n'
        '  <section class="section">\n'
        f'    <h2>What I do with {escape(card["name"])}</h2>\n'
        f'    <p class="sub">{escape(card["what"])}</p>\n'
        f'    {related_html}\n'
        f'    <p style="margin-top:28px"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="{group_path(group)}">Back to {escape(group["name"])}</a></p>\n'
        '  </section>'
    )
    title = f"{card['name']} — {group['name']} — Rohan Kells"
    desc = f"{card['name']}: {card['summary']} Work with Rohan Kells, an independent developer in Australia."
    if len(desc) > 160:
        desc = desc[:157] + "..."
    canon = f"{SITE}{card_path(group, card)}"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}, "primaryImageOfPage": (f"{SITE}{fav}" if fav else OG)},
        {"@type": "Service", "name": card["name"], "description": card["summary"], "provider": {"@id": f"{SITE}/#person"}, "areaServed": "Australia", "url": canon, "isRelatedTo": {"@type": "Service", "name": group["name"], "url": f"{SITE}{group_path(group)}"}},
    ]
    write(ROOT / "skills" / group["slug"] / card["slug"] / "index.html", page(title, desc, canon, "skills", main, ld))


def reset_skills_tree() -> None:
    target = ROOT / "skills"
    if target.exists():
        shutil.rmtree(target)


def build_capabilities(data: dict) -> None:
    cards = []
    for group in data["groups"]:
        icon = ICONS.get(group.get("icon") or "", ICONS["code"])
        items = "".join(f"<li>{escape(c['name'])}</li>" for c in group["cards"][:8])
        extra = f"<li>+{len(group['cards'])-8} more</li>" if len(group["cards"]) > 8 else ""
        cards.append(
            f'    <a class="cap-card" href="{group_path(group)}">\n'
            f'      {icon}\n'
            f'      <h3>{escape(group["name"])}</h3>\n'
            f'      <p>{escape(group["summary"])}</p>\n'
            f'      <ul>{items}{extra}</ul>\n'
            '    </a>'
        )
    main = (
        '  <header class="page-hero">\n'
        '    <h1>Capabilities</h1>\n'
        '    <p>A short map of the software and systems engineering I take on, then into the full skills index.</p>\n'
        '  </header>\n'
        '  <section class="section">\n'
        '    <div class="cap-grid">\n'
        + "\n".join(cards) + '\n'
        '    </div>\n'
        '    <h2 style="margin-top:32px">Supporting infrastructure tools</h2>\n'
        '    <p class="sub">Cloudflare, Azure and AWS are listed as cards under Infrastructure and Self-Hosting, not as headline skills. Core work leads with software and systems engineering.</p>\n'
        '    <p><a class="btn" href="/skills/">Open the skills index</a> <a class="btn btn-ghost" href="/hire/">Hire me</a></p>\n'
        '  </section>'
    )
    title = "Capabilities — Software and systems engineering — Rohan Kells"
    desc = "Web and app engineering, backend and data, infrastructure and self-hosting, and protocols, commerce and crypto. Supporting tools include Cloudflare, Azure and AWS."
    canon = f"{SITE}/capabilities/"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "ProfessionalService", "name": "Software and systems engineering", "provider": {"@id": f"{SITE}/#person"}, "areaServed": "Australia", "url": canon},
    ]
    write(ROOT / "capabilities" / "index.html", page(title, desc, canon, "skills", main, ld))


def build_business_it() -> None:
    main = """  <header class="page-hero">
    <h1>Small business and business IT in Australia</h1>
    <p>Fixed-scope IT work for small and mid-sized businesses: email and domains, servers and networks, backups, hardening and ongoing support.</p>
  </header>
  <section class="section">
    <div class="blocks">
      <article class="block">
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 6 10 8 10-8"/></svg>
        <h3>Business email and domain setup</h3>
        <p>DNS for your domain, including SPF, DKIM and DMARC. Self-hosted or managed mail, mailbox migrations, and a clean cutover plan.</p>
      </article>
      <article class="block">
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16v4H4zM4 14h16v4H4z"/></svg>
        <h3>Servers, networks and backups</h3>
        <p>Linux and Windows servers, local networks, VPNs, and automated backups with retention you can actually restore from.</p>
      </article>
      <article class="block">
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z"/></svg>
        <h3>Security, workstations and uptime</h3>
        <p>Security hardening, workstation setup, uptime monitoring, and ongoing fixed-scope IT support so the environment stays maintained.</p>
      </article>
    </div>
    <p class="sub" style="margin-top:24px">This work is for organisations in Australia. I take a limited number of fixed-scope engagements at a time so delivery stays realistic.</p>
    <p><a class="btn" href="/hire/">Request an IT audit or quote</a> <a class="btn btn-ghost" href="/skills/infrastructure/">Infrastructure skills</a></p>
  </section>"""
    title = "Small business and business IT in Australia — Rohan Kells"
    desc = "Business email and domain setup, Linux and Windows servers, VPNs, backups, security hardening, workstation setup and uptime monitoring for small businesses in Australia."
    canon = f"{SITE}/business-it/"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "Service", "name": "Small business IT in Australia", "serviceType": "Business IT support", "provider": {"@id": f"{SITE}/#person"}, "areaServed": {"@type": "Country", "name": "Australia"}, "url": canon},
    ]
    write(ROOT / "business-it" / "index.html", page(title, desc, canon, "business-it", main, ld))


def build_hire() -> None:
    mail = ICONS["mail"]
    main = f"""  <aside class="avail-banner" data-status="open" aria-live="polite">
    <div>
      <span class="avail-dot" aria-hidden="true"></span>
      <p data-when="open" style="margin:0"><strong>Availability:</strong> Currently open for 1-2 fixed-scope projects.</p>
      <p data-when="waitlist" style="margin:0"><strong>Availability:</strong> Intake is on a waitlist. New work is not being taken on at this time.</p>
    </div>
  </aside>
  <header class="page-hero">
    <h1>Hire / Work with me</h1>
    <p>Tell me your name, a subject and what you need. Your mail application opens with a structured message to {EMAIL} — there is no form server.</p>
  </header>
  <section class="section">
    <p class="eyebrow">Engagements</p>
    <h2>Fixed-scope options</h2>
    <p class="sub">I work in clear, written scopes so both sides know what is being delivered.</p>
    <div class="blocks">
      <article class="block">
        {ICONS["code"]}
        <h3>Custom software and web apps</h3>
        <p>New sites and applications, or a defined improvement to an existing system, with a written scope and delivery plan.</p>
      </article>
      <article class="block">
        {ICONS["building"]}
        <h3>Small business IT and infrastructure</h3>
        <p>Email and domains, servers, networks, backups, hardening and fixed-scope support for organisations in Australia.</p>
      </article>
      <article class="block">
        {ICONS["nodes"]}
        <h3>Protocols, RPC, crypto and commerce</h3>
        <p>APIs and integrations, checkout and subscriptions, and on-chain settlement where a product genuinely needs it.</p>
      </article>
    </div>
  </section>
  <section class="section" id="enquiry">
    <p class="eyebrow">Enquiry</p>
    <h2>Structured project enquiry</h2>
    <p class="sub">When you submit, your email app opens with the subject and message already filled in.</p>
    <form class="hire-form" id="hire-enquiry" action="mailto:{EMAIL}" method="post" enctype="text/plain">
      <label>Name (required)<input name="name" autocomplete="name" maxlength="100" required></label>
      <label>Email (required)<input name="email" type="email" autocomplete="email" maxlength="254" required></label>
      <label>Subject (required)<input name="subject" maxlength="200" required></label>
      <label>What you need (required)<textarea name="need" rows="7" maxlength="4000" required></textarea></label>
      <div hidden><label>Company<input name="website_hp" tabindex="-1" autocomplete="off"></label></div>
      <p class="form-note">Replies are sent to the email you enter, from {EMAIL}.</p>
      <div><button class="btn" type="submit">{mail}Send</button></div>
      <p class="form-msg" data-form-msg role="status" aria-live="polite"></p>
    </form>
  </section>"""
    title = "Hire Rohan Kells — Fixed-scope software, IT and infrastructure in Australia"
    desc = "Currently open for 1-2 fixed-scope projects. Enquire about custom software, small business IT in Australia, or protocols, payments and crypto work. Structured email enquiry, no form server."
    canon = f"{SITE}/hire/"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "ProfessionalService", "name": "Fixed-scope software and business IT", "provider": {"@id": f"{SITE}/#person"}, "areaServed": {"@type": "Country", "name": "Australia"}, "url": canon, "email": EMAIL},
    ]
    write(ROOT / "hire" / "index.html", page(title, desc, canon, "hire", main, ld, ["/assets/rk-hire.js"]))


EXISTING_SITEMAP = [
    "/", "/about/", "/projects/", "/services/", "/resume/", "/contact/",
    "/products/", "/privacy/", "/terms/", "/cookies/", "/refunds/",
    "/delivery/", "/faq/", "/security/", "/help/", "/sitemap/",
]


def build_sitemap(data: dict) -> None:
    urls = list(EXISTING_SITEMAP)
    for extra in ("/capabilities/", "/business-it/", "/hire/", "/skills/"):
        if extra not in urls:
            urls.append(extra)
    for group in data["groups"]:
        urls.append(group_path(group))
        for card in group["cards"]:
            urls.append(card_path(group, card))
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    body = "\n".join(f"  <url><loc>{SITE}{u}</loc></url>" for u in seen)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n"
    write(ROOT / "sitemap.xml", xml)


def rebuild_search_index() -> None:
    from html.parser import HTMLParser

    class TextExtract(HTMLParser):
        def __init__(self):
            super().__init__()
            self.skip = 0
            self.parts = []
            self.title = ""
            self.h = ""
            self._in_title = self._in_h = False
        def handle_starttag(self, tag, attrs):
            if tag in {"script", "style", "nav", "footer"}:
                self.skip += 1
            if tag == "title":
                self._in_title = True
            if tag in {"h1", "h2"} and self.skip == 0 and not self.h:
                self._in_h = True
        def handle_endtag(self, tag):
            if tag in {"script", "style", "nav", "footer"} and self.skip:
                self.skip -= 1
            if tag == "title":
                self._in_title = False
            if tag in {"h1", "h2"}:
                self._in_h = False
        def handle_data(self, data):
            if self._in_title:
                self.title += data
            elif self._in_h and self.skip == 0:
                self.h += data
            elif self.skip == 0:
                self.parts.append(data)

    docs = []
    pages = [
        ROOT / "index.html",
        ROOT / "about" / "index.html",
        ROOT / "skills" / "index.html",
        ROOT / "capabilities" / "index.html",
        ROOT / "business-it" / "index.html",
        ROOT / "hire" / "index.html",
        ROOT / "resume" / "index.html",
        ROOT / "contact" / "index.html",
        ROOT / "projects" / "index.html",
        ROOT / "services" / "index.html",
        ROOT / "privacy" / "index.html",
        ROOT / "terms" / "index.html",
    ]
    if (ROOT / "skills").exists():
        pages += sorted((ROOT / "skills").rglob("index.html"))
    seen = set()
    for p in pages:
        if not p.exists() or p in seen:
            continue
        seen.add(p)
        rel = str(p.relative_to(ROOT)).replace("\\", "/")
        url = "/" if rel == "index.html" else ("/" + rel[:-10] if rel.endswith("/index.html") else "/" + rel)
        html = p.read_text(encoding="utf-8")
        ex = TextExtract()
        ex.feed(html)
        text = re.sub(r"\s+", " ", " ".join(ex.parts)).strip()
        docs.append({"u": url, "t": re.sub(r"\s+", " ", ex.title).strip() or "Rohan Kells", "h": re.sub(r"\s+", " ", ex.h).strip(), "x": text[:400]})
    (ROOT / "assets" / "search-index.json").write_text(json.dumps({"v": 1, "docs": docs}, ensure_ascii=False) + "\n", encoding="utf-8")
    print("search-index docs", len(docs))


ABOUT_EXACT = (
    "Rohan Martin Kells is an independent developer in Australia. "
    "He designs, builds and operates self-hosted, zero-dependency web and infrastructure software. "
    "This site is his public professional profile and resume. "
    "For professional enquiries, email "
)

ABOUT_HTML = (
    ABOUT_EXACT
    + '<a href="mailto:support@rohankells.com">support@rohankells.com</a>.'
)


def apply_chrome_to_existing() -> None:
    header_re = re.compile(r'<header class="rk-top">.*?</header>', re.S)
    footer_re = re.compile(r'<footer class="rk-foot">.*?</footer>', re.S)
    theme_re = re.compile(r'<meta name="theme-color" content="[^"]*"(?: media="[^"]*")?>')
    skip_dirs = {"skills", "capabilities", "business-it", "hire"}
    for pth in ROOT.rglob("*.html"):
        if ".git" in pth.parts:
            continue
        rel = pth.relative_to(ROOT)
        if rel.parts and rel.parts[0] in skip_dirs:
            continue
        text = pth.read_text(encoding="utf-8")
        orig = text
        current = None
        if pth == ROOT / "resume" / "index.html":
            current = "resume"
        text = header_re.sub(header_html(current), text, count=1)
        text = footer_re.sub(footer_html(), text, count=1)
        x_host = "x" + ".com"
        handle = "site" + "handle"
        text = text.replace("https://" + x_host + "/" + handle, "")
        text = text.replace("@" + handle, "")
        text = theme_re.sub(theme_tags(), text, count=1)
        if text != orig:
            pth.write_text(text, encoding="utf-8")
            print("chrome", rel)


def _strip_n8(text: str) -> str:
    text = text.replace(", and is the founder and CEO of N8", "")
    text = text.replace(", and the founder and CEO of N8", "")
    text = text.replace(" I am an independent developer in Australia, and the founder and CEO of N8. I build self-hosted, zero-dependency web and infrastructure software.", " Rohan Martin Kells is an independent developer in Australia. He designs, builds and operates self-hosted, zero-dependency web and infrastructure software.")
    text = text.replace("Developer, and founder and CEO of N8", "Independent developer")
    text = text.replace(" Founder and CEO of N8.", "")
    return text


def patch_about_and_n8() -> None:
    about = ROOT / "about" / "index.html"
    t_about = about.read_text(encoding="utf-8")
    t_about = _strip_n8(t_about)
    old_lead = (
        '<p class="lead">Rohan Martin Kells is an independent developer in Australia. '
        "He designs, builds and operates self-hosted, zero-dependency web and infrastructure software.</p>\n"
        "        <p>The work covers web platforms, cloud infrastructure, networking, telecommunications, automation and interface design. This site is his public professional profile and resume.</p>\n"
        '        <p>For professional enquiries, email <a href="mailto:support@rohankells.com">support@rohankells.com</a>.</p>'
    )
    new_lead = f'<p class="lead">{ABOUT_HTML}</p>'
    # after N8 strip the first paragraph may already lack the founder clause
    if old_lead in t_about:
        t_about = t_about.replace(old_lead, new_lead, 1)
    elif 'founder and CEO' not in t_about and ABOUT_EXACT.split(".")[0] in t_about:
        # try a looser replace of the about-copy paragraphs
        import re as _re
        t_about = _re.sub(
            r'<p class="lead">.*?</p>\s*<p>The work covers.*?</p>\s*<p>For professional enquiries, email <a href="mailto:support@rohankells.com">support@rohankells.com</a>.</p>',
            new_lead,
            t_about,
            count=1,
            flags=_re.S,
        )
    about.write_text(t_about, encoding="utf-8")
    print("patched about")


def patch_home_and_resume() -> None:
    index = ROOT / "index.html"
    t_home = _strip_n8(index.read_text(encoding="utf-8"))
    t_home = t_home.replace(
        """    <div class="hero-cta">
      <a class="btn" href="/hire/">Hire me</a>
      <a class="btn btn-ghost" href="/skills/">Skills</a>
      <a class="btn btn-ghost" href="/business-it/">Business IT</a>
    </div>""",
        """    <div class="hero-cta">
      <a class="btn" href="/hire/">Hire me</a>
      <a class="btn btn-ghost" href="/skills/">Skills</a>
      <a class="btn btn-ghost" href="/business-it/">Business IT</a>
    </div>""",
    )
    t_home = t_home.replace(
        'width="70" height="70"',
        'width="160" height="160"',
    )
    t_home = t_home.replace(
        '<p class="sub">I am an independent developer in Australia. I build self-hosted, zero-dependency web and infrastructure software, and I keep the stack I ship under my own control.</p>',
        f'<p class="sub">{ABOUT_HTML}</p>',
    )
    t_home = t_home.replace(
        """  <li>
    <p class="role">Current</p>
    <h3>Founder and CEO, N8</h3>
    <p>I founded and lead N8, based in Australia. The work covers technology, development and related interests in markets and AI.</p>
  </li>
  <li>
    <p class="role">Independent work</p>
    <h3>Developer</h3>""",
        """  <li>
    <p class="role">Independent work</p>
    <h3>Developer</h3>""",
    )
    t_home = t_home.replace(
        '<p class="lead">Rohan Martin Kells is an independent developer in Australia. He designs, builds and operates self-hosted, zero-dependency web and infrastructure software.</p>',
        f'<p class="lead">{ABOUT_HTML}</p>',
    )
    t_home = t_home.replace(
        "<p>Send a structured enquiry with work type, budget band, timeline and brief.</p>",
        "<p>Send a structured enquiry with your name, a subject and what you need.</p>",
    )
    index.write_text(t_home, encoding="utf-8")
    print("patched home")

    resume = ROOT / "resume" / "index.html"
    r = _strip_n8(resume.read_text(encoding="utf-8"))
    r = r.replace('width="82" height="82"', 'width="112" height="112"')
    r = r.replace(
        """    <h3>Founder and CEO, N8</h3>
    <p>I founded and lead N8, based in Australia. The work covers technology, development and related interests in markets and AI.</p>
""",
        "",
    )
    resume.write_text(r, encoding="utf-8")
    print("patched resume")


def main() -> None:
    data = load_catalog()
    reset_skills_tree()
    build_skills_index(data)
    for group in data["groups"]:
        build_group_page(data, group)
        for card in group["cards"]:
            build_card_page(data, group, card)
    build_capabilities(data)
    build_business_it()
    build_hire()
    apply_chrome_to_existing()
    patch_home_and_resume()
    patch_about_and_n8()
    build_sitemap(data)
    rebuild_search_index()
    legacy = FAV_DIR / ("x" + ".png")
    if legacy.exists():
        legacy.unlink()
        print("removed unused social favicon")
    print("done. groups", len(data["groups"]), "cards", len(data["_by_slug"]))


if __name__ == "__main__":
    main()
