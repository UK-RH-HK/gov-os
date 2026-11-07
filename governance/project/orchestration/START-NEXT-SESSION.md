# Start here — the next CTO session (written 2026-11-07 by session 812bc5ce, for the session that starts right after re-pin window 4)

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`, in
**emergency mode**. This file maps everything you need, in order. Where it and an older note differ, this file holds;
the register and the owner's word hold over both. **Next free id: DEC-1089.**

## 0. First: has the owner's operator run re-pin window 4?
- **The hold:** `log/act-in-progress.txt` (ACT-REPIN-W4, written 2026-11-06 23:5x). While it exists, make no main-tree
  commit (DEC-1028 item 6).
- **Done when:**
  - `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/gov`;
  - the operator's log `~/repin-w4.log` ends `RE-PIN DONE: pin-bcea09060ebc is live ...`;
  - the owner says "done".
- **If it is not done:** write `log/cto-standby.txt` with the reason and wait. Start nothing (the owner: "start nothing
  else; the hold stays").
- **If it printed `STOP` or `ROLLED BACK`:** read `~/repin-w4.log`, find the cause, and tell the owner. The old pin
  `pin-8284fb408bd4` is then live.

## 1. The emergency: in force
- **What holds it:**
  - DEC-1047: the emergency;
  - DEC-1049: no nightly full suite until the owner's word;
  - DEC-1050 and DEC-1051: everything stopped until the refactoring and the re-pins;
  - DEC-1052: the basis, the plan D-0 to D-11, and the basis as a standing practice.

  DEC-1045 (no gitleaks scan) stands.
- **Allowed:**
  - the steps below, in order, with engineers, test designers, reviewers and research as agents of their role;
  - scoped test runs through `tools/heavy_slot.sh`;
  - record commits;
  - the repository's own servers restarted from committed configs;
  - one GPU job at a time under the GPU rules.
- **Not allowed (must not start):**
  - any lead (the dispatcher's ready list stays empty) and any landing or queue run, until after D-10 and the lift;
  - the nightly;
  - the runs sweep;
  - `tools/bench_loop.sh`;
  - the guard-refusal harvest's schedule (run `tools/guard_refusals.py` by hand for the digest);
  - any full suite (D-10 only, on the owner's word);
  - any `gov close`;
  - any gitleaks scan;
  - any machine change outside the repository except by an owner ACT.
  - **`tools/usage_watch.sh` is off:** the digest says "usage: no measured source". Ask the owner whether to re-arm it.

## 2. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md`: §0, §1, §8 (the countdown) and §15 (the reports, the block, the
   digests).
