#!/usr/bin/env python3
"""
Generate the /news/ pages from the NEWS array in ../index.html.

Why this exists
---------------
The homepage news section is rendered client-side from a `NEWS` array, so until
now the three articles had no URLs of their own: nothing for search engines to
index, and nothing anyone could share except "#news" on the homepage. This
script turns that same array into real HTML pages -- one per article, plus an
index -- so each story is a crawlable, linkable, shareable page.

The array in index.html stays the single source of truth. Edit an article there,
re-run this script, and the pages follow. Do NOT hand-edit the generated
.html files in this directory; your changes will be overwritten.

Usage (from the repo root or anywhere):
    python3 site/news/_build-news.py

Requires node, which is only used to evaluate the JS array literal into JSON.
Everything the script writes lands in this directory.
"""

import html
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
INDEX = os.path.join(SITE, "index.html")
ORIGIN = "https://www.hestora.net"

# Per-article SEO copy. Kept here rather than derived from the excerpt because a
# meta description has a different job: ~155 characters, written for someone
# scanning a results page, leading with the concrete claim. Keyed by title so
# reordering the NEWS array cannot mis-assign them.
META = {
    "Engineering the future of home heating": {
        "slug": "engineering-the-future-of-home-heating",
        "description": (
            "Inside the Hestora thermal energy store prototypes: precision engineering, "
            "rigorous testing, and the UK home trials that prove a direct swap from gas works."
        ),
        "keywords": "thermal energy store, home heating prototype, gas boiler replacement, home trials",
        "published": "2026-06-01",
    },
    "Engineering a direct swap": {
        "slug": "engineering-a-direct-swap",
        "description": (
            "How Hestora matches a gas boiler's output with high-temperature, high-pressure "
            "design -- a full day of heat, stored overnight, in a boiler-sized footprint."
        ),
        "keywords": "electric heating, boiler replacement, off-peak electricity, no radiator upgrade",
        "published": "2026-06-01",
    },
    "A data-driven approach to Net Zero": {
        "slug": "a-data-driven-approach-to-net-zero",
        "description": (
            "Domestic heating causes 21% of UK emissions. Why 28 million existing homes need "
            "a heating solution that works without a deep retrofit."
        ),
        "keywords": "UK domestic heating emissions, Net Zero 2050, housing stock retrofit, demand shifting",
        "published": "2026-05-01",
    },
}


def load_news():
    """Evaluate the NEWS array literal out of index.html and return it as data."""
    src = open(INDEX, encoding="utf-8").read()
    start = src.find("const NEWS = [")
    if start == -1:
        sys.exit("Could not find `const NEWS = [` in index.html")
    end = src.find("\n];\n", start)
    if end == -1:
        sys.exit("Could not find the end of the NEWS array in index.html")
    literal = src[start : end + 3]

    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
        fh.write(literal + "\nconsole.log(JSON.stringify(NEWS));")
        tmp = fh.name
    try:
        out = subprocess.run(
            ["node", tmp], capture_output=True, text=True, check=True
        ).stdout
    except FileNotFoundError:
        sys.exit("node is required to parse the NEWS array (it evaluates the JS literal)")
    except subprocess.CalledProcessError as exc:
        sys.exit(f"node failed to evaluate the NEWS array:\n{exc.stderr}")
    finally:
        os.unlink(tmp)
    return json.loads(out)


def strip_tags(s):
    return re.sub(r"<[^>]+>", "", s)


# ── Shared chrome ─────────────────────────────────────────────────────────────
# Deliberately modelled on resources.html rather than index.html: an article
# wants a narrow measure and a fast, static page, not the homepage's full
# navigation and 900 KB of inlined assets.

