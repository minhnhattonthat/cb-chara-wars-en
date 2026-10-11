# RE notes index (phase 1 recon, started 2026-10-11)

Prior English patch: none found (web search, 2 queries). No known docs/tables for this game.

## ROM
- 1 MiB LoROM, slow, no SRAM, header at $7FC0 ("CB CHARA WARS"), reset vector $8000. Banks $00-$1F, no free-space runs at bank ends (no FF/00 tails) -> expect to expand to 2 MiB for English.
- Entropy: banks 04-05 low (tile maps / tables?), 08+ high (~7.1, compressed graphics probably). Banks 00-03,06-07 look like code + data.

## Dialogue engine (found by tracing; Mesen, route `1200 -;6 start;300 -;6 start;300 -` + `--mash 40`, intro dialogue ~frame 1840+)
- Routine `$06:B8D1` (file 0x338D1) is the dialogue char loop. Sets DB=$07, reads one byte at `$1EA7` (WRAM pointer; stream is `07:xxxx`, file = 0x38000 + (ptr-0x8000)).
- Codes (from the compare chain at `$06:B8EA..`): `FF` end of message (sets flag $1EA3 bit 7), `FE` newline, `FD` page/wait, `F8 nn` (arg byte -> $1EA4), `F7`, `10` (uses attr $2400), `8E`/`8F` = dakuten/handakuten marks (written to the *current* cursor slot, no cursor advance), `00` space, everything else = **tile number** in the BG tilemap (`ORA #$2000` then `STA $7E7000,x` at `$06:B9E6`). So glyph code == VRAM tile index; the font tiles are preloaded to VRAM, not in ROM verbatim (VRAM tiles not found raw in ROM; DMA'd from WRAM $7E8000 blocks at ~frame 1608-1633, probably decompressed).
- Text tilemap buffer: WRAM `$7E7140` (0x300 bytes, 32 cols x 12 rows), DMA'd to VRAM each update. Window frame tiles E0-E3/F1-F4 are drawn by `$06:B800..B874`.
- Text-dense region in bank 07: file 0x38E00-0x3C400 (script, ~14 KB; first message at 07:C00D = 0x3C00D), more text-like blocks near 07:D800-E200 and E000-FC00 (unverified). Messages are chained sequentially via `FD`/`FF`; pointer table/format not found yet (no 16-bit pointer table hits for C00D).
- Codes seen in stream: 0x21/0x22/0x2D (punctuation?), 0x60-0x7F and 0x80-0xD6 glyph tiles (kana + a few kanji, e.g. 0x8B 0x86). Glyph-to-char mapping (tbl) not built yet.

## Tools (tools/)
- `tools/lua/*.lua` (run with the skill's `emu.py --script`): `romreads` (ROM data reads), `dmalog` (DMA list), `dumpmem` (WRAM/VRAM/CGRAM at a frame), `wramwriters` (PC that writes a WRAM range), `vramwriters`, `textptr` (text stream pointer trace -> textptr.txt).
- `tools/dis65816.py ROM ADDR [count]` (copied from sibling repo): linear 65816 disassembler; REP/SEP tracked linearly, so treat output after data bytes as garbage.
- `tools/tilesheet.py` (copied): render raw 2bpp/4bpp tiles to PNG.
- Note: Mesen reports writes done by DMA with the PC of the instruction after `STA $420B`; $2118 writer PC `$00:8960` = DMA queue, not text code.

## Findings after recon (all used by build.py)
- Tables: tbl/jp.tbl from the VRAM font (BG3 chars at VRAM $C000; code == tile; ASCII 20-5F, hiragana 60-8D, katakana 90-BD, small kana C0-D7, kanji 08-1F). Controls FD nn (typing speed), F8 nn, F7 yes/no, FE newline, FF end.
- Dialogue: 137 messages at 0x38DF8-0x3C33E, 24-bit pointer tables 07:8BCA (115 slots incl. 8D1A), 07:8D4A (58). Loaders $06:B60E, $07:E3CF, $0B:CB32. Two engine copies read with DB=07: $06:B8D1 (field) and $07:E5C1 (shop window).
- Windows: records via pointer list 0B:D9FD (pos, width, height, ...). Window 0 = dialogue box. Line starts $06:BA4C; page-start cursor LDA #$018C at $06:B5FB/$06:B686/$07:E396; $07:E374 picks wide vs portrait window ($32 bit 4 or $33 >= 9 -> wide).
- Items: 16-bit tables 07:DE74 (65), 07:E17F (3), 07:E1B3 (9); text = dakuten row FE name row. Menus: 0B:DB71 (79), row byte then column byte per line.
- LZ (tools/lz.py, decompressor $00:F7B4): font block 14:8000 (file 0xA0000, 0x1000 bytes -> VRAM $C000); recompressor is byte-identical to the original.
- HUD strings (tilemap words) bank 06 around 0x304D8.

## Next (historical)
1. Build glyph table: dump VRAM font after the dialogue starts, match tile numbers to kana/kanji (render with tilesheet.py) -> `tbl/jp.tbl`.
2. Find where the font gets into VRAM (decompress routine; source via DMA from $7E8000, look for the WRAM writer/decompressor) and whether tile set is fixed or per-scene.
3. Find script structure: how `$1EA7` gets set (writers of $1EA7), message-ID/pointer tables, other text engines (menus, battle, stage titles, credits).
4. Plan English font: 8x8 tile per char is too wide-limited by tile index (<256); likely need 16-bit tile numbers or a larger font tile area, ROM expansion to 2 MiB.
