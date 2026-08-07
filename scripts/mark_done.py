#!/usr/bin/env python3
"""Dedup registry: records which article slugs were posted to which platform.

Registry lives in .marketing/<platform>.json (committed to the repo).

Usage:
  python scripts/mark_done.py check <platform> <slug>
      -> prints SKIP and exits 1 if slug already posted to platform; else exits 0
  python scripts/mark_done.py post <platform> <slug>
      -> records slug as posted to platform (returns 0 always)
  python scripts/mark_done.py list <platform>
      -> prints all posted slugs
  python scripts/mark_done.py next <platform>
      -> prints the newest content/posts/*.md whose slug is NOT yet posted to
         platform (newest-first, first unposted one); exits 0. If all articles
         are already posted, prints nothing and exits 1.
"""
import json
import os
import sys
from pathlib import Path

REGISTRY_DIR = Path(__file__).resolve().parent.parent / ".marketing"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


def registry_file(platform: str) -> Path:
    return REGISTRY_DIR / f"{platform}.json"


def load(platform: str):
    f = registry_file(platform)
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    return []


def save(platform: str, slugs):
    f = registry_file(platform)
    f.write_text(json.dumps(slugs, indent=2) + "\n", encoding="utf-8")


def slug_of(path: Path) -> str:
    return path.stem


def next_unposted(platform: str):
    """Return newest content/posts/*.md not yet posted to platform, or ''."""
    posts_dir = Path(__file__).resolve().parent.parent / "content" / "posts"
    if not posts_dir.is_dir():
        return ""
    posted = set(load(platform))
    for p in sorted(posts_dir.glob("*.md"), reverse=True):  # newest first
        if p.stem not in posted:
            return str(p)
    return ""


def main():
    action = sys.argv[1]
    platform = sys.argv[2]
    if action == "check":
        slug = sys.argv[3]
        slugs = load(platform)
        if slug in slugs:
            print(f"SKIP: {slug} already posted to {platform}")
            sys.exit(1)  # non-zero = already done, caller must stop
        sys.exit(0)      # zero = not done, caller proceeds
    elif action == "post":
        slug = sys.argv[3]
        slugs = load(platform)
        if slug not in slugs:
            slugs.append(slug)
            save(platform, slugs)
            print(f"Marked {slug} as posted to {platform}")
        sys.exit(0)
    elif action == "list":
        for s in load(platform):
            print(s)
        sys.exit(0)
    elif action == "next":
        unposted = next_unposted(platform)
        if unposted:
            print(unposted)
            sys.exit(0)
        sys.exit(1)  # everything posted already
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()