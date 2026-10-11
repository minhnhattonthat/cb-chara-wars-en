"""Render a BG layer from Mesen dumps (tools/lua/dumpmem.lua) in real colours; optional tile-number grid.

    python -X utf8 tools/bgrender.py DIR/FRAME --map 0x7000 --chr 0x2000 [--bpp 4] [--big] [--out bg.png] [--nums]
--map/--chr are VRAM word addresses (Mesen ppu.txt prints them in decimal). --big = 16x16 tiles.
--nums prints the 32x32 tilemap entries (tile number + palette) instead of only rendering.
"""
import argparse, struct
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix", help="dump prefix, e.g. work/qa/title/1290")
    ap.add_argument("--map", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--chr", type=lambda s: int(s, 0), required=True)
    ap.add_argument("--bpp", type=int, default=4)
    ap.add_argument("--big", action="store_true")
    ap.add_argument("--out", default=None)
    ap.add_argument("--nums", action="store_true")
    ap.add_argument("--wide", action="store_true", help="64x32 map (second 32x32 screen follows the first)")
    a = ap.parse_args()
    vram = open(a.prefix + "_vram.bin", "rb").read()
    cg = open(a.prefix + "_cgram.bin", "rb").read()
    pal = []
    for i in range(256):
        c = struct.unpack_from("<H", cg, i * 2)[0]
        pal.append(((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3))
    ts = 16 if a.big else 8
    cols = 64 if a.wide else 32
    img = Image.new("RGB", (cols * ts, 32 * ts))

    def put8(tile, palno, hf, vf, ox, oy):
        base = a.chr * 2 + tile * 8 * a.bpp
        for y in range(8):
            for x in range(8):
                v = 0
                for p in range(a.bpp):
                    b = vram[(base + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF]
                    v |= ((b >> (7 - x)) & 1) << p
                if v:
                    px, py = (7 - x if hf else x), (7 - y if vf else y)
                    img.putpixel((ox + px, oy + py), pal[(palno << a.bpp) + v if a.bpp < 8 else v])

    grid = []
    for r in range(32):
        row = []
        for c in range(cols):
            idx = (c // 32) * 1024 + r * 32 + c % 32
            e = struct.unpack_from("<H", vram, (a.map * 2 + idx * 2) & 0xFFFF)[0]
            t, palno, hf, vf = e & 0x3FF, (e >> 10) & 7, e >> 14 & 1, e >> 15 & 1
            row.append(f"{t:03X}{palno}")
            if a.big:
                for dy in range(2):
                    for dx in range(2):
                        sx, sy = (1 - dx if hf else dx), (1 - dy if vf else dy)
                        put8(t + sx + 16 * sy, palno, hf, vf, c * 16 + dx * 8, r * 16 + dy * 8)
            else:
                put8(t, palno, hf, vf, c * 8, r * 8)
        grid.append(" ".join(row))
    if a.out:
        img.save(a.out)
    if a.nums:
        print("\n".join(f"{i:2d} {g}" for i, g in enumerate(grid)))


if __name__ == "__main__":
    main()
