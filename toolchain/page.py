"""Assemble <video_dir>/anim.html from common.css + scenes.html (+ optional extra.js) + common.js.

usage: python toolchain/page.py <video_dir>
scenes.html may use {{N}} (the zero-padded Fix Found number) and {{TOOL}} (the tool or category name) from meta.json.
The page opens on a start screen (the index.json "problem" line, plus logo.png and the name), which fades out
by 0.8 s. It is the first frame, so it is what TikTok shows as the cover by default.
"""
import json, pathlib, sys
from html import escape

HERE = pathlib.Path(__file__).parent
SIZE = {"16:9": (1920, 1080), "9:16": (1080, 1920)}

v = pathlib.Path(sys.argv[1]).resolve()
meta = json.loads((v / "meta.json").read_text(encoding="utf-8"))
w, h = SIZE[meta["format"]]
num = f"{meta['number']:03}" if meta.get("number") else ""
scenes = (v / "scenes.html").read_text(encoding="utf-8").replace("{{N}}", num).replace("{{TOOL}}", meta.get("title", ""))
extra = (v / "extra.js").read_text(encoding="utf-8") if (v / "extra.js").exists() else ""
brand = f'FIX FOUND<span>#{num}</span>' if num else "FIX FOUND"
index = json.loads((HERE.parent / "index.json").read_text(encoding="utf-8"))
entry = next((x for x in index["tools"] + index["categories"] if meta.get("title") in (x.get("name"), x.get("category"))), {})
problem = entry.get("problem", "")
logo = '<img src="logo.png">' if (v / "logo.png").exists() else ""
stamp = f'<div class="cv-stamp">Fix found · #{num}</div>' if num else ""
cover = (f'<div id="cover"><div class="cv-wrap"><div class="cv-problem{" long" if len(problem) > 44 else ""}">{escape(problem)}</div>'
         f'<div class="cv-tool">{logo}<span>{escape(meta.get("title", ""))}</span></div>{stamp}</div></div>') if problem else ""
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>:root{{--W:{w}px;--H:{h}px}}{(HERE / 'common.css').read_text(encoding='utf-8')}</style></head>
<body data-w="{w}" class="{'v' if meta['format'] == '9:16' else 'h'}"><div id="stage"><div id="dots"></div>
{scenes}
{cover}<div id="brand">{brand}</div><div id="chapter"></div><div id="cap"><span></span></div><div id="bar"></div></div>
<script src="timeline.js"></script>
<script>{extra}</script>
<script>{(HERE / 'common.js').read_text(encoding='utf-8')}</script>
</body></html>"""
(v / "anim.html").write_text(html, encoding="utf-8")
print("wrote", v / "anim.html")
