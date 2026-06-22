#!/usr/bin/env python3
"""
CYLINGAS — Static Site Generator v2
Assembles reusable components (/components) + content data (/data) + assets (/src)
into a deployable static site in /public.

Run:  python3 build.py
"""
import html, json, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COMP = ROOT / "components"
DATA = ROOT / "data"
SRC  = ROOT / "src"
PUB  = ROOT / "public"
CANONICAL_BASE = "https://cylingas.ae/"

# ----------------------------------------------------------------- load inputs
site = json.loads((DATA / "site.json").read_text(encoding="utf-8"))
pdata = json.loads((DATA / "projects.json").read_text(encoding="utf-8"))
HEAD = (COMP / "head.html").read_text(encoding="utf-8")
HEADER = (COMP / "header.html").read_text(encoding="utf-8")
FOOTER = (COMP / "footer.html").read_text(encoding="utf-8")
CTA = (COMP / "cta.html").read_text(encoding="utf-8")

IMG = site["images"]
PROJECTS = pdata["projects"]
CATS = pdata["categories"]

NAV = [
    ("index.html", "Home"),
    ("about.html", "About Us"),
    ("services.html", "Services"),
    ("projects.html", "Projects"),
    ("facilities.html", "Facilities"),
    ("qhse.html", "QHSE"),
    ("careers.html", "Careers"),
    ("contact.html", "Contact"),
]

# ----------------------------------------------------------------- icon library
_ICONS = {
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/>',
    "tank": '<rect x="5" y="8" width="14" height="12" rx="1"/><path d="M5 8c0-2 3.1-3.5 7-3.5S19 6 19 8" /><path d="M5 13h14M5 16.5h14"/>',
    "vessel": '<rect x="8" y="3" width="8" height="18" rx="4"/><path d="M8 8h8M8 16h8"/>',
    "ruler": '<rect x="3" y="8" width="18" height="8" rx="1"/><path d="M7 8v3M11 8v4M15 8v3M19 8v4"/>',
    "weld": '<path d="M4 19l7-7M11 12l3-3 4 4-3 3zM14 9l3-3"/><circle cx="18" cy="6" r="1.4"/>',
    "gear": '<circle cx="12" cy="12" r="3.2"/><path d="M12 4v2.5M12 17.5V20M4 12h2.5M17.5 12H20M6 6l1.8 1.8M16.2 16.2L18 18M18 6l-1.8 1.8M7.8 16.2L6 18"/>',
    "oil": '<path d="M12 3s6 6.5 6 11a6 6 0 11-12 0c0-4.5 6-11 6-11z"/>',
    "fuel": '<rect x="5" y="4" width="9" height="16" rx="1"/><path d="M14 9h3a2 2 0 012 2v5a1.5 1.5 0 01-3 0v-3"/>',
    "pipe": '<path d="M3 9h8v6H3zM11 12h4a3 3 0 003-3V6"/><path d="M3 9v6M21 6h-3"/>',
    "build": '<path d="M3 21V8l7-4 7 4v13"/><path d="M3 21h18M10 21v-5h4v5"/>',
    "globe": '<circle cx="12" cy="12" r="8.5"/><path d="M3.5 12h17M12 3.5c2.5 2.4 2.5 14.6 0 17M12 3.5c-2.5 2.4-2.5 14.6 0 17"/>',
    "shield": '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    "doc": '<path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4M10 13h6M10 16h6"/>',
    "factory": '<path d="M4 21V9l6 4V9l6 4V6l4 2v13z"/><path d="M4 21h18"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M3.5 6.5L12 13l8.5-6.5"/>',
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 005 5L15 13l5 2v4a2 2 0 01-2 2A16 16 0 013 6a2 2 0 012-2z"/>',
    "pin": '<path d="M12 21s7-6.2 7-11a7 7 0 10-14 0c0 4.8 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "fax": '<path d="M7 8V4h10v4M7 8h10a3 3 0 013 3v6h-3v-4H7v4H4v-6a3 3 0 013-3z"/>',
    "check": '<path d="M5 12l5 5L20 6" stroke-linecap="round" stroke-linejoin="round"/>',
}
def icon(name, cls=""):
    body = _ICONS.get(name, "")
    c = f' class="{cls}"' if cls else ""
    return f'<svg{c} viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true">{body}</svg>'

ARW = icon("arrow")

