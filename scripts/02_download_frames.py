"""Step 2: download each post and grab frames at 0.3s, 1.5s and 3s (first 2 slides for slideshows).

Needs curl and ffmpeg on PATH. Output: work/vids/, work/frames/<id>_<t>.jpg
(Instagram ids are prefixed with ig_). Safe to rerun: posts that already have frames are skipped.
"""
import glob
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

from common import FRAMES, FRAME_TIMES, RAW, VIDS, ensure_dirs, instagram_items, tiktok_items

UA = "Mozilla/5.0"


def curl(url, out):
    subprocess.run(["curl", "-sL", "-m", "90", "-A", UA, "-o", str(out), url], check=False)
    return out.exists() and out.stat().st_size > 2000


def frames_from_video(vid, out):
    for t in FRAME_TIMES:
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", t, "-i", str(out),
                        "-frames:v", "1", "-vf", "scale=480:-2", str(FRAMES / f"{vid}_{t}.jpg")], check=False)


def tiktok_job(a):
    vid = a["aweme_id"]
    if glob.glob(str(FRAMES / f"{vid}_*.jpg")):
        return
    ipi = a.get("image_post_info")
    if ipi:  # photo slideshow: the first slide is what viewers see first
        for i, im in enumerate((ipi.get("images") or [])[:2]):
            urls = (im.get("display_image") or im.get("owner_watermark_image") or {}).get("url_list", [])
            out = VIDS / f"{vid}_img{i}"
            if any(curl(u, out) for u in urls):
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(out), "-vf", "scale=540:-2",
                                str(FRAMES / f"{vid}_img{i}.jpg")], check=False)
        return
    out = VIDS / f"{vid}.mp4"
    if any(curl(u, out) for u in a["video"]["play_addr"]["url_list"]):
        frames_from_video(vid, out)
    else:
        print("download failed:", vid)


def instagram_job(m):
    vid = "ig_" + m["code"]
    if glob.glob(str(FRAMES / f"{vid}_*.jpg")):
        return
    versions = m.get("video_versions") or []
    out = VIDS / f"{vid}.mp4"
    if versions and curl(versions[0]["url"], out):
        frames_from_video(vid, out)
    else:
        print("download failed:", vid)


def main():
    ensure_dirs()
    jobs = []
    for f in sorted(glob.glob(str(RAW / "*_p*.json"))):
        jobs += [(tiktok_job, a) for a in tiktok_items(f)]
    for f in sorted(glob.glob(str(RAW / "ig_*.json"))):
        jobs += [(instagram_job, m) for m in instagram_items(f)]
    with ThreadPoolExecutor(int(os.environ.get("HOOKS_THREADS", 8))) as ex:
        list(ex.map(lambda j: j[0](j[1]), jobs))
    print(f"{len(jobs)} posts processed; frames in {FRAMES}")


if __name__ == "__main__":
    main()
