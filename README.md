# Fix Found

Short videos about useful open-source tools. Each one opens with a real problem, shows the tool that fixes it, and always includes the catch.

The tools come from the "Tools you might consider" lists in Jabran's Upwork proposals. This repo turns that list into videos, one tool at a time, and never makes the same video twice.

## How it works

```
AI Planning Room (separate repo)                         this repo
proposal skill ─writes─> proposals/*/<STEM>_tools.json ──read-only──> scan.py → index.json / INDEX.md → scripts → videos
```

1. **Sync.** New tools arrive on their own.
   - When a proposal session writes a `_tools.json`, a hook in the Planning Room runs `sync.py`. The hook lives in `.claude/settings.local.json` there.
   - `sync.py` runs `scan.py`, then commits and pushes `index.json` and `INDEX.md` only.
   - Every video skill also starts with `git pull` and `python sync.py`.
   - `scan.py` merges a renamed GitHub repo with its old URL and keeps every field the skills write. `--offline` skips the GitHub lookups.
2. **Pick.** Work from the top of `INDEX.md`. Tools listed by the most jobs come first.
3. **Research.** Read the repo fresh: README, docs, examples, licence, latest release. Where possible, run its quickstart. Note the sources and the date.
4. **Script.** Write the scripts from the templates below. **Jabran approves each script** before anything is rendered.
5. **Render.** Make the 16:9 and 9:16 versions with the toolchain (`toolchain/README.md`), with captions burned in.
6. **Review and post.** **Jabran watches the render and approves it.** Then `publish_youtube.py` uploads it automatically, with captions, thumbnail, chapters and playlist (see `PUBLISHING.md`). It refuses any video not marked `render approved`. The TikTok version is uploaded by hand for now.

**Skills:** `/intro-video`, `/howto-video`, `/compare-video` (in `.claude/skills/`).

## The three video types

| | Intro | How to use | How it compares |
|---|---|---|---|
| Made for | every tool | only tools that earn it (most listed, comments ask, or Jabran asks) | each category with 3+ tools |
| Answers | "What is it, and does it fix my problem?" | "How do I set it up?" | "Which one fits me?" |
| YouTube (16:9) | about 2 min, ~280 words | 5–8 min, with chapters | 3–4 min |
| TikTok (9:16) | about 60 s, ~140 words | none | about 60 s |

**Intro, YouTube (about 2 min)**

| Time | Section |
|---|---|
| 0:00–0:10 | The problem, as it happens |
| 0:10–0:20 | The "Fix Found #N" stamp, plus a plain comparison ("a flight recorder for your AI") |
| 0:20–0:40 | How it works, in one simple diagram |
| 0:40–1:25 | 3 real uses from the repo's own docs and examples, shown running |
| 1:25–1:40 | The catch: licence, hosting cost, maturity |
| 1:40–1:50 | Who it's for, who it isn't, plus one alternative from its category |
| 1:50–2:00 | Try it in 5 minutes (the quickstart command), then "What problem should we fix next?" |

**Intro, TikTok (about 60 s)**
1. The problem (0–3 s)
2. The stamp and comparison
3. The single best use, shown running
4. The catch
5. The question for comments

**How to use**
1. Show the finished result first.
2. What you need.
3. Install.
4. The first real use, start to finish.
5. One step further.
6. Mistakes to avoid.
7. Cost and clean-up.
8. Where to go next.

The steps live in a runnable script, and the recording is made from it, with the tool's version and date on screen. When the tool changes, re-run the script.

**How it compares**
1. The problem.
2. The contenders, one line each.
3. A side-by-side table: setup effort, hosting cost, licence, maturity.
4. "Pick A if…, pick B if…"
5. The catch they share.
6. The question.

Rank by fit, never "best".

## Titles and files

