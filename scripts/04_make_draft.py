"""Step 4: join listings + OCR into work/hooks_draft.csv for manual cleanup.

Each row has ocr_0.3 / ocr_1.5 / ocr_3.0 (lines joined with ' | ') and a pre-filled hook_text
taken from the 1.5s frame (or 0.3s, or the first slide). OCR drops spaces and picks up burned-in
spoken subtitles, so edit hook_text by hand (check frames with contact_sheet.py) and fill
hook_type. Write "No text hook" as hook_type for videos with no overlay.
"""
import csv
import datetime
import glob
import json
import os

from common import DRAFT_CSV, FRAMES, NO_HOOK, OCR_JSON, RAW, city_map, instagram_items, tiktok_items

MIN_CONF = 0.6


def frame_text(ocr, name):
    lines = [x for x in ocr.get(name, []) if x[2] > MIN_CONF]
    lines.sort(key=lambda x: x[0][0][1])  # top-to-bottom
    return " | ".join(x[1] for x in lines)


def records():
    for f in sorted(glob.glob(str(RAW / "*_p*.json"))):
        handle = os.path.basename(f).rsplit("_p", 1)[0]
        for a in tiktok_items(f):
            slides = bool(a.get("image_post_info"))
            yield dict(account=handle, platform="TikTok", format="Slideshow" if slides else "Video",
                       id=a["aweme_id"], ts=a["create_time"], views=a["statistics"]["play_count"],
                       likes=a["statistics"]["digg_count"], caption=a.get("desc") or "",
                       video_url=f"https://www.tiktok.com/@{handle}/{'photo' if slides else 'video'}/{a['aweme_id']}")
    for f in sorted(glob.glob(str(RAW / "ig_*.json"))):
        handle = os.path.basename(f)[3:-5]
        for m in instagram_items(f):
            yield dict(account=handle, platform="Instagram", format="Video", id="ig_" + m["code"],
                       ts=m["taken_at"], views=m.get("play_count") or m.get("ig_play_count") or 0,
                       likes=m.get("like_count") or 0, caption=(m.get("caption") or {}).get("text", ""),
                       video_url=f"https://www.instagram.com/reel/{m['code']}/")


def main():
    ocr = json.loads(OCR_JSON.read_text())
    cities = city_map()
    cols = ["id", "account", "platform", "format", "city", "post_date", "views", "likes", "video_url",
            "ocr_0.3", "ocr_1.5", "ocr_3.0", "hook_text", "hook_type", "caption"]
    with open(DRAFT_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        for r in records():
            o = {t: frame_text(ocr, f"{r['id']}_{t}.jpg") for t in ("0.3", "1.5", "3.0", "img0")}
            draft = o["1.5"] or o["0.3"] or o["img0"] or o["3.0"]
            w.writerow(dict(
                id=r["id"], account=r["account"], platform=r["platform"], format=r["format"],
                city=cities.get(r["account"], ""),
                post_date=datetime.datetime.fromtimestamp(r["ts"], datetime.timezone.utc).strftime("%Y-%m-%d"),
                views=r["views"], likes=r["likes"], video_url=r["video_url"],
                **{"ocr_0.3": o["0.3"] or o["img0"], "ocr_1.5": o["1.5"], "ocr_3.0": o["3.0"]},
                hook_text=draft.replace(" | ", " "), hook_type="" if draft else NO_HOOK,
                caption=r["caption"].replace("\n", " ")))
    print(f"Draft written to {DRAFT_CSV}. Clean hook_text / hook_type, then run 05_build_csv.py")


if __name__ == "__main__":
    main()
