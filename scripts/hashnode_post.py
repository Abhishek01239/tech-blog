#!/usr/bin/env python3
"""Cross-post the latest article to a Hashnode blog story.

Uses Hashnode's free GraphQL API (publishPost) with a Personal Access Token.
Auth via Authorization header. Sets the canonical URL back to the site so
traffic points to the original post.

Usage:
  HAS=HASHNODE_TOKEN PUB=publicationId    python scripts/hashnode_post.py <post.md>

Secrets:
  HASHNODE_ACCESS_TOKEN   your Hashnode PAT (Settings -> Developer -> Access Tokens)
  HASHNODE_PUBLICATION_ID the blog's publication/graph id (publicationId)
"""
import os
import re
import sys
import json
import urllib.request

API = "https://gql.hashnode.com"


def parse_frontmatter(path):
    raw = open(path, encoding="utf-8").read()
    fm, body = {}, raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) == 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip().strip('"')
            body = parts[2]
    return fm, body


def main():
    token = os.environ.get("HASHNODE_ACCESS_TOKEN", "").strip()
    pub = os.environ.get("HASHNODE_PUBLICATION", "").strip()
    if not token:
        print("SKIP: HASHNODE_ACCESS_TOKEN not set")
        return 0
    if not pub:
        print("ERROR: HASHNODE_PUBLICATION not set")
        return 1

    post = sys.argv[1] if len(sys.argv) > 1 else None
    if not post:
        print("ERROR: no post path given")
        return 1
    fm, body = parse_frontmatter(post)
    title = fm.get("title", "")
    slug = os.path.basename(post).replace(".md", "")
    canonical = f"https://tech-blog-eight-blush.vercel.app/posts/{slug}/"
    if not title:
        print("ERROR: empty title")
        return 1

    query = """
    mutation($input: PublishPostInput!, $pubId: String) {
      publishPost(input: $input, publicationId: $pubId) {
        post {
          id title url canonicalUrl
        }
      }
    }
    """
    variables = {
        "pubId": pub,
        "input": {
            "title": title,
            "contentMarkdown": body,
            "canonicalUrl": canonical,
            "tags": [],
        },
    }
    req = urllib.request.Request(
        API,
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={
            "Authorization": token,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        if "errors" in data:
            print("Hashnode errors:", json.dumps(data["errors"]))
            return 1
        post = data.get("data", {}).get("publishPost", {}).get("post", {})
        if post.get("url"):
            print("POSTED:", post["url"])
            return 0
        print("Unexpected response:", json.dumps(data))
        return 1
    except Exception as e:
        print("Hashnode error:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())