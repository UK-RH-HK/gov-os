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
| What | Merge | gov accept |
|---|---|---|
| The run-time tool, slice 1 (DAEO-5rgj): gov msg, gov dispatch watch/limits, the interim stall check | f49132c5e | 62/62 |
| gov update and the pinned install (W2-17, W2-18) | 24981ca81 | 25/25, 28/28 |
| gov discover with W2-34 folded (W2-36) | 6b3c1d742 | 41/41 |
| Memory by construction and the memory-use log (W2-197) | 708eb2ec9 | 90/90 |
| The product close (W2-193, W2-194) | a34e51925 | 14/14, 11/11 |
| gov queue and DONE as the green landing (W2-115b) | (the merge after a34e51925) | 56/56 |
| gov backup, gov memaudit scan, gov decisions basis (W2-198) | (the merge after it) | 33/33 |
Also: the launcher's no-prompt default (b33eecd9e), gov pause honoured by gov launch (85710e6e6), the model rule's hook
(24a384ae8), start_lead.sh and start_cto.sh (d46f5b394), the archive and CLAUDE.md/AGENTS.md (fc4afeee3).

## 3. Running at the handover
- **In the outgoing CTO's session** (they end with it, so the outgoing CTO stays until they return): the in-flight
  tickets' lead (W2-191, W2-192, W2-195, W2-156, the close records of W2-145/W2-155) and the guard retirement
  (`e2/retire-guard`).
- **Independent sessions** (survive the handover; their end reaches `gov msg read cto`): `close-e2` (no repair tickets
  for base reds; no review gate in gov close), started by `start_lead.sh`, return in `.gov-runtime/scratch/orchestrator/log/leads/`.
- **EXAMIN CTO:** fresh session `examin-ec` in tmux `examin-cto`, Remote Control "EXAMIN CTO", brief
  `/home/usain/gov-os-runs/W2-27/examin/.gov-runtime/scratch/govos/FRESH-START.md`; guards off, no-prompt mode.

## 4. The machine and the budget
- The heavy slots are one at a time tonight (`tools/heavy_slots.conf` SLOTS=1, WORKERS=8; was 3 and 6): every test run
  through `heavy_slot.sh`, no `-n`. The rule for leads: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/036b4433-fcd4-48f3-bb08-6f78d034d878/scratchpad/HOLD.md`
  (copy it into the briefs folder if the scratchpad is gone). mem_guard runs (pid 513002). Load peaked at 161 at 01:43.
- Plan: 72 % at 01:16 (resets Sun 22 Nov 09:00 London); budget `log/budget.md`: 10 points reserved (two fresh 80s, the
  proving run), 18 for building (Wed 6, Thu 4, Fri 4, Sat 4). Read hourly by `tools/usage_log.sh`.

## 5. Next, in order
1. Land what returns: the in-flight tickets, the guard retirement, close-e2 (each through the slot; gov accept on the
   merged tree; record new gov commands in `src/gov/check/commands.py` and W1-32).
2. Release 0.1.3 for EXAMIN (gov update, the product close, memory by construction, the launcher defaults): the owner's
   steps as `docs/emergency-2/release-0.1.2/` (copy and edit), then `gov update` in EXAMIN.
3. The test map: 339 changed paths map to no suite, so `select.scoped` refuses on Gov OS; map them, then move Gov OS's own
   landing onto `gov queue`.
4. The first fresh 80 for Gov OS (JOB-20261116-17's design, with `gov memaudit scan` for the hidden set) from the reserve.
5. Run-time tool slices 2 to 4; the switch-over (a cron line `gov dispatch watch`, the CTO arms `gov msg wait`).
6. The proving run (W2-81's six repositories) on Sonnet; the Contract and Charter re-baseline after the owner's G5.
7. Known reds to look at: W2-13 latency and context_watch timing under load; W1-07's gov check timeouts under load;
   W2-115 strict (openspec not installed); test_cto_safety_nets reads the live inbox (isolate it).
8. The 5-minute cache for launched workers (`WORKER_CACHE_TTL` in the launcher, uncommitted until its tests pass).
