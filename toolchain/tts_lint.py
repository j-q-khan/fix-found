"""Pre-synthesis lint for TTS narration: block heteronyms (words with two pronunciations).

Why: Polly's long-form ("expressive") voices silently IGNORE SSML <phoneme> tags, and Claude cannot
listen to audio. A heteronym such as "live" (live wire / live well) was mispronounced in a delivered
video even after a "fix". The only reliable cure is to reword the line before any audio is made.

usage (in a builder):  from tts_lint import check_lines;  check_lines(all_vo_lines)
Override a deliberate, checked use with env TTS_LINT_ALLOW="word1,word2" (and tell the user to listen).
"""
import os, re, sys

# Common English heteronyms that TTS engines get wrong depending on sense or part of speech.
HETERONYMS = {
    "live", "lives", "read", "reads", "lead", "leads", "record", "records", "close", "closes",
    "minute", "tear", "tears", "wind", "winds", "wound", "object", "objects", "present", "presents",
    "content", "refuse", "permit", "permits", "produce", "project", "projects", "subject", "conduct",
    "contract", "contracts", "address", "perfect", "row", "rows", "bow", "bass", "desert", "invalid",
    "use", "excuse", "house", "separate", "estimate", "estimates", "graduate", "moderate",
    "attribute", "conflict", "conflicts", "increase", "decrease", "progress", "suspect", "upset",
    "lead-in", "polish", "resume", "console", "compound", "entrance", "minute", "does", "sow",
}
# Words safe in this project's usual phrasing; review before adding.
SAFE_DEFAULT = {"use", "house", "does", "increase", "progress", "perfect"}  # adjective reading is the default

SUGGEST = {
    "live": "real / production / your customers'", "lives": "sits / is stored",
    "record": "save / log / measure", "records": "logs / keeps", "read": "look up / review",
    "reads": "look-ups", "lead": "guide / head up", "close": "near / finish", "minute": "tiny / 60 seconds",
    "estimate": "guess / figure", "estimates": "figures", "separate": "split / walled-off",
    "contract": "agreement", "contracts": "agreements", "conflict": "clash", "conflicts": "clashes",
    "present": "show / current", "content": "material", "object": "item / push back",
    "project": "build / work", "perfect": "flawless / refine", "address": "fix / handle",
}

def _strip_tags(line):
    # ignore anything inside <phoneme>...</phoneme> (deliberate, e.g. the user's name) and other tags
    line = re.sub(r"<phoneme[^>]*>.*?</phoneme>", " ", line)
    return re.sub(r"<[^>]+>", " ", line)

def find(lines):
    allow = SAFE_DEFAULT | {w.strip().lower() for w in os.environ.get("TTS_LINT_ALLOW", "").split(",") if w.strip()}
    hits = []
    for i, line in enumerate(lines):
        for m in re.finditer(r"[A-Za-z][A-Za-z'-]*", _strip_tags(line)):
            w = m.group(0).lower()
            if w in HETERONYMS and w not in allow:
                hits.append((i, m.group(0), line))
    return hits

def check_lines(lines):
    hits = find(lines)
    if hits:
        msg = ["TTS LINT FAILED: reword these lines before synthesis (phoneme tags are ignored by long-form voices):"]
        for i, w, line in hits:
            msg.append(f"  line {i}: '{w}' -> try: {SUGGEST.get(w.lower(), 'a word with one pronunciation')}\n      {line}")
        msg.append("Deliberate and verified by ear? set TTS_LINT_ALLOW=word")
        sys.stderr.write("\n".join(msg) + "\n")
        sys.exit(2)

if __name__ == "__main__":
    import json
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    lines = [l for h in data for l in h["vo"]] if isinstance(data, list) else data
    check_lines(lines); print("TTS lint: clean")
