#!/usr/bin/env python3
"""Post the latest article teaser to a Discord channel via webhook.

Discord webhooks need no bot/user OAuth — just a webhook URL. Ties into
the same teaser.py format (5-6 lines + link) and dedup registry.

Usage:
  DISCORD_WEBHOOK="https://discord.com/api/webhooks/..." \
    python scripts/discord_post.py "TEASER_TEXT"
"""
import json
import os
import sys
import urllib.request


def main():
    webhook = os.environ.get("DISCORD_WEBHOOK", "").strip()
    if not webhook:
        print("SKIP: DISCORD_WEBHOOK not set")
        return 0
    teaser = sys.argv[1] if len(sys.argv) > 1 else ""
    if not teaser:
        print("ERROR: no teaser text given")
        return 1

    payload = {
        "content": teaser[:1900],  # Discord message limit 2000; safe under
    }
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            if resp.status in (200, 204):
                print("POSTED to Discord (webhook accepted)")
                return 0
            print("Discord responded", resp.status)
            return 1
    except Exception as e:
        print("Discord error:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())