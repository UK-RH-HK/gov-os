# D10-RUNTIME: what D-10's first full run costs in time (research helper, 2026-11-10; head 6cc09c7ea; read-only, collect-only)

**Headline (1)** STOP FIRST: `pytest tests` on this head stops at collection (5 files, "import file mismatch": same basename in two
folders, no `__init__.py`): `tests/unit/resources/test_w2_20_{gate,launch,query_start,slots}.py` vs `tests/acceptance/W2-20/`, and
`tests/unit/operator/test_w2_148_trial.py` vs `tests/acceptance/W2-148/`. Both are new since 11-09. Reproduced (collect-only, whole tree, gate).
The nightly's parallel phase would end in ~25 s with 0 cases run; fix (rename 5 files) before run 1. If run 1 has started, look for `Interrupted: 5 errors`.
**(2)** Run 1 after that fix, healthy machine: **about 3,200-7,200 s (0.9-2.0 h), central 4,500-5,500 s (1.3-1.5 h)**; `nightly_estimate` 11,221 s is stale (it prices pre-cut cases and the 11-02 failure branch).
**(3)** Biggest healthy parts are three near-equal thirds (setup, parallel, serial). The biggest RISK is the real-model entries: on 11-02 serial + re-runs alone = 12,315 of 19,448 s (63%). Failure branch: 13,800-16,600 s.
**(4)** Best no-loss saving: a real-model health probe before the serial phase + no re-run of the same fixture timeouts (up to ~10,000 s in the failure branch, 0 healthy); lanes for the serial phase ~600-700 s; more workers <=150 s. None is worth a restart; the collection fix is. Apply the probe and lanes to run 2 (they change `nightly.sh`, a control path: ACT).

## Components of run 1 (the default selection: 9,649 cases collected; D-4's cut was 5,628)
| component | cases | seconds | M/E | how |
|---|---:|---:|:-:|---|
| setup: clone + rebuild (+ gate/slot wait kept out) | - | 1,000-2,400 | M | history setup_s: 942, 1,509, 1,016 quiet; 3,973 and 2,381 loaded (11-01, 11-02). Spread = the machine's load and the rebuild lock (`flock /tmp/gov-os-rebuild.lock`, inside setup); load avg now 4 -> low half. Gate/slot wait 0-1,154 s (M), outside setup, adds to wall |
| parallel, D-4's kept cases | 5,595 | sum 5,260 | E | pooled medians of 10-30 full close runs; 88.6% of ids matched (rest at file/all median) |
| parallel, added since D-4 (6008a41f): 242 new test files | 3,953 | sum 1,500-2,400 | E | 47.6% matched (recent scoped runs); unmatched priced at all-median (0.19 s) to matched-mean (0.6 s) |
| **parallel phase wall** | 9,548 | **960-1,450** | E | sum 6,800-7,700 x load factor 1.0-1.3 (11-02 per-case time was 1.33x 10-30) / 7.05 effective workers (M, lowest of last three runs; 7.05-8.5 over five) |
| serial phase (one process) | 136 | 1,100-1,500 | M/E | M: 1,109-1,262 s on 10-29..31 (longest 123-177 s). E: 1,426 s = today's 136 ids priced from 85 close/lead serial XMLs (98.5% matched; live-session cases perhaps under-measured, 108 s) |
| serial, failure branch (real models down) | 136 | 5,349 | M | 11-02: 8 real-model errors; longest case 2,313 s |
| reds re-run alone (`nightly_alone.py`, cap 1,800 s each, no total cap) | 20-40 | 100-900 healthy | E | 11-02 actual: 6,457 s (= 19,448 - 2,381 - 898 - 3,854 - 5,858), 5,243 s of it the 8 real-model cases (130-1,044 s each) |
| not in run 1: `lifted` (+8,596 cases), `breadth` (+5,870) | 14,466 | 0 | M | `nightly.sh` has no `--optin`; D4-LIST decision 2: lifted = one report-only run in D-10's window |

Slots: DEC-979 gives 3 x 6 = 18 workers on 18 of 20 CPUs (`heavy_slots.conf`; nightly holds all 3, `--held`; 11-02 held 2 of 3 = 12 workers and got 7.58 effective, no worse than 18 at 7.05); the serial phase gets all held CPUs for one process.
Serial list today (136 cases): real-model 14 (758 s; W2-54 `green_here` 363 + `time_limit` 244), daemon 65 (496), live-session 32 (108), latency 23 (50), race 2 (14).
Longest serial (s, pooled): W2-54 green_here 363; W2-54 time_limit 244; W1-19 hit@5 63; W1-21 family check 55; W1-16 renamed symbol [a-dev] 54, [b-dev] 54; W1-20 repeated runs 34; W1-16 daemon-dir env 29; W1-16 home 29; W1-49 forced compaction 27.
Needs serial? Latency/race (25 cases, 64 s): yes (p95 bounds). The 2,313 s case: no identity in history (only `longest`); by the 11-02 run it was one of W1-19/W1-21's real-model fixtures failing on an embedder timeout; both files are still listed (lines 105-107 of `serial-only.txt`).

## Options (saving in seconds of run wall; E unless stated)
| option | saving | coverage cost | effort | apply |
|---|---:|---|---|---|
| (a) more workers: CPUs are 20, 18 used, 12 of the 20 shared with the embedders; 12 vs 18 workers gave 7.58 vs 7.05 (M) | <= 150 | none | slot conf only | not worth it |
| (b) lifted only in run 2: already so (not in run 1). Its cost: lifted 9,635 case-s = ~1,370 s wall, breadth 5,222 = ~740 s, both ~2,100 s (35 min) | 0 (to run 1) | none | needs `NIGHTLY_PYTEST_EXTRA=--optin=lifted` and the plugin fix, else the serial phase stops (exit 4, the 39 listed cases) | run 2 |
| (c) serial lanes: latency/race alone (64 s); daemon (496 s) in 2-3 lanes if each gets its own daemon dir; real-model + live-session (866 s) in a lane beside the daemon lane (they wait on the embedder and the API, not on each other); W2-54 `green_here` has no time bound and could go to the parallel phase | 600-700 | none if lanes share nothing; unproven for daemon (needs one trial) | `nightly.sh` change (ACT) + review | run 2 |
| (d1) embedder health probe before the real-model entries; report "not run: embedder down" (red) instead of 8 timeouts, and do not re-run alone an error that is the same timeout | 0 healthy; up to ~10,000 failure branch | none (the cases still count red) | small | run 2 |
| (d2) cap `nightly_alone.py` in total (now 1,800 s per red, no sum) | up to ~5,000 failure branch | a red left un-re-run, named | small | run 2 |
| (e) rename the 5 clashing files (not a saving: without it run 1 yields no parallel result) | n/a | none | 5 renames | **before run 1** |

## Not measured
- No full run since the cut: parallel durations are 10-30 close runs (pre-cut) priced onto today's ids; 28% of parallel ids unmatched (new tests); the 5 clashing files (~110 cases) are in neither count.
- The nightly's JUnit for 11-02 and earlier is gone; the 2,313 s case's name and the per-case serial times of 11-02 are inferred, not read.
- Whether the embedders are healthy now (not touched, DEC-1038); real-model and live-session seconds when healthy; daemon-lane safety; the 35-case gap between the plugin's split (9,548 + 136) and the plain count (9,649).
- Scratch: collect lists and scripts in the session scratchpad; no test was run.
