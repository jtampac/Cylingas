# Cylingas Company L.L.C. — Corporate Website (v2)

A premium, production-ready industrial corporate website for **Cylingas** — EPC, fabrication,
storage tanks and pressure vessels, established Dubai 1974.

This is **Version 2.0**: an evolution of the existing site, not a restart. It keeps the
proven structure and rebuilds it into a modular framework with a new executive palette and a
**projects-first** homepage.

---

## What changed in v2

| Area | v1 | v2 |
|------|----|----|
| Palette | Dark navy + gold | **60% White · 25% Light Grey · 10% Charcoal · 5% Industrial Red** (gold removed) |
| Homepage focus | Company / services | **Projects are the hero** — large portfolio rows immediately below the hero |
| Hero type | Oversized | **Reduced, executive** — photo dominates |
| Facilities | Small section | Large-image **showcase** credibility band |
| Pages | 12 flat files | **8 focused pages** |
| Code | One monolithic generator | **Modular**: components + data + assets, assembled into `/public` |
| Mobile menu | Transparency issues | **Solid charcoal** full-screen panel, large touch targets, scroll-lock |

---

## Framework structure

```
cylingas-v2/
├── build.py              # generator: components + data → /public
├── components/           # reusable HTML partials
│   ├── head.html         #   <head> + JSON-LD     ({{TITLE}} {{DESC}} {{CANONICAL}})
│   ├── header.html       #   topbar + nav         ({{NAV_LINKS}})
│   ├── footer.html       #   charcoal footer
│   └── cta.html          #   contact CTA band
├── data/                 # content (no code)
│   ├── site.json         #   stats, capabilities, facilities, certs, timeline, offices, clients
│   └── projects.json     #   project portfolio (name / client / location / scope / image)
├── src/
│   ├── styles/styles.css # design system (single source of truth for tokens)
│   └── scripts/main.js   # interactions (nav, reveal, counters, filter)
└── public/               # ← GENERATED. THIS IS WHAT YOU DEPLOY.
    ├── index.html … contact.html   (8 pages)
    ├── sitemap.xml · robots.txt
    └── assets/{styles,scripts,images}
```

**Pages:** Home · About Us · Services · Projects · Facilities · QHSE · Careers · Contact

---

## Build

```bash
cd cylingas-v2
python3 build.py
```

Outputs the full static site to `/public`. No dependencies — standard library only.

To edit content, change the JSON in `/data` or the partials in `/components`, then rebuild.
To restyle, edit `src/styles/styles.css` (all colours are CSS variables at the top).

> Open `public/index.html` **from inside the `public` folder** so relative asset paths resolve.

---

## Design tokens (excerpt)

```
--red:#C8102E   --red-deep:#9E0C23     (primary brand — 5%)
--charcoal:#222A31                     (dark anchor — 10%)
--steel:#6E7B86                        (secondary accent)
--white / --gray-50 / --gray-100       (backgrounds — 85%)
```

Fonts: Archivo (display) · IBM Plex Sans (body) · IBM Plex Mono (labels).

---

## Pre-launch checklist

1. **Brand red** — confirm the exact hex from the official Cylingas logo / brand guide. v2 uses
   `#C8102E` (industrial red) as a close estimate; update `--red` in `styles.css` if it differs.
2. **Imagery** — project/facility images currently hot-link to `cylingas.ae`. For production,
   download licensed copies into `public/assets/images`, export as optimised **WebP/AVIF**, add
   `srcset`, and serve from a CDN.
3. **Project metadata** — verify client names, locations and scopes in `data/projects.json`.
4. **Contact form** — `#enquiry-form` is a front-end demo; connect it to a backend / email service.
5. **Certificates & vacancies** — add real certificate scans (QHSE) and live roles (Careers).

---

© Cylingas Company L.L.C. — EPC · Fabrication · Storage Tanks · Pressure Vessels.
