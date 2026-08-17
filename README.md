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
├── assets/           images, og-image, explainer video + poster, consent.js
└── docs/             the five published PDFs (white paper, sector briefings)
```

`sitemap.xml` advertises extensionless URLs (`/privacy`, `/resources`). Netlify serves
those from the `.html` files by default — no redirect rules needed.

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

**`assets/consent.js` and `cookies.html` must stay consistent.** The consent script has a
`COOKIELESS_BEFORE_CONSENT` flag governing how Microsoft Clarity loads; the cookie policy
describes whichever setting is live. Change one, change the other.

## Analytics

- **Microsoft Clarity** — loaded through `assets/consent.js`, gated on consent. Unaffected
  by hosting.
- **Cloudflare Web Analytics** — a cookieless beacon committed at the bottom of every page
  (added Aug 2026; previously Cloudflare's proxy injected it automatically). Same site and
  token throughout, so the dashboard history is continuous across the move to Netlify.

## History

Commit #1 is the site exactly as it was deployed by hand on 13 August 2026. Earlier
iterations predate version control and exist only as archived folders offline.
