#!/usr/bin/env python3
"""Ensure every article has a valid, cached local thumbnail (16:9).

For each post in content/posts/:
  - If frontmatter already has an image whose file exists locally -> keep it.
  - Otherwise generate a deterministic SVG cover from the title/summary/tags
    into static/images/<slug>.svg and set image: /images/<slug>.svg.

Deterministic + cached on disk: never regenerated, always available,
no broken image icons, no external API needed. Remote http images are
kept as-is; the template's onError fallback guards against 404s.
"""
import hashlib
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "content" / "posts"
IMG_DIR = ROOT / "static" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)

W, H = 800, 450  # 16:9

PALETTES = [
    ("#1e3a8a", "#0ea5e9"),  # blue
    ("#7c2d12", "#f59e0b"),  # orange
    ("#0f172a", "#8b5cf6"),  # violet
    ("#14532d", "#22c55e"),  # green
    ("#4c0519", "#f43f5e"),  # rose
    ("#1e1b4b", "#6366f1"),  # indigo
    ("#042f2e", "#2dd4bf"),  # teal
    ("#3b0764", "#d946ef"),  # fuchsia
]


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


def summary_of(fm: dict, body: str) -> str:
    text = fm.get("description", "")
    if not text:
        text = re.sub(r"\s+", " ", body.replace("**", "").replace("##", ""))
        text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    return text.strip()[:120]


def tags_of(fm: dict):
    t = fm.get("tags", "")
    if isinstance(t, str):
        t = [x.strip().strip('"') for x in t.replace("[", "").replace("]", "").split(",") if x.strip()]
    return [str(x) for x in t][:4] or ["tech"]


def make_svg(slug, title, summary, tags):
    h = int(hashlib.sha256((slug + "|" + "|".join(tags)).encode()).hexdigest(), 16)
    c1, c2 = PALETTES[h % len(PALETTES)]

    words = title.split()
    wrapped, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 > 28:
            wrapped.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        wrapped.append(cur)

    title_lines = "\n".join(
        f'<text x="60" y="{140 + i * 60}" font-family="Inter,Arial,sans-serif" '
        f'font-size="44" font-weight="700" fill="#ffffff">{escape(line)}</text>'
        for i, line in enumerate(wrapped[:3])
    )
    tag_text = "  ".join(t.upper() for t in tags[:4])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <linearGradient id="g" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}"/>
      <stop offset="100%" stop-color="{c2}"/>
    </linearGradient>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#g)"/>
  <circle cx="{W - 120}" cy="80" r="200" fill="#ffffff" opacity="0.08"/>
  <circle cx="100" cy="{H - 60}" r="150" fill="#000000" opacity="0.12"/>
  <text x="60" y="70" font-family="Inter,Arial,sans-serif" font-size="22" font-weight="700" fill="#ffffff" opacity="0.85">TechPulse</text>
  {title_lines}
  <text x="60" y="330" font-family="Inter,Arial,sans-serif" font-size="24" fill="#ffffff" opacity="0.75">{escape(summary)}</text>
  <text x="60" y="385" font-family="Inter,Arial,sans-serif" font-size="22" font-weight="700" fill="#22d3ee">{escape(tag_text)}</text>
</svg>"""


def local_file_exists(image: str) -> bool:
    """True if image is remote (JS guards it) or exists in static/."""
    if not image or image.startswith("http"):
        return bool(image)
    rel = image.lstrip("/")
    return (ROOT / "static" / rel).exists()


def main():
    if not POSTS.exists():
        print("No posts directory")
        return
    changed = []
    for post in sorted(POSTS.glob("*.md")):
        fm = parse_post(post)
        body = post.read_text(encoding="utf-8")
        image = fm.get("image", "")
        if local_file_exists(image):
            continue

        slug = slug_of(post)
        cover = IMG_DIR / f"{slug}.svg"
        if not cover.exists():
            cover.write_text(
                make_svg(slug, fm.get("title", slug), summary_of(fm, body), tags_of(fm)),
                encoding="utf-8",
            )
        new_image = f"/images/{cover.name}"
        if image != new_image:
            post.write_text(
                re.sub(r"(?m)^image:.*$", f'image: "{new_image}"', body),
                encoding="utf-8",
            )
            changed.append(f"{post.name}: {image or '(none)'} -> {new_image}")

    if changed:
        print("FIXED:\n" + "\n".join(changed))
    else:
        print("All posts already have valid images")


if __name__ == "__main__":
    main()