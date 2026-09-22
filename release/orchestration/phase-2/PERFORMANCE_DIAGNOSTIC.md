# Certification performance diagnostic — P2-PERF-0001

**Run id** P2-PERF-0001 · **branch** `phase2/perf-diag` · **base** `c34c439` (the 244-test tree)
**Date** 2026-09-22 · **Role** measurement and analysis only; no product, test, policy or `framework/` change was made
**Audience** an engineer acting on this after Phase 2 closes, who was not present for any of it

---

## 0. How to read this report

Every number carries one of these labels. Nothing here is an estimate presented as a finding.

| Label | Meaning |
|---|---|
| **MEASURED-CLEAN** | I ran it; 1-minute load average below ~3 for the whole measurement. Load stated. |
| **MEASURED-CONTAMINATED** | I ran it, but under competing CPU load. The load is stated with the number. Never averaged with clean data. |
| **INFERRED-FROM-RECORD** | Taken from a durable record already in the repository, cited by path. |
| **NOT DETERMINED** | I could not establish it. What it would take is stated. |

Two methodological rules I applied, because they change which contaminated numbers are still usable:

1. **CPU time is far more load-robust than wall time.** I instrumented with `os.wait4`, which returns user+sys CPU for the test binary **and every `gov`/`git` subprocess it reaped**. Contention inflates *wall clock*; it does not inflate *CPU consumed*. So ratios (sys% of CPU, cpu/wall) and CPU totals survive load; wall times do not.
2. **A contaminated measurement used as an upper bound to *reject* a hypothesis is sound**, because contention can only inflate it. Where I use a number this way I say so.

**Why some numbers here are contaminated.** A bounded repair was running concurrently in `wt/p2-r3-boundary`, and the orchestrator correctly stopped my per-family sweep partway (13 of 38 families) because it risked contaminating the repair's acceptance-relevant results. Those results take priority; this diagnostic gates nothing. The sections needing a quiet machine are marked **AWAITING CLEAN MEASUREMENT**.

---

## 1. The headline

**The ~2.5 hours is not a property of the certification suite. It is the cost of running it with `--test-threads=1`. The same suite, one-at-a-time on the machine with libtest's default 20-thread parallelism, is about 20 minutes.**

Normalising every durable suite record by test count (the suite grew from 189 to 244 tests over Phase 2) separates the records into four populations that differ by *concurrency conditions*, not by the suite:

| Population | s/test | Extrapolated to 244 tests | Records |
|---|---|---|---|
| Orchestrator reproductions labelled **"serialised"** | 4.30, 4.88, 5.11, 5.39 | **~1,201 s ≈ 20 min** | P2-AR-0041, 0064, 0054, 0067 |
| Worker runs sharing the machine with other agents | 8.53 – 10.35 | ~2,080 – 2,525 s | P2-AR-0072, 0066, 0067b, 0064b, 0065b |
| Independent reviewer, mode unrecorded — **decoded in §3.1 as ~3 test streams** | 11.24 | 2,742 s ≈ 46 min | P2-AR-0075 |
| The load→160 era | 23.68, 23.72 | ~5,780 s | P2-AR-0046, 0049 |
| **The one run with `--test-threads=1`** | **35.09** | **8,561 s = 2.38 h** | **P2-AR-0069** |

**INFERRED-FROM-RECORD**, `release/orchestration/phase-2/AGENT_RUNS/` — full table in §3.

Two consequences follow, and both matter more than any micro-optimisation in this report:

**(a) "Serialised" in this orchestration's vocabulary does not mean `--test-threads=1`.** Proof by contradiction: if it did, those four orchestrator reproductions would be ~35 s/test. They are 4.30–5.39 s/test — **7× faster**. "Serialised" therefore means *one suite at a time on the machine*, with default parallelism intact. The orchestrator's own worker packets corroborate the scale, telling workers that `cert_all` "takes about 25 minutes" (`release/orchestration/phase-2/packets/P2-AR-0060-wsF.json`).

**(b) 2.5 h ≈ 9,000 s, and nothing in the entire record is within 40 minutes of it except the single-threaded run** (8,035 s at 229 tests = 2.23 h; scaled to 244 tests, 8,561 s = 2.38 h). The `~2.5 h` claim in `release/orchestration/phase-2/HANDOFFS/P2-HO-0052-repair-3-bounded-final.md:182` is consistent with that mode, or with a round containing two full suite runs (P2-AR-0069's round did run two: a pre-fix `228/1` and the official post-fix `229/0`).

**The `--test-threads=1` habit is a category error with a traceable origin.** The requirement is real, but it belongs to the **independent verifiers' held-out harnesses**, which are separate crates under `release/verification/…` and genuinely do call `std::env::set_var("XDG_STATE_HOME")` and `set_var("HOME")` in-process (`release/verification/4.1.6-r1-2/evidence/heldout-tests/mint.rs:138-141`; the requirement is stated in that directory's `REPRODUCTION.md`). The **certification suite does none of this** — see §6. Carrying their constraint across to the certification suite costs roughly two hours per run and buys nothing.

**The second headline, independent of the first:** there is **no such thing as a warm no-op build in this repository**. Every single `cargo build` or `cargo test` recompiles `gov-runtime` and `gov-cli`. Cargo names the cause itself (§7).

---

## 2. Machine context

**MEASURED-CLEAN.** Recorded at 11:16 UTC, load `0.29 0.33 0.35`.

| Property | Value |
|---|---|
| CPU | 12th Gen Intel Core i7-12700F, **20 logical cores** |
| Memory | 16,288,940 kB total (~15.5 GiB) |
| Kernel | `6.6.87.2-microsoft-standard-WSL2` — **WSL2**, as stated in the brief |
| Worktree filesystem | `/dev/sdd`, **ext4**, mounted `/`, inside the WSL2 VM |
| `/tmp` (all test scratch) | same `/dev/sdd` ext4 filesystem |
| Disk | 1,007 GB total, **79% used, 201–221 GB available** |
| tmpfs available | `/dev/shm` and `/mnt/wsl`, 7.8 GB each |
| Toolchain | `rustc 1.98.1 (48a229cea 2026-09-01)`, `cargo 1.98.1`. **Stable only — no nightly installed** |
| `CARGO_TARGET_DIR` | **unset**; no `.cargo/config.toml` in the worktree and none at `$HOME/.cargo/config.toml` |
| Git worktrees | **44** on this repository |

**Important negative result on the WSL2 hypothesis:** the worktree and `/tmp` are on **ext4 inside the VM**, not on the 9p `drvfs` mount (`/mnt/c`). The slow-WSL2-filesystem failure mode does not apply here, and §5 measures it rather than assuming it.

---

## 3. Every durable suite duration in the repository

**INFERRED-FROM-RECORD.** Sources are `release/orchestration/phase-2/AGENT_RUNS/*.{run,report}.yaml` and `PHASE_LEDGER.md`. Sorted by s/test, which normalises for suite growth.

| Run | Tests | Wall | s/test | Mode / conditions as recorded |
|---|---|---|---|---|
| P2-AR-0041 | 189/0 | 813 s | 4.30 | orchestrator reproduction at `e4cb662` |
| P2-AR-0064 | 211/0 | 1,029 s | 4.88 | orchestrator, **"serialised"** |
| P2-AR-0054 | 207/0 | 1,058 s | 5.11 | orchestrator reproduction at merge `0bad524` |
| P2-AR-0067 | 225/0 | 1,213 s | 5.39 | orchestrator, **"serialised"** |
| P2-AR-0065 | 210/0 | 1,309 s | 6.23 | worker, before its edit, unmodified tree |
| P2-AR-0072 | 231/0 | 1,970 s | 8.53 | worker, **"default parallelism"** (stated) — and it was green, 231/0 |
| P2-AR-0066 | 216/0 | 1,857 s | 8.60 | worker, full suite single run |
| P2-AR-0067 | 225/0 | 2,180 s | 9.69 | worker |
| P2-AR-0064 | 211/0 | 2,104 s | 9.97 | worker, single run |
| P2-AR-0065 | 210/0 | 2,173 s | 10.35 | worker, **stated concurrent contention from another worktree's full suite** |
| P2-AR-0075 | 244/0 | 2,742 s | 11.24 | independent reviewer, clean, **mode not stated** |
| P2-AR-0051 | 207/0 | 2,598 s | 12.55 | verifier |
| P2-AR-0049 | 207/0 | 4,901 s | 23.68 | verifier, high-load era |
| P2-AR-0046 | 207/0 | 4,910 s | 23.72 | verifier, **stated machine load >160** |
| **P2-AR-0069** | **229/0** | **8,035 s** | **35.09** | worker, **`--test-threads=1` (single-threaded)** |

Also recorded, for the contention question only: five concurrent full suites at load ~160 returned 1,875 / 1,062 / 1,523 / 1,785 / 1,038 s, **two with spurious failures** (203/7 and 206/3) — `V8_3_EVIDENCE_PACKAGE.md:256`. §3.2 shows these five figures are **not physically consistent** with the suite's measured CPU cost if the five runs actually overlapped, so they should not be used for anything quantitative.

**Surprise worth flagging.** P2-AR-0069 gives no stated reason for choosing `--test-threads=1`; it appears to have been a worker's own defensive choice after the contention episode, not a documented policy. One undocumented flag choice is the largest single performance fact in this orchestration's history.

### 3.1 Reconciling P2-AR-0075's 2,742 s — it was about three test streams' worth of the machine

