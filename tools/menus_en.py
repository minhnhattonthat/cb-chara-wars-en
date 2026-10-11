"""English for the bank 0B menu/system strings (script/menus.json `en`). Re-run after editing: writes the JSON.

    python -X utf8 tools/menus_en.py
Rules: keep {y:}; every non-empty line starts with {x:}; JP dakuten rows become empty lines so rows stay put.
Widths: stay within the JP line's columns where a window edge is close (shop name windows: 8 columns from x=02).
"""
import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "script" / "menus.json"
HENCH = "{x:05}#1  #2  #3       #1  #2  #3"  # 子分1-3 slot labels, 4-column cells (see notes)

EN = {
    "M000": "{y:10}{x:0C}1 PLAYER{n}{n}{x:0C}2 PLAYERS{n}{n}{n}{x:08}© DYNAMIC   1992{n}{n}{x:08}© ALMANIC   1992{n}{n}{x:08}© BANPRESTO 1992{end}",
    "M004": "{y:15}{x:05}Buy{n}{n}{x:05}Talk{n}{n}{x:05}Leave{end}",
    "M005": "{y:15}{x:14}Buy{n}{n}{x:14}Talk{n}{n}{x:14}Leave{end}",
    "M006": "{y:0F}" + HENCH + "{end}",
    "M007": "{y:02}{x:02}Cafe{end}",
    "M008": "{y:02}{x:02}Diner{end}",
    "M009": "{y:01}{n}{x:02}Gadgets{end}",
    "M010": "{y:02}{x:02}Clothes{end}",
    "M011": "{y:01}{n}{x:02}Burgers{end}",
    "M012": "{y:01}{n}{x:02}Sweets{end}",
    "M013": "{y:02}{x:02}Bistro{end}",
    "M014": "{y:01}{n}{x:02}Sports{end}",
    "M015": "{y:02}{x:02}Henchmen{n}{n}{x:02}Weapons{n}{n}{x:02}Items{n}{n}{x:02}Status{n}{n}{x:02}EXIT{end}",
    "M016": "{y:01}{n}{x:02}Status{end}",
    "M017": "{y:07}{x:04}LIFE  {icon0D}{icon0E}{icon0F}{n}{n}{n}{x:04}Punch.....{n}{n}{x:04}Kick......{n}{n}{x:04}Defense...{n}{n}{x:04}Henchmen{end}",
    "M018": "{y:02}{x:02}Henchmen{end}",
    "M019": "{y:03}{n}{x:04}Decoy{n}{n}{x:04}Gofer{n}{n}{x:04}Work{n}{n}{x:04}Move{n}{n}{x:04}EXIT{end}",
    "M020": "{y:01}{n}{x:02}Decoy{n}{n}{x:04}Who?{end}",
    "M021": "{y:12}{x:04}EXIT{end}",
    "M022": "{y:01}{n}{x:02}Gofer{n}{n}{x:04}Who?{end}",
    "M023": "{y:01}{n}{x:02}Work{n}{n}{x:04}Who?{end}",
    "M024": "{y:01}{n}{x:02}Move{n}{n}{x:04}Who?{end}",
    "M025": "{y:02}{x:02}Buy what?{end}",
    "M026": "{y:07}{n}{x:04}Attack items{n}{n}{x:04}Defense items{n}{n}{x:04}HP items{n}{n}{x:04}Other{n}{n}{x:04}EXIT{end}",
    "M027": "{y:01}{n}{x:02}Weapons{end}",
    "M028": "{y:0F}{x:04}EXIT{end}",
    "M029": "{y:02}{x:02}Items{end}",
    "M030": "{y:19}{x:04}EXIT{end}",
    "M031": "{y:04}{n}{x:05}Do what?{n}{n}{x:06}Use{n}{n}{x:06}Give{n}{n}{x:06}EXIT{end}",
    "M032": "{y:0E}{n}{x:05}Do what?{n}{n}{x:06}Use{n}{n}{x:06}Give{n}{n}{x:06}EXIT{end}",
    "M033": "{y:12}{n}{x:05}Nobody here!{end}",
    "M034": "{y:09}{n}{x:04}Nobody here!{end}",
    "M035": "{y:08}{x:04}You have nothing!{end}",
    "M036": "{y:0D}{x:04}You have nothing!{end}",
    "M037": "{y:06}{x:06}Their{n}{n}{x:06}inventory{n}{n}{x:06}is full.{end}",
    "M038": "{y:10}{x:06}Their{n}{n}{x:06}inventory{n}{n}{x:06}is full.{end}",
    "M039": "{y:06}{x:06}Nobody{n}{n}{x:06}to give{n}{n}{x:06}it to!{end}",
    "M040": "{y:10}{x:06}Nobody{n}{n}{x:06}to give{n}{n}{x:06}it to!{end}",
    "M041": "{y:04}{n}{x:05}To whom?{n}{n}{x:06}Me{n}{x:06}#1{n}{x:06}#2{n}{x:06}#3{n}{x:06}EXIT{end}",
    "M042": "{y:0E}{n}{x:05}To whom?{n}{n}{x:06}Me{n}{x:06}#1{n}{x:06}#2{n}{x:06}#3{n}{x:06}EXIT{end}",
    "M043": "{y:01}{n}{x:0C}Which one?{end}",
    "M044": "{y:14}{n}{x:03}Who buys?{n}{n}{x:05}#1......{n}{x:05}#2......{n}{x:05}#3......{end}",
    "M045": "{y:14}{n}{x:12}Who buys?{n}{n}{x:14}#1......{n}{x:14}#2......{n}{x:14}#3......{end}",
    "M046": "{y:17}{x:0B}None{end}",
    "M047": "{y:18}{x:0B}None{end}",
    "M048": "{y:19}{x:0B}None{end}",
    "M049": "{y:17}{x:1A}None{end}",
    "M050": "{y:18}{x:1A}None{end}",
    "M051": "{y:19}{x:1A}None{end}",
    "M052": "{y:05}{x:0D}No henchmen,{n}{x:0D}can't buy!{end}",
    "M053": "{y:05}{n}{x:0D}Not enough money!{end}",
    "M054": "{y:05}{n}{x:0D}Inventory full,{n}{n}{x:0D}can't buy it!{end}",
    "M055": "{y:05}{n}{x:0E}Thank you!!!{end}",
    "M056": "{y:05}{n}{x:0D}HP restored!{n}{n}{x:13}/  {icon0D}{icon0E}{icon0F}{end}",
    "M057": "{y:06}{x:0D}Ahh! Delicious!!{end}",
    "M058": "{y:04}{n}{x:0D}Lottery ice pop{n}{n}{x:0D}Winner! One more!{end}",
    "M059": "{y:0E}{x:05}LET'S TRY BONUS STAGE!!{end}",
    "M060": "{y:06}{x:05}Your{n}{x:05}items{n}{x:05}are{n}{x:05}full,{n}{x:05}gofers{n}{x:05}are{n}{x:05}no use!{n}{n}{n}{n}{n}{n}{x:04}    {end}",
    "M061": "{y:0B}{n}{x:07}Spin for a prize!{n}{n}{x:07}Press any button!!{end}",
    "M062": "{y:0E}{x:06}LET'S PLAY STAGE  !!{end}",
    "M063": "{y:0A}{x:0D}PAUSE{end}",
    "M064": "{y:04}{x:04}Can't{n}{x:04}give{n}{x:04}orders{n}{x:04}to{n}{x:04}henchmen{n}{x:04}here!!{end}",
    "M065": "{y:05}{n}{x:04}HP{n}{n}{x:04}restored!{end}",
    "M066": "{y:05}{n}{x:04}LIFE{n}{n}{x:04}went up!{end}",
    "M067": "{y:04}{n}{x:04}Defense{n}{n}{n}{n}{x:04}went up!{end}",
    "M068": "{y:04}{n}{x:04}Punch{n}{n}{n}{n}{x:04}went up!{end}",
    "M069": "{y:04}{n}{x:04}Kick{n}{n}{n}{n}{x:04}went up!{end}",
    "M070": "{y:08}{x:04}was used.{end}",
    "M071": "{y:04}{x:0A}Yes{n}{n}{x:0A}No{end}",
    "M072": "{y:02}{x:02}Smuggler{end}",
    "M073": "{y:06}{x:04}Henchman{n}{x:04}refused{n}{x:04}orders!!{end}",
    "M074": "{y:05}{x:04}Can't{n}{x:04}use{n}{x:04}that{n}{x:04}here!!{end}",
    "M075": "{y:07}{x:07}UP!!{end}",
}

entries = json.loads(P.read_text(encoding="utf-8"))
for e in entries:
    if e["id"] in EN:
        e["en"], e["status"] = EN[e["id"]], "tl"
P.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"set {len(EN)} menu strings")
