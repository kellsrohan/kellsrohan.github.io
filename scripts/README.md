# Site generator

The public site is static HTML. Edit `data/skills.json` to add a skill group or a card (name, slug, summary, keywords, official favicon path, related slugs). Then run:

    python3 scripts/build-site.py

This writes `/skills/`, `/skills/<group>/`, `/skills/<group>/<card>/`, `/capabilities/`, `/business-it/`, `/hire/`, `sitemap.xml`, and `assets/search-index.json`, and refreshes nav and footer chrome on existing pages.

Place official cached favicons under `assets/favicons/` and point the card `favicon` field at that file. Do not invent third-party marks.
