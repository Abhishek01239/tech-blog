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
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)  # fresh clones lack the empty dir
IMAGE_DIR = Path(__file__).parent.parent / "static" / "images"
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

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


def get_image_url(category, slug=None, title=None, existing_hashes=None, seed=0):
    """Download a Pollinations-generated cover into static/images/<slug>.jpg.

    Pollinations AI is the ONLY image source (keyless, 0-cost). Each download
    is VERIFIED (EXIF Make=sana, 800x450) before being accepted. Image content
    must ALSO be unique: if its sha256 already exists in static/images/ (via
    existing_hashes), the download is rejected and retried with a different
    seed. Returns None if no unique verified cover is obtained.
    """
    img_name = f"{slug or category}.jpg"
    img_path = IMAGE_DIR / img_name
    if img_path.exists():
        return f"/images/{img_name}"  # already have a cover

    if not title:
        return None
    existing_hashes = existing_hashes or set()
    for attempt in range(POLLINATIONS_ATTEMPTS):
        seed_param = f"&seed={seed + attempt}" if (seed or attempt) else ""
        pol_url = (
            f"https://image.pollinations.ai/prompt/"
            f"{build_pollinations_prompt(title, category)}?width=800&height=450&nologo=true{seed_param}"
        )
        try:
            req = urllib.request.Request(pol_url, headers={"User-Agent": POLLINATIONS_UA})
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = resp.read()
            if len(data) > 5000:
                img_path.write_bytes(data)
                if is_pollinations_image(img_path):
                    content_hash = pollinations_image_hash(img_path)
                    if content_hash not in existing_hashes:
                        return f"/images/{img_name}"  # verified + unique
                    print(f"  INFO: duplicate image content for {img_name}, retrying with new seed...")
                # Not verified or duplicate -> delete the file and retry.
                try:
                    img_path.unlink()
                except OSError:
                    pass
        except Exception:
            pass
        if attempt < POLLINATIONS_ATTEMPTS - 1 and POLLINATIONS_BACKOFF:
            time.sleep(POLLINATIONS_BACKOFF[attempt])
    print(f"  WARN: could not get a unique verified Pollinations cover for {img_name}")
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


def normalize_title(title):
    """Lowercase, keep alphanumerics/space, collapse whitespace.
    Used to compare titles for dedup despite punctuation/case differences."""
    import re
    t = re.sub(r"[^a-z0-9 ]", " ", (title or "").lower())
    return re.sub(r"\s+", " ", t).strip()


def load_existing_titles():
    """Return set of normalized titles already present in content/posts/."""
    seen = set()
    if OUTPUT_DIR.exists():
        for path in OUTPUT_DIR.glob("*.md"):
            raw = path.read_text(encoding="utf-8")
            import re as _re
            m = _re.search(r"(?m)^title:\s*\"([^\"]+)\"", raw)
            if m:
                seen.add(normalize_title(m.group(1)))
    return seen


def pollinations_image_hash(img_path: Path) -> str:
    """Content (sha256) hash used to detect byte-identical duplicate covers."""
    import hashlib
    try:
        return hashlib.sha256(img_path.read_bytes()).hexdigest()
    except Exception:
        return ""


def existing_image_hashes():
    """Set of content hashes of every jpg already in static/images/."""
    hashes = set()
    img_dir = Path(__file__).parent.parent / "static" / "images"
    if img_dir.exists():
        for jpg in img_dir.glob("*.jpg"):
            hashes.add(pollinations_image_hash(jpg))
    return hashes

def save_article(article, existing_titles=None, existing_hashes=None, used_titles=None, seed=0):
    """Save article as Hugo markdown with a UNIQUE featured image.

    Returns the saved Path, or None if the title is a duplicate of an existing
    post / already-generated-this-run article (skipped, not saved).
    """
    existing_titles = existing_titles or set()
    used_titles = used_titles or set()
    norm = normalize_title(article.get("title", ""))
    if norm in existing_titles or norm in used_titles:
        print(f"  DUP: skipping duplicate title: {article.get('title','')!r}")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(article["title"])
    filename = f"{today}-{slug}.md"
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        print(f"  DUP: slug already exists, skipping: {filename}")
        return None

    category = article.get("category", "general")
    image_url = get_image_url(category, slug, article["title"], existing_hashes, seed)
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
    used_titles.add(norm)
    if image_url and existing_hashes is not None:
        img_path = IMAGE_DIR / f"{slug}.jpg"
        existing_hashes.add(pollinations_image_hash(img_path))  # prevent same-run dup
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
    
    print(f"Generating {num_articles} unique tech news articles (images: Pollinations AI)...")
    generated = []
    existing_titles = load_existing_titles()
    existing_hashes = existing_image_hashes()
    used_titles = set()

    i = 0
    total_attempts = 0
    max_attempts = max(num_articles * 5, 20)  # generous re-roll budget
    while i < num_articles and total_attempts < max_attempts:
        total_attempts += 1
        topic = random.choice(topics)
        print(f"\n[{i+1}/{num_articles}] attempt {total_attempts}: {topic[:60]}...")

        try:
            article = generate_news_article(client, topic)
            path = save_article(
                article,
                existing_titles=existing_titles,
                existing_hashes=existing_hashes,
                used_titles=used_titles,
                seed=i * 97 + 13,  # unique starting seed per slot
            )
            if path is None:
                continue  # duplicate -> re-roll with a fresh topic
            generated.append({
                "title": article["title"],
                "category": article.get("category", "general"),
                "file": str(path),
            })
            i += 1
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
