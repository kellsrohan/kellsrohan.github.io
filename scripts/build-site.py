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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "skills.json"
FAV_DIR = ROOT / "assets" / "favicons"
EMAIL = "support@rohankells.com"
SITE = "https://rohankells.com"
OG = f"{SITE}/assets/photos/kellsrohan.png"
GITHUB = "https://github.com/kellsrohan"


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


def nav_html(current=None) -> str:
    items = [
        ("skills", "/skills/", "Skills"),
        ("business-it", "/business-it/", "Business IT"),
        ("about", "/about/", "About"),
        ("contact", "/contact/", "Contact"),
        ("hire", "/hire/", "Hire"),
    ]
    links = []
    for key, href, label in items:
        cur = ' aria-current="page"' if current == key else ""
        cls = ' class="nav-hire"' if key == "hire" else ""
        links.append(f'      <a href="{href}"{cls}{cur}>{label}</a>')
    return '    <nav class="rk-nav" aria-label="Primary">\n' + "\n".join(links) + "\n    </nav>"


def header_html(current=None) -> str:
    return (
        '<header class="rk-top">\n'
        '  <div class="rk-top-in">\n'
        '    <a class="rk-wordmark" href="/">Rohan <span>Kells</span></a>\n'
        f"{nav_html(current)}\n"
        '    <div class="rk-nav-tools">\n'
        '      <div data-auth-kit-slot class="ak-slot"></div>\n'
        '      <button class="rk-menu-btn" type="button" aria-label="Open menu" aria-expanded="false">'
        '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        'stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>\n'
        "    </div>\n"
        "  </div>\n"
        "</header>"
    )


