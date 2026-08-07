#!/usr/bin/env python3
"""
Generate daily tech news articles using Groq API.
Images: Pexels API (if key available) → picsum fallback (always free).
"""
import os
import json
import random
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    print("pip install groq")
    exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "content" / "posts"

# Keyword → search terms mapping for Pexels
CATEGORY_SEARCH = {
    "ai": "artificial intelligence robot",
    "startups": "startup office technology",
    "phones": "smartphone mobile app",
    "crypto": "cryptocurrency bitcoin",
    "space": "space rocket nasa",
    "gaming": "gaming esports",
    "cloud": "server data center",
    "cybersecurity": "cybersecurity hacking",
    "programming": "programming code",
    "general": "technology innovation",
}

# Curated pool of real Unsplash photos (permanent images.unsplash.com CDN URLs,
# free, no API key/rate-limit). All verified to return HTTP 200.
# Images are DOWNLOADED into the repo so they're self-hosted on Vercel.
UNSPLASH_POOL = {
    "ai":             ["1518770660439-4636190af475", "1485827404703-89b55fcc595e", "1535378917042-10a22c95931a"],
    "general":        ["1516321497487-e288fb19713f", "1462331940025-496dfbfc7564", "1498050108023-c5249f4df085"],
    "startups":       ["1516321497487-e288fb19713f", "1498050108023-c5249f4df085", "1467232004584-a241de8bcf5d"],
    "phones":         ["1516321497487-e288fb19713f", "1535378917042-10a22c95931a", "1498050108023-c5249f4df085"],
    "crypto":         ["1518546305927-5a555bb7020d", "1563013544-824ae1b704d3"],
    "space":          ["1451187580459-43490279c0fa", "1446776811953-b23d57bd21aa", "1457364887197-9150188c107b", "1502134249126-9f3755a50d78"],
    "gaming":         ["1535378917042-10a22c95931a", "1516321497487-e288fb19713f", "1462331940025-496dfbfc7564"],
    "cloud":          ["1518770660439-4636190af475", "1451187580459-43490279c0fa", "1498050108023-c5249f4df085"],
    "cybersecurity":  ["1550751827-4bd374c3f58b", "1563013544-824ae1b704d3", "1526374965328-7f61d4dc18c5", "1563986768609-322da13575f3"],
    "programming":    ["1461749280684-dccba630e2f6", "1498050108023-c5249f4df085", "1467232004584-a241de8bcf5d"],
}

def build_pollinations_prompt(title, category):
    """Turn an article title+category into a safe AI-image prompt."""
    base = {
        "ai": "futuristic AI neural network glowing circuits",
        "startups": "modern tech startup office glass skyscrapers",
        "phones": "sleek smartphone on dark gradient background",
        "crypto": "digital blockchain coin glowing gold",
        "space": "rocket launching into deep space stars",
        "gaming": "futuristic gaming controller neon glow",
        "cloud": "server data center blue lights abstract",
        "cybersecurity": "cyber security holographic padlock circuits",
        "programming": "holographic code typing futuristic terminal",
    }.get((category or "").lower(), "futuristic technology innovation")
    prompt = f"{title}. style: {base}, cinematic lighting, high detail"
    return urllib.parse.quote(prompt[:120])


def get_image_url(category, slug=None, title=None):
    """Download article cover image into static/images/<slug>.jpg.

    Priority: Pollinations AI (unique, on-topic, 0-cost, no key) -> curated
    Unsplash pool -> picsum -> SVG cover (ensure_images.py last resort).
    Always downloads into the repo (self-hosted on Vercel, never hotlinks).
    Returns the local path or the /images/<slug>.svg fallback.
    """
    img_name = f"{slug or category}.jpg"
    img_path = Path(__file__).parent.parent / "static" / "images" / img_name
    if img_path.exists():
        return f"/images/{img_name}"  # cached

    sources = []
    # 1) Pollinations AI - unique generated image, no API key, works from GH DC.
    #    Flaky: retry 3x with backoff before falling through to Unsplash.
    if title:
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
        pol_url = f"https://image.pollinations.ai/prompt/{build_pollinations_prompt(title, category)}?width=800&height=450&nologo=true"
        import time
        for attempt in range(3):
            try:
                req = urllib.request.Request(pol_url, headers={"User-Agent": ua})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                    if len(data) > 5000 and resp.status == 200:
                        img_path.write_bytes(data)
                        return f"/images/{img_name}"
            except Exception:
                pass
            if attempt < 2:
                time.sleep(3 * (attempt + 1))  # 3s, 6s backoff
    # 2) curated Unsplash pool
    pool = UNSPLASH_POOL.get((category or "").lower(), UNSPLASH_POOL["general"])
    h = sum(ord(c) for c in (slug or category)) % len(pool)
    uid = pool[h]
    sources.append(
        ("unsplash", f"https://images.unsplash.com/photo-{uid}?auto=format&fit=crop&w=800&q=80", "Mozilla/5.0")
    )
    # 3) picsum fallback
    sources.append(
        ("picsum", f"https://picsum.photos/seed/{slug or category}/800/450", "Mozilla/5.0")
    )

    for name, src, ua in sources:
        try:
            req = urllib.request.Request(src, headers={"User-Agent": ua})
            with urllib.request.urlopen(req, timeout=40) as resp:
                data = resp.read()
                if len(data) > 5000 and resp.status == 200:
                    img_path.write_bytes(data)
                    return f"/images/{img_name}"
        except Exception:
            continue
    return f"/images/{slug or category}.svg"  # last resort -> SVG cover

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set")
        exit(1)
    return Groq(api_key=api_key)

