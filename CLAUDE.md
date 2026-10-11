# CB Chara Wars: Ushinawareta Gag (SNES, Banpresto 1992) English translation

Skill: translate-retro-game (H:/translation/cb-chara-wars/.claude/skills/translate-retro-game/SKILL.md). Read it before ROM, text or QA work.

## Commands (run from repo root)
- Build:    not yet written (phase 2: identity build) -> build/cbcw_en.sfc
- Check:    `python -X utf8 tools/check.py` (pytest; the pre-commit hook runs this)
- Smoke:    `python -X utf8 .claude/skills/translate-retro-game/scripts/emu.py build/cbcw_en.sfc --out work/qa/smoke --route tools/routes/boot.txt --smoke`
- Release:  not yet written (BPS via skill's bps.py; never publish without the user)

## Paths
- Original ROM: `rom/CB Chara Wars - Ushinawareta Gag (Japan).sfc` (gitignored). 1 MiB LoROM, CRC32 85ac87d5, SHA-1 d25e9d47fc1e7e8e3471b594be4df26dda6cc52e, MD5 7c8bc64800fec80dc54375bab4cfb9af.
- Emulator: Mesen2 found by emu.py in sibling repo `../little-master/tools/mesen2/`. Assembler: asar in `../little-master/tools/asar/`.
- Text: `script/` (TBD). Tables: `tbl/`. Glossary + rulings: `glossary.md`. RE notes: `docs/re/`. Savestates: `work/states/`.

## Rulings (2026-10-11, details in glossary.md)
- Drop honorifics, Western name order. English credits. Official/OVA names first, else Hepburn. No abbreviations (prefer engine work). Specs pre-approved.
- Prior patch: none found (web search 2026-10-11).

## Gotchas
- Edit source with Edit/Write only; guard hook blocks sed -i / heredoc edits.
- Dialogue text = 1 byte per glyph, code == VRAM tile number; `FE` newline, `FD` page, `FF` end, `8E/8F` dakuten marks. Details: `docs/re/README.md` (index of RE notes; Lua probes in `tools/lua/`).

## Status
- Done: Step 0 setup (hooks, gitignore, check, smoke boots original). Phase 1 recon partial: dialogue engine and stream format found (bank 07, file 0x38E00-0x3C400+).
- Next: glyph table (tbl/jp.tbl), font origin in VRAM, script/pointer structure, other text engines, then phase 2 identity build.