def footer_html() -> str:
    return f"""<footer class="rk-foot">
  <div class="rk-foot-in">
    <div class="rk-foot-grid">
      <div>
        <p class="brand-f">Rohan Kells</p>
        <p>Independent developer in Australia.</p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      <div>
        <p class="brand-f" style="font-size:1rem">Site</p>
        <ul>
          <li><a href="/skills/">Skills</a></li>
          <li><a href="/capabilities/">Capabilities</a></li>
          <li><a href="/business-it/">Business IT</a></li>
          <li><a href="/hire/">Hire</a></li>
          <li><a href="/about/">About</a></li>
          <li><a href="/resume/">Resume</a></li>
          <li><a href="/contact/">Contact</a></li>
        </ul>
      </div>
      <div>
        <p class="brand-f" style="font-size:1rem">Legal</p>
        <ul>
          <li><a href="/privacy/">Privacy</a></li>
          <li><a href="/terms/">Terms</a></li>
          <li><a href="/refunds/">Refund policy</a></li>
          <li><a href="/delivery/">Delivery</a></li>
          <li><a href="/cookies/">Cookies</a></li>
        </ul>
      </div>
    </div>
    <div class="rk-legal">
      <p>&copy; 2026 Rohan Kells. Australia.</p>
      <nav aria-label="Social and legal">
        <a href="{GITHUB}" rel="noopener noreferrer">GitHub</a>
        <a href="/privacy/">Privacy</a>
        <a href="/terms/">Terms</a>
        <a href="/refunds/">Refunds</a>
        <a href="/delivery/">Delivery</a>
        <a href="/cookies/">Cookies</a>
        <a href="/contact/">Contact</a>
        <a href="/about/">About</a>
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


ICONS = {
    "code": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="m8 8-4 4 4 4M16 8l4 4-4 4"/></svg>',
    "database": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/></svg>',
    "server": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6h16v4H4zM4 14h16v4H4zM8 8h.01M8 16h.01"/></svg>',
    "nodes": '<svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="M8 7.5 10.5 16M16 7.5 13.5 16"/></svg>',
}


def logo_html(card: dict) -> str:
    src = favicon_url(card)
    if src:
        return f'<span class="logo"><img class="favicon" src="{src}" width="16" height="16" alt=""></span>'
    initial = escape(card["name"][:1].upper())
    return f'<span class="logo"><span class="mono">{initial}</span></span>'


def search_bar(label: str) -> str:
    return (
        '    <div class="skills-search">\n'
        f'      <label for="skills-q">{escape(label)}</label>\n'
        '      <input id="skills-q" type="search" data-skills-search autocomplete="off" maxlength="200">\n'
        '      <p class="search-count" data-search-count></p>\n'
        '      <p data-empty>No skills or cards match that search.</p>\n'
        '    </div>'
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
    main = f"""  <aside class="avail-banner" data-status="open" aria-live="polite">
    <div>
      <p data-when="open" style="margin:0"><strong>Availability:</strong> Currently open for 1-2 fixed-scope projects.</p>
      <p data-when="waitlist" style="margin:0"><strong>Availability:</strong> Intake is on a waitlist. New work is not being taken on at this time.</p>
    </div>
  </aside>
  <header class="page-hero">
    <h1>Hire / Work with me</h1>
    <p>Tell me the work type, budget band, timeline and a short brief. Your mail application opens with a structured message to {EMAIL} — there is no form server.</p>
  </header>
  <section class="section">
    <p class="eyebrow">Engagements</p>
    <h2>Fixed-scope options</h2>
    <p class="sub">I work in clear, written scopes so both sides know what is being delivered.</p>
    <div class="blocks">
      <article class="block">
        <h3>Custom software and web apps</h3>
        <p>New sites and applications, or a defined improvement to an existing system, with a written scope and delivery plan.</p>
      </article>
      <article class="block">
        <h3>Small business IT and infrastructure</h3>
        <p>Email and domains, servers, networks, backups, hardening and fixed-scope support for organisations in Australia.</p>
      </article>
      <article class="block">
        <h3>Protocols, RPC, crypto and commerce</h3>
        <p>APIs and integrations, checkout and subscriptions, and on-chain settlement where a product genuinely needs it.</p>
      </article>
    </div>
  </section>
  <section class="section" id="enquiry">
    <p class="eyebrow">Enquiry</p>
    <h2>Structured project enquiry</h2>
    <p class="sub">Required fields keep the first message useful. When you submit, your email app opens with the work type, budget band, timeline and brief already filled in.</p>
    <form class="hire-form" id="hire-enquiry" action="mailto:{EMAIL}" method="post" enctype="text/plain">
      <label>Name (required)<input name="name" autocomplete="name" maxlength="100" required></label>
      <label>Email (required)<input name="email" type="email" autocomplete="email" maxlength="254" required></label>
      <label>Work type (required)
        <select name="work_type" required>
          <option value="">Select a work type</option>
          <option>Custom software and web apps</option>
          <option>Small business IT and infrastructure</option>
          <option>Protocols, RPC, crypto and commerce</option>
        </select>
      </label>
      <label>Budget band, AUD (required)
        <select name="budget" required>
          <option value="">Select a budget band</option>
          <option>Under $3,000 AUD</option>
          <option>$3,000-$8,000 AUD</option>
          <option>$8,000-$20,000 AUD</option>
          <option>$20,000+ AUD</option>
          <option>Budget to be confirmed in writing</option>
        </select>
      </label>
      <label>Timeline (required)
        <select name="timeline" required>
          <option value="">Select a timeline</option>
          <option>Within 2 weeks</option>
          <option>2-6 weeks</option>
          <option>1-3 months</option>
          <option>Flexible</option>
        </select>
      </label>
      <label>Project brief (required)<textarea name="brief" rows="7" maxlength="4000" required></textarea></label>
      <div hidden><label>Company<input name="website_hp" tabindex="-1" autocomplete="off"></label></div>
      <div><button class="btn" type="submit">Open email enquiry</button></div>
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


def apply_chrome_to_existing() -> None:
    nav_re = re.compile(r'<nav class="rk-nav" aria-label="Primary">.*?</nav>', re.S)
    x_host = "x" + ".com"
    handle = "site" + "handle"
    x_re = re.compile(r'\s*<a href="https://' + re.escape(x_host + "/" + handle) + r'"[^>]*>.*?</a>', re.S)
    theme_re = re.compile(r'<meta name="theme-color" content="[^"]*"(?: media="[^"]*")?>')
    same_re = re.compile(r',"https://' + re.escape(x_host + "/" + handle) + r'"')
    footer_site_re = re.compile(
        r'(<p class="brand-f" style="font-size:1rem">Site</p>\s*<ul>)(.*?)(</ul>)',
        re.S,
    )
    new_site_list = (
        '\n          <li><a href="/skills/">Skills</a></li>\n'
        '          <li><a href="/capabilities/">Capabilities</a></li>\n'
        '          <li><a href="/business-it/">Business IT</a></li>\n'
        '          <li><a href="/hire/">Hire</a></li>\n'
        '          <li><a href="/about/">About</a></li>\n'
        '          <li><a href="/resume/">Resume</a></li>\n'
        '          <li><a href="/contact/">Contact</a></li>\n        '
    )
    skip_dirs = {"skills", "capabilities", "business-it", "hire"}
    for p in ROOT.rglob("*.html"):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT)
        if rel.parts and rel.parts[0] in skip_dirs:
            continue
        text = p.read_text(encoding="utf-8")
        orig = text
        current = None
        if p == ROOT / "about" / "index.html":
            current = "about"
        elif p == ROOT / "contact" / "index.html":
            current = "contact"
        text = nav_re.sub(nav_html(current), text, count=1)
        text = x_re.sub("", text)
        text = same_re.sub("", text)
        text = text.replace("https://" + x_host + "/" + handle, "")
        text = text.replace("@" + handle, "")
        text = theme_re.sub(theme_tags(), text, count=1)
        text = footer_site_re.sub(r"\1" + new_site_list + r"\3", text, count=1)
        if text != orig:
            p.write_text(text, encoding="utf-8")
            print("chrome", rel)


