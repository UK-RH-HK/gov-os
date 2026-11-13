"""W2-173 acceptance tests' support: the planted forms and the argv recorder, on W2-149's planted world.

Nothing here imports the script under test: it runs as a program from W2-149's planted repository, with W2-149's
planted HOME, sets root and stub ``claude`` (imported from ``tests/acceptance/W2-149``, never copied). This module adds
only what W2-173's KPI lines need: briefs that name ``effort``, a recorder in front of W2-149's stub that keeps every
call's raw argv (``--effort`` included) and hands the stub the rest, a planted question set whose files' names are their
ids, the checker's notes and the auditor's classes in the audit briefs' fixed forms, and folder snapshots.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
W2_149 = HERE.parent / "W2-149"
if str(W2_149) not in sys.path:
    sys.path.insert(0, str(W2_149))

import w2_149_support as support  # noqa: E402
import w2_149_setup_a as sa  # noqa: E402,F401  (re-exported for the cases)

TICKET_ID = "DAEO-qz4p"
W2 = "W2-173"
BASE_FALLBACK = "dac438772"           # the ticket's claim commit, when no merge-base with w2/integrate is found
EFFORTS = ("low", "medium", "high", "xhigh", "max")
STOPPED = ("none", "input-missing", "input-malformed", "decisions-conflict", "forbidden-read-needed",
           "form-not-writable", "not-sealed")
STOP_WORDS = STOPPED[1:]              # every word but none
MISS_CLASSES = ("gold_wrong", "question_ambiguous", "retrieval_miss", "answer_wrong", "out_of_scope")

# -- S1: the planted briefs that name effort (W2-149's brief_text, one line added after its model line) -------------

def with_effort(text: str, value_yaml: str) -> str:
    lines = text.split("\n")
    at = next(i for i, x in enumerate(lines) if x.startswith("model: "))
    return "\n".join(lines[:at + 1] + [f"effort: {value_yaml}"] + lines[at + 1:])


def writer_brief(value_yaml: str) -> str:
    return with_effort(support.brief_text("writer", 5, budget=0.5, timeout=30), value_yaml)


def checker_brief(value_yaml: str) -> str:
    return with_effort(support.brief_text("checker", 3), value_yaml)


EFFORT_BRIEF = {v: f"w173/writer-effort-{v}" for v in EFFORTS}
CHECKER_HIGH = "w173/checker-effort-high"
# a value outside the five, as the YAML front matter holds it (the param id, the text after "effort: ")
BAD_EFFORT = {"loud": "loud", "upper-case": "High", "integer": "5", "list": "[high]", "empty-string": '""'}
BAD_BRIEF = {k: f"w173/writer-effort-bad-{k}" for k in BAD_EFFORT}

EXTRA_BRIEFS = {EFFORT_BRIEF[v]: writer_brief(v) for v in EFFORTS}
EXTRA_BRIEFS[CHECKER_HIGH] = checker_brief("high")
EXTRA_BRIEFS.update({BAD_BRIEF[k]: writer_brief(v) for k, v in BAD_EFFORT.items()})

# -- the argv recorder in front of W2-149's stub --------------------------------------------------------------------

RECORDER = r'''#!__PY__ -I
"""W2-173's recorder (acceptance tests only): keeps each call's raw argv, then runs W2-149's stub in this same process
(exec: the stub's pid, parent and stdin are the launch script's) with every --effort pair taken out of the argv."""
import json, os, sys

REAL = __REAL__
REC = __REC__
argv = sys.argv[1:]
with open(os.path.join(REC, "argv-raw.jsonl"), "a") as f:
    f.write(json.dumps({"pid": os.getpid(), "argv": argv}) + "\n")
rest, i = [], 0
while i < len(argv):
    if argv[i] == "--effort":
        i += 2
        continue
    if argv[i].startswith("--effort="):
        i += 1
        continue
    rest.append(argv[i])
    i += 1
os.execv(REAL, [REAL] + rest)
'''


def install_recorder(world):
    """W2-149's stub moved to bin/claude-w2-149; bin/claude is the recorder. world.write_stub keeps writing the stub's
    configuration (it only writes the program when bin/claude is missing)."""
    stub = world.bin / "claude"
    real = world.bin / "claude-w2-149"
    os.rename(stub, real)
    support._program(stub, RECORDER, REAL=real, REC=world.rec)


def raw_calls(world):
    p = world.rec / "argv-raw.jsonl"
    return [json.loads(x) for x in p.read_text().splitlines() if x.strip()] if p.exists() else []


def efforts_in(argv):
    """The values every --effort in one argv carries (``--effort X`` or ``--effort=X``)."""
    out = []
    for i, a in enumerate(argv):
        if a == "--effort":
            out.append(argv[i + 1] if i + 1 < len(argv) else None)
        elif a.startswith("--effort="):
            out.append(a.split("=", 1)[1])
    return out


def session_argvs(world):
    """The raw argv of each real session call (not the canary), matched to the stub's own record by its pid."""
    pids = {c["pid"] for c in world.session_calls()}
    return [r["argv"] for r in raw_calls(world) if r["pid"] in pids]


