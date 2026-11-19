# CTO handover (the CTO session 10cfb730 → the fresh CTO on Fable, 2026-11-18 ~23:20)

Read `docs/emergency-2/EMERGENCY-2.md` first, then this page, then DEC-1211 to DEC-1216 in `docs/DECISION_REGISTER.md`
and the owner's page `docs/emergency-2/audits/OWNER-DECISIONS-2026-11-18.md`. **The owner is asleep until about 08:00.**
Nothing waits for him except the 99 % push; bring everything else in the morning brief.

## 0. Your standing orders tonight (the owner, DEC-1215)
- **Full pace, both CTOs**, no daily budget, no rationing, no reserve.
- **The 99 % push:** when the plan reaches 99 %, push the owner (PushNotification): he resets it, a Fable reset first.
  The plan is read hourly by `usage_log.sh` into `.gov-runtime/scratch/orchestrator/log/usage.txt` (78 % at 22:02).
  Arm a watcher for it yourself: the outgoing CTO's watchers end with its session. A ready script you can copy:
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/10cfb730-e5bb-4839-8b24-9e2a7b3327a8/scratchpad/night_watch.sh`
  (lead ends, the 99 %, the load over 20 three samples in a row; change its SEEN path to your own scratchpad).
- **Models (temporary, DEC-1215):** you, the EXAMIN CTO and C3 roles on `claude-fable-5-2` at high effort; Sonnet roles
  on Sonnet; the memory reader and grader as DEC-1098. Enforced by `governance/project/model-substitution.yaml` (read by
  `gov launch` and `.claude/hooks/agent_model.py`); the revert is written in that file and in DEC-1215 (2).
- **The machine:** keep the load inside the gate (20). Every test run through
  `.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` (it waits until the 1-minute load is under 12; SLOTS=2,
  WORKERS=4). Watch `lead-mem.jsonl` and `uptime`.
- **The night's priority order, his sleep and the reporting rule are DEC-1216** (added by the fresh CTO, 23:5x): the
  six priorities in his words; only the 99 % push wakes him; every report ends with the status block from
  `.gov-runtime/scratch/orchestrator/tools/status_block.py`, run each time; the morning brief's contents.
- **The plan's resets (DEC-1215):** the owner's first Fable reset was used on 2026-11-19 at 02:06 (the plan 99 % at
  02:04, pushed 02:05; after it 84 % all models, Fable 0 %). One Fable reset is left; when it is used, DEC-1215 (1)
  ends and the revert of (2) is the CTO's to make and record.
- **Leads end into your inbox:** `PYTHONPATH=src python3 -m gov.cli.main msg read cto` (start_lead.sh sends a wake).

## 1. Running at the handover (nothing is to be stopped)
| What | Where it returns | Note |
|---|---|---|
| Lead `rt-slice2`: the run-time tool's slice 2, the machine-aware dispatcher and load balancer (W2-199) | `log/leads/rt-slice2.json` | priority 1; never switch the live dispatcher before landing |
| Lead `k1-usage`: K1 / RT-8 the rubric in code, audit 09's usage rules in code (W2-201) | `log/leads/k1-usage.json` | started before DEC-1215: on landing, keep the substitution (its table says Opus; `substitute` maps it to Fable) |
| Lead `m1-context`: retire `gov context` and its module (W2-200) | `log/leads/m1-context.json` | C3 |
| Lead `g1-g2`: bundles and tar first, archive branch and tag, `git rm` the retired history; record/w2 | `log/leads/g1-g2.json` | lists what memory's index must drop |
| Lead `g4-g5`: the register by group (lands), then Charter v6 and Contract v5 on its branch + `docs/emergency-2/G5-APPROVAL.md` | `log/leads/g4-g5.json` | G5 is for the owner's yes by group in the morning: do not merge Part 2 |
| Lead `l2-build`: L2's A1, A3, A4, A5 (no yes needed) | `log/leads/l2-build.json` | C3; A2 after M1 lands |
| **The green-base run:** `gov.close.nightly` by hand through the slot (`--held 1,2`, 4 workers), started 23:05 on 09143b8c4 | `log/green-base-20261118.{json,err,exit}`; on green it writes `docs/close/nightly/NR-*.json` in the main tree | commit that record; it is the base `select.scoped` reads (NIGHT (c)) |
| The EXAMIN CTO (tmux `examin-cto`) | its own reports | the owner sent it his answers and `gov update` 0.1.3 from the CTO's note |

Lead briefs: `docs/emergency-2/briefs/NIGHT-COMMON.md` and `LEAD-<name>.md`.

## 2. Next, in order (DEC-1214 applied; no approval per ticket for this list)
1. **Restart the EXAMIN CTO on Fable** (DEC-1215 (4)) at a quiet point in its work (between steps; not mid-commit,
   mid-test or mid-`gov update`): it writes its checkpoint first (`.gov-runtime/scratch/govos/CHECKPOINT.md` in
   `/home/usain/gov-os-runs/W2-27/examin`), then start it fresh the way it was started:
   `tmux new-session -d -s examin-cto-<hhmm> -c /home/usain/gov-os-runs/W2-27/examin env -u GOV_ROLE -u GOV_TICKET ~/.local/bin/claude --remote-control 'EXAMIN CTO' --model claude-fable-5-2 --effort high --permission-mode bypassPermissions "Read .gov-runtime/scratch/govos/FRESH-START.md in full and follow it; then your CHECKPOINT.md, ADDENDUM-WAVE0-2026-11-18.md and the owner's latest answers, and carry on"`;
   once the new one has read in and taken over, end the old session (`/exit` in its pane, then `tmux kill-session -t examin-cto`).
2. **Land each lead as it returns:** merge into `w2/integrate`, run its folders on the merged tree through the slot,
   fix reds (a fix, not a review). Order of landing where they touch the same files: M1 before l2-build's A2; k1-usage
   with the substitution kept.
3. **The green base (NIGHT (c)):** when the green-base run ends: green → commit `docs/close/nightly/NR-*.json`; red → fix
   every red (leads), then after tonight's batch lands, one more full run the same way, until green. Then move Gov OS's
   own landing onto `gov queue` (L2-4 waits for the owner's yes: prepare, do not switch).
4. **The morning brief** for the owner (~08:00): what landed, the green base, G5's approval page, L2's page
   (`docs/emergency-2/L2-COMMANDS.md`, six lines L2-1 to L2-6), the leads' morning lines, the machine (peak load, samples
   over 20), the usage.
5. Then from DEC-1214: T2 (pushes for decisions; the escalation rubric proposal), G7 (the install record), memory's
   index cleaned after G1, the first fresh 80, run-time slices 3-4, the proving run, G3 later.

## 3. Done today (2026-11-18)
- Release 0.1.3 (tag v0.1.3 on 116aa23cd, C 1d4e6a875a5d, re-pinned pin-1d4e6a875a5d, pushed by the owner).
- The morning's 115 reds fixed by four leads and two test designers; landed. Contract 4.4 (DEC-1213, CAP-44.m) landed.
- DEC-1214 (the owner's decisions on audits 01-08 and EXAMIN's page), DEC-1215 (Fable, usage, this handover).
- W2-130 accepts owner-decided pairs by rule (09143b8c4). L2's page merged (0e7af74df).
- The load rule: `heavy_slot.sh` admission under 12, 4 workers a slot (the cause of the night's 104.6 and 194: pytest
  outside the slot; of today's 54: the CTO's unconfined full suites).
- The reranker runs from the new pin; swap was old pages from the night's peak (VS Code server 2.9 GB).

## How to run things without false reds
Absolute `PYTHONPATH`; node on PATH for openspec (`/home/usain/.nvm/versions/node/v22.23.3/bin`); rebuild the main
tree's store at HEAD before a full suite (or W2-54's context check is red, until M1 retires it); W1-35 and W2-185 in one
run clash on `conftest`; W1-30 alone takes about 33 minutes. The CTO's memory file `test-run-gotchas` holds the same.
