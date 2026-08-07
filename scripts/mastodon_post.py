#!/usr/bin/env python3
"""Post an article teaser to Mastodon via the account's access token.

Auth: a Mastodon account token. Create it at your instance:
  Settings -> Development -> New application -> scopes 'write:statuses' -> submit
  -> copy the Access Token -> paste as MASTODON_TOKEN.

Secrets: MASTODON_INSTANCE (e.g. https://techhub.social, no trailing slash),
         MASTODON_TOKEN, optional MASTODON_VISIBILITY (default 'public').

Usage: python scripts/mastodon_post.py "<teaser>"
Exit:  0 on success, non-zero on failure.
"""
import json
import os
import sys
import urllib.request
import urllib.error


def get_auth():
    instance = os.environ.get("MASTODON_INSTANCE", "").rstrip("/")
    token = os.environ.get("MASTODON_TOKEN", "")
    if not instance or not token:
        print("error: MASTODON_INSTANCE / MASTODON_TOKEN not set")
        sys.exit(1)
    return instance, token


def main():
    teaser = sys.argv[1] if len(sys.argv) > 1 else ""
    if not teaser:
        print("error: no teaser provided")
        sys.exit(1)
    instance, token = get_auth()
    status = os.environ.get("MASTODON_VISIBILITY", "public")

    payload = json.dumps(
        {"status": teaser[:500], "visibility": status}
    ).encode()
    req = urllib.request.Request(
        f"{instance}/api/v1/statuses",
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.loads(r.read().decode())
            url = body.get("url", "")
            print(f"posted: {url}")
            sys.exit(0)
    except urllib.error.HTTPError as e:
        print(f"error: {e.code} {e.read().decode()[:300]}")
        sys.exit(1)
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()