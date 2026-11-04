# D-4b engineer: bring a built memory branch up to today's integration head, verified, with its evidence per KPI line

CTO session 33b3628c, 2026-11-03, under DEC-1055 (D4B-MEMORY-STAGE, approved). Read first, whole:
`.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` (your common rules) and
`governance/project/orchestration/INTENT-DEC-1052.md` (the basis). Your task brief names the ticket; this file is the
method. No ticket is claimed and no lead runs (DEC-1051): you work as refactoring work, the way D-1 merged the memory
branches as built. The CTO merges your branch into `w2/integrate` after one independent review.

**Role:** engineer. You build to the spec and its KPIs, never to the tests: you may run the acceptance tests and see
only pass or fail (`gov accept <W2>`), never read `tests/acceptance/<W2>/` (nor any other ticket's cases revised for
your ticket). **Where you write:** only the ticket's worktree `~/gov-os-worktrees/<W2>` (its branch `w2/<W2>`) and
`TMPDIR=/tmp/gov-os-emg-<w2 lower case>`. Commits there, with `Task: <ticket id>`, `Implements: DEC-1055`,
`Role: engineer` and the Co-Authored-By line (EMG-common's form). Never on `w2/integrate`.

**Steps:**
1. Read the ticket (`.tickets/<id>.md` in the worktree; compare with the main tree's copy), the lead's last return and
   checkpoint (the worktree's `.gov-runtime/scratch/lead/CHECKPOINT.md`), and the files the branch changes
   (`git diff --stat w2/integrate...w2/<W2>`).
2. `git merge --no-ff w2/integrate` into the branch. Resolve any conflict to keep both sides' intent (the task brief
   names the known one); commit the merge. Do not change the ticket's code beyond what the merge needs, unless a test
   fails because of the merge: then the smallest fix inside the ticket's `allowed_paths`, named in your return.
3. A seeded store rebuild of the worktree, one D-4b rebuild at a time machine-wide:
   `flock /tmp/gov-os-d4b-rebuild.lock bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh ~/gov-os-worktrees/<W2> --seed`
   (in the background; it may take 10 to 80 minutes; a timed-out embedding is retried by the rebuild itself).
4. Verify, each run through `heavy_slot.sh`: `gov accept <W2> --json` (every KPI line's pass or fail); the scoped set
   from `select_tests.py` (EMG-common's form). A red you did not cause: re-run it alone, then name it; do not fix it.
5. Write the evidence file `docs/changes/<W2>-evidence.md` (create or extend; DEC-995, DEC-1055): one row per KPI line
   id (S1 ... F*), with: how it is verified (the `gov accept` line, a unit test, a measure record), the command, the
   result, the commit it was verified on; and a "verified on" line naming the merge commit. A line not verifiable
   without the memory measure says "measure: D-4b measure 1" (the CTO runs the measures). Commit it.
6. Leave the worktree clean (`git status --porcelain` empty, apart from ignored files).

**Return:** the twelve fields of EMG-common; in `evidence` the merge commit, the head, `gov accept`'s counts, the
scoped run's counts and time, the rebuild's time; in `files_changed` the commits.
