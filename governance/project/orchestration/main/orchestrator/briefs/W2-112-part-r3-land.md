You are the ticket lead for ticket `DAEO-clon` (`W2-112`, "One reranker serves every session: a shared, on-demand reranker service on the GPU"), profile FULL, working only in the worktree `/home/usain/gov-os-worktrees/W2-112` on branch `w2/W2-112`.

**This is the last run, to land (the owner's DEC-1048: P-W2-112-F9 (c)).** `git rev-parse --short=12 HEAD` must show `518d8e8f1c6d`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read your checkpoint (`.gov-runtime/scratch/lead/CHECKPOINT.md`) and DEC-1047 and DEC-1048 in `docs/DECISION_REGISTER.md` first.

## The owner's decisions since your return
- **DEC-1048 (P-W2-112-F9 (c)):** the interim GPU-slot module stays as the machine-wide guard; KPI success-7 is re-baselined (`.tickets/DAEO-clon.md`, committed `6a572a4c` and `0b344408` on `w2/integrate`): §5 of the research document records that the module is not to be retired by an ACT now, and is retired only when old code fails closed by construction (a later ticket). W2-112's code lands. **No third review round** (DEC-1010): the change after round 2 is the re-baselined text and its test, checked by your acceptance run.
- **P-W2-112-SLOTS (i)** moves after the landing, as a follow-up (DEC-1048 item 5): do not build it in this run.
- **DEC-1047:** everything else is stopped; this is memory infrastructure, allowed to finish. **DEC-1045:** no gitleaks scan anywhere; `select_tests.py` now leaves out the gitleaks-subject suites (named in its JSON).

## The run
1. Merge `w2/integrate` (`--no-ff`, `Task: DAEO-clon`, `Role: orchestrator`).
2. A fresh test designer in `~/gov-os-worktrees/W2-112-tests` (kept for this) revises `tests/acceptance/W2-112/test_w2_112_retirement_act.py` (and its README row) to the re-baselined KPI 7 (`Rewrite-Reason: DEC-1048`); then merge it here (`Role: independent-test-designer`) and remove the tests worktree and branch.
3. Your engineer rewrites §5 of `docs/research/W2-112-shared-reranker.md` to the re-baselined KPI 7 (no retirement ACT; the module stays; the retirement path (b) named).
4. Verify: `gov accept DAEO-clon` (every KPI line) and the scoped set from `select_tests.py`, through the gate, every red explained against the base (known: W1-19's gitleaks-PATH reds, DEC-1046 item 3; W2-59 hook_lines; W2-54 sandboxed_worker; load-sensitive timings). The real reranker service only if a case needs it, with the slot holder's rule in mind (DEC-1043).
5. Return DONE with the head; the CTO lands W2-112 through the queue.

**Estimate:** about 1.5 hours. Scratch (DEC-898): 20 GB and 1,000,000 files and folders; `TMPDIR=/tmp/gov-os-lead-W2-112`.
