#!/usr/bin/env python3
"""Cross-post an article to Hashnode via GraphQL publishPost.

Secrets:
  HASHNODE_ACCESS_TOKEN - personal access token (Account -> Security -> Developer)
  HASHNODE_PUBLICATION - blog publication id (the slug after hashnode.com/)

Usage: python scripts/hashnode_post.py "<post.md>"
Exit:  0 on success, non-zero on failure.
"""
import json
import os
import re
import sys
from pathlib import Path
import urllib.request
import urllib.error

API = "https://gql.hashnode.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"


def gql(query, variables, token):
    payload = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": UA,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def parse_fm(md: Path):
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
    return fm, body


def main():
    md = Path(sys.argv[1])
    token = os.environ.get("HASHNODE_ACCESS_TOKEN", "").strip()
    pub = os.environ.get("HASHNODE_PUBLICATION", "").strip()
    if not token or not pub:
        print("error: HASHNODE_ACCESS_TOKEN / HASHNODE_PUBLICATION not set")
        sys.exit(1)
    fm, body = parse_fm(md)
    title = fm.get("title", "TechPulse daily news")
    slug = md.stem
    canonical = f"https://tech-blog-eight-blush.vercel.app/posts/{slug}/"

    query = """
    mutation PublishPost($input: PublishPostInput!) {
      publishPost(input: $input) {
        post { title url slug }
      }
    }
    """
    var = {
        "input": {
            "title": title,
            "publicationId": pub,
            "contentMarkdown": body,
            "isRepublished": True,
            "originalArticleURL": canonical,
            "tags": [],
        }
    }
    status, res = gql(query, var, token)
    if status != 200:
        print(f"error: gql HTTP {status}: {res}")
        sys.exit(1)
    err = res.get("errors")
    if err:
        print("error:", json.dumps(err))
        sys.exit(1)
    post = res.get("data", {}).get("publishPost", {})
    url = post.get("url") or ""
    print(f"HASHNODE SUCCESS: {url}")
    sys.exit(0)


if __name__ == "__main__":
    main()