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
import re
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

# Groq models currently supported for production/developer use.
# Keep the preferred high-quality model first, with fallbacks in case of
# temporary availability/rate-limit differences. Groq decommissioned
# qwen/qwen3.6-27b and the Compound systems in September 2026, so they must
# not remain in this list.
GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
]


def pick_working_model(client):
    """Return the first Groq model that handles a JSON-mode probe call.

    Raises RuntimeError if none of GROQ_MODELS are usable (so the workflow
    fails loudly instead of silently generating zero articles).
    """
    skip_codes = ("model_not_found", "model_decommissioned", "404", "400")
    for model in GROQ_MODELS:
        try:
            client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": 'reply with JSON: {"ok": true}'}],
                max_tokens=20,
                response_format={"type": "json_object"},
            )
            print(f"  Using Groq model: {model}")
            return model
        except Exception as e:
            msg = str(e).lower()
            if any(c in msg for c in skip_codes):
                print(f"  SKIP model {model}: no longer available")
                continue
            # Non-model error (bad key, rate limit) — don't silently swap models
            raise
    raise RuntimeError(
        "No available Groq model found among: " + ", ".join(GROQ_MODELS)
    )


def generate_news_article(client, topic=None, model="openai/gpt-oss-120b"):
    """Generate a sourced technology article draft using Groq."""
    prompt = f"""Write a well-sourced technology article draft about a recent development.

TOPIC: {topic or 'latest tech news'}

EDITORIAL REQUIREMENTS:
1. Use only claims that can be supported by the source URLs you provide.
2. Never invent companies, products, dates, figures, quotes, research findings, or announcements.
3. Prefer primary sources: company announcements, official documentation, regulatory filings, research papers, and court or government documents.
4. Include 2-4 specific source records with the exact public URL and page title. Do not invent URLs. If you cannot identify at least two credible sources, return an empty sources array.
5. Explain what happened, how it works, who is affected, limitations, and why it matters. Add original context rather than rewriting a headline.
6. Target 500-800 words. Use clear H2 subheadings and a useful conclusion.
7. Keep the tone factual and accessible. Clearly distinguish confirmed facts from analysis.
8. Do not include fabricated quotations. Paraphrase and attribute instead.
9. Write a concise, accurate title under 70 characters and a useful meta description.

OUTPUT FORMAT (strict JSON):
{{
    "title": "accurate headline",
    "description": "useful meta description",
    "category": "ai|startups|phones|crypto|space|gaming|cloud|cybersecurity|programming|general",
    "tags": ["tag1", "tag2", "tag3"],
    "content": "full markdown article content",
    "sources": [
        {{"title": "exact source page title", "url": "https://example.com/real-source"}}
    ]
}}

If reliable sources cannot be identified, return "sources": [] and do not fabricate them."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=3000,
        response_format={"type": "json_object"},
    )

    return json.loads(response.choices[0].message.content)
def slugify(text):
    """Lowercase, keep alphanumerics + dash, strip Hugo-sanitized chars ($ etc.)."""
    return re.sub(r"[^a-z0-9-]", "", text.lower().strip().replace(" ", "-").replace("/", "-"))[:60]


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
    """Save a sourced article as an unpublished Hugo draft for human review."""
    existing_titles = existing_titles or set()
    used_titles = used_titles or set()

    title = str(article.get("title", "")).strip()
    description = str(article.get("description", "")).strip()
    article_content = str(article.get("content", "")).strip()
    if not title or not description or not article_content:
        print("  REJECT: missing title, description, or article body")
        return None

    word_count = len(re.findall(r"\b[\w'-]+\b", article_content))
    if word_count < 350:
        print(f"  REJECT: article is too short ({word_count} words; minimum 350)")
        return None

    sources = article.get("sources", [])
    valid_sources = []
    seen_urls = set()
    if isinstance(sources, list):
        for source in sources:
            if not isinstance(source, dict):
                continue
            source_title = str(source.get("title", "")).strip()
            source_url = str(source.get("url", "")).strip()
            parsed_url = urllib.parse.urlparse(source_url)
            if (
                source_title
                and parsed_url.scheme == "https"
                and parsed_url.netloc
                and source_url not in seen_urls
            ):
                valid_sources.append({"title": source_title, "url": source_url})
                seen_urls.add(source_url)

    if len(valid_sources) < 2:
        print("  REJECT: at least two HTTPS source references are required")
        return None

    norm = normalize_title(title)
    if norm in existing_titles or norm in used_titles:
        print(f"  DUP: skipping duplicate title: {title!r}")
        return None

    today = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(title)
    filename = f"{today}-{slug}.md"
    filepath = OUTPUT_DIR / filename
    if filepath.exists():
        print(f"  DUP: slug already exists, skipping: {filename}")
        return None

    category = str(article.get("category", "general")).strip().lower()
    allowed_categories = {
        "ai", "startups", "phones", "crypto", "space", "gaming",
        "cloud", "cybersecurity", "programming", "general",
    }
    if category not in allowed_categories:
        category = "general"

    tags = article.get("tags", [category])
    if not isinstance(tags, list):
        tags = [category]
    tags_yaml = json.dumps([str(tag).strip() for tag in tags if str(tag).strip()])
    image_url = get_image_url(category, slug, title, existing_hashes, seed)
    image_line = f"image: {json.dumps(image_url)}" if image_url else 'image: ""'
    source_markdown = "\n".join(
        f"- [{source['title']}]({source['url']})" for source in valid_sources
    )

    frontmatter = f"""---
