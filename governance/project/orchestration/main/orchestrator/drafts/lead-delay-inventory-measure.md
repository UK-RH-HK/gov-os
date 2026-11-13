# Lead-delay inventory: lead-hours lost, 2026-11-12 00:00 to 22:50 UTC (measurement for DEC-1156 (9))

Read-only measurement by a helper, 22:50 UTC. A **lead-hour** is one lead slot idle for one hour, or one hour of lead work
redone. The cap is 5 leads (`dispatch/config.json` `max_leads: 5`, DEC-1138).

## Slot use (the baseline)

Source: `tools/lead_ledger.py --since 2026-11-11T21:00 --md --no-write`. Each lead run counts from its start to its
return, and runs started before midnight are included. The count is taken minute by minute.

| Window | Lead-hours used | Idle slot-hours | Available (5 x h) | Use |
|---|---|---|---|---|
| 00:00-18:00 | 56.2 | 33.8 | 90.0 | 62 % |
| 18:00-22:50 | 14.6 | 9.6 | 24.2 | 60 % |
| **Whole period** | **70.8** | **43.4** | **114.2** | **62 %** |
| of which 03:00-05:00 (night hold) | 1.4 | 8.6 | 10.0 | 14 % |
| of which 21:49-22:50 (IDLE-REASON stated) | 2.0 | 3.1 | 5.1 | 39 % |

No minute had more than 5 leads running. Exactly 5 ran for 160 min of the day and 23 min of the night.

## Method

1. For each ticket, the waits between a lead's return and its next start come from the ledger rows, the `dispatch/ready.txt`
   comment lines, `dispatch/dispatch.log` and the commit times on `w2/integrate`. Each wait is given one cause.
2. Each idle slot-minute goes to the tickets waiting at that minute, one slot at most per ticket. When more tickets wait
   than slots are idle, the idle slots are shared among them. This answers the question: without the mechanism, the
   ticket's lead would have filled a free slot.
3. Idle slots with no waiting ticket are a residual: "no line prepared" (rows 12 and 14c).
4. Redone work is added on top of the idle hours.
5. The idle columns sum to the measured idle: 33.8 for the day, 9.6 for tonight.
6. Rows 2 and 3 do not overlap. Owner waits held overnight because the owner was not pushed are in row 2. The interface
   waits decided in the daytime are in row 3.

## The table

