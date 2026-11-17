#!/usr/bin/env python3
"""Audit 8 (EMERGENCY-2 §9 row 8), step 1: parse docs/DECISION_REGISTER.md by code, read-only.

Per decision: id, first line, date, title, status word, the change marks in both directions, and whether the marks
already settle it (fully superseded, withdrawn, rejected, or a DONE one-off). Writes a CSV to stdout (or --out).

Rules for "settled by its marks" (class history), conservative: a mark that names items, parts, points, a clause or
a scope ("for", "only", "(2)", "item 3", "Q5", "§", "its last point" ...) is partial and settles nothing.
  S1  the status word is SUPERSEDED, WITHDRAWN or REJECTED;
  S2  the status word is DONE (a one-off carried out and recorded);
  S3  the entry's own `Superseded by:` / `Changed by:` / status text says superseded, withdrawn, replaced, reversed
      or spent with no partial qualifier;
  S4  another entry's `Supersedes:` / `Replaces:` / `Withdraws:` / `Changes:` names this id with no partial
      qualifier and says superseded/replaced/withdrawn (for Supersedes/Replaces/Withdraws the verb is implied);
  S5  the title says "(superseded ...)", "(withdrawn ...)", "(spent ...)" or "(replaced ...)" without "part".
Usage: python3 08-parse.py [--register PATH] [--out PATH]
"""
import argparse
import csv
import re
import sys
from collections import defaultdict

HEAD = re.compile(r"^### (DEC-\d+)(?: \([^)]*\))? — (.*)$")
DATE = re.compile(r"20\d\d-\d\d-\d\d")
DEC = re.compile(r"DEC-\d+")
FIELD = re.compile(r"\*\*([A-Z][A-Za-z ]{1,30}):\*\*\s*(.*?)(?=\s·\s\*\*[A-Z][A-Za-z ]{1,30}:\*\*|$)")
OUT_FIELDS = ("Changes", "Supersedes", "Replaces", "Amends", "Refines", "Corrects", "Extends", "Ratifies",
              "Withdraws", "Lifts", "Settles", "Confirms", "Amended", "Changed")
IN_FIELDS = ("Changed by", "Superseded by", "Lifted by")
ENDING = re.compile(r"\b(superseded|withdrawn|replaced|reversed|spent|void|overturned|retired)\b", re.I)
PARTIAL = re.compile(
    r"\bitems?\b|\bparts?\b|\bpoints?\b|\(\s*\d|\(\s*[a-z]{1,2}\s*\)|\(\s*[ivx]+\s*\)|\bfor (the|one|its|a|wave|"
    r"this|that|research|w\d)|\bonly\b|\bresidual\b|\blimit\b|§|\bQ\d|\bclause\b|\bsteps?\b|\bfirst\b|\blast\b|"
    r"\bsecond\b|\bthird\b|\bexcept\b|\bsentence\b|\bline\b|\brule\b|\bpartly\b|\bpartially\b|\bin part\b|"
    r"\bits\b|\bthe\b|\bS\d|\bDP-\d|\bgap\b|\bexception\b|\bas a gate\b|\bstays in force\b|\bstands\b|\bkept\b|\bstanding\b",
    re.I)


def entries(path):
    text = open(path, encoding="utf-8").read().split("\n")
    cur = None
    for n, line in enumerate(text, 1):
        m = HEAD.match(line)
        if m:
            if cur:
                yield cur
            cur = {"id": m.group(1), "line": n, "title": m.group(2).strip(), "body": []}
        elif cur is not None:
            if line.startswith("## ") and not line.startswith("### "):
                yield cur
                cur = None
            else:
                cur["body"].append(line)
    if cur:
        yield cur


def status_line(body):
    for line in body:
        if line.startswith("- **Status:**"):
            return line
    return ""


def fields(line):
    out = defaultdict(list)
    for name, value in FIELD.findall(line):
        out[name.strip()].append(value.strip())
    return out


