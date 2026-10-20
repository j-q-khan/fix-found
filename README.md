# Fix Found

Short videos about useful open-source tools. Each one opens with a real problem, shows the tool that fixes it, and always includes the catch.

The tools come from the "Tools you might consider" lists in Jabran's Upwork proposals. This repo turns that list into videos, one tool at a time, and never makes the same video twice.

## How it works

```
AI Planning Room (separate repo)                         this repo
proposal skill ─writes─> proposals/*/<STEM>_tools.json ──read-only──> scan.py → index.json / INDEX.md → scripts → videos
```

1. **Scan.** `python scan.py` reads every `*_tools.json` in the proposals folder set in `config.json`, then rebuilds `index.json` and `INDEX.md`. It's safe to re-run and picks up new proposals each time. A renamed GitHub repo is merged with its old URL. `--offline` skips the GitHub lookups.
2. **Pick.** Work from the top of `INDEX.md`. Tools listed by the most jobs come first.
3. **Research.** Read the repo fresh: README, docs, examples, licence, latest release. Where possible, run its quickstart. Note the sources and the date.
4. **Script.** Write the scripts from the templates below. Jabran approves each script before anything is rendered.
5. **Render.** Make the 16:9 and 9:16 versions, with captions burned in.
6. **Review and post.** Jabran watches the render, then uploads it himself. Nothing is posted automatically.

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

## Rules

- **Unbranded.** Jabran's name, face and voice stay out of the videos, and there are no "hire me" or Upwork calls to action. The narration is an AI voice that speaks only about the problem and the tool.
- **No client details, ever.** Videos, scripts and this repo hold nothing from a proposal except the tool list. Never use the proposals' client-specific text, such as "how it might come in handy".
- **Facts come fresh from the repo, with a date.** Star counts, licence and release are checked on the day. Nothing comes from memory, and there's no claim that anyone used a tool in production.
- **A tool is a fix to consider, not an endorsement.** Every video includes the catch.
- **Never post automatically.** Uploading to YouTube and TikTok is Jabran's action.
- **Demos use dummy data and a throwaway API key**, revoked after recording. No real key ever appears on screen.
- **Captions are burned in**, because people watch muted in Teams and on TikTok.

## Layout

| Path | What |
|---|---|
| `config.json` | Path to the Planning Room's `proposals/` folder |
| `scan.py` | Builds the index (Python standard library only) |
| `index.json` | The index. Edit only `problem`, `intro`, `howto` and `compare` by hand |
| `INDEX.md` | Readable view of the index |
| `tools/<slug>/` | Per tool: sources, scripts, scenes, captions, title and description (added when work starts) |
| `toolchain/` | Video toolchain, copied from the Planning Room's about-me videos and adapted (added with the first video) |
| `renders/` | MP4s and thumbnails; kept out of git |

Status values:
- `intro`: new → scripted → approved → rendered → posted
- `howto`: not planned → new → …
- `compare` (per category): new → …
