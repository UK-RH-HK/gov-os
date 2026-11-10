# Start here — the next CTO session (written 2026-11-10, final at ~15:15 UTC, by session ad44f5fe: the fresh-session handover of DEC-1110 (2))

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`, in
**emergency mode**. This file maps everything you need, in order. Where it and an older note differ, this file holds;
the register and the owner's word hold over both. **Next free id: DEC-1120.**

## 0. Where things stand (2026-11-10 ~14:30 UTC)
- **The lift is next:** about 11-11 (FORECAST-W2-2: lift 11-11, EXAMIN's copy 11-15, Wave 2's end 11-22, E). Its
  chain: ACT-CLAUDE-COPIES-3 (owner's yes) → this fresh session → **D-10 on the owner's word** (two full runs and
  fixes) → the re-pin ACT (row 88) → the owner's re-pin and push → the formal closes (row 97).
- **Done before the lift:** item 8; W2-139/140; W2-130's sitting; Q07/Q14; ADR-0002; the operator agent (W2-148, first
  live ACTs 11-10); **D-6 part 2** (complete 11-09); **D-5** (W2-128 rounds 1/2a/2b, W2-152, W2-153 merged; templates
  approved as 1.0.0, DEC-1116; ACT-CLAUDE-COPIES-1 and -2 applied by the operator agent); W2-56 with R3/R5 (S8's reach
  and S10 to Wave 3, DEC-1114); W2-149 with F11 and set-up A's wiring; W2-141's staged hook rebuilt on the live guard.
- **D-10's red-fix list: ready** except (a) the adapter-portability family (47 cases), which turns green with
  ACT-CLAUDE-COPIES-3 (verified in a clone), and (b) **W1-08's 10 cases** (found 15:16 by the landing check after
  ACT-WIN-TOAST-1, red on integrate since W2-128's templates): `tests/acceptance/W1-08/` uses the kernel's ticket and
  checkpoint templates as sample records, and the new templates (approved 1.0.0, DEC-1116) do not validate against
  `ticket.schema.json` and the checkpoint schema in that form. Fix by a test designer under DEC-866 (take the sample
  from the template's fenced block or a fixture); the templates do not change. Before D-10's run. The serial-phase blocker is fixed (`b78f862a9`); every lift ticket's map
  reads (`93ac67c0b`); `gov accept` enables `breadth` only, `lifted` report-only (`8f6e66a17`). Detail:
  `packages/LIFT-1/D10-REDS.md` §6, `P1-PLAN.md`'s D-10 row.
- **Usage: 58 % of the week at 13:56** (reset 11-15 09:00). **DEC-1115 (4): past 80 % before the lift, only the lift's
  critical path runs.** USAGE-1 (`packages/USAGE-1.md`): one meter point ≈ $27.5 at list price; most cost is long Opus
  contexts re-read. Keep your own context short; brief helpers to hand over past ~200k.
- **Nothing is running** but the session watchers (§6).

## 0c. YOUR FIRST TASK (DEC-1119), before the lift's other steps
1. **Find the owner's tiered rubric of model and effort by task** ("decided long ago, in this repository"). Search the
   register, the Contract (CAP-35 and its lenses, lens F included), the research and assessment records
   (`docs/research/`, `docs/assessment/`), the packages, the role files (`template/governance/kernel/roles/`) and the
   earlier session records (CHECKPOINT history, `log/`); then search again once in other words (tier, T0-T3, model
   choice, effort level, cost tier, routing). Bring it with its decision id and status, and name any conflict with
   DEC-839 or DEC-957. If no decision holds it, bring the closest map (e.g. lens F's T0-T3) for the owner to decide;
   **write none yourself**. A research helper may do the search (Sonnet is not for it: it is not ACT preparation).
2. **Then apply it before the lift:** in practice at once (every launch's and helper's model and effort by its tier:
   `launch_worker.sh`'s `LAUNCH_MODEL` and effort, the Agent call's `model` and `effort`, recorded in `spend.jsonl`);
   into the product through **W2-33 and W2-60a**, with a trial exception (W2-60a refuses a model not the role's),
   beside the lift's critical path without holding D-10, landing **before EXAMIN's copy**, so the dispatcher,
   `gov launch` and every launch apply each tier's model and effort. Check every committed path's class first.
3. Within it: **ACT-preparation helpers on Sonnet at effort high now** (Agent `model: "sonnet"`, `effort: "high"`;
   DEC-1119 (3) is the owner's explicit instruction); trials E then F only for roles the rubric leaves open, after the
   lift; not MODEL-TIERS-1's options 4 or 5 unless the rubric calls for them; option 6 as guidance in helper and lead
   briefs (`gov retrieve` for orientation questions; long command outputs cut to head and tail).
4. **A small ACT for the owner's operator:** `~/.claude/settings.json`'s `effortLevel` from `xhigh` to `high`
   (DEC-957's floor); class by class-rules.yaml; rehearsed with a planted HOME; one review; the exact yes line.
5. **An inventory, read-only, a short package (`packages/EMERGENCY-TOOLS-1.md`):** every tool, check and wiring built
   during the emergency (`.gov-runtime/scratch/orchestrator/tools/`, `~/gov-os-operator/install/`, the hooks, the
   crontab, `governance/project/orchestration/tools/`, the product), where each lives today, whether the kernel and an
   adopted repository need it, its route into the product (proven in use first, then a ticket), and which must land
   before EXAMIN's copy.

## 1. With the owner now (bring each in the first report if still open)
1. **Yes lines** (each on its own line, the agent's form `yes ACT-<id> <manifest sha8>`):
   `yes ACT-CLAUDE-COPIES-3 7368f4f2` (lift-critical: clears the portability family),
   `yes ACT-DEADMAN-WAKE-1 25c3af62` (the 60-minute wake into the CTO's inbox),
   `yes ACT-W2-149-INSTALL-1 dec93288` (set-up A's briefs and the launch script's list; class (O), by hand).
   After a yes: queue the two (b) bundles for the operator agent (`~/gov-os-operator/queue/<ACT>.req`, one line
   `ACT-<id> <64-hex manifest sha>`); the install ACT goes to the owner's operator by hand (package §5).
2. **By the owner's operator, by hand:** ACT-W2-149-INSTALL-1 after its yes. (ACT-OPERATOR-2 applied 11-10 15:04:20,
   APPROVED `b4a15c8f…`; ACT-WIN-TOAST-1 applied as `3849c1ca2`.)
3. **USAGE-1 decided (DEC-1118):** A, B, C in force (rule 11). **Yours to do:** (D) confirm on this CLI that
   `FORCE_PROMPT_CACHING_5M=1` gives launched workers the 5-minute cache (check `claude --version`, the official
   env-vars page, one planted worker's usage fields), then set it in `launch_worker.sh` and record it; (E, F) trials
   only after the lift. **Every session's list-price cost logged** (DEC-1118 (3)): a daily job from USAGE-1's scripts
   (`drafts/usage-1/collect.py`) appends the CTO's and the helpers' costs to `log/spend.jsonl` in its schema.
6. **MODEL-TIERS-1 (DEC-1118 (4)): done, with the owner** (`packages/MODEL-TIERS-1.md`, 11-10). Its options: (1) apply C
   as decided: every ACT-preparation helper's Agent call passes `model: "sonnet"` (and `effort: "high"` once the
   owner says so: a Sonnet helper does not take the session's effort, and the Agent tool's effort is set only on an
   explicit instruction); (2) E and F trials after the lift; (3) the map written through W2-33 and W2-60a after the
   lift, with a trial exception (CIT-P and an ACT); (6) brief guidance on `gov retrieve` and long Bash outputs; not 4
   or 5. Bring the owner's choice into the register; nothing else changes until then.
4. **D-10's word** (the full suite), after ACT-CLAUDE-COPIES-3 and this fresh session.
5. The owner's phone check of Claude notifications (DEC-1117 (2)); ntfy only if that is not the cause.

## 1b. The standing operating rules (DEC-1110 (1))
The list at the top of `governance/project/prompts/w2-orchestrator.md`: read it there first. In short: never idle
while unblocked work remains; DECIDED-NOT-DONE kept current; ACTs as messages for the owner's operator (the owner does
only re-pins, pushes, sudo); fixed briefs never changed without the owner; memory audited, notices resolved in a day;
usage recorded only, the brake at twice each projection (before the lift, past 80 % of the week only the lift's
critical path runs, DEC-1115 (4)); faults to the owner at once; waits by pid; after the lift, ready lists several
batches deep; only P1s, re-pins/pushes/sudo, class (b) yeses, fixed briefs, changes to standing decisions and
physical steps go to the owner, every other P2 is the CTO's (DEC-1112 (3)).
**Learned 11-09/10 (memory files hold them):** never leave a merge staged in the shared tree (merge in one command
with the ticket's trailer); before a brief edits a committed tool, check `class-rules.yaml`: (b)/(O) paths go by ACT;
give each round's spend projection in its brief (`launch_worker.sh --projection-usd`).
**Rule 11 (DEC-1118):** helpers hand over past ~200k context; the CTO checkpoints and clears at ~200k and before any
planned idle over an hour; ACT-preparation helpers on Sonnet (`model: "sonnet"` in the Agent call), reviews, test
design and engineering on Opus; every session's list-price cost logged.

## 2. The emergency: in force
- **What holds it:** DEC-1047; DEC-1049 (no nightly or full suite until the owner's word); DEC-1050 and DEC-1051;
  DEC-1052 (D-0 to D-11). DEC-1045 (no gitleaks scan); DEC-1091 (no budget cap; a runaway brake at twice each
  projection, now in `launch_worker.sh` and `spend.py`); DEC-1089 (3) (usage never pinged or alarmed, only recorded).
- **Allowed:** record commits; scoped test runs through `tools/heavy_slot.sh`; agents of their role for decided work;
  servers restarted from committed configs; one GPU job at a time.
- **Not allowed:** the nightly; the runs sweep; `tools/bench_loop.sh`; any full suite (D-10 only, on the owner's
  word); any `gov close`; any gitleaks scan; any machine change outside the repository except by an owner ACT; any
  commit on `w2/integrate` during a GPU measure.

## 3. Decided but not done — read at every session start
`packages/DECIDED-NOT-DONE.md` (rows 1-97; §0 to §0l). Keep it current: tick each item with its commit; add each new
decided item with its trigger the moment it is decided. The open rows that matter first:
- **Row 88, the lift's re-pin ACT:** carries W2-136, 137, 138, 141 (its staged hook `docs/changes/W2-141-hook/`, rebuilt
  on `74f8dbea4761`), 142, 145, 147, 20, 56, 153; revise or expect red g14's four engineer near-miss cases; re-run
  `drafts/w2-141-rebase/rehearse.sh` with the candidate pin; ADR-0002 re-read.
- **Row 97, the formal closes:** run `gov accept W2-92` and `W2-05` first; W2-151 closes on its evidence (no folder).
- **Rows 66, 75, 86 (set-up A):** after the install ACT's apply, record the declaration's amendment A6
  (`drafts/w2-149-sgx/PIN-AMENDMENT-A6.md`); before the overlap auditor's first real run, dry-build its wall at the pin
  and search it for any tell (F40: never write which side is which in DECISIONS-IN-FORCE, the register or `reviews/`).
  Set-up A's run waits on the week's allowance.
- **Row 87:** the replay check's follow-ups; no path-map or deny-list ACT through the agent before 2026-11-11 20:02Z.
- **After the lift:** W2-154 (the serial plugin, nightly.sh's serial count, the `brief` citation); row 89 (CAP-38.b);
  W2-20's sample day; the three-layer plan; W2-66c; the map rows of W1-49 (95-96) and W1-27 (S8).

## 4. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md`: the standing rules, §0, §1, §8 and §15.
2. **This file**, then `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`'s RESUME HERE (its first block).
3. `governance/project/orchestration/DECISIONS-IN-FORCE.md` from DEC-1097 to DEC-1117 and the delegated entries.
4. `docs/DECISION_REGISTER.md`: DEC-1110 to DEC-1117 in full.
5. `packages/DECIDED-NOT-DONE.md` §0h to §0l; `packages/FORECAST-W2-2.md`; `packages/USAGE-1.md`.
6. `packages/LIFT-1/P1-PLAN.md`'s D-10 row and `D10-REDS.md` §6.
7. The ACT packages with the owner: `ACT-CLAUDE-COPIES-3.md`, `ACT-DEADMAN-WAKE-1.md`, `ACT-W2-149-INSTALL-1.md`,
   `ACT-OPERATOR-2.md`, `ACT-WIN-TOAST-1.md`.

