"""Dialogue word wrap for the widened box: 28 columns, 4 lines per page (the engine pages after line 4).

English text is written as paragraphs: `{n}` forces a line break, `{p}` starts a new page, other `{...}` codes
take no space. wrap() returns text with every break as `{n}`, ready for the en table.

    python -X utf8 tools/wrap.py "{fd:04}Some long English line ... {p}Next page"   # preview the box layout
"""
import re
import sys

WIDTH, LINES = 28, 4
TOKEN = re.compile(r"(\{[a-z0-9]+(?::[0-9A-F]+)?\})")
# Two windows: "wide" = widened box 0 (28 cols, 4 lines); "shop" = portrait + right window (cols 12-29, 5 lines),
# used by table 07:8D4A messages unless a cutscene flag picks the wide box ($07:E380). "both" fits either.
BOXES = {"wide": (28, 4), "shop": (18, 5), "both": (18, 4)}
WIDE_8D4A = {"D130", "D131", "D132", "D133"}  # intro cutscene: wide box (seen in game)
T8BCA = range(0x38BCA, 0x38BCA + 115 * 3)
T8D4A = range(0x38D4A, 0x38D4A + 58 * 3)


def box_of(entry):
    tables = {("8BCA" if int(s, 16) in T8BCA else "8D4A") for s in entry["slots"]}
    if tables == {"8D4A"}:
        # $07:E380 picks the box at runtime ($32 bit 4 / $33 >= 9 -> wide), so unverified ones must fit both
        return "wide" if entry["id"] in WIDE_8D4A else "both"
    return "both" if len(tables) == 2 else "wide"


def visible_len(s):
    return len(TOKEN.sub("", s))


def wrap_paragraph(par, width=WIDTH):
    """Balanced wrap: fewest lines (greedy count), then the most even line lengths."""
    words = par.split(" ")
    if not par:
        return [""]
    lens = [visible_len(w) for w in words]
    n = len(words)
    # cost[i] = (lines, raggedness) for words[i:]
    best = [(0, 0, n)] * (n + 1)
    for i in range(n - 1, -1, -1):
        cand = None
        width_so_far = -1
        for j in range(i, n):
            width_so_far += lens[j] + 1
            if width_so_far > width and j > i:
                break
            rest = best[j + 1]
            slack = 0 if j == n - 1 else (width - width_so_far) ** 2
            c = (rest[0] + 1, rest[1] + slack, j + 1)
            if cand is None or c[:2] < cand[:2]:
                cand = c
        best[i] = cand
    lines, i = [], 0
    while i < n:
        j = best[i][2]
        lines.append(" ".join(words[i:j]))
        i = j
    return lines


def layout(text, width=WIDTH, lines_per_page=LINES):
    """-> list of pages, each a list of lines (strings may contain zero-width control codes)."""
    body = text[:-5] if text.endswith("{end}") else text
    pages = []
    for page in body.split("{p}"):
        out = []
        for par in page.split("{n}"):
            out += wrap_paragraph(par.strip(" "), width)
        while out:
            pages.append(out[:lines_per_page])
            out = out[lines_per_page:]
    return pages


def wrap(text, width=WIDTH, lines_per_page=LINES):
    """Paragraph text -> engine text: lines joined with {n}, pages padded so each starts a new box."""
    pages = layout(text, width, lines_per_page)
    out = []
    for k, page in enumerate(pages):
        out.append("{n}".join(page))
        if k < len(pages) - 1:
            out.append("{n}" * (lines_per_page - len(page) + 1))
    return "".join(out) + ("{end}" if text.endswith("{end}") else "")


if __name__ == "__main__":
    for k, page in enumerate(layout(sys.argv[1])):
        print(f"-- page {k + 1}")
        for line in page:
            print(f"|{TOKEN.sub('', line):<{WIDTH}}| {visible_len(line)}")
