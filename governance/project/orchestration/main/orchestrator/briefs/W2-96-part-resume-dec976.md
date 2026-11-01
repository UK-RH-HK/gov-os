You are the ticket lead for ticket `DAEO-ouet` (`W2-96`, "the opaque acceptance runner, gov accept"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-96` on branch `w2/W2-96`.

**This is a resume of run 2, under DEC-976 (P-W2-96-GATE (a)): read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("Run 2 END"), first**, and your last return (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/W2-96-A5-resume-dec970.json`). `git rev-parse --short=12 HEAD` must show `162f8f4ed51e` (your run-2 checkpoint commit), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## What DEC-976 decided, and what is left
- **P-W2-96-GATE (a):** you resume now that the queue lets you start; no exemption from the load gate. **P-W2-96-R9-PREMISE (a)** (your P3, `c348af6b`) stands.
- **Left, in this order:**
  1. your own red check of review 3's cases (td-4's `588e43ae` on run 2's code: the whole folder, and the new file alone);
  2. the engineer's one `gov accept DAEO-ouet` run on all 106 cases (resume eng-6, session `7db40b77-6636-42a9-a111-3ffe1a6fb25f`, with `briefs/eng-6-resume.md`, or a fresh engineer from the same brief), reading results only;
  3. review 4, the second and last review of this round (DEC-916): a fresh reviewer (brief A3, `JUDGEMENT.md`, effort max) on review 3's finding V1 and its fix (R14, R15: `b3dd46f8`, `a1d14a3f`) and on eng-6's fix of the `..` escape; add to its probe list processes started outside the child's process group (your V1 lesson);
  4. the rebuild on the final head, `select_tests.py`, the scoped run once, the probe record.
- **P3, still left:** if the empty `.claude/.cc-writes/` folder inside the acceptance folder is still there, your test designer removes it.
- **KPI 6** (the brief change naming `gov accept`) stays the orchestrator's at merge; your README map forms are recorded (`design-r2.md`).
- **If the load gate holds one step for more than 90 minutes again:** write your checkpoint and return PACKAGES; do not wait longer.

## How this resume runs (the common brief holds; these are the points that changed since your last run)
- **The work order (DEC-963 as the common brief now states it):** a test designer works in the tests worktree (`/home/usain/gov-os-worktrees/W2-96-tests`, retrieving only from the integration branch's store); **you merge its branch** into this worktree while no worker's command runs here (the engineer's sandbox mounts the acceptance tests read-only, so it cannot); then the engineer, or a fresh one, runs the acceptance tests once, reading results only. A merge takes no `--trailer`: use a message file (`-F`).
- **Verification (DEC-968):** the scoped set `select_tests.py` gives, run once before you return, in the close's form. Never the full suite: the nightly runs it. `verify_lock.sh` now waits for nothing (DEC-970: a scoped run does not wait for a full run's room). A case that fails and that your change did not cause (it fails on `w2/integrate` too) is named for the CTO, who deals with it at once; one your change caused is yours to fix.
- **Installs** are refused for you; raise any as a P1. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-96`.
- **Clean up before you return:** remove your temp folders (`/tmp/gov-os-lead-W2-96` and your workers' `/tmp/gov-launch-*` folders) and any worktree you added; if a removal is refused, name what is left. 
- **Return:** the twelve fields, then `brief_gaps:` and `guard_refusals:` (each refusal with time, the command's form, the rule, true or false-positive, and its cost), status DONE or PACKAGES.
