# Style reference

Comedy crossover of Go Nagai characters (SD/chibi). Heroes: Devilman and Mazinger Z (the player, addressed as
"you"/"you guys"). Laughter has vanished from the world because the "Gaaag" was stolen; the heroes travel through
Worlds based on Go Nagai manga (Harenchi Gakuen, Mazinger, Dororon Enma-kun, Devilman, Cutie Honey ...).

## Voices
| Who | Voice |
|---|---|
| Kikunosuke's father (bald old man, ワシ) | blustery old-man exclamations: "Listen well!", "Give it your all!" |
| Kikunosuke (girl, uses オレ/〜ぜ) | tomboyish, casual: "Good luck!!", "stuff", "you guys" |
| Miki and friendly guides (〜わ/〜よ) | warm, chatty, a bit dramatic |
| Villains (Mecha Hige-Godzilla: おかま, あたち) | campy, flamboyant: "Oh ho ho ho!", "Impossible, darling!" |
| Shopkeepers | brisk service phrases: "Welcome!", "What'll it be?" |
| Dialect speakers (Jack's Shop, おいどん) | folksy rural English, keep it readable |
| System messages ({fd:01}) | plain narration: "Used the key." |

## Approved pairs (pilot, in-game checked)
- D130 JP: デビルマン!マジンガーZ! / よくきくのだ!{fd:09}　 / {fd:04}きょうは　おまえたちに / じゅうような　はなしがある!!
  EN: {fd:04}Devilman! Mazinger Z! Listen well!{fd:09} {fd:04}I have something very important to tell you today!!
- D130 JP: わらうことが　できなくなると / ひとびとのせいかつは / くらく{fd:09}　 / {fd:04}つらいひびがつづく
  EN: When people can't laugh anymore, their lives turn gloomy{fd:09} {fd:04}and every day is a struggle.
- D132 JP: このせかいを　すくえば / "ヒーロー"に　なれるのだからな! / がんばってくれよ!
  EN: Save this world, and you'll be "heroes"! Give it your all!
- D133 JP: さいしょのワールドに　ついたら{fd:09}　 / {fd:04}まず　"みき"をさがしな!!
  EN: {fd:04}Once you reach the first World,{fd:09} {fd:04}go find "Miki" first thing!!
- Corrected example: "the Gyaagu" -> "the "Gaaag"" (glossary name, keep the JP quote marks as "...").

## Layout
- Write each message as flowing English. The build wraps at 28 columns, 4 lines per box page.
- Use `{p}` where the JP clearly starts a new box (blank lines `/  / ` padding a page, a change of topic or
  speaker tone). Don't leave a single orphan line on a page if a `{p}` earlier reads naturally.
- `{fd:09}` + one space = dramatic pause: keep it at the same beat (usually after the first clause).
