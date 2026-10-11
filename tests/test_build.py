import json, os, sys

import pytest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import build  # noqa: E402
import text  # noqa: E402

needs_rom = pytest.mark.skipif(not text.ROM.exists(), reason="original ROM not present")


@needs_rom
def test_identity_build(tmp_path, monkeypatch):
    """With every `en` blank, the build must reproduce the original ROM byte for byte."""
    real = build.load
    monkeypatch.setattr(build, "load", lambda b: [dict(e, en="") for e in real(b)])
    out = build.build(tmp_path / "id.sfc")
    assert bytes(out) == text.ROM.read_bytes()


@needs_rom
def test_marker_build_relocates_dialogue(tmp_path):
    rom = build.build(tmp_path / "m.sfc", marker=True)
    assert len(rom) == 0x200000 and rom[build.HEADER_SIZE] == 0x0B
    assert all(rom[op] == build.DIALOGUE_BANK for op in build.ENGINE_BANK_OPERANDS)
    # every dialogue pointer slot now points into bank $20 at a message start
    for e in json.loads((text.SCRIPT_DIR / "dialogue.json").read_text(encoding="utf-8")):
        for s in e["slots"]:
            s = int(s, 16)
            assert rom[s + 2] == build.DIALOGUE_BANK
