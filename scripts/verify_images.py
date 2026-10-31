#!/usr/bin/env python3
"""Verify every article has a usable, unique cover.

Rules:
  - Every post must declare an `image` in frontmatter.
  - A remote image URL (http/https) is accepted as-is.
  - A local image must exist in static/images/ and be a non-empty file.
  - Two posts may not share a local cover with identical content (--strict).

Usage:
  python scripts/verify_images.py          # scan local covers
  python scripts/verify_images.py --strict # also check every post's frontmatter

Exit code 0 = every article has a cover. Exit code 1 = something is missing
or duplicated (details printed). Safe to run anywhere (no network).
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMG_DIR = ROOT / "static" / "images"
POSTS = ROOT / "content" / "posts"


def posts():
    return sorted(POSTS.glob("*.md"))


def frontmatter_image(body: str) -> str:
    m = re.search(r"(?m)^image:\s*\"?([^\n\"]+)\"?\s*$", body)
    return m.group(1).strip() if m else ""


def local_path(img: str) -> Path:
    return IMG_DIR / img.removeprefix("/images/").split("?")[0]


def main():
    strict = "--strict" in sys.argv

    jpgs = sorted(list(IMG_DIR.glob("*.jpg")) + list(IMG_DIR.glob("*.png")))
    empty = [p.name for p in jpgs if p.stat().st_size == 0]
    if empty:
        print("EMPTY IMAGE FILES FOUND:")
        for name in empty:
            print("  - /images/" + name)
        return 1

    print(f"Scanned {len(jpgs)} local covers in static/images/")

    if not strict:
        print("Use --strict to also check every post's frontmatter.")
        return 0

    missing = []
    by_hash = {}
    for post in posts():
        body = post.read_text(encoding="utf-8")
        img = frontmatter_image(body)
        if not img:
            missing.append(f"{post.name}: (no image)")
            continue
        if img.startswith("http"):
            continue
        path = local_path(img)
        if not path.exists() or path.stat().st_size == 0:
            missing.append(f"{post.name}: {img}")
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        by_hash.setdefault(digest, []).append(post.name)

    print("\n-- strict: posts without a usable cover --")
    if missing:
        for x in missing:
            print("  ", x)
    else:
        print("   none")

    dup = {h: v for h, v in by_hash.items() if len(v) > 1}
    if dup:
        print("\n-- strict: duplicate covers shared by multiple posts --")
        for v in dup.values():
            print("   ", ", ".join(v))

    if missing or dup:
        print("\nFAILED: every article needs a unique, existing cover.")
        return 1
    print("\nALL ARTICLES HAVE A COVER ✔")
    return 0


if __name__ == "__main__":
    sys.exit(main())
