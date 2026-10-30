#!/usr/bin/env python3
"""Wave 2 plan validator (W2-51, DEC-744). Run: python3 docs/plan/tools/validate_w2.py [--root <tree root>].

Reads only files inside the tree root: docs/plan/WAVE_2_WBS.md (§1 ticket table and its baseline paragraph),
.tickets/*.md (a Wave 2 ticket by wbs_id, or external-ref when it has none; DEC-730), docs/plan/WAVE_2_LIST.md,
docs/plan/WAVE_2_TRIAGE.md, docs/contract/contract.yaml, docs/changes/*-CIT-P.md and the files under tests/acceptance/.
Each check prints one line, `<PASS|FAIL|NOT RUN> <name> — <reason>`; an input it cannot read is a FAIL naming it.
It never reads ~/gov-os-workbench or docs/source/, by default or by any option: the checks that would need them print
NOT RUN (DEC-744 item 2). Exit 0 when no check fails, 1 otherwise. docs/plan/tools/validate_s1.py is Wave 1's record.
"""
import argparse
import functools
import os
import re
import sys
from pathlib import Path

import yaml

W2_ID = re.compile(r"W2-[0-9]{2}[a-z]?")
CAP = re.compile(r"(?<![A-Za-z0-9])CAP-\d+(?:\.[a-z]+)?(?![A-Za-z0-9])")
ROW = re.compile(r"^\| W2-[HMLI]\d+ \|")
SEVERITIES = ("high", "medium", "low", "info")
NOT_RUN = (  # Wave 1's validator checks whose inputs live outside the tree (validate_s1.py)
    ("scenario-ids-in-coverage-matrix", "gov-os-workbench (synthetic/COVERAGE_MATRIX.md)"),
    ("mr-rules-verbatim-in-architecture", "gov-os-workbench (input/GOV_OS_ARCHITECTURE_v0.3.md)"),
    ("register-prefix-v0.12", "gov-os-workbench (input/GOV_OS_DECISION_REGISTER_v0.12.md)"),
    ("s1a-round-1-fingerprints", "gov-os-workbench (s1a-round1.sha256)"),
    ("readiness-dimensions-vs-framework", "docs/source (the Framework's original, §37)"),
)


class Unreadable(Exception):
    pass


def one_line(e):
    return " ".join(str(e).split()) or type(e).__name__


def read(rel):
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise Unreadable(f"cannot read {rel}: {type(e).__name__}")


def section(text, start):
    """The lines of `text` from the heading line starting with `start` to the next heading of level 1 or 2."""
    lines, out = text.splitlines(), None
    for line in lines:
        if out is None:
            out = [] if line.startswith(start) else None
        elif re.match(r"#{1,2} ", line):
            break
        else:
            out.append(line)
    return out


