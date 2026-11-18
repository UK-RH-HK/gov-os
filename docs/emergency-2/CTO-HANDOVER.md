# CTO handover (the outgoing CTO session 036b4433, the night of 2026-11-17 to 18)

Read `docs/emergency-2/EMERGENCY-2.md` first. This page is the state at the handover and what comes next. Facts carry
their commit; the register's DEC-1211 (EMERGENCY-2 approved) and DEC-1212 (the owner's audit 09 decisions) are in force.

## 1. What the owner decided and what waits on the owner
- **Decided tonight:** EMERGENCY-2 v3 (DEC-1211); audit 09's decisions (DEC-1212): the CTO's full window, a fresh CTO
  each morning, models and effort by the rubric enforced by code (helpers and leads on Sonnet, the CTO on Opus), the
  CTO's items; the working assumptions for gov queue (thin queue, DONE = the green landing) and the run-time tool
  (stall check in the dispatcher's tick, a push only for a CTO stall, no CPU fallback).
- **Waits on the owner (morning):** the one decision message `docs/emergency-2/audits/DECISIONS-FOR-THE-OWNER.md`
  (24 lines; the "building on" ones are already built). Add the leads' own questions: gov update's conflict rule (built
  (b)); the product close's untrailered first commit (recommended (a), (c) a Wave 3 row).

## 2. Landed on w2/integrate tonight (after release 0.1.2, tag v0.1.2 on 666f88d9b, re-pinned by the owner)
Each merged with gov accept green on the merged tree, and closed at the land (EMERGENCY-2 4.3):
| What | Merge | gov accept |
|---|---|---|
| The run-time tool, slice 1 (W2-121c, W2-121d folded): gov msg, gov dispatch watch/limits, the interim stall check | f49132c5e | 62/62 |
| gov update and the pinned install (W2-17, W2-18) | 24981ca81 | 25/25, 28/28 |
| gov discover with W2-34 folded (W2-36) | 6b3c1d742 | 41/41 |
| Memory by construction and the memory-use log (W2-197) | 708eb2ec9 | 90/90 |
| The product close (W2-193, W2-194), then no repair tickets and no review gate (W2-193 S6, S7) | a34e51925, 9b847bf0d | 22/22, 11/11 |
| gov queue and DONE as the green landing (W2-115b) | after a34e51925 | 56/56 |
| gov backup, gov memaudit scan, gov decisions basis (W2-198) | after it | 33/33 |
| The guard and the sandbox retired in the product (DAEO-gr7t) | b18c3ddec | (retirement; 1,892 unit passed) |
| W2-191, W2-192, W2-156, W2-195; W2-145 and W2-155 closed on their records | b7fb5cf92 .. 8158fe1f2 | 30, 30, 34, 45 |
Also: gov launch's no-prompt default, gov pause honoured, the 5-minute cache for launched workers, the model rule's hook,
start_lead.sh and start_cto.sh, the archive and the new CLAUDE.md/AGENTS.md, q22 re-anchored, the close's commit-check
tests out of the opt-in list, hourly backups (cron, `~/.gov-os/backups/`, Gov OS and EXAMIN).

## 3. Running at the handover
- **The full suite** (opt-in suites on), started detached by the outgoing CTO, alone on the machine: its log is
  `.gov-runtime/scratch/orchestrator/log/full-20261118.txt` (exit in `full-20261118.exit`). Read its reds first. Never run
  a full suite inside the one heavy slot: tests that call heavy_slot.sh themselves deadlock (it cost 1 h 45 min tonight).
- No lead runs. New leads start with `start_lead.sh` (independent Sonnet sessions; their end reaches `gov msg read cto`).
- **EXAMIN CTO:** fresh session `examin-ec` in tmux `examin-cto`, Remote Control "EXAMIN CTO", brief
  `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/FRESH-START.md`; guards off, no-prompt mode, the
  helper model hook (b797deb). It began Wave 0 step 3.

## 4. The machine and the budget
- The heavy slots are one at a time tonight (`tools/heavy_slots.conf` SLOTS=1, WORKERS=8; was 3 and 6): every test run
  through `heavy_slot.sh`, no `-n`. The rule for leads: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/036b4433-fcd4-48f3-bb08-6f78d034d878/scratchpad/HOLD.md`
  (copy it into the briefs folder if the scratchpad is gone). mem_guard runs (pid 513002). Load peaked at 161 at 01:43.
- Plan: 72 % at 01:16 (resets Sun 22 Nov 09:00 London); budget `log/budget.md`: 10 points reserved (two fresh 80s, the
  proving run), 18 for building (Wed 6, Thu 4, Fri 4, Sat 4). Read hourly by `tools/usage_log.sh`.

## 5. Next, in order
1. The full suite's reds (§3). Then the owner's morning decisions (§1), applied.
2. Release 0.1.3 for EXAMIN (gov update, the product close, memory by construction, the launcher defaults): the owner's
   steps as `docs/emergency-2/release-0.1.2/` (copy and edit), then `gov update` in EXAMIN.
3. The test map: 339 changed paths map to no suite, so `select.scoped` refuses on Gov OS; map them, then move Gov OS's own
   landing onto `gov queue`.
4. The first fresh 80 for Gov OS (JOB-20261116-17's design, with `gov memaudit scan` for the hidden set) from the reserve.
5. Run-time tool slices 2 to 4; the switch-over (a cron line `gov dispatch watch`, the CTO arms `gov msg wait`).
6. The proving run (W2-81's six repositories) on Sonnet; the Contract and Charter re-baseline after the owner's G5.
7. Known reds to look at: W2-13 latency and context_watch timing under load; W1-07's gov check timeouts under load;
   W2-115 strict (openspec not installed); test_cto_safety_nets reads the live inbox (isolate it).
8. Open small items: W2-195's launch refusal (LAUNCH_JUDGING_RULE_MISSING, narrowed) stays or becomes a gov brief flag
   (audit 4 suggests the flag); gov brief's retrieval time (W2-197's lead recommends a 60 s limit); the memory line in
   CLAUDE.md/AGENTS.md and the other skills (audit 2 M5, M6); held-out Read deny rules that gov adapters still writes and
   the indep-walls PreToolUse hook (permission editing, a separate §6.1 row); delete the W2-155 branch and the
   E2-finish-base worktree after bundling (audit 5); heavy_slots.conf back to SLOTS=2 or 3 once the night's rule ends.
