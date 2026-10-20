# Publishing to YouTube

**Status: set up and working.** The first upload, Fix Found #001 Langfuse, went up on 2026-10-20: https://youtu.be/q7ZDsAuv_D0

## How a video gets posted

1. **Jabran approves the script.** The skill stops for this.
2. **The skill renders and checks the video itself:** stills, `ffprobe` and the dry run. It then sets the status to `rendered`.
3. **It uploads as private:**
   ```
   .venv/Scripts/python publish_youtube.py tools/<slug>/intro-youtube
   ```
   This is Jabran's standing rule (2026-10-20): *"You can upload to the channel and not make it public, I can take it from there."* `config.json` → `youtube.private_upload_after_render: true` allows a `rendered` video to go up as **private** without a separate render approval.
4. **Jabran reviews the private video in YouTube Studio and publishes it himself.**
5. **TikTok:** Jabran uploads the 9:16 file from `renders/` by hand. TikTok's posting API needs an app review first.

**Public or unlisted uploads** (if `youtube.privacy` is ever changed) still need the status `render approved`, which is set only when Jabran approves the render.

**After an upload**, `index.json` records:
- `intro` = `uploaded private` (or `posted` if public)
- `intro_youtube_url`
- `intro_visibility`

The same fields exist for `howto` and `compare`. A video whose status is already `uploaded private` or `posted` is refused, so nothing goes up twice.

**Every upload includes:**
- the title, the keyword-first description with chapters, and the tags (all SEO fields; see `README.md` → "SEO")
- category Science & Technology, English, not made for kids, embeddable, the recording date, standard licence
- the thumbnail, the English captions (`captions.srt`), and the playlist if one is set

Comments, "Paid promotion" and "Featured places" can't be set through the API, so they stay at YouTube's defaults.

```
.venv/Scripts/python publish_youtube.py <dir> --dry-run   # check everything, send nothing; shows whether the approval gate is open
.venv/Scripts/python publish_youtube.py <dir> --test      # a private "[TEST]" upload; leaves index.json alone
```

## The channel and sign-in

- **Channel:** `config.json` → `youtube.channel_id` = `UCmxifChwsfWA4E9FhQgQ78Q`, **Jabran Qamar Khan (@JQK-Upwork)**. The script checks the signed-in channel before every upload and stops if it's a different one.
- **Google key:** the Google Cloud OAuth client is shared with the QuranLM project (copied from `Documents/QuranLM/client_secrets.json` to `.secrets/youtube_client_secret.json`). That's why Google's screens say "QuranLM". To change that label, rename the app in Google Cloud → Google Auth Platform → Branding.
- **Sign-in:** saved in `.secrets/youtube_token.json`, so uploads run without asking. Git ignores `.secrets/`.
- **If Google asks again** (the token expired or was deleted):
  1. A browser window opens. Click **jabranqkhan@gmail.com**.
  2. On "Choose your account or a brand account", pick **Xambuster**. That's the old name, still shown there, of the Jabran Qamar Khan brand channel. **Not** the plain account, which is the Quran-LM channel.
  3. Tick **Select all**, then **Continue**.
- **If it says "signed in to Quran-LM…":** the wrong entry was picked. Delete `.secrets/youtube_token.json` and run again, picking Xambuster.
- **If sign-in is needed every week:** the Google app is in "Testing" mode, where sign-ins expire after 7 days. In Google Cloud → Google Auth Platform → Audience, set the publishing status to **In production**.

## Settings in `config.json` → `youtube`

| Key | Value | Meaning |
|---|---|---|
| `channel_id`, `channel_name` | Jabran Qamar Khan | Where videos go. To move the series to its own channel later, change these and delete the token. |
| `signin_hint` | pick Xambuster | Printed whenever sign-in is needed. |
| `privacy` | `private` | Jabran publishes from Studio. Switch to `public` only if he wants videos to go live automatically; that also needs render approval each time. |
| `private_upload_after_render` | `true` | Jabran's standing rule: a rendered video may go up as private without a separate render approval. |
| `contains_synthetic_media` | `false` | YouTube Help ([support.google.com/youtube/answer/14328491](https://support.google.com/youtube/answer/14328491), checked 2026-10-20) requires disclosure for realistic content: a real person saying or doing something they didn't, altered real events, or realistic invented scenes. It lists "cloning one's own voice to create voice overs" as not needing it. A generic AI narrator doesn't depict a real person, and every description says "Narration: AI voice." |
| `category_id` | `28` | Science & Technology |
| `playlists` | `{}` | Optional, for example `{"intro": "PL…", "howto": "PL…", "compare": "PL…"}` |

## Limits (YouTube Data API `videos.insert`, checked against the raw page on 2026-10-20)

- "Quota impact: 100 calls per day … 1 unit in the Video Uploads quota bucket." Captions, thumbnails and playlists use the normal daily quota.
- "Videos uploaded from unverified API projects are not restricted to private viewing mode."
