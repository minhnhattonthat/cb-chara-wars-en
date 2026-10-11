"""Render the sprites from Mesen dumps (dumpmem.lua: _vram/_cgram/_oam) onto a 256x224 canvas and list them.

    python -X utf8 tools/oamrender.py work/qa/title/1600 [--base 0] [--gap 0x1000] [--mode 0] [--out obj.png] [--list]
--base / --gap: OBJ char base and second-table offset, VRAM words (ppu.oamBaseAddress / ppu.oamAddressOffset).
"""
import argparse, struct
from PIL import Image

SIZES = {0: ((8, 8), (16, 16)), 1: ((8, 8), (32, 32)), 2: ((8, 8), (64, 64)), 3: ((16, 16), (32, 32)),
         4: ((16, 16), (64, 64)), 5: ((32, 32), (64, 64))}


def sprites(oam, mode):
    out = []
    for i in range(128):
        x, y, t, attr = oam[i * 4:i * 4 + 4]
        hi = (oam[512 + i // 4] >> ((i % 4) * 2)) & 3
        x |= (hi & 1) << 8
        if x >= 256:
            x -= 512
        size = SIZES[mode][hi >> 1]
        out.append(dict(i=i, x=x, y=y, tile=t | ((attr & 1) << 8), pal=(attr >> 1) & 7, prio=(attr >> 4) & 3,
                        hf=attr >> 6 & 1, vf=attr >> 7 & 1, w=size[0], h=size[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prefix")
    ap.add_argument("--base", type=lambda s: int(s, 0), default=0)
    ap.add_argument("--gap", type=lambda s: int(s, 0), default=0x1000)
    ap.add_argument("--mode", type=int, default=0)
    ap.add_argument("--out")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    vram = open(a.prefix + "_vram.bin", "rb").read()
    cg = open(a.prefix + "_cgram.bin", "rb").read()
    oam = open(a.prefix + "_oam.bin", "rb").read()
    pal = [((c & 31) << 3, ((c >> 5) & 31) << 3, ((c >> 10) & 31) << 3)
           for c in struct.unpack("<256H", cg)]
    img = Image.new("RGB", (256, 256), (40, 0, 40))
    for s in reversed(sprites(oam, a.mode)):
        if s["y"] >= 224 and s["y"] + s["h"] <= 256:
            continue
        for ty in range(s["h"] // 8):
            for tx in range(s["w"] // 8):
                n = s["tile"]
                col = (n & 0xF) + tx
                row = (n >> 4 & 0xF) + ty
                tn = (n & 0x100) | ((row & 0xF) << 4) | (col & 0xF)
                word = a.base + (a.gap if tn & 0x100 else 0) + (tn & 0xFF) * 16
                for y in range(8):
                    for x in range(8):
                        v = 0
                        for p in range(4):
                            b = vram[(word * 2 + (p // 2) * 16 + y * 2 + (p & 1)) & 0xFFFF]
                            v |= ((b >> (7 - x)) & 1) << p
                        if not v:
                            continue
                        px = (s["w"] - 1 - (tx * 8 + x)) if s["hf"] else tx * 8 + x
                        py = (s["h"] - 1 - (ty * 8 + y)) if s["vf"] else ty * 8 + y
                        X, Y = s["x"] + px, (s["y"] + py) & 0xFF
                        if 0 <= X < 256:
                            img.putpixel((X, Y), pal[128 + s["pal"] * 16 + v])
        if a.list:
            print(s)
    if a.out:
        img.save(a.out)


if __name__ == "__main__":
    main()