def generate_news_article(client, topic=None):
    """Generate a tech news article using Groq."""
    prompt = f"""Write a tech news article about a recent development in technology.

TOPIC: {topic or 'latest tech news'}

REQUIREMENTS:
1. Title: Catchy, news-style headline (under 70 characters), include company/product name if relevant
2. Meta description: 150-160 characters, news-style, compelling click
3. Lead: First paragraph summarizes the news in 2-3 sentences
4. Body: 400-600 words covering: what happened, why it matters, industry impact
5. Tone: Journalistic, factual, engaging — like TechCrunch or The Verge
6. Use H2 (##) subheadings for major points
7. Include specific details: company names, dates, numbers, quotes if applicable
8. End with "What's Next" or "Impact" section
9. SEO keywords: tech news, {topic or 'technology'}, startup, AI, innovation

OUTPUT FORMAT (strict JSON):
{{
    "title": "headline (under 70 chars)",
    "description": "meta description (150-160 chars)",
    "category": "ai|startups|phones|crypto|space|gaming|cloud|cybersecurity|programming|general",
    "tags": ["tag1", "tag2", "tag3"],
    "content": "full markdown article content"
}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    
    return json.loads(response.choices[0].message.content)

def slugify(text):
    return text.lower().strip().replace(" ", "-").replace("/", "-")[:60]

def save_article(article):
    """Save article as Hugo markdown with featured image."""
    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(article["title"])
    filename = f"{today}-{slug}.md"
    filepath = OUTPUT_DIR / filename
    
    category = article.get("category", "general")
    image_url = get_image_url(category, slug, article["title"])
    tags_yaml = json.dumps(article.get("tags", [category]))
    
    frontmatter = f"""---
title: "{article['title']}"
date: {today}
draft: false
description: "{article['description']}"
tags: {tags_yaml}
categories: ["{category.title()}"]
author: "{os.environ.get('BLOG_AUTHOR', 'TechPulse')}"
image: "{image_url}"
---"""
    
    content = f"{frontmatter}\n\n{article['content']}"
    filepath.write_text(content, encoding="utf-8")
    print(f"  -> {filename}")
    return filepath

def main():
    client = get_groq_client()
    num_articles = int(os.environ.get("NUM_ARTICLES", "5"))
    
    topics = [
        "latest AI model release or breakthrough",
        "major tech company product launch or announcement",
        "startup funding round or acquisition",
        "open source project milestone or release",
        "cybersecurity incident or vulnerability discovery",
        "cloud computing service update or new feature",
        "mobile app or phone technology update",
        "space technology or satellite launch",
        "programming language or developer tool release",
        "regulatory news about big tech companies",
    ]
    
    pexels = "yes" if os.environ.get("PEXELS_API_KEY") else "no"
    print(f"Generating {num_articles} tech news articles (Pexels: {pexels})...")
    generated = []
    
    for i in range(num_articles):
        topic = random.choice(topics)
        print(f"\n[{i+1}/{num_articles}] {topic[:60]}...")
        
        try:
            article = generate_news_article(client, topic)
            path = save_article(article)
            generated.append({
                "title": article["title"],
                "category": article.get("category", "general"),
                "file": str(path),
            })
        except Exception as e:
            print(f"  ERROR: {e}")
    
    summary_path = OUTPUT_DIR.parent.parent / "generation-summary.json"
    summary_path.write_text(json.dumps(generated, indent=2), encoding="utf-8")
    
    print(f"\nDone! Generated {len(generated)} articles.")
    
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("## Generated Tech News Articles\n\n")
            for g in generated:
                f.write(f"- **{g['title']}** ({g['category']})\n")

if __name__ == "__main__":
    main()
