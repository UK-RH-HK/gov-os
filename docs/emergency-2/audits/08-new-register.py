#!/usr/bin/env python3
"""Build the proposed new register from the classed old one (EMERGENCY-2 §11.3; audit 8 "Archiving ..."; G4, DEC-1214).

    python3 docs/emergency-2/audits/08-new-register.py --out /tmp/NEW_DECISION_REGISTER.md [--check]

It writes nothing into the tree unless told to: the new register holds, verbatim and in the old order, every entry whose
`**Class:**` is `kept` (each already carries its changed-items note) and every entry of DEC-1211 and later (the
decisions made since audit 8), under a new header. `--check` parses the result with the store's own loader and reports
the entries it reads, the ids a kept entry cites that the new register does not hold (they are in the archive), and
whether `gov close`'s `accepted_reds` ids resolve. The CTO moves the old file and puts the new one in its place (audit
8's steps 1 to 7); this script is step 2.
"""
import argparse, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "docs/DECISION_REGISTER.md"
HEAD = re.compile(r"### (DEC-\d+)")
HEADER = """# Governance OS — Decision Register (in force)

**Register ID:** GOV-DR · **Built from:** the old register `docs/archive/DECISION_REGISTER-2026-11-17.md` (archived read-only,
EMERGENCY-2 §11.3), by `docs/emergency-2/audits/08-new-register.py`.

Each entry below is copied verbatim from the old register. The entries are the decisions audit 8 classed **kept** (the
owner approved the classes by group, DEC-1214 G4) and every decision since (DEC-1211 and later). The `**Class:**` field at
the end of an entry's status line says which items of a kept entry no longer hold. A decision that is not here is in the
archive; the archive is not in memory's index.

---

## Decisions

"""


def entries(text):
    lines = text.split("\n")
    heads = [i for i, l in enumerate(lines) if HEAD.match(l)]
    out = []
    for k, i in enumerate(heads):
        end = heads[k + 1] if k + 1 < len(heads) else len(lines)
        j = i + 1
        while j < end and not lines[j].startswith("## ") and lines[j] != "---":
            j += 1
        body = "\n".join(lines[i:j]).rstrip("\n")
        out.append((HEAD.match(lines[i]).group(1), body))
    return out


def keep(id, body):
    n = int(id[4:])
    if n >= 1211:
        return True
    m = re.search(r"\*\*Class:\*\* (\w+)", body)
    return bool(m) and m.group(1) == "kept"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    ents = entries(REG.read_text(encoding="utf-8"))
    kept = [(i, b) for i, b in ents if keep(i, b)]
    text = HEADER + "\n\n".join(b for _, b in kept) + "\n"
    Path(a.out).write_text(text, encoding="utf-8")
    print(f"old register {len(ents)} entries; new register {len(kept)} entries -> {a.out}")
    if a.check:
        sys.path.insert(0, str(ROOT / "src"))
        from gov.store.loader import register_entries
        live, refused = register_entries(text)[:2]
        ids = {e["id"] for e in live}
        print(f"the store's loader reads {len(live)} entries; refused: {refused if refused else 'none'}")
        cited = {}
        for i, b in kept:
            for c in set(re.findall(r"(?<![A-Za-z0-9_])DEC-\d+(?![A-Za-z0-9_])", b)):
                if c not in ids and c != i:
                    cited.setdefault(c, set()).add(i)
        print(f"ids cited by a kept entry that are in the archive only: {len(cited)} (by {len({x for s in cited.values() for x in s})} entries)")
        print("DEC-1134 (accepted_reds) kept:", "DEC-1134" in ids)


main()
