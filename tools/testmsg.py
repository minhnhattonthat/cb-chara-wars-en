"""Build a test ROM with dialogue messages replaced (engine experiments: width, paging, which id shows where).

    python -X utf8 tools/testmsg.py D133 "{fd:04}0123456789ABCDEFGHIJKLMNOPQRSTUV{n}line2{end}" work/test.sfc
    python -X utf8 tools/testmsg.py D127,D128 "{fd:03}Message {id}{end}" work/test.sfc   # {id} -> each entry's id
The first intro message is D130 (route: tools/routes/shop1.txt goes on into the first shop).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

mids, msg, out = sys.argv[1:4]
ids = set(mids.split(","))
real = build.load
build.load = lambda b: [dict(e, en=msg.replace("{id}", e["id"])) if e["id"] in ids else e for e in real(b)]
build.build(out, marker=True)  # marker everywhere else; marker=True keeps relocation + font
