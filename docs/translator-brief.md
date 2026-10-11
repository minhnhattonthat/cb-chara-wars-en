# Translator brief - CB Chara Wars: Ushinawareta Gag (SNES, 1992)

You translate part of the Japanese script of CB Chara Wars into English for a fan patch. It is a comedy RPG/action
crossover of chibi Go Nagai characters; the heroes are Devilman and Mazinger Z, out to recover the stolen "Gaaag"
(the source of all laughter). Work only on the batch named in your dispatch. Do all translation yourself; do not
dispatch subagents. Do not edit anything except your own output file.

## Read first
1. `docs/style-reference.md` - voices, approved example pairs, layout rules. Match this voice.
2. `work/tl/terms_<batch>.txt` - binding glossary rows for this batch (full table in `glossary.md`).

## Input: `work/tl/<batch>.tsv`
`id<TAB>speaker<TAB>form<TAB>limit<TAB>Japanese`. ` / ` marks the original 20-column line breaks (`/  / ` = a blank
line, often padding to the next box page). Speaker is `?`: infer it from content (first person, sentence endings,
neighbours). Entries are in ROM order, which mostly follows the story world by world; use neighbours for context.

## Output: `work/tl/<batch>.out.tsv`, written with your file-write tool (not a shell heredoc)
`id<TAB>English`, every input id exactly once, same order. Plain ASCII except ♥ (allowed if the JP has it).
Straight quotes, `...` for ellipses. No tabs in the English, no Japanese, no `\uXXXX`, and none of `* $ % @ \`
(the font has no glyph for them).

Control codes (copy exactly, as in the JP):
- Start with the same leading `{fd:XX}` as the JP and end with `{end}`.
- `{fd:XX}` = typing speed; `{fd:09}` followed by one space = a dramatic pause. Keep pauses at the matching beat;
  you may drop a mid-line `{fd:}` if the sentence order changes, but only use values present in the JP.
- `{f8:XX}` and `{yesno}` (a yes/no prompt after a question) must appear exactly as often as in the JP, in the
  same place (normally right before `{end}`).
- Layout: write flowing English; the build word-wraps at 28 columns, 4 lines per page. `{p}` starts a new page,
  `{n}` forces a line break (rare). Do not insert ` / `.
- Preview a line: `python -X utf8 tools/wrap.py "<english>"` shows the pages.

## Validate
Run `python -X utf8 tools/batches.py check <batch>` from the repo root and fix every reported id until it prints OK.

## Style
- Faithful: keep the information and order of ideas; adapt idiom, not meaning. Don't add details the Japanese
  doesn't state; don't summarise or skip. Jokes, puns and gag phrases (ムチムチプリン etc.) must still land in
  English: adapt them, no translator notes.
- Names and terms exactly as in the glossary (Gaaag, World, Kikunosuke, Koji Kabuto ...). Never abbreviate.
  Honorifics dropped; Western name order. JP quote marks "..." around names/terms stay as "...".
- Punctuation: ・・・ -> ..., !! stays !!, ? stays ?. Stretched shouts (ギャーーーーッ!!) -> stretched English
  ("Gyaaaaaaah!!").
- Shopkeepers and system messages are short and plain. Villains can be hammy.

## Consistency
Never edit `glossary.md`. For a recurring name or term not in it, pick a form, use it consistently, and report it.

## Report (reply with only this)
Files written and entry count; then any lines: `NEW TERM: jp -> en`, `UNSURE: id - note`, `LONG: id - note`.
