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

Not in this repo, deliberately. The masters stay in Dropbox under
`05 Sales & Marketing / 01 Website`:

- `assets/` — the 66 MB of full-resolution images and the original explainer video
- `Website Thoughts.pptx`, `Website thoughts 250326.pptx` — design thinking
- `Website text v2/v3.docx` — the copy decks

Only the web-sized derivatives are committed here (~13 MB total). Same split as
`Skippers-Retreat`: masters in cloud storage, derivatives in git.

## Things to know before editing

**`index.html` is one 960 KB file.** Git stores a complete new copy on every edit and
the diffs are effectively unreadable. It works, but it means you lose most of the
"what actually changed?" benefit of version control. If the site keeps growing, split
it into partials or move to a static site generator — `Skippers-Retreat` uses Astro and
is a reasonable model.

**Never commit `.analytics-config.json`.** It carries a live Cloudflare API token and a
Clarity export token. It is in `.gitignore`, and it should live in a password manager.

**`assets/consent.js` and `cookies.html` must stay consistent.** The consent script has a
`COOKIELESS_BEFORE_CONSENT` flag governing how Microsoft Clarity loads; the cookie policy
describes whichever setting is live. Change one, change the other.

## Analytics

- **Microsoft Clarity** — loaded through `assets/consent.js`, gated on consent. Unaffected
  by hosting.
- **Cloudflare Web Analytics** — was injected automatically by Cloudflare and stops working
  once the site is on Netlify. Needs replacing (Plausible is cookieless and needs no consent
  banner; GA4 is free but does need consent).

## History

Commit #1 is the site exactly as it was deployed by hand on 13 August 2026. Everything
before that point exists only as the dated folders in Dropbox
(`Website 270726`, `Website 290726`, `Archive`) — kept for reference, superseded by this
repo's history.