HEAD = """<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{canonical}">
{extra_meta}
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='7' fill='%231B3A2F'/%3E%3Crect x='8' y='7' width='16' height='3.4' rx='1.7' fill='%23D74732'/%3E%3Crect x='8' y='12.5' width='16' height='3.4' rx='1.7' fill='%23F59435'/%3E%3Crect x='8' y='18' width='16' height='3.4' rx='1.7' fill='%233F8D86'/%3E%3Crect x='8' y='23.5' width='16' height='3.4' rx='1.7' fill='%231491A6'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=Inter:wght@400;500&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--red:#D74732;--amber:#F59435;--teal:#3F8D86;--blue:#1491A6;--grn:#1B3A2F;--ink:#1A1A1A;--muted:#5b6763;--bg:#F2F0EA;--border:#E4E1D8}}
body{{font-family:'Inter',sans-serif;background:var(--bg);color:var(--ink);line-height:1.7;-webkit-font-smoothing:antialiased}}
.bar{{display:flex;height:5px}}.bar div{{flex:1}}
header{{background:#fff;border-bottom:1px solid var(--border)}}
.head-inner{{max-width:820px;margin:0 auto;padding:20px 24px;display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap}}
.logo{{font-family:'Manrope',sans-serif;font-weight:800;font-size:22px;letter-spacing:-.02em;color:var(--ink);text-decoration:none;display:flex;align-items:center;gap:10px}}
.logo .mark{{width:26px;height:30px;display:inline-block}}
.back{{font-family:'Manrope',sans-serif;font-weight:700;font-size:14px;color:var(--teal);text-decoration:none}}
.back:hover{{text-decoration:underline}}
main{{max-width:820px;margin:0 auto;padding:44px 24px 80px}}
a{{color:var(--blue)}}
.crumbs{{font-size:13px;color:var(--muted);margin-bottom:22px}}
.crumbs a{{color:var(--muted);text-decoration:none}}
.crumbs a:hover{{text-decoration:underline}}
.crumbs span{{margin:0 7px;opacity:.55}}
h1{{font-family:'Manrope',sans-serif;font-weight:800;font-size:clamp(28px,4.4vw,40px);line-height:1.18;letter-spacing:-.03em;margin-bottom:14px}}
.meta{{display:flex;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:26px}}
.tag{{font-family:'Manrope',sans-serif;font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:var(--accent);border-radius:20px;padding:5px 13px}}
.date{{font-size:14px;color:var(--muted)}}
.hero-img{{width:100%;aspect-ratio:16/9;object-fit:cover;border-radius:12px;border:1px solid var(--border);background:var(--bg);margin-bottom:32px;display:block}}
article p{{margin-bottom:20px;font-size:17px}}
article p strong{{font-family:'Manrope',sans-serif;font-weight:800;color:var(--grn)}}
.lede{{font-size:19px;line-height:1.65;color:var(--muted);border-left:3px solid var(--accent);padding-left:20px;margin-bottom:34px}}
.endcap{{margin-top:44px;padding-top:30px;border-top:1px solid var(--border)}}
.endcap h2{{font-family:'Manrope',sans-serif;font-size:19px;font-weight:800;margin-bottom:8px}}
.endcap p{{font-size:15px;color:var(--muted);margin-bottom:16px}}
.cta{{display:inline-flex;align-items:center;gap:9px;background:var(--red);color:#fff;text-decoration:none;font-family:'Manrope',sans-serif;font-weight:700;font-size:15px;border-radius:40px;padding:13px 28px;transition:all .2s}}
.cta:hover{{background:#E0563F;transform:translateY(-1px)}}
.cta-alt{{background:var(--teal)}}
.cta-alt:hover{{background:#4CA69D}}
.more{{margin-top:52px;padding-top:30px;border-top:1px solid var(--border)}}
.more h2{{font-family:'Manrope',sans-serif;font-size:15px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);margin-bottom:18px}}
.morelist{{list-style:none;display:grid;gap:14px}}
.morelist a{{display:block;background:#fff;border:1px solid var(--border);border-left:3px solid var(--accent2, var(--teal));border-radius:10px;padding:16px 20px;text-decoration:none;color:inherit;transition:all .15s}}
.morelist a:hover{{transform:translateX(2px);box-shadow:0 2px 10px rgba(0,0,0,.05)}}
.morelist h3{{font-family:'Manrope',sans-serif;font-size:16px;font-weight:700;margin-bottom:4px}}
.morelist p{{font-size:13px;color:var(--muted);line-height:1.5}}
footer{{background:var(--ink);padding:28px 24px;text-align:center;font-size:12px;color:rgba(255,255,255,.4)}}
footer a{{color:rgba(255,255,255,.62)}}
@media(max-width:600px){{main{{padding:32px 20px 60px}}article p{{font-size:16px}}.lede{{font-size:17px;padding-left:16px}}}}
</style>
{schema}
</head>
<body>
<div class="bar"><div style="background:var(--red)"></div><div style="background:var(--amber)"></div><div style="background:var(--teal)"></div><div style="background:var(--blue)"></div></div>
<header><div class="head-inner">
  <a class="logo" href="/"><svg class="mark" viewBox="0 0 32 38" fill="none"><path d="M4 14 16 4l12 10v20H4z" stroke="#111" stroke-width="2.4" stroke-linejoin="round"/><rect x="10" y="12" width="12" height="3" rx="1.5" fill="#D74732"/><rect x="10" y="17" width="12" height="3" rx="1.5" fill="#F59435"/><rect x="10" y="22" width="12" height="3" rx="1.5" fill="#3F8D86"/><rect x="10" y="27" width="12" height="3" rx="1.5" fill="#1491A6"/></svg>HESTORA</a>
  <a class="back" href="/">&larr; Back to hestora.net</a>
</div></header>
"""

