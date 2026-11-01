# W2-11 (DAEO-k7hz) lead checkpoint — round 1 of 2 (DEC-916)

## State (2026-11-01 01:05)
- Branch w2/W2-11, base 4c064bab02b4, head be6186a802e2 (15 commits). Status clean apart from sandbox placeholder
  dotfiles and the stray `pytest-of-usain/` (185M, 21,038 inodes) and `gov-rebuild-4-xtmxc8yp.lock` in the worktree
  root (left by ps-4's run; my rm needed a permission prompt: for the orchestrator to remove).
- Round 1 built: briefs, orchestration skill (+4 reference files), audit, test-design (+test-kinds.md), qa-review
  (new, scenarios first), skill template (scenarios first), metadata.version on 9 kernel skills, rulesync sources,
  role file sweep sentences, CIT-P docs/changes/W2-11-CIT-P.md. CIT-P review PASS (be6186a8).
- Tests worktree W2-11-tests removed; branch w2/W2-11-tests deleted (git warned it could not lock the main repo's
  .git/config: another session held it).
- Verification: rebuild-2 exit 0 (00:45); collect-only clean (18685/18687, 2 deselected); scoped parallel run in
  progress (verify_b.py), then gov check, validator, trailer gate. No serial-route entry in scope.

## Verification (final, 01:50) — head be6186a802e2
- gov.__file__ = /home/usain/gov-os-worktrees/W2-11/src/gov/__init__.py; rebuild-2 exit 0 (00:45, 35 s incremental).
- select_tests: scoped, core_changed [], unplaced [], 38 targets; no serial-route entry selected.
- collect-only: "18685/18687 tests collected (2 deselected) in 18.66s", exit 0.
- scoped parallel run: 25 failed, 5108 passed, 2 skipped (30:44). 18 = missing .claude copies (P-5: 17 W2-11 +
  W1-33 agent definition[orchestrator]); 4 = W1-33 guard_and_launcher, red on w2/integrate (nightly 2026-10-31
  red-alone; fixture lacks .claude/hooks/pretooluse.py since ACT-1-GUARD) - not ours; 3 packaged test disputes
  (P-6, P-7, P-8); 1 validator (P-2). [25 = 17+1+4+2(P-6,P-8)+1(P-7)... see return]
- gov check exit 3: adapter-portability RED (P-5); retrieval-regression RED (time-out 600 s under load ~55-70);
  core-decision-citations YELLOW (time-out 60 s; alone: 195 DECISION_UNRECORDED, none on this ticket's commits);
  openspec-validate YELLOW (openspec not on PATH: my gov check call lacked the node PATH). Others GREEN.
- validator exit 0 on 9 skills; trailer_gate: "DAEO-k7hz: 21 commits, 21 judged, 0 lacking, 0 Implements item(s)
  not a decision or Contract id that resolves"; keyword_warn 0 files.
- Scratch: /tmp/gov-os-lead-W2-11 336M / 39,784 inodes; worktree .gov-runtime 462M / 3,224 (store);
  worktree-root pytest-of-usain 185M / 21,038 + gov-rebuild-4-xtmxc8yp.lock (orchestrator to remove);
  sandbox temp /tmp/gov-launch-independent-test-designer-7mjltxwv (td-1's 63M pytest trees, per its return).

## Commits (base..head)
45e57f00, 4f5dffc1 (ps batch 1) · 9cc3288d, 33816755 (td, merged) · 632e708b (lead merge) · adeda5b8, 99dd5ca5
(batch 2) · ecb7824a (batch 3) · a6999485, 8d6fbd72 (batch 4) · 7e1cb058, fe21fcb2 (repair 1) · 095167b8 (repair 2)
· 12e7e56c (lead gov checkpoint CP-DAEO-k7hz-0008) · be6186a8 (lead probe record).

## Loop
Repair iterations: converged on everything but the packaged cases (count held by the lead, DEC-096).

## Packages (return PACKAGES; none blocks the rest of round 1's text)
P-W2-11-5 copies (.claude/ read-only in gov launch's sandbox); P-W2-11-1 W2-60a reader vs metadata.version;
P-W2-11-7 W2-11 PYTHONPATH case vs W1-35 DEC-534; P-W2-11-6 W1-35 record-frontmatter case vs W2-L258;
P-W2-11-8 W1-35 discovery case reads front matter; P-W2-11-2 validator failure KPI + W2-L097 need src;
P-W2-11-3 DEC-808 schema fields not in paths; P-W2-11-4 vendored/openspec skills carry no version.

## What a resume must do
1. After the orchestrator's answers: one test-design batch (fresh designer, a new tests worktree from this head)
   for P-7, P-6, P-8 (Rewrite-Reason as decided); merge; TESTS-READY.
2. A session that may write .claude/ generates the 16 copies (P-5) with rulesync into an empty folder and copies
   only in-path files; adapter check green.
3. F1-F6 of the review ride along (CIT-P stale on the briefs' version and repairs 2-3; role file lead-return
   sentence; vendored skills named in §6; orchestration formatting; README-map dependency on W2-96; scenarios
   not yet run) - a fresh product-spec worker; then the scoped run once.

## Brief gaps (running)
- rulesync drops a top-level `version` from generated skill copies | ROLES-SPEC-1 G13 / this ticket's part | 25 (meas.)
- the skill validator and DEC-808's schemas are outside the ticket file's paths though its KPI/card need them | ticket file | 10 (est.)
- gov launch's sandbox makes .claude/ read-only although the ticket's paths include .claude/skills | tool / this ticket's part | 40 (est.)
- the designers' store W2-00-store is a link to W2-00-store-a | common brief | 1 (meas.)
- the Bash tool moves a foreground wait to the background at its timeout and kills it 10 min later | common brief | 15 (est.)
- the rebuild lock queue (flock, not first-come) held the first rebuild 78 min | common brief / tool | 78 (meas.)
- product-spec's Write is refused under .gov-runtime/scratch/<role>/ by the session's permission settings | common brief | 5 (est.)
- a lead cannot rm a worker's stray scratch in its own worktree (permission prompt) | common brief / tool | 3 (meas.)
- the order "gov checkpoint record before the final probe" vs a review already running | common brief | 5 (est.)
- W1-35's suite takes ~20 min (skill-regression cases ~2 min each) | this ticket's part | 20 (meas.)
