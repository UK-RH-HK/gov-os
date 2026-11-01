
## 15:40 — for the 20:00 brief
- Latency trace (log/capacity/latency-trace.txt): the 11 hook-latency cases (W1-02 p95, W1-05 live hooks, W2-57
  designer read; all "p95 under 100 ms") with W2-106's merge: red 8, 0, 1 of 11 over 3 rounds; without it: 0, 0, 5.
  Run time 34-152 s at load 15-30. Load, not W2-106. The batch of four's refusal (15:19) was the close tool's single
  trace; it now traces 3 rounds each way interleaved (6 if mixed); red without in any round = not the change's.
- Batch of six re-closing from ~15:35: W2-106 W2-84 W2-76 W2-49 W2-16 W2-108 (log/close-six-20261031.out).
- P-LATENCY-1 (owner, DEC-906): the 11 cases are load-sensitive, owned by no ticket (not W2-90b). Options:
  (a) a fresh test designer revises them to measure the hook's own time (CPU time of the hook process, or a quiet
      reference beside each run) at the same 100 ms, lowering nothing; (b) run them only in the nightly
      (route), keeping them red-able there; (c) leave as is and name them each close (an accepted red: ruled out by
      DEC-968). Recommend (a), filed after W2-90b in the same files' order (W1-05 shared).

## 16:30 — DEC-974 items for the brief
### Memory's state
- Measured (visible half, 20 q): W2-61 baseline hit@5 8/20, full evidence 12/20, bundle 14/20; after W2-87 (closed)
  hit@5 11/20 (55 %), full evidence 11/20 (55 %), bundle 15/20. Target 95 % (floor 85 %), full evidence 99 %.
- Closed: W2-61 (the measure), W2-87 (authority order + register fix), W2-54 (context check). Merged, closing in the
  batch of six: W2-108 (freshness once per process). Running: W2-81 (proving ground: claimed; check its lead state).