## 5. The order from here
1. The owner's yes on ACT-CLAUDE-COPIES-3 → queue it → after the agent's commit, re-run the portability family (W2-05,
   W1-38, W1-33, W2-57) on integrate; the live worktrees merge integrate.
2. The owner's word on D-10 → the full suite (`lifted` once; heavy slots; no commits during it); triage the reds by
   group the same evening; fix by role; second run.
3. The re-pin ACT (row 88), rehearsed and reviewed → the owner's re-pin and push → the formal closes (row 97),
   `gov plan --ready` (ready lists several batches deep, DEC-1110 (3)).
4. Beside, only if usage allows (DEC-1115 (4)): ACT-DEADMAN-WAKE-1 and ACT-W2-149-INSTALL-1 after their yeses;
   set-up A's run; ACT-OPERATOR-2 and ACT-WIN-TOAST-1 by the owner's operator.

## 6. Watchers, loops and digests to re-arm (each session)
- **The inbox waiter:** `bash .../tools/inbox_wait_quiet.sh` (background). File each item to `dispatch/inbox/read/`, re-arm.
- **The helper watch:** `python3 .../tools/helper_watch.py --every 300 --max 86400` (background; inbox items for a
  helper or worker dead on an error, silent 30 min, or gone without its exit file; re-arm after 24 h).
