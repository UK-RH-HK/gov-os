"""P-R1's interim filter (delegated) and five brief-gap fixes (DEC-943) in the common lead brief, inserted after the
retrieval line (DEC-836); and the brief-gaps register's first rows. Safe to re-run."""
import pathlib
import sys

ROOT = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS")
B = ROOT / "governance/project/briefs/LEAD-w2-common.md"
G = ROOT / "governance/project/orchestration/brief-gaps.md"
t = B.read_text(encoding="utf-8")
ADD = (
    "- **P-R1 (delegated, 2026-10-30), until `gov retrieve` filters it itself:** every test designer's brief tells it to "
    "drop unread any `gov retrieve` result under its ticket's implementation paths (the ticket's `allowed_paths` outside "
    "`tests/acceptance/`), and to name in its return any such result it was served (DEC-820 (c)).\n"
    "- **Fixes from the leads' brief gaps (DEC-943, 2026-10-30):**\n"
    "  - **Waiting:** never wait in the foreground past a few minutes (the Bash tool stops it at ten); wait in a background "
    "script and check it with short calls.\n"
    "  - **A run held past 90 minutes** (by the load gate, the verification lock, a close or the nightly): stop waiting, "
    "write your checkpoint, and return PACKAGES naming what held it and what is left, rather than losing the run to the "
    "two-hour limit.\n"
    "  - **A new worktree has no store:** run `flock /tmp/gov-os-rebuild.lock gov rebuild` (this worktree's code) before "
    "the first worker, so its `gov retrieve` does not answer STORE_MISSING.\n"
    "  - **A worker's untracked scratch file** that neither you nor the worker may remove (the guard or the sandbox "
    "refuses): name it, with its path, in your return; the orchestrator has it removed before the close.\n"
    "  - **The probe record's `probed_commit`** is the full commit id the probe gate reads; DEC-911's 12-character rule "
    "is for files under `.gov-runtime/`, not for the committed probe record.\n"
)
if "P-R1 (delegated, 2026-10-30)" not in t:
    lines = t.split("\n")
    at = next((i for i, l in enumerate(lines) if l.startswith("- **DEC-836, memory used:**")), None)
    if at is None:
        sys.exit("retrieval line not found")
    lines.insert(at + 1, ADD.rstrip("\n"))
    B.write_text("\n".join(lines), encoding="utf-8")
    print("common brief: P-R1 filter and five gap fixes")
g = G.read_text(encoding="utf-8")
ROWS = [
    ("W2-05", "the merge-again test reads its own side", "this ticket's part", "5 (est.)", "open"),
    ("W2-05", "whether worker starts are load-gated; folding step 2 into the designer's run", "common brief", "15 (est.)", "common brief 2026-10-30: a run held past 90 minutes"),
    ("W2-05", "`gov retrieve` has no filter for the counterpart's files", "tool", "25 (meas.)", "common brief 2026-10-30: P-R1 interim filter; the tool fix is a row"),
    ("W2-05", "retrieval-regression cases fail inside the sandbox (no embedder)", "this ticket's part", "10 (est.)", "open"),
    ("W2-05", "nobody can remove a worker's untracked scratch under tests/acceptance", "common brief / tool", "10 (est.)", "common brief 2026-10-30: name it in the return"),
    ("W2-05", "W1-02's deadline support vs W2-L160", "this ticket's part / decision", "the park", "P-B1-1 to the owner"),
    ("W2-05", "the close's commit identity reads ~/.gitconfig vs W2-M161", "this ticket's part", "15 (est.)", "open"),
    ("W2-05", "close/gates.py starts tests without naming git (missing from the 27-file list)", "this ticket's part", "5 (est.)", "open"),
    ("W2-77", "no store in a new worktree (STORE_MISSING)", "this ticket's part", "4 (est.)", "common brief 2026-10-30: rebuild before the first worker"),
    ("W2-77", "a foreground wait passes the Bash tool's ten-minute limit", "common brief", "15 (est.)", "common brief 2026-10-30: background waits"),
    ("W2-77", "the probe gate reads probed_commit as a full id vs DEC-911's 12 digits", "common brief", "3 (meas.)", "common brief 2026-10-30"),
    ("W2-77", "checkpoint-before-probe commit order", "this ticket's part", "2 (est.)", "open"),
    ("W2-77", "a run loses its two hours waiting on the close's then the nightly's verification lock", "common brief", "60 (meas.)", "common brief 2026-10-30: a run held past 90 minutes; the queue takes the lock later"),
    ("W2-57", "a checkpoint committed after the run's rebuild leaves the index stale", "this ticket's part / skill checkpoint", "25 (meas.)", "open (skill: CIT-P)"),
    ("W2-57", "the load gate held its starts 19:30-22:20", "common brief", "150 (meas.)", "common brief 2026-10-30: a run held past 90 minutes"),
    ("W2-57", "flock is not first-come; a lock wait outlasted the two-hour window", "common brief / tool", "15 (meas.)", "common brief 2026-10-30: background waits"),
    ("W2-57", "a run past its gate waiting on the lock when CLOSE-RUNNING appears", "common brief", "5 (est.)", "common brief 2026-10-30: a run held past 90 minutes"),
    ("W2-57", "disk_gate.sh's printed verdict", "tool", "minor", "open"),
]
if "| 2026-10-30 | W2-05 |" not in g:
    g = g.rstrip("\n") + "\n" + "\n".join("| 2026-10-30 | %s | %s | %s | %s | %s |" % r for r in ROWS) + "\n"
    G.write_text(g, encoding="utf-8")
    print("brief-gaps register: %d rows" % len(ROWS))
