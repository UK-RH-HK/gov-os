# Start here — the next CTO session (written 2026-11-08 by session ad44f5fe, before its compaction)

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`, in
**emergency mode**. This file maps everything you need, in order. Where it and an older note differ, this file holds;
the register and the owner's word hold over both. **Next free id: DEC-1112.**

## 0. Where things stand (2026-11-08)
- **Re-pin window 4 is live** (`pin-bcea09060ebc`, 11-07 14:22); the pool is on (`c00d525f`); PAT-1 done.
- **Every experiment is done** (records in `packages/LIFT-1/`): E0 (106/138 hit@5; gold in the first bundle 123),
  E0b, E1's pilot, E2 (search again once: 83.3 % → 92.8 % right end to end), E2G (the glossary as consulted lowers:
  122 vs 128), E3 (today's 6,000-token bundle best of five), E3-SA, E4 (M3/M1 rank higher, answer no better: 111, 113
  vs 114), E5 (12,000 tokens no gain), G1's profile (the reranker's GPU saturated). Best: **the 0.6B's bundle with
  search again once, 128/138**.
- **Merged since window 4, live at the lift:** W2-136 (`gov plan`), W2-137 (the reranker's cap 64), W2-138 (the
  store's commit in results). **Filed, not started:** W2-139, W2-140, W2-141, W2-142.
- **Nothing is running** but the session watchers (§6).

## 0b. DEC-1098 (2026-11-09): the fresh 80 accepted; the work restarts
- **The fresh 80 ran 11-08:** K9's memory line met (78/79 right end to end, 0 wrong claims; `packages/LIFT-1/FRESH-80-RESULT.md`).
  **Standing:** the measured configuration is Gov OS's memory standard and every adopted repository's Wave 0 practice.
- **Started 11-09 (agents):** item 8 (W2-141, W2-20 rebuilt with DEC-1037's line, W2-142, W2-145 filed; test designers
  first); W2-130's sitting applied (patches, then an independent audit, then the CTO applies); W2-88-STANDARD-1 (the
  lines for the standard); P-SELECT-FIXES-1 (three proposals; the code route's figures by a counts-only script the CTO
  runs); SANDBOX-GUARD-EXP-1 (the design, to the owner before any run); Q07/Q14 re-worded (`Q07-Q14-REWORD.md`).
- **Then, in order:** W2-139/W2-140 in one batch; D-5 and D-6 part 2; D-10 on the owner's word; the lift (ADR-0002
  re-read at its re-pin). Track every item in `packages/DECIDED-NOT-DONE.md` §0 and §0b.

## 1. DEC-1097 (2026-11-08): the experiments decided; the road to the fresh 80
- **Decided:** the fresh 80 judges window 4's pin, pool on, today's bundle, search again once, at `c00d525f`, the
  visible-40 control first; every experiment runs on the 80 for data, only that one judged; **K9's bar: right end to
  end ≥ 85 % (≥ 68 of 79), wrong claims ≤ 5 % (≤ 3), target 95 %, hit@5 beside it**; keep the 0.6B (M3, M1 data
  only); G3 no change; W2-139/W2-140 held until after the 80. **The glossary (item 6) is OPEN:** ask the owner.
- **The order (DEC-1097):** ACT-GUARD-SETS-1 rebuilt; the fresh-80 scripts built and reviewed; the owner's checker's
  pass and the seven-reviewer readiness review in parallel, W2-130 and P-SELECT-GRAPH beside; then the ACT applied
  by the operator, the pre-flight and the control; then the 80. **Tell the owner when it is ready to launch.**
- **Started 11-08 (agents, records uncommitted until reviewed):** the ACT's rebuild (`drafts/sets-root-guard/`); the
  fresh-80 scripts (`drafts/fresh80/`, the declaration draft `packages/LIFT-1/FRESH-80-DECLARATION.md`); readiness
  reviewers 1, 2, 3, 4, 6 (`reviews/readiness-<n>-*.md`; 5 and 7 after the ACT and the scripts); P-SELECT-GRAPH
  (`packages/P-SELECT-GRAPH-RESULT.md`); W2-130 (`drafts/w2-130/`, `packages/W2-130-SITTING.md`); ADR-0002
  (`drafts/adr-0002/`); W2-145's draft (no private reranker, `drafts/w2-145/`).
- **Next wave (item 8, before the lift):** W2-141 (tests first), W2-20 rebuilt (its test designer for the new line),
  W2-145 filed and built, ADR-0002 reviewed and to the owner.
- **The owner's checker** has the brief (FRESH-80-READINESS §2); only counts and the new sha256 come back.
- **State at 11-08 evening:** FRESH-80-READINESS §7: everything on the CTO's side is ready and pinned; the owner's
  checker, operator (the ACT, the transcripts) and item 6 remain. Then the pre-flight, declaration, control, the 80.

## 1b. The standing operating rules (DEC-1110 (1))
The same list as the top of `governance/project/prompts/w2-orchestrator.md`: read it there first. In short: never idle
while unblocked work remains; DECIDED-NOT-DONE kept current; ACTs as messages for the owner's operator (the owner does
only re-pins, pushes, sudo); fixed briefs never changed without the owner; memory audited, notices resolved in a day;
usage recorded only, the brake at twice each projection; faults to the owner at once; waits by pid; after the lift,
ready lists several batches deep.

## 2. The emergency: in force
- **What holds it:** DEC-1047 (the emergency); DEC-1049 (no nightly or full suite until the owner's word); DEC-1050
  and DEC-1051 (everything stopped until the refactoring and the re-pins); DEC-1052 (the basis, D-0 to D-11). DEC-1045
  (no gitleaks scan) stands; DEC-1091 (no budget cap; a runaway brake at twice each projection); DEC-1089 (3) (usage is
  never pinged or alarmed, only recorded).
- **Allowed:** record commits; scoped test runs through `tools/heavy_slot.sh`; agents of their role for decided work;
  the repository's own servers restarted from committed configs; one GPU job at a time under the GPU rules.
- **Not allowed:** any lead or landing or queue run until after D-10 and the lift; the nightly; the runs sweep;
  `tools/bench_loop.sh`; any full suite (D-10 only, on the owner's word); any `gov close`; any gitleaks scan; any
  machine change outside the repository except by an owner ACT; **any commit on `w2/integrate` during a GPU measure**
  (its hook rebuilds the store).

## 3. Decided but not done — read at every session start
The full audit (251 action items in DEC-1047 to DEC-1096 and the owner actions since: 193 done, 15 not done, 36
waiting on a trigger, 7 superseded) is `packages/DECIDED-NOT-DONE.md`. **Keep it current:** tick an item off with its
commit when done; add every new decided item with its trigger the moment it is decided; raise any item whose trigger
has passed in the next report. A decision whose trigger is a stage ("after X", "beside X", "with X") is lost when
nothing notes it as X ends: check this list whenever a stage ends.

**Overdue (should already have happened by its own terms):**
1. **ACT-GUARD-SETS-1** (DEC-1084, DEC-1082 (3)): due right after window 4. Not applied; patch stale (`apply.sh check`
   exit 1); add the 80's reader folder. **Before the 80.**
2. **W2-141** (DEC-1093 (2), `DAEO-xwro`): to be built beside the experiments. Not started. Ready before the lift.
3. **G3, overlapping slices** (DEC-1090 (4)): to be decided after E0. Undecided; recommendation in FRESH-80-READINESS §6.
4. **G1's "fewer scored pairs" option** (DEC-1094 (1)): to be brought after E3 to E5. Never brought; any ranking
   change means re-measuring the 138 (FRESH-80-READINESS §4).
5. **W2-20's launch line** (DEC-1088 (5)(b)): to land with W2-136. W2-136 merged without it; W2-20 not rebuilt (branch
   of 10-17). Rebuild to the line and W2-136's F2 entry criterion; review; merge before the lift.
6. **W2-130's link cleanup and the 110-decision reconciliation list** (DEC-1074 (7), DEC-1073 (2), (5)(a)): due right
   after window 4. Not started (`DAEO-q8cl`). Feeds the 150-id sitting.
7. **The P-SELECT-GRAPH trial** (DEC-1062): a D-9 step. Not run (research, CPU only).
8. **W2-84's hidden-half cases deleted** (DEC-1061 (4)): due at D-9. Still in `tests/optin-lifted-guard.txt` and
   `tests/unit/guard/test_w2_84_trees.py`; with ACT-GUARD-SETS-1's rebuild.
9. **No private reranker beside the shared service** (DEC-1048 (5), DEC-1046 (1)): a follow-up after W2-112 landed.
   In no ticket; W2-112's KPI still falls back to a private reranker.
10. **P-LB-PRODUCT-1** (DEC-1048 (3)): to be decided after the investigation (done 11-03). Never brought back.
11. **Q07 and Q14 re-worded to stable facts** (DEC-1070 (13), DEC-1074 (8)) and **the visible 40's category
    shortfalls** (DEC-1074 (8)): open since 11-05; an independent writer.
12. **The status block counts K9 as done** from stale tags (DEC-948, DEC-1087 (6)): fix the source or keep it by hand.
13. **ADR-0002** (DEC-1093 (3)): refresh, one review, to the owner. Due now; deadline the lift's re-pin.
14. **The label audit** (DEC-1070 (14), DEC-1076 (5), DEC-1078 (4)): no cadence set; RUBRIC.md still v2. Needs a
    trigger from the owner.

**Waiting on the owner's word:** FRESH-80-1 §5; M3-ADOPTION-1 §6; GLOSSARY-1 §9 (W2-143 and W2-144 not filed);
the readiness review (FRESH-80-READINESS §5); the hold on W2-139 and W2-140 until after the 80; the verdict-transfer
check (FRESH-80-READINESS §4); the deferred embedder trial (DEC-1079 (d), DEC-1085 (4): no trigger).

**Before the 80 (after the owner's word):** the fresh-80 scripts (FRESH-80-1 items 14 to 19); the checker's pass.

**Before or at the lift's re-pin:** W2-142 (`DAEO-qskx`) built; W2-20 rebuilt; W2-141 and the guard ACT; the re-pin
carries W2-136, W2-137, W2-138, W2-20, W2-141, W2-142; D-5 (the templates, W2-128, the owner's approval and the
`.claude/` copies ACT); D-6 part 2; D-10 on the owner's word (with `lifted` once, `core.bare`'s half, W1-01b, W2-66b,
W2-90c).

**After the lift:** the 21 formal closes (W2-55 among them); the first numbered release (W2-27, before W2-81's run);
the three-layer plan (DEC-1087 (13)); D-11; W2-88 as a kernel skill; G-4 to G-6 re-scoped; W2-15a/b's corpora; W2-42a
resumed; the spill floor re-read about 11-13; the search-again adoption count weekly from about 11-21.

## 4. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md`: §0, §1, §8 and §15.
2. **This file**, then `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`'s RESUME HERE (its first block).
3. `governance/project/orchestration/DECISIONS-IN-FORCE.md` to DEC-1096 and the owner's word of 11-08.
4. `docs/DECISION_REGISTER.md`: DEC-1089 to DEC-1096 in full.
5. `packages/LIFT-1/`: FRESH-80-1, FRESH-80-READINESS, M3-ADOPTION-1, GLOSSARY-1, SEARCH-AGAIN-PRACTICE, then the
   RESULTs (E0 … E5, E0B, E2G, G1-PROFILE, PAT-1); `packages/ACT-GUARD-SETS-1.md`; `packages/K7-W2-REMAINDER.md`.