FOOTER = """<footer>&copy; 2026 Hestora Limited &middot; Company No. 16856062 &middot; Registered in England &amp; Wales &middot; <a href="/resources">Resources</a> &middot; <a href="/privacy">Privacy Policy</a> &middot; <a href="/cookies">Cookie Policy</a></footer>
</body>
</html>
"""


def social_meta(title, description, url, image, kind="article", published=None):
    tags = [
        f'<meta property="og:type" content="{kind}">',
        '<meta property="og:site_name" content="Hestora">',
        f'<meta property="og:title" content="{title}">',
        f'<meta property="og:description" content="{description}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{image}">',
        '<meta property="og:locale" content="en_GB">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:description" content="{description}">',
        f'<meta name="twitter:image" content="{image}">',
    ]
    if published:
        tags.insert(6, f'<meta property="article:published_time" content="{published}">')
    return "\n".join(tags)


def article_page(item, meta, others):
    slug = meta["slug"]
    url = f"{ORIGIN}/news/{slug}"
    title_txt = html.escape(item["title"], quote=True)
    desc = html.escape(meta["description"], quote=True)
    img_url = f"{ORIGIN}/{item['image']}" if item.get("image") else f"{ORIGIN}/assets/og-image.jpg"

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "NewsArticle",
                "headline": item["title"],
                "description": meta["description"],
                "image": img_url,
                "datePublished": meta["published"],
                "dateModified": meta["published"],
                "articleSection": item["tag"],
                "keywords": meta["keywords"],
                "inLanguage": "en-GB",
                "mainEntityOfPage": {"@type": "WebPage", "@id": url},
                "author": {"@type": "Organization", "name": "Hestora", "url": ORIGIN},
                "publisher": {
                    "@type": "Organization",
                    "name": "Hestora Limited",
                    "url": ORIGIN,
                    "logo": {"@type": "ImageObject", "url": f"{ORIGIN}/assets/og-image.jpg"},
                },
                "articleBody": " ".join(strip_tags(p) for p in item["body"]),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": ORIGIN + "/"},
                    {"@type": "ListItem", "position": 2, "name": "News", "item": f"{ORIGIN}/news"},
                    {"@type": "ListItem", "position": 3, "name": item["title"], "item": url},
                ],
            },
        ],
    }

    head = HEAD.format(
        title=f"{title_txt} | Hestora News",
        description=desc,
        canonical=url,
        extra_meta=social_meta(
            title_txt, desc, url, img_url, "article", meta["published"]
        ),
        schema='<script type="application/ld+json">'
        + json.dumps(schema, ensure_ascii=False)
        + "</script>",
    )

    body_html = "\n".join(f"  <p>{p}</p>" for p in item["body"])
    hero = (
        f'<img class="hero-img" src="/{item["image"]}" alt="{title_txt}" '
        f'width="1200" height="675" loading="eager">'
        if item.get("image")
        else ""
    )
    related = "\n".join(
        f'''    <li><a href="/news/{o[1]["slug"]}"><h3>{html.escape(o[0]["title"])}</h3>'''
        f'''<p>{html.escape(o[1]["description"])}</p></a></li>'''
        for o in others
    )

    return f"""{head}
<main style="--accent:{item['accent']}">
  <nav class="crumbs" aria-label="Breadcrumb">
    <a href="/">Home</a><span>/</span><a href="/news">News</a><span>/</span>{title_txt}
  </nav>

  <h1>{title_txt}</h1>
  <div class="meta">
    <span class="tag">{html.escape(item['tag'])}</span>
    <time class="date" datetime="{meta['published']}">{html.escape(item['date'])}</time>
  </div>

  {hero}

  <p class="lede">{item['excerpt']}</p>

  <article>
{body_html}
  </article>

  <div class="endcap">
    <h2>Be first in the queue</h2>
    <p>A monitored pilot of more than 20 homes begins in November 2026, with commercial sales planned for 2027.</p>
    <a class="cta" href="/#contact">Register interest<span aria-hidden="true">&rarr;</span></a>
    <a class="cta cta-alt" href="/resources" style="margin-left:10px">Resources &amp; downloads<span aria-hidden="true">&#8599;</span></a>
  </div>

  <div class="more">
    <h2>More from Hestora</h2>
    <ul class="morelist">
{related}
    </ul>
  </div>
</main>
{FOOTER}"""