The 2,742 s figure (11.24 s/test) sits between the "serialised" band and the single-threaded run, and it is the number quoted to the repair worker and in the owner-facing package. It is worth explaining rather than leaving as an outlier. **Its mode is genuinely unrecorded** — `P2-AR-0075.run.yaml` names no command line, no thread count and no load; there is no accompanying `.report.yaml`. That absence is itself an instance of the requirement `V8_3_EVIDENCE_PACKAGE.md` §5.3 articulates: *"a test result without its concurrency conditions is unfalsifiable."*

But it can be decoded, because **total CPU work is a property of the tree, not of the schedule**. Define `W` = total CPU seconds the suite consumes and `P = W / wall` = effective parallelism achieved.

**Calibrating `W` two independent ways, which agree:**
- From the single-threaded record: one test stream, with each `gov` using its clamped ≤4 workers. The measured `cpu/wall` for exactly that shape is **1.845** (clean brownfield alone) to **1.98** (sweep aggregate). So `W(229 tests)` = 8,035 × (1.845…1.98) = **14,825 – 15,909 s CPU**.
- From my sweep, measured directly (a CPU total, hence load-robust): `W(133 heaviest tests)` = **11,722.7 s**, i.e. 88.1 s CPU/test. For the two `W` figures above to hold, the remaining 111 lighter tests must hold 3,102–4,187 s, i.e. **27.9–37.7 s CPU/test** against 88.1 for the heaviest third. Given families were ordered heaviest-first, that is exactly the right shape.

Take **`W ≈ 15,800 s CPU` (range ~15,000–16,500)** for the 244-test tree.

| Recorded run | Wall (at 244 tests) | `P` = effective cores | % of 20 |
|---|---|---|---|
| Single-threaded (P2-AR-0069, scaled) | 8,561 s | **1.85** | 9% |
| Orchestrator "serialised" band (mean 4.92 s/test) | 1,200 s | **13.2** | 66% |
| **P2-AR-0075** | **2,742 s** | **5.76** | **29%** |
| 20-core theoretical ceiling | 790 s | 20.0 | 100% |

The single-threaded row is the **validator**: the model independently reproduces the 1.845–1.98 `cpu/wall` I measured for a single serial test stream, to within 2%. The model is therefore trustworthy enough to read the other rows.

**So P2-AR-0075 achieved 5.76 effective cores — almost exactly three test streams** (3 streams × 1.85 = 5.6 cores, predicting 2,847 s against 2,742 s observed, a 4% miss). Two mechanisms produce that, and the record cannot distinguish them:

- **(a) A reduced `--test-threads`.** `--test-threads=3` predicts 2,847 s; `--test-threads=4` predicts 2,135 s, which reaches 2,742 s under ~28% contention. **`--test-threads=4` is the value hard-coded in `scripts/collect_evidence.sh:22`** — the most likely thing a reviewer reproducing checks would copy.
- **(b) A machine shared roughly three ways.** On this same tree and in the same window, P2-AR-0074 ran the full suite **twice** ("first 241 passed / 2 failed … then 244 passed / 0 failed") and the orchestrator ran its own serialised reproduction. Whether any of these overlapped P2-AR-0075 is not recorded.

**And the third hypothesis — that `c34c439` genuinely costs more per test — is largely excluded.** Per-test cost *was* rising as the suite grew; a linear fit on the four "serialised" points (189→4.30, 207→5.11, 211→4.88, 225→5.39) gives `s/test = 0.0295 × tests − 1.21`, predicting **5.98 s/test = 1,459 s at 244 tests** (P = 10.8 cores). So growth explains a rise from ~1,200 s to **~1,460 s** — about 20% of the gap. It does not explain 2,742 s; 1,283 s of the gap remains attributable to scheduling, not to the tree.

**What this means for the owner-facing package.** Do not quote 2,742 s as the clean cost of the suite. The defensible planning figure for a machine-exclusive run at default threads on this tree is **~1,460 s (24 min)** — the growth-adjusted prediction — with **1,200 s (20 min)** as the optimistic end. This is item (c) of §12 and one clean run settles it.

### 3.2 A record that does not add up, and should not be used

Applying the same model to the five-concurrent-suites figures: `W(210 tests) ≈ 13,598 s CPU`, so five such suites require **67,992 s of CPU**. The longest of the five reported walls, 1,875 s, supplies only 1,875 × 20 = **37,500 core-seconds**. The five figures are therefore **impossible if the runs genuinely overlapped** — short by a factor of 1.8. The likeliest benign explanation is staggered starts, so that five suites were never simultaneously in flight; two of the five also reported spurious failures. Either way these numbers cannot support a quantitative claim, which matches how both `V8_3_EVIDENCE_PACKAGE.md` and this diagnostic's brief already treat them. Recorded here so the inconsistency is on the record rather than rediscovered later.

---

## 4. Wall-clock breakdown by family and test

**MEASURED-CONTAMINATED — median load 14.35, max 21.27.** Granularity and method are stated because both bound what these numbers can be used for.

### 4.1 Method, and its limitation

No nightly toolchain is installed, so `-Z unstable-options --report-time` is unavailable. Instead each family was run as **its own process with `--test-threads=1`**, and each stdout line was timestamped as it arrived; under `--test-threads=1` libtest emits exactly one completion line per test in order, so **line-arrival deltas are a sound measure of per-test duration**. Families were run 6-at-a-time so the 20 cores were used, because one serial full run costs 8,035 s.

The instrument (`scratchpad/perf/timed_run.py`) runs the binary with `subprocess`, takes the exit status from `wait4`, and **uses no shell pipe anywhere** — so the `cert_all` defect class (a red suite reporting exit 0 through a pipeline) is structurally impossible here. All 13 families exited 0.

**Limitations, explicitly:**
- **Coverage is 133 of 244 tests (54.5%), in 13 of 38 families.** The sweep was stopped at the orchestrator's instruction. Because families were ordered longest-first, the 13 measured are the **heaviest**, so the mean and median below are biased high relative to the full suite. Do not extrapolate them linearly to 244.
- Wall times are inflated by contention. A cross-check on the size of that inflation: the sweep gives **44.55 s/test** where the single-threaded record gives **35.09 s/test** — consistent with roughly **25–30%** inflation, not a multiple. The families are also the heaviest, which accounts for part of the gap.
- Four families — `repair3`, `ws05r3`, `migration`, `repair2` — completed at load 17.3–19.7 partly because of **my own** cross-worktree build experiment (§7), not the concurrent repair. They are the least trustworthy rows.

### 4.2 Per family

| Family | Tests | Wall (s) | CPU (s) | cpu/wall | sys% of CPU | s/test | Load at finish |
|---|---|---|---|---|---|---|---|
| `repair` | 20 | 901.0 | 1845.1 | 2.05 | 3.1 | 45.1 | 14.68 |
| `ws04r3` | 9 | 681.2 | 1169.7 | 1.72 | 2.4 | 75.7 | 14.50 |
| `repair2` | 9 | 640.5 | 1251.5 | 1.95 | 2.8 | 71.2 | 18.33 ⚠ |
| `migration` | 4 | 595.5 | 1001.7 | 1.68 | 1.8 | **148.9** | 18.96 ⚠ |
| `ws05r3` | 10 | 584.0 | 1107.3 | 1.90 | 2.7 | 58.4 | 19.66 ⚠ |
| `ws03_r3` | 10 | 453.1 | 957.5 | 2.11 | 3.6 | 45.3 | 14.52 |
| `ws04r2` | 5 | 426.6 | 705.9 | 1.66 | 2.4 | 85.3 | 14.50 |
| `ws03` | 15 | 386.1 | 824.3 | 2.13 | 3.9 | 25.7 | 11.91 |
| `ws08_r2` | 10 | 298.0 | 892.0 | 2.99 | 7.4 | 29.8 | 14.96 |
| `repair3` | 5 | 295.8 | 558.5 | 1.89 | 2.4 | 59.2 | 17.29 ⚠ |
| `ws05` | 7 | 277.6 | 523.4 | 1.89 | 3.1 | 39.7 | 13.80 |
| `ws06r3` | 8 | 204.7 | 450.6 | 2.20 | 3.8 | 25.6 | 14.96 |
| `srr` | 21 | 181.1 | 435.2 | 2.40 | 4.2 | **8.6** | 12.02 |
| **Totals** | **133** | **5,925.2** | **11,722.7** | **1.98** | **3.3** | 44.6 | — |

⚠ = additionally contaminated by my own build experiment.

**Note how little test *count* predicts cost.** `srr` runs 21 tests in 181 s (8.6 s/test); `migration` runs 4 tests in 596 s (148.9 s/test). Any sharding or selection scheme that balances by test count will be badly wrong.

### 4.3 The slowest individual tests

**MEASURED-CONTAMINATED** (loads as in §4.2). Per-test timing is *sound* in method (`--test-threads=1`); the absolute values carry ~25–30% contention inflation. **Use the ranking, not the absolute numbers.**

