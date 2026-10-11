"""Build a test ROM with one dialogue message replaced (engine experiments: width, paging, codes).

    python -X utf8 tools/testmsg.py D133 "{fd:04}0123456789ABCDEFGHIJKLMNOPQRSTUV{n}line2{end}" work/test.sfc
The first intro message is D133 (route: "1200 -;6 start;300 -;6 start;300 -" + --mash 40, text ~frame 1850+).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

mid, msg, out = sys.argv[1:4]
real = build.load
build.load = lambda b: [dict(e, en=msg) if e["id"] == mid else e for e in real(b)]
build.build(out, marker=True)  # marker everywhere else; marker=True keeps relocation + font
