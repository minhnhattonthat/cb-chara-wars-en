"""Render raw SNES tiles (2bpp or 4bpp planar) as a greyscale sheet, 16 tiles per row, tile numbers every row.

    python -X utf8 tools/tilesheet.py IN.bin OUT.png [--bpp 4] [--scale 2]
    python -X utf8 tools/tilesheet.py ROM OUT.png --at D0000 --len 2000 --bpp 2
"""
import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw



def tile(data, n, bpp):
    base = n * 8 * bpp
    return [[sum(((data[base + (p // 2) * 16 + y * 2 + (p & 1)] >> (7 - x)) & 1) << p for p in range(bpp))
             for x in range(8)] for y in range(8)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--bpp", type=int, default=4)
    ap.add_argument("--scale", type=int, default=2)
    ap.add_argument("--at", type=lambda s: int(s, 16), default=0)
    ap.add_argument("--len", type=lambda s: int(s, 16))
    a = ap.parse_args()
    data = Path(a.src).read_bytes()
    data = data[a.at:a.at + a.len if a.len else None]
    count = len(data) // (8 * a.bpp)
    rows = (count + 15) // 16
    s = a.scale
    img = Image.new("L", (16 * 8 * s + 30, rows * 8 * s), 40)
    d = ImageDraw.Draw(img)
    for n in range(count):
        t = tile(data, n, a.bpp)
        x0, y0 = 30 + (n % 16) * 8 * s, (n // 16) * 8 * s
        for y in range(8):
            for x in range(8):
                v = t[y][x] * 255 // ((1 << a.bpp) - 1)
                d.rectangle([x0 + x * s, y0 + y * s, x0 + x * s + s - 1, y0 + y * s + s - 1], fill=v)
        if n % 16 == 0:
            d.text((0, y0), f"{n:03X}", fill=255)
    img.save(a.out)


if __name__ == "__main__":
    main()