# ----------------------------------------------------------------- shell helpers
def nav_links(active):
    out = ""
    for href, label in NAV:
        cur = ' aria-current="page"' if href == active else ""
        out += f'<a href="{href}"{cur}>{label}</a>'
    return out

def head(title, desc, page):
    return (HEAD
            .replace("{{TITLE}}", title)
            .replace("{{DESC}}", desc)
            .replace("{{CANONICAL}}", CANONICAL_BASE + ("" if page == "index.html" else page)))

def header(active):
    return HEADER.replace("{{NAV_LINKS}}", nav_links(active))

def shell(page, title, desc, body):
    return head(title, desc, page) + header(page) + body + CTA + FOOTER

def page_hero(eyebrow, h1, sub, img, crumb):
    return f"""<section class="pagehero">
  <div class="pagehero__media"><img src="{img}" alt="" loading="eager"></div>
  <div class="container">
    <p class="breadcrumb reveal"><a href="index.html">Home</a> &nbsp;/&nbsp; <span>{crumb}</span></p>
    <span class="eyebrow reveal">{eyebrow}</span>
    <h1 class="reveal" data-delay="1" style="margin-top:1rem">{h1}</h1>
    <p class="lead reveal" data-delay="2">{sub}</p>
  </div>
</section>"""

# ----------------------------------------------------------------- components
def pfeature(p, idx, flip):
    alt = html.escape(p["name"].replace("&mdash;", "-").replace("&amp;", "&"))
    flipcls = " pfeature--flip" if flip else ""
    return f"""<article class="pfeature{flipcls} reveal">
  <div class="pfeature__media"><span class="pfeature__tag">{p['category']}</span><img src="{p['image']}" alt="{alt}" loading="lazy"></div>
  <div class="pfeature__body">
    <span class="pfeature__no">PROJECT {idx:02d}</span>
    <h3>{p['name']}</h3>
    <dl class="pfeature__meta">
      <div><dt>Client</dt><dd>{p['client']}</dd></div>
      <div><dt>Location</dt><dd>{p['location']}</dd></div>
      <div><dt>Sector</dt><dd>{p['sector']}</dd></div>
      <div><dt>Category</dt><dd>{p['category']}</dd></div>
    </dl>
    <p class="pfeature__scope">{p['scope']}</p>
    <a class="pfeature__link" href="projects.html">View Portfolio {ARW}</a>
  </div>
</article>"""

def project_card(p):
    alt = html.escape(p["name"].replace("&mdash;", "-").replace("&amp;", "&"))
    return f"""<article class="project reveal" data-category="{p['category']}">
  <div class="project__media"><span class="project__cat">{p['category']}</span><img src="{p['image']}" alt="{alt}" loading="lazy"></div>
  <div class="project__body">
    <h3>{p['name']}</h3>
    <dl class="project__meta">
      <div><dt>Client</dt><dd>{p['client']}</dd></div>
      <div><dt>Location</dt><dd>{p['location']}</dd></div>
      <div><dt>Scope</dt><dd>{p['scope']}</dd></div>
      <div><dt>Sector</dt><dd>{p['sector']}</dd></div>
    </dl>
  </div>
</article>"""

def cap_card(c, i):
    return f"""<a class="cap-card reveal" data-delay="{i%3}" href="services.html">
  <span class="cap-card__icon">{icon(c['icon'])}</span>
  <h3>{c['title']}</h3>
  <p>{c['desc']}</p>
  <span class="cap-card__link">Explore {ARW}</span>
</a>"""

def stat_item(s, i):
    return f"""<div class="stat reveal" data-delay="{i}"><div class="stat__num"><span data-count="{s['num']}">{s['num']}</span><span class="unit">{s['unit']}</span></div><div class="stat__label">{s['label']}</div></div>"""

def statbar():
    return f"""<section class="statbar"><div class="container" style="padding-block:0"><div class="statbar__grid">{''.join(stat_item(s,i) for i,s in enumerate(site['stats']))}</div></div></section>"""

def cert_card(c, i):
    return f"""<div class="cert reveal" data-delay="{i%3}"><div class="cert__stamp">{c['stamp']}</div><h4>{c['title']}</h4><p>{c['desc']}</p></div>"""

