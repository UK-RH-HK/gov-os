# Start here — the next CTO session (rewritten 2026-11-13 under DEC-1158 (4), for session b2f0511f's handover)

You are the Wave 2 orchestrator (the CTO), `orchestrator DAEO-sdxk`, in the main tree on `w2/integrate`. The emergency
of 2026-11-02 is lifted (DEC-1158): normal working, under DEC-1157's practices (§2). This file maps everything you
need, in order. Where it and an older note differ, this file holds; DECISIONS-IN-FORCE, the register and the owner's
word hold over both. **Next free id: DEC-1172** (DEC-1164 recorded: drafted, PROPOSED, the owner reading).

## 0a. THE COMPACTION TRIAL (DEC-1171 (6), from the 2026-11-14 morning handover, 3 days)
The CTO's launch line gains `--settings '{"env":{"CLAUDE_CODE_AUTO_COMPACT_WINDOW":"300000"}}'` (the CTO's session only). Each morning digest reports the day's stale facts, the owner's corrections, missed items and the CTO's cost, against 11-13's baseline (missed 5, corrections ~3, stale ~2).

## 0. NOW: read CHECKPOINT's RESUME HERE first, then the 09:00 digest's items
- **The current state** (leads running, the queue, what is in flight, what to record next) is in
  `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`, RESUME HERE (its newest dated lines first), and in
  `.gov-runtime/scratch/orchestrator/drafts/digest-0900-20261113-items.md` (the owner's packages and the open items).
- **Decided overnight 11-12/13:** DEC-1157 (every rule that held or delayed a lead removed, except the machine's and the
  governance's protections); DEC-1158 (the emergency lifted); DEC-1159 (the nightly beside the leads; W2-155 option 1,
  option 5 the fallback; the live reranker's limit). Committed `931281df5` and `75fcf97b0`.
- **Check first whether these landed** (CHECKPOINT 00:45): the nightly-beside-leads amendment of ACT-NIGHTLY-RESTART-1
  (its independent review was running; it had to be committed before 04:00); ACT-OPERATOR-HOURS-3 (the operator's
  crontab, class (b), and G9, class (O)), built by a helper for the owner; the prompt's §0 edit
  (`drafts/PROMPT-s0-dec1158.md`) for the owner's operator; this file and DECISIONS-IN-FORCE from their `.next.md` drafts.
- **The live pin is `pin-797495bdfc70`** (re-pin window 5, 11-11 13:31; `pin-bcea09060ebc` kept for rollback).

## 1. With the owner now (bring each in the first report if still open)
1. The digest's items (`drafts/digest-0900-20261113-items.md`), each as a full package: question, why now, options with
   costs, recommendation, links. Never a name only.
2. **The sweep's recommendations** (`drafts/dif-sweep-20261113.md`; DEC-1157 (16)): the owner decided only the emergency's
   lift (DEC-1158) and the nightly (DEC-1159). Every other row stays in force until the owner decides it; DECISIONS-IN-FORCE
   marks them "(the 09:00 sweep: recommended to supersede)" or "(… recommended to amend)". Its top 10 and the prompt
   edits (§0's emergency bullet, §3, §7, §15, rule 6) are the owner's.
3. **ACT-OPERATOR-HOURS-3** after its review: until it is applied the operator agent launches nothing from 02:10 to
   08:00 (DEC-1157 (2)); a queued ACT waits until 08:00. Check the review record's verdict block before queueing.
4. **W2-155:** one reading of the per-request GPU memory peak in a GPU window, then option 1 (`MAX_REQUEST_CHARS` about
   48,000) or option 5 (DEC-1159 (2)). No worker sends the live shared reranker requests above its limit outside a GPU
   window (DEC-1159 (3)).
5. The two peak figures re-measured from the lead ledger by 11-19 (DEC-1149 (4)).

## 1b. The standing operating rules (DEC-1110 (1))
The list at the top of `governance/project/prompts/w2-orchestrator.md`: read it there first (its §0 emergency bullet is
lifted by DEC-1158 until the owner's edit lands; DECISIONS-IN-FORCE holds over the prompt). In short: never idle while
unblocked work remains; DECIDED-NOT-DONE kept current; ACTs as messages for the owner's operator (the owner does only
re-pins, pushes, sudo); fixed briefs never changed without the owner; memory audited, notices resolved in a day; usage
recorded and reported only, never a stop (DEC-1149 (3)); the runaway brake at twice each projection stays a stop;
faults to the owner at once; waits by pid; only P1s, re-pins/pushes/sudo, class (b) yeses, fixed briefs, changes to
standing decisions and physical steps go to the owner, every other P2 is the CTO's (DEC-1112 (3)).
**No token cap for any session** (DEC-1141 (3)): full window and compaction, the hook writing the checkpoint; RUBRIC-2
(DEC-1120) for every spawn (name model and effort; `launch_worker.sh --class C0-C3 --model`).
**Learned (the memory files hold them):** never leave a merge staged in the shared tree (one command, with the ticket's
`Task:` trailer); before a brief edits a committed tool, check `class-rules.yaml` ((b)/(O) paths go by ACT); every
pytest through `heavy_slot.sh` with TMPDIR outside the repository; a resource gate's refusal is a wait (DEC-1146), a
permission refusal twice is a stop (DEC-1142 (9)); `log/act-in-progress.txt` holds every queued ACT in G9; check
before a ready line (role-lead.md in the worktree, brief non-empty, no `{UPPER}` slots, unused log name); a change
decided after review gets a narrow check without asking (DEC-1154); write `log/cto-standby.txt` while waiting.

## 2. How work runs now (DEC-1157, DEC-1158, DEC-1159)
- **The emergency is lifted** (DEC-1158): no freeze, no "nothing scheduled", no ban on the nightly, the runs sweep, the
  full suite or closes. Closes run by DEC-953's practices (`tk close` and a close record; never `gov close` here,
  DEC-1132 (1)). `log/report-state.json`'s `emergency` fact: "none (lifted, DEC-1158)".
- **No lead cap and no CPU band** (DEC-1157 (5), (8)): memory admits each start (the gate's 3 GiB floor plus 0.75 GiB
  per live session, DEC-1149 (1); the hold below 5 GB available; `mem_guard`; the OOM trip). A ticket on EXAMIN's
  critical path never waits.
- **No night hold** (DEC-1157 (2)): no lead start and no landing is held for the nightly; leads run all night.
- **No commit freeze during lands** (DEC-1157 (7)): commit when needed and accept the queue's re-test.
- **Lands in batches of two or three tickets with disjoint paths** (DEC-1157 (4)), through `tools/land.py` after
  `tools/kernel_gate.py`; a land holds at most two of the three heavy slots (DEC-1157 (10)).
- **Two lead lines prepared ahead at all times** (DEC-1157 (6)): claim committed, worktree built, brief checked, so no
  slot waits for preparation.
- **The interface stated at claim** (DEC-1157 (3)): the CTO writes each ticket's interface (from the ticket and the code)
  before its lead takes a slot; a lead returns an interface package only for a gap that statement leaves.
- **Merged dependencies count as met for starting** (DEC-1157 (9)): put `plan_override: DEC-1157` on the ticket so
  `gov launch`'s plan check admits it (it logs the override); closing still waits for the dependency to be closed. The
  product's own "merged" reading is parked to Wave 3.
- **Decisions that stop a lead go to the owner at once, at any hour** (DEC-1157 (1)), as a full package with a push;
  no quiet-hours wait for them. Widenings and KPI edits within a ticket's own purpose are yours, listed for the owner
  (DEC-1157 (12)); new tickets and splits are the owner's (DEC-974, DEC-1142 (8)).
- **Two logs** (DEC-1157 (13)): every start the dispatcher refuses (`tools/refused_starts.py`) and every heavy-slot
  wait (`heavy_slot.sh`'s wait log).
- **The nightly runs beside the leads** (DEC-1159 (1)): the 04:00 cron's `nightly_restart.sh` calls
  `quiet_check.py --beside-leads` (it ignores leads and their work, still waits for a land, a close, the queue, an
  ACT, a memory measure, the main tree, the rg storm); its own capped memory unit; `nightly_check.sh` at 08:00.
- **What still holds or delays work:** DECISIONS-IN-FORCE's top block (DEC-1157 (14)): the memory protections, the
  guard's refusals, the spend brake, the brief checks, review rounds, the kernel gate and the owner's approval of kernel
  bytes, new tickets and splits to the owner, the idle check's record.

## 3. Decided but not done — read at every session start
`packages/DECIDED-NOT-DONE.md` (under `governance/project/orchestration/`). Keep it current: tick each item with its
commit; add each new decided item with its trigger the moment it is decided. Bring any item whose trigger has passed
to the owner in the first report. The register's DEC-1142 to DEC-1159 each name their follow-ons.

## 4. The reading list, in order
1. `governance/project/prompts/w2-orchestrator.md`: the standing rules, §1, §8 and §15 (§0's emergency bullet lifted).
2. **This file**, then `.gov-runtime/scratch/orchestrator/CHECKPOINT.md`'s RESUME HERE and
   `drafts/digest-0900-20261113-items.md`.
3. `governance/project/orchestration/DECISIONS-IN-FORCE.md`: the top block, "Lifted", and DEC-1142 to DEC-1159.
4. `docs/DECISION_REGISTER.md`: DEC-1154 to DEC-1159 in full.
5. `packages/DECIDED-NOT-DONE.md`; `drafts/dif-sweep-20261113.md`; `drafts/lead-delay-inventory-measure.md`.
6. `governance/project/briefs/LEAD-w2-common.md` (the common lead brief: the two-refusal rule, DEC-1146, P1-G).

## 5. The order from here
1. RESUME HERE's open items, in its order; the leads running stay running.
2. Keep two lines ready; claim and state the interface; release as memory admits; lands in batches of two or three.
3. Every lead-stopping question to the owner at once as a package; every P2 decided and listed.
4. The 09:00 and 18:00 digests (R-11); the nightly's result at 08:00 case by case.
5. EXAMIN's path first (W2-27 and what it depends on: RESUME HERE and the digest's item 5 table).

## 6. Watchers, loops and digests to re-arm (each session)
- **The inbox waiter:** `bash .../tools/inbox_wait_quiet.sh` (background). File each item to `dispatch/inbox/read/`, re-arm.
- **The helper watch:** `python3 .../tools/helper_watch.py --every 300 --max 86400` (background; inbox items for a
  helper or worker dead on an error, silent 30 min, or gone without its exit file; re-arm after 24 h).
- **The sentinel check:** `bash .../tools/sentinel_check.sh` (background). Push the owner at once on a `*-sentinel-down.txt`.
- **`core.bare`:** `bash .../tools/bare_watch.sh` (background).
- **The store backstop:** `env SEED_REBUILD_CMD="bash .../tools/rebuild_pinned.sh" bash .../tools/store_refresh_daily.sh`.
- **The refused-starts log:** `tools/refused_starts.py` running (DEC-1157 (13)); the lead ledger
  (`tools/lead_ledger.py`) for the digests and the peak re-measure.
- **Usage, report only:** `bash .../tools/usage_log.sh` (background; `log/usage.txt`; the runaway brake check). Spend in
  `log/spend.jsonl` (`tools/spend.py`); clear a false brake trip with `spend.py clear <W2> --note`.
- **The digests (R-11):** CronCreate `2 9 * * *` and `2 18 * * *`, per prompt §15, ending `status_block.py --mark`.
  Session crons die with the session: re-arm them.
- **Reports:** open with `status_block.py --countdown`, end with `status_block.py`; hand-kept facts in
  `log/report-state.json` (countdown, owner_action, examin, emergency): keep them current.
- Every wait and stop by pid only (`tools/proc.sh wait --max <s> <pid>`, `wait_for.sh <exit file>`); never Monitor.
- **After every record commit:** `tools/structural_pass.py <repo> HEAD~1`; `sync_context.py --commit "<subject>"`.
- The operator agent's ACT results: `~/gov-os-operator/log/operator-launch.out`; a landing check after each ACT commit
  (`log/landing-select.log`): triage RED by re-running the failing cases alone, with and without the ACT's files.

## 7. The checks at start
1. `echo "$GOV_ROLE $GOV_TICKET"` = `orchestrator DAEO-sdxk`; `git status --porcelain` empty (or only helpers' files).
2. **Your session id into `.gov-runtime/scratch/orchestrator/log/cto-session.txt`** (the operator agent reads the
   owner's yes lines from that session's transcript, and the dead-man watches it); arm §6; `log/deadman.log`'s last
   line under 10 minutes; Remote Control and one test push (O-5).
3. The pin: `readlink -f ~/.local/bin/gov` = `/home/usain/.local/share/gov-os/pin-797495bdfc70/bin/gov`. The guard:
   `python3 .gov-runtime/scratch/orchestrator/tools/guard4_check.py --settings /home/usain/Dynamic-Agentic-Engineering-OS`
   = `PASS`; the live hook's and the path map's sha256 as the last applied ACT recorded them.
4. `git --git-dir=.git config --get core.bare` = `false`. The inbox read and filed.
5. **§1 and §3 read; anything whose trigger has passed is raised with the owner in the first report.**

## History
Earlier sessions' dated blocks are in CHECKPOINT.md below RESUME HERE and in this file's git history (the 11-11
version, written in emergency mode, is the live file's last commit before this rewrite; the 11-08 version is at
`ac9d12716`).
