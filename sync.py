"""Scan for new tools, then commit and push the index (index.json and INDEX.md only).

usage:
  python sync.py                 run now (also what the video skills do first)
  python sync.py --hook          as a Claude Code PostToolUse hook in the Planning Room: reads the hook's JSON on stdin
                                 and does nothing unless the file just written ends in _tools.json

Always exits 0, so a failed push never blocks a proposal session; the next run retries.
Commits only index.json and INDEX.md, whatever else is staged or changed in this repo.
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).parent


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)


def repos():
    p = ROOT / "index.json"
    return {t["repo"].lower() for t in json.loads(p.read_text(encoding="utf-8"))["tools"]} if p.exists() else set()


def main():
    if "--hook" in sys.argv:
        try:
            path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
        except ValueError:
            return
        if not path.endswith("_tools.json"):
            return
    before = repos()
    r = subprocess.run([sys.executable, str(ROOT / "scan.py")], capture_output=True, text=True)
    if r.returncode != 0:
        print("fix-found sync: scan failed:", (r.stderr or r.stdout).strip().splitlines()[-1:])
        return
    after = repos()
    if git("diff", "--quiet", "--", "index.json", "INDEX.md").returncode == 0:
        print("fix-found sync: index unchanged, nothing to commit")
        return
    new = len(after - before)
    msg = f"Scan: {len(after)} tools" + (f" (+{new} new)" if new else " (index refreshed)")
    if "--dry-run" in sys.argv:
        print(f"fix-found sync (dry run): would commit and push '{msg}'")
        return
    c = git("commit", "-m", msg, "--", "index.json", "INDEX.md")
    if c.returncode != 0:
        print("fix-found sync: commit failed:", c.stderr.strip()[:200])
        return
    p = git("push")
    print(f"fix-found sync: {msg}; " + ("pushed" if p.returncode == 0 else f"push failed, will retry next run ({p.stderr.strip()[:120]})"))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:   # never block the caller
        print("fix-found sync: error:", e)
    sys.exit(0)
