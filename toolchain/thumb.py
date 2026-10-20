"""Make the YouTube thumbnail (1280x720 JPEG): 2-4 big words for the problem, plus the tool's name and logo.

usage: python toolchain/thumb.py <video_dir> "<PROBLEM WORDS>" [--logo]
--logo downloads the GitHub owner's avatar (https://github.com/<owner>.png) as logo.png, if it isn't there yet.
Writes <video_dir>/thumb.jpg (kept under 2 MB, YouTube's limit). Look at it before uploading.
"""
import html, json, pathlib, subprocess, sys, urllib.request

ROOT = pathlib.Path(__file__).parent.parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

v = pathlib.Path(sys.argv[1]).resolve()
words = sys.argv[2]
meta = json.loads((v / "meta.json").read_text(encoding="utf-8"))
index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
tool = next((t for t in index["tools"] if t["name"] == meta["title"]), None)
logo = v / "logo.png"
if "--logo" in sys.argv and tool and not logo.exists():
    req = urllib.request.Request(f"https://github.com/{tool['repo'].split('/')[0]}.png?size=400", headers={"User-Agent": "fix-found"})
    logo.write_bytes(urllib.request.urlopen(req, timeout=30).read())
num = f"#{meta['number']:03}" if meta.get("number") else ""
img = f'<img src="logo.png" style="width:170px;height:170px;border-radius:32px;background:#fff;object-fit:contain">' if logo.exists() else ""
page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
*{{margin:0;box-sizing:border-box}}body{{width:1280px;height:720px;overflow:hidden;font-family:'Segoe UI',Arial,sans-serif;color:#F7F5F0;
background:radial-gradient(900px 600px at 78% 18%,#22386a 0%,#14213D 55%,#0e1830 100%)}}
.brand{{position:absolute;left:60px;top:46px;font:800 30px 'Segoe UI';letter-spacing:7px;color:#D9A441}}
.brand span{{color:#8FA0B8;margin-left:12px}}
.problem{{position:absolute;left:60px;top:130px;width:1160px;font:900 128px/1.02 'Segoe UI';text-transform:uppercase;letter-spacing:-1px}}
.tool{{position:absolute;left:60px;bottom:56px;display:flex;align-items:center;gap:34px}}
.name{{font:700 88px Georgia,serif;color:#4FD1C5}}
.bar{{position:absolute;left:0;bottom:0;width:1280px;height:14px;background:linear-gradient(90deg,#4FD1C5,#D9A441,#FF7A59)}}
</style></head><body><div class="brand">FIX FOUND<span>{num}</span></div>
<div class="problem">{html.escape(words)}</div><div class="tool">{img}<div class="name">{html.escape(meta['title'])}</div></div><div class="bar"></div></body></html>"""
(v / "thumb.html").write_text(page, encoding="utf-8")
png = v / "thumb.png"
subprocess.run([CHROME, "--headless=new", f"--screenshot={png}", "--window-size=1280,720", "--hide-scrollbars",
                "--force-device-scale-factor=1", "--allow-file-access-from-files", (v / "thumb.html").as_uri()],
               capture_output=True, timeout=60)
subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(png), "-q:v", "3", str(v / "thumb.jpg")], check=True)
png.unlink()
print("wrote", v / "thumb.jpg", (v / "thumb.jpg").stat().st_size, "bytes")
