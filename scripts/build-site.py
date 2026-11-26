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
        ("resume", "/resume/", "Resume", "document"),
        ("hire", "/hire/", "Hire", "briefcase"),
    ]
    skill_groups = [
        ("/skills/web-and-app-engineering/", "Web & App Engineering"),
        ("/skills/backend-and-data/", "Backend & Data"),
        ("/skills/infrastructure/", "Infrastructure & Self-Hosting"),
        ("/skills/protocols-commerce-crypto/", "Protocols, Commerce & Crypto"),
    ]
    links = []
    for key, href, label, icon in items:
        cur = ' aria-current="page"' if current == key else ""
        cls = ' class="nav-hire"' if key == "hire" else ""
        if key == "skills":
            sub = "\n".join(
                f'        <li><a href="{g_href}">{escape(g_label)}</a></li>'
                for g_href, g_label in skill_groups
            )
            links.append(
                "      <div class=\"rk-dd\">\n"
                f'        <a href="{href}"{cur}>{ICONS[icon]}{label}</a>\n'
                '        <ul class="rk-dd-menu" aria-label="Skill groups">\n'
                f"{sub}\n"
                "        </ul>\n"
                "      </div>"
            )
        else:
            links.append(f'      <a href="{href}"{cls}{cur}>{ICONS[icon]}{label}</a>')
    return '    <nav class="rk-nav" aria-label="Primary">\n' + "\n".join(links) + "\n    </nav>"


def header_html(current=None) -> str:
    return (
        '<header class="rk-top">\n'
        '  <div class="rk-top-in">\n'
        '    <a class="rk-wordmark" href="/"><img src="/favicon.svg?v=2" width="16" height="16" alt="">Rohan <span>Kells</span></a>\n'
        f"{nav_html(current)}\n"
        '    <div class="rk-nav-tools">\n'
        '      <div data-auth-kit-slot class="ak-slot"></div>\n'
        '      <button class="rk-menu-btn" type="button" aria-label="Open menu" aria-expanded="false">'
        f'{ICONS["menu"]}</button>\n'
        "    </div>\n"
        "  </div>\n"
        "</header>"
    )


SIDEBAR_GROUPS = [
    (
        "Profile",
        [
            ("/", "Home", "home"),
            ("/about/", "About", "about"),
            ("/background/", "Background", "background"),
            ("/resume/", "Resume", "resume"),
            ("/approach/", "Approach", "approach"),
        ],
    ),
    (
        "Work & Skills",
        [
            ("/skills/", "Skills", "skills"),
            ("/capabilities/", "Capabilities", "capabilities"),
            ("/services/", "Services", "services"),
            ("/business-it/", "Business IT", "business-it"),
            ("/locations/", "Locations", "locations"),
            ("/projects/", "Projects", "projects"),
            ("/tools/", "Tools", "tools"),
        ],
    ),
    (
        "Resources & Contact",
        [
            ("/hire/", "Hire", "hire"),
            ("/contact/", "Contact", "contact"),
            ("/search/", "Search", "search"),
            ("/resources/", "Resources", "resources"),
            ("/faq/", "FAQ", "faq"),
            ("/status/", "Status", "status"),
        ],
    ),
]


def _sidebar_current(href: str, current=None, page_path=None) -> bool:
    if href == "/":
        return page_path in {None, "/", ""} or current == "home"
    if page_path and (page_path == href or page_path.startswith(href)):
        # avoid /skills/ matching when on a more specific current of another section
        if href == "/skills/" and current and current not in {"skills"}:
            # still current if path is under /skills/
            return page_path.startswith("/skills/")
        return True
    key_map = {
        "/skills/": "skills",
        "/capabilities/": "capabilities",
        "/business-it/": "business-it",
        "/resume/": "resume",
        "/hire/": "hire",
        "/about/": "about",
        "/background/": "background",
        "/projects/": "projects",
        "/services/": "services",
        "/tools/": "tools",
        "/approach/": "approach",
        "/contact/": "contact",
        "/search/": "search",
        "/resources/": "resources",
        "/faq/": "faq",
        "/status/": "status",
    }
    return bool(current) and key_map.get(href) == current


def sidebar_html(current=None, page_path=None) -> str:
    blocks = ['<aside class="rk-side">', '  <details class="rk-side-panel">', '    <summary class="rk-side-toggle">Site menu</summary>', '    <nav class="rk-side-nav" aria-label="Site">']
    for label, items in SIDEBAR_GROUPS:
        blocks.append(f'      <p class="rk-side-label">{escape(label)}</p>')
        for href, name, _key in items:
            cur = ' aria-current="page"' if _sidebar_current(href, current, page_path) else ""
            blocks.append(f'      <a href="{href}"{cur}>{escape(name)}</a>')
    blocks += ["    </nav>", "  </details>", "</aside>"]
    return "\n".join(blocks)