# -- the counts ----------------------------------------------------------------------------------------------------

def counts_schema():
    return json.loads(support.COUNTS_SCHEMA.read_text())


def counts_file(world, line):
    return json.loads((world.counts_dir(line) / "counts.json").read_text())


def schema_errors(line):
    return support.validate(counts_schema(), line)


# -- snapshots -----------------------------------------------------------------------------------------------------

def snapshot(root: Path):
    """Every entry under a folder: (relative path, 'dir' | 'link' | the file's sha256); None when it does not exist."""
    root = Path(root)
    if not root.exists():
        return None
    out = []
    for dp, dn, fn in os.walk(root):
        for n in dn:
            p = os.path.join(dp, n)
            out.append((os.path.relpath(p, root), "link" if os.path.islink(p) else "dir"))
        for n in fn:
            p = os.path.join(dp, n)
            out.append((os.path.relpath(p, root), "link" if os.path.islink(p) else support.sha_file(p)))
    return sorted(out)


# -- S3: the checker's set and notes (checker.md §6) ---------------------------------------------------------------

AUDIT_SET = "memory-audit-9"
SET_IDS = ("q01", "q02", "q03")


def plant_audit_set(world, ids=SET_IDS):
    """A planted question set: one file per id, the file named by its id (``<id>.yaml``), flat."""
    for i in ids:
        support.write_file(world.sr, f"fixtures/evaluation/{AUDIT_SET}/hidden/{i}.yaml",
                           f"id: {i}\nquestion: planted question {i}\ncategory: decision\ndrawn: changed\n")
    return world.sr / "fixtures" / "evaluation" / AUDIT_SET


QUESTION_LINES = [
    "q01 | accept | - | also: docs/d01.md#Planted doc 1 | the anchor holds the deciding line",
    "q02 | revise | R6-SPAN-MISSES | also: none | the anchor ends before the deciding line",
    "q03 | accept | - | also: none | the question reads one way only",
]
SET_LINES = [
    "domains: code 1, decisions 1, tickets 0, plan 0, contract 0, none 1",
    "categories: decision 1, contract 0, plan 0, ticket 0, exact-string 1, callers 0, code-paraphrase 1, "
    "kernel-template 0, multi-file 0, failure-memory 0, history 0, nonexistent-id 0",
    "keyword: any 0, all 0",
    "supersession 0, kernel roles or skills 0, failure or lesson 0, drawn changed 3, drawn sample or none 0",
    "set codes: none",
]


def notes_lines(questions=None, set_lines=None):
    return (["# Cross-check notes", "## Questions"] + list(QUESTION_LINES if questions is None else questions)
            + ["## The set"] + list(SET_LINES if set_lines is None else set_lines))


def notes_text(lines) -> str:
    return "\n".join(lines) + "\n"


def checker_result(lines=None, **override):
    """The checker's result.json counted from the notes' question lines (checked: the set's files)."""
    qs = [x for x in (lines or notes_lines()) if x[:1] == "q"]
    words = [x.split("|")[1].strip() for x in qs]
    res = {"checked": len(SET_IDS), "accepted": words.count("accept"), "revise": words.count("revise"),
           "rejected": words.count("reject")}
    res.update(override)
    return res


def checker_out(lines=None, result=None, **result_extra):
    lines = notes_lines() if lines is None else lines
    res = dict(result if result is not None else checker_result(lines), **result_extra)
    return {"notes.md": notes_text(lines), "result.json": json.dumps(res)}


# -- S4: the auditor's classes (auditor.md §6); the misses are W2-149's planted runs/audit-1/misses.jsonl ----------

MISS_IDS = ("m1", "m2", "m3")
AUDIT = "audit-1"
GOOD_CLASSES = {"m1": {"class": "retrieval_miss", "reason": "the gold place never reached the agent"},
                "m2": {"class": "retrieval_miss", "reason": "the gold place never reached the agent"},
                "m3": {"class": "gold_wrong", "reason": "the gold span ends before the deciding line"}}


def misses_of(classes) -> dict:
    """The result's five counts, from the classes' own words (every class of the five present, zeros included)."""
    words = [v.get("class") if isinstance(v, dict) else None for v in classes.values()]
    return {c: words.count(c) for c in MISS_CLASSES}


def auditor_out(classes=None, misses=None):
    classes = GOOD_CLASSES if classes is None else classes
    return {"classes.json": json.dumps(classes),
            "result.json": json.dumps({"misses": misses if misses is not None else misses_of(classes)})}


def audit_folder(world):
    return world.sr / "runs" / AUDIT


def audits_log(world):
    p = world.runs / "AUDITS.log"
    return p.read_bytes() if p.exists() else None