| Rank | Duration | Test |
|---|---|---|
| 1 | 305.3 s | `repair2::plugins_are_governed_capabilities_not_arbitrary_commands` |
| 2 | 237.3 s | `ws04r2::checkpoint_and_handoff_continuity` |
| 3 | 223.0 s | `migration::path_migration_with_rollback_and_memory_rebuild` |
| 4 | 208.5 s | `ws04r3::every_cit_write_is_sealed_and_a_hand_edit_stays_broken` |
| 5 | 194.3 s | `ws03_r3::os_written_facts_are_honoured_on_the_owners_other_provisioned_machines_and_nowhere_else` |
| 6 | 166.3 s | `repair3::plugin_descriptors_can_never_authorise_themselves` |
| 7 | 163.9 s | `migration::adoption_independence_is_bound_to_declared_roles_and_approved_artefacts` |
| 8 | 151.3 s | `ws05r3::material_changes_inside_a_task_complete_only_through_change_control` |
| 9 | 141.9 s | `repair::destructive_migration_requires_answered_gate_record` |
| 10 | 138.2 s | `ws04r3::a_governed_change_reseals_only_what_the_os_may_seal` |
| 11 | 130.1 s | `migration::adoption_dependency_proof_citations_and_rerun_identity` |
| 12 | 113.4 s | `ws04r2::upstream_change_reaches_completed_work` |
| 13 | 100.1 s | `repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger` |
| 14 | 99.5 s | `ws04r3::cit_e_rolls_back_relationships_it_introduces_but_not_their_consequences` |
| 15 | 97.6 s | `repair2::cit_approval_derives_only_from_an_answered_gate` |

**And separately, MEASURED-CLEAN** (load_before 0.86, load_after 2.41 — the single most reliable timing in this report):

> **`brownfield::brownfield_adoption_end_to_end` — ONE test, 318.457 s**, 578.586 s user + 9.115 s sys CPU, cpu/wall 1.845, 1,609,104 blocks written (≈824 MB), 501 files and 19 MB of state left in its scratch root.

That test drives a complete adoption lifecycle through ~24 `gov` invocations: `adopt baseline/inventory/classify/map/plan/test-design`, `adopt review`, `adopt migrate --batch 7`, `verify-migration`, `extract-legacy`, `build-memory`, `verify-memory`, `adopt audit` ×2, a full CIT `propose/simulate/approve/execute` cycle, and a loop of `gate present`. That is ~13 s per `gov` invocation.

### 4.4 The cost distribution — this is the most actionable shape in the report

**MEASURED-CONTAMINATED**, but a *distribution shape*, which is robust to roughly-uniform contention.

Across the 133 tests measured: mean 44.5 s, **median 26.7 s**, p90 99.5 s, max 305.3 s, min ~0.00 s.

| Threshold | Tests | % of tests | Share of total test time |
|---|---|---|---|
| ≥ 10 s | 117 | 88.0% | 99.5% |
| ≥ 30 s | 62 | 46.6% | 81.6% |
| ≥ 60 s | 26 | 19.5% | 56.6% |
| ≥ 120 s | 11 | 8.3% | 34.8% |

> **The slowest 21 tests (15.8%) hold 50% of all test time. The slowest 59 (44.4%) hold 80%.**

The suite is **not** slow because it has 244 tests. It is slow because a few dozen end-to-end lifecycle tests are each minutes long. This is why *test-count-based* sharding fails and why a *duration-aware* schedule (or optimising the shared `gov` hot path) is the lever.

---

## 5. The compile / subprocess / I-O / test-logic split

### 5.1 Compilation — **not** the bottleneck

**MEASURED-CLEAN.** Separated from execution by building first (`cargo build --tests --timings`) and timing the already-built binary afterwards.

| Measurement | Wall | CPU | Notes | Load |
|---|---|---|---|---|
| **Cold build**, no `target/` at all | **39.27 s** | 207.0 s (171.07 user + 35.91 sys), **527% CPU** | 186 units; `--timings` sum of unit durations 159.2 s; peak RSS 1.76 GB; produces a 2.1 GB `target/` | 0.30 → 2.90 |
| "Warm" build ×3 | 3.787 / 3.700 / 3.638 s | — | **Not a no-op — see §7** | 1.33–1.55 |
| Touch one certification test file | 6.382 s | — | | 1.41 |
| Touch `runtime/src/lib.rs` | 3.555 s | — | incremental codegen reuse | 1.46 |

Heaviest compile units (`cargo --timings`): `gov-runtime` 21.79 s + 19.16 s, `libsqlite3-sys` custom build 6.09 s, `gov-cli` 4.95 s, then `zerocopy` 4.31, `syn` 4.25 + 4.07, `regex-automata` 4.18, `regex-syntax` 3.61, `nom` 3.56, `aho-corasick` 3.12.

**Conclusion:** against a suite costing 1,200–8,600 s, a 39 s cold build and a 3.6 s incremental build are noise. **Compilation is not where the time goes.** It matters only as a fixed per-invocation tax (§7), which bites developers running targeted tests repeatedly.

### 5.2 Subprocesses — where the time actually goes

The suite's only subprocesses are **`gov`** and **`git`**. There is no nested cargo (§5.4).

- **Total CPU including all reaped subprocesses: 11,722.7 s across 133 tests** (MEASURED-CONTAMINATED, but a CPU total, so load-robust). This is *the work*.
- **`gov` process spawn is cheap: 3.9 ms.** MEASURED-CLEAN — 10 × `gov --help` = 0.0395 s, load 1.03. Spawning the 190 MB debug binary is not the cost; what `gov` *does* is.
- **`git`: 5 spawns per test** (`init`, 2× `config`, `add -A`, `commit`) from `common::git_init_commit`, i.e. ~665 spawns across 133 tests. At a few ms each this is single-digit seconds in total — **negligible**.
- **Estimated `gov`-invocation count: ≥1,668** static `.ok(` / `.run(` / `.err(` call sites across the suite, plus 258 `for` loops containing them, so the true count is higher. Heaviest: `repair.rs` 160, `ws03.rs` 129, `repair2.rs` 106, `ws05r3.rs` 99, `srr.rs` 99.

**Partition of the CPU between `gov` and the test harness itself: NOT DIRECTLY MEASURED, but bounded.** The libtest harness only builds argv, spawns, and asserts on returned JSON; `git` is negligible by the spawn-count argument above. Therefore effectively all of the 11,722.7 s CPU is inside `gov`. To measure it exactly would require either a `gov` wrapper shim that logs per-invocation `rusage` (the harness bakes the binary path in at compile time via `env!("CARGO_BIN_EXE_gov")`, so this needs a build-time change) or `perf`/`bpftrace` process accounting.

**`gov` is internally multi-threaded**, which is why a "serial" family still occupies ~2 cores:
- **cpu/wall = 1.845 clean** (brownfield alone), **1.98 aggregate** across the sweep; individual family processes were observed at 113–216% CPU.
- Source: `runtime/src/scheduler/mod.rs:818` and `runtime/src/doctor.rs:126` use `thread::scope`.
- The worker count is **deliberately bounded**: `scheduler/mod.rs:798-802` takes `opts.workers` or else `available_parallelism().clamp(2, 4)` — **at most 4 workers**, not one per core. This is sound design, not a defect: 20 concurrent `gov` processes can reach at most ~80 threads rather than ~400. There is a CLI `workers` option but **no environment override**, so a caller cannot lower it to fit a shared machine.
- Because contention *reduces* cpu/wall, **1.98 is a lower bound** on a single `gov` invocation's true parallelism.

**The key scheduling fact, stated correctly.** Applying the CPU-conservation model of §3.1: the suite's total work is `W ≈ 15,800 s` CPU, and the machine-exclusive "serialised" runs achieve `P ≈ 13.2` effective cores — **about 66% of the 20 available**. So the default-parallelism suite is **not** CPU-saturated; roughly a third of the machine is still idle, lost to the long tail (a single 305 s test cannot be subdivided) and to `gov`'s ≤4-worker clamp.

*(Correction of record: an earlier draft of this section asserted the suite was "CPU-saturated" on the reasoning that 20 test threads × ~2 cores = ~40 cores of demand. That reasoning was wrong — it confused peak demand with achieved throughput, and it is contradicted by the 66% utilisation the model derives from the measured CPU total. The 20-core ceiling of ~790 s is therefore not reachable, but it is not the binding constraint either; see R5 on why sharding is still not the answer.)*

### 5.3 Filesystem I/O — measured, and **not** a factor

**The decisive number is the user/system CPU split.** MEASURED-CLEAN on brownfield: **578.586 s user vs 9.115 s system — system time is 1.55% of CPU**, despite ≈824 MB written. Across the contaminated sweep: **382.4 s sys vs 11,340.3 s user — 3.3%**. Writes are buffered through the page cache; the workload is **user-space compute**.

Direct filesystem probe (MEASURED-CONTAMINATED at load 12.17, therefore **pessimistic**, and used as an upper bound to reject):

| Location | `mkdir`+`realpath` ×300 | per op | copy brownfield fixture ×40 | per copy |
|---|---|---|---|---|
| `/tmp` — ext4, ~37,808 entries | 0.044 s | 0.146 ms | 0.176 s | **4.4 ms** |
| fresh empty ext4 dir | 0.035 s | 0.115 ms | 0.184 s | 4.6 ms |
| `/dev/shm` — tmpfs | 0.007 s | 0.023 ms | 0.062 s | 1.6 ms |

- A **repository/fixture copy costs 4.4 ms** (34 files, 216 KB). The suite does ~1 per test → **≈1.1 s for all 244 tests.**
- Fixtures are tiny: only 3 of 7 have a `project/` tree — `brownfield` 34 files/216 KB, `migration` 15/96 KB, `greenfield` 5/32 KB.
- `/tmp` holding 37,808 entries costs **0.03 ms/op** versus an empty directory. Immaterial.
- tmpfs would save ~3 ms per copy. **Immaterial.**

**Therefore: the WSL2 filesystem hypothesis is rejected on measurement, not assumption.** Moving scratch to tmpfs is not worth doing for speed.

