#!/usr/bin/env python3
"""Build a social-media teaser (~5 lines) from an article: title + excerpt + link.

Usage: python scripts/teaser.py <post.md>
Output: plain-text teaser like:
  <title>
  <first paragraph(s), trimmed to ~400 chars>
  Read more → https://...
"""
import re
import sys
from pathlib import Path

MAX_CHARS = 400

def extract(md: Path):
    raw = md.read_text(encoding="utf-8")
    fm = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            body = parts[2].strip()

    title = fm.get("title", "")
    # First body paragraph(s): take everything up to the first ## heading
    excerpt = body.split("##")[0].strip()
    # Collapse blank lines and markdown links
    excerpt = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", excerpt)
    excerpt = re.sub(r"\*\*([^*]+)\*\*", r"\1", excerpt)
    excerpt = re.sub(r"\n{2,}", " ", excerpt)
    excerpt = excerpt.strip()
    if len(excerpt) > MAX_CHARS:
        excerpt = excerpt[:MAX_CHARS].rsplit(" ", 1)[0] + "…"
    return title, excerpt

if __name__ == "__main__":
    md = Path(sys.argv[1])
    slug = md.stem
    title, excerpt = extract(md)
    url = f"https://tech-blog-eight-blush.vercel.app/posts/{slug}/"
    lines = [title, "", excerpt, "", f"Read more → {url}"]
    print("\n".join(l for l in lines if l))