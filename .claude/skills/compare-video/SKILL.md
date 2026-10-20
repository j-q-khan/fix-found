---
name: compare-video
description: Make a Fix Found "How it compares" video for one problem category (the ~5 tools that fix the same problem), as a 3-4 minute 16:9 YouTube video plus a ~60-second 9:16 TikTok cut. Ranks by fit ("pick A if…"), never "best". Researches every tool fresh, waits for Jabran to approve the script and then the render, then uploads to YouTube. Use when he says "compare <category>", "comparison video", "which tool fits". Trigger: /compare-video [category]
---

# Comparison video

Read `README.md` and `toolchain/README.md` first. The intro skill's rules apply here too: unbranded, no client details, fresh dated facts, and two approval stops.

## 1. Sync, pick, check
- Run `git pull` and `python sync.py`.
- **Category:** the one Jabran named. Otherwise, the category with `compare: new` where most of its tools already have intros posted, so the video can point to them. It needs at least 3 tools.
- **Voice and AWS account:** check them as in the intro skill, step 2.

## 2. Research every contender fresh
In `compare/<slug>/sources.md` (dated), record for each tool in the category (from `index.json`), using its own repo and docs:
- what it does, in one line
- **setup effort:** one command / a few services / a cluster
- **hosting cost or effort**
- **licence:** note open-core, fair-code or source-available terms
- **maturity:** stars, latest release date, how active it is
- **where it fits best**

If a tool no longer fits the category, or the repo is archived, tell Jabran rather than forcing it in.

## 3. Problem, folders, script, then STOP
- Write the category's one-line `problem` in `index.json` ("How do you catch your AI giving wrong answers?").
- Run `python toolchain/new_video.py compare "<category>"`, which creates `compare-youtube/` and `compare-tiktok/`. Comparisons have no number; the stamp reads "Fix found · compared".

**YouTube script** (~500 words, at most 245 s):

| Scene | Label | Content |
|---|---|---|
| `problem` | "" | the problem as it happens |
| `contenders` | "01  The contenders" | each tool in one line |
| `table` | "02  Side by side" | setup, hosting, licence, maturity, as an animated table |
| `pick` | "03  Which fits you" | "Pick A if… Pick B if…", one line per tool |
| `catch` | "04  The catch they share" | what's true of all of them |
| `ask` | "" | the closing question, and that each tool has its own intro |

**TikTok script** (~140 words, at most 65 s): "Five tools, five lines: which one fits you?" Problem → one line per tool → the closing question.

**Then:**
- Draft `upload.json`, filling every SEO field as set out in `README.md` → "SEO". Title: "5 open-source ways to catch your AI lying, compared". Link each tool's posted intro in the description.
- Set the category's `compare` to `scripted`. **Show Jabran both scripts, then stop.** On approval, set it to `script approved`.

## 4. Build, render, STOP
- **Build:** as in `toolchain/README.md`.
  - The table scene reveals row by row in time with the words.
  - Show each tool's logo or name chip.
  - Never crown a winner.
- **Thumbnail:** `thumb.py` with words like "5 WAYS TO CATCH AI LIES", without `--logo`.
- **Checks:** run the dry run, then set `compare` to `rendered`.
- **Give Jabran both MP4s and what to listen for, then stop.**

## 5. After he approves the render
- Set `compare` to `render approved`, then run `.venv/Scripts/python publish_youtube.py compare/<slug>/compare-youtube`.
- Report the URL and the TikTok file's path.
- Offer to commit; commit only when he says so.