**Repository copies inside the product** are also bounded: of 41 scheduler checks, **36 are `Isolation::InProcess`, 3 are `Isolation::Sandbox`, 1 `OwnSandboxes`** (`runtime/src/scheduler/catalogue.rs`). Only the 3 sandbox checks copy a tree (`scheduler/sandbox.rs:63` iterating `paths::iter_repo_files`), and only on explicit tier runs. At fixture scale that is milliseconds.

### 5.4 Nested Cargo — **none**, verified

- **No `Command::new("cargo")` anywhere in `tests/certification/`.** `arch.rs` only inspects command strings and registry config; `ws07.rs` probes for `python3`.
- `runtime/src/verification/product.rs` *builds* a `cargo test` argv (lines 95, 118) for the `rust-cargo` ecosystem — and `fixtures/greenfield/project/Cargo.toml` exists, so a plan *is* produced for it. But that file contains **no execution call site at all** (no `Command::new`, `.output()`, `.status()` or `.spawn()`). The command is planned, never run.
- `runtime/src/memory/claims.rs:775-860` spawns 25 child processes of its own test binary — that is in **`cargo test --lib`**, not the certification suite.

### 5.5 Actual test logic

Not separable from `gov` execution time by construction: these are black-box tests whose "logic" *is* driving `gov` through its JSON contract and asserting on the result (as `tests/certification/main.rs` states). The assertions themselves are JSON comparisons costing microseconds. **Effectively 100% of test time is `gov` execution.**

### 5.6 Why `gov` is CPU-expensive — the mechanism

Not a timing measurement; a structural reading that explains the 96.7% user-space CPU, and it points at the top recommendation.

**The suite drives a *debug* `gov`: `opt-level = 0` for `gov-runtime` (99,655 lines across 122 files) and every dependency except one.** The hot work per invocation is regex tokenisation, string allocation, JSON/YAML parsing, JSON-Schema validation, SHA-256 hashing, ed25519 verification and SQLite. For example `runtime/src/memory/embeddings.rs` is a hashed-n-gram embedder running two regexes, camel-splitting, lowercasing and a SHA-256 per token over every chunk of every file — at `opt-level = 0`.

**The repository already contains the precedent and the measurement.** `Cargo.toml`:

```toml
# IP-W7R3-10 (WS-7 round 3, optional; P2-AR-0043): debug builds hash every bound plugin file, T2 seal, manifest and
# pin with unoptimised sha2, about 20x slower than optimised. Optimising this one dependency in the dev profile changes
# no behaviour (the release profile is unchanged) and keeps the debug `gov` the certification suite drives usable.
[profile.dev.package.sha2]
opt-level = 3
```

`sha2` was found to be **~20× slower** unoptimised and was given `opt-level = 3`. `regex`, `jsonschema`, `serde_json`, `serde_yaml`, `curve25519-dalek` and `gov-runtime` itself are **still at `opt-level = 0`**. See recommendation **R3** — this is the highest-value *unmeasured* experiment and I did not run it because the sweep was stopped.

---

## 6. Q6 — what "serialised" means in practice

**Answer: today it means "one full suite at a time on the machine". It has also, in exactly one recorded run, been taken to mean `--test-threads=1`, and that single conflation is the entire ~2.5 h problem.**

**MEASURED / verified by inspection** — the certification suite contains none of the mechanisms that would force serial execution:

| Mechanism | Finding |
|---|---|
| `#[serial]` attributes | **zero**, repository-wide |
| `serial_test` dependency | **absent** from all three `Cargo.toml` files |
| `std::env::set_var` / `remove_var` in `tests/certification/` | **zero** (count = 0) |
| `set_current_dir` anywhere in `runtime/src`, `cli/src`, `tests/` | **zero** |
| `env::set_var` / `remove_var` in `runtime/src`, `cli/src` | **zero** |
| Statics in `tests/certification/common.rs` | 5, all idempotent `OnceLock` lazy caches of test key material (`suite_root_file`, `signed_source`, `binding_role_key`, `suite_binding`, `foreign_owner`) |
| `RUST_TEST_THREADS` set anywhere | **no** |

**How isolation is actually achieved** (`tests/certification/common.rs`) — and it is good:
- `Gov::run` sets every variable **per `Command`**, never process-wide: `c.env("XDG_STATE_HOME", machine_state_home(&self.root))`, `c.env("GOV_CANONICAL_ROOT", …)`, `c.env_remove("GOV_SESSION")`, `c.env_remove("GOV_ROLE")`.
- Each test's scratch root comes from `tmp()`, whose name contains the **PID and a nanosecond clock** — unique across threads *and* processes.
- `machine_state_home(root)` = `sha256(root path)[..16]`, so each scenario gets **its own simulated machine**, keyed by its own root. The comment states the intent exactly: "the protected machine state is a property of the MACHINE, not of a project, so each certification scenario gets its own simulated machine keyed by its repository root."
- `admin_domain()` is keyed by **process id**, so it is safe across processes too.

**Where the `--test-threads=1` requirement genuinely lives:** the independent verifiers' held-out harnesses, separate crates under `release/verification/…`, which *do* mutate process-global environment. `release/verification/4.1.6-r1-2/evidence/heldout-tests/mint.rs:138-141` calls `env::remove_var` then `env::set_var("XDG_STATE_HOME", …)` and `set_var("HOME", …)`; the accompanying `REPRODUCTION.md` states "**`--test-threads=1` is required.** Several scenarios set `XDG_STATE_HOME`/`HOME`, which are process-global." That is correct **for those harnesses** and must be preserved for them. It does not apply to `tests/certification`.

**One inconsistency to fix while you are here:** `scripts/collect_evidence.sh:22` runs the suite with `--test-threads=4` — a third setting, matching neither the orchestrator's practice nor the single-threaded run. And that script has `set -u` but **no `set -o pipefail`**, while piping `cargo test … | tee … | grep`. It survives only because it parses the `test result:` line; but if compilation fails there is no such line and `status_of_test_result` returns `NOT_RUN (no result line)` — **not `FAIL`**. Given §4 of `V8_3_EVIDENCE_PACKAGE.md` ("V8.3 must treat 'a check can report success while failing' as a class of defect to test for deliberately"), this is a live instance of that class.

**NOT DETERMINED:** the exact `--test-threads` value used by the orchestrator's `cert_all` / `run_check` wrapper. That wrapper is part of the agent harness, not the repository — no definition exists in `release/orchestration/phase-2/packets/specs/`. Only its documented expectation survives: "It takes about 25 minutes." To settle it, capture the wrapper's argv from the harness that provides `run_check`.

---

## 7. Q5 — are artefacts unnecessarily rebuilt?

**Answer: YES — unconditionally, on every single build, in every worktree. And cargo names the cause itself.**

**MEASURED-CLEAN** (load 2.34 → 2.47), `cargo build --tests -v` on an already-built tree:

```
Dirty gov-runtime v4.1.6 (…/p2-perf-diag/runtime): the file `runtime/../.git/HEAD` is missing
Dirty gov-cli v4.1.6 (…/p2-perf-diag/cli): the dependency `gov-runtime` was rebuilt
```

Three "warm" builds in a row each recompiled `gov-runtime` **and** `gov-cli` — **3.638 / 3.700 / 3.787 s**. There is no no-op build.

**Root cause, precisely.** `runtime/build.rs` ends with:

```rust
println!("cargo:rerun-if-changed={}", root.join(".git").join("HEAD").display());
println!("cargo:rerun-if-changed={}", root.join(".git").join("refs").join("heads").display());
println!("cargo:rerun-if-changed={}", manifest.display());
```

In a **linked git worktree** `.git` is a *file*, not a directory:

```
$ cat .git
gitdir: /home/usain/Dynamic-Agentic-Engineering-OS/.git/worktrees/p2-perf-diag
```

so `.git/HEAD` and `.git/refs/heads` **do not exist**. A `rerun-if-changed` path that does not exist makes cargo treat the build script as dirty every time. Verified per path:

| Declared path | Exists in this worktree? |
|---|---|
| `.git/HEAD` | **NO** |
| `.git/refs/heads` | **NO** |
| `release/releases/4.1.6/manifest.json` | **NO** (4.1.6 is unreleased) |
| `framework`, `migrations`, `tools` | yes |

The `.git` misses affect **all 40 linked agent worktrees**. The `manifest.json` miss affects **every tree including the main checkout**, where `.git` *is* a directory — so even the main repository never achieves a no-op build.

**Cost:** ~3.6–3.8 s on every `cargo build` / `cargo test` invocation, plus re-linking the 190 MB `gov` and 164 MB certification binaries. It does not move the 20-minute suite much, but it is a floor on *every* targeted test run during iteration, which is exactly the loop the owner wants to make cheap. A side effect: because the binary is relinked every time, its `stat` identity changes, so the `runtime-digests.json` exe-SHA cache always misses (costing a further 0.106 s, §9).

**Are dependencies rebuilt across worktrees? Yes today, but needlessly.** Controlled experiment (MEASURED-CONTAMINATED for wall time at load 17.3–19.9; the **unit counts are load-independent and are the finding**). A second tree was materialised with `git archive c34c439` into my scratchpad and both trees built against **one shared** `CARGO_TARGET_DIR`:

| Step | Wall | Units compiled |
|---|---|---|
| 1. cold build of the clone → fresh shared target | 62.08 s | **141** |
| 2. build the **original worktree** → *same* shared target | 42.26 s | **2** (`gov-runtime`, `gov-cli` only) |
| 3. build the clone again → *same* shared target | 38.85 s | **2** |

**All 139 third-party dependency units were reused across a different absolute path.** Nothing about the tree location prevents sharing.