- **Title:** the problem first, then the tool, both within ~60 characters. "Is your AI lying to customers? Langfuse catches it". The series name goes last or is left out.
- **Thumbnail:** 2–4 big words for the problem, plus the tool's name.
- **File name:** `Fix Found 012 - Is your AI lying to customers - Langfuse.mp4`. Teams shows the file name as the title.
- The `problem` field in `index.json` holds the one-line problem. Title, thumbnail and file name all come from it.

## SEO: fill every field (Jabran's rule, 2026-10-20)

`upload.json` per video:
- **Title:** the problem first, then the tool name, within ~60 characters. The limit is 100.
- **Description:**
  - **Opening two lines:** what the tool is, with the search terms people use ("open-source LLM observability"). Only these show before "more".
  - **"In this video:" bullets.**
  - **Then:** the 3 uses, the catch, the try-it commands, and links (repo, docs, alternative).
  - **"Facts checked <date> (<version>, <stars>)."**
  - **"An open-source option to consider, not an endorsement. Not affiliated with <tool or owner>."**
  - **"Narration: AI voice."**
  - **Exactly 3 hashtags on the last line.** The first three show above the title.
  - `publish_youtube.py` adds the chapters from the scene labels.
- **Tags:** 15–20, about 450 characters at most:
  - the tool name, plus "<tool> tutorial"
  - the category's search terms
  - related tools and frameworks it works with
  - "fix found"

`publish_youtube.py` also sets:
- category Science & Technology
- English for both the title and the audio
- not made for kids
- the synthetic-media setting from `config.json`
- embeddable, with public stats
- standard YouTube licence
- the recording date

It then uploads the captions file and the thumbnail, and adds the playlist if one is configured. Comments, "Paid promotion" and "Featured places" can't be set through the API; leave them at YouTube's defaults or set them in Studio.

## Rules

- **Unbranded.** Jabran's name, face and voice stay out of the videos, and there are no "hire me" or Upwork calls to action. The narration is an AI voice that speaks only about the problem and the tool.
- **No client details, ever.** Videos, scripts and this repo hold nothing from a proposal except the tool list. Never use the proposals' client-specific text, such as "how it might come in handy".
- **Facts come fresh from the repo, with a date.** Star counts, licence and release are checked on the day. Nothing comes from memory, and there's no claim that anyone used a tool in production.
- **A tool is a fix to consider, not an endorsement.** Every video includes the catch.
- **Post only what Jabran has approved.** YouTube uploads run automatically after he approves the render, never before. `publish_youtube.py` refuses anything not marked `render approved`, so the step can't be skipped by mistake.
- **Demos use dummy data and a throwaway API key**, revoked after recording. No real key ever appears on screen.
- **Captions are burned in**, because people watch muted in Teams and on TikTok.

## Layout

| Path | What |
|---|---|
| `config.json` | Proposals path, narrator voice, AWS account, caption spellings, YouTube settings |
| `scan.py` | Builds the index (Python standard library only) |
| `sync.py` | Scan, then commit and push the index; also run by the Planning Room hook |
| `index.json` | The index. `scan.py` recomputes name, repo, url, category, jobs and first_seen; every other field (problem, number, statuses, URLs) belongs to the skills |
| `INDEX.md` | Readable view of the index |
| `tools/<slug>/` | Per tool: sources, then `intro-youtube/`, `intro-tiktok/`, `howto-youtube/` |
| `compare/<slug>/` | Per category: sources, then `compare-youtube/`, `compare-tiktok/` |
| `toolchain/` | The video toolchain (see `toolchain/README.md`) |
| `publish_youtube.py`, `PUBLISHING.md` | YouTube upload and its one-time setup |
| `.venv/`, `.secrets/`, `renders/` | Kept out of git: Python libraries, YouTube sign-in, MP4s and voice samples |

Status values for `intro`, `howto` and `compare`:
- The flow: new → scripted → script approved → rendered → render approved → posted.
- `howto` starts at `not planned`.
- `compare` reads `too few tools` when a category has fewer than 3.
