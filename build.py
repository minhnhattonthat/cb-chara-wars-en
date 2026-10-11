"""Build the English ROM.

    python -X utf8 build.py [--out build/cbcw_en.sfc] [--marker]

Text: script/{dialogue,items,menus}.json; `en` if set, else `jp` (so an untranslated build is the original ROM,
byte-identical: tests/test_build.py). --marker replaces every dialogue line with "[id] ..." for engine QA.
Dialogue that no longer fits bank 07 moves to bank $20 (file 0x100000, ROM expanded to 2 MiB) and the
engine's `LDA #$07 / PHA / PLB` at $06:B8D7 is patched to the new bank.
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
import font  # noqa: E402
import lz  # noqa: E402
import text  # noqa: E402
import wrap  # noqa: E402
from tbl import Table  # noqa: E402

OUT = ROOT / "build" / "cbcw_en.sfc"
EN_TBL = ROOT / "tbl" / "en.tbl"
DIALOGUE_BANK = 0x20                 # LoROM bank for relocated dialogue
DIALOGUE_FILE = 0x100000             # file offset of $20:8000
ENGINE_BANK_OPERAND = 0x338D8        # operand of LDA #$07 at $06:B8D7 (dialogue DB)
HEADER_SIZE = 0x7FD7                 # ROM size byte: 0x0A = 1 MiB, 0x0B = 2 MiB
LINE_WIDTH = 28                      # dialogue chars per line after the box widening below
# (file offset, original bytes, English bytes); applied to English builds, original bytes asserted first.
PATCHES = [
    # window 0 (dialogue box) record at 0B:DA3B: tilemap pos row 6 col 5 -> col 1, width 22 -> 30
    (0x5DA3B, bytes.fromhex("8a01 1600"), bytes.fromhex("8201 1e00")),
    # dialogue line-start table $06:BA4C (4 lines, bottom first): column 6 -> 2
    (0x33A4C, bytes.fromhex("0c03 8c02 0c02 8c01"), bytes.fromhex("0403 8402 0402 8401")),
    # page-start cursor LDA #$018C -> #$0184 ($06:B5FB, $06:B686 -> $1EA5; $07:E396 -> $72)
    (0x335FB, bytes.fromhex("a98c01"), bytes.fromhex("a98401")),
    (0x33686, bytes.fromhex("a98c01"), bytes.fromhex("a98401")),
    (0x3E396, bytes.fromhex("a98c01"), bytes.fromhex("a98401")),
]


def load(block):
    return json.loads((text.SCRIPT_DIR / f"{block}.json").read_text(encoding="utf-8"))


def encode_entry(block, e, jp, en, marker):
    if e["en"]:
        return text.encode(en, block, wrap.wrap(e["en"]) if block == "dialogue" else e["en"])
    if marker and block == "dialogue":
        return en.encode(marker_text(e))
    return text.encode(jp, block, e["jp"])


def marker_text(e):
    """One marker per page: '[id] p<n>' padded to a full 20-column line, keeping the JP control codes."""
    import re
    codes = re.findall(r"\{fd:[0-9A-F]{2}\}|\{f8:[0-9A-F]{2}\}|\{yesno\}", e["jp"])
    lead = codes[0] if codes and e["jp"].startswith(codes[0]) else ""
    rest = "".join(c for c in codes[1:] if not c.startswith("{fd"))
    return f"{lead}[{e['id']}] Quick brown fox{{n}}jumps over the lazy{{n}}dog. 0123456789 ABC{{n}}Line four WWWWWWWW{rest}{{end}}"


def pack_dialogue(rom, entries, jp, en, marker):
    blobs = [encode_entry("dialogue", e, jp, en, marker) for e in entries]
    total = sum(map(len, blobs))
    # untranslated -> in place (identity build); any English/marker -> bank $20 (one layout to test)
    in_place = not marker and not any(e["en"] for e in entries)
    if in_place:
        base_file, bank = text.SCRIPT_LO, 0x07
    else:
        if total > 0x8000:
            sys.exit(f"dialogue {total:#x} bytes > one bank; split across banks not implemented")
        if len(rom) < 0x200000:
            rom.extend(b"\xff" * (0x200000 - len(rom)))
            rom[HEADER_SIZE] = 0x0B
        base_file, bank = DIALOGUE_FILE, DIALOGUE_BANK
        rom[ENGINE_BANK_OPERAND] = bank
    bank_file = 0x38000 if in_place else base_file   # file offset of <bank>:8000
    pos = base_file
    for e, b in zip(entries, blobs):
        cpu = 0x8000 + pos - bank_file
        rom[pos:pos + len(b)] = b
        for s in e["slots"]:
            s = int(s, 16)
            rom[s:s + 3] = bytes([cpu & 0xFF, cpu >> 8, bank])
        pos += len(b)
    if in_place:
        rom[pos:text.SCRIPT_HI] = b"\xff" * (text.SCRIPT_HI - pos)
    return total, in_place


def pack_ptr16(rom, block, entries, jp, en):
    """Repack a 16-bit pointer block in place, in ROM order, skipping the gaps between the original strings
    (pointer tables + padding)."""
    base = text.PTR16[block][0]
    offs = [(int(e["off"], 16), int(e["off"], 16) + e["len"]) for e in entries]
    spans = [(a_end, b) for (_, a_end), (b, _) in zip(offs, offs[1:]) if a_end < b]
    lo, hi = offs[0][0], offs[-1][1]
    pos = lo
    for e in entries:
        b = encode_entry(block, e, jp, en, False)
        for a, z in spans:                       # never write into a table/padding gap
            if pos < z and pos + len(b) > a:
                pos = z
        if pos + len(b) > hi:
            sys.exit(f"{block}: {e['id']} overflows its block ({pos + len(b):06X} > {hi:06X})")
        rom[pos:pos + len(b)] = b
        cpu = pos - base + 0x8000
        for s in e["slots"]:
            s = int(s, 16)
            rom[s:s + 2] = bytes([cpu & 0xFF, cpu >> 8])
        pos += len(b)


def write_font(rom):
    data, old_len = font.english_font(rom)
    packed = lz.compress(data)
    if len(packed) > old_len:
        sys.exit(f"English font {len(packed):#x} bytes > original slot {old_len:#x}; relocation not implemented")
    rom[font.FONT_OFF:font.FONT_OFF + len(packed)] = packed


def build(out=OUT, marker=False):
    rom = bytearray(text.ROM.read_bytes())
    jp, en = Table.load(text.JP_TBL), Table.load(EN_TBL)
    total, in_place = pack_dialogue(rom, load("dialogue"), jp, en, marker)
    for block in text.PTR16:
        pack_ptr16(rom, block, load(block), jp, en)
    if not in_place:                             # English build: lowercase font, wider dialogue box
        write_font(rom)
        for off, old, new in PATCHES:
            assert rom[off:off + len(old)] == old, f"patch at {off:06X}: unexpected bytes"
            rom[off:off + len(new)] = new
    out = Path(out)
    out.parent.mkdir(exist_ok=True)
    out.write_bytes(rom)
    where = "bank 07 (in place)" if in_place else f"bank ${DIALOGUE_BANK:02X}"
    print(f"wrote {out} ({len(rom) // 1024} KiB); dialogue {total:#x} bytes in {where}")
    return rom


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--marker", action="store_true")
    a = ap.parse_args()
    build(a.out, a.marker)


if __name__ == "__main__":
    main()
