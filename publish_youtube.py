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
It then reads the video back from YouTube and checks that the title, description, tags, category, languages, privacy and
publish time are what was sent. A wrong snippet is re-sent once; anything still wrong goes in the run report and fails the run.
It checks the signed-in channel before uploading. At Google's sign-in, pick the brand account in config youtube.signin_hint.
--dry-run checks everything and prints the request without contacting YouTube.
--test labels the upload "[TEST]", forces it private and leaves index.json alone (the approval gate still applies).
One-time setup (Google Cloud project, OAuth client, choosing the channel): see PUBLISHING.md.
"""
import datetime, json, pathlib, sys
from zoneinfo import ZoneInfo

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


SNIPPET = ("title", "description", "tags", "categoryId", "defaultLanguage", "defaultAudioLanguage")


def mismatches(yt, vid, body):
    """The fields YouTube stored differently from the request body (empty when everything arrived)."""
    items = yt.videos().list(part="snippet,status", id=vid).execute().get("items", [])
    if not items:
        return ["video not found"]
    got, want = items[0], body
    norm = lambda x: (x or "").replace("\r\n", "\n").strip()
    bad = [k for k in ("title", "description") if norm(got["snippet"].get(k)) != norm(want["snippet"].get(k))]
    if sorted(got["snippet"].get("tags", [])) != sorted(want["snippet"].get("tags", [])):
        bad.append("tags")
    bad += [k for k in SNIPPET[3:] if want["snippet"].get(k) and got["snippet"].get(k) != want["snippet"][k]]
    bad += [k for k in ("privacyStatus", "publishAt") if want["status"].get(k) and got["status"].get(k) != want["status"][k]]
    return bad


def report(line):
    """Append one line to today's run report (reports/YYYY-MM-DD.md), which Jabran can skim."""
    d = ROOT / "reports"
    d.mkdir(exist_ok=True)
    f = d / f"{datetime.date.today().isoformat()}.md"
    if not f.exists():
        f.write_text(f"# Fix Found run report, {datetime.date.today().isoformat()}\n\n", encoding="utf-8")
    with f.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def next_slot(index, sched):
    """The earliest free publish slot at least lead_hours from now, at the configured local times (2 a day)."""
    tz = ZoneInfo(sched["timezone"])
    taken = {v for x in index["tools"] + index["categories"] for k, v in x.items() if k.endswith("_publish_at") and v}
    start = datetime.datetime.now(tz) + datetime.timedelta(hours=sched.get("lead_hours", 36))
    day = start.date()
    while True:
        for hhmm in sched["times"]:
            h, m = map(int, hhmm.split(":"))
            t = datetime.datetime(day.year, day.month, day.day, h, m, tzinfo=tz)
            iso = t.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            if t >= start and iso not in taken:
                return iso
        day += datetime.timedelta(days=1)


def entry(index, meta):
    if meta["kind"] == "compare":
        return next(c for c in index["categories"] if c["category"] == meta["title"])
    return next(t for t in index["tools"] if t["name"] == meta["title"])


