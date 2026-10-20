"""Make a short sample of the same line in each candidate narrator voice, so Jabran can choose by ear.

usage: python toolchain/voice_samples.py ["<sample line>"]
Writes renders/voice-samples/<Voice>-<engine>.mp3. Then set "voice" and "engine" in config.json.
"""
import pathlib, shutil, sys

HERE = pathlib.Path(__file__).parent
sys.path.insert(0, str(HERE))
from vo_build import synth
from tts_lint import check_lines

CANDIDATES = [("Gregory", "long-form"), ("Patrick", "long-form"), ("Danielle", "long-form"), ("Ruth", "long-form"),
              ("Matthew", "generative"), ("Stephen", "generative")]
LINE = ("Your A.I. just told a customer the wrong refund policy. Would you even know? "
        "Fix found: Langfuse. A flight recorder for your A.I.")

text = sys.argv[1] if len(sys.argv) > 1 else LINE
check_lines([text])
out = HERE.parent / "renders" / "voice-samples"
out.mkdir(parents=True, exist_ok=True)
for voice, engine in CANDIDATES:
    f = synth(text, voice, engine, 1.10)
    shutil.copy(f, out / f"{voice}-{engine}.mp3")
    print("wrote", out / f"{voice}-{engine}.mp3")
