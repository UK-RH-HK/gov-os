"""Amends repair ticket DAEO-sg6x (the refused close of W2-71, 2026-10-30 02:12): the fault is in W2-71's own
acceptance test, so the role is the independent test designer and the path W2-71's acceptance folder (as DAEO-2upp);
the W2-54 time-limit red is a load question for the owner, not a repair, and the body says so. Parses the
frontmatter after the edit."""
import pathlib
import sys

import yaml

P = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-sg6x.md")
t = P.read_text(encoding="utf-8")
if "role: independent-test-designer" in t:
    sys.exit("already amended")
for old, new in (
    ("role: engineer\nallowed_paths:\n- src/gov/secrets/**\n- tests/unit/secrets_check/**\n",
     "role: independent-test-designer\nallowed_paths:\n- tests/acceptance/W2-71/**\n"),
):
    if t.count(old) != 1:
        sys.exit("not found once: " + old[:50])
    t = t.replace(old, new)
t = t.rstrip("\n") + (
    "\n\n## The orchestrator's reading (2026-10-30)\n\n"
    "- **W2-71's premise test:** `written_by_the_branch()` takes `git diff` from `merge-base(HEAD, w2/integrate)`, which "
    "is empty in the main tree once the ticket is merged, so the premise can pass only on the ticket's branch, never at "
    "its close; its sister test then checks nothing. The repair derives the ticket's files from its own commits (the "
    "`Task: DAEO-e8f0` trailer), with a `Rewrite-Reason:`, and lowers no expectation. Role and paths set to the "
    "independent test designer and W2-71's acceptance folder (MR-3), as for DAEO-2upp.\n"
    "- **W2-54's time-limit red** is a time limit missed under load (the close ran beside four leads; row W2-L429's "
    "family). It is re-run alone; if green alone, `load_sensitive` is the owner's list (DEC-757) and the morning "
    "package of 2026-10-30 asks. It is not this repair's work.\n")
fm = t.split("\n---", 1)[0].lstrip("-\n")
yaml.safe_load(fm)
P.write_text(t, encoding="utf-8")
print("DAEO-sg6x amended; frontmatter parses")
