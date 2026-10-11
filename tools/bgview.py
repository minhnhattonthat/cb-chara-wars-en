"""Render one BG layer from a VRAM dump (tools/lua/vramdump.lua) in greyscale, and/or print its tile numbers.

    python -X utf8 tools/bgview.py VRAM.bin --map 0x4000 --chr 0x6000 [--bpp 4] [--out bg.png] [--rows 18-24]
Addresses are VRAM word addresses (as Mesen's ppu.txt prints them, in decimal there).
"""
import argparse

from PIL import Image


def tile_px(vram, chr_word, bpp, n):
    base = chr_word * 2 + n * 8 * bpp
    rows = []
    for y in range(8):
        row = []
        for x in range(8):
            v = 0
            for p in range(bpp):
                b = vram[(base + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF]
                v |= ((b >> (7 - x)) & 1) << p
            row.append(v)
        rows.append(row)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vram")
    ap.add_argument("--map", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--chr", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--bpp", type=int, default=4)
    ap.add_argument("--out")
    ap.add_argument("--rows", help="print tilemap entries for rows a-b")
    a = ap.parse_args()
    vram = open(a.vram, "rb").read()
    img = Image.new("L", (256, 256))
    scale = 255 // ((1 << a.bpp) - 1)
    for ty in range(32):
        for tx in range(32):
            o = (a.map * 2 + (ty * 32 + tx) * 2) & 0xFFFF
            e = vram[o] | vram[o + 1] << 8
            px = tile_px(vram, a.chr, a.bpp, e & 0x3FF)
            for y in range(8):
                for x in range(8):
                    sx = 7 - x if e & 0x4000 else x
                    sy = 7 - y if e & 0x8000 else y
                    img.putpixel((tx * 8 + x, ty * 8 + y), px[sy][sx] * scale)
    if a.out:
        img.resize((512, 512), Image.NEAREST).save(a.out)
    if a.rows:
        lo, hi = map(int, a.rows.split("-"))
        for ty in range(lo, hi + 1):
            o = a.map * 2 + ty * 64
            print(f"{ty:2d}", " ".join(f"{(vram[o + 2 * x] | vram[o + 2 * x + 1] << 8):04X}" for x in range(32)))


if __name__ == "__main__":
    main()