def strip_auth_kit(text: str) -> str:
    text = re.sub(r'\s*<link rel="stylesheet" href="/auth-kit/auth.css">', "", text)
    text = re.sub(r'\s*<script src="/auth-kit/header.js" defer></script>', "", text)
    return text


def ensure_layout(text: str, current=None, page_path=None) -> str:
    """Insert or refresh the left sidebar layout without disturbing page main content."""
    text = strip_auth_kit(text)
    if 'class="page-bg"' not in text and "<body" in text:
        text = re.sub(
            r"(<body[^>]*>)",
            r'\1\n<div class="page-bg" aria-hidden="true"></div>',
            text,
            count=1,
        )
    header_re = re.compile(r'<header class="rk-top">.*?</header>', re.S)
    footer_re = re.compile(r'<footer class="rk-foot">.*?</footer>', re.S)
    if header_re.search(text):
        text = header_re.sub(header_html(current), text, count=1)
    if footer_re.search(text):
        text = footer_re.sub(footer_html(), text, count=1)
    side = sidebar_html(current, page_path)
    side_re = re.compile(r'<aside class="rk-side">.*?</aside>', re.S)
    if 'class="rk-body"' in text and side_re.search(text):
        return side_re.sub(side, text, count=1)
    if header_re.search(text):
        text = header_re.sub(lambda m: m.group(0) + '\n<div class="rk-body">\n' + side + '\n<div class="rk-content">\n', text, count=1)
        text, n = re.subn(
            r"</footer>\s*</div>\s*</body>",
            "</footer>\n</div>\n</div>\n</div>\n</body>",
            text,
            count=1,
        )
        if n != 1:
            # fallback: close before final body if footer already wrapped unusually
            text, n2 = re.subn(
                r"</footer>\s*</div>\s*</div>\s*</body>",
                "</footer>\n</div>\n</div>\n</div>\n</body>",
                text,
                count=1,
            )
            if n2 != 1:
                print("warn: could not close rk-body layout for", page_path or current)
    return text



MAIL_ICON_SVG = (
    '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
    '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg>'
)


def mail_link() -> str:
    return (
        f'<a class="mail-ico" href="mailto:{EMAIL}" '
        f'aria-label="Email {EMAIL}" title="{EMAIL}">{MAIL_ICON_SVG}</a>'
    )


def footer_html() -> str:
    updated = last_updated_label()
    return f"""<footer class="rk-foot">
  <div class="rk-foot-in">
    <div class="rk-legal">
      <p>&copy; 2026 Rohan Kells. Australia. {mail_link()}</p>
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
<link rel="apple-touch-icon" href="/apple-touch-icon.png?v=2">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="icon" href="/favicon-32.png?v=2" sizes="32x32" type="image/png">
<link rel="icon" href="/favicon-16.png?v=2" sizes="16x16" type="image/png">
<link rel="icon" href="/favicon.svg?v=2" type="image/svg+xml">
<link rel="stylesheet" href="/assets/rk-portfolio.css">
<script src="/assets/rk-nav.js" defer></script>
{script_tags}
<script type="application/ld+json">
{ld}
</script>
</head>"""


