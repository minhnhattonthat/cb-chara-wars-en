"""Menu highlight tables: $0B:B638[menu] -> list of entry pointers -> list of tilemap byte offsets (FFFF ends).
The code at $07:E846 ORs palette bit $0800 into the listed cells of unselected entries (grey) and clears it for the
selected one, so each list must cover the whole (English) label.

    python -X utf8 tools/hilite.py ROM      # dump the structure
"""
import struct, sys

BANK0B = 0x58000
TABLE = 0xB638


def off(a, bank=BANK0B):
    return bank + a - 0x8000


def w(rom, a):
    return struct.unpack_from("<H", rom, a)[0]


def parse(rom, n_menus=None):
    """-> [(menu index, [[cell offsets] per entry])] for menus whose pointer is nonzero."""
    menus = []
    first_target = None
    i = 0
    while True:
        slot = off(TABLE) + 2 * i
        if first_target is not None and slot >= first_target:
            break
        p = w(rom, slot)
        i += 1
        if p == 0:
            menus.append((i - 1, None))
            continue
        first_target = min(first_target or 1 << 30, off(p))
        entries, k = [], 0
        while True:
            q = w(rom, off(p) + 2 * k)
            k += 1
            if q == 0xFFFF:
                break
            cells, j = [], 0
            while True:
                c = w(rom, off(q) + 2 * j)
                j += 1
                if c == 0xFFFF:
                    break
                cells.append(c)
            entries.append(cells)
        menus.append((i - 1, entries))
    return menus


NEW_BANK, NEW_FILE = 0x21, 0x108000      # rebuilt structure lives at $21:8000
BANK_OPERANDS = [0x3E84D, 0x3E86F, 0x3E879]  # bank bytes of LDA $0B....,x at $07:E84A, $07:E86C, $07:E876
# English label spans per menu entry: [(row, first col, last col), ...] (menu strings in tools/menus_en.py)
OVERRIDES = {
    0: [[(6, 2, 9)], [(8, 2, 8)], [(10, 2, 6)], [(12, 2, 7)], [(14, 2, 5)]],    # pause: Henchmen..EXIT
    4: [[(8, 4, 8)], [(10, 4, 8)], [(12, 4, 7)], [(14, 4, 7)], [(16, 4, 7)]],   # Decoy Gofer Work Move EXIT
    19: [[(11, 6, 8)], [(13, 6, 9)], [(15, 6, 9)]],                             # Use Give EXIT
    20: [[(21, 6, 8)], [(23, 6, 9)], [(25, 6, 9)]],
}


def cells(spans):
    return [r * 64 + c * 2 for r, c0, c1 in spans for c in range(c0, c1 + 1)]


def rebuild(rom):
    """Serialise the structure (with OVERRIDES) for $21:8000; returns bytes."""
    menus = parse(rom)
    for m, spans in OVERRIDES.items():
        assert menus[m][1] is not None and len(menus[m][1]) == len(spans), m
        menus[m] = (m, [cells(s) for s in spans])
    out = bytearray(2 * len(menus))
    for m, entries in menus:
        if entries is None:
            continue
        lists = []
        for c in entries:
            lists.append(0x8000 + len(out))
            out += b"".join(struct.pack("<H", x) for x in c) + b"\xff\xff"
        struct.pack_into("<H", out, 2 * m, 0x8000 + len(out))
        out += b"".join(struct.pack("<H", a) for a in lists) + b"\xff\xff"
    return bytes(out)


def apply(rom):
    blob = rebuild(rom)
    rom[NEW_FILE:NEW_FILE + len(blob)] = blob
    for op in BANK_OPERANDS:
        assert rom[op] == 0x0B, hex(op)
        rom[op] = NEW_BANK
    # table pointer operand at $07:E84A: B638 -> 8000
    assert rom[0x3E84B:0x3E84D] == b"\x38\xb6"
    rom[0x3E84B:0x3E84D] = b"\x00\x80"


if __name__ == "__main__":
    rom = open(sys.argv[1], "rb").read()
    for m, entries in parse(rom):
        if entries is None:
            print(m, "-")
            continue
        desc = []
        for cells in entries:
            rows = sorted({c // 64 for c in cells})
            cols = sorted({(c % 64) // 2 for c in cells})
            desc.append(f"r{rows} c{cols[0]}-{cols[-1]}({len(cells)})" if cells else "[]")
        print(m, "; ".join(desc))
