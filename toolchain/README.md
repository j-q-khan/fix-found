# Video toolchain

This is shared by the three video skills. It was copied from the Planning Room's About-me video toolchain and adapted:
- it's unbranded (no photo and no name)
- it renders 16:9 and 9:16
- captions are burned in
- it includes the Fix Found stamp

## Files per video

Each video has its own folder, for example `tools/langfuse/intro-youtube/`, created by `new_video.py`:

| File | Who writes it | What |
|---|---|---|
| `meta.json` | `new_video.py` | kind, format (`16:9` or `9:16`), title, number, max_seconds |
| `script.json` | you | `[[scene_id, chapter_label, [lines…]], …]` |
| `scenes.html` | you | the motion graphics, one `<div class="scene" id="s-<scene_id>">` per scene |
| `extra.js` | you (optional) | `window.extra(t)` for custom motion; it must depend only on `t` and `TL` |
| `narration.wav`, `timeline.json`, `captions.srt` | `vo_build.py` | audio, timing, captions |
| `anim.html` | `page.py` | the assembled page |
| `thumb.jpg` | `thumb.py` | 16:9 YouTube videos only |
| `upload.json` | you | title, description, tags, render path and thumbnail, for `publish_youtube.py` |

## Commands (run from the repo root)

```
python toolchain/vo_build.py <dir>                    # narration, timeline.json, captions.srt (stops if too long)
python toolchain/page.py <dir>                        # anim.html
node toolchain/capture.mjs <dir> x.mp4 1.0 "3,12,30"  # stills only: still_<t>.jpg in <dir>
node toolchain/capture.mjs <dir> "renders/<file>.mp4" 1.0   # the render
python toolchain/thumb.py <dir> "IS YOUR AI LYING?" --logo
ffprobe -v error -show_entries stream=codec_name,width,height,sample_rate,channels -show_entries format=duration -of compact "renders/<file>.mp4"
```

## The voice

- **Settings:** `config.json` holds `voice`, `engine` (`long-form` or `generative`) and `tempo`. If no voice is set, `vo_build.py` stops; run `python toolchain/voice_samples.py` and let Jabran choose.
- **Long-form voices:** Gregory and Patrick (male), Danielle and Ruth (female).
- **Generative voices** include Matthew and Stephen.
- **Audio** comes from Amazon Polly on the default AWS profile. Check the account with `aws sts get-caller-identity --query Account`. It must end with `config.json` → `aws_account` (the last four digits, confirmed by Jabran). If it doesn't, stop and ask.

**Narration rules (the TTS lint enforces the first):**
- No words with two pronunciations (live, read, lead, record, minute, project, content, present, close…). Reword them: "real", "look up", "guide".
- Spell abbreviations the way they're spoken: "A.I.", "A.P.I.", "L.L.M.", "sequel" for SQL.
- Write tool names the way they're said ("n-eight-n", "prompt foo"). Add each one to `config.json` → `caption_spellings` so the captions show the real name.
- Say numbers and prices in words. No links, ever.
- Claude can't hear the audio, so never claim a pronunciation is right. List the names to listen for.

## Engine (`common.js`)

- **Animation:** `data-a="<scene> <line> <offset s> <type> [dur]"` animates an element relative to the start of a spoken line.
  - Types: `show`, `pop`, `left`, `right`, `fade`, `grow` (bars), `drop`, `stamp`, `type`.
  - `type` reveals plain text one character at a time, for terminal lines.
- **Counting:** `data-count="<scene> <line> <offset> <dur> <target> [comma]"` counts a number up.
- **Placeholders:** `{{N}}` (the zero-padded number) and `{{TOOL}}` are filled in by `page.py`.
- **The stamp:** `<div class="stamp" data-a="<scene> 0 0 stamp" style="left:…;top:…">Fix found · #{{N}}</div>`.
- **Classes:** `h1`, `h2`, `sub`, `eyebrow`, `chip`, `card` (navy), `paper` (cream), `term` (terminal window; text goes in its own `abs` element), `stamp`, `serif`, plus the colours `gold`, `teal`, `coral`, `green`, `violet`.
- **Images:** screenshots go beside the video's files and are referenced with a relative path. `capture.mjs` waits for every image to load.
- **Motion graphics, never slides:** things move, stack, count, type and stamp in time with the words.

## Layout safe zones

| | 16:9 (1920×1080) | 9:16 (1080×1920) |
|---|---|---|
| Brand mark | top-left | top-left (y 110) |
| Chapter label | top-right | hidden |
| Content | y 150–880 | y 230–1230, x 60–940 (the right edge is for TikTok's buttons) |
| Captions | bottom, y ≈ 900–1020 | y ≈ 1270–1420, above TikTok's bottom bar |

## Check stills, then render

1. Take stills 1–2 seconds into each scene, after its animations land: `capture.mjs` with a list of seconds.
2. Look at each still. Fix overlaps, clipped words, text running out of its card, captions covering content, and stamps covering text.
3. Rebuild the page and check again until every still is clean.
4. Render, then confirm with `ffprobe`: 1920×1080 or 1080×1920, H.264, AAC at 48 kHz with 2 channels, within `max_seconds`.
5. Delete the `still_*.jpg` files.
