# TechPulse

A daily tech-news blog powered by Hugo + Groq AI. Three articles with unique, verified Pollinations AI covers are generated and published to **Vercel** daily at 08:00 UTC (GitHub Actions commits to `main`; Vercel deploys on push). The job publishes nothing unless all three articles and covers pass validation.

## Pipeline
- **Generate Articles** (`generate.yml`) — Groq writes three articles + unique Pollinations covers each day at 08:00 UTC, validates all three, and commits to `main` with `[skip ci]` so unrelated social-marketing and image-backfill workflows do not run.
- **Marketing Automation** (`marketing.yml`) — cross-posts new articles to Telegram/Dev.to/Discord.
- **Deploy** — handled by Vercel's GitHub integration (no GitHub Pages deploy workflow).

> Note: there is intentionally **no GitHub Pages "Deploy Site" workflow** — the blog lives on Vercel. The original template's Pages job is gone.

## Setup
- `GROQ_API_KEY` repo secret (required for generation).
- Vercel project linked to this repo (`tech-blog` / `prj_UKYevxkxhdY2TNafxTFHnMLK6swX`).

## Usage
Articles generate daily at 08:00 UTC. To run manually: **Actions → Generate Articles → Run workflow**. The repository Actions secret `GROQ_API_KEY` is required.

Troubleshooting: if a run "succeeds" in seconds with 0 articles, the Groq model list has drifted — re-run the model diagnostic (`MODE=list` or the `Diagnose Groq Models` workflow) and update `GROQ_MODELS` in `scripts/generate.py`. The generator fails loudly (exit 1) on 0 articles so silent breakage can't recur.
