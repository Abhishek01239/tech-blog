#!/usr/bin/env python3
"""
Generate daily tech news articles using Groq API.
Images: Pollinations AI ONLY (keyless, 0-cost) — every cover is verified to
be Pollinations-generated (EXIF Make=sana, 800x450) or the article ships
without a cover. No Unsplash / Picsum / SVG fallbacks.
"""
import os
import json
import random
import time
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

try:
    from PIL import Image
    from PIL.ExifTags import TAGS
except ImportError:
    Image = None
    TAGS = {}

OUTPUT_DIR = Path(__file__).parent.parent / "content" / "posts"

POLLINATIONS_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "Chrome/120 Safari/537.36"
)
POLLINATIONS_ATTEMPTS = 4
POLLINATIONS_BACKOFF = [5, 10, 20]  # seconds between attempts


def is_pollinations_image(img_path: Path) -> bool:
    """Verify a downloaded cover is genuinely Pollinations-generated.

    Signature: EXIF Make == "sana" (Pollinations model) AND exactly 800x450.
    Returns False if Pillow is unavailable, parsing fails, or any check fails —
    an unverified image is treated as a failed download (never accepted).
    """
    if Image is None:
        return False
    try:
        with Image.open(img_path) as im:
            if im.format != "JPEG":
                return False
            w, h = im.size
            if w != 800 or h != 450:
                return False
            exif = im._getexif()
            if not exif:
                return False
            for k, v in exif.items():
                if TAGS.get(k) == "Make" and str(v).strip().lower() == "sana":
                    return True
            return False
    except Exception:
        return False


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
    """Download a Pollinations-generated cover into static/images/<slug>.jpg.

    Pollinations AI is the ONLY image source (keyless, 0-cost). Each download
    is VERIFIED (EXIF Make=sana, 800x450) before being accepted — if it cannot
    be verified after retries, returns None so the article ships without a
    cover rather than using a non-Pollinations image.
    """
    img_name = f"{slug or category}.jpg"
    img_path = Path(__file__).parent.parent / "static" / "images" / img_name
    if img_path.exists():
        return f"/images/{img_name}"  # already have a cover

    if not title:
        return None
    pol_url = (
        f"https://image.pollinations.ai/prompt/"
        f"{build_pollinations_prompt(title, category)}?width=800&height=450&nologo=true"
    )
    for attempt in range(POLLINATIONS_ATTEMPTS):
        try:
            req = urllib.request.Request(pol_url, headers={"User-Agent": POLLINATIONS_UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if len(data) > 5000:
                img_path.write_bytes(data)
                if is_pollinations_image(img_path):
                    return f"/images/{img_name}"
                # Not verified -> delete the unverified file and retry.
                try:
                    img_path.unlink()
                except OSError:
                    pass
        except Exception:
            pass
        if attempt < POLLINATIONS_ATTEMPTS - 1 and POLLINATIONS_BACKOFF:
            time.sleep(POLLINATIONS_BACKOFF[attempt])
    print(f"  WARN: could not get a verified Pollinations cover for {img_name}")
    return None


def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set")
        exit(1)
    try:
        from groq import Groq
    except ImportError:
        print("pip install groq")
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
    image_line = f'image: "{image_url}"' if image_url else "image: \"\""
    tags_yaml = json.dumps(article.get("tags", [category]))
    
    frontmatter = f"""---
title: "{article['title']}"
date: {today}
draft: false
description: "{article['description']}"
tags: {tags_yaml}
categories: ["{category.title()}"]
author: "{os.environ.get('BLOG_AUTHOR', 'TechPulse')}"
{image_line}
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
    
    print(f"Generating {num_articles} tech news articles (images: Pollinations AI)...")
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