- Queued: W2-86 (claimed 16:2x, worktree at 8d513849, second in the queue after W2-105; re-measure in its own run).
- Not started: W2-61h (28 new questions; after W2-84's close), W2-91 (after W2-86), W2-92 (graph routes), W2-13
  (BM25), W2-93 (W2-81's hidden half), W2-94 (EXAMIN's set), W2-88 (any repository), W2-04, W2-55, W2-14, W2-15a,
  W2-15b, W2-32.
- Next measure: W2-86's run (visible half) when its lead runs, about 5-6 h after it starts; the 48-question measure
  (>= 21 of 24 on the hidden half) after W2-61h.
### Tickets added since approval (24): owner 23, CTO under delegation 1 (W2-90b, DEC-965/DEC-970, 13:15 today)
- DEC-954 (owner): W2-86, W2-88. DEC-957 (owner): W2-90, W2-91, W2-92, W2-93, W2-94. DEC-959 (owner): W2-95..W2-104.
  DEC-966 (owner): W2-105, W2-106, W2-107 (W2-107's start DEC-967). DEC-969 (owner): W2-108. DEC-971 (owner): W2-109,
  W2-110. W2-90b: CTO, delegated (DEC-965 item 3 resume + DEC-970), now a P1 under DEC-974: ask for retro approval.
### P-TOOLS-LANE-1 (DEC-974 item 3)
- Scope: scratch tools (close_build, select_tests, gate_check, verify_lock, watchers, samplers, brief builders) and the
  nightly folder (governance/project/orchestration/nightly/).
- Today: nightly folder = reviewed commit + test_nightly.sh for every change; scratch tools: no tests, no review,
  changes noted only in the checkpoint; none is a WBS ticket (W2-00 carries them) but they cost lead-like time.
- Proposed: (1) every tool has its own test file beside it (close_build's attribution rule first; gate_check;
  select_tests), run before the tool is used; (2) an independent review only if the change could fail open (let a red
  or a refusal through, widen a gate) or lose work (kill, delete, lock, overwrite); else none, the nightly folder
  included; (3) a "Tools changed" section in the daily document: tool, change, test, reviewed or why not; (4) never a
  WBS ticket; commits Task: W2-00. Changes: fewer reviews on the nightly (e.g. a time or message change), more tests on
  scratch tools (stricter), and the WBS count shows only product tickets.
- Today's example: the close's attribution change can fail open -> reviewed (code-reviewer, 16:30).
- Tools changed today (for the daily document's section, if P-TOOLS-LANE-1 is approved): close_build.py red
  attribution: 3+3 interleaved rounds; absent-without = the change's; penv for traced runs; timeouts red; record order;
  one shared trace_node(); tests tools/test_close_build.py 11 pass; reviewed twice (code-reviewer): 4 findings fixed,
  then 1 (tests on a copy) fixed; residual named: a red caused by the revert itself (exit 1 without) lands in unowned.
- W2-95 lesson (cost of overload): load gate ~60 min + rebuild lock ~15 + rebuild 20 in one run; W2-67: 62 min load wait.
- DEC-975: the bigger-machine sizing waits for the re-measure after W2-107 merges (gitleaks ~8 of 20 threads, 54
  processes, per the operator's check ~17:00). The 20:00 brief gives today's figures as "before W2-107".
- W2-96 (17:26): load gate held its single-process steps 90 min (15:53-17:24) plus ~35 min earlier; option (b) exempt
  single-process runs (one gov accept, a red check) from the lead-side load wait -> an option in CAPACITY-1.

## 18:30 — the day's figures (14:17-18:26, 231 one-minute samples; before W2-107)
- Machine: busy 16.2 of 20 cores on average (idle 1.9, iowait 0.04); load avg 44, max 89; memory used avg 11.4 GiB,
  max 18.7 of 23.5.
- CPU by kind (scaled to the machine's busy): test runs 8.2 cores (51 %), rebuilds 2.5 (16 %), embedding 2.3 (14 %),
  other 2.0 (12 %), Claude sessions 0.7 (4.5 %), rerankers 0.2 (1 %), gitleaks seen as its own process 0.1 (1 %).
  CAVEAT: gitleaks runs as short-lived processes (one per file and rule set) and its time is reaped into the parent:
  most of "rebuilds" (W2-76: secrets 548-696 s of 735 s) and part of "test runs" (fixture rebuilds) IS gitleaks. The
  operator's snapshot (~8 of 20 threads, 54 gitleaks processes at once) agrees. W2-107's counts line + the re-measure
  will separate it.
- Memory (RSS by kind): rerankers 3.4 GiB, test runs 2.8, other 2.5, embedding 1.3, Claude sessions 1.3, gitleaks 0.7.
- Overload cost (the same tests/unit -n 4, 2,976 tests, every 30 min): 66-94 s at load ~20, 177-196 s at 48-55,
  211-252 s at 57-76: 2.7-3.8x slower. More at once does not finish more: at load 75 the same work takes ~3.5x as long.
- W2-107 KPI 7 measured 18:25-18:30 (worktree a4aa7d75, load 13-16): rebuild 1 (after the merge, cache warm from the
  lead's runs) secrets 12.3 s, content 99 scanned / 2,672 remembered, path 38 / 2,634, total 133 s; rebuild 2
  (unchanged) secrets 5.1 s, content 5 scanned (findings, rescanned by design) / 2,672, path 0 / 2,672, total 36 s.
  Before: secrets 548-696 s of a 735 s rebuild. -> ~98-99 % of the secrets stage gone; a rebuild ~5-20x faster.
- Tools changed 2026-10-31 evening (daily document, DEC-979 D3): close_build.py culprit search (DEC-979 item 3):
  explained_without/red_alone/assign_culprits/merge_is_own; 26 tests; reviewed three times (fail-open paths fixed:
  absent-by-collection proved with the ticket alone; non-isolable merges and skipped candidates refuse; a candidate
  that edited the failing test must be proven alone). Known residual: two tickets that each break a test one of them
  added: only the adder goes back; the other's break shows when the adder returns.
- Tools changed 2026-11-01 00:00-00:50 (daily document, DEC-979 D3): heavy_slot.sh (new; flock -o so daemons never
  keep a slot; tests H1-H6), verify_lock.sh takes a slot, close_build's parallel run takes a slot; close_build's trace
  falls back to the head before the batch when a merge cannot be reverted (W2-76's after W2-107), and clears a red
  both ways only when it fails with the same exception type (reviewed; 28 tests). Nightly folder: DEC-984 (reviewed x2).