def clients_strip():
    items = "".join(f'<div class="logos__item reveal" data-delay="{i%4}"><img src="{u}" alt="Client logo" loading="lazy"></div>' for i, u in enumerate(site["clients"]))
    return f"""<section class="section--tight bg-gray">
  <div class="container">
    <div class="shead reveal" style="text-align:center;margin-inline:auto"><span class="eyebrow center">Clients &amp; Partners</span><h3 style="margin-top:1rem">Trusted by the region's principal operators &amp; EPC contractors</h3></div>
    <div class="logos">{items}</div>
  </div>
</section>"""

# ================================================================ HOME
def home():
    featured = sorted([p for p in PROJECTS if p.get("featured")], key=lambda x: x["featured"])
    feat_rows = "".join(pfeature(p, i + 1, flip=(i % 2 == 1)) for i, p in enumerate(featured))
    caps = "".join(cap_card(c, i) for i, c in enumerate(site["capabilities"]))
    inds = "".join(f'<div class="industry reveal" data-delay="{i%3}"><span class="industry__icon">{icon(d["icon"])}</span><div><h4>{d["title"]}</h4><p>{d["desc"]}</p></div></div>' for i, d in enumerate(site["industries"]))
    tl = "".join(f'<div class="tl-item reveal"><div class="tl-item__year">{t["year"]}</div><p class="tl-item__text">{t["text"]}</p></div>' for t in site["timeline"][:1] + [t for t in site["timeline"] if t["year"] in ("2018", "2010", "1976", "1974")])
    certs = "".join(cert_card(c, i) for i, c in enumerate(site["certs"]))

    body = f"""<section class="hero">
  <div class="hero__media"><img src="{IMG['hero']}" alt="Cylingas bulk liquid storage tank farm"></div>
  <div class="container hero__inner">
    <span class="eyebrow hero__eyebrow reveal">EPC &middot; Fabrication &middot; Storage Tanks &middot; Pressure Vessels</span>
    <h1 class="reveal" data-delay="1">Building Industrial Infrastructure <em>Since 1974</em></h1>
    <p class="hero__sub reveal" data-delay="2">Storage tanks, pressure vessels, EPC projects and industrial fabrication solutions across the UAE and GCC &mdash; engineered and built to international code by a prequalified ADNOC contractor.</p>
    <div class="hero__actions reveal" data-delay="3">
      <a class="btn btn--red" href="projects.html">View Our Projects {ARW}</a>
      <a class="btn btn--ghost" href="facilities.html">Our Facilities</a>
    </div>
  </div>
  <div class="hero__badge" aria-hidden="true">ASME U &middot; U2<br>NBBI R<br>ISO 9001 / 14001 / 45001</div>
</section>

{statbar()}

<section class="section bg-gray">
  <div class="container">
    <div class="shead shead--split">
      <div class="shead__text reveal"><span class="eyebrow">Featured Projects</span><h2 style="margin-top:1rem">Major industrial assets, delivered across the UAE &amp; GCC.</h2></div>
      <a class="btn btn--ghost reveal" data-delay="1" href="projects.html">Full Portfolio {ARW}</a>
    </div>
    {feat_rows}
  </div>
</section>

<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Facilities &amp; Workshop</span><h2 style="margin-top:1rem">A 300,000 sq ft heavy-fabrication facility.</h2><p class="lead" style="margin-top:1rem">In-house plate rolling to 70 mm, CNC cutting and drilling, certified welding and surface protection &mdash; the capacity to fabricate and erect storage tanks, spheres and heavy-wall pressure vessels under one roof.</p></div>
    <div class="showcase">
      <div class="showcase__item showcase__item--lg reveal"><img src="{IMG['fabrication']}" alt="Cylingas fabrication workshop"><div class="showcase__cap"><span>Shop Fabrication</span><h4>Heavy plate &amp; vessel fabrication</h4></div></div>
      <div class="showcase__item showcase__item--sm reveal" data-delay="1"><img src="{IMG['spheres']}" alt="Storage spheres under construction"><div class="showcase__cap"><span>Storage Tanks</span><h4>Spheres &amp; API tanks</h4></div></div>
      <div class="showcase__item showcase__item--third reveal"><img src="{IMG['vessel']}" alt="Pressure vessel fabrication"><div class="showcase__cap"><span>Pressure Vessels</span><h4>Heavy-wall vessels</h4></div></div>
      <div class="showcase__item showcase__item--third reveal" data-delay="1"><img src="{IMG['epc']}" alt="EPC site construction"><div class="showcase__cap"><span>EPC Projects</span><h4>Site construction</h4></div></div>
      <div class="showcase__item showcase__item--third reveal" data-delay="2"><img src="{IMG['om']}" alt="Operations and maintenance works"><div class="showcase__cap"><span>O&amp;M</span><h4>Shutdowns &amp; integrity</h4></div></div>
    </div>
    <div style="margin-top:2.2rem"><a class="btn btn--dark" href="facilities.html">Explore Facilities &amp; Equipment {ARW}</a></div>
  </div>
</section>

<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Core Capabilities</span><h2 style="margin-top:1rem">Six integrated capabilities, one accountable contractor.</h2></div>
    <div class="cards cards--3">{caps}</div>
  </div>
</section>

<section class="section bg-white">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">Company Legacy</span>
        <h2 style="margin:1rem 0 1.4rem">Five decades of industrial delivery.</h2>
        <div class="prose">
          <p>Cylingas was established on 28 April 1974 by decree of the late ruler of Dubai, His Highness Sheikh Rashid Bin Saeed Al Maktoum &mdash; the first GCC company in Dubai to manufacture gas cylinders and pressure vessels.</p>
          <p>From that foundation the company grew into a full EPC and fabrication contractor, today delivering complete storage facilities, process equipment and infrastructure for the region's most demanding operators.</p>
        </div>
        <a class="btn btn--ghost" style="margin-top:1.8rem" href="about.html">Our Full History {ARW}</a>
      </div>
      <div class="reveal" data-delay="1"><div class="timeline">{tl}</div></div>
    </div>
  </div>
</section>

<section class="section bg-charcoal">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Industries Served</span><h2 style="margin-top:1rem">Engineering across the energy value chain.</h2></div>
    <div class="industries">{inds}</div>
  </div>
</section>

<section class="section bg-gray">
  <div class="container">
    <div class="shead shead--split">
      <div class="shead__text reveal"><span class="eyebrow">Certifications &amp; QHSE</span><h2 style="margin-top:1rem">Internationally coded. Independently certified.</h2></div>
      <a class="btn btn--ghost reveal" data-delay="1" href="qhse.html">QHSE &amp; Certifications {ARW}</a>
    </div>
    <div class="cert-grid">{certs}</div>
  </div>
</section>

{clients_strip()}"""
    return shell("index.html",
                 "Cylingas | EPC, Storage Tanks & Pressure Vessels — Since 1974",
                 "Cylingas builds storage tanks, pressure vessels, EPC projects and industrial fabrication across the UAE and GCC. A prequalified ADNOC contractor, ASME U/U2 and NBBI R stamp holder, established 1974.",
                 body)

