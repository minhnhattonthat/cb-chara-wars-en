import json, os, re, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import text  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not text.ROM.exists(), reason="original ROM not present")
BLOCKS = ["dialogue", "items", "menus"]


def load(block):
    return json.loads((text.SCRIPT_DIR / f"{block}.json").read_text(encoding="utf-8"))


@needs_rom
def test_roundtrip():
    assert text.roundtrip()


@needs_rom
@pytest.mark.parametrize("block", BLOCKS)
def test_json_matches_rom_and_covers_block(block):
    rom, table = text.ROM.read_bytes(), Table.load(text.JP_TBL)
    strings = text.all_blocks(rom, table)[block]
    assert [(e["off"], e["jp"]) for e in load(block)] == [(f"{o:06X}", t) for o, _, t, _ in strings]
    # coverage: strings tile their region; gaps may only hold this block's pointer tables and 00 padding
    tables = [(t, t + 2 * n) for t, n in text.PTR16.get(block, (0, []))[1]]
    for (o1, n1, _, _), (o2, _, _, _) in zip(strings, strings[1:]):
        rest = [i for i in range(o1 + n1, o2) if not any(a <= i < b for a, b in tables) and rom[i] != 0]
        assert not rest, f"{block}: unexplained bytes {o1 + n1:06X}-{o2:06X}"
    if block == "dialogue":
        assert strings[0][0] == text.SCRIPT_LO and strings[-1][0] + strings[-1][1] == text.SCRIPT_HI


@pytest.mark.parametrize("block", BLOCKS)
def test_no_unknown_codes_in_jp(block):
    assert not [e["id"] for e in load(block) if re.search(r"\[[0-9A-F]{2}\]", e["jp"])]