def patch_home_and_resume() -> None:
    index = ROOT / "index.html"
    t = index.read_text(encoding="utf-8")
    t = t.replace(
        """    <div class="hero-cta">
      <a class="btn" href="#sites">Public work</a>
      <a class="btn btn-ghost" href="/resume/">Resume</a>
      <a class="btn btn-ghost" href="/contact/">Contact</a>
    </div>""",
        """    <div class="hero-cta">
      <a class="btn" href="/hire/">Hire me</a>
      <a class="btn btn-ghost" href="/skills/">Skills</a>
      <a class="btn btn-ghost" href="/business-it/">Business IT</a>
    </div>""",
    )
    t = t.replace(
        "<h3>Cloud and Cloudflare</h3><p>Deploying and operating services on Cloudflare, including Workers, Pages, DNS and email routing.</p>",
        "<h3>Systems and infrastructure</h3><p>Deploying and operating servers, DNS, certificates, mail and monitoring, with self-hosted Linux and Windows at the centre.</p>",
    )
    old_stack = '<ul class="skills"><li>HTML, CSS and JavaScript</li><li>Python</li><li>Cloudflare Workers and Pages</li><li>DNS and email routing</li><li>Windows and Linux applications</li><li>PayPal checkout</li><li>Automation and scripting</li><li>Interface and brand design</li></ul>'
    new_stack = (
        '<ul class="skills"><li>HTML, CSS and JavaScript</li><li>Python</li><li>Node.js</li>'
        "<li>SQLite</li><li>DNS and email routing</li><li>Windows and Linux</li>"
        "<li>Automation and scripting</li><li>Interface and brand design</li></ul>\n"
        '    <p class="eyebrow" style="margin-top:20px">Supporting infrastructure tools</p>\n'
        '    <ul class="skills support"><li>Cloudflare Workers, Pages and DNS</li><li>Azure</li><li>AWS</li><li>PayPal checkout</li></ul>'
    )
    t = t.replace(old_stack, new_stack)
    if 'id="engage"' not in t:
        engage = """
  <section class="section" id="engage">
    <p class="eyebrow">Work with me</p>
    <h2>How to hire</h2>
    <p class="sub">Fixed-scope software, small business IT in Australia, and infrastructure work. Availability is stated on the hire page so I do not take on more than I can handle.</p>
    <div class="blocks">
      <a class="cap-card" href="/skills/">
        <h3>Skills</h3>
        <p>Browse core engineering skills and individual cards, including supporting platforms.</p>
      </a>
      <a class="cap-card" href="/business-it/">
        <h3>Business IT</h3>
        <p>Email, domains, servers, backups, hardening and support for organisations in Australia.</p>
      </a>
      <a class="cap-card" href="/hire/">
        <h3>Hire</h3>
        <p>Send a structured enquiry with work type, budget band, timeline and brief.</p>
      </a>
    </div>
  </section>
"""
        t = t.replace('<hr class="gold-rule">\n', '<hr class="gold-rule">\n' + engage, 1)
    index.write_text(t, encoding="utf-8")
    print("patched home")

    resume = ROOT / "resume" / "index.html"
    r = resume.read_text(encoding="utf-8")
    r = r.replace(
        "<h3>Cloud and Cloudflare</h3><p>Deploying and operating services on Cloudflare, including Workers, Pages, DNS and email routing.</p>",
        "<h3>Systems and infrastructure</h3><p>Deploying and operating servers, DNS, certificates, mail and monitoring, with self-hosted Linux and Windows at the centre.</p>",
    )
    r = r.replace(old_stack, new_stack)
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
    build_sitemap(data)
    rebuild_search_index()
    legacy = FAV_DIR / ("x" + ".png")
    if legacy.exists():
        legacy.unlink()
        print("removed unused social favicon")
    print("done. groups", len(data["groups"]), "cards", len(data["_by_slug"]))


if __name__ == "__main__":
    main()