They are not shared today because `CARGO_TARGET_DIR` is unset and there is no `.cargo/config.toml`. **MEASURED (load-independent): 177,991 MB — 178 GB — across 41 `target/` directories**, on a disk that is 79% full with ~201 GB free. Range 385 MB to 13,785 MB per worktree.

**This observation was acted on during the diagnostic, and the remediation is recorded here as measured outcome.** The orchestrator audited all 44 worktrees, confirmed that only the active repair held uncommitted content and that every other worktree's work was committed on its branch, then reclaimed the space held by the 23 worktrees belonging to the two completed generations (repair-iteration-1 rounds 3/4, and verification iteration 1):

| | Before | After |
|---|---|---|
| Scratchpad worktree footprint | 177 GB | **59 GB** |
| Filesystem used | 80% | **67%** |
| Free space | ~201 GB | **319 GB** |
| Branches verified still present | — | **all 23** |

All 23 are restorable from their branches at any time. This also removed a hazard that was latent in the original finding and worth naming explicitly: **at 79–80% used, the concurrent repair worker's build could have hit a full filesystem mid-round**, which would have presented as an inexplicable build or test failure on an acceptance-relevant run.

**But sharing is not a free win, and the same experiment shows why:** the two workspace crates carry the same `-C metadata` hash in both trees, so they **overwrite each other and recompile on every cross-tree switch** (steps 2 and 3, 2 units each), and cargo takes an **exclusive lock** on the target directory, which would *serialise* the concurrent agent builds this orchestration depends on. See recommendation **R4** for the balanced form.

---

## 8. Q7 — what shared/global state still prevents safe parallel execution

**Context.** `6aa1cf8` ("scope the suite-run/observation guards per project, not per process") rescoped `SUITE_DEPTH: AtomicUsize` and `OBSERVING: AtomicBool` in `runtime/src/scheduler/mod.rs` into per-project registries keyed by canonical root (`HashMap`/`HashSet` behind `Mutex`+`OnceLock`, poison-tolerant). That fix is correct and is now at `scheduler/mod.rs:1802-1809`.

**The decisive framing, which the question's premise slightly understates.** For the certification suite **as it stands today, none of the runtime's process-global state can affect parallel safety at all**, because every governed operation runs in a **fresh `gov` process** handling exactly **one project**. Process-global and per-project are indistinguishable in a one-project process. The suite's test threads share only the 5 idempotent `OnceLock` caches in `common.rs`.

**So the honest answer to "what still prevents safe parallel execution" is: nothing in the runtime, for the current architecture.** What follows is (a) the one genuine latent defect of the same class, which matters for correctness and for any future in-process execution, and (b) the state that is genuinely shared *outside* the process, which is what Q8 must reason about.

### 8.1 A load-bearing single-project-per-process assumption — disclosed observation, **not** a defect

**`runtime/src/orchestration/generation.rs:91`**

```rust
/// Set once this process has reconciled, so the post-command site does not repeat an operation's own reconciliation.
static RECONCILED: AtomicBool = AtomicBool::new(false);
```

Written at line 1384, read at line 1720 inside `pub fn after_command(p: &Project, label: &str)` — **a function that takes a project but consults a process-global flag**. In a process handling two projects, project A's reconciliation would silently suppress project B's post-command work generation.

**The severity distinction matters, and it is the orchestrator's, adopted here.** Unlike `SUITE_DEPTH` and `OBSERVING` — which were silent process-globals where per-project was plainly meant — this one **declares its process scope in its own doc comment** ("Set once this *process* has reconciled"). It is therefore a **documented design assumption that is currently valid**, because every `gov` invocation handles exactly one project. That makes it a **latent multi-project constraint**, not a defect someone forgot.

Recorded accordingly: a **disclosed observation for the formal verifier**, and a **Phase-8 input**. The point of consequence is that *the single-project-per-process assumption is load-bearing in at least one place*, so in-process multi-project execution is not merely an integration task — it requires this site (and the two set-once statics in §8.2) to be rescoped first. **Not a Phase-2 blocker, and it should not be repaired in this round.**

### 8.2 Process-global but **sound** — audited, no action needed

| State | Verdict |
|---|---|
| `scheduler/mod.rs:1802,1809` observing/suite-depth registries | **per-project**, keyed by canonical root — the `6aa1cf8` fix |
| `kernel_trust.rs:182` verdict cache | **per-project**, keyed `(PathBuf root, String protected-state digest)`; the doc comment states the reason ("a process that changes machine (tests, CI runners) never reads a verdict computed for another machine's records") |
| `capabilities/pincache.rs:258` digest memo | **sound**: lookup slot is `dev:ino`, but `memo_get` additionally filters on the **full `StatKey`** (dev, ino, size, mtime_ns, ctime_ns, mode, uid), so inode reuse cannot alias. Cross-project sharing here is *correct* — same bytes, same digest |
| `kernel.rs:161` `VERIFIED: Mutex<Option<PathBuf>>` | single-slot cache of the verified embedded-kernel dir. Two different dirs in one process would merely miss the cache and re-verify — **performance only, not correctness** |
| `t2.rs:522` `VIEW_CACHE: Mutex<Option<(String, Arc<MachineView>)>>` | single-slot, key-checked; same character — a miss, not a fault |
| `util.rs:131` `GLOB_CACHE`, and ~30 `OnceLock<Regex>` statics | pure function caches — safe by construction |
| `authority.rs:106` `PROCESS_ROLE: OnceLock<ActingRole>`, `migrations/identity.rs:191` `DECLARED_SESSION: OnceLock<Option<String>>` | genuinely process-wide and set once. Harmless now (role and session arrive as `--role`/`--session` per `gov` process) but **both are hard blockers to any in-process, multi-session test execution** |
| `kernel_trust.rs:189` `evaluated()` root set | accumulates roots process-wide by design (BC-P2-36). In a multi-project process it would over-report — a *presentation* leak, not a correctness break |

### 8.3 Genuinely shared state **outside** the process — this is what sharding must reason about

1. **`~/.cache/gov/kernels/`** — the embedded kernel payload cache. The suite sets `XDG_STATE_HOME` per test but **not** `XDG_CACHE_HOME`; only 5 tests override `GOV_KERNEL_CACHE` (in `ws08_r2.rs` and `repair.rs`, being the tests *about* the cache). So **~239 of 244 tests share one machine-level cache**, across all worktrees and all concurrent suites. **MEASURED: 69 MB, 73 entries.** It *is* hardened — `kernel.rs:150-160` documents a past corruption defect ("Two threads materialising at once interleaved their writes and removals and left a corrupt cache marked complete") and the current design stages into `.staging-<pid>-<uuid>`, verifies against the embedded listing, and publishes with one `rename`, keeping a race loser's directory when it verifies. Content-addressed and concurrency-safe by design — but it is the single biggest piece of cross-shard shared state.

2. **`~/.cache/gov/runtime-digests.json`** — exe-SHA cache, keyed `<exe path>|<dev:ino:size:mtime:ctime>`. Written **read-modify-write then rename** (`currency.rs:368-381`), so two concurrent `gov` processes can **lose each other's entries**; and it **self-clears above 64 entries** (`if o.len() > 64 { o.clear(); }`). Benign — a lost entry costs one 0.106 s rehash. MEASURED: currently 31 entries / 15 distinct exe paths, so **not** thrashing today. Named for completeness because it is unsynchronised machine-global mutable state.

3. **`/tmp/gov-cert-machine/<sha256(root)[..16]>/`** — per-scenario simulated machines. Keyed by root hash, and roots contain PID + nanoseconds, so **collision-free by construction**, across threads and processes. But never cleaned: **MEASURED 37,808 leaked scratch roots and 30,837 machine directories totalling 3.7 GB** (`ls` cannot even expand the glob). Costs almost no time (§5.3) but grows without bound.

---

## 9. Answers to the eleven questions

**Q1 — Exactly which command/run consumed the ~2.5 hours?**
**INFERRED-FROM-RECORD** (`release/orchestration/phase-2/AGENT_RUNS/P2-AR-0069.run.yaml:57`). The single largest consumer is `cargo test --test certification`, and the only recorded execution approaching 2.5 h is **P2-AR-0069's official post-fix run: 229 passed / 0 failed in 8,035 s (2.23 h), explicitly "single-threaded"**. Scaled to today's 244 tests at its own 35.09 s/test, that is 8,561 s = **2.38 h**. Nothing else in the record is within 40 minutes of 2.5 h. Two caveats stated plainly: that round ran **two** full suites (a superseded pre-fix `228/1` plus the official `229/0`), so a round total could exceed 2.5 h on its own; and the required check set per round is four commands — `cargo build --release`, `gov contract verify`, `cargo test --lib`, `cargo test --test certification` — of which **only the certification suite has ever been timed in the records**. The other three are **NOT DETERMINED**; measuring them takes ~5 minutes on a quiet machine and is item (b) of §12.

**Q2 — Wall-clock breakdown by test/family.**
**MEASURED-CONTAMINATED** (median load 14.35) — §4.2, per-family table, 13 of 38 families / 133 of 244 tests, with per-test granularity via `--test-threads=1` line timestamping. Granularity achieved: **per test**. Coverage and bias limits stated in §4.1. Completing the other 25 families needs a quiet machine.

**Q3 — The slowest tests/checks and their durations.**
**MEASURED-CONTAMINATED** for the top-15 ranking (§4.3) and **MEASURED-CLEAN** for the single worst confirmed: `brownfield::brownfield_adoption_end_to_end`, **318.457 s for one test** at load 0.86→2.41. Use the ranking rather than the absolute contaminated values. The shape is the finding: **the slowest 21 of 133 tests hold 50% of all test time; the slowest 59 hold 80%**.

