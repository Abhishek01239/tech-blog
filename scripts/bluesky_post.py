#!/usr/bin/env python3
"""Post an article teaser to Bluesky via the AT Protocol.

Auth: a Bluesky account's handle + an App Password (no OAuth, no approval).
  settings -> App Passwords -> Add app password -> paste as BSKY_PASSWORD.

Secrets: BSKY_HANDLE (e.g. alice.bsky.social), BSKY_PASSWORD, optional BSKY_API (default bsky.social).

Usage: python scripts/bluesky_post.py "<teaser>"
Exit:  0 on success, non-zero on failure.
"""
import json
import os
import sys
import urllib.request
import urllib.error

API = os.environ.get("BSKY_API", "https://bsky.social")


def fetch(url, payload, headers=None, method="POST"):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def main():
    teaser = sys.argv[1] if len(sys.argv) > 1 else ""
    if not teaser:
        print("error: no teaser provided")
        sys.exit(1)
    handle = os.environ.get("BSKY_HANDLE")
    password = os.environ.get("BSKY_PASSWORD")
    if not handle or not password:
        print("error: BSKY_HANDLE / BSKY_PASSWORD not set")
        sys.exit(1)

    # 1. create a session -> jwt
    status, body = fetch(
        f"{API}/xrpc/com.atproto.server.createSession",
        {"identifier": handle, "password": password},
    )
    if status != 200:
        print(f"error: createSession failed ({status}): {body}")
        sys.exit(1)
    jwt = body["accessJwt"]
    did = body.get("did", handle)

    # 2. create post record. Bluesky cap = 300 chars; compose title + link so
    #    the URL (the whole point) always survives truncation.
    lines = teaser.splitlines()
    title = lines[0] if lines else ""
    link = next((l for l in lines if l.startswith("Read more")), "")
    # keep link, trim title to leave room for it
    budget = 300 - len(link) - 3
    if len(title) > budget:
        title = title[: budget - 1].rsplit(" ", 1)[0] + "…"
    text = f"{title}\n\n{link}".strip()
    record = {
        "$type": "app.bsky.feed.post",
        "text": text[:300],
        "createdAt": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    payload = {
        "repo": did,
        "collection": "app.bsky.feed.post",
        "record": record,
    }
    status, body = fetch(
        f"{API}/xrpc/com.atproto.repo.createRecord",
        payload,
        headers={"Authorization": f"Bearer {jwt}"},
    )
    if status == 200:
        uri = body.get("uri", "")
        print(f"posted: {uri}")
        sys.exit(0)
    else:
        print(f"error: createRecord failed ({status}): {body}")
        sys.exit(1)


if __name__ == "__main__":
    main()