"""Text lint for translated entries (run by tools/check.py; batches.py uses the same per-entry check).

    python -X utf8 tools/lint.py        -> prints errors, exit 1 if any
Dialogue: auto-wrapped at 28 columns (tools/wrap.py); every line must fit, characters must have a glyph, control
codes must match the JP (leading {fd:} kept, {f8:}/{yesno} multiset equal, {fd:} values drawn from the JP), and
glossary names must appear when their JP form does.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import wrap  # noqa: E402

# glyphs that exist in the font with their ASCII meaning (0x24 $, 0x25 %, 0x2A *, 0x40 @, 0x5C \ draw other glyphs)
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !\"#&'()+,-./:;<=>?[]^_♥")
CODE = re.compile(r"\{([a-z0-9]+)(?::([0-9A-F]+))?\}")
KNOWN_CODES = {"n", "p", "end", "fd", "f8", "yesno"}


def glossary_terms(path=ROOT / "glossary.md"):
    """[(jp, en, avoid list)] from every markdown table row with JP | EN | ... | Avoid."""
    terms = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [a.strip() for a in cells[4].split(",") if a.strip()]
            terms.append((cells[0], cells[1], avoid))
    return terms


def check_dialogue(jp, en, terms=(), box="wide"):
    width, lines = wrap.BOXES[box]
    errs = []
    if not en.endswith("{end}"):
        errs.append("must end with {end}")
    for name, arg in CODE.findall(en):
        if name not in KNOWN_CODES:
            errs.append(f"unknown code {{{name}}}")
    bad = sorted(set(CODE.sub("", en)) - ALLOWED)
    if bad:
        errs.append(f"characters without a glyph: {''.join(bad)!r}")
    jp_codes = CODE.findall(jp)
    en_codes = CODE.findall(en)
    lead = re.match(r"\{fd:[0-9A-F]{2}\}", jp)
    if lead and not en.startswith(lead[0]):
        errs.append(f"must start with {lead[0]}")
    if {a for n, a in en_codes if n == "fd"} - {a for n, a in jp_codes if n == "fd"}:
        errs.append("{fd:} value not used in the JP")
    want = Counter((n, a) for n, a in jp_codes if n in ("f8", "yesno"))
    got = Counter((n, a) for n, a in en_codes if n in ("f8", "yesno"))
    if want != got:
        errs.append(f"{{f8}}/{{yesno}} codes differ: JP {dict(want)} EN {dict(got)}")
    for page in wrap.layout(en, width, lines):
        for line in page:
            if wrap.visible_len(line) > width:
                errs.append(f"word too long for a {width}-column {box} line: {line!r}")
    for t_jp, t_en, avoid in terms:
        if t_jp in jp and t_en and not any(alt in en for alt in t_en.split(" / ")):  # "a / b" = alternatives
            errs.append(f"glossary: {t_jp} -> {t_en} missing")
        for a in avoid:
            if re.search(rf"\b{re.escape(a)}\b", en):
                errs.append(f"glossary: avoid {a!r} (use {t_en})")
    return errs


def lint():
    terms = glossary_terms()
    n = 0
    for e in json.loads((ROOT / "script" / "dialogue.json").read_text(encoding="utf-8")):
        if e["en"]:
            for err in check_dialogue(e["jp"], e["en"], terms, wrap.box_of(e)):
                print(f"{e['id']}: {err}")
                n += 1
    print(f"lint: {n} errors")
    return n == 0


if __name__ == "__main__":
    sys.exit(0 if lint() else 1)