6. `packages/LIFT-1/P1-PLAN.md`'s status table; `docs/research/W2-88-memory-practice.md` §7 and §8.
7. Briefs: `governance/project/briefs/LEAD-w2-common.md`, `AUDITOR-common.md`, `JUDGEMENT.md`;
   `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md` (each carries the search-again line and the exclusion line).

## 5. After the owner decides (the order, if approved as recommended)
1. Record the decision (DEC-1097) with every item; bring DECISIONS-IN-FORCE, this file and RESUME HERE to it.
2. **ACT-GUARD-SETS-1:** an engineer rebuilds the patch against today's `.claude/hooks/pretooluse.py` and
   `governance/project/path-map.yaml`, adding the 80's reader-run folder to the hidden globs; rehearsal end to end;
   the CTO's review; the owner's operator applies; the guard check; live worktrees merge integrate. **Before the 80.**
3. The readiness review, if approved (seven read-only reviewers; FRESH-80-READINESS §5).
4. The fresh-80 scripts (FRESH-80-1 items 14 to 19), one review, pinned; the checker's pass (FRESH-80-READINESS §2).
5. The pre-flight and the visible-40 control, then **the fresh 80 once** under the fault rule (FRESH-80-1 §3.5).
6. Then W2-139 and W2-140 in one batch (held until after the 80); D-6 part 2 and D-5 on the CPU; ADR-0002's refresh;
   D-10 on the owner's word; the lift.