def segments(value):
    """Split a mark's value into (DEC id, the text that qualifies it) pairs."""
    ids = list(DEC.finditer(value))
    out = []
    for i, m in enumerate(ids):
        end = ids[i + 1].start() if i + 1 < len(ids) else len(value)
        start = ids[i - 1].end() if i else 0
        before = value[start:m.start()]
        after = value[m.end():end]
        out.append((m.group(0), before, after))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--register", default="docs/DECISION_REGISTER.md")
    ap.add_argument("--out", default="-")
    args = ap.parse_args()

    rows = list(entries(args.register))
    incoming = defaultdict(list)  # id -> [(from id, field, qualifier text, full?)]
    for e in rows:
        st = status_line(e["body"])
        e["status"] = st
        e["fields"] = fields(st)
        for name in OUT_FIELDS:
            for value in e["fields"].get(name, []):
                for target, before, after in segments(value):
                    qual = (before + " " + after).strip()
                    implied = name in ("Supersedes", "Replaces", "Withdraws")
                    ends = implied or bool(ENDING.search(qual))
                    bare = not re.search(r"[A-Za-z0-9]", re.sub(r"\band\b|\bby\b", "", before + after))
                    full = (bare if implied else ends and not PARTIAL.search(qual))
                    incoming[target].append((e["id"], name, qual[:120], full))

    w = csv.writer(sys.stdout if args.out == "-" else open(args.out, "w", newline="", encoding="utf-8"))
    w.writerow(["id", "line", "date", "title", "status_word", "out_marks", "in_marks_own", "in_marks_from_others",
                "settled", "settled_rule", "partly_changed"])
    for e in rows:
        st = e["status"]
        sw = re.sub(r"- \*\*Status:\*\*\s*", "", st)
        word = (re.match(r"[A-Z]+", sw) or [""])[0]
        dm = DATE.search(st) or DATE.search(" ".join(e["body"][:6])) or DATE.search(" ".join(e["body"]))
        date = dm.group(0) if dm else ""
        f = e["fields"]
        out_marks = "; ".join(f"{k}: {DEC.findall(v) and ', '.join(dict.fromkeys(DEC.findall(v)))}"
                              for k in OUT_FIELDS for v in f.get(k, []) if DEC.findall(v))
        own = "; ".join(f"{k}: {v[:160]}" for k in IN_FIELDS for v in f.get(k, []))
        inc = incoming.get(e["id"], [])
        inc_txt = "; ".join(f"{src} {name}{' (full)' if full else ''}" for src, name, _, full in inc)
        rule = ""
        if word in ("SUPERSEDED", "WITHDRAWN", "REJECTED"):
            rule = f"S1 status {word}"
        elif word == "DONE":
            rule = "S2 status DONE (one-off carried out)"
        else:
            for k in ("Superseded by", "Changed by"):
                for v in f.get(k, []):
                    if ENDING.search(v) and not PARTIAL.search(v) and DEC.search(v):
                        rule = f"S3 own {k}: {v[:80]}"
                    elif k == "Superseded by" and not PARTIAL.search(v) and DEC.search(v):
                        rule = f"S3 own Superseded by: {v[:80]}"
            if not rule:
                full = [src for src, _, _, ok in inc if ok]
                if full:
                    rule = "S4 superseded in full by " + ", ".join(dict.fromkeys(full))
            if not rule:
                t = re.search(r"\((superseded|withdrawn|spent|replaced)[^)]*\)", e["title"], re.I)
                if t and not re.search(r"part|item|standing", t.group(0), re.I):
                    rule = "S5 title: " + t.group(0)[:80]
        partly = bool(own) or any(not ok for _, _, _, ok in inc)
        w.writerow([e["id"], e["line"], date, e["title"][:200], word, out_marks, own, inc_txt,
                    "yes" if rule else "no", rule, "yes" if (partly and not rule) else "no"])


if __name__ == "__main__":
    main()