def page(title, description, canonical, current, main, jsonld, scripts=None) -> str:
    path = canonical.replace(SITE, "") if canonical.startswith(SITE) else canonical
    return (
        head_html(title, description, canonical, jsonld, scripts)
        + "\n<body>\n"
        + '<a class="skip" href="#main">Skip to content</a>\n'
        + '<div class="page-bg" aria-hidden="true"></div>\n'
        + '<div class="wrap">\n'
        + header_html(current)
        + '\n<div class="rk-body">\n'
        + sidebar_html(current, path)
        + '\n<div class="rk-content">\n'
        + '<main id="main">\n'
        + main
        + "\n</main>\n"
        + footer_html()
        + "\n</div>\n</div>\n</div>\n</body>\n</html>\n"
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
    "cycle": _svg('<path d="M4 12a8 8 0 0 1 14-4M18 4v4h-4M20 12a8 8 0 0 1-14 4M6 20v-4h4"/>'),
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


def level_html(card: dict) -> str:
    level = (card.get("level") or "").strip()
    if not level:
        return ""
    return f'<span class="skill-level">{escape(level)}</span>'


def card_item(group: dict, card: dict) -> str:
    kw = " ".join(card.get("keywords") or [])
    level = level_html(card)
    level_line = f"          {level}\n" if level else ""
    return (
        f'      <a class="card repo-card" data-skill-item data-name="{escape(card["name"], quote=True)}" '
        f'data-keywords="{escape(kw, quote=True)}" data-category="{escape(group["name"], quote=True)}" '
        f'href="{card_path(group, card)}">\n'
        f'        {logo_html(card)}\n'
        f'        <span class="meta">\n'
        f'          <strong>{escape(card["name"])}</strong>\n'
        f"{level_line}"
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
            f'      <h2>{escape(group["name"])}</h2>\n'
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
        '    <details class="rk-acc">\n'
        '      <summary>Browse every card</summary>\n'
        '      <div class="rk-acc-body rk-panel-scroll">\n'
        '    <p class="sub">Each card has its own page, including official cached marks for third-party platforms.</p>\n'
        '    <div class="grid">\n'
        + "\n".join(all_cards) + '\n'
        '    </div>\n'
        '      </div>\n'
        '    </details>\n'
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
        '    <div class="grid rk-panel-scroll">\n'
        + cards + '\n'
        '    </div>\n'
        f'    <p class="section-links"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="/skills/">All skills</a></p>\n'
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
        f'    <div class="card-head">\n      {logo_html(card)}\n      <h1>{escape(card["name"])}{(" " + level_html(card)) if card.get("level") else ""}</h1>\n    </div>\n'
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
            f'      <h2>{escape(group["name"])}</h2>\n'
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
        <h2>Business email and domain setup</h2>
        <p>DNS for your domain, including SPF, DKIM and DMARC. Self-hosted or managed mail, mailbox migrations, and a clean cutover plan.</p>
      </article>
      <article class="block">
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16v4H4zM4 14h16v4H4z"/></svg>
        <h2>Servers, networks and backups</h2>
        <p>Linux and Windows servers, local networks, VPNs, and automated backups with retention you can actually restore from.</p>
      </article>
      <article class="block">
        <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3l8 4v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V7l8-4z"/></svg>
        <h2>Security, workstations and uptime</h2>
        <p>Security hardening, workstation setup, uptime monitoring, and ongoing fixed-scope IT support so the environment stays maintained.</p>
      </article>
    </div>
    <p class="sub" style="margin-top:16px">This work is for organisations in Australia. I take a limited number of fixed-scope engagements at a time so delivery stays realistic.</p>
    <p class="section-links"><a class="btn" href="/hire/">Request an IT audit or quote</a> <a class="btn btn-ghost" href="/business-it/remote-support/">Remote support</a> <a class="btn btn-ghost" href="/skills/infrastructure/">Infrastructure skills</a> <a class="btn btn-ghost" href="/locations/">Locations</a></p>
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
        <h2>Custom software and web apps</h2>
        <p>New sites and applications, or a defined improvement to an existing system, with a written scope and delivery plan.</p>
      </article>
      <article class="block">
        {ICONS["building"]}
        <h2>Small business IT and infrastructure</h2>
        <p>Email and domains, servers, networks, backups, hardening and fixed-scope support for organisations in Australia.</p>
      </article>
      <article class="block">
        {ICONS["nodes"]}
        <h2>Protocols, RPC, crypto and commerce</h2>
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


SITEMAP_SKIP_DIRS = {"thank-you", "thanks", "legal"}
SITEMAP_SKIP_FILES = {"404.html", "500.html"}


def iter_public_page_urls() -> list[str]:
    urls = []
    for pth in sorted(ROOT.rglob("*.html")):
        if ".git" in pth.parts:
            continue
        rel = pth.relative_to(ROOT)
        if rel.name in SITEMAP_SKIP_FILES:
            continue
        if rel.parts and rel.parts[0] in SITEMAP_SKIP_DIRS:
            continue
        urls.append(_page_path_from(pth))
    # stable unique
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    return seen


def build_sitemap(data: dict) -> None:
    urls = iter_public_page_urls()
    for extra in ("/capabilities/", "/business-it/", "/hire/", "/skills/", "/background/"):
        if extra not in urls:
            urls.append(extra)
    for group in data["groups"]:
        gp = group_path(group)
        if gp not in urls:
            urls.append(gp)
        for card in group["cards"]:
            cp = card_path(group, card)
            if cp not in urls:
                urls.append(cp)
    seen = []
    for u in urls:
        if u not in seen:
            seen.append(u)
    body = "\n".join(f"  <url><loc>{SITE}{u}</loc></url>" for u in seen)
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "\n</urlset>\n"
    write(ROOT / "sitemap.xml", xml)
    print("sitemap urls", len(seen))


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
    pages = []
    for pth in sorted(ROOT.rglob("*.html")):
        if ".git" in pth.parts:
            continue
        rel = pth.relative_to(ROOT)
        if rel.name in SITEMAP_SKIP_FILES:
            continue
        if rel.parts and rel.parts[0] in SITEMAP_SKIP_DIRS:
            continue
        pages.append(pth)
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
    + mail_link()
    + "."
)


def _page_path_from(pth: Path) -> str:
    rel = pth.relative_to(ROOT)
    s = str(rel).replace("\\", "/")
    if s == "index.html":
        return "/"
    if s.endswith("/index.html"):
        return "/" + s[:-10]
    return "/" + s


def apply_chrome_to_existing() -> None:
    theme_re = re.compile(r'<meta name="theme-color" content="[^"]*"(?: media="[^"]*")?>')
    skip_dirs = {"skills", "capabilities", "business-it", "hire", "locations"}
    current_by_dir = {
        "resume": "resume",
        "about": "about",
        "background": "background",
        "approach": "approach",
        "projects": "projects",
        "services": "services",
        "tools": "tools",
        "contact": "contact",
        "search": "search",
        "resources": "resources",
        "faq": "faq",
        "status": "status",
        "hire": "hire",
        "locations": "locations",
    }
    for pth in ROOT.rglob("*.html"):
        if ".git" in pth.parts:
            continue
        rel = pth.relative_to(ROOT)
        if rel.parts and rel.parts[0] in skip_dirs:
            continue
        # Legal aliases are written as redirects after chrome runs.
        if rel.parts[:2] in {("legal", "privacy"), ("legal", "terms")}:
            continue
        text = pth.read_text(encoding="utf-8")
        orig = text
        page_path = _page_path_from(pth)
        current = current_by_dir.get(rel.parts[0] if rel.parts else "")
        if pth == ROOT / "index.html":
            current = "home"
            page_path = "/"
        text = ensure_layout(text, current, page_path)
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


LOCATION_BLOCK = (
    "    <div class=\"hero-location-block\">\n"
    "      <p class=\"hero-location\"><svg aria-hidden=\"true\" viewBox=\"0 0 24 24\" fill=\"none\" "
    "stroke=\"currentColor\" stroke-width=\"1.6\" stroke-linecap=\"round\" stroke-linejoin=\"round\">"
    "<path d=\"M12 21s-6-5.33-6-10a6 6 0 1 1 12 0c0 4.67-6 10-6 10z\"/>"
    "<circle cx=\"12\" cy=\"11\" r=\"2.2\"/></svg><span>Australia</span> &middot; <a href=\"/locations/\">Locations across Australia</a></p>\n"
    "    </div>"
)


HOME_SEARCH = """    <form class="site-search hero-search" data-site-search data-inline-search data-search-out="home-search-out" role="search" action="/search/" method="get">
      <label for="home-q">Search this site</label>
      <div class="ask-row">
        <input id="home-q" type="search" name="q" autocomplete="off" enterkeyhint="search">
        <button class="btn" type="submit">Search</button>
      </div>
      <div id="home-search-out" class="search-out" aria-live="polite"></div>
    </form>"""


def _ensure_home_hero(t_home: str) -> str:
    """Keep a minimal homepage: photo, name, clean Australia location line, lede, key links and inline search."""
    t_home = t_home.replace('width="70" height="70"', 'width="160" height="160"')
    t_home = re.sub(r"\s*<div class=\"hero-location-block\">.*?</div>\s*(?=\n\s*<p class=\"lede\">)", "", t_home, flags=re.S)
    t_home = re.sub(r"\s*<p class=\"hero-location\">.*?</p>", "", t_home, flags=re.S)
    needle = "        <h1>Rohan Martin Kells</h1>\n      </div>\n    </div>"
    if needle in t_home:
        t_home = t_home.replace(needle, needle + "\n" + LOCATION_BLOCK, 1)
    if "data-inline-search" not in t_home:
        if re.search(r'<ul class="hero-key-links">.*?</ul>', t_home, flags=re.S):
            t_home = re.sub(
                r'(<ul class="hero-key-links">.*?</ul>)',
                r"\1\n" + HOME_SEARCH,
                t_home,
                count=1,
                flags=re.S,
            )
        else:
            t_home = re.sub(
                r'(<div class="hero-cta">.*?</div>)',
                r"\1\n" + HOME_SEARCH,
                t_home,
                count=1,
                flags=re.S,
            )
    if "/assets/rk-search.js" not in t_home:
        t_home = t_home.replace(
            '<script src="/assets/rk-nav.js" defer></script>',
            '<script src="/assets/rk-nav.js" defer></script>\n<script src="/assets/rk-search.js" defer></script>',
            1,
        )
    # Never re-inject a skills wall on the homepage.
    return t_home


def patch_home_and_resume() -> None:
    index = ROOT / "index.html"
    t_home = _strip_n8(index.read_text(encoding="utf-8"))
    t_home = _ensure_home_hero(t_home)
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


def patch_error_pages() -> None:
    for name in ("404.html", "500.html"):
        path = ROOT / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = re.sub(
            r'<link rel="canonical" href="https://rohankells.com/[^"]*">',
            f'<link rel="canonical" href="{SITE}/{name}">',
            text,
            count=1,
        )
        if 'name="robots"' not in text:
            text = text.replace(
                '<meta charset="utf-8">',
                '<meta charset="utf-8">\n<meta name="robots" content="noindex">',
                1,
            )
        path.write_text(text, encoding="utf-8")
        print("patched", name)


def write_legal_alias(src_path: str, dest: str, title: str) -> None:
    dest_url = f"{SITE}{dest}"
    html = f"""<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)} — Rohan Kells</title>
<link rel="canonical" href="{dest_url}">
<meta http-equiv="refresh" content="0; url={dest}">
{theme_tags()}
</head>
<body>
<p>This page has moved to <a href="{dest}">{escape(title)}</a>.</p>
</body>
</html>
"""
    write(ROOT / src_path / "index.html", html)


def patch_legal_aliases() -> None:
    write_legal_alias("legal/privacy", "/privacy/", "Privacy")
    write_legal_alias("legal/terms", "/terms/", "Terms")



LOCATIONS = [
    {
        "slug": "nsw",
        "name": "New South Wales",
        "short": "NSW",
        "capital": "Sydney",
        "summary": "Web platforms, business IT and infrastructure work for organisations in New South Wales, including Sydney and regional centres across the state.",
        "body": (
            "I work with organisations in New South Wales on web platforms, integrations, and day-to-day business IT. "
            "Sydney is the capital and a frequent point of contact, and the same fixed-scope approach covers regional centres when remote sessions or a scheduled visit is the better fit. "
            "Typical work includes email and DNS, servers and networks, application delivery, and practical support for teams that want a clear owner for the system."
        ),
        "focus": (
            "Engagements in the state usually start with a written scope: what is in, what is out, and how we will hand the work back. "
            "That keeps delivery realistic whether the job is a mailbox cutover, a self-hosted service, or a small internal tool."
        ),
    },
    {
        "slug": "vic",
        "name": "Victoria",
        "short": "VIC",
        "capital": "Melbourne",
        "summary": "Software and business IT for organisations in Victoria, including Melbourne and regional Victoria, delivered as fixed-scope remote or on-site work.",
        "body": (
            "Victoria is covered for software delivery and business IT. Melbourne is the capital, and I also work with organisations in regional Victoria when a defined piece of work needs an independent operator. "
            "The brief stays practical: platforms that can be maintained, mail and identity that actually deliver, and infrastructure that can be restored."
        ),
        "focus": (
            "A typical Victorian engagement is a contained project — a migration, a hardening pass, or a build with a documented hand-over — rather than an open-ended retainer with no edge."
        ),
    },
    {
        "slug": "qld",
        "name": "Queensland",
        "short": "QLD",
        "capital": "Brisbane",
        "summary": "Fixed-scope web, infrastructure and business IT work for organisations in Queensland, including Brisbane and centres further north and west.",
        "body": (
            "Queensland work covers web applications, infrastructure and business IT for organisations in Brisbane, the capital, and in other centres across the state. "
            "Distance is handled with secure remote sessions first, and travel is planned only when the scope genuinely needs hands on the hardware or a room of people at once."
        ),
        "focus": (
            "I keep runbooks and access notes with the client so the system is not locked to a single operator after the engagement ends."
        ),
    },
    {
        "slug": "sa",
        "name": "South Australia",
        "short": "SA",
        "capital": "Adelaide",
        "summary": "Independent software and IT support for organisations in South Australia, with Adelaide as the capital and a clear written scope for each job.",
        "body": (
            "In South Australia I take on web, infrastructure and business IT work for organisations based in Adelaide, the capital, and elsewhere in the state. "
            "The work is the same craft as elsewhere in Australia: DNS and mail, servers, integrations, and applications that a small team can keep running."
        ),
        "focus": (
            "Scopes are written so finance and operations can see the boundary of the job, the expected artefacts, and when the work is done."
        ),
    },
    {
        "slug": "wa",
        "name": "Western Australia",
        "short": "WA",
        "capital": "Perth",
        "summary": "Web platforms and business IT for organisations in Western Australia, including Perth, with remote delivery as the default and travel when the work requires it.",
        "body": (
            "Western Australia spans a long distance from Perth, the capital, to regional centres. Most of my work for organisations in the state is delivered remotely, with careful change windows that respect local time. "
            "When a visit is the right tool, it is scheduled against a written scope rather than an open ticket pile."
        ),
        "focus": (
            "Reliable remote access, backups you can restore, and documentation that survives the engagement are the usual foundations."
        ),
    },
    {
        "slug": "tas",
        "name": "Tasmania",
        "short": "TAS",
        "capital": "Hobart",
        "summary": "Software, infrastructure and business IT for organisations in Tasmania, including Hobart and regional Tasmania, delivered as contained fixed-scope work.",
        "body": (
            "Tasmania is part of the same Australia-wide practice. I work with organisations in Hobart, the capital, and in other parts of the state on web platforms, mail and identity, and the infrastructure those services sit on. "
            "Remote sessions cover most tasks; a visit is arranged when hardware, a cutover, or a workshop is genuinely needed on the ground."
        ),
        "focus": (
            "Smaller teams often need a single owner for a defined job rather than a large managed-service contract. That is the shape of work I take on."
        ),
    },
    {
        "slug": "nt",
        "name": "Northern Territory",
        "short": "NT",
        "capital": "Darwin",
        "summary": "Business IT and infrastructure support for organisations in the Northern Territory, including Darwin, planned around local time and a clear scope.",
        "body": (
            "The Northern Territory is covered for business IT and infrastructure work. Darwin is the capital, and I also work with organisations elsewhere in the Territory when a fixed-scope job is a good fit. "
            "Time zones and connectivity are part of the plan: changes are scheduled, access is agreed in advance, and rollback is written down before anything is touched."
        ),
        "focus": (
            "The aim is a system the local team can operate afterwards, with notes, credentials handling, and restore steps that have been tested."
        ),
    },
    {
        "slug": "act",
        "name": "Australian Capital Territory",
        "short": "ACT",
        "capital": "Canberra",
        "summary": "Web, infrastructure and business IT work for organisations in the Australian Capital Territory, including Canberra, delivered as written fixed-scope engagements.",
        "body": (
            "The Australian Capital Territory is covered alongside the states. Canberra is the capital, and I work with organisations there on web platforms, integrations, and business IT that has to be documented and defensible. "
            "Engagements stay bounded: a stated outcome, a working system, and a hand-over the team can keep."
        ),
        "focus": (
            "Where policy or records matter, I leave a paper trail of what changed, why, and how to reverse it."
        ),
    },
]


def build_locations() -> None:
    loc_icon = (
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 21s-6-5.33-6-10a6 6 0 1 1 12 0c0 4.67-6 10-6 10z"/>'
        '<circle cx="12" cy="11" r="2.2"/></svg>'
    )
    cards = []
    for loc in LOCATIONS:
        cards.append(
            '      <article class="card">\n'
            f'        <h2><a href="/locations/{loc["slug"]}/">{escape(loc["name"])}</a></h2>\n'
            f'        <p>{escape(loc["summary"])}</p>\n'
            f'        <p class="sub">Capital: {escape(loc["capital"])}.</p>\n'
            "      </article>"
        )
    hub_main = (
        '  <header class="page-hero">\n'
        f'    <p class="eyebrow"><a href="/">Home</a> / Locations</p>\n'
        '    <div class="card-head">\n'
        f'      <span class="logo">{loc_icon}</span>\n'
        "      <h1>Locations</h1>\n"
        "    </div>\n"
        "    <p>I work with organisations across Australia. State and territory pages describe how I take on work in each place. I do not publish a personal address.</p>\n"
        "  </header>\n"
        '  <section class="section">\n'
        '    <details class="rk-acc" open>\n'
        "      <summary>States and territories</summary>\n"
        '      <div class="rk-acc-body loc-grid">\n'
        + "\n".join(cards) + "\n"
        "      </div>\n"
        "    </details>\n"
        '    <p class="section-links"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="/business-it/">Business IT</a> <a class="btn btn-ghost" href="/skills/">Skills</a> <a class="btn btn-ghost" href="/capabilities/">Capabilities</a></p>\n'
        "  </section>"
    )
    hub_title = "Locations in Australia — Rohan Kells"
    hub_desc = "Rohan Kells works with organisations across Australia. Read how fixed-scope software and business IT work is delivered in each state and territory."
    hub_canon = f"{SITE}/locations/"
    hub_ld = [
        person_ld(),
        {"@type": "WebPage", "@id": hub_canon, "url": hub_canon, "name": hub_title, "description": hub_desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "ProfessionalService", "name": "Rohan Kells", "url": hub_canon, "areaServed": "Australia"},
    ]
    write(ROOT / "locations" / "index.html", page(hub_title, hub_desc, hub_canon, "locations", hub_main, hub_ld))

    for loc in LOCATIONS:
        others = "".join(
            f'<li><a href="/locations/{o["slug"]}/">{escape(o["name"])}</a></li>'
            for o in LOCATIONS
            if o["slug"] != loc["slug"]
        )
        main = (
            '  <header class="page-hero">\n'
            f'    <p class="eyebrow"><a href="/">Home</a> / <a href="/locations/">Locations</a> / {escape(loc["name"])}</p>\n'
            '    <div class="card-head">\n'
            f'      <span class="logo">{loc_icon}</span>\n'
            f'      <h1>{escape(loc["name"])}</h1>\n'
            "    </div>\n"
            f'    <p>{escape(loc["summary"])}</p>\n'
            "  </header>\n"
            '  <section class="section">\n'
            f'    <h2>Working in {escape(loc["name"])}</h2>\n'
            f'    <p class="sub">{escape(loc["body"])}</p>\n'
            f'    <h2>How engagements run</h2>\n'
            f'    <p class="sub">{escape(loc["focus"])}</p>\n'
            "    <h2>Other locations</h2>\n"
            f'    <ul class="related">{others}</ul>\n'
            '    <p class="section-links"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="/skills/">Skills</a> <a class="btn btn-ghost" href="/capabilities/">Capabilities</a> <a class="btn btn-ghost" href="/business-it/">Business IT</a> <a class="btn btn-ghost" href="/locations/">All locations</a></p>\n'
            "  </section>"
        )
        title = f"{loc['name']} — Locations — Rohan Kells"
        desc = loc["summary"]
        if len(desc) > 160:
            desc = desc[:157] + "..."
        canon = f"{SITE}/locations/{loc['slug']}/"
        ld = [
            person_ld(),
            {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
            {"@type": "ProfessionalService", "name": "Rohan Kells", "description": loc["summary"], "provider": {"@id": f"{SITE}/#person"}, "areaServed": f"{loc['name']}, Australia", "url": canon},
        ]
        write(ROOT / "locations" / loc["slug"] / "index.html", page(title, desc, canon, "locations", main, ld))


def build_remote_support(data: dict) -> None:
    related_slugs = [
        "linux",
        "windows",
        "vpn",
        "microsoft-365",
        "networking-fundamentals",
        "business-it",
        "incident-response",
    ]
    related_links = []
    for slug in related_slugs:
        hit = data.get("_by_slug", {}).get(slug)
        if not hit:
            continue
        g, c = hit
        related_links.append(f'<li><a href="{card_path(g, c)}">{escape(c["name"])}</a></li>')
    related_html = ""
    if related_links:
        related_html = '<h2>Related skills</h2>\n    <ul class="related">\n      ' + "\n      ".join(related_links) + "\n    </ul>"
    icon = (
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="3" y="4" width="18" height="12" rx="2"/>'
        '<path d="M8 20h8M12 16v4"/>'
        '<circle cx="12" cy="10" r="2"/>'
        "</svg>"
    )
    summary = "Remote support, remote assistance and business helpdesk in Australia for workstations, servers, email and networks."
    what = (
        "I provide remote troubleshooting for workstations and servers, Windows and Linux helpdesk work, and secure remote sessions for email, identity and network fixes. "
        "Sessions are scheduled against a written scope, access is agreed in advance, and changes are documented so your team can keep the system afterwards."
    )
    main = (
        '  <header class="page-hero">\n'
        '    <p class="eyebrow"><a href="/">Home</a> / <a href="/business-it/">Business IT</a> / Remote Support</p>\n'
        '    <div class="card-head">\n'
        f'      <span class="logo">{icon}</span>\n'
        "      <h1>Remote Support</h1>\n"
        "    </div>\n"
        f"    <p>{escape(summary)}</p>\n"
        "  </header>\n"
        '  <section class="section">\n'
        "    <h2>What I do</h2>\n"
        f'    <p class="sub">{escape(what)}</p>\n'
        f"    {related_html}\n"
        '    <p class="section-links"><a class="btn" href="/hire/">Hire me</a> <a class="btn btn-ghost" href="/business-it/">Back to Business IT</a> <a class="btn btn-ghost" href="/locations/">Locations</a></p>\n'
        "  </section>"
    )
    title = "Remote Support — Business IT — Rohan Kells"
    desc = summary
    canon = f"{SITE}/business-it/remote-support/"
    ld = [
        person_ld(),
        {"@type": "WebPage", "@id": canon, "url": canon, "name": title, "description": desc, "isPartOf": {"@id": f"{SITE}/#site"}},
        {"@type": "Service", "name": "Remote Support", "description": summary, "provider": {"@id": f"{SITE}/#person"}, "areaServed": "Australia", "url": canon, "isRelatedTo": {"@type": "Service", "name": "Business IT", "url": f"{SITE}/business-it/"}},
    ]
    write(ROOT / "business-it" / "remote-support" / "index.html", page(title, desc, canon, "business-it", main, ld))


def patch_mailto_icons() -> None:
    pattern = re.compile(
        r'<a\s+(?=[^>]*href="mailto:support@rohankells\.com")(?![^>]*mail-ico)[^>]*>.*?</a>',
        re.I | re.S,
    )
    icon = mail_link()
    changed = 0
    for pth in ROOT.rglob("*.html"):
        if any(part.startswith(".") or part in {"node_modules"} for part in pth.parts):
            continue
        text = pth.read_text(encoding="utf-8")
        new = pattern.sub(icon, text)
        if new != text:
            pth.write_text(new, encoding="utf-8")
            changed += 1
    print("mailto icons", changed)


def patch_favicon_cachebust() -> None:
    reps = [
        (re.compile(r'href="/apple-touch-icon\.png(?:\?v=\d+)?"'), 'href="/apple-touch-icon.png?v=2"'),
        (re.compile(r'href="/favicon\.ico(?:\?v=\d+)?"'), 'href="/favicon.ico?v=2"'),
        (re.compile(r'href="/favicon\.svg(?:\?v=\d+)?"'), 'href="/favicon.svg?v=2"'),
        (re.compile(r'href="/favicon-16\.png(?:\?v=\d+)?"'), 'href="/favicon-16.png?v=2"'),
        (re.compile(r'href="/favicon-32\.png(?:\?v=\d+)?"'), 'href="/favicon-32.png?v=2"'),
        (re.compile(r'src="/favicon\.svg(?:\?v=\d+)?"'), 'src="/favicon.svg?v=2"'),
    ]
    insert = (
        '<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">\n'
        '<link rel="icon" href="/favicon-32.png?v=2" sizes="32x32" type="image/png">\n'
        '<link rel="icon" href="/favicon-16.png?v=2" sizes="16x16" type="image/png">'
    )
    changed = 0
    for pth in ROOT.rglob("*.html"):
        if any(part.startswith(".") or part in {"node_modules"} for part in pth.parts):
            continue
        text = pth.read_text(encoding="utf-8")
        new = text
        for pat, rep in reps:
            new = pat.sub(rep, new)
        if 'href="/favicon-32.png?v=2"' not in new and 'rel="icon" href="/favicon.ico?v=2"' in new:
            new = re.sub(
                r'<link rel="icon" href="/favicon\.ico\?v=2"[^>]*>',
                insert,
                new,
                count=1,
            )
        elif 'href="/favicon-32.png?v=2"' not in new and 'rel="apple-touch-icon"' in new:
            new = re.sub(
                r'(<link rel="apple-touch-icon"[^>]*>)',
                r"\1\n" + insert,
                new,
                count=1,
            )
        if new != text:
            pth.write_text(new, encoding="utf-8")
            changed += 1
    print("favicon cache-bust", changed)


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
    build_remote_support(data)
    build_locations()
    build_hire()
    apply_chrome_to_existing()
    patch_home_and_resume()
    patch_about_and_n8()
    patch_error_pages()
    patch_legal_aliases()
    patch_mailto_icons()
    patch_favicon_cachebust()
    build_sitemap(data)
    rebuild_search_index()
    legacy = FAV_DIR / ("x" + ".png")
    if legacy.exists():
        legacy.unlink()
        print("removed unused social favicon")
    print("done. groups", len(data["groups"]), "cards", len(data["_by_slug"]))


if __name__ == "__main__":
    main()
