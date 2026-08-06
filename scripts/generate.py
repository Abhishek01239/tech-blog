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

def get_image_url(category):
    """Get image URL: Pexels API first, picsum fallback."""
    search = CATEGORY_SEARCH.get(category, CATEGORY_SEARCH["general"])
    
    # Try Pexels API (free: 33 req/month, needs key)
    pexels_key = os.environ.get("PEXELS_API_KEY")
    if pexels_key:
        try:
            query = urllib.parse.quote(search)
            url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
            req = urllib.request.Request(url, headers={"Authorization": pexels_key})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                if data.get("photos"):
                    return data["photos"][0]["src"]["large"]  # 800px wide
        except Exception:
            pass  # Fall through to picsum
    
    # Picsum fallback (free, no key, seeded for consistency)
    seed = f"{category}-{random.randint(1,9999)}"
    return f"https://picsum.photos/seed/{seed}/800/400"

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
    image_url = get_image_url(category)
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
