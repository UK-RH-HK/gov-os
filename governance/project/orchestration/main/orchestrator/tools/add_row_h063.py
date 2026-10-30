"""Adds row W2-H063 (the guard's hidden-part refusal is rooted at the session's own tree, checked 2026-10-29) to the
Wave 2 list after W2-H062, and updates the counts."""
import pathlib
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
H063 = ("| W2-H063 | The guard's refusal of an evaluation set's hidden part (DEC-820 (d)) is rooted at the session's own "
        "project root (`gov.guard.reads.parts`): a measured session in a worktree is refused the hidden part in its own "
        "tree, but allowed it in the main tree, in another worktree and in a run clone (checked with `policy_refusal` on "
        "2026-10-29, `tools/probe_hidden_rooting.py`). Once W2-61h writes the memory set's hidden half, a measured "
        "engineer could read it by an absolute path | engineer | The refusal matches a set's hidden globs under every "
        "tree of this repository (the main tree, every registered worktree, the run clones under `~/gov-os-runs/`), by "
        "real path, fail closed; W2-61h's auditor starts only after it lands. | The orchestrator, 2026-10-29 (from the "
        "brief drafter's finding; ordinary work: yes; other: other) |")
text = LIST.read_text(encoding="utf-8")
if "| W2-H063 |" in text:
    sys.exit("already in")
lines = text.split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-H062 |"))
lines.insert(at + 1, H063)
text = "\n".join(lines)
for old, new in [
    ("W2-L452 (the orchestrator), so 964 were opened;", "W2-L452 and W2-H063 (the orchestrator), so 965 were opened;"),
    ("so 948 are open, 61 of them high, 396 medium and 448 low.", "so 949 are open, 62 of them high, 396 medium and 448 low."),
    ("### 3.1 high (61)", "### 3.1 high (62)"),
]:
    if text.count(old) != 1:
        sys.exit("not found once: " + old[:50])
    text = text.replace(old, new)
LIST.write_text(text, encoding="utf-8")
print("added W2-H063")
