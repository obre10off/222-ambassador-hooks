"""Step 5: turn the hand-cleaned draft into the published dataset data/222_hooks.csv.

Usage: python scripts/05_build_csv.py [path/to/hooks_draft.csv]
"""
import csv
import re
import sys

from common import DATA_CSV, DRAFT_CSV, NO_HOOK

COLS = ["account", "platform", "format", "city", "post_date", "views", "likes", "hook_text", "hook_type",
        "hook_mentions_222", "caption_mentions_222", "video_url", "caption"]


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else DRAFT_CSV
    rows = list(csv.DictReader(open(src, newline="")))
    missing = [r["id"] for r in rows if not r["hook_type"].strip()]
    if missing:
        sys.exit(f"{len(missing)} rows still have no hook_type, e.g. {missing[:5]}")
    out = []
    for r in rows:
        hook = r["hook_text"].strip()
        out.append(dict(
            account="@" + r["account"].lstrip("@"), platform=r["platform"], format=r["format"], city=r["city"],
            post_date=r["post_date"], views=int(r["views"] or 0), likes=int(r["likes"] or 0),
            hook_text=hook, hook_type=r["hook_type"].strip(),
            hook_mentions_222="yes" if "222" in hook and r["hook_type"] != NO_HOOK else "no",
            caption_mentions_222="yes" if re.search(r"222", r["caption"] or "") else "no",
            video_url=r["video_url"], caption=r["caption"]))
    with open(DATA_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        w.writerows(out)
    print(f"{len(out)} rows -> {DATA_CSV}")


if __name__ == "__main__":
    main()
