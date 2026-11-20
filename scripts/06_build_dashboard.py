"""Step 6: embed data/222_hooks.csv and data/hook_templates.json into a single self-contained
index.html (no network requests, opens by double-click, works on GitHub Pages).

Usage: python scripts/06_build_dashboard.py [output.html]
"""
import csv
import json
import sys

from common import DATA_CSV, REPO, TEMPLATES_JSON

TEMPLATE = REPO / "scripts" / "dashboard_template.html"


def safe_json(obj):
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else REPO / "index.html"
    rows = list(csv.DictReader(open(DATA_CSV, newline="")))
    for r in rows:
        r["views"], r["likes"] = int(r["views"]), int(r["likes"])
    tpls = [[t["template"], t["pattern"], t["proof_views"]] for t in json.loads(TEMPLATES_JSON.read_text())]
    html = TEMPLATE.read_text().replace("__DATA__", safe_json(rows)).replace("__TEMPLATES__", safe_json(tpls))
    open(out, "w").write(html)
    print(f"{len(rows)} hooks -> {out}")


if __name__ == "__main__":
    main()
