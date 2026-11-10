# EMERGENCY-TOOLS-1: what the emergency built, where it lives, and its route into the product (DEC-1119 (5))

Written by a read-only research helper for the CTO (DAEO-sdxk) on 2026-11-10 at about 15:45 local time, at `w2/integrate`
`95f4c0348`. Nothing was run except git, `ls`, `ps`, `sha256sum`, `crontab -l` and header reads. **M** means measured
(source named); **E** means estimated (basis named).

- **Question:** what tools, checks and wiring were built from DEC-1047 (about 2026-11-02) on, where does each live, is
  it in use, does the kernel or an adopted repository need it, what is its route into the product, and which must land
  before EXAMIN's copy (about 11-15, FORECAST-W2-2)?
- **Decision it feeds:** DEC-1119 (5), on DEC-1052 question 1 (what the emergency built reaches the product by its own
  route: proven in use first, then a ticket; INTENT-DEC-1052 item 5). DECIDED-NOT-DONE row 107.
- **Method:** every file in `.gov-runtime/scratch/orchestrator/tools/` changed since 11-02, compared byte for byte with
  `record/w2`'s copy (`governance/project/orchestration/main/orchestrator/tools/`); `git log --since=2026-11-01` on
  `governance/project/orchestration/{tools,nightly}`, `governance/project/operator/`, `.claude/hooks`, `src/gov`; the
  operator install compared by sha256 with the repository; the crontab, the git hook, both settings files' hooks and
  the running processes read; "in use" from the logs' times, the running processes and START-NEXT-SESSION §6-§7.
  W2-27's `deps:` for the EXAMIN path. **Stop rule:** 45 minutes, or every place in the brief covered once.