title: {json.dumps(title, ensure_ascii=False)}
date: {today}
draft: true
review_status: "needs-review"
description: {json.dumps(description, ensure_ascii=False)}
tags: {tags_yaml}
categories: [{json.dumps(category.title())}]
author: {json.dumps(os.environ.get('BLOG_AUTHOR', 'TechPulse'), ensure_ascii=False)}
{image_line}
---"""

    content = f"{frontmatter}\n\n{article_content}\n\n### Sources\n\n{source_markdown}\n"
    filepath.write_text(content, encoding="utf-8")
    used_titles.add(norm)

    if image_url and existing_hashes is not None:
        img_path = IMAGE_DIR / f"{slug}.jpg"
        existing_hashes.add(pollinations_image_hash(img_path))

    print(f"  -> saved unpublished review draft: {filename} ({word_count} words, {len(valid_sources)} sources)")
    return filepath
def list_models(client):
    """Print all chat models Groq currently exposes (diagnostic / MODE=list)."""
    resp = client.models.list()
    out = [m.id for m in resp.data]
    print("ALL_MODELS:" + ",".join(out))
    return out


def main():
    client = get_groq_client()

    # Diagnostic mode: just list what models are live right now.
    if os.environ.get("MODE") == "list":
        list_models(client)
        return

    model = pick_working_model(client)
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
    
    print(f"Generating {num_articles} sourced tech article drafts (images: Pollinations AI)...")
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
            article = generate_news_article(client, topic, model=model)
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
                "review_status": "needs-review",
            })
            i += 1
        except Exception as e:
            print(f"  ERROR: {e}")
    
    summary_path = OUTPUT_DIR.parent.parent / "generation-summary.json"
    summary_path.write_text(json.dumps(generated, indent=2), encoding="utf-8")
    
    print(f"\nDone! Generated {len(generated)} unpublished drafts. Human editorial approval is required before publication.")

    # Fail loudly if we generated nothing — a silent success with zero articles
    # is how the daily pipeline broke for 17 days (retired model returned 404).
    if not generated:
        print("ERROR: generated 0 articles — failing the job so it's visible.")
        exit(1)
    
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a") as f:
            f.write("## Generated Tech News Articles\n\n")
            for g in generated:
                f.write(f"- **{g['title']}** ({g['category']})\n")

if __name__ == "__main__":
    main()
