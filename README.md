# TechPulse

A technology publication built with Hugo and deployed on Vercel.

Live: https://www.nexivo.org.in

## Current publishing status

**Article publishing and marketing automation are intentionally disabled while the Google AdSense application is under review.** No GitHub Actions workflow generates, publishes, or cross-posts articles.

The existing published website and article archive are preserved. Do not add or publish new articles until the AdSense decision has been received and the site owner explicitly chooses to resume publishing.

## Structure

| Path | Purpose |
| --- | --- |
| `content/posts/` | Existing published articles |
| `layouts/` | Hugo templates |
| `static/` | CSS, JS, images, and ads.txt |
| `build.sh` | Installs Hugo and builds the site for Vercel |
| `scripts/` | Retained utility scripts; no article-generation workflow invokes them |

## Deployment

The site remains connected to Vercel through GitHub. A push to `main` may trigger a website build and deployment. This is deployment of the existing site, not an article-generation or marketing workflow.

## Local development

```bash
npm install
npx hugo server
npx hugo --minify
```

## Google AdSense

- The existing publisher verification metadata and `static/ads.txt` are preserved.
- Ad requests remain disabled until consent management is correctly configured.
- The AdSense application and its decision are managed in the owner's AdSense account.
- Do not interpret a successful Vercel deployment as AdSense approval.
