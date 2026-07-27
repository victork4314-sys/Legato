from pathlib import Path
import re

text = Path("index.html").read_text(encoding="utf-8")
required = [
    "Source Serif 4",
    "data-ptr=\"Edit score title\"",
    "openScoreEditor('clef'",
    "clefOctaves",
    "'4/4': [1, 1, 1, 1]",
    "'6/8': [1.5, 1.5]",
    "'7/8': [1, 1, 1.5]",
    "manualBreak",
    "headLeftUp",
    "beamY: edge",
    "Math.max(1.6, Math.abs(stemEnd - stemFrom))",
    "Cross-staff note",
    "clef-octave-change",
    "let y = 112"
]
for token in required:
    assert token in text, token
assert "Barlow Semi Condensed" not in text
assert "const infos = run.map(r => (this._beamInfo || {})[r.i]);" not in text
assert text.count("notes: (() => {") == 1
assert text.count("beams: this._beams || []") == 1

patterns = {
    "4/4": [1, 1, 1, 1],
    "3/4": [1, 1, 1],
    "2/2": [2, 2],
    "6/8": [1.5, 1.5],
    "5/4": [3, 2],
    "12/8": [1.5, 1.5, 1.5, 1.5],
    "7/8": [1, 1, 1.5],
}
expected_sums = {"4/4":4,"3/4":3,"2/2":4,"6/8":3,"5/4":5,"12/8":6,"7/8":3.5}
for meter, groups in patterns.items():
    assert abs(sum(groups) - expected_sums[meter]) < 1e-9

def offsets(steps, up):
    out, run = {}, 0
    for i, step in enumerate(steps):
        run = run + 1 if i and step - steps[i-1] <= 1 else 0
        out[step] = -7 + ((-7 if up else 7) if run % 2 else 0)
    return out
for up in (True, False):
    o = offsets([4,5,6,8,9], up)
    assert o[4] != o[5]
    assert o[5] != o[6]
    assert o[8] != o[9]

assert "const edge = at(xs[i]) + (up ? thick : -thick);" in text
script = re.search(r'<script type="text/x-dc"[^>]*>(.*?)</script>', text, re.S)
assert script, "embedded logic script missing"
Path("/tmp/legato-logic.js").write_text(script.group(1), encoding="utf-8")
print("Static engraving checks passed")
