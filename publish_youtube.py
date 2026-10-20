"""Upload one approved 16:9 render to the YouTube channel in config.json (youtube.channel_id), with captions, thumbnail and playlist.

usage: .venv/Scripts/python publish_youtube.py <video_dir> [--dry-run]

<video_dir> (for example tools/langfuse/intro-youtube) must hold meta.json, timeline.json, captions.srt and upload.json:
  {"video": "renders/<file>.mp4", "title": "...", "description": "...", "tags": ["..."], "thumbnail": "thumb.jpg"}
Chapters are added to the description from timeline.json's scene labels.

Approval rules:
- Public or unlisted: index.json must mark the video "render approved" by Jabran.
- Private, with config.json youtube.private_upload_after_render on: a "rendered" video may go up. This is Jabran's standing
  rule (2026-10-20): "upload to the channel and not make it public, I can take it from there". He reviews and publishes in Studio.
After a successful upload it sets the status to "uploaded private" (or "posted" if public) and stores the URL in index.json.
It checks the signed-in channel before uploading. At Google's sign-in, pick the brand account in config youtube.signin_hint.
--dry-run checks everything and prints the request without contacting YouTube.
--test labels the upload "[TEST]", forces it private and leaves index.json alone (the approval gate still applies).
One-time setup (Google Cloud project, OAuth client, choosing the channel): see PUBLISHING.md.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).parent
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
STATUS_FIELD = {"intro": "intro", "howto": "howto", "compare": "compare"}


def fail(msg):
    sys.exit(f"publish: {msg}")


def chapters(tl):
    rows = [(0.0, "Intro")] + [(s["start"], s["label"].split("  ", 1)[-1]) for s in tl["scenes"][1:] if s["label"]]
    rows = [r for i, r in enumerate(rows) if i == 0 or r[0] - rows[i - 1][0] >= 10]   # YouTube needs 10 s per chapter
    if len(rows) < 3:
        return ""
    return "Chapters\n" + "\n".join(f"{int(t // 60)}:{int(t % 60):02} {label}" for t, label in rows)


def entry(index, meta):
    if meta["kind"] == "compare":
        return next(c for c in index["categories"] if c["category"] == meta["title"])
    return next(t for t in index["tools"] if t["name"] == meta["title"])


def main(vdir, dry, test=False):
    vdir = (ROOT / vdir).resolve() if not pathlib.Path(vdir).is_absolute() else pathlib.Path(vdir)
    meta = json.loads((vdir / "meta.json").read_text(encoding="utf-8"))
    up = json.loads((vdir / "upload.json").read_text(encoding="utf-8"))
    tl = json.loads((vdir / "timeline.json").read_text(encoding="utf-8"))
    cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))["youtube"]
    index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
    e = entry(index, meta)
    field = STATUS_FIELD[meta["kind"]]

    # checks (the approval gate comes last, so a dry run checks the files before Jabran approves)
    if meta["format"] != "16:9":
        fail("only the 16:9 YouTube version is uploaded; the 9:16 version is for TikTok")
    video = ROOT / up["video"]
    for f in (video, vdir / "captions.srt"):
        if not f.exists():
            fail(f"missing {f}")
    thumb = vdir / up["thumbnail"] if up.get("thumbnail") else None
    if thumb and (not thumb.exists() or thumb.stat().st_size > 2_000_000):
        fail(f"thumbnail missing or over 2 MB: {thumb}")
    desc = up["description"].rstrip() + ("\n\n" + chapters(tl) if chapters(tl) else "")
    title = up["title"]
    if len(title) > 100 or any(c in title + desc for c in "<>"):
        fail("title over 100 characters, or '<' / '>' in the title or description (YouTube rejects them)")
    if len(desc.encode("utf-8")) > 5000 or len(",".join(up.get("tags", []))) > 450:
        fail("description over 5000 bytes or tags too long")
    body = {"snippet": {"title": title, "description": desc, "tags": up.get("tags", []), "categoryId": cfg.get("category_id", "28"),
                        "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": cfg.get("privacy", "private"), "selfDeclaredMadeForKids": False,
                       "containsSyntheticMedia": bool(cfg.get("contains_synthetic_media", False)),
                       "embeddable": True, "publicStatsViewable": True, "license": "youtube"},
            "recordingDetails": {"recordingDate": json.loads((vdir / "meta.json").read_text(encoding="utf-8")).get("recorded")
                                 or __import__("datetime").date.today().isoformat() + "T00:00:00Z"}}
    playlist = cfg.get("playlists", {}).get(meta["kind"])
    if test:   # label it, keep it private, no playlist; the approval gate still applies
        body["snippet"]["title"] = ("[TEST] " + title)[:100]
        body["snippet"]["description"] = "Pipeline test upload. Safe to delete.\n\n" + desc
        body["status"]["privacyStatus"] = "private"
        playlist = None
    privacy = body["status"]["privacyStatus"]
    # Jabran's standing rule (2026-10-20): a finished render may go up as PRIVATE, and he reviews and publishes it in Studio.
    # Anything public or unlisted still needs "render approved".
    private_ok = privacy == "private" and cfg.get("private_upload_after_render", False) and e.get(field) == "rendered"
    approved = e.get(field) == "render approved" or private_ok
    gate = (f"index.json has {meta['title']} {field} = '{e.get(field)}'; a {privacy} upload needs 'render approved'"
            + ("" if privacy != "private" else " (or 'rendered' with private_upload_after_render on)"))
    if dry:
        print(json.dumps({"video": str(video), "bytes": video.stat().st_size, "thumbnail": str(thumb), "playlist": playlist,
                          "body": body}, indent=2, ensure_ascii=False))
        print("publish (dry run): file and metadata checks passed; nothing was sent")
        print("approval gate:", ("open (render approved)" if e.get(field) == "render approved" else "open (private upload after render)") if approved else "closed: " + gate)
        return
    if not approved:
        fail(gate)

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token = ROOT / cfg["token"]
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        print(f"Sign in and choose the channel: {cfg.get('channel_name', cfg.get('channel_id'))}. {cfg.get('signin_hint', '')}", flush=True)
        creds = InstalledAppFlow.from_client_secrets_file(str(ROOT / cfg["client_secret"]), SCOPES).run_local_server(
            port=0, prompt="select_account consent")   # always show the account and channel picker
    token.parent.mkdir(exist_ok=True)
    token.write_text(creds.to_json(), encoding="utf-8")
    yt = build("youtube", "v3", credentials=creds)
    # upload only to the channel named in config.json; a sign-in on another channel stops here
    mine = yt.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    if cfg.get("channel_id") and not any(c["id"] == cfg["channel_id"] for c in mine):
        names = ", ".join(f"{c['snippet']['title']} ({c['id']})" for c in mine) or "none"
        fail(f"signed in to {names}, not {cfg.get('channel_name', cfg['channel_id'])}. "
             f"Delete {cfg['token']} and run again. {cfg.get('signin_hint', '')}")

    req = yt.videos().insert(part="snippet,status,recordingDetails", body=body, media_body=MediaFileUpload(str(video), chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        status, resp = req.next_chunk()
        if status:
            print(f"uploaded {int(status.progress() * 100)}%")
    vid = resp["id"]
    url = f"https://youtu.be/{vid}"
    print("uploaded", url, "(private test)" if test else "")
    if not test:
        e[field] = "posted" if privacy == "public" else f"uploaded {privacy}"
        e[f"{field}_youtube_url"] = url
        e[f"{field}_visibility"] = privacy if privacy == "public" else f"{privacy} (Jabran publishes from Studio)"
        (ROOT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # the extras: a failure here leaves the video up, so report and carry on
    for what, call in [
        ("thumbnail", lambda: thumb and yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()),
        ("captions", lambda: yt.captions().insert(part="snippet", body={"snippet": {"videoId": vid, "language": "en", "name": "English"}},
                                                   media_body=MediaFileUpload(str(vdir / "captions.srt"), mimetype="application/octet-stream")).execute()),
        ("playlist", lambda: playlist and yt.playlistItems().insert(part="snippet", body={"snippet": {"playlistId": playlist,
                                                   "resourceId": {"kind": "youtube#video", "videoId": vid}}}).execute()),
    ]:
        if what == "playlist" and not playlist or what == "thumbnail" and not thumb:
            print(f"{what}: skipped (none set)")
            continue
        try:
            call()
            print(f"{what}: done")
        except Exception as ex:
            print(f"{what}: failed ({ex}); add it in YouTube Studio")


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv, "--test" in sys.argv)