# ================================================================ ABOUT
def about():
    tl = "".join(f'<div class="tl-item reveal"><div class="tl-item__year">{t["year"]}</div><p class="tl-item__text">{t["text"]}</p></div>' for t in site["timeline"])
    vmo = [
        ("Vision", "To be the preferred contractor to the Oil, Gas and Utility industries &mdash; a creator of value and sustainable growth, recognised for operational excellence, client service and the development of our people."),
        ("Mission", "To meet the expectations of our stakeholders through operational excellence in quality, delivery and customer focus, while fostering a genuinely EHSQ-conscious culture and retaining talent."),
        ("Objectives", "A human asset driven by continuous improvement &mdash; safe, ethical, dependable, innovative and cost-conscious, with active participation in CSR initiatives."),
    ]
    vmo_html = "".join(f'<div class="value reveal" data-delay="{i}"><div class="value__num">0{i+1}</div><h4>{v[0]}</h4><p>{v[1]}</p></div>' for i, v in enumerate(vmo))
    body = page_hero("About Cylingas", "One of the UAE's longest-established EPC &amp; fabrication specialists.",
                     "More than five decades engineering, fabricating and constructing industrial assets for the Oil &amp; Gas, energy and infrastructure sectors &mdash; from a single Dubai workshop to a regional contractor.",
                     IMG["tankfarm"], "About Us") + f"""
<section class="section bg-white">
  <div class="container">
    <div class="split">
      <div class="reveal">
        <span class="eyebrow">Company Profile</span>
        <h2 style="margin:1rem 0 1.4rem">Engineering capability, proven at industrial scale.</h2>
        <div class="prose">
          <p>Cylingas is an EPC and fabrication company operating for more than 50 years, with an approximately 300,000 sq ft facility in Dubai, a skilled workforce and complete infrastructure &mdash; including the in-house capability to roll plate up to 70 mm thick.</p>
          <p>We deliver the design, engineering and fabrication of Oil &amp; Gas storage tanks, spheres, API 650 and 620 vertical storage tanks, pressure vessels, process equipment, pipeline spools and steel products.</p>
          <p>Association with renowned international brands, strict adherence to HSE requirements, and a wide customer base stand as testimony to our commitment to quality across five decades.</p>
        </div>
        <ul class="checklist">
          <li>Prequalified ADNOC EPC / Fabrication contractor</li>
          <li>ASME U, U2 &amp; NBBI R stamp holder</li>
          <li>ISO 9001 / 14001 / 45001 certified</li>
          <li>UAE, GCC &amp; international delivery</li>
        </ul>
      </div>
      <div class="reveal" data-delay="1"><div class="media-frame"><img src="{IMG['epc']}" alt="Cylingas EPC works"><span class="media-frame__tag">300,000 SQ FT &middot; DUBAI</span></div></div>
    </div>
  </div>
</section>

{statbar()}

<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Our History</span><h2 style="margin-top:1rem">From 1974 to today.</h2></div>
    <div class="timeline">{tl}</div>
  </div>
</section>

<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Vision, Mission &amp; Objectives</span><h2 style="margin-top:1rem">What guides our work.</h2></div>
    <div class="value-grid" style="grid-template-columns:repeat(3,1fr)">{vmo_html}</div>
  </div>
</section>"""
    return shell("about.html", "About Cylingas | EPC & Fabrication Since 1974",
                 "Established in Dubai in 1974, Cylingas is one of the UAE's longest-established EPC and fabrication specialists for storage tanks, pressure vessels and process equipment.",
                 body)

