#!/usr/bin/env python3
"""Post an article teaser to Bluesky via the AT Protocol.

Auth: a Bluesky account's handle + an App Password (no OAuth, no approval).
  settings -> App Passwords -> Add app password -> paste as BSKY_PASSWORD.

Secrets: BSKY_HANDLE (e.g. alice.bsky.social), BSKY_PASSWORD, optional BSKY_API (default bsky.social).

Usage: python scripts/bluesky_post.py "<teaser>" ["<image_path_or_url>"]
  - teaser is the multi-line text from teaser.py (title / excerpt / "Read more -> url").
  - image (optional) is the cover; when provided it is uploaded as a real
    embedded photo (not just the URL's link-card preview).

Post format:  <title>

              <article url>
  i.e. the title, a single blank line, then the raw link — plus the cover photo.

Exit:  0 on success, non-zero on failure.
"""
import json
import os
import re
import sys
import mimetypes
import urllib.request
import urllib.error
from datetime import datetime, timezone

API = os.environ.get("BSKY_API", "https://bsky.social")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

MAX = 300  # Bluesky hard cap per post


def fetch(url, payload=None, data=None, headers=None, method="POST"):
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json", "User-Agent": UA,
                 **(headers or {})},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def upload_blob(jwt, image):
    """Upload an image (local path or URL) and return the blob ref."""
    if image.startswith("http://") or image.startswith("https://"):
        req = urllib.request.Request(image, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        content_type = r.headers.get("Content-Type", "image/jpeg")
    else:
        with open(image, "rb") as f:
            data = f.read()
        content_type = mimetypes.guess_type(image)[0] or "image/jpeg"
    status, body = fetch(
        f"{API}/xrpc/com.atproto.repo.uploadBlob",
        data=data,
        headers={"Authorization": f"Bearer {jwt}", "Content-Type": content_type},
    )
    if status != 200:
        raise RuntimeError(f"uploadBlob failed ({status}): {body}")
    return body["blob"]


def build_facets(text):
    """Make a link facet for every http(s) URL so it renders clickable."""
    facets = []
    for m in re.finditer(r"https?://\S+", text):
        start_b = len(text[:m.start()].encode("utf-8"))
        end_b = len(text[:m.end()].encode("utf-8"))
        facets.append({
            "index": {"byteStart": start_b, "byteEnd": end_b},
            "features": [{"$type": "app.bsky.richtext.facet#link",
                          "uri": m.group(0)}],
        })
    return facets


def compose(teaser):
    """From the teaser, extract title + article URL -> 'title\\n\\nurl'."""
    lines = teaser.splitlines()
    title = lines[0].strip() if lines else ""
    link = ""
    for line in lines:
        m = re.search(r"https?://\S+", line)
        if m:
            link = m.group(0).rstrip(").,")
            break
    # Keep the link whole; trim the title if we're over budget.
    text = f"{title}\n\n{link}".strip()
    if len(text) > MAX:
        budget = MAX - len(link) - 2
        if len(title) > budget:
            title = title[:budget - 1].rsplit(" ", 1)[0] + "…"
        text = f"{title}\n\n{link}".strip()
    return text[:MAX]


def main():
    teaser = sys.argv[1] if len(sys.argv) > 1 else ""
    image = sys.argv[2] if len(sys.argv) > 2 else ""
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

    # 2. compose text: title, blank line, raw link (+ clickable facet)
    text = compose(teaser)
    facets = build_facets(text)
    record = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    if facets:
        record["facets"] = facets

    # 3. optionally embed the cover photo as a real image
    if image and os.path.exists(image) or (image and image.startswith("http")):
        try:
            blob = upload_blob(jwt, image)
            record["embed"] = {
                "$type": "app.bsky.embed.images",
                "images": [{"alt": (teaser.splitlines()[0] if teaser else "cover"),
                            "image": blob}],
            }
        except Exception as e:
            print(f"warn: image embed failed, posting text only: {e}")

    # 4. create the post
    status, body = fetch(
        f"{API}/xrpc/com.atproto.repo.createRecord",
        {"repo": did, "collection": "app.bsky.feed.post", "record": record},
        headers={"Authorization": f"Bearer {jwt}"},
    )
    if status == 200:
        print(f"posted: {body.get('uri', '')}")
        sys.exit(0)
    else:
        print(f"error: createRecord failed ({status}): {body}")
        sys.exit(1)


if __name__ == "__main__":
    main()
