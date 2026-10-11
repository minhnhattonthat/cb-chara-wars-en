"""English for Japanese drawn in background/effect graphics (LZ blocks by gfx id). Each sign: a rectangle in the
block's tile-sheet coordinates (16 tiles = 128 px wide, tiles in block order, which is how these sheets are laid
out), filled with the sign's background index, then English text in the sign's text index (+ optional shadow).
Colours are read from the original pixels in the rectangle: background = most common, text = next most common.

    python -X utf8 tools/signs.py preview   -> work/signs/<id>.png (before | after, 4x)
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402
import titlegfx  # noqa: E402

FONTS = {"bold": "C:/Windows/Fonts/arialbd.ttf", "black": "C:/Windows/Fonts/ariblk.ttf",
         "impact": "C:/Windows/Fonts/impact.ttf"}
TINY = {  # 3x5 font for very small signs
    "A": "010101111101101", "C": "011100100100011", "D": "110101101101110", "E": "111100110100111",
    "G": "011100101101011", "I": "111010010010111", "K": "101101110101101", "L": "100100100100111",
    "N": "101111111111101", "O": "010101101101010", "S": "011100010001110", "!": "010010010000010",
    "F": "111100110100100", "V": "101101101101010", " ": "000000000000000",
    "B": "110101110101110", "H": "101101111101101", "M": "101111111101101", "P": "110101110100100",
    "R": "110101110101101", "T": "111010010010010", "U": "101101101101111", "Y": "101101010010010",
    "&": "010101010101011",
}
BPP = {193: 2}  # blocks that are 2bpp (default 4bpp)


def game_glyphs():
    """The dialogue font's stroke pixels (index 3) per ASCII char: {ch: (width, set of (x, y))}, 7 rows tall."""
    rom = (ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc").read_bytes()
    font, _ = lz.decompress(rom, 0xA0000)
    out = {}
    for c in range(0x21, 0x5B):
        px = {(x, y) for y in range(8) for x in range(8)  # 2bpp: both planes set = colour 3
              if (font[c * 16 + y * 2] >> (7 - x)) & (font[c * 16 + y * 2 + 1] >> (7 - x)) & 1}
        if px:
            out[chr(c)] = (max(x for x, _ in px) + 1, px)
    out[" "] = (3, set())
    return out
# id: [sign, ...]; rect = (x0, y0, x1, y1) exclusive, sheet pixels
SIGNS = {
    102: [dict(rect=(5, 17, 85, 48), lines=["EDUCATIONAL", "SOFTWARE"], font="bold", shadow=False)],
    114: [dict(rect=(2, 24, 63, 48), lines=["DINER"], font="black", shadow=False)],
    115: [dict(rect=(97, 33, 126, 47), lines=["CLOSING", "SALE"], font="tiny", shadow=False),
          dict(rect=(67, 52, 78, 60), lines=["OFF"], font="tiny", shadow=False)],
    116: [dict(rect=(97, 33, 126, 47), lines=["CLOSING", "SALE"], font="tiny", shadow=False),
          dict(rect=(67, 52, 78, 60), lines=["OFF"], font="tiny", shadow=False)],
    120: [dict(rect=(3, 18, 124, 44), lines=["SPORTS SHOP"], font="impact", shadow=True)],
    149: [dict(rect=(71, 141, 122, 155), lines=["ARUMA SPA"], font="bold", shadow=False),
          dict(rect=(3, 259, 78, 275), lines=["SPA TOWN"], font="game", shadow=False, fg=15, outline=1),
          dict(rect=(3, 275, 56, 285), lines=["ALMANIC!!"], font="bold", shadow=False, fg=15, outline=1),
          dict(rect=(3, 305, 14, 358), lines=list("NO KIDS!"), font="tiny", shadow=False, vertical=True, fg=15, outline=1),
          dict(rect=(35, 311, 90, 327), lines=["SEXY LANE"], font="bold", shadow=False, fg=10)],
    37: [dict(rect=(70, 241, 94, 248), lines=["LIVE!"], font="tiny", shadow=False)],
    193: [dict(rect=(0, 0, 16, 16), lines=["BRA", "IN"], font="tiny"),   # 2bpp 16x16 organ labels
          dict(rect=(16, 0, 32, 16), lines=["LUNG"], font="tiny"),
          dict(rect=(32, 0, 48, 16), lines=["STOM", "ACH"], font="tiny"),
          dict(rect=(48, 0, 80, 16), lines=["LIVER"], font="tiny"),
          dict(rect=(80, 0, 112, 16), lines=["GALL", "BLADDER"], font="tiny"),
          dict(rect=(112, 0, 128, 16), lines=["KID", "NEY"], font="tiny"),
          dict(rect=(0, 16, 16, 32), lines=["PANC", "REAS"], font="tiny"),
          dict(rect=(16, 16, 32, 32), lines=["SPLE", "EN"], font="tiny"),
          dict(rect=(32, 16, 64, 32), lines=["BLADDER"], font="tiny"),
          dict(rect=(64, 16, 80, 32), lines=["GUTS"], font="tiny"),
          dict(rect=(112, 16, 128, 32), lines=["HE", "ART"], font="tiny")],
    200: [dict(rect=(18, 2, 61, 13), lines=["HEY!"], font="bold", shadow=False),
          dict(rect=(66, 2, 85, 13), lines=["HI"], font="bold", shadow=False),
          dict(rect=(4, 22, 42, 38), lines=["SUMMON"], font="bold", shadow=False)],
    15: [dict(rect=(0, 0, 32, 16), lines=["WHIFF"], font="bold", shadow=False)],
    16: [dict(rect=(0, 0, 32, 16), lines=["WHIFF"], font="bold", shadow=False)],
}


def get(data, x, y, bpp=4):
    base = ((y // 8) * 16 + x // 8) * 8 * bpp
    return sum(((data[base + (p // 2) * 16 + (y % 8) * 2 + (p & 1)] >> (7 - x % 8)) & 1) << p for p in range(bpp))


def put(data, x, y, v, bpp=4):
    base = ((y // 8) * 16 + x // 8) * 8 * bpp
    for p in range(bpp):
        i = base + (p // 2) * 16 + (y % 8) * 2 + (p & 1)
        data[i] = (data[i] & ~(0x80 >> (x % 8))) | (((v >> p) & 1) << (7 - x % 8))


def text_mask(lines, font, w, h, vertical=False):
    """Set of (x, y) pixels of the text centred in a w x h box (1-bit, no antialiasing)."""
    if font == "game":
        g = game_glyphs()
        total_h = 7 * len(lines) + (len(lines) - 1)
        pts = set()
        for k, line in enumerate(lines):
            lw = sum(g[ch][0] + 1 for ch in line) - 1
            ox, oy = (w - lw) // 2, (h - total_h) // 2 + 8 * k
            for ch in line:
                cw, px = g[ch]
                pts |= {(ox + x, oy + y) for x, y in px}
                ox += cw + 1
        return pts
    if font == "tiny":
        rows = []
        if vertical:
            gap = max(0, (h - 5 * len(lines)) // max(1, len(lines) - 1))
            for k, ch in enumerate(lines):
                bits = TINY[ch]
                oy = k * (5 + gap)
                for i, b in enumerate(bits):
                    if b == "1":
                        for sx in range(2):  # double width for narrow vertical signs
                            rows.append(((i % 3) * 2 + sx + (w - 6) // 2, oy + i // 3))
            return set(rows)
        total_h = 5 * len(lines) + (len(lines) - 1)
        for k, line in enumerate(lines):
            lw = 4 * len(line) - 1
            ox, oy = (w - lw) // 2, (h - total_h) // 2 + 6 * k
            for c, ch in enumerate(line):
                for i, b in enumerate(TINY[ch]):
                    if b == "1":
                        rows.append((ox + c * 4 + i % 3, oy + i // 3))
        return set(rows)
    for size in range(40, 5, -1):
        f = ImageFont.truetype(FONTS[font], size)
        boxes = [f.getbbox(l) for l in lines]
        lh = max(b[3] - b[1] for b in boxes)
        total = lh * len(lines) + (len(lines) - 1)
        if max(b[2] - b[0] for b in boxes) <= w - 1 and total <= h - 1:
            break
    img = Image.new("1", (w, h))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    y = (h - total) // 2
    for line, b in zip(lines, boxes):
        d.text(((w - (b[2] - b[0])) // 2 - b[0], y - b[1]), line, font=f, fill=1)
        y += lh + 1
    return {(x, yy) for yy in range(h) for x in range(w) if img.getpixel((x, yy))}


def paint(data, sign, bpp=4):
    x0, y0, x1, y1 = sign["rect"]
    counts = Counter(get(data, x, y, bpp) for y in range(y0, y1) for x in range(x0, x1))
    order = [v for v, _ in counts.most_common()]
    bg, fg = order[0], sign.get("fg", order[1])        # "fg"/"outline": explicit indices where needed
    shadow = order[2] if sign.get("shadow") and len(order) > 2 else None
    outline = sign.get("outline")
    mask = text_mask(sign["lines"], sign["font"], x1 - x0, y1 - y0, sign.get("vertical", False))
    ring = {(x + dx, y + dy) for x, y in mask for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))} - mask
    for y in range(y0, y1):
        for x in range(x0, x1):
            p = (x - x0, y - y0)
            if p in mask:
                v = fg
            elif outline is not None and p in ring:
                v = outline
            elif shadow is not None and (p[0] - 1, p[1] - 1) in mask:
                v = shadow
            else:
                v = bg
            put(data, x, y, v, bpp)


def blocks(rom):
    """{gfx id: (src cpu address, decompressed data, compressed size)} for the ids in SIGNS."""
    out = {}
    for i in SIGNS:
        bank = rom[titlegfx.BLOCK_ID_BANKS - 0x8000 + i]
        addr = int.from_bytes(rom[titlegfx.BLOCK_ID_ADDRS - 0x8000 + 2 * i:][:2], "little")
        src = bank << 16 | addr
        data, used = lz.decompress(rom, titlegfx.file_off(src))
        out[i] = (src, bytearray(data), used)
    return out


def apply(rom, reloc):
    """Paint every sign and write the blocks back (in place, or relocated from `reloc`). Returns next reloc."""
    for i, (src, data, used) in blocks(rom).items():
        for s in SIGNS[i]:
            paint(data, s, BPP.get(i, 4))
        reloc = titlegfx.put_block(rom, i, src, data, used, reloc)
    return reloc


def preview():
    import gfxsurvey
    rom = (ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc").read_bytes()
    out = ROOT / "work" / "signs"
    out.mkdir(parents=True, exist_ok=True)
    for i, (src, data, used) in blocks(rom).items():
        before = gfxsurvey.sheet(bytes(data), BPP.get(i, 4))
        for s in SIGNS[i]:
            paint(data, s, BPP.get(i, 4))
        after = gfxsurvey.sheet(bytes(data), BPP.get(i, 4))
        ys = [s["rect"][1] for s in SIGNS[i]] + [s["rect"][3] for s in SIGNS[i]]
        top, bot = max(0, min(ys) - 4), min(before.height, max(ys) + 4)
        img = Image.new("L", (264, bot - top), 60)
        img.paste(before.crop((0, top, 128, bot)), (0, 0))
        img.paste(after.crop((0, top, 128, bot)), (136, 0))
        img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(out / f"{i}.png")
    print("wrote", out)


if __name__ == "__main__":
    {"preview": preview}[sys.argv[1]]()