# ================================================================ SERVICES
def services():
    caps = "".join(cap_card(c, i) for i, c in enumerate(site["capabilities"]))
    codes = "".join(f"<span>{c}</span>" for c in site["codes"])
    software = "".join(f"<span>{s}</span>" for s in site["software"])
    detail = [
        ("EPC Projects", IMG["epc"], "Turnkey engineering, procurement and construction.",
         ["Front-end and detailed engineering", "Procurement &amp; expediting", "Site construction &amp; erection", "Pre-commissioning &amp; commissioning"]),
        ("Shop Fabrication", IMG["fabrication"], "Heavy fabrication in a 300,000 sq ft Dubai works.",
         ["Storage tanks, spheres &amp; bullets", "ASME pressure vessels &amp; columns", "Pipe spools &amp; structural steel", "Plate rolling to 70 mm"]),
        ("Engineering &amp; Design", IMG["engineering1"], "In-house multidiscipline design.",
         ["Mechanical, piping &amp; structural", "Stress &amp; FEA analysis", "Civil &amp; E&amp;I design", "3D modelling &amp; drafting"]),
        ("Operations &amp; Maintenance", IMG["om"], "Shutdown, refurbishment &amp; integrity.",
         ["Planned shutdowns &amp; turnarounds", "Tank &amp; vessel refurbishment", "Integrity &amp; repair (NBBI R)", "Brownfield tie-ins"]),
    ]
    det_html = ""
    for i, (title, img, tag, items) in enumerate(detail):
        flip = i % 2 == 1
        media = f'<div class="reveal"><div class="media-frame"><img src="{img}" alt="{html.escape(title.replace("&amp;","&"))}"><span class="media-frame__tag">{tag}</span></div></div>'
        text = f'<div class="reveal" data-delay="1"><span class="eyebrow">Capability 0{i+1}</span><h2 style="margin:1rem 0 1.2rem">{title}</h2><ul class="checklist" style="grid-template-columns:1fr">{"".join(f"<li>{x}</li>" for x in items)}</ul></div>'
        cols = (text + media) if flip else (media + text)
        bg = "bg-white" if i % 2 == 0 else "bg-gray"
        det_html += f'<section class="section {bg}"><div class="container"><div class="split">{cols}</div></div></section>'

    body = page_hero("Capabilities &amp; Services", "Engineering, fabrication and EPC under one accountable contractor.",
                     "From storage tanks and pressure vessels to complete EPC delivery, Cylingas provides integrated industrial capability across the asset lifecycle.",
                     IMG["fabrication"], "Services") + f"""
<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Core Capabilities</span><h2 style="margin-top:1rem">Six integrated capabilities.</h2></div>
    <div class="cards cards--3">{caps}</div>
  </div>
</section>
{det_html}
<section class="section bg-charcoal">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Codes &amp; Standards</span><h2 style="margin-top:1rem">Engineered to international standards.</h2></div>
    <div class="taglist reveal">{codes}</div>
    <div class="shead reveal" style="margin-top:2.6rem"><span class="eyebrow">Engineering Software</span><h3 style="margin-top:1rem">Analysis &amp; design tools.</h3></div>
    <div class="taglist reveal">{software}</div>
  </div>
</section>"""
    return shell("services.html", "Services | EPC, Fabrication & Engineering — Cylingas",
                 "Cylingas delivers storage tanks, pressure vessels, EPC projects, engineering, fabrication and maintenance to ASME, API and international codes.",
                 body)

