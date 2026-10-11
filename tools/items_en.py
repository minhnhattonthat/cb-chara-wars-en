"""English for the bank 07 item/status names (script/items.json `en`). Re-run after editing: writes the JSON.

    python -X utf8 tools/items_en.py
Each item is two rows: the JP dakuten row, then the name row (dot leaders + price follow it in shop lists).
English: one name row of <= 10 characters; longer names use the top row too ("Cheese" / "burger").
Henchman statuses (I071-I075) are 3 rows of 5 columns.
"""
import json
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "script" / "items.json"
MAX = 10

NAMES = {  # id: name, or (top row, name row)
    "I000": "Coffee", "I001": "Tea", "I002": "Cocoa", "I003": "Water", "I004": "Cake",
    "I005": "Sandwich", "I006": "Hamburger", "I007": ("Cheese", "burger"), "I008": ("Fish", "burger"),
    "I009": "Big Burger", "I010": "Fries", "I011": ("Fried", "Chicken"), "I012": "Shake",
    "I013": ("Hamburg", "Set Meal"), "I014": ("Shrimp Fry", "Set Meal"), "I015": "Steak",
    "I016": ("Ghost", "Hamburg"), "I017": ("2.5 Kilo", "Steak"), "I018": "Takoyaki", "I019": "Yakisoba",
    "I020": "Croquette", "I021": "Oyster Fry", "I022": "Shrimp Fry", "I023": "Rice", "I024": "Tempura",
    "I025": "Teriyaki", "I026": "Ramen", "I027": "Oyakodon", "I028": "Katsudon", "I029": "Tendon",
    "I030": ("Oyster Fry", "Set Meal"), "I031": "Unadon", "I032": ("Jack's", "Belly Wrap"),
    "I033": ("School", "Uniform"), "I034": ("Kekko's", "Panties"), "I035": ("Honey's", "Scarf"),
    "I036": ("Jubei's", "Bra"), "I037": "Parka", "I038": ("Koji's", "Battlesuit"), "I039": "Ice Cream",
    "I040": ("Lottery", "Ice Pop"), "I041": ("Sports", "Drink"), "I042": ("Spike", "Juice"),
    "I043": ("Ballerina", "Juice"), "I044": ("Hiking", "Boots"), "I045": "Cooler",
    "I046": ("Washing", "Machine"), "I047": "Videotape", "I048": "Jackknife", "I049": "Oni Horn",
    "I050": "Chiko Nut", "I051": ("Susanoo's", "Hair"), "I052": "Safe", "I053": "Spacesuit",
    "I054": "Nikomago", "I055": ("Nanako's", "Egg"), "I056": ("Yonegon's", "Horn"), "I057": "Sunprint",
    "I058": "Photo", "I059": ("Wobbly", "Drink"), "I060": ("Kumiko's", "Eyes"), "I061": ("Fire-", "crackers"),
    "I062": ("Powdered", "Juice"), "I063": "Knee Pad", "I064": "Drum", "I065": ("Black", "Tracksuit"),
    "I066": ("Red", "Tracksuit"), "I067": ("Blue", "Tracksuit"), "I068": "Next Page", "I069": "First Page",
    "I070": "EXIT",
}
STATUS = {"I071": "Idle", "I072": "Decoy", "I073": "Gofer", "I074": "Work", "I075": "Move"}  # 5 columns


def en_for(i):
    if i in STATUS:
        return "{n}" + STATUS[i].ljust(5) + "{n}     {end}"
    v = NAMES[i]
    top, name = v if isinstance(v, tuple) else ("", v)
    assert len(top) <= MAX and len(name) <= MAX, i
    return f"{top}{{n}}{name}{{end}}"


entries = json.loads(P.read_text(encoding="utf-8"))
for e in entries:
    if e["id"] in NAMES or e["id"] in STATUS:
        e["en"], e["status"] = en_for(e["id"]), "tl"
P.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print(f"set {sum(1 for e in entries if e['en'])} item strings")
