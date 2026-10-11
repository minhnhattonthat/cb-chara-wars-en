import os, zlib

import pytest

ROM = os.path.join(os.path.dirname(__file__), "..", "rom", "CB Chara Wars - Ushinawareta Gag (Japan).sfc")


@pytest.mark.skipif(not os.path.exists(ROM), reason="original ROM not present")
def test_original_rom_crc():
    assert zlib.crc32(open(ROM, "rb").read()) == 0x85AC87D5
