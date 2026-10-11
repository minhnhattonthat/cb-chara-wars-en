"""English dialogue font: the original LZ font block (14:8000 = file 0xA0000, 256 2bpp tiles -> VRAM $C000)
with lowercase glyphs from font/lowercase.txt in tiles 0x61-0x7A.

    python -X utf8 tools/font.py preview OUT.png   # render the patched font (scale 3)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402

FONT_OFF = 0xA0000
GLYPHS = ROOT / "font" / "lowercase.txt"


def parse_glyphs(path=GLYPHS):
    glyphs, name, rows = {}, None, []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith(";") or not line.strip():
            continue
        if line.startswith("== "):
            name, rows = line[3:].strip(), []
            glyphs[name] = rows
        else:
            rows.append([c == "#" for c in line.ljust(8, ".")[:8]])
    for k, r in glyphs.items():
        assert len(r) == 8, f"glyph {k}: {len(r)} rows"
    return glyphs


def shade(core):
    """Original font rule: stroke=3; left neighbour stroke -> 2; else up-left neighbour stroke/2 -> 1."""
    px = [[0] * 8 for _ in range(8)]
    for y in range(8):
        for x in range(8):
            if core[y][x]:
                px[y][x] = 3
            elif x and core[y][x - 1]:
                px[y][x] = 2
            elif x and y and px[y - 1][x - 1] in (2, 3):
                px[y][x] = 1
    return px


def tile_bytes(px):
    out = bytearray()
    for row in px:
        lo = hi = 0
        for x, p in enumerate(row):
            lo |= (p & 1) << (7 - x)
            hi |= (p >> 1) << (7 - x)
        out += bytes([lo, hi])
    return bytes(out)


def english_font(rom):
    font, used = lz.decompress(rom, FONT_OFF)
    font = bytearray(font)
    for ch, core in parse_glyphs().items():
        n = ord(ch)
        font[n * 16:n * 16 + 16] = tile_bytes(shade(core))
    return bytes(font), used


def main():
    if sys.argv[1:2] != ["preview"]:
        sys.exit(__doc__)
    from PIL import Image
    rom = (ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc").read_bytes()
    font, _ = english_font(rom)
    pal = [(0, 0, 0), (90, 90, 90), (170, 170, 170), (255, 255, 255)]
    img = Image.new("RGB", (128, 128))
    for n in range(256):
        b = font[n * 16:n * 16 + 16]
        for y in range(8):
            for x in range(8):
                p = ((b[y * 2] >> (7 - x)) & 1) | (((b[y * 2 + 1] >> (7 - x)) & 1) << 1)
                img.putpixel((n % 16 * 8 + x, n // 16 * 8 + y), pal[p])
    img.resize((384, 384), Image.NEAREST).save(sys.argv[2])
    print("wrote", sys.argv[2], "compressed", hex(len(lz.compress(font))))


if __name__ == "__main__":
    main()
