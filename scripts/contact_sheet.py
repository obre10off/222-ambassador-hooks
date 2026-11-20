"""Optional helper: tile the 3 frames of several posts into one image to eyeball overlay text.

Usage: python scripts/contact_sheet.py out.jpg <post_id> [<post_id> ...]
"""
import sys

from PIL import Image, ImageDraw

from common import FRAMES


def main():
    out, ids = sys.argv[1], sys.argv[2:]
    rows = []
    for vid in ids:
        files = sorted(FRAMES.glob(f"{vid}_*.jpg"))[:3]
        row = Image.new("RGB", (60 + 240 * 3, 427), "white")
        ImageDraw.Draw(row).text((5, 200), vid[-8:], fill="red")
        for k, f in enumerate(files):
            row.paste(Image.open(f).convert("RGB").resize((240, 427)), (60 + 240 * k, 0))
        rows.append(row)
    sheet = Image.new("RGB", (780 * 2, 427 * ((len(rows) + 1) // 2)), "white")
    for k, r in enumerate(rows):
        sheet.paste(r, ((k % 2) * 780, (k // 2) * 427))
    sheet.save(out, quality=80)
    print("saved", out)


if __name__ == "__main__":
    main()
