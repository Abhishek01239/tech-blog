#!/usr/bin/env python3
"""Ensure every article has a cover image.

For each post in content/posts/:
  - Keep it if frontmatter image is a remote URL (e.g. Cloudinary) or points at
    a local file that exists in static/images/.
  - Otherwise generate a Pollinations cover into static/images/<slug>.jpg.

Editors' hand-made or AI-generated covers are never replaced, whatever their
provenance — only genuinely missing covers are backfilled.
"""
import re
import sys
from pathlib import Path

# Reuse the Pollinations logic (import safe without groq: lazy import there).
from generate import get_image_url

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
IMG_DIR = ROOT / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)


def parse_post(path: Path):
    raw = path.read_text(encoding="utf-8")
    fm = {}
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
    return fm


def slug_of(path: Path) -> str:
    name = path.stem
    m = re.match(r"^\d{4}-\d{2}-\d{2}-(.+)$", name)
    return m.group(1) if m else name


def cover_exists(img: str) -> bool:
    if not img:
        return False
    if img.startswith("http"):
        return True
    candidate = IMG_DIR / img.removeprefix("/images/").split("?")[0]
    return candidate.exists()


def main():
    changed = []
    for post in sorted(POSTS.glob("*.md")):
        fm = parse_post(post)
        img = fm.get("image", "")
        if cover_exists(img):
            continue

        slug = slug_of(post)
        title = fm.get("title", slug)
        category = fm.get("categories", "general").strip("[]")
        new_image = get_image_url(category, slug, title) or ""

        body = post.read_text(encoding="utf-8")
        pattern = r"(?m)^image:.*$\n?"
        new_body = re.sub(pattern, f'image: "{new_image}"\n', body)
        if "image:" not in body:
            m = re.match(r"(?s)(---\n.*?)(\n---)", body)
            new_body = f"{m.group(1)}image: \"{new_image}\"\n{m.group(2)}" if m else body
        if new_body != body:
            post.write_text(new_body, encoding="utf-8")
            changed.append(f"{post.name}: -> {new_image or '(no cover generated)'}")

    for c in changed:
        print("FIXED:", c)

    print(f"Checked {len(list(POSTS.glob('*.md')))} posts; {len(changed)} updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
