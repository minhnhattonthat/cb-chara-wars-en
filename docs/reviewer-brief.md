# Translation reviewer brief - CB Chara Wars: Ushinawareta Gag (SNES, 1992)

You review one batch of a JP->EN fan translation. Read-only: no edits, no git, no subagents. Mechanical validity
(ids, control codes, ASCII, width) is already enforced by the check tool - judge translation quality.

## Inputs (paths in your dispatch)
- Pairs file: every translated entry as `>> id [box] | JP` then the EN line, in ROM (mostly story) order. Read ALL of it. JP ` / ` are original line breaks; EN `{p}` = new page, `{fd:XX}` typing speed (09 = pause). Speakers are not marked; infer from content.
- `glossary.md` (rulings at the top), `docs/style-reference.md`, the translator's report (unverified claims).

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip like "Bran" for "Plan" is what players notice); honorific relationships stable
  within a scene; voice matches the style reference.
- Things players and users caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a
  variable ("1th"); abbreviated names or terms (unless the glossary rulings allow them); stock phrases that read awkwardly in English ("... GET!").
- Naturalness: would a fan-translation reader stumble?

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
