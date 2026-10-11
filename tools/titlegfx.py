"""Title logo: replace the katakana キャラウォーズ (BG1 outline + BG2 gradient fill, 16x16 4bpp tiles from LZ block
$1E:D0E2) with English art, drawn into the tiles the original tilemaps already use (no tilemap changes).

    python -X utf8 tools/titlegfx.py coverage   # preview which screen pixels each layer can draw (work/title_cov.png)
    python -X utf8 tools/titlegfx.py preview    # render the new logo composite (work/title_new.png)
Screen geometry comes from a title-screen dump (work/qa/title/1600_*, tools/lua/dumpmem.lua at frame 1600):
BG1 map $7000 scroll (256, 271); BG2 map $7400 (64x32) scroll (776, 263).
"""
import struct, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402

BLOCK = 0x1ED0E2
BLOCK_ID_BANKS, BLOCK_ID_ADDRS = 0xF9C7, 0xFAB2      # $00:F9C7 bank bytes, $00:FAB2 address words, by gfx id
DUMP = ROOT / "work" / "qa" / "title" / "1600"
LAYERS = {"bg1": dict(map=0x7000, wide=False, scroll=(256, 271)),
          "bg2": dict(map=0x7400, wide=True, scroll=(776, 263))}
AREA = (84, 36, 256, 100)  # screen box (x0, y0, x1, y1) the logo may use


def file_off(a):
    return ((a >> 16) & 0x7F) * 0x8000 + (a & 0x7FFF)


