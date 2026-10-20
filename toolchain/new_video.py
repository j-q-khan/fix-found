"""Create a video folder with its meta.json, and give an intro its Fix Found number.

usage:
  python toolchain/new_video.py intro   "<tool name or owner/repo>"   -> tools/<slug>/intro-youtube and intro-tiktok
  python toolchain/new_video.py howto   "<tool name or owner/repo>"   -> tools/<slug>/howto-youtube
  python toolchain/new_video.py compare "<category>"                  -> compare/<slug>/compare-youtube and compare-tiktok

Intros take the next free number, stored on the tool in index.json; the how-to reuses the tool's number.
Prints each folder and the render file name. The name needs the tool's "problem" line in index.json, so set it first.
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent.parent
MAX = {("intro", "16:9"): 125, ("intro", "9:16"): 65, ("howto", "16:9"): 485, ("compare", "16:9"): 245, ("compare", "9:16"): 65}
FORMATS = {"intro": ["16:9", "9:16"], "howto": ["16:9"], "compare": ["16:9", "9:16"]}
PLATFORM = {"16:9": "youtube", "9:16": "tiktok"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main(kind, what):
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    if kind == "compare":
        cat = next((c for c in index["categories"] if c["category"].lower() == what.lower()), None)
        if not cat:
            sys.exit(f"no category '{what}' in index.json")
        base, title, number, problem = ROOT / "compare" / slug(cat["category"]), cat["category"], None, cat.get("problem", "")
    else:
        tool = next((t for t in index["tools"] if what.lower() in (t["name"].lower(), t["repo"].lower())), None)
        if not tool:
            sys.exit(f"no tool '{what}' in index.json")
        if kind == "intro" and not tool.get("number"):
            tool["number"] = max([t.get("number") or 0 for t in index["tools"]]) + 1
            (ROOT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        base, title, number, problem = ROOT / "tools" / slug(tool["name"]), tool["name"], tool.get("number"), tool.get("problem", "")
    for fmt in FORMATS[kind]:
        d = base / f"{kind}-{PLATFORM[fmt]}"
        d.mkdir(parents=True, exist_ok=True)
        meta = {"kind": kind, "format": fmt, "title": title, "number": number, "max_seconds": MAX[(kind, fmt)]}
        (d / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        label = {"intro": "", "howto": "How to use ", "compare": "Compared "}[kind]
        name = f"Fix Found {number:03} - " if number else "Fix Found - "
        shown = {"youtube": "YouTube", "tiktok": "TikTok"}[PLATFORM[fmt]]
        name += f"{label}{problem.rstrip('?.!') + ' - ' if problem else ''}{title} ({shown}).mp4"
        name = re.sub(r'[<>:"/\\|?*]', "", name)   # Windows forbids these in file names
        print(f"{d.relative_to(ROOT)}  ->  renders/{name}")
    if not problem:
        print("note: no 'problem' line yet; set it in index.json and re-run to get the final file name")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