- **The sentinel check:** `bash .../tools/sentinel_check.sh` (background). Push the owner at once on a `*-sentinel-down.txt`.
- **`core.bare`:** `bash .../tools/bare_watch.sh` (background).
- **The store backstop:** `env SEED_REBUILD_CMD="bash .../tools/rebuild_pinned.sh" bash .../tools/store_refresh_daily.sh`.
- **Usage, record only:** `bash .../tools/usage_log.sh` (background; `log/usage.txt`; runs the brake check). Spend in
  `log/spend.jsonl` (one schema since 11-10; `tools/spend.py`); clear a brake with `spend.py clear <W2> --note`.
- **The digests (R-11):** CronCreate `2 9 * * *` and `2 18 * * *`, per prompt §15, ending `status_block.py --mark`.
- **Reports:** open with `status_block.py --countdown`, end with `status_block.py`; hand-kept facts in
  `log/report-state.json` (countdown, owner_action, examin, emergency: keep them current).
- Every wait and stop by pid only (`tools/proc.sh wait --max <s> <pid>`, `wait_for.sh <exit file>`); never Monitor.
- **After every record commit:** `tools/structural_pass.py <repo> HEAD~1`; `sync_context.py --commit "<subject>"`.
- The operator agent's ACT results: `~/gov-os-operator/log/operator-launch.out`; a landing check after each ACT commit
  (`log/landing-select.log`): triage RED by re-running the failing cases alone, with and without the ACT's files.

## 7. The checks at start
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` empty (or only helpers' files).
2. **Your session id into `.gov-runtime/scratch/orchestrator/log/cto-session.txt`** (the operator agent reads the
   owner's yes lines from that session's transcript, and the dead-man watches it); arm §6; `log/deadman.log`'s last
   line under 10 minutes.
3. The pin: `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/gov`. The guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS`
   = `PASS`; the live hook `74f8dbea4761…`, the path map `44f99ea563cb…`.
4. `git --git-dir=.git config --get core.bare` = `false`. The inbox read and filed.
5. **§1 and §3 read; anything whose trigger has passed is raised with the owner in the first report.**

## History
Earlier sessions' dated blocks are in CHECKPOINT.md below RESUME HERE and in this file's git history (the 11-08
version is at `ac9d12716`).
