"""Adds rows W2-M408 and W2-L451 (DEC-939 item 2, ticket W2-76) and W2-L452 (W2-58's review cases inside a Claude
session) to the Wave 2 list, and updates the counts."""
import pathlib
import sys

LIST = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/docs/plan/WAVE_2_LIST.md")
M408 = ("| W2-M408 | Store rebuilds in several sessions on one machine run at once and contend for the code-graph daemon "
        "and gitleaks: a main-tree rebuild on 2026-10-29 took 6 h 39 min (04:10 to 10:49) while a lead rebuilt its own "
        "stores, against 271 s alone (P1-MORNING-2026-10-29 item 2) | engineer | One store rebuild at a time on the "
        "machine: every gov rebuild, in every session (main tree, worktree, clone, sandboxed or not), takes one "
        "machine-wide lock and says what it waits for (W2-76; until then `flock /tmp/gov-os-rebuild.lock`). | The owner, "
        "2026-10-29 (DEC-939 item 2; ordinary work: yes; other: other) |")
L451 = ("| W2-L451 | gov rebuild times only its lexical stage, and nothing records what a slow rebuild waits on, so the "
        "6 h 39 min rebuild of 2026-10-29 could not be diagnosed (P1-MORNING-2026-10-29 item 2) | engineer | The rebuild "
        "times every stage; past 30 minutes it records the stages done and each process's state and wait channel, flags "
        "itself slow and goes on (W2-76). | The owner, 2026-10-29 (DEC-939 item 2; ordinary work: yes; other: other) |")
L452 = ("| W2-L452 | W2-58's review cases (`tests/acceptance/W2-58/test_w2_58_review.py`, 178 cases) fail when pytest "
        "runs inside a Claude session: the session's own environment (its CLAUDE* variables) reaches the guard in the "
        "test's sandbox, which refuses without a reason; in a clean environment (env -i) all pass (2026-10-28) | "
        "engineer | The cases build their sandbox environment from scratch, so the caller's session variables never "
        "reach it. | The orchestrator, 2026-10-28 (ordinary work: no; other: other) |")
text = LIST.read_text(encoding="utf-8")
lines = text.split("\n")
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-M407 |"))
lines.insert(at + 1, M408)
at = next(i for i, l in enumerate(lines) if l.startswith("| W2-L450 |"))
lines[at + 1:at + 1] = [L451, L452]
text = "\n".join(lines)
for old, new in [
    ("W2-L450 (W2-07's run 5), so 961 were opened;",
     "W2-L450 (W2-07's run 5), W2-M408 and W2-L451 (DEC-939), W2-L452 (the orchestrator), so 964 were opened;"),
    ("so 945 are open, 61 of them high, 395 medium and 446 low.", "so 948 are open, 61 of them high, 396 medium and 448 low."),
    ("### 3.2 medium (395)", "### 3.2 medium (396)"),
    ("### 3.3 low (446)", "### 3.3 low (448)"),
]:
    if text.count(old) != 1:
        sys.exit("not found once: " + old[:50])
    text = text.replace(old, new)
LIST.write_text(text, encoding="utf-8")
print("added W2-M408, W2-L451, W2-L452")
