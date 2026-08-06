# Tech Tutorials Hub

A tech tutorial blog powered by Hugo and Groq AI. Articles are auto-generated daily using Groq's fast inference API, then deployed to GitHub Pages.

## Features

- **Auto-generated articles** — Groq API writes SEO-optimized tutorials daily
- **SEO optimized** — Proper meta tags, structured data, keywords
- **Fast deployment** — Hugo static site on GitHub Pages
- **Free hosting** — No server costs

## Setup

### 1. Create the repo
```bash
# Create a new repo on GitHub, then:
git init
git remote add origin https://github.com/YOUR_USERNAME/tech-blog.git
```

### 2. Set GitHub Secrets
Go to **Settings → Secrets and variables → Actions → New repository secret**:
- `GROQ_API_KEY` — Your Groq API key (get from https://console.groq.com)

### 3. Enable GitHub Pages
Go to **Settings → Pages → Source → GitHub Actions**

### 4. Push and deploy
```bash
git add .
git commit -m "initial commit"
git push -u origin main
```

The site will be live at `https://YOUR_USERNAME.github.io/tech-blog/`

## Usage

### Auto-generate articles
Articles generate automatically daily at 8am UTC. To generate manually:
1. Go to **Actions → Generate Articles → Run workflow**
2. Enter number of articles (default: 3)

### Generate locally
```bash
pip install groq
export GROQ_API_KEY="your-key-here"
python scripts/generate.py
```

### Customize topics
Edit `scripts/generate.py` → `TOPICS` dict to add/remove categories and topics.

## Tech Stack

- **Hugo** — Static site generator
- **Groq API** — Fast article generation (Llama 3.3 70B)
- **GitHub Actions** — CI/CD pipeline
- **GitHub Pages** — Free hosting

## Revenue

After getting traffic:
1. Buy a custom domain (~$10/year)
2. Apply for Google AdSense
3. Earn ~$5-15 per 1,000 daily visitors

## License

MIT
