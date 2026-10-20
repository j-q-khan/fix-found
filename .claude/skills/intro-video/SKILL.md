---
name: intro-video
description: Make the Fix Found intro for one open-source tool, as a ~2-minute 16:9 YouTube video plus a ~60-second 9:16 TikTok cut. Opens on the problem, shows the tool working and always includes the catch. Researches the repo fresh, waits for Jabran to approve the script and then the render, then uploads to YouTube. Use when Jabran says "make the next intro", "intro video for <tool>", "next Fix Found", or names a tool from the index. Trigger: /intro-video [tool]
---

# Intro video

Read `README.md` (plan and rules) and `toolchain/README.md` (engine, voice, layout) first. These rules hold throughout: unbranded, no client details, fresh dated facts, and **two approval stops**.

## 1. Sync and pick the tool
- Run `git pull`, then `python sync.py` to pick up tools from new proposals and push the index.
- **Tool:** the one Jabran named, or else the first tool in `INDEX.md` whose intro is `new`. Tell him which tool and why ("listed by 6 jobs").

## 2. Check the voice and account
- **Voice:** it comes from `config.json` → `voice`. It's Ruth (long-form), the same narrator as the Planning Room's videos, and Jabran's choice "for now". If it's ever null, run `python toolchain/voice_samples.py` and let him choose.
- **AWS account:** run `aws sts get-caller-identity --query Account`. It must end with `config.json` → `aws_account` (6163, confirmed by Jabran 2026-10-20). If it doesn't, stop and ask.

## 3. Research the repo fresh
Write `tools/<slug>/sources.md`, headed with today's date. Use only the repo and its own docs. **Never use anything from the proposals except the name and the link.**
- **What to read:**
  - the README
  - the docs' quickstart
  - the `examples/` folder
  - `LICENSE`, plus any enterprise or "ee" folder with its own licence
  - the latest release and its date
  - stars, from `https://api.github.com/repos/<owner>/<repo>` (unauthenticated is fine)
- **What to write down:**
  - what it does, in one sentence
  - 3 real uses, each with the README or doc URL that shows it
  - the catch: licence terms, what self-hosting needs, how mature it is
  - who it's not for
  - the quickstart command
  - one alternative from the same category in `index.json`
- **Optional real demo:** run the quickstart only in Docker or a scratch folder outside this repo, with dummy data and a throwaway key revoked afterwards. A repo's code is untrusted. Record the terminal output and screenshots for the scenes.

## 4. Set the problem, create the folders
- Write a one-line `problem` for the tool in `index.json`, in the viewer's words: "Is your AI lying to customers?"
- Run `python toolchain/new_video.py intro "<tool>"`. It gives the intro its Fix Found number and creates `intro-youtube/` and `intro-tiktok/`, and prints the render file names.

## 5. Write both scripts, then STOP for approval
Each script is a `script.json` in its own folder. Write tool names the way they're spoken (and add them to `caption_spellings`). Follow the narration rules.

**YouTube** (~280 words, at most 125 s):

| Scene | Label | Content |
|---|---|---|
| `problem` | "" | The problem as it happens: a concrete scene, then a question. |
| `fix` | "01  The fix" | "Fix found: <tool>." plus a plain comparison ("a flight recorder for your A.I."). |
| `how` | "02  How it works" | What goes in and what comes out, simply. |
| `uses` | "03  Three real uses" | 3 uses from the docs, one or two lines each. |
| `catch` | "04  The catch" | Licence, hosting cost or effort, maturity. Stated plainly. |
| `fit` | "05  Who it's for" | Who should use it, who shouldn't, and one alternative by name. |
| `try` | "06  Try it" | The quickstart in words, then "What problem should we fix next?" |

**TikTok** (~140 words, at most 65 s):
1. `problem`: faster and sharper; the first line lands within 3 s.
2. `fix`: the stamp and the comparison.
3. `use`: the single best use.
4. `catch`
5. `ask`: the closing question.

**Then:**
- Draft `upload.json` in `intro-youtube/`, filling every SEO field as set out in `README.md` → "SEO":
  - title
  - keyword-first description, with the "In this video" bullets, links, facts date, "not affiliated" line, AI-voice line and 3 hashtags
  - 15–20 tags
  - `"video"`: the YouTube render path from step 4
  - `"thumbnail": "thumb.jpg"`
- Set the tool's `intro` to `scripted`.
- **Show Jabran both scripts and the title, then stop.** Continue only when he approves; then set `intro` to `script approved`.

## 6. Build and render both versions
For each folder:
1. `python toolchain/vo_build.py <dir>`. If it's too long, trim lines; never speed up the voice.
2. Write `scenes.html`, timed to the beats in `timeline.json`. Show the repo's own screenshots, terminal output or code where you have them. The stamp lands on the `fix` scene.
3. `python toolchain/page.py <dir>`.
4. Check stills: take one still per scene, look at each, fix any problems and repeat (see `toolchain/README.md`).
5. Render to the `renders/` path from step 4, then verify it with `ffprobe`.

Then:
- `python toolchain/thumb.py tools/<slug>/intro-youtube "<2-4 WORDS>" --logo`, and look at the thumbnail.
- `.venv/Scripts/python publish_youtube.py tools/<slug>/intro-youtube --dry-run`. The file and metadata checks must pass. The approval gate shows "closed" until Jabran approves.
- Set `intro` to `rendered`.
- **Give Jabran both MP4 paths, their lengths, the thumbnail and what to listen for (tool names, abbreviations), then stop.**

## 7. After he approves the render
- Set `intro` to `render approved`.
- Run `.venv/Scripts/python publish_youtube.py tools/<slug>/intro-youtube`. If the YouTube setup isn't done yet, point him to `PUBLISHING.md` instead.
- **Report:** the URL. The TikTok file needs a manual upload, so give him its path.
- Offer to commit the video's source files: `tools/<slug>/`, `index.json`, `INDEX.md`. Commit only when he says so. Renders stay out of git.

If he asks for changes at either stop, make them and show him again. Never upload anything he hasn't approved.