## 6. Watchers, loops and digests to re-arm (each session)
- **The inbox waiter:** `tools/inbox_wait_quiet.sh` (background). File each item to `dispatch/inbox/read/`, re-arm.
- **The sentinel check:** `tools/sentinel_check.sh` (background). Push the owner at once on a `*-sentinel-down.txt`.
- **`core.bare`:** `tools/bare_watch.sh` (background).
- **The store backstop:** `env SEED_REBUILD_CMD="bash .../tools/rebuild_pinned.sh" bash .../tools/store_refresh_daily.sh`
  (background; 10:00 and 18:00). W2-116's hook is the primary refresh.
- **Usage, record only:** `tools/usage_log.sh` (background; `log/usage.txt`); spend in `log/spend.jsonl`.
- **The digests (R-11):** CronCreate `2 9 * * *` and `2 18 * * *`, per prompt §15, ending `status_block.py --mark`.
- **Reports:** open with `status_block.py --countdown`, end with `status_block.py`; hand-kept facts in
  `log/report-state.json`. The block counts K9 as done from stale tags: correct it by hand (K7-W2-REMAINDER §5).
- **The GPU backstop** (`tools/gpu_backstop.sh <pgid>...`) per GPU job; processes in their own group
  (`run_group.sh`); every wait and stop by pid only (`tools/proc.sh`).
- **After every record commit:** `tools/structural_pass.py <repo> HEAD~1`; fix what the commit made.
- **The record branch:** `python3 governance/project/orchestration/sync_context.py --commit "<subject>"` hourly and at
  session end.
- **Keep:** `~/gov-os-worktrees/EMG-queue` (the guard suite's fixture); `~/gov-os-runs/D4B/` (the experiments' runs).

## 7. The checks at start
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` empty.
2. Your session id into `log/cto-session.txt`; arm §6; one test push; `log/deadman.log`'s last line under 10 minutes.
3. The pin: `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/gov`. The guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS`
   = `PASS`.
4. The GPU servers: both embedders 29/29 layers; the reranker READY on `cuda:0` from the pin; a `gov retrieve` from
   `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`.
5. `git --git-dir=.git config --get core.bare` = `false`. The inbox read and filed.
6. **§3's list read; anything whose trigger has passed is raised with the owner in the first report.**

## History
Earlier sessions' dated blocks are in CHECKPOINT.md below RESUME HERE and in this file's git history.
