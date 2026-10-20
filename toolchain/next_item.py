"""Pick the next video to make, claim it in index.json, and print it as JSON (or NOTHING LEFT).

usage: python toolchain/next_item.py [--peek]      (--peek shows the pick without claiming it)

Rules:
- Intros follow INDEX.md order: tools listed by the most jobs first.
- About every Nth video (config production.compare_every) is a comparison. It needs a category with compare "new",
  3+ tools, and at least production.compare_min_intros of them already uploaded.
- Skipped:
  - a tool whose folder already exists while its status is still "new" (someone is making it by hand)
  - anything marked "qa failed" (it needs Jabran)
  - anything a run claimed today
- A claim left over from an earlier day (a crashed run) can be picked again.
"""
import datetime, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).parent.parent
DONE = ("scheduled", "uploaded private", "posted")


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def main(peek):
    today = datetime.date.today().isoformat()
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["production"]
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    tools, cats = index["tools"], index["categories"]

    def free(entry, field, folder):
        st = entry.get(field)
        if st == "new":
            return not folder.exists()
        return st == "in progress" and entry.get(f"{field}_claimed_on", today) < today

    intro = next((t for t in tools if free(t, "intro", ROOT / "tools" / slug(t["name"]))), None)
    done_by_cat = {}
    for t in tools:
        if t.get("intro") in DONE:
            done_by_cat[t["category"]] = done_by_cat.get(t["category"], 0) + 1
    compare = next((c for c in cats if c.get("tools", 0) >= 3 and done_by_cat.get(c["category"], 0) >= cfg["compare_min_intros"]
                    and free(c, "compare", ROOT / "compare" / slug(c["category"]))), None)
    made = sum(t.get("intro") in DONE for t in tools) + sum(c.get("compare") in DONE for c in cats)
    want_compare = "compare" in cfg["kinds"] and compare and ((made + 1) % cfg["compare_every"] == 0 or not intro)
    if want_compare:
        pick, kind, name, field, d = compare, "compare", compare["category"], "compare", f"compare/{slug(compare['category'])}"
    elif intro and "intro" in cfg["kinds"]:
        pick, kind, name, field, d = intro, "intro", intro["name"], "intro", f"tools/{slug(intro['name'])}"
    else:
        print("NOTHING LEFT")
        return
    if not peek:
        pick[field] = "in progress"
        pick[f"{field}_claimed_on"] = today
        (ROOT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"kind": kind, "name": name, "dir": d, "claimed": not peek}))


if __name__ == "__main__":
    main("--peek" in sys.argv)