def index_page(items):
    url = f"{ORIGIN}/news"
    desc = (
        "News from Hestora: prototype development, home trials, and the data behind "
        "zero-emission heating for the UK homes we already live in."
    )
    schema = {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "News from Hestora",
        "description": desc,
        "url": url,
        "inLanguage": "en-GB",
        "mainEntity": {
            "@type": "ItemList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "url": f"{ORIGIN}/news/{m['slug']}",
                    "name": it["title"],
                }
                for i, (it, m) in enumerate(items)
            ],
        },
    }
    head = HEAD.format(
        title="News | Hestora",
        description=html.escape(desc, quote=True),
        canonical=url,
        extra_meta=social_meta(
            "News from Hestora",
            html.escape(desc, quote=True),
            url,
            f"{ORIGIN}/assets/og-image.jpg",
            "website",
        ),
        schema='<script type="application/ld+json">'
        + json.dumps(schema, ensure_ascii=False)
        + "</script>",
    )
    rows = "\n".join(
        f'''    <li><a href="/news/{m["slug"]}" style="--accent2:{it["accent"]}">
      <h3>{html.escape(it["title"])}</h3>
      <p>{html.escape(it["tag"])} &middot; {html.escape(it["date"])} &mdash; {html.escape(m["description"])}</p>
    </a></li>'''
        for it, m in items
    )
    return f"""{head}
<main style="--accent:var(--blue)">
  <nav class="crumbs" aria-label="Breadcrumb">
    <a href="/">Home</a><span>/</span>News
  </nav>
  <h1>News from Hestora</h1>
  <p class="lede">Progress on prototypes, home trials, and our journey to bring zero-emission
  heating to the homes we already live in.</p>
  <ul class="morelist">
{rows}
  </ul>
  <div class="endcap">
    <h2>Be first in the queue</h2>
    <p>A monitored pilot of more than 20 homes begins in November 2026, with commercial sales planned for 2027.</p>
    <a class="cta" href="/#contact">Register interest<span aria-hidden="true">&rarr;</span></a>
    <a class="cta cta-alt" href="/resources" style="margin-left:10px">Resources &amp; downloads<span aria-hidden="true">&#8599;</span></a>
  </div>
</main>
{FOOTER}"""


def main():
    news = load_news()
    missing = [n["title"] for n in news if n["title"] not in META]
    if missing:
        sys.exit(
            "No META entry for: "
            + ", ".join(missing)
            + "\nAdd a slug, description, keywords and published date to META in this script."
        )

    pairs = [(n, META[n["title"]]) for n in news]

    written = []
    for item, meta in pairs:
        others = [p for p in pairs if p[1]["slug"] != meta["slug"]]
        path = os.path.join(HERE, meta["slug"] + ".html")
        open(path, "w", encoding="utf-8").write(article_page(item, meta, others))
        written.append(path)

    path = os.path.join(HERE, "index.html")
    open(path, "w", encoding="utf-8").write(index_page(pairs))
    written.append(path)

    # Keep the slug list where the sitemap generator (and a human) can find it.
    open(os.path.join(HERE, "_slugs.json"), "w", encoding="utf-8").write(
        json.dumps([m["slug"] for _, m in pairs], indent=2) + "\n"
    )

    for p in written:
        print(f"wrote {os.path.relpath(p, SITE)}  ({os.path.getsize(p):,} bytes)")


if __name__ == "__main__":
    main()
