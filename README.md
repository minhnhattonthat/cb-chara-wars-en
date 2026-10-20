# CB Chara Wars: Ushinawareta Gag English translation

Unofficial English fan translation of **CB Chara Wars: Ushinawareta Gag** (Super Famicom, Banpresto, 1992): the source
text and tools that build the patch.

**No game data is included.** Download the BPS patch from the [latest release](../../releases/latest) and apply it to
your own dump, `CB Chara Wars - Ushinawareta Gag (Japan).sfc` (1 MiB, CRC32 85AC87D5). The release README lists the
hashes, patching steps and known issues.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## What is translated
All dialogue, menus and items, the title logo and subtitle, and the signs, speech balloons, sound effects and other
in-game graphics labels. Names use the official or OVA spellings where they exist, in Western order, without
honorifics; the credits are in English.

## Building from source
You need your own ROM under `rom/` (gitignored) and asar. See `CLAUDE.md` for the commands (`python -X utf8 build.py`,
`tools/check.py`, `tools/release.py`) and `docs/re/` for the engine research.

- `script/`: dialogue, items and menus (Japanese + English)
- `data/`, `font/`: title maps and the lowercase font
- `tools/`: text, wrap, graphics, batch and release tools
- `tbl/`: text tables
- `glossary.md`: naming rulings

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

Translation, tools and patch were produced with AI assistance (Claude, Anthropic) under the direction of the project
owner. The game is (c) Banpresto; the characters belong to their respective owners. This project is not affiliated
with them. Do not share patched ROMs.