def cells(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


@functools.lru_cache(None)
def contract():
    rel = "docs/contract/contract.yaml"
    try:
        doc = yaml.safe_load(read(rel))
        covers = {cv["id"]: cv.get("wave") for cap in doc["capabilities"] for cv in cap.get("covers") or []}
        ids = {cap["id"] for cap in doc["capabilities"]} | set(covers)
    except Unreadable:
        raise
    except Exception as e:
        raise Unreadable(f"cannot parse {rel}: {one_line(e)}")
    return ids, covers


@functools.lru_cache(None)
def tickets():
    """The Wave 2 tickets: a list of (W2 id, frontmatter, file text)."""
    if not (ROOT / ".tickets").is_dir():
        raise Unreadable("cannot read .tickets/: no such folder")
    found = []
    for name in sorted(os.listdir(ROOT / ".tickets")):
        if not name.endswith(".md"):
            continue
        rel = f".tickets/{name}"
        text = read(rel)
        m = re.match(r"---\n(.*?)\n---\s*(\n|$)", text, re.S)
        try:
            fm = yaml.safe_load(m.group(1)) if m else None
        except yaml.YAMLError as e:
            raise Unreadable(f"cannot parse {rel}: {one_line(e)}")
        if not isinstance(fm, dict):
            raise Unreadable(f"cannot parse {rel}: no frontmatter mapping")
        w2 = str(fm.get("wbs_id") or fm.get("external-ref") or "")
        if W2_ID.fullmatch(w2):
            found.append((w2, fm, text))
    return found


@functools.lru_cache(None)
def wbs():
    """(the W2 ids of §1's ticket table, the baseline Wave 2 item ids or None)."""
    rel = "docs/plan/WAVE_2_WBS.md"
    body = section(read(rel), "## 1.") or []
    ids = {m.group(1) for m in (re.match(r"^\|\s*(?:\*\*)?(W2-[0-9]{2}[a-z]?)(?:\*\*)?\s*\|", l) for l in body) if m}
    if not ids:
        raise Unreadable(f"cannot parse {rel}: no W2 rows in the §1 ticket table")
    baseline, inside = None, False
    for line in body:
        if re.match(r"^\*\*The Contract's \d+ Wave 2 items, by ticket\.\*\*", line):
            baseline, inside = set(), True
        elif inside and line.startswith("- "):
            baseline |= set(CAP.findall(line))
        else:
            inside = False
    return ids, baseline


@functools.lru_cache(None)
def cit_p_lines():
    """Every CIT-P line: (file, covers id, wave) for a `- id:` entry of a ```yaml block that carries `wave:`."""
    if not (ROOT / "docs/changes").is_dir():
        return []
    out = []
    for name in sorted(n for n in os.listdir(ROOT / "docs/changes") if n.endswith("-CIT-P.md")):
        in_yaml, cid = False, None
        for line in read(f"docs/changes/{name}").splitlines():
            if line.startswith("```"):
                in_yaml, cid = line.strip() == "```yaml", None
            elif in_yaml and (m := re.match(r"^\s*- id: (CAP-\d+\.[a-z]+)\b", line)):
                cid = m.group(1)
            elif in_yaml and cid and (m := re.match(r"^\s*wave: (W1|W2|W3|NONE)\s*$", line)):
                out.append((name, cid, m.group(1)))
                cid = None
    return out


@functools.lru_cache(None)
def acceptance_citations():
    found = set()
    for dirpath, _, files in os.walk(ROOT / "tests/acceptance"):
        for f in files:
            p = Path(dirpath) / f
            try:
                found |= set(CAP.findall(p.read_bytes().decode("utf-8", "replace")))
            except OSError as e:
                raise Unreadable(f"cannot read {p.relative_to(ROOT)}: {type(e).__name__}")
    return found


def wave2_items():
    return sorted(cid for cid, wave in contract()[1].items() if wave == "W2")


def result(bad, ok, what):
    return (False, f"{what}: {', '.join(bad)}") if bad else (True, ok)


def check_wave2_tickets():
    table, files = wbs()[0], {w2 for w2, _, _ in tickets()}
    bad = [f"{i} (WBS table only)" for i in sorted(table - files)]
    bad += [f"{i} (.tickets/ only)" for i in sorted(files - table)]
    return result(bad, f"{len(table)} W2 ids agree between the WBS §1 table and .tickets/", "ids on one side only")


def check_delivered():
    closed = {c for _, fm, _ in tickets() for entry in (fm.get("closes") or []) for c in CAP.findall(str(entry))}
    items = wave2_items()
    return result([i for i in items if i not in closed], f"{len(items)} Wave 2 items, each in a Wave 2 ticket's closes",
                  "no Wave 2 ticket delivers")


def check_cited():
    cited, items = acceptance_citations(), wave2_items()
    return result([i for i in items if i not in cited], f"{len(items)} Wave 2 items, each cited under tests/acceptance/",
                  "no acceptance test cites")


def check_ids_exist():
    ids = contract()[0]
    bad = sorted({f"{c} ({w2})" for w2, _, text in tickets() for c in CAP.findall(text) if c not in ids})
    return result(bad, f"every Contract id cited by {len(tickets())} Wave 2 tickets exists", "not in the Contract")


def check_cit_p_moved():
    baseline = wbs()[1]
    if baseline is None:
        raise Unreadable("cannot parse docs/plan/WAVE_2_WBS.md: no baseline line \"The Contract's N Wave 2 items\"")
    moved = [i for i in wave2_items() if i not in baseline]
    lined = {cid for _, cid, wave in cit_p_lines() if wave == "W2"}
    return result([i for i in moved if i not in lined], f"{len(moved)} items moved to Wave 2, each with a CIT-P line",
                  "moved to Wave 2 with no CIT-P line")


def check_cit_p_applied():
    covers, lines = contract()[1], cit_p_lines()
    bad = [f"{cid} ({name}, wave {wave})" for name, cid, wave in lines if covers.get(cid) != wave]
    return result(bad, f"{len(lines)} CIT-P lines, each applied in the Contract", "CIT-P line with no change")


def check_list_counts():
    rel, stated, rows, current = "docs/plan/WAVE_2_LIST.md", {}, {}, None
    for line in read(rel).splitlines():
        if m := re.match(r"^### 3\.\d+ (\S+) \((\d+)\)", line):
            current, stated[m.group(1)], rows[m.group(1)] = m.group(1), int(m.group(2)), 0
        elif line.startswith("#"):
            current = None
        elif current and ROW.match(line):
            rows[current] += 1
    if not stated:
        raise Unreadable(f"cannot parse {rel}: no '### 3.n <severity> (<count>)' heading")
    bad = [f"{s} states {n}, has {rows[s]} rows" for s, n in stated.items() if rows[s] != n]
    return result(bad, f"{len(stated)} severity counts agree with {sum(rows.values())} rows", "count disagrees")


def check_triage_counts():
    rel = "docs/plan/WAVE_2_TRIAGE.md"
    text = read(rel)
    table, open_rows = section(text, "## Counts"), section(text, "## Every open row")
    table = [cells(l) for l in table or [] if l.startswith("|") and not l.startswith("|---")]
    if not table or open_rows is None:
        raise Unreadable(f"cannot parse {rel}: no '## Counts' table or no '## Every open row' section")
    cols, counted = table[0][1:], {}
    for line in filter(ROW.match, open_rows):
        cs = cells(line)
        sev = next((c for c in cs[2:] if c in SEVERITIES), None)
        disp = cs[cs.index(sev) + 1] if sev else ""
        col = "Wave 2" if W2_ID.fullmatch(disp) else disp
        for key in ((sev, col), (sev, "Total"), ("all", col), ("all", "Total")):
            counted[key] = counted.get(key, 0) + 1
    stated = {r[0].strip("*"): r[1:] for r in table[1:]}
    bad = []
    for row in SEVERITIES + ("all",):
        try:
            got = [int(c.strip("*")) for c in stated[row]]
        except (KeyError, ValueError):
            bad.append(f"{row} (row missing or not a number)")
            continue
        bad += [f"{row} {c} states {n}, rows give {counted.get((row, c), 0)}"
                for c, n in zip(cols, got) if n != counted.get((row, c), 0)]
    return result(bad, f"every Counts cell agrees with {counted.get(('all', 'Total'), 0)} open rows", "count disagrees")


CHECKS = (("wave2-tickets", check_wave2_tickets), ("contract-items-delivered", check_delivered),
          ("contract-items-cited-by-tests", check_cited), ("ticket-contract-ids-exist", check_ids_exist),
          ("cit-p-moved-items", check_cit_p_moved), ("cit-p-lines-applied", check_cit_p_applied),
          ("list-counts", check_list_counts), ("triage-counts", check_triage_counts))


def main():
    global ROOT
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[3]), help="the plan tree's root")
    ROOT = Path(ap.parse_args().root)
    if not ROOT.is_dir():
        print(f"FAIL root — the tree root does not exist or is not a folder: {ROOT}")
        return 1
    fails = 0
    for name, fn in CHECKS:
        try:
            ok, reason = fn()
        except Unreadable as e:
            ok, reason = False, str(e)
        fails += not ok
        print(f"{'PASS' if ok else 'FAIL'} {name} — {reason}")
    for name, need in NOT_RUN:
        print(f"NOT RUN {name} — would need {need}; never read by this validator (DEC-744)")
    print(f"\nRESULT: {f'{fails} FAIL' if fails else 'no FAIL'}, {len(NOT_RUN)} NOT RUN")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
