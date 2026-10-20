"""Automated quality gate for one video set. It stands in for Jabran's review in unattended runs.

usage: python toolchain/qa.py tools/<slug>      (intro: checks intro-youtube and intro-tiktok)
       python toolchain/qa.py compare/<slug>    (comparison: checks compare-youtube and compare-tiktok)

Writes <set>/qa.json, {"passed": true|false, "failures": [...]}. publish_youtube.py won't upload an unattended video
without passed = true. Checks:
- the TTS lint
- lengths and render specs (ffprobe)
- that captions and the thumbnail exist
- the SEO fields in upload.json
- a denylist scan: no Jabran, Upwork, employer or client wording in any script, scene, upload or sources file
- that every multi-digit number in the YouTube description also appears in sources.md
"""
import datetime, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "toolchain"))
from tts_lint import find as lint

DENY = [r"\bjabran\b", r"\bupwork\b", r"\btoluna\b", r"\bmetrix\s?lab\b", r"\bbacardi\b", r"\btideline\b", r"\bxambuster\b",
        r"\brotterdam\b", r"@gmail", r"\bmy client", r"\bour client", r"\ba client of\b", r"\bproposals?\b", r"\bhire me\b"]
SIZE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}


def probe(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,sample_rate,channels",
                        "-show_entries", "format=duration", "-of", "json", str(f)], capture_output=True, text=True)
    return json.loads(r.stdout or "{}")


def main(base):
    base = (ROOT / base).resolve()
    fails = []
    variants = sorted((d for d in base.iterdir() if d.is_dir() and (d / "meta.json").exists()),
                      key=lambda d: json.loads((d / "meta.json").read_text(encoding="utf-8"))["format"] != "16:9")   # YouTube first
    if not variants:
        sys.exit(f"qa: no video folders in {base}")
    sources = (base / "sources.md").read_text(encoding="utf-8") if (base / "sources.md").exists() else ""
    if not sources:
        fails.append("sources.md missing")
    yt_render = None
    for v in variants:
        meta = json.loads((v / "meta.json").read_text(encoding="utf-8"))
        script = json.loads((v / "script.json").read_text(encoding="utf-8"))
        lines = [l for _, _, ls in script for l in ls]
        fails += [f"{v.name}: heteronym '{w}' in: {l}" for _, w, l in lint(lines)]
        for f in ("timeline.json", "captions.srt", "anim.html", "scenes.html"):
            if not (v / f).exists():
                fails.append(f"{v.name}: {f} missing")
        tl = json.loads((v / "timeline.json").read_text(encoding="utf-8")) if (v / "timeline.json").exists() else {"total": 0}
        if tl["total"] + 1.0 > meta["max_seconds"]:
            fails.append(f"{v.name}: {tl['total'] + 1:.1f}s is over {meta['max_seconds']}s")
        texts = {n: (v / n).read_text(encoding="utf-8") for n in ("script.json", "scenes.html", "upload.json") if (v / n).exists()}
        texts["sources.md"] = sources
        for n, t in texts.items():
            for pat in DENY:
                if re.search(pat, t, re.I):
                    fails.append(f"{v.name}/{n}: forbidden wording /{pat}/")
        # the render: YouTube's path is in upload.json; TikTok's is the same name with (TikTok)
        if meta["format"] == "16:9":
            up = json.loads(texts.get("upload.json", "{}"))
            render = ROOT / up.get("video", "missing")
            yt_render = render
            t, d = up.get("title", ""), up.get("description", "")
            if not t or len(t) > 100 or re.search("[<>]", t + d):
                fails.append("upload.json: title missing, over 100 characters, or has < >")
            if len(d.encode("utf-8")) > 5000 or len(",".join(up.get("tags", []))) > 450 or len(up.get("tags", [])) < 10:
                fails.append("upload.json: description over 5000 bytes, or tags missing or too long")
            for need in ("Narration: AI voice", "Facts checked", "not an endorsement"):
                if need.lower() not in d.lower():
                    fails.append(f"upload.json: description lacks '{need}'")
            if len(re.findall(r"(?<!\w)#\w+", d.splitlines()[-1] if d else "")) != 3:
                fails.append("upload.json: the description's last line needs exactly 3 hashtags")
            digits = re.sub(r"[,\s]", "", sources)
            for n in re.findall(r"\d[\d,.]*\d|\d{2,}", d):
                core = n.replace(",", "").split(".")[0]
                if len(core) >= 2 and core not in digits:
                    fails.append(f"upload.json: number '{n}' isn't in sources.md")
            thumb = v / up.get("thumbnail", "thumb.jpg")
            if not thumb.exists() or thumb.stat().st_size > 2_000_000:
                fails.append("thumbnail missing or over 2 MB")
        else:
            render = yt_render.with_name(yt_render.name.replace("(YouTube)", "(TikTok)")) if yt_render else None
        if not render or not render.exists():
            fails.append(f"{v.name}: render not found")
            continue
        info = probe(render)
        st = {s.get("codec_name"): s for s in info.get("streams", [])}
        w, h = SIZE[meta["format"]]
        if st.get("h264", {}).get("width") != w or st.get("h264", {}).get("height") != h:
            fails.append(f"{v.name}: render is not {w}x{h} H.264")
        if st.get("aac", {}).get("sample_rate") != "48000" or st.get("aac", {}).get("channels") != 2:
            fails.append(f"{v.name}: audio is not AAC 48 kHz stereo")
        if float(info.get("format", {}).get("duration", 0)) > meta["max_seconds"]:
            fails.append(f"{v.name}: render longer than {meta['max_seconds']}s")
    result = {"passed": not fails, "failures": fails, "checked_at": datetime.datetime.now().isoformat(timespec="seconds"),
              "variants": [v.name for v in variants]}
    (base / "qa.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("QA PASSED" if not fails else "QA FAILED:\n  " + "\n  ".join(fails))
    sys.exit(0 if not fails else 1)


if __name__ == "__main__":
    main(sys.argv[1])