| # | Mechanism (who set it) | Lead-hours lost today (00:00-18:00) | Lead-hours lost tonight (18:00-22:50) | Method / evidence |
|---|---|---|---|---|
| 1 | Owner packages, daytime (owner awake), plus the CTO's own P2 decisions and re-release latency | **4.4** (owner 3.35 + CTO 1.03) | **1.4** (owner 0.78 + CTO 0.66) | Owner: W2-23 P-W2-23-8 and W2-115 PK-1 from 08:00 until DEC-1142 (~09:50, re-runs 09:55/09:59); W2-45 P-W2-45-2 15:01-16:44 (DEC-1148); W2-115 PK-6 16:15-17:17 (DEC-1150); W2-45 P-W2-45-4 18:48-19:54 (DEC-1153). CTO P2s: 17 gaps of 1-26 min (e.g. W2-121b tests→build 15:46-16:12; W2-121b 18:45-19:04; W2-171 08:00-08:17). Ledger "waiting on the CTO or the owner"; ready.txt comments; commits 37de9fcaa, ef69b937a, 486bc0fb6, b42bcff9e |
| 2 | Night push rule: owner pushed at night only for a P1 on EXAMIN's path (last night: only for the 99 % reset, DEC-1021 quiet hours; tonight: the CHECKPOINT "Tonight" line; ended by DEC-1156 (8) ~22:55) | **6.6** (W2-23 02:20-08:00, W2-115 03:27-08:00) | **3.2** (W2-98 21:05, W2-33 21:25, W2-113 21:26, W2-120 21:48, W2-160 22:23, each to 22:50) | Packages marked "to the owner at 09:00" in ready.txt and digest items 10, 12, 14, 16, 17. The owner was answering at 21:35 (DEC-1155) and at ~22:55 (DEC-1156), so the hold was a rule, not the owner's absence. Raw ticket-hours tonight: 6.05. Four of the five holds tonight are interface stops (see row 3) |
| 3 | Interface check before any worker (DEC-1052) | **3.95** (CTO-decided 1.77 + owner-decided 2.18) | **0.96** (CTO 0.41 + owner 0.55) | 14 stops: W2-121, W2-171, W2-159, W2-146, W2-124, W2-45, W2-121b, W2-172 (day); W2-160, W2-98, W2-33, W2-113, W2-120, W2-154 (night). The biggest waits: W2-171 01:50-03:00 (then the night hold, row 11); W2-124 11:50-14:01 (owner widening, fe7bd01ae); W2-160 19:12-19:57 (DEC-1153). Run time at the stop: 0.33 h day and 0.28 h night (1-5 min each). This is spent, not counted as lost. A further 2.9 h tonight is in row 2 |
| 4 | Brief / release refusals and pre-launch checks | **0.3** | **0** | W2-177 run 1 pulled 05:12 (old brief form; release_lead.sh refuses it, gov brief NEEDS_MISSING, 2a35ec307), re-briefed and started 05:19; W2-157 fix brief 14:31-14:41. gov brief refuses W2-11 and W2-152 (KPI_NO_VERIFY), so old-form briefs were used with no delay seen. release_lead.sh writes no refusal log, so its count is not measurable |
| 5 | Worktree creation (new_worktree.sh, cold store) and merging integrate into branches | **0.5** | **0.46** | Claim commit to first start: W2-124 11:08-11:24 (rebuild slow behind the land, incident 1116); W2-172 17:38-17:59; W2-160 and W2-88a 18:52-19:07/19:09; W2-98, W2-33, W2-113, W2-120, W2-154 1-6 min each. The integrate merges run inside the leads (e.g. W2-115 run 2's merge 1 min after its start), so their cost is inside the time used |
| 6 | The CTO's commit freezes during lands, and queue restarts caused by commits | **0.72** (restarts) | **2.0** (freeze) | Restarts ("moved while under test"): 10:53 (W2-180), 14:04 (W2-179), 15:50 (W2-146), plus 11:25 (incident 1116). Lead effect is counted on W2-172's start delay (14:04-14:22 and 15:50-16:28). Freeze tonight: W2-98, W2-33, W2-113, W2-120 and W2-154 were startable from 20:30 (CHECKPOINT 20:30 line). Their claims waited for land gaps: 21:00:45 after W2-124's land, 21:21 after W2-172's, 21:40 after W2-121b's. W2-154 run 2 waited 21:55-21:57 for W2-45's land. IDLE-REASON 21:49 |
| 7 | One land per batch (row 171), with ejections | **2.6** (queue 2.27 + ejections 0.27 + W2-11 redo 0.1) | **1.8** (ejection waits 0.87 + W2-172 run 3 redo 0.97) | Queue: W2-172 (EXAMIN's critical path) could start once W2-171 closed. W2-171 was DONE 12:51 (with its probe record) but landed 16:44 behind W2-11, W2-23, W2-177, W2-179, W2-178 and W2-146; this counts 13:15-17:05 less the restarts in row 6. Ejections: W2-121+W2-179 07:29 (two-ticket batch, so W2-159's claim waited until 07:47); W2-157 07:46 and 08:05; W2-11 12:51; W2-171 17:05 (W2-172 waited until 17:38); W2-172 21:18 (run 3 21:27-22:25, and W2-88 has waited since 21:18); W2-121b 21:37 (its re-run comes later). Land runs lost to ejection: 90 min day, 32 min night (`log/land-dispatch-20261112-*.out`). DONE→CLOSED waits: about 56 ticket-hours for DONEs before 18:00 (W2-158 9.9 h, W2-179 7.3, W2-178 6.2, W2-159 6.1, W2-177 5.0, W2-171 4.8, W2-146 4.6, W2-180 3.7) and about 9 tonight, both counting open tickets |
| 8 | Runaway / spend brake trips (DEC-1091) | **0.07** | **0.05** | 4 trips, each cleared in about 1 min: W2-115 02:32, W2-171 07:54, W2-172 19:20, W2-45 21:13 (`inbox/read/*spend-brake*`, `log/brake/cleared/`). The ledger shows 1-2 min brake waits. Only worker launches were stopped; no slot sat idle |
| 9 | The 5-lead cap | **0** | **0** | No minute had more than 5 leads (ledger minute count). The dispatcher's idle items appear only below the cap, and none named a startable line held by the cap. At most 0.36 h of unexplained start delay may be cap or forecast related; it is counted in row 10 |
| 10 | Memory / resource gate and admission (before ACT-DISPATCH-1 10:33 and ACT-P95-1 ~16:53) | **3.98** | **0** | (a) Forecast refusals until 01:06: held heavy slots were counted at their nominal peak (incident `2026-11-11-2323-T1`). W2-115, W2-52, W2-110, W2-176 and W2-23 lines waited 15-56 min (2.48). (b) Admission held 05:50-06:26 by a heavy step outside a slot (incident 0556); W2-121 run 3 and W2-179 waited (0.41). (c) LAUNCH_GATE_SHUT, memory: W2-124 11:24-11:47 and W2-157 14:41-15:03 (`log/W2-124-20261112-1124-launch.txt`, `log/W2-157-20261112-1441-launch.txt`) (0.73). (d) Unexplained start delays after a ready line: W2-159 07:49-08:14 and W2-146 08:52-09:19, likely the forecast (0.36, uncertain). Tonight: no refusal |
| 11 | Night hold (no new lead after 03:00 until the nightly ends; DEC-1138 (3), tools/night_hold.py) | **5.5** (sole cause) | **0** (not yet reached) | Hold 03:00:17 to 05:00:57 (`log/night-hold.jsonl`). The lines it held were 2 already-returned lines, so no fresh line was written for the hold. Sole cause: W2-171 (interface ruled 05:05, 00a9e4ed9), W2-121 (P-W2-121-5 decided 03:20, released 05:10) and W2-173 (03:41-05:07). Idle slots 03:00-05:10: 9.35 h, of which 3.9 h also had an owner wait (counted in row 2). The task named a 03:00-09:00 window, but the hold ended at the nightly's end, 05:00 |
| 12 | Dependencies (open deps) | **0 measured** (masked) | **0 measured** (masked) | After 21:49 every idle slot is held by row 2's tickets or by W2-88's wait on W2-172 (row 7). IDLE-REASON 21:49/21:50/22:25/22:28: W2-155 waits on W2-138 and W2-145; W2-111 needs load-50 runs; W2-130 is the CTO's own work. 38 tickets are not started (digest item 5, status_block; 33 `status: open` in `.tickets/`, 5 of them parked). Deps will bind once row 2's holds are answered (DEC-1156) |
| 13 | The idle check's escape (IDLE-REASON in log/stop-idle.log) | 0 (no IDLE-REASON before 21:49; 20 "no IDLE-REASON stated" passes) | **3.1 idle with a reason** (overlaps rows 2 and 7, so not added) | 4 IDLE-REASON lines: 21:49, 21:50, 22:25, 22:28. Idle slots 21:49-22:50: 3.10 h. The check records idle; it does not cause it |
| 14a | Usage 97 % stop (DEC-1140 (6); lifted by DEC-1149 (3) at 16:40-16:53) | **2.0** (idle 1.61 + resume redo about 0.4) | 0 | W2-158, W2-159, W2-181 and W2-146 CHECKPOINTED at 09:34-10:01 (`log/brake/cleared/*usage97*`). They resumed at 10:02-10:21. W2-181 was then parked (DEC-1142 (8)). The redo is an estimate of about 10 min per resumed lead |
| 14b | Network outage 02:00 | **0.65** (wait 0.35 + redo about 0.3) | 0 | W2-121 run 2 killed (7 min of run lost, resumed 02:19); W2-173 run 1 ERROR, resumed 02:17 (ready.txt comments) |
| 14c | No line prepared (startable tickets not yet claimed; the CTO's capacity or choice) | **3.37** | **0.65** | Residual idle: 11:53-13:56 (2.8 h: W2-45 claimed 12:48, during the morning decisions and the incident), 10:54-11:08, 01:32-01:40, 19:51-20:30 (W2-124 DONE; W2-98 and others were claimed only after the lands) |
| 14d | Heavy-slot waits (DEC-979) | **about 1-4 (estimate; inside time used, not added)** | about 0 | heavy_slot.sh keeps no wait log. Incident 1116: W2-180's land held all 3 heavy slots 10:53-12:28 while 4 leads sat in light phases. Earlier the same land hung 1 h 45 min on W2-157's backstop test. Upper bound: the ledger's unattributed gaps between workers, 974 min day and 0 night |
| 14e | Narrow checks (DEC-1154) and land pre-check refusals (DEC-802) | 0 lead-h | 0 lead-h (worker about 1-1.5 h) | Land REFUSED W2-115 19:13 and W2-121b 19:54 (no passing record at head, `land-dispatch-20261112-191305/195409.out`). W2-115 landed 0.7 h later and W2-121b about 1.5 h later. W2-172's check is running. These are ticket and worker delays, not slots |
| 14f | Guard refusals | about 0.2 (worker) | about 0.05 (worker) | 22 refusals today (`log/guard-refusals.jsonl`), 8 tagged false positives costing about 1 min each. Also the guard refused the CTO's removal of `.git/config.lock`, which is with the owner |
| 14g | Review rounds (DEC-1010 cap), kernel gate, CIT-P approvals, the two-refusal stop | 0 lead-h | 0 lead-h | 25 review rounds by day and 5 at night (167/69 min of review wait) are work. No cap stop was recorded. The kernel gate passed every land checked (exit 0). CIT-P waits (W2-146 11:53→DEC-1145 ~14:35; W2-88a to 09:00) held lands, not slots. The two-refusal stop: only the CTO's P1-D reviewer, refused twice by the memory gate; DEC-1146 now counts a gate refusal as a wait |
| | **Total idle attributed** (rows 1-7, 10, 11, 14a-c idle parts) | **33.8** | **9.6** | Equals the measured idle slot-hours |
| | **Redo on top** | **0.8** (W2-11 0.1, network 0.3, usage resumes 0.4) | **1.0** (W2-172 run 3) | |
| | **Total measurable loss** | **34.6** of 90.0 available | **10.6** of 24.2 available | **45.2 lead-hours over the period**, against 70.8 used |

## Ranking for the whole period (idle plus redo)

| Mechanism | Lead-hours |
|---|---|
| Night push rule (row 2) | 9.8 |
| Owner daytime and the CTO's P2s (row 1) | 5.8 |
| Night hold (row 11) | 5.5 (plus 3.9 shared with row 2) |
| Interface check (row 3) | 4.9 (plus 2.9 of row 2 tonight) |
| One land per batch and ejections (row 7) | 4.5 |
| Resource gate and admission (row 10) | 4.0 |
| No line prepared (14c) | 4.0 |
| Commit freezes and restarts (row 6) | 2.7 |
| Usage 97 % stop (14a) | 2.0 |
| Worktree creation (row 5) | 1.0 |
| Network outage (14b) | 0.65 |
| Brief refusals (row 4) | 0.3 |
| Brakes (row 8) | 0.12 |
| Cap (row 9) and deps (row 12) | 0 measured |

## Notes on uncertain numbers

- **The attribution is a counterfactual.** Idle slots are shared among the tickets waiting at each minute, one slot at most
  per ticket. Where more tickets waited than slots were idle (03:00-05:00, 21:49-22:50), a different sharing rule would
  move hours between rows 2 and 11, and between rows 2 and 7. Each row total could move by about 1-2 h; the grand total
  would not.
- **Row 2's tonight figure stops at 22:50.** DEC-1156 (~22:55) ended the hold. Had the five packages waited until 09:00,
  the loss would have grown to roughly 25-40 lead-hours: about 10 h for each of up to 5 slots, less the 03:00-05:00 night
  hold and less any other work. That figure is a bounded estimate, not a measurement.
- **Row 10 (d) and row 9.** The 25-27 min starts after a ready line (W2-159 07:49, W2-146 08:52) have no logged cause. The
  dispatcher logged no "not admitted" line, and `status.json` keeps no history. They are put down to the old forecast
  (incident 2323's cause) as the likeliest reason; the cap is the other possibility.
- **Row 14d (heavy slots)** is not measurable: heavy_slot.sh keeps no wait log. The bound comes from the ledger's
  unattributed gaps (16.2 lead-hours by day), which also hold the leads' own thinking time. The 1-4 h estimate rests on
  incident 1116 (all 3 slots held about 1.6 h, with 4 leads in light phases).
- **Row 7's queue figure** counts only W2-172's start delay, the one start known to depend on a land (W2-171). The other
  DONE→CLOSED waits (about 56 ticket-hours by day) held no slot. Their cost is in later work (W2-88, W2-45's merge order)
  and is not counted.
- **Ledger artefacts.** The open waits for W2-181 (792 min, parked by the owner), W2-159 (600 min, resolved by the CTO's
  commit d5b63037d, landed 18:51) and W2-152 (499 min, no re-run needed, landed 19:15) are not stalls. They are left out.
- **Redo estimates.** The usage-resume redo (about 10 min per lead) and the network redo (about 0.3 h) are estimates. The
  W2-172 run 3 redo (0.97 h) is measured.
- **"Used" lead-hours** include the leads' waits on workers, reviewers and heavy slots. Lead slot use therefore overstates
  useful work, and row 14d sits inside it.
- Times are UTC from file names, log lines and commit times. A worker's end can be off by a minute (`spend.jsonl` minutes).