# ================================================================ PROJECTS
def projects():
    filt = '<button class="active" data-filter="all">All Projects</button>' + "".join(f'<button data-filter="{c}">{c}</button>' for c in CATS)
    cards = "".join(project_card(p) for p in PROJECTS)
    body = page_hero("Project Portfolio", "A portfolio of landmark industrial assets.",
                     "Storage terminals, pressure vessels, process equipment and infrastructure delivered for ADNOC, ENOC, DEWA, Vopak, Dragon Oil, QAFCO and other principal operators.",
                     IMG["spheres"], "Projects") + f"""
<section class="section bg-gray">
  <div class="container">
    <div class="proj-filter reveal">{filt}</div>
    <div class="projects-grid">{cards}</div>
  </div>
</section>"""
    return shell("projects.html", "Projects | Storage Tanks, Vessels & EPC — Cylingas",
                 "Explore Cylingas project experience: storage tanks, pressure vessels, process equipment and EPC works across the UAE, GCC and internationally.",
                 body)

# ================================================================ FACILITIES
def facilities():
    specs = "".join(f'<div class="spec reveal" data-delay="{i}"><div class="spec__num"><span data-count="{s["num"]}">{s["num"]}</span><span class="unit">{s["unit"]}</span></div><div class="spec__label">{s["label"]}</div><div class="spec__desc">{s["desc"]}</div></div>' for i, s in enumerate(site["facility_specs"]))
    equip = "".join(f'<div class="cap reveal"><span class="cap__name">{n}</span><span class="cap__val">{v}</span></div>' for n, v in site["equipment"])
    body = page_hero("Facilities &amp; Equipment", "A 300,000 sq ft heavy-fabrication facility in Dubai.",
                     "Covered fabrication bays, heavy plate rolling, CNC cutting and drilling, certified welding and surface protection &mdash; the capacity to engineer, fabricate and erect at industrial scale.",
                     IMG["fabrication"], "Facilities") + f"""
<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Facility at a Glance</span><h2 style="margin-top:1rem">Capacity that de-risks delivery.</h2></div>
    <div class="spec-panel">{specs}</div>
  </div>
</section>

<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Workshop &amp; Yards</span><h2 style="margin-top:1rem">Inside the works.</h2></div>
    <div class="showcase">
      <div class="showcase__item showcase__item--half reveal"><img src="{IMG['fabrication']}" alt="Fabrication workshop"><div class="showcase__cap"><span>Fabrication Shop</span><h4>Plate &amp; vessel fabrication</h4></div></div>
      <div class="showcase__item showcase__item--half reveal" data-delay="1"><img src="{IMG['spheres']}" alt="Storage spheres"><div class="showcase__cap"><span>Storage Tanks</span><h4>Spheres &amp; API tanks</h4></div></div>
      <div class="showcase__item showcase__item--third reveal"><img src="{IMG['vessel']}" alt="Pressure vessel"><div class="showcase__cap"><span>Pressure Vessels</span><h4>Heavy-wall fabrication</h4></div></div>
      <div class="showcase__item showcase__item--third reveal" data-delay="1"><img src="{IMG['engineering2']}" alt="Engineering"><div class="showcase__cap"><span>Engineering</span><h4>Design &amp; analysis</h4></div></div>
      <div class="showcase__item showcase__item--third reveal" data-delay="2"><img src="{IMG['epc']}" alt="EPC site"><div class="showcase__cap"><span>EPC</span><h4>Site construction</h4></div></div>
    </div>
  </div>
</section>

<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Plant &amp; Equipment</span><h2 style="margin-top:1rem">Fabrication &amp; inspection capability.</h2></div>
    <div class="cap-list">{equip}</div>
  </div>
</section>"""
    return shell("facilities.html", "Facilities & Equipment | 300,000 sq ft Works — Cylingas",
                 "Cylingas operates a 300,000 sq ft Dubai fabrication facility with plate rolling to 70 mm, CNC cutting and drilling, certified welding and NDT.",
                 body)

