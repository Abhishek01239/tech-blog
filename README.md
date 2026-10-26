# TechPulse

A daily technology news site built with Hugo and deployed on Vercel. Stories are generated several times a day, verified before publishing, and committed to `main`. Vercel's GitHub integration builds and deploys on every push — there is no separate deploy workflow.

Live: https://tech-blog-eight-blush.vercel.app

## Structure

| Path | Purpose |
| --- | --- |
| `content/posts/` | Articles (Markdown with YAML front matter) |
| `layouts/` | Hugo templates |
| `static/` | CSS, JS, images, `ads.txt` |
| `build.sh` | Installs Hugo and builds the site (used by Vercel) |
| `scripts/` | Generation and image tooling |

## Workflows

- **Ensure Article Images** (`ensure-article-images.yml`) — backfills missing article covers and commits them to `main`.
- **Marketing Automation** (`marketing.yml`) — cross-posts newly published articles to Telegram, Dev.to, and Discord.

There is intentionally no GitHub Pages deploy job; the site runs on Vercel.

## Local development

```bash
npm install
npx hugo server      # http://localhost:1313
npx hugo --minify    # build to public/
```

`build.sh` pins Hugo 0.167.0 for production builds. If a local Hugo is older, `hugo build` will not exist — use `hugo --minify` instead.

## Google AdSense

- Publisher ID lives in `hugo.toml` as `params.adsensePublisher` and is used for the verification meta tag.
- `static/ads.txt` must match that ID exactly.
- The AdSense script is loaded only after a visitor accepts the cookie banner (`static/js/consent.js`); rejecting means no ad cookies.
- Ad slots render only when `adsenseSlotArticle` / `adsenseSlotSidebar` are set to real unit IDs from AdSense. While empty, the pages render no ad containers.

## Setup

- `GROQ_API_KEY` repository secret, required for article generation.
- Vercel project `tech-blog` (`prj_UKYevxkxhdY2TNafxTFHnMLK6swX`), linked to this repository.

## Troubleshooting

If a generation run finishes in seconds with zero articles, the Groq model list has drifted. Re-run the model diagnostic (`MODE=list`) and update `GROQ_MODELS` in `scripts/generate.py`. The generator exits non-zero on zero articles so silent breakage is visible.
