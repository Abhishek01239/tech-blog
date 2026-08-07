#!/usr/bin/env python3
"""Cross-post the latest article to Dev.to as a published article."""
import os
import sys
import json
import urllib.request
import urllib.error

API = "https://dev.to/api/articles"

def main():
    key = os.environ["DEVTO_API_KEY"].strip()
    markdown_path = sys.argv[1]

    with open(markdown_path, encoding="utf-8") as f:
        raw = f.read()

    # Parse frontmatter
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

    title = fm.get("title", "TechPulse daily news")
    tags = fm.get("tags", "technology").replace("[\"", ",").replace("\"]", "").replace("\"", "").replace("[", "").replace("]", "")
    raw_list = [t.strip() for t in tags.split(",") if t.strip()]
    # Dev.to requires alphanumeric-only tags (no spaces, no punctuation), max 4.
    sanitized = []
    for t in raw_list:
        clean = "".join(ch for ch in t.lower() if ch.isalnum())
        if clean and len(clean) <= 32 and clean not in sanitized:
            sanitized.append(clean)
    if not sanitized:
        sanitized = ["technology"]  # always-valid fallback tag
    tags_list = sanitized[:4]
    canonical = fm.get("canonical_url", "")

    payload = {
        "article": {
            "title": title,
            "body_markdown": body,
            "published": True,
            "tags": tags_list or ["technology"],
        }
    }
    if canonical:
        payload["article"]["canonical_url"] = canonical

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        API,
        data=data,
        headers={"api-key": key, "Content-Type": "application/json", "User-Agent": "TechPulseBot/1.0"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read())
            print("Dev.to SUCCESS:", res.get("url") or res.get("id"))
    except urllib.error.HTTPError as e:
        print("Dev.to HTTP", e.code, ":", e.read().decode()[:300])
        sys.exit(1)

if __name__ == "__main__":
    main()