def main(vdir, dry, test=False, unattended=False):
    vdir = (ROOT / vdir).resolve() if not pathlib.Path(vdir).is_absolute() else pathlib.Path(vdir)
    meta = json.loads((vdir / "meta.json").read_text(encoding="utf-8"))
    up = json.loads((vdir / "upload.json").read_text(encoding="utf-8"))
    tl = json.loads((vdir / "timeline.json").read_text(encoding="utf-8"))
    full_cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
    cfg = full_cfg["youtube"]
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
    prod = full_cfg.get("production", {})
    today = datetime.date.today().isoformat()
    qa_file = vdir.parent / "qa.json"
    qa_ok = qa_file.exists() and json.loads(qa_file.read_text(encoding="utf-8")).get("passed") is True
    # Who may upload (Jabran's rules, 2026-10-20):
    # - autonomous: "make videos without my review and post them to the channel scheduled out into the future, 2 a day".
    #   A "rendered" video whose qa.json passed goes up PRIVATE with a scheduled publish time (the next free slot).
    # - private_upload_after_render: a "rendered" video goes up private and unscheduled; he publishes it in Studio.
    # - anything public or unlisted right away needs "render approved".
    auto = bool(prod.get("autonomous")) and privacy == "private" and e.get(field) == "rendered" and qa_ok and not test
    private_ok = privacy == "private" and cfg.get("private_upload_after_render", False) and e.get(field) == "rendered" and qa_ok
    approved = e.get(field) == "render approved" or auto or private_ok
    gate = (f"index.json has {meta['title']} {field} = '{e.get(field)}', qa passed = {qa_ok}; an upload needs 'rendered' "
            f"with a passed toolchain/qa.py (private), or 'render approved' by Jabran")
    publish_at = next_slot(index, cfg["schedule"]) if auto else None
    if publish_at:
        body["status"]["publishAt"] = publish_at
    uploaded_today = sum(1 for x in index["tools"] + index["categories"] for k, val in x.items()
                         if k.endswith("_uploaded_on") and val == today)
    if dry:
        print(json.dumps({"video": str(video), "bytes": video.stat().st_size, "thumbnail": str(thumb), "playlist": playlist,
                          "body": body}, indent=2, ensure_ascii=False))
        print("publish (dry run): file and metadata checks passed; nothing was sent")
        print("approval gate:", ("open: scheduled for " + publish_at if auto else "open") if approved else "closed: " + gate)
        print(f"uploads today: {uploaded_today} of {prod.get('daily_max', 10)}")
        return
    if not approved:
        fail(gate)
    if uploaded_today >= prod.get("daily_max", 10) and not test:
        fail(f"daily cap reached: {uploaded_today} uploads today (production.daily_max)")

    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload

    token = ROOT / cfg["token"]
    creds = Credentials.from_authorized_user_file(str(token), SCOPES) if token.exists() else None
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as ex:   # a refresh token that expired or was revoked
            creds = None
            if unattended:
                report(f"- FAILED {meta['title']}: YouTube sign-in expired ({ex}). Run publish_youtube.py by hand once to sign in.")
                fail("YouTube sign-in expired; run it by hand once (see PUBLISHING.md)")
    if not creds or not creds.valid:
        if unattended:   # nobody is there to click through Google's sign-in
            report(f"- FAILED {meta['title']}: YouTube sign-in needed. Run publish_youtube.py by hand once.")
            fail("YouTube sign-in needed; unattended runs never open a browser (see PUBLISHING.md)")
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
        index = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))   # re-read: the upload took minutes
        e = entry(index, meta)
        e[f"{field}_youtube_url"] = url
        e[f"{field}_uploaded_on"] = today
        if publish_at:
            local = datetime.datetime.strptime(publish_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc) \
                .astimezone(ZoneInfo(cfg["schedule"]["timezone"])).strftime("%a %d %b %Y %H:%M %Z")
            e[field], e[f"{field}_publish_at"] = "scheduled", publish_at
            e[f"{field}_visibility"] = f"private until {local}, then public automatically"
        else:
            local = None
            e[field] = "posted" if privacy == "public" else f"uploaded {privacy}"
            e[f"{field}_visibility"] = privacy if privacy == "public" else f"{privacy} (Jabran publishes from Studio)"
        (ROOT / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tiktok = video.with_name(video.name.replace("(YouTube)", "(TikTok)"))
        report(f"- {meta['kind']} #{meta.get('number') or '-'} **{title}**: {url} | "
               f"{'publishes ' + local if local else privacy} | TikTok file: renders/{tiktok.name if tiktok.exists() else '(none)'}")
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
    # read the video back: the SEO fields must be on YouTube, not only in the request
    bad = mismatches(yt, vid, body)
    if set(bad) & set(SNIPPET):
        try:
            yt.videos().update(part="snippet", body={"id": vid, "snippet": body["snippet"]}).execute()
        except Exception as ex:
            print(f"metadata re-send failed ({ex})")
        bad = mismatches(yt, vid, body)
    if bad:
        if not test:
            report(f"- CHECK {meta['title']}: on YouTube these differ from upload.json: {', '.join(bad)}. Fix them in Studio: {url}")
        fail(f"uploaded {url}, but YouTube has the wrong or missing {', '.join(bad)}; fix in YouTube Studio")
    print("metadata check: passed (title, description, tags, category, languages, privacy, publish time)")


if __name__ == "__main__":
    main(sys.argv[1], "--dry-run" in sys.argv, "--test" in sys.argv, "--unattended" in sys.argv)