2. **This file.**
3. `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, its **RESUME HERE**: its first block is the state at the
   hand-over.
4. `governance/project/orchestration/DECISIONS-IN-FORCE.md`, to DEC-1088. Above all DEC-1085 to DEC-1088:
   - the order: the build, then search-again, then end-to-end, then the fresh 80;
   - window 4 and its first test;
   - `gov plan`;
   - the standing rule that a closed ticket is never edited.
5. `docs/DECISION_REGISTER.md`: DEC-1085 to DEC-1088 in full.
6. The packages of the last two days, `governance/project/orchestration/packages/`:
   - `ACT-REPIN-W4.md` (what the re-pin carries);
   - `LIFT-1/SEVEN-ANSWERS.md` (the full picture the owner decided on);
   - `LIFT-1/DEPENDENCY-MAP-1.md` (W2-136);
   - `LIFT-1/D4B-SEARCH-AGAIN.md` (E1 and E2, declared before any run);
   - `LIFT-1/D4B-SCORE-ONCE.md` (the grid and every lever's result);
   - `LIFT-1/BUNDLE-BUDGET-1.md`; `LIFT-1/W2-32-S11-WORDING.md`.
7. `packages/LIFT-1/P1-PLAN.md`, the status table (D-0 to D-11).
8. `docs/research/W2-88-memory-practice.md`: how memory is built and used now.
9. The agents' common rules `.gov-runtime/scratch/orchestrator/briefs/EMG-common.md`; reviewers
   `governance/project/briefs/JUDGEMENT.md`.

## 3. What re-pin window 4 carries (`pin-bcea09060ebc`)
- **The builds:**
  - W2-92: the stated links (one bounded hop; each register item's status in the bundle);
  - W2-32 S11: the candidate pool, **not yet switched on** (§4 step 2);
  - W2-131 and W2-133: register items carry their own entry's id, not DEC-999;
  - W2-112's memory release: the shared reranker empties its GPU cache after each request and logs MiB;
  - W2-134 and W2-61h S7: the measure re-anchors gold in memory per commit, and source families;
  - W2-135: a line over 4,000 characters cut in a bundle item, marked `cut`;
  - W2-116 pass 1: `gov rebuild --integration`, the double-buffered integration store, and `GOV_STORE` set by
    `gov launch` for every worker;
  - W2-129: `gov links`;
  - D-6 part 1; D-9's records.
- **The ACT also:**
  - rebuilt the store at the commit;
  - restarted the shared reranker from the new pin (class 3);
  - installed W2-116's `reference-transaction` hook (`.git/hooks/`), so every update of `w2/integrate` refreshes the
    store in the background (`log/integration-store.log`).
- **Rollback:** one command, in ACT-REPIN-W4.md. `pin-8284fb408bd4` stays.

## 4. The steps after "done", in order
1. **End the hold:** `mv log/act-in-progress.txt log/act-in-progress.ended-<HHMM>-act-repin-w4.txt` (never `rm`). End
   `log/cto-standby.txt` the same way. Confirm the pin, the reranker (`tail -2 ~/.cache/gov-os/rerank.log`: READY
   from `pin-bcea09060ebc`, with MEMORY lines after requests) and the hook (`.git/hooks/reference-transaction`,
   executable).
2. **Switch the pool on** (W2-32 S11; DEC-1086 A). One commit to `governance/project/retrieval.yaml`, adding beside
   `routing:`:
   ```yaml
   pool:
     meaning_uncut: true
     route_depth: 60
     rerank_depth: 40
     per_file_first10: 2
     drop_nested: true
   ```
   Never before the switch: the old pin refuses the key.
3. **Check the hook refreshed the store:**
   - a new line in `log/integration-store.log` at the new head, from `gov rebuild --integration`;
   - `git -C "$(readlink -f ~/gov-os-worktrees/W2-00-store)" rev-parse HEAD` equals integrate's head;
   - a `gov retrieve` from the store has both facets, `rerank.by` service, and register items with their own ids.
   - **The speed check (DEC-1086 A):** time a plain search's median, the pin against the candidate, side by side.
   - **If the hook did not fire,** run `gov rebuild --integration w2/integrate` by hand and record why.
4. **The parallel-agents and memory test, before any experiment (DEC-1087 (10)).** Explain, then test:
   - agents in two worktrees search the shared integration store (`GOV_STORE` from `gov launch`, or `--root`), and read
     and edit their own worktree;
   - whether results carry their commit, or line numbers mislead an agent whose branch is behind;
   - what a search does during a refresh, and a continuation after the switch (W2-116's R2-F3: page 2 after a switch
     pages the other half);
   - the link graph and the dependency gating used (today: `depends_on` and the READY rule; `gov plan` comes with
     W2-136);
   - the search time with 10 and 20 agents at once;
   - **W2-112's live measure** (its review F1): the 20-search p50, p95 and max against 2.32, 3.82 and 4.01 s; the
     MEMORY lines against `nvidia-smi`; error answers and fallbacks counted.
   - **The test itself:** two agents in two worktrees searching while a merge refreshes the store. Report every gap to
     the owner before the experiments.
5. **Then the experiments (DEC-1087 (11)):**
   - E0 (the 138 through the live product: hit@5, @10, @20, in the bundle) and E0b (the same through the harness at
     the same commit), on a measure clone at window 4's commit;
   - E1, the search-again pilot (5 questions; `D4B-SEARCH-AGAIN.md`); **the pilot's cost to the owner, who sets the
     cap before E2**;
   - then E2, E3, E4, E5 (SEVEN-ANSWERS §7); the owner's decisions; the fresh 80, once.
   - E3 to E5 need their design package (reader, grader, rubric, cost, a proposed K9 bar) approved before any run
     (DEC-1085 (6)).
6. **Beside the experiments (CPU): W2-136** (`DAEO-p3ln`, `gov plan`, DEC-1088): tests first, the engineer, one review.
   It lands with W2-20's launch line (DEC-1088 (5)(b)), live at the lift's re-pin.

## 5. Watchers, loops and digests to re-arm (each session; with the new pin)
- **The inbox waiter:** `tools/inbox_wait_quiet.sh` (a Bash background run). Read and file each item to
  `dispatch/inbox/read/`, then re-arm. It fires on any item left in the inbox.
- **The sentinel check:** `tools/sentinel_check.sh` (background). Push the owner at once on a `*-sentinel-down.txt`.
- **`core.bare`:** `tools/bare_watch.sh` (background).
- **The daily store backstop:**
  `env SEED_REBUILD_CMD="bash .../tools/rebuild_pinned.sh" bash .../tools/store_refresh_daily.sh` (background; 10:00
  and 18:00). W2-116's hook is the primary refresh; this is the backstop until W2-116's S2 lands.
- **By hand after a merge,** if the hook did not run: the same `refresh_integration_store.sh` with `SEED_REBUILD_CMD`.
- **The digests (R-11):** CronCreate `2 9 * * *` and `2 18 * * *`. Each builds the digest per prompt §15, ends with
  `status_block.py --mark` (which writes `log/status-latest.txt`), and pushes its three most important lines. Session
  jobs: re-create them each session (7-day expiry).
- **Reports (DEC-878, DEC-948, DEC-1087 (6)):**
  - every report opens with `status_block.py --countdown` and ends with `status_block.py` (`--mark` after sending);
  - every message, the short ones included, ends with the block;
  - the hand-kept facts are in `log/report-state.json`;
  - a push on entering stand-by or starting a background job over 30 minutes, except in quiet hours.
- **The GPU backstop** (`tools/gpu_backstop.sh <pgid>...`, `arm` checks it is alive) is armed per GPU job.
- **The structural pass after every record commit:** `tools/structural_pass.py <repo> HEAD~1`. It now has a `links`
  family (`gov links --since <base>`, a notice). When it names new findings, fix those the commit made, such as a
  missing `sources:` entry.
- **Keep:**
  - `~/gov-os-worktrees/EMG-queue`, the guard suite's fixture (`test_guard_fix_4.py` writes a planted path into it);
  - `~/gov-os-runs/D4B/g1-fam`, the families re-score root.

## 6. Waiting on the owner
- **P1 now:** the operator's ACT-REPIN-W4, after the owner's push (pushed 2026-11-07: `w2/integrate` at `71b1f9b7`,
  `record/w2` at `74de225a`; the three script hashes checked).
- **P2:** ADR-0002, PROPOSED and cited by W2-112 (a `gov links` notice).
- **Later:**
  - the pilot's cost before E2 (the cap);
  - the E3 to E5 design package;
  - M3's adoption (DEC-1043), after all the experiments;
  - the 150-id sitting (DEC-1074 (7) O2);
  - the templates' approval and their `.claude/` copies (an ACT);
  - after the lift, the three layers' plan as a package (DEC-1087 (13));
  - whether to re-arm `usage_watch.sh`.

## 7. The checks at start (after the prompt's §1)
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` in the main tree empty.
2. Register: your session id into `log/cto-session.txt`; arm §5's background runs; one test push; the sentinel's last
   line in `log/deadman.log` under 10 minutes old.
3. **Holds:** §0. While you wait on the owner or the operator, keep `log/cto-standby.txt`. **Every wait and stop is by
   pid only (`tools/proc.sh`).**
4. **The pin** after the act: `readlink -f ~/.local/bin/gov` = `.../pin-bcea09060ebc/bin/gov`. The guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS`
   = `PASS`.
5. **The servers on the GPU:** both embedders 29/29 layers; the reranker READY on `cuda:0` from the new pin; a
   `gov retrieve` from `~/gov-os-worktrees/W2-00-store` gives `rerank.by` = `service`.
6. **`core.bare`:** `git --git-dir=.git config --get core.bare` = `false`.
7. **The inbox:** read and file each item.

## History
The dated blocks of every earlier session are in CHECKPOINT.md below RESUME HERE, and in this file's git history.
- the score-once grid and the levers;
- the trials;
- D-0 to D-9;
- the measure's audit;
- the night records `drafts/d4b/NIGHT*.md`.
