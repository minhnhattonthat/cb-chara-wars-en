"""Dialogue script extract / roundtrip (bank 07 script, see docs/re/README.md).

    python -X utf8 tools/text.py dump [--force]   -> script/dialogue.json (refuses to overwrite without --force)
    python -X utf8 tools/text.py roundtrip        -> re-encode every jp string, compare with ROM bytes
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc"
JP_TBL = ROOT / "tbl" / "jp.tbl"
SCRIPT = ROOT / "script" / "dialogue.json"
SCRIPT_LO, SCRIPT_HI = 0x38DF8, 0x3C33F          # message data, contiguous, each ends with FF
PTR_TABLES = [(0x38BCA, 77), (0x38D1A, 3), (0x38D4A, 58)]  # 24-bit pointers lo,hi,07 into the script


def file_off(lo, hi):
    return 0x38000 + ((hi << 8) | lo) - 0x8000


def pointer_slots(rom):
    """{message file offset: [slot file offsets]} from the three pointer tables."""
    slots = {}
    for base, n in PTR_TABLES:
        for i in range(n):
            s = base + 3 * i
            assert rom[s + 2] == 0x07, hex(s)
            slots.setdefault(file_off(rom[s], rom[s + 1]), []).append(s)
    return slots


def messages(rom, table):
    """[(offset, length, text)] for every message in the script region, in ROM order."""
    out, pos = [], SCRIPT_LO
    while pos < SCRIPT_HI:
        text, n = table.decode(rom, pos)
        out.append((pos, n, text))
        pos += n
    assert pos == SCRIPT_HI, f"script decode overran: {pos:#x}"
    return out


def dump(force):
    if SCRIPT.exists() and not force:
        sys.exit(f"{SCRIPT} exists; pass --force to overwrite (English would be lost)")
    rom, table = ROM.read_bytes(), Table.load(JP_TBL)
    slots = pointer_slots(rom)
    entries = []
    for i, (off, n, text) in enumerate(messages(rom, table)):
        entries.append({"id": f"D{i:03d}", "off": f"{off:06X}", "len": n,
                        "slots": [f"{s:06X}" for s in slots.get(off, [])],
                        "jp": text, "en": "", "status": "todo", "notes": ""})
    SCRIPT.parent.mkdir(exist_ok=True)
    SCRIPT.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} messages to {SCRIPT}")


def roundtrip():
    rom, table = ROM.read_bytes(), Table.load(JP_TBL)
    bad = 0
    for off, n, text in messages(rom, table):
        if table.encode(text) != rom[off:off + n]:
            bad += 1
            print(f"mismatch at {off:06X}: {text[:40]}")
    slots = pointer_slots(rom)
    starts = {off for off, _, _ in messages(rom, table)}
    stray = [hex(o) for o in slots if o not in starts]
    if stray:
        print("pointers not at a message start:", stray)
    print(f"roundtrip: {bad} mismatches, {len(stray)} stray pointers")
    return bad == 0 and not stray


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["dump", "roundtrip"])
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "dump":
        dump(a.force)
    else:
        sys.exit(0 if roundtrip() else 1)


if __name__ == "__main__":
    main()
