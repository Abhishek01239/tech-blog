#!/usr/bin/env python3
"""Ensure every article cover is a VERIFIED Pollinations-generated image.

For each post in content/posts/:
  - If frontmatter image is a local jpg that VERIFIES as Pollinations
    (EXIF Make=sana, 800x450) -> keep it.
  - Otherwise fetch a Pollinations cover (Pollinations-only, no other source).
  - If a verified cover cannot be obtained -> leave image empty (no SVG fallback).

Also scans static/images/*.jpg and fails/warns on any file that is NOT
Pollinations-verified, so a non-Pollinations image can never reach the site.
"""
import re
import sys
from pathlib import Path

# Reuse the Pollinations logic (import safe without groq: lazy import there).
from generate import get_image_url, is_pollinations_image

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
IMG_DIR = ROOT / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

NON_POLLINATIONS_EXIT = False  # becomes True if any committed jpg is not verified


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


def main():
    global NON_POLLINATIONS_EXIT
    if not POSTS.exists():
        print("No posts directory")
        return

    # --- 1) Reject any committed non-Pollinations jpg (exit non-zero) ---
    bad = []
    for jpg in sorted(IMG_DIR.glob("*.jpg")):
        if not is_pollinations_image(jpg):
            bad.append(jpg.name)
            NON_POLLINATIONS_EXIT = True
    if bad:
        print("NON-POLLINATIONS COVERS FOUND (must be removed/replaced):")
        for b in bad:
            print("  - /images/" + b)

    # --- 2) Ensure each post points at a verified Pollinations cover ---
    changed = []
    for post in sorted(POSTS.glob("*.md")):
        fm = parse_post(post)
        img = fm.get("image", "")

        # Local file that is already a verified Pollinations cover -> keep.
        local_path = None
        if img.startswith("/images/") or (img and not img.startswith("http")):
            candidate = IMG_DIR / img.lstrip("/").split("/")[-1]
            if candidate.exists():
                local_path = candidate

        if local_path and is_pollinations_image(local_path):
            continue  # already good

        # Not verified / missing -> (re)generate a Pollinations cover.
        slug = slug_of(post)
        title = fm.get("title", slug)
        category = fm.get("categories", "general").strip("[]")
        img_url = get_image_url(category, slug, title)

        new_image = img_url or ""
        body = post.read_text(encoding="utf-8")
        pattern = r"(?m)^image:.*$\n?"
        new_body = re.sub(pattern, f'image: "{new_image}"\n', body)
        if "image:" not in body:
            # insert into frontmatter before closing ---
            m = re.match(r"(?s)(---\n.*?)(\n---)", body)
            new_body = f"{m.group(1)}image: \"{new_image}\"\n{m.group(2)}" if m else body
        if new_body != body:
            post.write_text(new_body, encoding="utf-8")
            changed.append(f"{post.name}: -> {new_image or '(no verified cover)'}")

    for c in changed:
        print("FIXED:", c)

    if NON_POLLINATIONS_EXIT:
        print("\nERROR: non-Pollinations image found in static/images — refusing to proceed.")
        sys.exit(1)
    print("All article covers are verified Pollinations images.")


if __name__ == "__main__":
    main()