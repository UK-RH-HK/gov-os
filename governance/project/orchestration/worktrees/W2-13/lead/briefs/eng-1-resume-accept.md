The lead has merged the acceptance tests: `/home/usain/gov-os-worktrees/W2-13/.gov-runtime/scratch/lead/TESTS-READY` now exists (merge commit bd329ce38f0a). Do this, and nothing else:

1. Check `git -C /home/usain/gov-os-worktrees/W2-13 log --oneline -1` shows bd329ce3.
2. Run the acceptance tests once, through `gov accept` only, with the sandbox's own TMPDIR (do not set TMPDIR): `cd /home/usain/gov-os-worktrees/W2-13 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-13/src python3 -m gov.cli.main accept DAEO-zqvn --json`. Never run `pytest` on `tests/acceptance/W2-13/`, and never read anything under it (DEC-820 (c)). If the run errors or times out, report its kind and stop; do not retry more than once.
3. Change no file and make no commit.

Return its per-KPI-line result (pass or fail, with the counts per line) and its totals, exactly as `gov accept` printed them, and its exit code. Refused twice for the same call: stop and say so; no third try.

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so; no third try.
