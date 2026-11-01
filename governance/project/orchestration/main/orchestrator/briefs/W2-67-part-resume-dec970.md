You are the ticket lead for ticket `DAEO-9nys` (`W2-67`, "test hygiene"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-67` on branch `w2/W2-67`.

**This is a resume, under DEC-968 and DEC-970: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first**, and your last return (`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/W2-67-A5-resume-dec954.json`). `git rev-parse --short=12 HEAD` must show `0978a976e85f` (the orchestrator merged `w2/integrate` in: ACT-GUARD-FIX-2, DEC-968 to DEC-970, your ticket's DEC-970 edit), and `git status --short` must show `?? tests/acceptance/W1-27/w2_67_td4_plant.py` only (the plant file, kept under DEC-920 item 5). Anything else: stop and return PACKAGES naming it.

## What DEC-970 decided for you, and what is left
- **P-W2-67-R6-DISP (a):** a second test-design batch for the two-line fix: in `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure`, `DEC-cyc1`/`DEC-cyc2` become `DEC-9003`/`DEC-9004` (W2-64's fixture ids), `Rewrite-Reason: DEC-954 merge of W2-64`, lowering nothing. Then a short review of that fix only (FULL; a new round).
- **Then:** the scoped run once; W1-30 green.
- **Rows for your return:** rev-6 G1 and G2 (README-W2-67's wording), KPI 4's count of four base folders on a run with a red, F-A, F-B and W2-L446.
- **Leftovers of run 6 to remove:** `.gov-runtime/scratch/td-10/after-PF15.log` and `.gov-runtime/scratch/lead/briefs/rev-5.filled.md` in this worktree.

## How this resume runs (the common brief holds; these are the points that changed since your last run)
- **The work order (DEC-963 as the common brief now states it):** a test designer works in the tests worktree (`/home/usain/gov-os-worktrees/W2-67-tests`, retrieving only from the integration branch's store); **you merge its branch** into this worktree while no worker's command runs here (the engineer's sandbox mounts the acceptance tests read-only, so it cannot); then the engineer, or a fresh one, runs the acceptance tests once, reading results only. A merge takes no `--trailer`: use a message file (`-F`).
- **Verification (DEC-968):** the scoped set `select_tests.py` gives, run once before you return, in the close's form. Never the full suite: the nightly runs it. `verify_lock.sh` now waits for nothing (DEC-970: a scoped run does not wait for a full run's room). A case that fails and that your change did not cause (it fails on `w2/integrate` too) is named for the CTO, who deals with it at once; one your change caused is yours to fix.
- **Installs** are refused for you; raise any as a P1. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-67`.
- **Clean up before you return:** remove your temp folders (`/tmp/gov-os-lead-W2-67` and your workers' `/tmp/gov-launch-*` folders) and any worktree you added; if a removal is refused, name what is left. 
- **Return:** the twelve fields, then `brief_gaps:` and `guard_refusals:` (each refusal with time, the command's form, the rule, true or false-positive, and its cost), status DONE or PACKAGES.