# ================================================================ QHSE
def qhse():
    certs = "".join(cert_card(c, i) for i, c in enumerate(site["certs"]))
    pillars = [
        ("shield", "Safety First", "An ISO 45001 occupational health &amp; safety system, with rigorous controls for brownfield and live-plant work."),
        ("check", "Quality Assured", "An ISO 9001 quality system spanning engineering, procurement, fabrication and construction, with full traceability."),
        ("globe", "Environmental Care", "An ISO 14001 environmental management system minimising impact across our operations."),
    ]
    pill_html = "".join(f'<div class="feature reveal" data-delay="{i}"><span class="feature__icon">{icon(p[0])}</span><h4>{p[1]}</h4><p>{p[2]}</p></div>' for i, p in enumerate(pillars))
    body = page_hero("Certifications &amp; QHSE", "Internationally coded. Independently certified.",
                     "Cylingas holds the ASME 'U' and 'U2' stamps and the NBBI 'R' stamp, with quality, environmental and safety systems certified to ISO 9001, 14001 and 45001.",
                     IMG["vessel"], "QHSE") + f"""
<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Accreditations</span><h2 style="margin-top:1rem">Authorisations &amp; certifications.</h2></div>
    <div class="cert-grid">{certs}</div>
  </div>
</section>

<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">QHSE Commitment</span><h2 style="margin-top:1rem">A culture built on safe, quality delivery.</h2></div>
    <div class="features">{pill_html}</div>
  </div>
</section>"""
    return shell("qhse.html", "Certifications & QHSE | ASME, NBBI & ISO — Cylingas",
                 "Cylingas holds ASME U and U2 stamps and the NBBI R stamp, certified to ISO 9001, ISO 14001 and ISO 45001.",
                 body)

# ================================================================ CAREERS
def careers():
    values = [
        ("Engineering Excellence", "Work on landmark storage, vessel and EPC projects for the region's leading operators."),
        ("Safety &amp; Integrity", "An uncompromising QHSE culture where everyone goes home safe."),
        ("Growth &amp; Development", "Structured development for engineers, fabricators and project professionals."),
        ("A 50-Year Legacy", "Join a company that has built critical infrastructure across the UAE and GCC since 1974."),
    ]
    val_html = "".join(f'<div class="value reveal" data-delay="{i%2}"><div class="value__num">0{i+1}</div><h4>{v[0]}</h4><p>{v[1]}</p></div>' for i, v in enumerate(values))
    roles = [
        ("Mechanical / Static Equipment Engineer", "Dubai", "Engineering", "Full-time"),
        ("Senior QA/QC Inspector (Welding)", "Dubai", "QHSE", "Full-time"),
        ("Project Engineer &mdash; EPC", "Abu Dhabi", "Projects", "Full-time"),
        ("Piping Designer (CAD Worx)", "Dubai", "Engineering", "Full-time"),
    ]
    job_html = "".join(f'<div class="job reveal"><div class="job__info"><h4>{r[0]}</h4><div class="job__tags"><span>{r[2]}</span> &middot; {r[1]} &middot; {r[3]}</div></div><a class="btn btn--ghost" href="contact.html">Apply {ARW}</a></div>' for r in roles)
    body = page_hero("Careers", "Build critical infrastructure with a 50-year industrial leader.",
                     "We are always interested in talented engineers, fabricators, inspectors and project professionals who share our commitment to safe, quality delivery.",
                     IMG["engineering1"], "Careers") + f"""
<section class="section bg-white">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Why Cylingas</span><h2 style="margin-top:1rem">A place to do your best work.</h2></div>
    <div class="value-grid">{val_html}</div>
  </div>
</section>

<section class="section bg-gray">
  <div class="container">
    <div class="shead reveal"><span class="eyebrow">Open Positions</span><h2 style="margin-top:1rem">Current opportunities.</h2></div>
    {job_html}
    <p style="margin-top:1.6rem;color:var(--steel);font-size:.9rem">Sample roles shown &mdash; replace with live vacancies. To apply, send your CV to <a href="mailto:info@cylingas.ae" style="color:var(--red)">info@cylingas.ae</a>.</p>
  </div>
</section>"""
    return shell("careers.html", "Careers | Engineering & Fabrication Jobs — Cylingas",
                 "Build your career with Cylingas — engineering, fabrication, QHSE and project roles with a 50-year UAE industrial contractor.",
                 body)

