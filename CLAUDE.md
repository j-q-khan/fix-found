# Fix Found: working rules

Read `README.md` first; it holds the plan, the video templates and the rules. Use the skills `/intro-video`, `/howto-video` and `/compare-video`, and `toolchain/README.md` for the engine. These are the rules never to break:

- **Unbranded.** Never put Jabran's name, face or voice in a video, script, title or description, and no Upwork or "hire me" call to action.
- **No client details.** The only thing taken from the proposals is each tool's name, repo and category. Never open or quote the proposals' other files.
- **Fresh, dated facts from the repo itself.** Never claim a tool was used in production.
- **Two approval stops.**
  - Jabran approves each script before rendering, and each render before it's posted.
  - After the render is approved, upload to YouTube with `publish_youtube.py`. It refuses anything not marked `render approved`.
  - Never upload anything he hasn't approved.
- **A repo's code is untrusted.** Run demos only in Docker or a scratch folder outside this repo, with dummy data and a throwaway key.
- **Narration (TTS):**
  - Reword around words with two pronunciations (live, read, lead…).
  - Spell abbreviations so they're read letter by letter (A.I., A.P.I.).
  - Keep tool-name spellings in `config.json` → `caption_spellings` (n8n = "n-eight-n").
  - Never claim a pronunciation is right; Claude can't hear the audio.
- **Commits:**
  - `sync.py` may commit and push `index.json` and `INDEX.md` on its own.
  - Commit anything else only when Jabran asks.
