"""Decompress every LZ graphics block in the id table ($00:F9C7 banks / $00:FAB2 addresses) and render contact
pages of 4bpp tile sheets, to spot Japanese drawn as graphics.

    python -X utf8 tools/gfxsurvey.py OUTDIR [--per-page 8]   -> OUTDIR/page_NN.png + OUTDIR/index.txt
"""
import argparse, sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lz  # noqa: E402

N_IDS, BANKS, ADDRS = 235, 0xF9C7 - 0x8000, 0xFAB2 - 0x8000


def blocks(rom):
    for i in range(N_IDS):
        bank = rom[BANKS + i]
        addr = rom[ADDRS + 2 * i] | rom[ADDRS + 2 * i + 1] << 8
        off = (bank & 0x7F) * 0x8000 + (addr & 0x7FFF)
        try:
            data, used = lz.decompress(rom, off)
        except Exception:
            continue
        if 0 < len(data) <= 0x10000:
            yield i, bank << 16 | addr, data


def sheet(data, bpp=4, cols=16):
    n = len(data) // (8 * bpp)
    rows = (n + cols - 1) // cols
    img = Image.new("L", (cols * 8, rows * 8))
    for t in range(n):
        base = t * 8 * bpp
        for y in range(8):
            for x in range(8):
                v = sum(((data[base + (p // 2) * 16 + y * 2 + (p & 1)] >> (7 - x)) & 1) << p for p in range(bpp))
                img.putpixel((t % cols * 8 + x, t // cols * 8 + y), v * 17)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--per-page", type=int, default=8)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rom = (ROOT / "rom" / "CB Chara Wars - Ushinawareta Gag (Japan).sfc").read_bytes()
    items = [(i, src, sheet(d)) for i, src, d in blocks(rom)]
    idx = []
    for p in range(0, len(items), a.per_page):
        chunk = items[p:p + a.per_page]
        h = max(s.height for _, _, s in chunk) + 12
        page = Image.new("L", (136 * len(chunk), min(h, 600)), 40)
        d = ImageDraw.Draw(page)
        for k, (i, src, s) in enumerate(chunk):
            page.paste(s.crop((0, 0, 128, min(s.height, 588))), (136 * k, 12))
            d.text((136 * k, 0), f"{i}:{src:06X}", fill=255)
            idx.append(f"page {p // a.per_page:02d}  id {i:3d}  {src:06X}  {s.height // 8 * 16} tiles")
        page.save(out / f"page_{p // a.per_page:02d}.png")
    (out / "index.txt").write_text("\n".join(idx) + "\n", encoding="utf-8")
    print(f"{len(items)} blocks, {(len(items) + a.per_page - 1) // a.per_page} pages")


if __name__ == "__main__":
    main()
