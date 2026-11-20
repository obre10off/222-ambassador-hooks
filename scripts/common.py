"""Shared paths and helpers for the hook pipeline."""
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
WORK = Path(os.environ.get("HOOKS_WORKDIR", REPO / "work"))
RAW = WORK / "raw"
VIDS = WORK / "vids"
FRAMES = WORK / "frames"
OCR_JSON = WORK / "ocr.json"
DRAFT_CSV = WORK / "hooks_draft.csv"
DATA_CSV = REPO / "data" / "222_hooks.csv"
TEMPLATES_JSON = REPO / "data" / "hook_templates.json"
ACCOUNTS_JSON = Path(os.environ.get("HOOKS_ACCOUNTS", REPO / "scripts" / "accounts.json"))

# Seconds into each video where a frame is grabbed for OCR.
FRAME_TIMES = ["0.3", "1.5", "3.0"]
NO_HOOK = "No text hook"


def load_accounts():
    return json.loads(ACCOUNTS_JSON.read_text())


def city_map():
    acc = load_accounts()
    return {a["handle"]: a.get("city", "") for a in acc["tiktok"] + acc["instagram"]}


def tiktok_items(path):
    """aweme_list from a saved TikTok listing page."""
    return json.loads(Path(path).read_text()).get("aweme_list") or []


def instagram_items(path):
    """Reel media objects from a saved Instagram listing (handles a few response shapes)."""
    body = json.loads(Path(path).read_text())
    reels = (body.get("reels") or (body.get("output") or {}).get("reels")
             or ((body.get("data") or {}).get("data") or {}).get("items") or [])
    return [r.get("media") or r for r in reels]


def ensure_dirs():
    for d in (RAW, VIDS, FRAMES):
        d.mkdir(parents=True, exist_ok=True)
