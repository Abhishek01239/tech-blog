#!/usr/bin/env python3
"""Post the latest article to Reddit as a link post, with per-slug dedup."""
import os
import sys
import json
import time
import base64
import urllib.request
import urllib.parse
import urllib.error

USER_AGENT = "linux:TechPulseBot:v1.0 (by /u/{uname})"

def get_oauth(client_id, secret, username, password):
    """Get Reddit OAuth access token via password flow."""
    auth = "Basic " + base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "password",
        "username": username,
        "password": password,
    }).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token",
        data=data,
        headers={"Authorization": auth, "User-Agent": USER_AGENT.format(uname=username)},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print("OAuth HTTP", e.code, ":", e.read().decode()[:300])
        sys.exit(1)
    if "access_token" not in body:
        print("OAuth response:", json.dumps(body))
        sys.exit(1)
    return body["access_token"]

def submit_link(token, username, subreddit, title, url):
    data = urllib.parse.urlencode({
        "sr": subreddit,
        "title": title,
        "kind": "link",
        "url": url,
        "resubmit": "true",
    }).encode()
    req = urllib.request.Request(
        "https://oauth.reddit.com/api/submit",
        data=data,
        headers={"Authorization": "Bearer " + token, "User-Agent": USER_AGENT.format(uname=username)},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())

def main():
    sub = sys.argv[1]
    title = sys.argv[2]
    url = sys.argv[3]
    username = os.environ["REDDIT_USERNAME"].strip()
    password = os.environ["REDDIT_PASSWORD"].strip()
    client_id = os.environ["REDDIT_CLIENT_ID"].strip()
    secret = os.environ["REDDIT_SECRET"].strip()

    slug = url.rstrip("/").rsplit("/", 1)[-1]
    posted_file = os.path.join(os.path.dirname(__file__), ".reddit_posted")
    if os.path.exists(posted_file) and slug in open(posted_file).read():
        print(f"Already posted {slug}, skipping")
        sys.exit(0)

    token = get_oauth(client_id, secret, username, password)
    # reddit requires a short wait, then submit
    res = submit_link(token, username, sub, title, url)
    print("Reddit response:", json.dumps(res))

    errors = res.get("json", {}).get("errors", [])
    if res.get("success") or res.get("jquery") or not errors:
        with open(posted_file, "a") as f:
            f.write(slug + "\n")
        print("SUCCESS: posted to r/" + sub)
    elif any("ALREADY_SUB" in str(e) for e in errors):
        print("Already submitted recently, skipping")
        sys.exit(0)
    else:
        print("FAILED:", errors)
        sys.exit(1)

if __name__ == "__main__":
    main()