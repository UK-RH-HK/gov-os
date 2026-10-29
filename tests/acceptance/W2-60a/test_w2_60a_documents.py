"""W2-60a, KPI success 9 and the statements KPI success 6 and 8 put in documents.

KPI success 9 [lens G Q4]: "Research first, by the lead before the engineer
starts: whether a paths:-scoped .claude/rules/ file loads in a headless worker
started by gov launch, its token cost, and whether the worker can change it;
recorded in docs/research/W2-60-rules-probe.md". The research is the lead's;
one case checks that the record exists and answers its three questions.

KPI success 6: "what the CLI gives no switch for is a package naming it, never
passed silently" (the design's P-W2-60a-1, the CLI's built-ins, and
P-W2-60a-2, user-level ``CLAUDE.md`` and rules and the resumed prompt). KPI
success 8: the shared record folder is "stated in the CIT-E". These cases read
the two documents at run time (the test designer has not read them: they are
this ticket's own files, DEC-820 (c)); a failure names what is missing, never
the documents' text.
"""

from __future__ import annotations

import re

import w2_60a_support as s

RESEARCH = s.REPO_ROOT / "docs/research/W2-60-rules-probe.md"
CIT_E = s.REPO_ROOT / "docs/changes/W2-60a-CIT-E.md"


def _text(path):
    assert path.is_file(), f"{path.relative_to(s.REPO_ROOT)} does not exist"
    return path.read_text(encoding="utf-8")


def test_the_rules_probe_record_answers_its_three_questions():
    text = _text(RESEARCH)
    lower = text.lower()
    missing = []
    if ".claude/rules" not in text or "paths:" not in text:
        missing.append("the paths:-scoped .claude/rules/ file it probes")
    if not any(word in lower for word in ("loads", "loaded", "not loaded", "does not load")):
        missing.append("whether the file loads in a headless worker")
    if not re.search(r"\d[\d,.]*\s*(k\s*)?tokens?", lower):
        missing.append("its token cost, as a number of tokens")
    if not all(tool in text for tool in ("Edit", "Write", "Bash")):
        missing.append("whether the worker's Edit, Write and Bash can change it")
    assert not missing, f"{RESEARCH.relative_to(s.REPO_ROOT)} does not state: {missing}"


def test_the_cit_e_states_the_shared_record_folder_and_names_the_packages():
    text = _text(CIT_E)
    missing = [what for what, present in (
        ("the record folder .gov-runtime/launches/", ".gov-runtime/launches" in text),
        ("every worktree's sharing it (the main checkout)", "main checkout" in text.lower()),
        ("the package naming the CLI's built-ins (P-W2-60a-1)", "P-W2-60a-1" in text),
        ("the package naming what is not measured (P-W2-60a-2)", "P-W2-60a-2" in text),
    ) if not present]
    assert not missing, f"{CIT_E.relative_to(s.REPO_ROOT)} does not state: {missing}"
