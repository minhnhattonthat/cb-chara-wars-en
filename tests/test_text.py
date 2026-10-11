import json, os, re, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import text  # noqa: E402
from tbl import Table  # noqa: E402

needs_rom = pytest.mark.skipif(not text.ROM.exists(), reason="original ROM not present")


@needs_rom
def test_dialogue_roundtrip():
    assert text.roundtrip()


@needs_rom
def test_script_json_matches_rom():
    rom, table = text.ROM.read_bytes(), Table.load(text.JP_TBL)
    entries = json.loads(text.SCRIPT.read_text(encoding="utf-8"))
    msgs = text.messages(rom, table)
    assert [(e["off"], e["jp"]) for e in entries] == [(f"{o:06X}", t) for o, _, t in msgs]
    # coverage: messages tile the script region with no gaps
    assert msgs[0][0] == text.SCRIPT_LO and msgs[-1][0] + msgs[-1][1] == text.SCRIPT_HI


def test_no_unknown_codes_in_jp():
    entries = json.loads(text.SCRIPT.read_text(encoding="utf-8"))
    assert not [e["id"] for e in entries if re.search(r"\[[0-9A-F]{2}\]", e["jp"])]