def layer_cells(vram, name):
    """{(screen x, screen y) of each pixel in area: (tile8 index, px, py, hflip, vflip, palette)}"""
    L = LAYERS[name]
    cols = 64 if L["wide"] else 32
    out = {}
    x0, y0, x1, y1 = AREA
    for sy in range(y0, y1):
        for sx in range(x0, x1):
            mx = (sx + L["scroll"][0]) % (cols * 16)
            my = (sy + L["scroll"][1]) % 512
            c, r = mx // 16, my // 16
            idx = (c // 32) * 1024 + r * 32 + c % 32
            e = struct.unpack_from("<H", vram, L["map"] * 2 + idx * 2)[0]
            t = e & 0x3FF
            if t == 0:
                continue
            hf, vf = e >> 14 & 1, e >> 15 & 1
            ix, iy = mx % 16, my % 16
            if hf:
                ix = 15 - ix
            if vf:
                iy = 15 - iy
            out[(sx, sy)] = (t + ix // 8 + 16 * (iy // 8), ix % 8, iy % 8, (e >> 10) & 7)
    return out


def get_px(data, t, x, y):
    base = t * 32
    return sum(((data[base + (p // 2) * 16 + y * 2 + (p & 1)] >> (7 - x)) & 1) << p for p in range(4))


def set_px(data, t, x, y, v):
    base = t * 32
    for p in range(4):
        i = base + (p // 2) * 16 + y * 2 + (p & 1)
        data[i] = (data[i] & ~(0x80 >> x)) | (((v >> p) & 1) << (7 - x))


def coverage():
    from PIL import Image
    vram = (DUMP.parent / "1600_vram.bin").read_bytes()
    img = Image.new("RGB", (256, 224))
    for name, col in (("bg1", (0, 120, 255)), ("bg2", (255, 80, 0))):
        for (sx, sy) in layer_cells(vram, name):
            r, g, b = img.getpixel((sx, sy))
            img.putpixel((sx, sy), (max(r, col[0]), max(g, col[1]), max(b, col[2])))
    img.resize((768, 672)).save(ROOT / "work" / "title_cov.png")


TEXT, FONT = "CHARA WARS", "C:/Windows/Fonts/impact.ttf"
BOX = (90, 44, 246, 86)    # where the new letters go (inside both layers' coverage)
SHEAR = 0.28               # italic slant like the original


def letters_mask():
    """Binary mask (set of (x, y)) of the slanted text fitted into BOX."""
    from PIL import Image, ImageDraw, ImageFont
    x0, y0, x1, y1 = BOX
    w, h = x1 - x0, y1 - y0
    for size in range(60, 10, -1):
        f = ImageFont.truetype(FONT, size)
        l, t, r, b = f.getbbox(TEXT)
        tw, th = r - l + int((b - t) * SHEAR) + 2, b - t
        if tw <= w and th <= h:
            break
    img = Image.new("L", (tw + 8, th + 8))
    ImageDraw.Draw(img).text((4 - l + int(th * SHEAR), 4 - t), TEXT, font=f, fill=255)
    img = img.transform(img.size, Image.AFFINE, (1, SHEAR, 0, 0, 1, 0), Image.BICUBIC)  # x' = x + s*y: lean right
    ox = x0 + (w - img.width) // 2
    oy = y0 + (h - img.height) // 2
    return {(ox + x, oy + y) for y in range(img.height) for x in range(img.width) if img.getpixel((x, y)) >= 128}


def fill_index_by_row(vram, data):
    """Most common BG2 fill index per screen row in the original logo (the baked gradient)."""
    from collections import Counter, defaultdict
    rows = defaultdict(Counter)
    for (sx, sy), (t, x, y, p) in layer_cells(vram, "bg2").items():
        i = get_px(data, t, x, y)
        if i:
            rows[sy][i] += 1
    known = {y: c.most_common(1)[0][0] for y, c in rows.items()}
    ys = sorted(known)
    return lambda y: known[min(ys, key=lambda k: abs(k - y))]


def draw(vram, data):
    """Return new tile data (bytearray) with the English logo drawn into the BG1/BG2 logo tiles."""
    data = bytearray(data)
    fill_of = fill_index_by_row(vram, data)
    mask = letters_mask()
    ring = {(x + dx, y + dy) for (x, y) in mask for dx in range(-2, 3) for dy in range(-2, 3)
            if abs(dx) + abs(dy) <= 3} - mask
    bg1, bg2 = layer_cells(vram, "bg1"), layer_cells(vram, "bg2")
    lost = [p for p in mask if p not in bg2] + [p for p in ring if p not in bg1]
    assert not lost, f"{len(lost)} logo pixels outside the existing tiles, e.g. {lost[:5]}"
    for (sx, sy), (t, x, y, p) in bg2.items():
        set_px(data, t, x, y, fill_of(sy) if (sx, sy) in mask else 0)
    for (sx, sy), (t, x, y, p) in bg1.items():
        if (sx, sy) not in ring:
            v = 0
        else:  # shade by which side of the letter this outline pixel sits on (light from top-left)
            near = [(mx - sx, my - sy) for mx in range(sx - 3, sx + 4) for my in range(sy - 3, sy + 4)
                    if (mx, my) in mask]
            vx = sum(a for a, _ in near) / len(near)
            vy = sum(b for _, b in near) / len(near)
            d = (vx + vy) / max(0.5, (vx * vx + vy * vy) ** 0.5)       # +1.4 = letter is down-right
            v = 1 if min(abs(a) + abs(b) for a, b in near) <= 1 else max(2, min(14, round(8 + 4.5 * d)))
        set_px(data, t, x, y, v)
    return data


def load_block(rom):
    return lz.decompress(rom, file_off(BLOCK))


# Subtitle 失われたギャ〜グ: OBJ palette 2 sprites from block $1D:CBF4 (gfx id 165), tiles 0-31 at OBJ base 0.
SUB_BLOCK, SUB_ID, LOGO_ID = 0x1DCBF4, 165, 130
SUB_TEXT, SUB_FONT = "The Lost Gaaag", "C:/Windows/Fonts/ariblk.ttf"
SUB_BOX = (104, 88, 208, 104)    # 8x8 column at x=104 (tiles 3/19) + six 16x16 sprites (tiles 4..15 / 20..31)
FILL, SHADOW, EDGE = 15, 13, 12  # yellow, black drop shadow, dark-yellow edge


def sub_tile_at(sx, sy):
    """(tile, px, py) of the subtitle sprite pixel at screen (sx, sy) inside SUB_BOX."""
    x, y = sx - 104, sy - 88
    if x < 8:
        return (3 if y < 8 else 19), x, y % 8
    k, ix = divmod(x - 8, 16)
    return 4 + 2 * k + ix // 8 + 16 * (y // 8), ix % 8, y % 8


def draw_subtitle(data):
    from PIL import Image, ImageDraw, ImageFont
    data = bytearray(data)
    x0, y0, x1, y1 = SUB_BOX
    w, h = x1 - x0 - 1, y1 - y0 - 1       # leave a pixel for the drop shadow
    for size in range(20, 6, -1):
        f = ImageFont.truetype(SUB_FONT, size)
        l, t, r, b = f.getbbox(SUB_TEXT)
        if r - l <= w and b - t <= h:
            break
    img = Image.new("L", (w, h))
    ImageDraw.Draw(img).text(((w - (r - l)) // 2 - l, (h - (b - t)) // 2 - t), SUB_TEXT, font=f, fill=255)
    core = {(x, y) for y in range(h) for x in range(w) if img.getpixel((x, y)) >= 140}
    edge = {(x, y) for y in range(h) for x in range(w) if 60 <= img.getpixel((x, y)) < 140}
    for sy in range(y0, y1):
        for sx in range(x0, x1):
            p = (sx - x0, sy - y0)
            q = (p[0] - 1, p[1] - 1)
            v = FILL if p in core else EDGE if p in edge else SHADOW if (q in core or q in edge) else 0
            t, x, y = sub_tile_at(sx, sy)
            set_px(data, t, x, y, v)
    for x in range(8):                     # tile 0 was the グ dakuten above the last sprite
        for y in range(8):
            set_px(data, 0, x, y, 0)
    return data


RELOC_FILE, RELOC_BANK = 0x110000, 0x22   # $22:8000 for blocks that outgrow their slot


def put_block(rom, gfx_id, src, new_data, old_used, reloc):
    packed = lz.compress(bytes(new_data))
    if len(packed) <= old_used:
        rom[file_off(src):file_off(src) + len(packed)] = packed
        return reloc
    rom[reloc:reloc + len(packed)] = packed
    cpu = 0x8000 + reloc - RELOC_FILE
    rom[BLOCK_ID_BANKS - 0x8000 + gfx_id] = RELOC_BANK
    rom[BLOCK_ID_ADDRS - 0x8000 + 2 * gfx_id:BLOCK_ID_ADDRS - 0x8000 + 2 * gfx_id + 2] = cpu.to_bytes(2, "little")
    return reloc + len(packed)


MAPS = ROOT / "data" / "title_maps.bin"  # title-screen VRAM $E000-$F7FF (BG1 $7000 + BG2 $7400 64x32 tilemaps)


def map_vram():
    vram = bytearray(0x10000)
    vram[0xE000:0xF800] = MAPS.read_bytes()
    return vram


def apply(rom):
    """English build: new logo + subtitle drawn into their LZ blocks (geometry from data/title_maps.bin)."""
    assert rom[BLOCK_ID_BANKS - 0x8000 + LOGO_ID] == BLOCK >> 16
    vram = map_vram()
    logo, used = lz.decompress(rom, file_off(BLOCK))
    sub, sub_used = lz.decompress(rom, file_off(SUB_BLOCK))
    reloc = put_block(rom, LOGO_ID, BLOCK, draw(vram, logo), used, RELOC_FILE)
    put_block(rom, SUB_ID, SUB_BLOCK, draw_subtitle(sub), sub_used, reloc)


def preview():
    from PIL import Image
    vram = bytearray((DUMP.parent / "1600_vram.bin").read_bytes())
    cg = (DUMP.parent / "1600_cgram.bin").read_bytes()
    rom = (ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc").read_bytes()
    data, _ = load_block(rom)
    assert vram[0x4000:0x4000 + len(data)] == data, "dump VRAM differs from the LZ block"
    new = draw(vram, data)
    pal = [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3) for c in struct.unpack("<256H", cg)]
    img = Image.new("RGB", (256, 112), (120, 80, 56))
    for name in ("bg2", "bg1"):
        for (sx, sy), (t, x, y, p) in layer_cells(vram, name).items():
            i = get_px(new, t, x, y)
            if i and sy < 112:
                img.putpixel((sx, sy), pal[p * 16 + i])
    img.resize((1024, 448), Image.NEAREST).save(ROOT / "work" / "title_new.png")
    print("wrote work/title_new.png")


if __name__ == "__main__":
    {"coverage": coverage, "preview": preview}[sys.argv[1]]()
