#!/usr/bin/env python3
"""Apply audit 8's classes to the register (G4, DEC-1214): one group per run.

    python3 docs/emergency-2/audits/08-apply.py --list            # the groups and their counts
    python3 docs/emergency-2/audits/08-apply.py --group G05       # put the class on each entry of one group
    python3 docs/emergency-2/audits/08-apply.py --header          # the register's one-paragraph note on the class field
    python3 docs/emergency-2/audits/08-apply.py --check           # every entry carries its class once

An entry's class is written at the end of its status line (its last physical line, when the line wraps) as
``· **Class:** kept`` (kept, with its changed items), ``superseded by <EMERGENCY-2 section or DEC>``, ``retired`` or
``history``. The class is the CSV's (`08-register.csv`), except for the rows `08-doubtful-settled.md` marks changed.
The register's parsers read only the status word and the named fields, so the new field changes no meaning; the
entry's own ACCEPTED/DONE word is untouched.
"""
import argparse, collections, csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REG = ROOT / "docs/DECISION_REGISTER.md"
CSV = ROOT / "docs/emergency-2/audits/08-register.csv"
SETTLED = ROOT / "docs/emergency-2/audits/08-doubtful-settled.md"
CLASSES = ("kept", "superseded", "retired", "history")
THEMES = ("guard", "memory", "landing", "tickets", "runtime", "releases", "examin", "records", "other")
HEAD = re.compile(r"### (DEC-\d+)")


def rows():
    out = {r["id"]: r for r in csv.DictReader(open(CSV, encoding="utf-8"))}
    for line in SETTLED.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 7 and cells[0].startswith("DEC-") and cells[5] == "yes":
            r = out[cells[0]]
            r["class"] = cells[3].strip("*")
            r["by"], r["items"] = ("", "")
            if r["class"] == "kept":
                r["items"] = re.sub(r"^items:\s*", "", cells[4])
            elif r["class"] == "superseded":
                r["by"] = cells[4]
    return out


def groups(original=None):
    """G01.. in the audit's order: themes in order, classes in order, a combination with no rows skipped."""
    base = list(csv.DictReader(open(CSV, encoding="utf-8")))
    names, n = {}, 0
    for theme in THEMES:
        for cls in CLASSES:
            if any(r["theme"] == theme and r["class"] == cls for r in base):
                n += 1
                names[(theme, cls)] = f"G{n:02d}"
    return names


def text(r):
    cls = r["class"]
    if cls == "kept":
        return "kept" + (f" (items changed: {r['items']})" if r["items"] else "")
    if cls == "superseded":
        by = r["by"]
        by = f"EMERGENCY-2 {by} (DEC-1211)" if by.startswith("§") else by
        return f"superseded by {by}"
    if cls == "retired":
        return "retired"
    by = r["by"]
    return "history" + (" (one-off, done)" if by == "DONE" else f" (settled by {by})" if by else "")


def split(lines):
    heads = [i for i, l in enumerate(lines) if HEAD.match(l)]
    return {HEAD.match(lines[i]).group(1): i for i in heads}, heads


def status_end(lines, i):
    """Index of the last physical line of the entry's status line (wrapped continuation lines are indented)."""
    j = i + 1
    while not lines[j].startswith("- **Status:**"):
        j += 1
    k = j
    while k + 1 < len(lines) and re.match(r"  +\S", lines[k + 1]) and not re.match(r"\s*[-*+]\s", lines[k + 1]):
        k += 1
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--group")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--header", action="store_true")
    a = ap.parse_args()
    R, G = rows(), groups()
    lines = REG.read_text(encoding="utf-8").split("\n")
    pos, heads = split(lines)
    gid = {id: G[(r["theme"], r["class"])] if (r["theme"], r["class"]) in G else None for id, r in R.items()}
    for id, r in R.items():  # a row moved to a new theme x class takes that group's number
        if gid[id] is None:
            sys.exit(f"{id}: no group for {r['theme']} x {r['class']}")
    if a.list:
        c = collections.Counter(gid.values())
        for (theme, cls), g in sorted(G.items(), key=lambda kv: kv[1]):
            print(g, theme, cls, c[g])
        print("total", sum(c.values()))
        return
    if a.header:
        note = ("**The class field (audit 8, DEC-1214 G4).** Each entry DEC-001 to DEC-1210 carries `**Class:**` at the end "
                "of its status line, put there by `docs/emergency-2/audits/08-apply.py` from audit 8 "
                "(`docs/emergency-2/audits/08-register.md`), with the 48 doubtful rows settled in "
                "`08-doubtful-settled.md`: *kept* (in force, with the items that changed), *superseded by* "
                "(EMERGENCY-2 section or decision), *retired* (its subject is gone) or *history* (a one-off, done or "
                "settled). The status word itself (ACCEPTED, DONE ...) is untouched. This register is read-only history "
                "once EMERGENCY-2 §11.3 is carried out.")
        s = "\n".join(lines)
        if "**The class field (audit 8" in s:
            return
        marker = "Evidence was gathered on 2026-09-28"
        assert marker in s
        s = s.replace(marker, note + "\n\n" + marker, 1)
        REG.write_text(s, encoding="utf-8")
        print("header written")
        return
    if a.check:
        bad = 0
        for id, r in R.items():
            e = status_end(lines, pos[id])
            n = sum(1 for l in lines[pos[id]:heads[heads.index(pos[id]) + 1] if pos[id] != heads[-1] else len(lines)] if "**Class:**" in l)
            if n != 1 or f"**Class:** {text(r)}" not in lines[e]:
                bad += 1
                print("BAD", id, n)
        print("entries", len(R), "bad", bad)
        sys.exit(1 if bad else 0)
    n = 0
    for id, r in R.items():
        if gid[id] != a.group:
            continue
        e = status_end(lines, pos[id])
        if "**Class:**" in lines[e]:
            continue
        lines[e] = lines[e].rstrip() + f" · **Class:** {text(r)}"
        n += 1
    REG.write_text("\n".join(lines), encoding="utf-8")
    print(a.group, "entries changed", n)


main()
