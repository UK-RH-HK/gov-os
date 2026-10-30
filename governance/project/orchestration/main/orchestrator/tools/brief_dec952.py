"""DEC-952 (owner, 2026-10-30, replacing DEC-880 item 2 (b)) in the common lead brief's draft
(drafts/LEAD-w2-common.dec952.md): scoped verification as a scoped close selects; the full suite only when that
selection is full; the verification lock only for full runs; the nightly as the integration check."""
import pathlib
import sys

P = pathlib.Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/LEAD-w2-common.dec952.md")
t = P.read_text(encoding="utf-8")
TOOL = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/scoped_plan.py"
EDITS = [
    ("- **No test cache (DEC-880, superseding DEC-852 item 2):** W2-48's cache was withdrawn, so your verification runs "
     "every suite in full, as before every return; this stays as it is when W2-66's path-scoped close lands, which "
     "narrows only what a close runs, never your verification.",
     "- **Scoped verification (owner, standing, DEC-952, replacing DEC-880 item 2 (b)):** you verify your ticket's own "
     "tests plus the affected tests, selected exactly as a scoped close selects them (W2-66). After your last commit, "
     "run `PYTHONPATH=/home/usain/gov-os-worktrees/{W2}/src python3 " + TOOL + " /home/usain/gov-os-worktrees/{W2} {W2} "
     "{ID}`: it prints the scope (`scoped` or `full`, with why) and the `pytest_options` (`--ignore`, `--deselect`) to "
     "add to step 4's two commands. Quote its scope and its reasons in your return. The full suite runs only when that "
     "scope is `full` (a change to the judge's own core, gov close, the guard, the checks or the selection, or anything "
     "else a close would run in full). The nightly is the integration check: the full suite once a day on everything "
     "merged, a red bisected over that day's merges."),
    ("  - **One run at a time, machine-wide:** start the run under the lock, `flock /tmp/gov-os-verify.lock <the run's "
     "command>`, and let it wait while another session's run holds the lock. Never run two verification runs at once.",
     "  - **The verification lock (owner, DEC-952 item 5):** only a full run (scope `full`) takes it: `flock "
     "/tmp/gov-os-verify.lock <the run's command>`, waiting while another session's full run holds it. A scoped run "
     "takes no lock."),
    ("   - **every suite under `tests/acceptance/` and `tests/unit`, in the close's form (DEC-889 items 6 and 12; "
     "worksteal waits for W2-67 or W2-57, DEC-892):** the full scope as before, but in one parallel run, then the "
     "serial-only cases alone, the way `gov close` runs them, each with JUnit XML:",
     "   - **the scoped selection (DEC-952), in the close's form (DEC-889 items 6 and 12; worksteal waits for W2-67 or "
     "W2-57, DEC-892):** the tests `scoped_plan.py` selects, its `pytest_options` added to both commands below (the "
     "full suite only when its scope is `full`), in one parallel run, then the selected serial-only cases alone, the "
     "way `gov close` runs them, each with JUnit XML. The `flock /tmp/gov-os-verify.lock` prefix below is for a full "
     "run only:"),
]
for old, new in EDITS:
    if new in t:
        continue
    if t.count(old) != 1:
        sys.exit("not found once: " + old[:70])
    t = t.replace(old, new)
P.write_text(t, encoding="utf-8")
print("draft brief: DEC-952's scoped verification")
