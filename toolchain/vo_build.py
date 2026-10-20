"""Build the narration for one video: Polly audio -> narration.wav, timeline.json (with caption chunks) and captions.srt.

usage: python toolchain/vo_build.py <video_dir>
<video_dir> holds script.json ([[scene_id, chapter_label, [lines...]], ...]) and meta.json (see new_video.py).
The voice comes from config.json ("voice", "engine", "tempo"); env VOICE / ENGINE override it (for samples and tests).
Audio is cached by (voice, engine, tempo, text), so an edited line is always re-synthesised.
Fails if the video (narration + end card + hold) would run past meta.json's max_seconds.
"""
import hashlib, json, os, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from tts_lint import check_lines

LEAD, GAP, TAIL, XF, END_CARD, HOLD = 0.3, 0.06, 0.35, 0.4, 1.6, 1.0
CAPTION_CHARS = {"16:9": 64, "9:16": 40}   # longest caption chunk; CSS wraps it to at most two lines


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-2000:]); sys.exit(1)
    return r.stdout


def dur(f):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)]).strip())


def voice_settings():
    cfg = json.loads((HERE.parent / "config.json").read_text(encoding="utf-8"))
    voice = os.environ.get("VOICE") or cfg.get("voice")
    if not voice:
        sys.exit("No narrator voice chosen yet: run toolchain/voice_samples.py, let Jabran pick, then set \"voice\" in config.json.")
    return voice, os.environ.get("ENGINE") or cfg.get("engine", "long-form"), float(cfg.get("tempo", 1.10))


def synth(text, voice, engine, tempo):
    h = hashlib.sha1(f"{voice}|{engine}|{tempo}|{text}".encode()).hexdigest()[:16]
    cache = HERE / "vo"
    cache.mkdir(exist_ok=True)
    f = cache / f"{voice}_{h}.mp3"
    if not f.exists():
        raw = f.with_suffix(".raw.mp3")
        run(["aws", "polly", "synthesize-speech", "--engine", engine, "--voice-id", voice,
             "--output-format", "mp3", "--sample-rate", "24000", "--text", text, str(raw)])
        run(["ffmpeg", "-y", "-hide_banner", "-i", str(raw), "-af", f"atempo={tempo}", str(f)])
        raw.unlink()
    return f


def written(text, spellings):
    """Captions show the written form: "A.I." -> "AI", plus config.json "caption_spellings" ("n-eight-n" -> "n8n")."""
    text = re.sub(r"\b((?:[A-Z]\.){2,})", lambda m: m.group(1).replace(".", ""), text)
    for spoken, shown in spellings.items():
        text = re.sub(r"\b" + re.escape(spoken) + r"\b", shown, text, flags=re.I)
    return text


def chunks(text, limit):
    """Split a spoken line into caption chunks of at most `limit` characters, breaking at words."""
    out, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > limit:
            out.append(cur); cur = w
        else:
            cur = f"{cur} {w}".strip()
    return out + [cur] if cur else out


def srt_time(s):
    ms = int(round(s * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main(vdir):
    vdir = pathlib.Path(vdir).resolve()
    meta = json.loads((vdir / "meta.json").read_text(encoding="utf-8"))
    script = json.loads((vdir / "script.json").read_text(encoding="utf-8"))
    check_lines([l for _, _, lines in script for l in lines])
    voice, engine, tempo = voice_settings()
    limit = CAPTION_CHARS[meta["format"]]
    spellings = json.loads((HERE.parent / "config.json").read_text(encoding="utf-8")).get("caption_spellings", {})
    scenes, captions, t_scene, inputs, filt, labels = [], [], 0.0, [], [], []
    for sid, label, lines in script:
        t, beats = LEAD, []
        for line in lines:
            f = synth(line, voice, engine, tempo)
            d = dur(f)
            start = t_scene + t
            beats.append({"start": round(start, 3), "dur": round(d, 3), "text": line})
            parts = chunks(written(line, spellings), limit)
            weights = [len(p) + 4 for p in parts]
            c0 = start
            for p, w in zip(parts, weights):
                c1 = c0 + d * w / sum(weights)
                captions.append({"start": round(c0, 3), "end": round(c1, 3), "text": p})
                c0 = c1
            idx = len(inputs) // 2
            inputs += ["-i", str(f)]
            ms = int(start * 1000)
            filt.append(f"[{idx}:a]aresample=48000,adelay={ms}|{ms}[a{idx}]")
            labels.append(f"[a{idx}]")
            t += d + GAP
        sdur = round(t - GAP + TAIL, 3)
        scenes.append({"id": sid, "label": label, "start": round(t_scene, 3), "dur": sdur, "beats": beats})
        t_scene += sdur - XF
    total = round(scenes[-1]["start"] + scenes[-1]["dur"] + END_CARD, 3)
    print(json.dumps({"voice": voice, "total": total, "words": sum(len(l.split()) for _, _, ls in script for l in ls),
                      "scenes": [(s["id"], s["start"], s["dur"]) for s in scenes]}))
    if total + HOLD > meta["max_seconds"]:
        sys.stderr.write(f"TOO LONG: {total + HOLD:.1f}s > {meta['max_seconds']}s. Trim the script.\n"); sys.exit(3)
    filt.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,"
                f"aresample=48000,apad,atrim=0:{total}[out]")
    run(["ffmpeg", "-y", "-hide_banner", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
         "-ar", "48000", "-ac", "2", str(vdir / "narration.wav")])
    scenes[-1]["dur"] = round(total - scenes[-1]["start"], 3)
    (vdir / "timeline.json").write_text(json.dumps({"total": total, "fps": 30, "voice": voice, "scenes": scenes,
                                                    "captions": captions}, indent=1), encoding="utf-8")
    (vdir / "captions.srt").write_text("".join(f"{i}\n{srt_time(c['start'])} --> {srt_time(c['end'])}\n{c['text']}\n\n"
                                               for i, c in enumerate(captions, 1)), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
