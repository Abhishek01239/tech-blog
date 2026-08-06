#!/usr/bin/env python3
"""
Generate daily tech news articles using Groq API.
Outputs Hugo-compatible markdown with featured images.
"""
import os
import json
import random
from datetime import datetime
from pathlib import Path

try:
    from groq import Groq
except ImportError:
    print("pip install groq")
    exit(1)

OUTPUT_DIR = Path(__file__).parent.parent / "content" / "posts"

# Free image sources (Pexels/Unsplash keywords)
IMAGE_KEYWORDS = {
    "ai": ["artificial-intelligence", "machine-learning", "neural-network", "robot", "deep-learning"],
    "startups": ["startup", "technology-office", "coding", "developer", "laptop"],
    "phones": ["smartphone", "mobile-app", "iphone", "android", "mobile-phone"],
    "crypto": ["cryptocurrency", "bitcoin", "blockchain", "ethereum", "digital-currency"],
    "space": ["space", "rocket", "nasa", "satellite", "mars"],
    "gaming": ["gaming", "esports", "video-game", "controller", "gaming-setup"],
    "cloud": ["cloud-computing", "server", "data-center", "cloud", "infrastructure"],
    "cybersecurity": ["cybersecurity", "hacker", "firewall", "encryption", "security"],
    "programming": ["programming", "code", "developer", "software", "coding"],
    "general": ["technology", "innovation", "tech", "computer", "digital"],
}

def get_image_url(category):
    """Get a free Pexels image URL for the category."""
    keywords = IMAGE_KEYWORDS.get(category, IMAGE_KEYWORDS["general"])
    keyword = random.choice(keywords)
    # Use picsum for reliable free images (seeded by article content)
    return f"https://picsum.photos/seed/{keyword}-{random.randint(1,999)}/800/400"

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
1. Title: Catchy, news-style headline (under 70 characters), include the company/product name if relevant
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
    
    # Hot topics to cycle through
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
    
    print(f"Generating {num_articles} tech news articles...")
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
    
    # Summary
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