# ================================================================ CONTACT
def contact():
    offices = ""
    for o in site["offices"]:
        lines = "<br>".join(o["lines"])
        offices += f"""<div class="office reveal">
  <h4>{o['name']}</h4>
  <div class="office__row">{icon('pin')}<span>{lines}</span></div>
  <div class="office__row">{icon('phone')}<span><a href="tel:{o['tel'].replace(' ','')}">{o['tel']}</a></span></div>
  <div class="office__row">{icon('fax')}<span>{o['fax']}</span></div>
</div>"""
    body = page_hero("Contact Cylingas", "Let's discuss your project.",
                     "Speak with our engineering and business development team about storage tanks, pressure vessels, EPC scopes and fabrication packages.",
                     IMG["epc"], "Contact") + f"""
<section class="section bg-white">
  <div class="container">
    <div class="contact-grid">
      <div class="reveal">
        <span class="eyebrow">Enquiry</span>
        <h2 style="margin:1rem 0 1.4rem">Request a proposal.</h2>
        <form id="enquiry-form" novalidate>
          <div class="field"><label for="name">Name</label><input id="name" name="name" type="text" required></div>
          <div class="field"><label for="company">Company</label><input id="company" name="company" type="text"></div>
          <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" required></div>
          <div class="field"><label for="scope">Scope of Interest</label><select id="scope" name="scope"><option>Storage Tanks</option><option>Pressure Vessels</option><option>EPC Project</option><option>Shop Fabrication</option><option>Engineering &amp; Design</option><option>Operations &amp; Maintenance</option></select></div>
          <div class="field"><label for="message">Message</label><textarea id="message" name="message"></textarea></div>
          <button class="btn btn--red" type="submit">Send Enquiry {ARW}</button>
          <p class="form-note" role="status" style="display:none;margin-top:1.1rem;color:var(--red);font-size:.9rem"></p>
        </form>
      </div>
      <div class="reveal" data-delay="1">
        <span class="eyebrow">Our Offices</span>
        <h2 style="margin:1rem 0 1.4rem">Across the Emirates.</h2>
        {offices}
        <div class="office reveal"><h4>General Enquiries</h4>
          <div class="office__row">{icon('mail')}<span><a href="mailto:info@cylingas.ae">info@cylingas.ae</a></span></div>
        </div>
      </div>
    </div>
  </div>
</section>"""
    return shell("contact.html", "Contact | Request a Proposal — Cylingas",
                 "Contact Cylingas in Dubai, Abu Dhabi and Fujairah to discuss storage tanks, pressure vessels, EPC and fabrication scopes.",
                 body)

# ----------------------------------------------------------------- write
PAGES = {
    "index.html": home, "about.html": about, "services.html": services,
    "projects.html": projects, "facilities.html": facilities, "qhse.html": qhse,
    "careers.html": careers, "contact.html": contact,
}

def build():
    PUB.mkdir(exist_ok=True)
    (PUB / "assets").mkdir(exist_ok=True)
    # copy assets
    for sub in ("styles", "scripts"):
        dst = PUB / "assets" / sub
        dst.mkdir(parents=True, exist_ok=True)
        for f in (SRC / sub).glob("*"):
            shutil.copy2(f, dst / f.name)
    (PUB / "assets" / "images").mkdir(parents=True, exist_ok=True)
    # pages
    for fname, fn in PAGES.items():
        (PUB / fname).write_text(fn(), encoding="utf-8")
        print("wrote", fname)
    # sitemap + robots
    urls = "".join(f"  <url><loc>{CANONICAL_BASE}{'' if p=='index.html' else p}</loc><priority>{'1.0' if p=='index.html' else '0.8'}</priority></url>\n" for p in PAGES)
    (PUB / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n', encoding="utf-8")
    (PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {CANONICAL_BASE}sitemap.xml\n", encoding="utf-8")
    print("DONE — site generated in /public")

if __name__ == "__main__":
    build()
