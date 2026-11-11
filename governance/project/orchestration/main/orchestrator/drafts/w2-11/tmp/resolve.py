"""Resolve the 9 hunks of the four skills by RESOLUTION.md section 5 (helper, scratch only).

Input: tmp/mf/<skill>.merged (git merge-file output, markers). Output: tmp/resolved/<skill>.md.
Each hunk is replaced by a fixed text keyed by (skill, index). Prints the hunk's marker text if the shape differs.
"""
import re
import sys
from pathlib import Path

MF = Path(__file__).parent / "mf"
OUT = Path(__file__).parent / "resolved"
OUT.mkdir(exist_ok=True)

VER = lambda v: f'version: "{v}"\nmetadata:\n  version: "{v}"\n'

H = {}
H[("discovery", 0)] = VER("1.1.0")
H[("retrieval", 0)] = VER("1.1.0")
H[("test-design", 0)] = VER("1.3.0") + (
    "description: Method for independent test design from the specification and KPIs, in parallel with the "
    "implementer and never reading its work.\n"
)
H[("test-design", 1)] = (
    "- The work order is in parallel: the designer works from the specification and the KPIs beside the engineer, "
    "at the same time as it builds the code from the same specification, in a worktree of its own, and never reads "
    "its work; neither waits for the other (DEC-959 item 7, DEC-963).\n"
    "- It never reads this ticket's implementation: no file the ticket's branch changes against its base, other than "
    "its own tests; a retrieval or search result under those paths is dropped unread and named in its return "
    "(DEC-820 (c)). It may read the integrated code it must work with, on the integration branch "
    "(DEC-963, DEC-820). Its retrieval uses the integration branch's store, never the ticket worktree's "
    "(DEC-963 item 2). Everything else is open to it (DEC-820).\n"
    "- When its tests are committed, the lead merges them and the implementer runs them once, reading results only, "
    "through the project's opaque acceptance runner where it has one (DEC-959 item 6).\n"
    "\n## Inputs\n\n"
    "1. The ticket: its specification, its KPIs (success and failure lines) and its acceptance test path (CAP-38.c).\n"
    "2. The public interfaces the ticket must work with, as they stand on the integration branch (CAP-38.c, DEC-963).\n"
    "3. Probe or QA findings, when present, as described behaviours (DEC-136, CAP-38.e).\n"
)
H[("orchestration", 0)] = VER("1.3.0")
H[("orchestration", 1)] = (
    "- A ticket lead per ticket is started in that worktree with its identity (the orchestrator role and the "
    "ticket's id), from the brief envelope `brief.md` and the lead template `role-lead.md` (DEC-236, DEC-1050).\n"
    "- No fixed number of tickets in flight: the eligible tickets, the resource gate and the owner's usage limits "
    "decide, each time a slot could open; every countdown says how many and why (DEC-847). A ticket idle on an owner "
    "answer frees its slot (DEC-235, DEC-363).\n"
)
H[("orchestration", 2)] = None  # integrate's line + W2-11's second line (built from the hunk below)
H[("orchestration", 3)] = None  # integrate's line + one sentence
H[("orchestration", 4)] = None  # integrate's three lines


def hunks(text):
    pat = re.compile(r"<<<<<<< integrate-HEAD\n(.*?)=======\n(.*?)>>>>>>> W2-11\n", re.S)
    return pat, list(pat.finditer(text))


for skill in ("discovery", "orchestration", "retrieval", "test-design"):
    text = (MF / f"{skill}.merged").read_text()
    pat, found = hunks(text)
    out, pos = [], 0
    for i, m in enumerate(found):
        out.append(text[pos:m.start()])
        ours, theirs = m.group(1), m.group(2)
        new = H.get((skill, i))
        if new is None:
            if (skill, i) == ("orchestration", 2):
                first = ours.splitlines(True)[0]
                second = [l for l in theirs.splitlines(True) if l.startswith("- Every return starts")][0]
                new = first + second
            elif (skill, i) == ("orchestration", 3):
                new = ours.rstrip("\n") + " A checkpoint is written at every handover (DEC-837 item 3).\n"
            elif (skill, i) == ("orchestration", 4):
                new = ours
        out.append(new)
        pos = m.end()
    out.append(text[pos:])
    (OUT / f"{skill}.md").write_text("".join(out))
    print(skill, len(found), "hunks resolved")
