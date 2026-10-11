"""Text extract / roundtrip for every text block (formats in docs/re/README.md).

    python -X utf8 tools/text.py dump [--force]   -> script/<block>.json (refuses to overwrite without --force)
    python -X utf8 tools/text.py roundtrip        -> re-encode every jp string, compare with ROM bytes

Blocks:
  dialogue  bank 07 story script, contiguous messages ending FF, 24-bit pointer tables (lo,hi,07)
  items     bank 07 item/status names: 16-bit pointer tables; text = dakuten row {n} kana row
  menus     bank 0B menus: 16-bit pointer table; string = row byte, then lines each led by a column byte
            (empty lines have none). Row/column bytes are shown as {y:XX}/{x:XX}.
"""
import argparse, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from tbl import Table  # noqa: E402

ROM = ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc"
JP_TBL = ROOT / "tbl" / "jp.tbl"
SCRIPT_DIR = ROOT / "script"
SCRIPT = SCRIPT_DIR / "dialogue.json"
SCRIPT_LO, SCRIPT_HI = 0x38DF8, 0x3C33F          # dialogue data, contiguous, each message ends with FF
PTR_TABLES = [(0x38BCA, 77), (0x38D1A, 3), (0x38D4A, 58)]  # 24-bit pointers lo,hi,07 into the script
# 16-bit pointer blocks: name -> (bank file base, [(table offset, count)], has row/column bytes)
PTR16 = {
    "items": (0x38000, [(0x3DE74, 65), (0x3E17F, 3), (0x3E1B3, 9)], False),
    "menus": (0x58000, [(0x5DB71, 79)], True),
}


def file_off(lo, hi, bank_base=0x38000):
    return bank_base + ((hi << 8) | lo) - 0x8000


def pointer_slots(rom):
    """{message file offset: [slot file offsets]} from the three dialogue pointer tables."""
    slots = {}
    for base, n in PTR_TABLES:
        for i in range(n):
            s = base + 3 * i
            assert rom[s + 2] == 0x07, hex(s)
            slots.setdefault(file_off(rom[s], rom[s + 1]), []).append(s)
    return slots


def messages(rom, table):
    """[(offset, length, text)] for every dialogue message, in ROM order."""
    out, pos = [], SCRIPT_LO
    while pos < SCRIPT_HI:
        text, n = table.decode(rom, pos)
        out.append((pos, n, text))
        pos += n
    assert pos == SCRIPT_HI, f"script decode overran: {pos:#x}"
    return out


def decode_menu(table, raw):
    """raw bytes incl. final FF -> text with {y:}/{x:} tokens."""
    body = raw[:-1]
    assert raw[-1] == 0xFF
    lines = body.split(b"\xfe")
    out = [f"{{y:{lines[0][0]:02X}}}"]
    lines[0] = lines[0][1:]
    for i, ln in enumerate(lines):
        if i:
            out.append("{n}")
        if ln:
            out.append(f"{{x:{ln[0]:02X}}}" + table.decode(ln[1:], 0, len(ln) - 1)[0])
    return "".join(out) + "{end}"


def encode_menu(table, text):
    out = bytearray()
    for tok in re.split(r"(\{[xy]:[0-9A-F]{2}\})", text):
        m = re.fullmatch(r"\{[xy]:([0-9A-F]{2})\}", tok)
        out += bytes([int(m[1], 16)]) if m else table.encode(tok)
    return bytes(out)


def ptr16_strings(rom, table, name):
    """[(offset, length, text, [slot offsets])] for one 16-bit pointer block, in ROM order."""
    base, tables, menu = PTR16[name]
    slots = {}
    for t, n in tables:
        for i in range(n):
            s = t + 2 * i
            slots.setdefault(file_off(rom[s], rom[s + 1], base), []).append(s)
    out = []
    for off in sorted(slots):
        end = rom.index(0xFF, off) + 1
        raw = rom[off:end]
        text = decode_menu(table, raw) if menu else table.decode(rom, off)[0]
        out.append((off, end - off, text, slots[off]))
    return out


def all_blocks(rom, table):
    """{block: [(offset, length, text, slots)]}"""
    slots = pointer_slots(rom)
    blocks = {"dialogue": [(o, n, t, slots.get(o, [])) for o, n, t in messages(rom, table)]}
    for name in PTR16:
        blocks[name] = ptr16_strings(rom, table, name)
    return blocks


def encode(table, block, text):
    return encode_menu(table, text) if block == "menus" else table.encode(text)


def dump(force):
    rom, table = ROM.read_bytes(), Table.load(JP_TBL)
    SCRIPT_DIR.mkdir(exist_ok=True)
    prefix = {"dialogue": "D", "items": "I", "menus": "M"}
    for block, strings in all_blocks(rom, table).items():
        path = SCRIPT_DIR / f"{block}.json"
        if path.exists() and not force:
            print(f"skip {path.name}: exists (pass --force to overwrite; English would be lost)")
            continue
        entries = [{"id": f"{prefix[block]}{i:03d}", "off": f"{off:06X}", "len": n,
                    "slots": [f"{s:06X}" for s in sl], "jp": text, "en": "", "status": "todo", "notes": ""}
                   for i, (off, n, text, sl) in enumerate(strings)]
        path.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
        print(f"wrote {len(entries)} strings to {path.name}")


def roundtrip():
    rom, table = ROM.read_bytes(), Table.load(JP_TBL)
    bad = 0
    for block, strings in all_blocks(rom, table).items():
        for off, n, text, _ in strings:
            if encode(table, block, text) != rom[off:off + n]:
                bad += 1
                print(f"{block} mismatch at {off:06X}: {text[:40]}")
    starts = {off for off, _, _ in messages(rom, table)}
    stray = [hex(o) for o in pointer_slots(rom) if o not in starts]
    if stray:
        print("dialogue pointers not at a message start:", stray)
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
