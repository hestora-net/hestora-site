# hestora-site

The public marketing site, **www.hestora.net**. Static HTML — no framework, no build step.

## Deploying

Push to `main`. Netlify builds and deploys automatically. There is no other step, and
no manual upload — if a change isn't in `main`, it isn't live.

```bash
git add -A
git commit -m "Describe what changed and why"
git push
```

Netlify publishes the `site/` directory exactly as it stands. Every pull request gets
its own deploy preview URL — use it to check a change before merging.

## What's here

```
site/
├── index.html        the whole homepage, single file (~960 KB)
├── privacy.html  cookies.html  resources.html
├── robots.txt  sitemap.xml
├── _redirects        Netlify redirect rules -- must live here, not at the repo root
├── assets/           images, og-image, explainer video + poster, consent.js
└── docs/             the five published PDFs (white paper, sector briefings)
```

`sitemap.xml` advertises extensionless URLs (`/privacy`, `/resources`). Netlify serves
those from the `.html` files by default, so no rule is needed to make them work.
(`_redirects` exists for a different job — see below.)

Two things follow from that:

- **Write internal links in the extensionless form yourself.** `href="/privacy"`, not
  `href="privacy.html"`. Netlify's post-processing used to rewrite the `.html` form for us,
  but only in HTML — never in JavaScript — so a link built inside `consent.js` had to be
  canonical already, and the deployed HTML was never byte-identical to what was committed.
  As of 22 Aug 2026 every internal link in the repo is canonical to begin with, so that
  rewrite has nothing left to do and repo and deploy now agree. Keep it that way: a new
  `.html` link would quietly reintroduce the split.

  This is not cosmetic. While internal links pointed at `resources.html` and the sitemap
  advertised `/resources`, Google saw the sitemap URL as an orphan with nothing linking to
  it and never crawled the page — *"URL is unknown to Google — no referring sitemaps
  detected, no referring page detected"* on 22 Aug. Bing, which leans on the sitemap more,
  had it indexed fine. Both forms still return 200, so old bookmarks keep working.
- **Both forms return 200.** `/privacy` and `/privacy.html` each serve the page rather than
  one redirecting to the other, so every page carries a `rel="canonical"` pointing at the
  extensionless form to keep search engines on a single URL. Keep that tag on any new page.

## Where the source material lives

Not in this repo, deliberately. The full-resolution image masters, the original
explainer video, and the design/copy working documents live in company cloud
storage. Only the web-sized derivatives are committed here (~13 MB total).

## Things to know before editing

**`index.html` is one 960 KB file.** Git stores a complete new copy on every edit and
the diffs are effectively unreadable. It works, but it means you lose most of the
"what actually changed?" benefit of version control. If the site keeps growing, split
it into partials or move to a static site generator — `Skippers-Retreat` uses Astro and
is a reasonable model.

**Never commit credential files.** `.gitignore` blocks `.env` files and analytics
config files. Anything secret belongs in a password manager, never in this repo.

**The Product schema in `index.html` has no `offers` block, deliberately.** Google Search
Console will flag the Product entity as missing `image` and report a critical Merchant
listings error. **Do not fix that by adding an `image` field.** The `offers` object was
removed on 22 Aug 2026 because it was false: it declared a `schema.org/PreOrder` — which
means the item can be ordered *now* — on a site with no cart, no checkout, and no orders
until 2027. It also published `£3,500` as a machine-readable fact, stripped of the `**`
caveats the page shows, with `priceValidUntil` asserting the price holds to the end of
2027. Restoring product rich results means publishing a firm price ahead of launch: a
commercial decision, worth a word with whoever owns the consumer terms first.

**`_redirects` must live in `site/`, not the repo root.** `netlify.toml` sets
`publish = "site"`, and Netlify only reads `_redirects` from the publish root — a copy at
the repo root is silently ignored. It currently does one job: 301s the Netlify-assigned
subdomain `hestora-site.netlify.app` to `www.hestora.net`, so that host stops competing
with the real site for the same content. Apex → www is *not* here; that is set in Netlify
Domain management by making `www.hestora.net` the primary domain.

**`assets/consent.js` and `cookies.html` must stay consistent.** The consent script has a
`COOKIELESS_BEFORE_CONSENT` flag governing how Microsoft Clarity loads; the cookie policy
describes whichever setting is live. Change one, change the other.

The same rule covers anything else that measures visitors. `cookies.html` documents every
tracking technology on the site — currently the consent preference in local storage, the
Chilli Pepper form, Cloudflare Web Analytics and Microsoft Clarity. **Adding or removing a
script that observes visitors means editing that table in the same commit.** The Cloudflare
beacon was added in Aug 2026 without updating the policy, and the gap went unnoticed until
the site was reviewed.

**There is only one consent banner**, built by `assets/consent.js`, keyed on
`hestora-consent` in local storage. An older inline banner keyed on `hestora-cookie-ok`
used to sit in `index.html` as well, which meant first-time visitors dismissed a banner
twice. Don't reintroduce a second one.

## Analytics

- **Microsoft Clarity** — loaded through `assets/consent.js`, gated on consent. Unaffected
  by hosting.
- **Cloudflare Web Analytics** — a cookieless beacon committed at the bottom of every page
  (added Aug 2026; previously Cloudflare's proxy injected it automatically). Same site and
  token throughout, so the dashboard history is continuous across the move to Netlify.

## History

Commit #1 is the site exactly as it was deployed by hand on 13 August 2026. Earlier
iterations predate version control and exist only as archived folders offline.