**Q4 — Time in compilation / nested subprocesses / repository copies / filesystem I/O / test logic.**
- Compilation — **MEASURED-CLEAN**: 39.27 s cold, 3.6–3.8 s per invocation. **Not the bottleneck.**
- Nested Cargo — **MEASURED (inspection)**: **none executed.** `product.rs` plans a `cargo test` argv but has no execution call site.
- `gov` subprocesses — **MEASURED-CONTAMINATED but CPU-based, so load-robust**: effectively **all** of the 11,722.7 s CPU across 133 tests. Spawn itself is 3.9 ms (clean); the cost is inside `gov`.
- `git` subprocesses — **bounded, negligible**: 5 spawns/test.
- Repository copies — **MEASURED**: 4.4 ms per fixture tree, ~1.1 s for the whole suite. Product-side sandbox copies apply to only 3 of 41 checks.
- Filesystem I/O — **MEASURED**: system time is **1.55%** of CPU clean / **3.3%** contaminated. Rejected as a factor.
- Actual test logic — **not separable by construction** (black-box tests whose logic *is* driving `gov`); assertions are microseconds.
- **NOT DIRECTLY MEASURED:** the `gov`-internal split (hashing vs schema validation vs SQLite vs crypto vs regex). It would take a `gov` wrapper shim recording per-invocation `rusage`, or a profiler (`perf record` on one `gov` invocation). This is the single most valuable follow-up measurement.

**Q5 — Are build artefacts unnecessarily rebuilt between tests/worktrees?**
**MEASURED-CLEAN. Yes, twice over.** (i) Every build in every tree recompiles `gov-runtime` + `gov-cli` because `runtime/build.rs` declares `rerun-if-changed` on three paths that do not exist — cargo's own words: `the file 'runtime/../.git/HEAD' is missing`. Cost ~3.6–3.8 s per invocation. (ii) Dependencies are rebuilt per worktree because `CARGO_TARGET_DIR` is unset — **178 GB across 41 target dirs** — yet the shared-target experiment shows **139 of 141 dependency units are reusable** across trees. Full detail and the measured downside of sharing in §7.

**Q6 — What does "serialised" currently mean in practice?**
**MEASURED (inspection) + INFERRED-FROM-RECORD. It means one full suite at a time on the machine, not tests forced serial within a suite** — proven by contradiction from the 7× gap in §1. Tests are **not** forced serial by anything: zero `#[serial]`, no `serial_test`, zero `env::set_var` in the suite, all env per-`Command`. In exactly one run (P2-AR-0069) it was *also* taken to mean `--test-threads=1`, which is where the 2.5 h comes from. A third setting, `--test-threads=4`, is hard-coded in `scripts/collect_evidence.sh:22`. Full detail §6.

**Q7 — Which shared/global-state reasons still prevent safe parallel execution, after the guards went per-project?**
**MEASURED (inspection). For the suite as architected: none in the runtime** — every governed operation is a fresh one-project process, so runtime globals cannot interfere. What remains, and matters: **one latent instance of the repaired defect class** — `generation.rs:91 RECONCILED: AtomicBool`, read by `after_command(p, …)`, process-global where per-project is meant (a correctness finding, inert today); **two hard blockers to in-process multi-session execution** — `authority.rs:106 PROCESS_ROLE` and `migrations/identity.rs:191 DECLARED_SESSION`, both `OnceLock` set-once; and **three genuinely machine-shared resources outside the process** — `~/.cache/gov/kernels/` (shared by 239 of 244 tests, hardened, content-addressed), `~/.cache/gov/runtime-digests.json` (lost-update race, benign), and `/tmp/gov-cert-machine/` (collision-free but unbounded). Full audit table §8.

**Q8 — Can the suite be safely sharded into isolated groups with bounded parallelism, preserving deterministic evidence?**
**Technically yes — and I demonstrated it: 13 families ran as 13 separate concurrent processes, 133 tests, all exit 0, no cross-shard failures.** The per-process fixed setup also appears small relative to test cost (below). **But my recommendation is not to shard**, because sharding solves a problem that default in-process parallelism already solves better (§10, R5).