**Key:** **S** = the CTO's scratch, `.gov-runtime/scratch/orchestrator/tools/`. Every S file has a byte-identical copy on
`record/w2` (M, 95 of 95 files changed since 11-02, at 15:40), but **none is on `w2/integrate`**. **O** =
`governance/project/orchestration/tools/` on integrate. **OP** = `governance/project/operator/` on integrate, installed
in `~/gov-os-operator/install/` (sha256 identical, M). **H** = `.claude/hooks/` (tracked). "Re-pin" = the lift's re-pin
ACT (DECIDED-NOT-DONE row 88: W2-136, 137, 138, 141, 142, 145, 147, 20, 56, 153). Each "kernel" or "adopted" answer is
E (my judgement from the tool's purpose and the ticket that names it).

## 1. The table

### A. Wiring: cron, git hook, settings hooks, HOME installs

| # | tool / check / wiring | where it lives today | what it does (≤ 12 words) | decision | in use? (evidence) | kernel? | adopted repo? | route into the product | before EXAMIN's copy? |
|---|---|---|---|---|---|---|---|---|---|
| A1 | crontab: dispatcher tick `* * * * * run_tick.sh` | crontab; same text in `record/w2` `drafts/operator-1/backup/crontab.after` (M) | runs the dispatcher once a minute | DEC-1010 (6)-(7) | yes: `dispatch/status.json` 15:37 (M) | yes | yes | ticket W2-121 exists | yes, DEC-1008 |
| A2 | crontab: operator agent `*/10 0,8-23` | crontab; same committed copy | launches the operator agent from its queue | DEC-1104 (2), (5) | yes: `~/gov-os-operator/log/operator-launch.out` 15:40 (M) | no | no | none (this machine's) | no, machine-level |
| A3 | crontab: nightly, check, runs sweep commented out | crontab | the nightly stopped | DEC-1049, DEC-1050 | no (stopped) | — | — | none (restore at the lift) | no, stopped |
| A4 | `.git/hooks/reference-transaction`: store refresh after a landing | `.git/hooks/` (untracked); identical to `record/w2` `drafts/operator-1/reference-transaction.candidate` (M) | rebuilds the integration store after each integrate update | W2-116, DEC-1087 (3) | yes: `log/integration-store.log` 15:19 (M) | yes | yes | ticket W2-116 exists (its title says nightly and daily; the after-landing trigger is not named, E) | yes, W2-116 says so |
| A5 | same hook: the commit freeze (`freeze_gate.py`) | as A4; gate in OP | refuses live-branch updates during an operator ACT | DEC-1106 (3) | yes: armed on every update (M, hook text) | no | no | none | no, operator-only |
| A6 | same hook: landing selection | as A4; calls S `landing_select.sh` | scoped tests after a landing outside a ticket | DEC-1100 (2)-(3) | yes: `log/landing-select.log` 15:18 (M) | yes | yes | ticket W2-115 exists (DND row 40: "once proven in use") | yes, with W2-115 |
| A7 | `.claude/settings.local.json` PermissionRequest hook | local file (untracked); script in O | queues permission prompts for the owner | pre-emergency (11-01) | yes: `log/approval-queue.jsonl` 15:35 (M) | no | no | none | no |
| A8 | settings.local Stop hook: `stop_waiter_check.py` | local file; script in O | the CTO's stop names an unarmed inbox waiter | DEC-1027 E | yes: registered (no log of its own) | part | part | needs a ticket (after the lift) | no |
| A9 | settings.local Stop hook: `stop_idle_check.py` | local file; script in O | blocks the CTO idling while unblocked work remains | DEC-1110 (1) | yes: `log/stop-idle.log` 15:32 (M) | part | part | needs a ticket (after the lift) | no |
| A10 | `~/.local/bin/ollama` = S `ollama_query_cpu_wrapper.sh` | HOME (sha256 equal to S, M) | query server started on CPUs, no GPU | DEC-1033, DEC-1037 | yes: every query-server start goes through it | yes | yes | ticket W2-20 exists (the caps, `1a8c27f36`; DND row 20 the removal) | yes, W2-20 replaces it |
| A11 | reranker venv `gov_reranker_gpu_slot.py` | `~/.local/share/gov-os/reranker-venv/…/site-packages/`; source in O | a reranker waits for a GPU slot, never the CPU | DEC-1032, DEC-1033 | yes: every reranker load | yes | yes | ticket W2-145 exists (and W2-20) | yes, GPU budget |
| A12 | CTO sentinel (tmux `cto-sentinel`, Haiku, remote control) | process since 11-05 (pid 2621405, M); brief in O `sentinel-brief.md`; launch line in `record/w2` `drafts/dec991/ACT-SENTINEL-1.md` | watches the CTO; alerts the owner on a stall | DEC-998 | yes (running, M) | no | no | none | no, CTO-only |
| A13 | guard call log `~/.gov-os/guard-calls/` | written by H `pretooluse.py` | hashes of each guard decision, for the operator's replay | ACT-GUARD-CALLLOG-1, DEC-1108 (2) | yes: folder 11-10 00:00 (M) | no | no | none | no |
| A14 | in-session digests (CronCreate 09:02, 18:02) | the CTO's session only (re-armed from START-NEXT-SESSION §6) | the twice-daily digest ending `status_block.py --mark` | R-11 (prompt §15) | yes, by §6 | no | no | none | no |

### B. Guard hooks (this repository's own guard, H)

| # | tool / check / wiring | where it lives today | what it does (≤ 12 words) | decision | in use? (evidence) | kernel? | adopted repo? | route into the product | before EXAMIN's copy? |
|---|---|---|---|---|---|---|---|---|---|
| B1 | `pretooluse.py`: the five rules, with this emergency's ACTs (FIX-4, G14, SETS-1, INDEP-WALLS-1, CALLLOG-1, OPERATOR-1 rule 2d, SETS-GLOBS-1) | H | this repository's guard on every tool call | DEC-953 (2), DEC-1050 (8), DEC-1084, DEC-1108 | yes: every call; `guard4_check.py` PASS at each start (§7) | no (the product guard is `gov.guard` + the kernel hook) | no | already in product (DEC-820's rules in `gov.guard.decide`) | no, product has its own |
| B2 | `bash_writes.py` | H | reads what a Bash command writes (heredocs, variables, inline Python) | ACT-GUARD-FIX-3, DEC-958 | yes: imported by B1 | yes | yes | ticket W2-42a exists (in progress) | **yes**, DEC-1028 (4) |
| B3 | `role_reads.py` | H | role separation from the path map's `role_paths` | DEC-1052 G-14, DEC-1056, DEC-1058 | yes: imported by B1 | yes | yes | already in product (counterpart rule in `gov.guard.decide`; search filter `gov.util.role_paths`, W2-13 S5); W2-141 for the engineer's search, at the re-pin | no, product has it |

### C. Committed orchestration tools (O) and the operator agent (OP)

| # | tool / check / wiring | where it lives today | what it does (≤ 12 words) | decision | in use? (evidence) | kernel? | adopted repo? | route into the product | before EXAMIN's copy? |
|---|---|---|---|---|---|---|---|---|---|
| C1 | `dispatch/dispatcher.py` + `balancer.py` (the Load Balancer, GPU watch, embedder health) + `run_tick.sh`, `loop.sh`, `launch_now.sh` | O; reads S `heavy_slots.conf` | admits leads by measured peaks; watches GPU and servers | DEC-1007, DEC-1030, DEC-1032 iii, DEC-1039 (1b), DEC-1052 O-A1 | yes: cron A1; `dispatch/*.json` 15:37 (M) | yes | yes | ticket W2-121 exists (open, not started; P-LB-PRODUCT-1 never brought back, DEC-1048 (3)) | **yes**, DEC-1008 (K9) |
| C2 | `merge_queue.py`'s emergency changes (seeded copies, Q-1 attribution, slots, the freeze) | O; calls S `rebuild_slot.sh` and `select_tests.py` | tests the merged batch, attributes a red, lands | DEC-1001, DEC-1011, DEC-1033 (d), DEC-1050 Q-1 | not since 11-02/03, E: last `log/land-dispatch-*.out` 11-02 23:07, `merge-queue/` 11-02 15:48 (M) | yes | streams only | ticket W2-115 exists (W2-117 merged into it, DEC-1083) | no, LITE copy needs no queue (W2-117) |
| C3 | `deadman.py` (+ its wake, pending ACT-DEADMAN-WAKE-1) + `win_toast.ps1` | O (identical to S, M) | alerts the owner when the CTO stalls | DEC-988 (4), DEC-991, DEC-1007 | yes: `--watch` pid 4003607; `log/deadman.log` 15:35 (M) | part | part | needs a ticket (an adopted product's CTO watch, after the lift) | no |
| C4 | `indep_launch.py` + `indep-schemas/` | O | a walled headless session per approved independent job | DEC-1101, DEC-1109 (2), DEC-1112 (3) | not yet: ACT-W2-149-INSTALL-1 waits for the owner's yes | no | unknown (W2-88's verdict set may use it) | ticket W2-149 exists | no, E |
| C5 | `nightly.sh` changes (held slots, DEC-1045 switch, seeding) + `rotate.sh` | `governance/project/orchestration/nightly/`; calls S `heavy_slot.sh` | the nightly full run through the gate | DEC-1033 (d), DEC-1039, DEC-1045 | no: stopped (DEC-1049) | part | part | ticket W2-154 exists (the serial count) | no, stopped |
| C6 | `sync_context.py` follows the secrets switch | `governance/project/orchestration/` | the record sync skips scans when switched off | DEC-1045 | yes: after every record commit (§6) | no | no | none | no |
| C7 | operator agent core: `operator_run.py` (G1-G9, apply, undo, digest), `opcommon.py`, `operator_launch.py`, briefs | OP + installed (identical, M); `APPROVED` = `record/w2` `drafts/operator-2/APPROVED.after` (M) | applies the owner's ACTs by class from a queue | DEC-1104, DEC-1106, DEC-1107, DEC-1108 | yes: `operator.jsonl` 15:40 (M) | no, E | open question, E | ticket W2-148 exists (as a project tool; no product route decided) | no, machine-level |
| C8 | `act_class.py` + `class-rules.yaml` | OP + installed (identical) | classes an ACT a, b or O from what it touches | DEC-1104, W2-148 | yes: every queued ACT | no, E | open question | ticket W2-148 exists | no |
| C9 | `landing_check.py`, pinned `verdict.py`, `wall/` hook and settings template, `operator-settings.json` | OP + installed; settings = `record/w2` `drafts/operator-2/operator-settings.after.json` (M) | the after-checks and the operator's walled session | DEC-1106, DEC-1108 | yes: with C7 | no | no | ticket W2-148 exists | no |

### D. The CTO's scratch tools (S; all with byte-identical copies on `record/w2`, none on integrate)

| # | tool / check / wiring | where it lives today | what it does (≤ 12 words) | decision | in use? (evidence) | kernel? | adopted repo? | route into the product | before EXAMIN's copy? |
|---|---|---|---|---|---|---|---|---|---|
| D1 | `launch_worker.sh` | S | every worker's launch through `gov launch`, with checks and the brake | TPL-3b, DEC-1052, DEC-1079, DEC-1091 | yes: pid 4009228 now (M) | yes | yes | ticket W2-56 exists (merged, live at the re-pin); W2-60a (model and effort), W2-153 (template) | **yes**, DEC-1119 (2) |
| D2 | `spend.py` (spend log, runaway brake) | S | one spend schema; brakes a run at twice its projection | DEC-1089 (3), DEC-1091, DEC-1112 (3) | yes: `log/spend.jsonl` 14:15, `log/brake/` 14:12 (M) | yes | yes | ticket W2-60b exists (the session record); **the brake needs a ticket** | **yes**, runaway |
| D3 | `wait_for.sh` | S | waits on a job's exit file, bounded, by pid | TPL-3b, DEC-1079 | yes: pid 4009423 now (M) | part | part | needs a ticket (or a W2-56 line, E) | no |
| D4 | `lead_verify.sh` | S | a lead's scoped run, then the serial phase, in slots | TPL-3b, DEC-1050 T-5 | yes: in the lead brief; mentioned in CHECKPOINT 11-10 (M) | yes | yes | ticket W2-115 exists; W2-154 (serial) | yes, with W2-115 |
| D5 | `select_tests.py` + `nightly_only.txt`, `helper_exceptions.txt`, `load_sensitive.txt` | S | one scoped selection at every level, governance files out | DEC-953 (4), DEC-968, DEC-1045 (2), DEC-1050 Q-1, DEC-1061 (9) | yes: callers D4, D6, C2, `close_build.py` (M) | yes | yes | ticket W2-115 exists (the base, W2-66, is already product's `gov.close.select`) | **yes**, the scoped close |
| D6 | `landing_select.sh` | S | the selection after a landing that held a non-ticket commit | DEC-1100 (2)-(4) | yes: A6 (M) | yes | yes | ticket W2-115 exists (DND row 40) | yes, with W2-115 |
| D7 | `close_build.py` | S | the build-phase close on the audit's 10 practices | DEC-953 (1), (5), DEC-968 | no since 11-02 (no close in the emergency; `log/close-build/` 11-02, M) | yes | yes | ticket W2-115 exists | yes, with W2-115 |
| D8 | `land.py` (with `structural_pass.py` inside) | S | merge and close in one step through the queue | DEC-988, DEC-989, DEC-1050 Q-1, G-1 | not since 11-03, E (as C2) | yes | streams only | ticket W2-115 exists | no, LITE copy |
| D9 | `structural_pass.py` | S | cheap schema, graph and link checks on a head; notice only | R1-21, DEC-1052 | yes: after every record commit (§6) | yes | yes | needs a ticket | no |
| D10 | `verdict.py` | S (pinned copy in OP) | READY computed from a reviewer's verdict block | DEC-1010 (1) | yes: every review's READY (CHECKPOINT) | yes | yes | needs a ticket (none found) | no, E |
| D11 | `heavy_slot.sh` + `heavy_slots.conf` + `rebuild_slot.sh` | S (the last two pre-emergency) | machine-wide test and rebuild slots with CPU sets | DEC-979 D1, DEC-1011, DEC-1038 (4) | yes: A4's hook, `nightly.sh`, every test run (common brief) | yes | yes | ticket W2-20 exists (merged 11-09, live at the re-pin) | **yes**, machine load |
| D12 | `gpu_backstop.sh` | S | pauses a GPU job on budget, spill or partial load | DEC-1067, DEC-1068 (4) | yes, for GPU jobs: `log/gpu-backstop.log` 11-08 21:24 (M) | yes | yes | ticket W2-20 exists (trip-wire; the spill rule not checked, E) | yes, GPU safety |
| D13 | `rerank_service_slot_hold.py` | S | holds every reranker GPU slot while the shared service runs | DEC-1036 | yes: pid 8416 since 11-04; log 15:27 (M) | yes | yes | ticket W2-145 exists (merged, live at the re-pin) | yes, then retire |
| D14 | `rerank_reset_watch.sh` | S | restarts the shared reranker when its memory climbs | DEC-1067 (11-04 night) | no since 11-04 07:22 (M) | no | no | none (W2-112's cache emptying replaced it) | no, retire |
| D15 | `new_worktree.sh` + `seed_store.py` | S | a lead's worktree with its store seeded warm | DEC-1032 (iv) | yes: `log/seed.jsonl` 15:05 (M) | yes | yes | already in product (W2-122, `gov rebuild --seed`, merged D-1) | yes, done (close at the lift) |
| D16 | `refresh_integration_store.sh` + `rebuild_pinned.sh` + `store_refresh_daily.sh` | S (the last pre-emergency) | the designers' store, double-buffered, rebuilt with the pinned gov | DEC-963, DEC-1032 (iv), DEC-1087 (2)-(3) | yes: `store_refresh_daily.sh` pid 4003400 (M) | yes | yes | ticket W2-116 exists (pass 1 in product) | yes, W2-116 says so |
| D17 | `helper_watch.py` | S | inbox item when a helper dies, goes silent or vanishes | DEC-1112 (3) | yes: running; log 15:32 (M) | part | part | needs a ticket (W2-121 could hold it, E) | no |
| D18 | `inbox_wait_quiet.sh` | S | wakes the CTO on an inbox item; quiets repeats | DEC-1012 | yes: running (M) | no | no | none (W2-121's inbox, E) | no |
| D19 | `usage_log.sh` | S | records plan usage each 30 min; runs the brake check | DEC-1089 (3) | yes: running; `log/usage.txt` 15:26 (M) | no | no | none | no |
| D20 | `sentinel_check.sh` | S | tells the owner when the sentinel's login is down | the owner's order 11-04 (no id in the header) | yes: running; log 15:26 (M) | no | no | none | no, retire |
| D21 | `bare_watch.sh` | S | resets `core.bare` to false and logs who set it | 11-04 incident (DEC-1068 era; no id in the header) | yes: running; log 15:26 (M) | no | no | none (the test half is on D-10's list, DEC-1074 (8)) | no, retire after D-10 |
| D22 | `proc.sh`, `tree_busy.sh` | S | waits and busy checks by pid or folder, never by name | DEC-1073 (4), DEC-1012 | yes: the standing rule (§6, memory) | no | no | none (practice; a skill line at most, E) | no |
| D23 | `status_block.py` | S | the five-line block ending each owner report | DEC-948 | yes: `log/status-latest.txt` 15:32 (M) | no | no | none | no |
| D24 | `cto_checkpoint.sh`, `record_checks.sh`, `worktree_states.py` | S | the CTO's checkpoint; checks before record commits; worktree table | DEC-1038, DEC-868 (2), DEC-1087 (7) | checkpoint yes; record checks 11-09 (M); states 11-06 | no | no | none | no |
| D25 | `guard4_check.py` | S | the guard's two-minute case check | DEC-953 (2), DEC-1050 | yes: §7 start check | no | no | none (this repository's guard) | no |
| D26 | `guard_refusals.py` | S | harvests guard refusals from session transcripts | DEC-958, DEC-1097 | yes: `log/guard-refusals.jsonl` 09:34 (M) | no | no | none (W2-119 retired by DEC-1083 G-10) | no |
| D27 | `secrets_switch.py` | S | reads `secrets.yaml`'s scan switch without a product import | DEC-1045 | yes: by D5 and D11 | no | no | already in product (`ddcec657c`) | no |
| D28 | `queue_park.py` | S | parks the queue's approvals in an emergency stop | DEC-1037 (5) | no since 11-02, E | no | no | none | no, retire |
| D29 | measures: `lb_measure.py`, `server_log_scan.py`, `targets_report.py`, `rebuild_counts.py` | S | one-off load, server-log, target and rebuild counts | DEC-1028 (5e), DEC-1030 (3), DEC-1038 (4), DEC-1032 (iv) | no since 11-02/03, E (one-off) | no | no | none (targets in W2-121, E) | no, retire |
| D30 | `resources_sample_day.sh` | S | W2-20's `gov resources --sample` over a working day | DEC-1105 | not yet (after the re-pin) | no | no | already in product (W2-20) | no |
| D31 | ACT and ticket builders: `build_claude_copies_act.py`, `build_replay_calls.py`, `file_w2_149.py`, `hook_timing.py` | S | build one ACT's bundle, call set, ticket or timing | DEC-1109 (2), DEC-1112 (3), DEC-1108 (2), DEC-1101 | per ACT (COPIES-3 and OPERATOR-2 11-10, M) | no | no | none | no, retire (replay builder while the operator's replay is used) |
| D32 | `mem_sampler.sh` (pre-emergency, 10-29) | S | samples memory | — | yes: pid 8409 since 11-04 (M), no reader found | no | no | none | no, retire |
| D33 | 21 tests of the tools above (`test_*`) | S | test D1-D31's tools | as their tool | with their tool | — | — | follow their tool | — |
| D34 | 27 backups from the emergency (`*.pre-*`, `*.candidate*`, `*.applied-*`), plus 9 older | S | earlier versions kept for rollback | — | no | no | no | none | no, retire |

### E. Product changes (`src/gov`) from the emergency's work, by subject (all on integrate)

| # | tool / check / wiring | where it lives today | what it does (≤ 12 words) | decision | in use? (evidence) | kernel? | adopted repo? | route into the product | before EXAMIN's copy? |
|---|---|---|---|---|---|---|---|---|---|
| E1 | secrets switch; the scan's pools sized to the CPU set | `gov.secrets`, `gov.config` (`ddcec657c`, `c1257869b`) | scan on or off by configuration; bounded pools | DEC-1045 | yes: on the pin since re-pin window 2 | yes | yes | already in product | yes, done |
| E2 | the selection's record-only rule | `gov.close.select` (`83b7f85f4`, `194e3289c`) | record checks join a selection only when needed | DEC-1050 T-4 | yes: on the pin | yes | yes | already in product | yes, done |
| E3 | the machine-wide vector cache | `gov.retrieval` (`e99adb9a7`) | one cache keyed by model and text | DEC-1032, DEC-1039 | yes: since D-1 | yes | yes | already in product (W2-126) | yes, done (W2-27 dep) |
| E4 | no CPU embedding; the shared reranker empties its cache, cap 64 | `gov.retrieval` (`3a27107d3`, `7448ce364`, `8586d60f7`) | GPU-only embeddings; the reranker's memory bounded | DEC-1066, DEC-1068, DEC-1090 | W2-112 live (window 4); the cap at the re-pin | yes | yes | already in product (W2-32 S10, W2-112, W2-137) | yes, done |
| E5 | no private reranker beside the shared service | `gov.retrieval` (`86f1af6e5`, `1be3e47de`) | the service holds every reranker GPU slot | DEC-1046 (1), DEC-1048 (5) | at the re-pin | yes | yes | already in product (W2-145) | yes, at the re-pin |
| E6 | the machine-wide resource gate | `gov.resources`, `gov.launch.gate` (`4be0bb81a` … `057926aa3`) | slots, CPU sets, trip-wire, launch gate, re-measure | DEC-1088 (5)(b), DEC-1105 | at the re-pin | yes | yes | already in product (W2-20) | **yes**, at the re-pin |
| E7 | `gov launch` for every worker; the role template at launch | `gov.launch` (`8c399ea3e` …, `e57be0ee8`) | cleaned env, temp folders, process group, template | DEC-1112 (3), DEC-1114 | at the re-pin | yes | yes | already in product (W2-56, W2-153) | **yes**, at the re-pin |
| E8 | `gov rebuild --integration`; GOV_STORE in launched sessions | `gov.rebuild.integration` (`ca757c610`, `1f33a6888`) | the designers' double-buffered store | DEC-1087 (3) | yes: A4's hook runs it (M) | yes | yes | already in product (W2-116 pass 1) | yes, done |
| E9 | `gov plan` (the batches, cycles broken inside components) | `gov.plan` (`69aa361ab`, `fd4b2763f`) | dependency map, launch batches, ready list | DEC-1088 | at the re-pin | yes | yes | already in product (W2-136, W2-147) | yes, at the re-pin |
| E10 | the guard: an engineer's search into its own acceptance folder | `gov.guard` (`a3dbf84fc`, `7716610e2`) | refuses such a search unless it excludes the folder | DEC-1093 (2) | at the re-pin with the hook ACT | yes | yes | already in product (W2-141) | no, not a W2-27 dep |
| E11 | search filtered by role; D-5 and D-6 work (`gov brief`, `gov links`, the shared utilities, memory's import closure) | `gov.util`, `gov.brief`, `gov.links` (W2-13 S5, W2-152, W2-129, W2-150, D-6 part 1) | refactoring and templates under DEC-1052's plan | DEC-1052, DEC-1109 (2) | part live, part at the re-pin | yes | yes | already in product | W2-128 and its halves are W2-27 deps |

## 2. Must land before EXAMIN's copy

Each is on W2-27's `deps:` closure, or a decision says "before EXAMIN" (M: the ticket or the register).

1. **The dispatcher and the Load Balancer (C1, A1) → W2-121.** DEC-1008: the Gov OS is not adopted on EXAMIN without
   a dispatcher (K9). W2-121 is **open and not started**. P-LB-PRODUCT-1 (DEC-1048 (3)) was never brought back, and
   W2-121 carries no balancer line. This is the largest item with no work yet.
2. **The scoped close and selection (D5, D7, D4, D6, A6) → W2-115.** It must land before W2-27 (its own Order). It is
   **open and not started**. DEC-953 wants `gov close` proved on W2-81 and on EXAMIN's copy. The queue part (C2, D8)
   can wait, because a LITE copy needs no queue (W2-117).
3. **The resource gate (D11, D12, A10, E6) → W2-20.** It is merged and goes live at the re-pin. The copy shares this
   machine's CPUs and GPU, and the 11-02 overload came from unbounded runs. When it is live, the wrapper A10 retires
   (DND row 20).
4. **The launch: model and effort by tier, the template, the brake (D1, D2, E7) → W2-56 and W2-153 (merged, live at
   the re-pin), W2-60a (in progress), W2-60b (open).** DEC-1119 (2) says the tiers land before EXAMIN's copy. **No
   ticket holds the runaway brake (D2), which needs a ticket or a W2-60b line.**
5. **The product's guard reads Bash writes (B2) → W2-42a (in progress).** DEC-1028 (4) says before EXAMIN's copy.
   EXAMIN's agents meet the kernel guard, not this repository's hook.
6. **GPU safety for the reranker (A11, D13, E5) → W2-145 (merged, live at the re-pin).** When it is live, D13 retires.
   A11's installed module needs checking first (see §4).
7. **The designers' store (D16, A4, E8) → W2-116.** Its ticket says before W2-27. Pass 1 is in the product. The
   after-landing trigger lives only in this machine's git hook (E).

Already done, kept here for completeness: E1-E4, E8 and D15 (W2-122).

## 3. Retire with the emergency

These exist only for the emergency. Each retires when its condition is met, and the condition is in brackets.

- The interim GPU and load guards: A10, the query wrapper (W2-20 live); D13, the slot hold (W2-145 live); D14,
  `rerank_reset_watch.sh` (unused since 11-04); D12, `gpu_backstop.sh`, once W2-20's trip-wire covers a spill (E).
- The emergency's watches: D20 `sentinel_check.sh`; D21 `bare_watch.sh` (after D-10 fixes `core.bare`'s test half);
  D32 `mem_sampler.sh` (no reader found); D19 `usage_log.sh` and D26 `guard_refusals.py`, if the owner ends the
  recording.
- One-off measures and builders: D29 (four measures), D31 (four builders), D28 `queue_park.py`, D30 after the sample
  day.
- The stop state: A3's commented cron lines (restored or deleted at the lift); C5's DEC-1049 hold.
- The 27 emergency backups and 9 older ones (D34); `land.candidate.applied-2112.py` is already named a dead copy (O-8).
- After W2-115 lands: D5, D6, D7, D8, D4, C2 and `load_sensitive.txt` move onto the product, as W2-117 says ("W2-97's
  tool is retired").

## 4. Gaps: in use, with no committed copy (the highest risk)

The scratch tools are safe here: every one of the 95 files changed since 11-02 is byte-identical on `record/w2` (M).
The operator install equals OP. The crontab equals its committed after-copy. The git hook equals a committed
candidate. The query wrapper equals S. The real gaps are these:

1. **`.claude/settings.local.json`** (A7-A9: the PermissionRequest hook and both Stop hooks). It is untracked, and no
   byte copy is committed. Only its sha256 (`d715292711a2…`) is in commit `115be1912`'s subject; older versions are in
   `record/w2` `drafts/act-permissions-*`. A lost file silently drops the idle check and the waiter check.
2. **The reranker venv's `gov_reranker_gpu_slot.py`** (A11). The installed module is the `81b7a7397` version (M, blob
   match). Integrate's copy is the later `c5d2ad004` version (the Load Balancer's change). So the live module is not
   the committed head; its source exists only in history. The cause is not determined: an install ACT not re-run, or
   a deliberate hold.
3. **A structural gap: committed tools depend on scratch-only paths.** On integrate, `merge_queue.py` calls S
   `rebuild_slot.sh` and `select_tests.py`; `nightly.sh` calls S `heavy_slot.sh`; `dispatcher.py` reads S
   `heavy_slots.conf`; the git hook calls S `heavy_slot.sh` and `landing_select.sh`. A clean clone of integrate does
   not have them, because `record/w2` holds them under another path. This is why W2-20 and W2-115 matter for an
   adopted repository: today that machinery is not in the product at all.
4. **Session-only wiring:** the CronCreate digests (A14) and the background watchers (D17-D21) live only in the
   running session. Each new session re-arms them from START-NEXT-SESSION §6, which is committed. This is low risk by
   design.

## 5. Counts

- **Table rows: 71** (A 14, B 3, C 9, D 34, E 11). Grouped rows hold more items.
- **Scratch:** 95 files changed since 11-02: **47 tools, 21 tests, 27 backups** (M). There are 36 backups in all. All
  95 are byte-identical on `record/w2`; **0 are on integrate**.
- **Committed files changed or added since 11-01 (M, git log):** 11 tool files in O (`dispatcher.py`, `balancer.py`,
  `launch_now.sh`, `loop.sh`, `run_tick.sh`, `merge_queue.py`, `deadman.py`, `gov_reranker_gpu_slot.py`,
  `stop_waiter_check.py`, `stop_idle_check.py`, `indep_launch.py`), plus 10 schemas. Also: 13 files in OP, 3 hooks in H,
  2 nightly scripts with their test, and `sync_context.py`.
- **Routes over rows A-D (60 rows):** already in product 5; a ticket exists 24 (W2-20, 42a, 56, 60a, 60b, 115, 116,
  121, 145, 148, 149, 154); needs a ticket 7 rows (A8, A9, C3, D3, D9, D10, D17), plus D2's brake, so 8 items; none 23;
  1 not applicable (D33, the tests).
- **Before EXAMIN's copy:** 18 rows in A-D answer yes (A1, A4, A6, A10, A11, B2, C1, D1, D2, D4-D7, D11-D13, D15,
  D16), and 9 in E (E1-E9; E1-E4 and E8 are done). §2 sorts them into 7 groups, of which 2 are not started (W2-121,
  W2-115).
- **Retire with the emergency:** 16 rows or groups now, plus 6 rows after W2-115 lands (§3).
- **Gaps:** 2 files plus 1 structural gap (§4).

## 6. What I could not determine

- Whether `land.py` and `merge_queue.py` ran after 11-03. I found no log after 11-02 23:07, but landings may have run
  through other logs (E).
- Why the installed reranker slot module lags integrate's copy (§4.2).
- Whether W2-116, W2-20 and W2-121 already hold lines for the after-landing trigger, the GPU spill rule and the helper
  watch. I read their titles and why-lines only, not every KPI.
- Whether the operator agent (C7-C9) and `indep_launch.py` (C4) are wanted in the product. No decision names a route,
  so I left both at their tickets.
- Who reads `mem_sampler.sh`'s output and `log/lead-mem.jsonl` (both live).
- The "in use" answers for tools started by hand rest on the logs' times and START-NEXT-SESSION §6. I did not trace
  each run.
