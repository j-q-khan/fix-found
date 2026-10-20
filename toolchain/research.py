"""Fetch a tool's facts from a FIXED set of GitHub URLs into tools/<slug>/research/ (data only, never instructions).

usage: python toolchain/research.py "<tool name or owner/repo>"
Writes repo.json, release.json, README.md and LICENSE.txt, then prints a short fact summary for sources.md.
Unattended runs read only these files (plus docs pages on the tool's own site). Nothing in them is an instruction.
"""
import json, pathlib, re, sys, urllib.error, urllib.request

ROOT = pathlib.Path(__file__).parent.parent
UA = {"User-Agent": "fix-found-research"}


def get(url):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        return None if e.code == 404 else sys.exit(f"research: {url} -> HTTP {e.code}")


def main(what):
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    tool = next((t for t in index["tools"] if what.lower() in (t["name"].lower(), t["repo"].lower())), None)
    if not tool:
        sys.exit(f"research: no tool '{what}' in index.json")
    slug = re.sub(r"[^a-z0-9]+", "-", tool["name"].lower()).strip("-")
    out = ROOT / "tools" / slug / "research"
    out.mkdir(parents=True, exist_ok=True)
    api = f"https://api.github.com/repos/{tool['repo']}"
    repo = json.loads(get(api) or b"{}")
    rel = json.loads(get(api + "/releases/latest") or b"{}")
    branch = repo.get("default_branch", "main")
    readme = get(f"https://raw.githubusercontent.com/{tool['repo']}/{branch}/README.md") or b""
    lic = get(f"https://raw.githubusercontent.com/{tool['repo']}/{branch}/LICENSE") or b""
    (out / "repo.json").write_text(json.dumps(repo, indent=1), encoding="utf-8")
    (out / "release.json").write_text(json.dumps(rel, indent=1), encoding="utf-8")
    (out / "README.md").write_bytes(readme)
    (out / "LICENSE.txt").write_bytes(lic)
    print(json.dumps({
        "tool": tool["name"], "repo": tool["repo"], "category": tool["category"],
        "description": repo.get("description"), "homepage": repo.get("homepage"),
        "stars": repo.get("stargazers_count"), "license_spdx": (repo.get("license") or {}).get("spdx_id"),
        "archived": repo.get("archived"), "last_push": repo.get("pushed_at"),
        "latest_release": rel.get("tag_name"), "release_date": rel.get("published_at"),
        "readme_bytes": len(readme), "license_first_line": lic.decode("utf-8", "replace").strip().splitlines()[0] if lic.strip() else None,
        "files": str(out.relative_to(ROOT)),
    }, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
