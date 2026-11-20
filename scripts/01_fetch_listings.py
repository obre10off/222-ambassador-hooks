"""Step 1: list each account's recent posts and save the raw JSON to work/raw/.

TikTok:    ScrapeCreators  GET /v3/tiktok/profile/videos   (env SCRAPECREATORS_API_KEY)
Instagram: TikHub          GET /api/v1/instagram/v2/fetch_user_reels  (env TIKHUB_API_KEY)

Usage:  python scripts/01_fetch_listings.py [--pages 2] [--only handle1,handle2]
Run step 2 right after this one: the video CDN URLs in the listings expire within hours.
"""
import argparse
import json
import os
import sys

import requests

from common import RAW, ensure_dirs, load_accounts

SC_URL = "https://api.scrapecreators.com/v3/tiktok/profile/videos"
TIKHUB_URL = "https://api.tikhub.io/api/v1/instagram/v2/fetch_user_reels"


def need(var):
    val = os.environ.get(var)
    if not val:
        sys.exit(f"Set the {var} environment variable (see README).")
    return val


def fetch_tiktok(handle, pages, key):
    cursor = None
    for page in range(1, pages + 1):
        params = {"handle": handle, "trim": "true", "region": "US"}
        if cursor:
            params["max_cursor"] = cursor
        r = requests.get(SC_URL, params=params, headers={"x-api-key": key}, timeout=60)
        body = r.json()
        if r.status_code != 200 or not body.get("success", True):
            print(f"  ! @{handle}: {r.status_code} {body.get('message')}")
            return
        (RAW / f"{handle}_p{page}.json").write_text(json.dumps(body))
        items = body.get("aweme_list") or []
        print(f"  @{handle} page {page}: {len(items)} posts")
        cursor = body.get("max_cursor")
        if not body.get("has_more") or not cursor:
            return


def fetch_instagram(handle, key):
    r = requests.get(TIKHUB_URL, params={"username": handle},
                     headers={"Authorization": f"Bearer {key}"}, timeout=60)
    if r.status_code != 200:
        print(f"  ! IG @{handle}: {r.status_code} {r.text[:200]}")
        return
    items = ((r.json().get("data") or {}).get("data") or {}).get("items") or []
    (RAW / f"ig_{handle}.json").write_text(json.dumps({"reels": items}))
    print(f"  IG @{handle}: {len(items)} reels")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=2, help="TikTok pages of ~10 posts each")
    ap.add_argument("--only", default="", help="comma-separated handles to fetch")
    args = ap.parse_args()
    only = {h.strip() for h in args.only.split(",") if h.strip()}
    ensure_dirs()
    acc = load_accounts()
    tt = [a["handle"] for a in acc["tiktok"] if not only or a["handle"] in only]
    ig = [a["handle"] for a in acc["instagram"] if not only or a["handle"] in only]
    if tt:
        key = need("SCRAPECREATORS_API_KEY")
        for h in tt:
            fetch_tiktok(h, args.pages, key)
    if ig:
        key = need("TIKHUB_API_KEY")
        for h in ig:
            fetch_instagram(h, key)


if __name__ == "__main__":
    main()
