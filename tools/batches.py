"""Translation batches for parallel agents (dialogue).

    python -X utf8 tools/batches.py split          -> work/tl/bNN.tsv + work/tl/terms_bNN.txt (untranslated only)
    python -X utf8 tools/batches.py check bNN      -> validate work/tl/bNN.out.tsv; prints OK or errors
    python -X utf8 tools/batches.py merge bNN      -> check, then write EN into script/dialogue.json
Input TSV:  id<TAB>speaker<TAB>form<TAB>limit<TAB>jp   (jp line breaks shown as " / ")
Output TSV: id<TAB>en  (en keeps the control codes; {n} forced break, {p} new page; build auto-wraps at 28 cols)
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402

SCRIPT = ROOT / "script" / "dialogue.json"
TL = ROOT / "work" / "tl"
BATCH_SIZE = 46


def load():
    return json.loads(SCRIPT.read_text(encoding="utf-8"))


def batch_ids(entries):
    todo = [e for e in entries if not e["en"]]
    return {f"b{k // BATCH_SIZE:02d}": todo[k:k + BATCH_SIZE] for k in range(0, len(todo), BATCH_SIZE)}


def split():
    TL.mkdir(parents=True, exist_ok=True)
    terms = lint.glossary_terms()
    for name, rows in batch_ids(load()).items():
        lines = [f"{e['id']}\t?\tdlg\t28col/line, 4 lines/page, auto-wrap\t{e['jp'].replace('{n}', ' / ')}"
                 for e in rows]
        (TL / f"{name}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        jp_all = "".join(e["jp"] for e in rows)
        used = [f"{j}\t{en}" for j, en, _ in terms if j in jp_all]
        (TL / f"terms_{name}.txt").write_text("\n".join(used) + "\n", encoding="utf-8", newline="\n")
        print(f"{name}: {len(rows)} entries, {len(used)} terms")


def read_out(name):
    out = {}
    for n, line in enumerate((TL / f"{name}.out.tsv").read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise SystemExit(f"{name}.out.tsv line {n}: no tab")
        i, en = line.split("\t", 1)
        if i in out:
            raise SystemExit(f"{name}.out.tsv: duplicate id {i}")
        out[i] = en.strip()
    return out


def check(name):
    want = [l.split("\t")[0] for l in (TL / f"{name}.tsv").read_text(encoding="utf-8").splitlines() if l]
    out = read_out(name)
    entries = {e["id"]: e for e in load()}
    jp = {i: e["jp"] for i, e in entries.items()}
    errs = [f"missing id {i}" for i in want if i not in out] + [f"extra id {i}" for i in out if i not in want]
    terms = lint.glossary_terms()
    for i, en in out.items():
        if i in jp:
            errs += [f"{i}: {m}" for m in lint.check_dialogue(jp[i], en, terms, lint.wrap.box_of(entries[i]))]
    for m in errs:
        print(m)
    print("OK" if not errs else f"{len(errs)} errors")
    return not errs


def merge(name):
    if not check(name):
        raise SystemExit("merge refused")
    out = read_out(name)
    entries = load()
    for e in entries:
        if e["id"] in out:
            e["en"], e["status"] = out[e["id"]], "tl"
    SCRIPT.write_text(json.dumps(entries, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print(f"merged {len(out)} entries")


if __name__ == "__main__":
    cmd = sys.argv[1]
    {"split": lambda: split(), "check": lambda: sys.exit(0 if check(sys.argv[2]) else 1),
     "merge": lambda: merge(sys.argv[2])}[cmd]()
