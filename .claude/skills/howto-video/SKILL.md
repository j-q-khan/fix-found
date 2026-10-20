---
name: howto-video
description: Make a Fix Found "How to use" walkthrough for one tool, a 5-8 minute 16:9 YouTube video recorded from a script that really runs, with the tool's version and date on screen. Only for tools that earn one (most listed, viewers ask, or Jabran asks). Waits for Jabran to approve the steps and then the render, then uploads to YouTube. Use when he says "how-to for <tool>", "setup walkthrough", "tutorial video". Trigger: /howto-video <tool>
---

# How-to video

Read `README.md` and `toolchain/README.md` first. The intro skill's rules apply here too: unbranded, no client details, fresh dated facts, and two approval stops.

## 1. Sync, pick, check
- Run `git pull` and `python sync.py`.
- **Tool:** the one Jabran named. A tool earns a how-to if it's among the most listed, viewers ask for one, or he asks.
  - If its intro isn't `posted` yet, say so; the how-to is the follow-up.
- **Voice and AWS account:** check them as in the intro skill, step 2.
- **Docker:** run `docker version`; the demo runs inside a container. VHS isn't installed, so terminal output is recorded to a log and drawn as `term` scenes.

## 2. Plan the walkthrough from the docs
In `tools/<slug>/howto-sources.md` (dated), using the official docs only, write down:
- **what the viewer ends with:** one concrete result, which is the main use from the intro
- **prerequisites:** Docker, language version, accounts, API keys
- the exact install steps
- the first real use, end to end
- one step further
- the clean-up, and what keeping it running costs

## 3. Write the steps script and run it safely
- **The script:** `tools/<slug>/howto/steps.sh` runs every command in order, against a pinned version tag.
- **Where it runs:** only in a throwaway Docker container or a scratch folder outside this repo. The repo's code is untrusted.
- **Data and keys:** dummy data only. Any API key is a throwaway created for this recording and revoked afterwards. Never show a real key or account on screen, and blank out anything that looks like one.
- **Recording:** save each command and its real output to `howto/steps.log`.
- **Screenshots:** capture web UIs with headless Chrome (`chrome --headless=new --screenshot=… --window-size=1600,900 <local url>`) into the video folder.
- **Mistakes:** note every error you hit and how you fixed it. They become the "mistakes to avoid" scene.
- **Re-recording later:** when the tool changes, re-run `steps.sh` and rebuild.

## 4. Script, then STOP for approval
- Run `python toolchain/new_video.py howto "<tool>"`. It creates `howto-youtube/` and reuses the intro's number.
- Write `script.json` (~700–1000 words, at most 485 s) with these scenes:

| Scene | Label | Content |
|---|---|---|
| `result` | "" | The finished result first: "By the end, you'll have…" |
| `need` | "01  What you need" | prerequisites |
| `install` | "02  Install" | the commands, as they ran |
| `first` | "03  First real use" | start to finish |
| `further` | "04  One step further" | the next use |
| `mistakes` | "05  Mistakes to avoid" | from the real run |
| `cost` | "06  Cost and clean-up" | what it costs, how to switch it off |
| `next` | "07  Where to go next" | the docs, plus the closing question |

- Draft `upload.json`, filling every SEO field as set out in `README.md` → "SEO". The title is the result first: "Set up Langfuse in 10 minutes: trace every AI answer". Put the version and date in the description.
- Set the tool's `howto` to `scripted`. **Show Jabran the steps and the script, then stop.** On approval, set it to `script approved`.

## 5. Build, render, STOP
- **Build:** do it as in `toolchain/README.md`.
  - Terminal lines use `term` windows with `type` reveals, copied verbatim from `steps.log`. Never type something that didn't run.
  - Screenshots show real output.
  - Keep the version and date visible in a corner.
- **Thumbnail:** `thumb.py` with words like "SET UP IN 10 MIN".
- **Checks:** run the dry run, then set `howto` to `rendered`.
- **Give Jabran the MP4, its length and what to listen for, then stop.**

## 6. After he approves the render
- Set `howto` to `render approved`, then run `.venv/Scripts/python publish_youtube.py tools/<slug>/howto-youtube`.
- Report the URL.
- Offer to commit `tools/<slug>/` with the index; commit only when he says so.
