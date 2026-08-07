#!/usr/bin/env python3
"""Backfill every article's cover with Pollinations AI.

Deletes each post's cached image then re-downloads via generate.get_image_url
(which tries Pollinations 3x, then Unsplash, then falls back to SVG). Prints
source used per article. Safe to re-run.
"""
import importlib.util
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent  # tech-blog/

spec = importlib.util.spec_from_file_location("gen", ROOT / "scripts" / "generate.py")
g = importlib.util.module_from_spec(spec)
sys.modules["groq"] = type("G", (), {"Groq": lambda **k: None})
spec.loader.exec_module(g)

posts_dir = ROOT / "content" / "posts"
static_dir = ROOT / "static" / "images"


def parse(md: pathlib.Path):
    raw = md.read_text(encoding="utf-8")
    fm = {}
    if raw.startswith("---"):
        for line in raw.split("---", 2)[1].strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip('"')
    return fm


def category_of(fm):
    c = fm.get("categories", "").replace("[", "").replace("]", "").replace('"', "").strip()
    if not c:
        c = fm.get("category", "general")
    return (c.split(",")[0].lower().strip() or "general")


ok, fails = 0, 0
for m in sorted(posts_dir.glob("*.md")):
    name = m.stem
    fm = parse(m)
    title = fm.get("title", name.replace("-", " ").title())
    img_name = fm.get("image", "").split("/")[-1] or f"{name}.jpg"
    img_file = static_dir / img_name

    if img_file.exists():
        for _ in range(3):
            try:
                img_file.unlink()
                break
            except PermissionError:
                time.sleep(1)

    t0 = time.time()
    g.get_image_url(category_of(fm), img_name[:-4], title)
    dt = round(time.time() - t0, 1)

    if img_file.exists():
        from PIL import Image
        try:
            maker = Image.open(img_file).getexif().get(271) or "none"
        except Exception:
            maker = "?"
        src = "POLLINATIONS" if "sana" in str(maker).lower() else "UNSPLASH/other"
        print(f"{name:40s} {dt:6.1f}s  {src}  maker={maker}", flush=True)
        ok += 1 if "POLLINATIONS" in src else 0
    else:
        print(f"{name:40s} {dt:6.1f}s  FALLBACK (no file)", flush=True)
        fails += 1

print(f"\nDONE. pollinations={ok} fallback/fails={fails}")