If it is nonetheless pursued, these are the specific things each shard boundary must prove isolated, none of which is hypothetical:
1. **`~/.cache/gov/kernels/`** — shared by ~239 of 244 tests. Must prove the staging+rename+verify protocol holds under N-way concurrency, or give each shard its own `GOV_KERNEL_CACHE`. Giving each shard its own cache re-pays the payload materialisation N times and *changes what is under test* for the 5 tests that exercise the cache.
2. **`~/.cache/gov/runtime-digests.json`** — concurrent read-modify-write loses entries. Benign (0.106 s rehash) but must be *stated* as benign, not assumed.
3. **Per-process suite fixtures** — `suite_root_file`, `signed_source`, `suite_binding`, `binding_role_key`, `foreign_owner` are `OnceLock`, built **once per process**, so N shards pay N times. `signed_source` stages and ed25519-signs the whole 1.1 MB / 123-file `framework/` payload. **NOT DETERMINED** how much that costs: my estimator (first-test duration minus median of the rest) gave a median of 6.8 s but a range of **−33.7 s to +209.1 s**, because within-family test costs vary far too much for that control. The method failed; I am not reporting a number I do not trust. What it would take: one instrumented run with a timer around each `OnceLock::get_or_init`, or a purpose-built 2-test binary. The weak conclusion that *is* supportable: the setup is small relative to 30–300 s tests, since no family showed a clear first-test spike.
4. **Evidence determinism** — the acceptance record currently reports one `test result:` line. Sharding produces N, which must be aggregated without ever letting a shard's failure or crash be lost. Given the `cert_all` pipefail precedent, the aggregator is itself a "can report success while failing" risk and must be tested with a deliberately failing shard.
5. **Load recording** — bounded parallelism means shards contend with each other by design, so the evidence must record shard count and machine load or it is unfalsifiable (this is `V8_3_EVIDENCE_PACKAGE.md` §5.3's generalisable requirement).
6. **Duration-aware packing** — test count does not predict cost (`srr` 8.6 s/test vs `migration` 148.9 s/test), so shards balanced by count will be badly skewed.

**Q9 — Can normal development use impact-selected/targeted G1–G4 checks, reserving exhaustive qualification for G5/G6?**
**Partly — and the important half of the answer is INFERRED-FROM-RECORD, because this was already tried and it failed.** `V8_3_EVIDENCE_PACKAGE.md:235-236`: "Per-task check lists let workers close their own class while breaking others (WS-B 20, WS-F 7, WS-D 3 failures). The orchestrator recorded this as **its own design error** and added the full suite as a required check for every run." So **30 real cross-family failures** are the measured cost of narrow selection as practised.

The distinction that makes the question still answerable: what failed was **worker-chosen** check lists, not **derived** impact selection. Derived selection has real raw material — `tests/governance/capability-evidence-map.yaml` binds capabilities to individual tests as `test:certification:<family>::<test>`, **MEASURED: 868 references, 172 distinct tests, 33 families**. But **172 of 244 tests (70%) are mapped; 72 (30%) are not in the map at all**, so map-derived selection cannot currently be sound for the whole suite. Note also that the *product's* G0–G6 tiering already exists and works (41 checks, per-tier membership, 36 of 41 `Cache::Cacheable`) — that is a different level from the certification suite, which has **no** tier structure and is all-or-nothing.

**Recommendation: keep the policy the owner already made explicit** — targeted while iterating, affected dependency families next, exactly one full suite before review — and treat the 72 unmapped tests as a gap to close *before* any automated selection is built. Do not automate selection in Phase 2.

**Q10 — Can evidence caching safely skip unchanged checks where all relevant inputs/hashes are still valid?**
**Yes at whole-suite granularity, no at per-test granularity — and two mechanisms already exist; do not rebuild them.**

Already present: (a) the product's **per-check evidence cache** for its own governance checks — `runtime/src/scheduler/store.rs`, "A result is reused only when the current key is byte-identical", key = `sha256({check, parts:{classes: <digest per expanded dependency class>, extras}})` built at `scheduler/mod.rs:503`, with `key_parts` stored for audit and `result_hash_of` re-verified before reuse, 36 of 41 checks `Cacheable`. Sound design — but it **cannot** speed up the certification suite, because every test builds a brand-new project so the per-project cache is always cold. (b) **`release/orchestration/phase-2/tools/product_identity.py`**, which computes `product_code_digest` = SHA-256 over the git tree object ids of `runtime, cli, tests, framework, capabilities, migrations, tools, fixtures, bin, scripts, Cargo.toml, Cargo.lock`, with its own stated guarantee: *"Two commits with equal product_code_digest carry byte-identical product code, whatever else differs."*

So a **whole-suite** skip is keyable today. For it to be **sound**, the key must additionally hash, and `product_code_digest` covers none of these:
1. **Toolchain** — `rustc`/`cargo` version (here `1.98.1 (48a229cea 2026-09-01)`).
2. **Cargo profile actually used** — opt-level, debug-assertions, overflow-checks. Especially since R3 proposes changing it.
3. **Run mode and machine load** — `--test-threads` and load average. A cached GREEN without its concurrency conditions is unfalsifiable; this orchestration already misread contention as seven defects.
4. **Wall-clock expiry** — the suite calls `chrono::Utc::now()` and signs with `srr_material::far_future()` expiries, so a freshness/currency assertion can change verdict with time alone and no input change. **Entries must expire, not merely match a digest.**
5. **Host state outside the repository** — `~/.cache/gov/kernels/` and `runtime-digests.json` (§8.3).

**What could go wrong, and how it would be detected.** The dominant risk is **freezing a lucky green**: this suite *has* flaked under contention (`203/7` on a tree that was really `210/0`), and a cache would stop re-running the test that would expose it. Mitigation, in order: make the cache **advisory for G1–G4 only and always bypassed for G5/G6 acceptance evidence**; and run a **scheduled unconditional full suite whose result is compared against what the cache would have claimed** — any divergence is a cache-key defect and is reported as one. The product already contains the primitive for exactly this comparison (`store.rs::cache_peek`, "used for the reproducibility comparison and stale reporting"). **Per-test caching is not sound today**: it needs test→input-file attribution, and the evidence map provides capability→test, not test→source paths.

**Q11 — Estimated target runtimes.** See §11. Each is derived, with the derivation shown and its unmeasured components named.

---

## 10. Recommendations as V8.3 input

Ranked by saving-per-risk. "Touches acceptance evidence" means adopting it changes what a verifier must record or re-run.

### R1 — Never add `--test-threads=1` to the certification suite; keep machine-exclusivity. **Do in Phase 2.**
- **Expected saving: ~7×, i.e. ~2 hours per full run** (8,561 s → ~1,201 s at 244 tests). This is by far the largest item and it costs nothing to adopt.
- **Basis:** INFERRED-FROM-RECORD §1/§3, plus MEASURED inspection §6.
- **What must be proven safe first: essentially already is.** The suite has no `#[serial]`, no `serial_test`, zero `env::set_var`; env is per-`Command`; scratch roots are PID+nanosecond unique; `XDG_STATE_HOME` is per-root-hash. The one real hazard — process-global scheduler guards — was repaired in `6aa1cf8`. And P2-AR-0072 already ran **231/0 at stated default parallelism**. The residual risk is not parallelism but *concurrency between suites*, which machine-exclusivity already handles.
- **Touches acceptance evidence: YES, beneficially.** Every run record must state `--test-threads` and the load average. Make the vocabulary explicit so no future worker repeats the conflation: **"serialised" = one suite at a time on the machine, default thread count.**
- **Risk: LOW.**

### R2 — Fix the perpetual rebuild in `runtime/build.rs`. **Defer — out of Phase-2 scope, but it is a small, contained fix.**
- **Expected saving: 3.6–3.8 s on every `cargo build`/`cargo test` invocation, in every one of 41 worktrees**, plus re-linking the 190 MB and 164 MB binaries. Small per run; it is the floor cost of the fast iteration loop the owner wants.
- **Basis:** MEASURED-CLEAN §7, with cargo's own dirty reason.
- **Fix:** emit `cargo:rerun-if-changed` only for paths that **exist**, and resolve the real gitdir for a linked worktree (read the `gitdir:` line from the `.git` file) instead of assuming `.git/` is a directory. Same for the unreleased `release/releases/<version>/manifest.json`.
- **What must be proven safe first:** that `EMBEDDED_COMMIT` still invalidates correctly when `HEAD` moves — that trigger is *why* `.git/HEAD` is declared. A fix that simply drops the trigger would silently stale the embedded release provenance, which is worse than a slow build. Prove with a test that moves HEAD and asserts `EMBEDDED_COMMIT` changes.
- **Touches acceptance evidence: NO** directly, but it changes build fingerprinting, so re-run the suite once after it lands.
- **Risk: LOW–MEDIUM** (the provenance trigger is the whole risk).

### R3 — Raise `opt-level` for the dev profile. **Do NOT do in Phase 2. Highest-value unmeasured experiment.**
- **Expected saving: NOT DETERMINED — potentially the largest item after R1.** I did not measure it; the sweep was stopped first. I am labelling it a candidate, not a finding.
- **Why it is the leading candidate:** the workload is **96.7% user-space CPU** in code compiled at `opt-level = 0` (§5.6), and the repository already records that `sha2` alone was **~20× slower** unoptimised, which is why `[profile.dev.package.sha2] opt-level = 3` exists. `regex`, `jsonschema`, `serde_json`, `serde_yaml`, `curve25519-dalek` and all 99,655 lines of `gov-runtime` are still unoptimised.
- **The exact experiment to run** (≈5 minutes on a quiet machine, no file change — environment only), comparing against the clean 318.457 s baseline:
  ```
  CARGO_PROFILE_DEV_OPT_LEVEL=2 cargo test --test certification brownfield::
  ```
  Then consider `[profile.dev.package."*"] opt-level = 2` (optimise dependencies only, keeping workspace crates cheap to rebuild) versus `[profile.dev] opt-level = 2` (also optimises `gov-runtime`, faster tests but slower incremental builds).
- **Use `CARGO_PROFILE_DEV_OPT_LEVEL`, not `--release`.** `--release` also sets `debug-assertions = false` and `overflow-checks = false`. There is exactly **1** `debug_assert` in the codebase (`policy_precedence.rs:542`) and no `cfg(debug_assertions)`, and arithmetic uses explicit `saturating_*`/`checked_*`/`wrapping_*` (40 sites) rather than relying on profile overflow semantics — so `--release` is *probably* safe, but changing opt-level alone is safe by construction and is the variant to adopt.
- **What must be proven safe first:** a full green suite under the new profile, byte-identical verdicts, and the profile recorded in the evidence. Also measure the incremental-build regression, which is the real cost.
- **Touches acceptance evidence: YES** — the binary under test changes, so the suite must be re-run and the profile becomes part of the evidence record (and of any cache key, per Q10).
- **Risk: MEDIUM.**

### R4 — Reclaim target-directory disk; do **not** share a target dir between concurrently-active worktrees. **Safe in Phase 2 (GC only).**
- **Expected saving: up to 178 GB** on a 79%-full disk; ~20 s of dependency build per newly created worktree if sharing were adopted.
- **Basis:** MEASURED §7 (178 GB across 41 dirs; 2-vs-141 unit reuse).
- **Recommendation:** GC stale worktree `target/` directories (the largest are 10–14 GB each, several belonging to long-finished roles). **Do not** set a global shared `CARGO_TARGET_DIR` while many agents build concurrently: the measured downsides are workspace-crate metadata collision (recompile on every cross-tree switch) and cargo's exclusive target-dir lock, which would serialise concurrent builds. A shared target dir is appropriate only for trees that are not built concurrently.
- **Touches acceptance evidence: NO.**
- **Risk: LOW** for GC; **MEDIUM** for sharing, which is why sharing is not recommended.

### R5 — Do **not** shard the certification suite. **Decision, not an action.**
- **Rationale:** sharding's purpose is to use idle cores. §5.2 shows the suite at default parallelism is already **CPU-saturated** — 20 test threads × ~2 cores per `gov` ≈ 40 cores of demand on 20. Sharding therefore buys little, while adding every isolation obligation in Q8, N× repeated per-process fixture setup, and an evidence-aggregation step that is itself a "reports success while failing" risk. **R1 gets the 7× for free; sharding would add risk for a small remainder.**
- Revisit only if R1 is adopted and a *measured* clean full-suite figure still misses the §11 target.

### R6 — Evidence caching: whole-suite skip only, advisory for G1–G4, never for G5/G6. **Defer.**
- **Expected saving:** skips a ~20-minute run when `product_code_digest` is unchanged — common after documentation-only or orchestration-only commits, which this repository produces constantly.
- **Exact inputs to hash for soundness, and the detection scheme:** Q10. The non-negotiable parts are wall-clock **expiry** and a **scheduled unconditional full run compared against what the cache would have claimed**.
- **Touches acceptance evidence: YES, centrally.** A cached result must never stand as G5/G6 acceptance evidence.
- **Risk: MEDIUM** — the failure mode is freezing a lucky green, which this project has already been bitten by.

### R7 — Add `set -o pipefail` to `scripts/collect_evidence.sh`, and make a missing result line FAIL. **Safe in Phase 2 (not product code).**
- **Expected saving: none — this is a correctness item** in the exact class `V8_3_EVIDENCE_PACKAGE.md` §4 says to treat as a defect class. The script has `set -u` but no `pipefail` while piping `cargo test … | tee … | grep`; if compilation fails there is no `test result:` line and `status_of_test_result` reports `NOT_RUN`, not `FAIL`. It also uses a third thread count, `--test-threads=4` (line 22), which should be reconciled with R1.
- **Risk: LOW.**

### R8 — Clean up suite scratch state. **Safe any time.**
- **MEASURED: 37,808 leaked scratch roots and 30,837 simulated-machine directories, 3.7 GB**, in `/tmp`; `ls /tmp/gov-cert-*` fails with "Argument list too long". Growth is unbounded because roots are PID+nanosecond unique. Time cost is negligible (0.03 ms/op), so this is hygiene, not performance. `common::tmp` says dirs are "kept on failure as evidence" but they are kept on success too.
- **Risk: LOW.** Keep failures' directories; reap successes', or reap by age.

---

## 11. Proposed G1–G6 performance SLOs and the three target runtimes

### 11.1 Product tier SLOs

These govern `gov health run --tier Gn` inside a project — the product's own machinery, which already exists (41 checks, per-tier membership, 36 of 41 cacheable).

The only durable measurements available are **INFERRED-FROM-RECORD** from `P2-AR-0065.run.yaml:45`: on a fresh fixture, **G1 ≈ 2.5 s** (45 executed + 8 reused + 0 not_evaluated, all 53 declared G1 members including all 35 doctor checks) and **G5 ≈ 5.3 s**. Note that record's own warning: folding the 35-check doctor half into every explicit G1/G5 run lengthens the `SUITE_DEPTH > 0` window and raised the odds of interference landing on the heaviest tests.

| Tier | Trigger | Proposed SLO | Reasoning |
|---|---|---|---|
| G0 | every privileged/mutating command | **≤ 150 ms** | a guard in the path of every command; must be imperceptible |
| G1 | mutation — changed paths/schema/secrets | **≤ 3 s** | measured ~2.5 s; hold the line rather than let the doctor half grow it |
| G2 | task close | **≤ 10 s** | superset of G1's families plus scope/readiness/tests/references |
| G3 | checkpoint/handoff | **≤ 10 s** | comparable breadth to G2 |
| G4 | milestone (CIT-E, migration, memory, architecture) | **≤ 30 s** | wider staleness propagation; 11 of 41 checks are G4-and-up only |
| G5 | full suite (adopt/update/release/full audit) | **≤ 60 s** | measured ~5.3 s on a *fresh fixture*; a real project is far larger, so the SLO carries headroom rather than pretending the fixture figure generalises |
| G6 | qualification (synthetic repos/chaos/soak/hidden tests) | **no wall SLO; budgeted** | inherently long-running by design; govern by budget, not latency |

**Stated assumption:** G2, G3, G4 and G5 have **no measurement** behind them — only check-membership counts. They are proposals to be replaced by measurement, not findings. Measuring them needs `gov health run --tier Gn` timed on a realistic project, which is a few minutes of quiet machine.

### 11.2 The three target runtimes the owner asked for

| Scenario | Target | Derivation |
|---|---|---|
| **Ordinary task/change validation** | **≤ 3 min** | The honest basis is per-family cost. Contaminated per-family walls (serial within family) were 181–901 s; at default parallelism a 10–20 test family should land in the low tens of seconds. Add the measured **3.6–3.8 s** build tax (R2 removes it) and `cargo test --lib`. The binding constraint is not speed but the §9/Q9 lesson: targeted runs **must** be followed by one full suite before review, because narrow lists already caused 30 cross-family failures. Confidence: **moderate** — needs the clean sweep to firm up. |
| **Milestone validation** | **≤ 25 min** | The one full certification suite, machine-exclusive, default parallelism. Two derivations bracket it: the four orchestrator "serialised" reproductions at 4.30/4.88/5.11/5.39 s/test give mean 4.92 × 244 = **1,200 s (20 min)**; the growth-adjusted linear fit of §3.1 gives **1,459 s (24 min)** at 244 tests, which is the figure to plan against because it accounts for the suite getting dearer per test as it grew. Corroborated independently by the orchestrator's own "about 25 minutes" guidance to workers. **Available today with no code change**, purely by never passing `--test-threads=1` (R1). Note this supersedes the 2,742 s figure previously quoted — see §3.1. |
| **Full certification (G5/G6 gate)** | **≤ 35 min** | The full required check set: `cargo build --release` + `gov contract verify` + `cargo test --lib` (280 tests) + `cargo test --test certification` (244 tests), run machine-exclusive. The suite contributes ~1,459 s; the other three are **NOT DETERMINED** (never timed in any record) and I budget ~600 s for them, which is the weakest number in this report. Measuring them is item (b) of §12 and takes ~5 minutes. |

**If R3 (dev-profile optimisation) proves out**, all three should be re-derived downward; the workload is 96.7% user-space CPU in unoptimised code, so that is where the remaining headroom is. I am deliberately **not** putting a number on it, because I did not measure it.

---

## 12. What is still outstanding, and what it would take

**AWAITING CLEAN MEASUREMENT**, in priority order. Items (a) and (b) together need ~10 minutes of quiet machine.

- **(a) R3's saving — the highest-value gap.** `CARGO_PROFILE_DEV_OPT_LEVEL=2 cargo test --test certification brownfield::`, compared against the clean **318.457 s** baseline. ~5 min. Turns the report's leading recommendation from a candidate into a finding.
  **The measurement must report two things, not one.** Alongside the duration, it must state explicitly **whether any observable test outcome changed** — pass/fail per test, and ideally the asserted values — because the owner's constraint is that nothing be introduced for speed unless its safety is demonstrated. A build-profile change that provably alters no observable outcome is a different proposition from one that does, and only the former can be adopted without re-opening acceptance evidence. The prior expectation is that nothing changes (opt-level alone leaves `debug-assertions` and `overflow-checks` at their dev defaults, and the repository already carries `[profile.dev.package.sha2] opt-level = 3` with the recorded judgement that "optimising this one dependency in the dev profile changes no behaviour") — but **expectation is not demonstration**, and this is exactly the kind of assumption this orchestration has been burned by. If the saving is large, the honest next step is a full green suite under the new profile before anyone relies on it.
- **(b) The other three required checks (Q1, and the weakest number in §11.2).** Time `cargo build --release`, `cargo test --lib`, and `gov contract verify` individually. ~5 min.
- **(c) The remaining 25 families (Q2, Q3).** Re-run the full sweep clean; the 13 families already measured should also be re-measured, since all 13 are contaminated. ~25 min at pool 6, or ~20 min as one default-parallelism run if only totals are wanted.
- **(d) The `gov`-internal CPU split — the most valuable follow-up of all.** Where inside `gov` the 11,722 s of user CPU goes: hashing, JSON-Schema validation, regex, SQLite, ed25519. Needs `perf record` on one `gov` invocation, or a wrapper shim recording per-invocation `rusage` (the binary path is baked in at compile time via `env!("CARGO_BIN_EXE_gov")`, so a shim needs a build-time change). Without this, R3 is directionally justified but unquantified.
- **(e) Per-process fixture setup cost (Q8 item 3).** My estimator failed (median 6.8 s, range −33.7 to +209.1 s). Needs a timer around each `OnceLock::get_or_init`, or a purpose-built 2-test binary.
- **(f) The `cert_all` wrapper's actual `--test-threads` value (Q6).** Not in the repository; capture it from the agent harness that provides `run_check`.
- **A full 244-test suite run is *not* required.** P2-AR-0075's 2,742 s exists for this exact tree, and the §3 record analysis is stronger evidence for the headline than one more data point would be. Any full run should be cleared with the orchestrator first.

## 13. Things that surprised me

1. **The 2.5 hours is one undocumented flag.** P2-AR-0069 records no reason for `--test-threads=1`. A single defensive choice, made once and never questioned, produced a 7× cost and then became the premise of a performance investigation.
2. **"Serialised" meant the opposite of what it sounds like.** The orchestrator's "serialised" runs are the *fastest* in the entire record. The word was doing two jobs and one of them cost two hours per run.
3. **A correct, well-documented `--test-threads=1` requirement migrated to a corpus it does not apply to.** The held-out verifier harnesses genuinely need it. The certification suite is scrupulously per-`Command` — a deliberate design, with the reasoning written in the comments. Good engineering in one place became folklore in another.
4. **`cargo` never achieves a no-op build here, and nobody noticed**, because 3.7 s looks like a no-op. Cargo was saying `the file 'runtime/../.git/HEAD' is missing` the whole time, just not at default verbosity.
5. **One test takes 318 seconds.** I expected a long tail of many medium tests; instead 15.8% of tests hold 50% of the time. Test *count* is nearly uninformative — `srr` runs 21 tests in the time `migration` runs 1.2.
6. **Every plausible I/O hypothesis was wrong.** WSL2, tmpfs, the 37,808-entry `/tmp`, fixture copying, process spawn, exe hashing — all measured, all immaterial. System time is 1.5% of CPU. The answer was unoptimised user-space compute all along, and the repository already contained the clue in a comment about `sha2` being 20× slower.
7. **`178 GB` of build artefacts**, and 139 of 141 dependency units provably reusable — yet sharing them would make concurrent agent builds *worse*, not better.
8. **The third `RECONCILED` latch.** `6aa1cf8` fixed two process-global guards that should have been per-project. A third, structurally identical, is still there — and I found it while answering a performance question. (It turned out to be the better-behaved kind: it documents its own process scope, so it is a disclosed constraint rather than an oversight — §8.1.)
9. **The most-quoted figure in the package was a scheduling artefact.** 2,742 s was being planned around as the suite's clean cost. Conservation of CPU says it was ~3 test streams' worth of a 20-core machine; the honest machine-exclusive figure is ~1,460 s. The suite records a duration but not the one thing needed to interpret it — the thread count and the load — which is precisely the requirement `V8_3_EVIDENCE_PACKAGE.md` §5.3 had already written down.
10. **A published set of five durations is physically impossible.** The five-concurrent-suite figures need 68,000 CPU-seconds and the longest reported wall supplies 37,500 core-seconds (§3.2). Probably staggered starts — but it means those numbers had been sitting in the evidence package unreconciled.
11. **Total CPU turned out to be the most useful instrument in the whole diagnostic**, and it was almost an afterthought. Because CPU work is schedule-invariant while wall time is not, one `wait4` call did more than any wall-clock timing: it decoded three recorded runs into effective core counts, validated itself against an independent measurement to 2%, falsified my own "CPU-saturated" claim, and survived the contention that invalidated everything else.

---

*Prepared by P2-PERF-0001. Measurement and analysis only: no product source, test, policy or `framework/` file was modified. Raw instrumentation, logs and per-test data are committed alongside this report in `release/orchestration/phase-2/perf-diagnostic-evidence/` (`timed_run.py`, `sweep.py`, `analyse.py`, `M*-*.txt`, `sweep/fam-*.{meta.json,tests.tsv,timed.tsv}`, `sweep/loadavg.tsv`).*
