# Certification performance diagnostic — P2-PERF-0001

**Run id** P2-PERF-0001 · **branch** `phase2/perf-diag` · **base** `c34c439` (the 244-test tree)
**Date** 2026-09-22 · **Role** measurement and analysis only; no product, test, policy or `framework/` change was made
**Audience** an engineer acting on this after Phase 2 closes, who was not present for any of it

---

> ## ⚠ CORRECTION — 2026-09-22, after a clean full-suite measurement
>
> **A machine-exclusive full-suite run has since been measured directly, and it falsifies this report's CPU calibration. Read §3.1 before relying on any figure here.**
>
> ```
> 252 passed; 0 failed; finished in 2966.26s
> real 50m9.968s   user 630m50.420s   sys 18m40.657s
> ```
> Verified quiet at start (load 0.64 / 0.45 / 0.41, no other cargo/gov processes, 319 GB free).
>
> **Total CPU `W` = 38,971 s** — **2.39× the ~15,800 s this report originally inferred.** Three consequences:
>
> 1. **The milestone figure is ~50 minutes, not 20–25.** The 20-minute target in the first version of §11.2 was wrong and is retracted. The achievable floor is **~40–43 min** (§5.2): the machine has **12 physical cores, not 20** — 20 logical CPUs on an 8P+4E part — so `W ÷ 20 = 1,949 s` is a bound SMT cannot reach. **No scheduling change alone is worth more than about 7–10 minutes here.**
> 2. **P2-AR-0075's 2,742 s was never an anomaly.** With the true `W` it decodes to `P ≈ 12.2–13.1` effective cores against this run's 12.95 — indistinguishable. The "~3 test streams" conclusion is **retracted in full**; there was nothing to explain. §3.1 says what went wrong and why the two calibrations agreed with each other while both were wrong.
> 3. **The `--test-threads=1` speedup is ~3×, not 7×** — a correction beyond the one requested, derived in §3.1. The category-error finding itself is **unaffected and is now confirmed directly** rather than by cross-tree scaling.
>
> **What still stands, unaffected:** R1 and the `--test-threads=1` category error · the user/system CPU split (this run: **2.88% system**, against 1.55% clean and 3.3% swept — the I/O rejection is reinforced) · the Pareto shape · the "2 units, not 141" shared-target finding and the 178 GB · the perpetual-rebuild root cause with cargo's own dirty reason · the `RECONCILED` disclosed observation · the evidence-map gap (172 of 244 mapped) · every rejected hypothesis in §5.
>
> **And it materially strengthens R3.** If the workload is ~97% user-space CPU at `opt-level = 0` and scheduling bottoms out around 40–43 min, then **optimisation is the only remaining lever on the milestone figure**, not merely the largest one — and the 12-physical-core correction makes that sharper still, since it shows the machine is already near saturation.

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

**The ~2.5 hours is the cost of running the suite with `--test-threads=1`. Machine-exclusive at default parallelism the same suite is ~50 minutes — measured. But the suite is also genuinely expensive: 38,971 CPU-seconds, 154.6 s of CPU per test, which puts a floor of roughly 40–43 minutes on any scheduling fix — the machine has 12 physical cores, not 20.**

*(Corrected. The first version of this report said "about 20 minutes", inferred from records rather than measured. A direct measurement gave 50 min — see the banner above and §3.1. The half of the headline about `--test-threads=1` is confirmed; the half about what it costs otherwise was wrong.)*

The direct measurement now confirms the `--test-threads=1` mechanism **without any cross-tree scaling**. With `W = 38,971 s` and `gov`'s internal worker cap of `available_parallelism().clamp(2, 4)` — at most 4 workers plus the main thread, so `P ≤ ~5` however many tests you queue — a single-threaded run achieves `P ≈ 4.3` and therefore:

> **38,971 ÷ 4.3 = 9,063 s = 2.52 h** — the owner's "~2.5 hours", reproduced from first principles.

Against the measured 3,010 s at `P = 12.95`, the like-for-like speedup is **3.0×**, not the 7× this report first claimed (§3.1 explains that error too).

The measured anchor, and the only full-suite figure in this report that is a direct measurement rather than an inference:

| | Value |
|---|---|
| Result | **252 passed / 0 failed**, machine-exclusive, default `--test-threads`, quiet at start (load 0.64) |
| Wall | 2,966.26 s harness / **3,010 s real (50 min)** |
| CPU | user 37,850.4 s + sys 1,120.7 s = **38,971 s**, system = **2.88%** |
| Effective cores `P` | **12.95** (65% of 20) |
| Per test | **154.6 s CPU**, 11.94 s wall |
| Achievable floor | **~2,400–2,600 s ≈ 40–43 min** (modelled, §5.2; `W ÷ 20 = 1,949 s` is an unreachable bound) |

**INFERRED-FROM-RECORD** durations from `release/orchestration/phase-2/AGENT_RUNS/` are tabulated in §3, but **§3.1 shows they cannot be normalised across trees the way the first version of this report did**, because per-test cost changed by more than a factor of two as heavy end-to-end tests were added. The s/test comparisons that produced the retracted "20 minutes" and "7×" are no longer used.

Two consequences:

**(a) "Serialised" in this orchestration's vocabulary does not mean `--test-threads=1`.** This survives, and now on a firmer footing than the cross-tree normalisation it originally rested on. Under `--test-threads=1` the machine **cannot exceed `P ≈ 5`** — `gov`'s worker pool is `available_parallelism().clamp(2, 4)`, so at most 4 workers plus a main thread, however many tests are queued behind them — i.e. ≤25% utilisation. The measured machine-exclusive run reached **`P = 12.95`, 65% utilisation**. Runs the orchestrator labelled "serialised" therefore cannot have been single-threaded, whatever their absolute durations turn out to mean. "Serialised" means *one suite at a time on the machine*, default parallelism intact.

**(b) The `~2.5 h` claim** (`release/orchestration/phase-2/HANDOFFS/P2-HO-0052-repair-3-bounded-final.md:182`) is now reproduced from first principles rather than by scaling: **38,971 s ÷ `P≈4.3` = 9,063 s = 2.52 h**. It is independently consistent with P2-AR-0069's single-threaded 8,035 s at 229 tests, and with a round containing two full suites (that round ran a pre-fix `228/1` and the official post-fix `229/0`).

**The `--test-threads=1` habit is a category error with a traceable origin.** The requirement is real, but it belongs to the **independent verifiers' held-out harnesses**, which are separate crates under `release/verification/…` and genuinely do call `std::env::set_var("XDG_STATE_HOME")` and `set_var("HOME")` in-process (`release/verification/4.1.6-r1-2/evidence/heldout-tests/mint.rs:138-141`; the requirement is stated in that directory's `REPRODUCTION.md`). The **certification suite does none of this** — see §6. Carrying their constraint across to the certification suite costs roughly two hours per run and buys nothing.

**The second headline, independent of the first:** there is **no such thing as a warm no-op build in this repository**. Every single `cargo build` or `cargo test` recompiles `gov-runtime` and `gov-cli`. Cargo names the cause itself (§7).

---

## 2. Machine context

**MEASURED-CLEAN.** Recorded at 11:16 UTC, load `0.29 0.33 0.35`.

> **Corrected: this machine does not have 20 independent cores, and the guest cannot see how many it has.**
>
> `nproc` returns 20 and `lscpu` reports *"Core(s) per socket: 10, Thread(s) per core: 2"*, and `/proc/cpuinfo` shows a perfectly uniform 10 × 2 layout with sibling pairs `0-1, 2-3, … 18-19`. **That topology is synthetic.** The `hypervisor` flag is set, and the real i7-12700F is an Alder Lake *hybrid* part: **8 P-cores (2 threads each) + 4 E-cores (1 thread each) = 12 physical cores, 20 threads**. WSL2 is flattening a heterogeneous 8P+4E package into a fabricated homogeneous 10 × 2, so the guest's sibling pairs need not correspond to real SMT siblings, and the guest has no way to learn the vCPU→host mapping.
>
> Three consequences, worked through in §5.2: the "20 cores" divisor used throughout the first version of this report was wrong; **`W ÷ 20` is a bound that certainly cannot be reached**; and the measured `P = 12.95` is far closer to saturation than "65% of 20" suggests, because there are at most 12 physical cores for those threads to run on.

| Property | Value |
|---|---|
| CPU | 12th Gen Intel Core i7-12700F — **20 logical CPUs; 12 physical cores on the real part (8 P + 4 E); guest reports a synthetic 10 × 2** |
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

### 3.1 RETRACTED AND REPLACED — P2-AR-0075 needed no explanation

**The first version of this section concluded that P2-AR-0075's 2,742 s represented "about three test streams' worth of the machine", and offered a reduced `--test-threads` or a three-way shared machine as the mechanism. That conclusion is wrong and is retracted in full.** A direct machine-exclusive measurement (banner, §1) gives `W = 38,971 s` of CPU for 252 tests — **2.39× the ~15,800 s inferred here** — and with the true `W`:

| | Wall | `P` = effective cores | Utilisation |
|---|---|---|---|
| The clean measured run (252 tests) | 3,010 s | **12.95** | 65% |
| **P2-AR-0075 re-derived** (244 tests, the 8 new heavy tests removed) | 2,742 s | **12.2 – 13.1** | 61–66% |

The eight tests added since are genuinely heavy (~177 s/test in isolation; several run ~95 installs or a full governed security-review workflow three times), and removing 3,000–5,600 s of their CPU from `W` brackets P2-AR-0075 at 12.2–13.1 — **statistically indistinguishable from 12.95, and exactly the healthy 65% figure the model predicts for a machine-exclusive run.** There was no reduced thread count, no shared machine, and nothing to explain. **11.24 s/test is simply what this tree costs**, and the clean run reproduces it at 11.94.

There is also an accidental control in the pair: **2,742 s (244 tests) → 2,966 s (252 tests) is +224 s of wall for eight tests carrying ~1,400 test-seconds of work** — which is what parallelism absorbing extra load looks like, and further evidence both runs were scheduled the same way.

#### What went wrong in the calibration, and why the two estimates agreed

This matters more than the retraction, because §3.2 rests on the same inference and because the failure mode is general.

**Error 1 — I calibrated `cpu/wall` from an unrepresentative sample.** `W` was inferred from the single-threaded record as `8,035 s × cpu/wall`, with `cpu/wall` taken as **1.845–1.98** from (a) the clean `brownfield` run and (b) the per-family sweep. Both are biased low, because **`gov`'s internal parallelism depends on which command is running**: the scheduler spins up to `clamp(2, 4)` = 4 workers, but only for `health run` / tier invocations. `brownfield` is an adoption lifecycle dominated by single-threaded commands — `adopt`, `cit`, `gate` — so it measured 1.845. The suite-wide figure is ~4.3. **The damning part: `clamp(2, 4)` is documented in §5.2 of this very report. I found the fact that bounds `gov` at four workers and then calibrated as though it used fewer than two, and never reconciled the two statements.**

**Error 2 — my "heaviest families first" ordering was a bad proxy, and I had the evidence.** The sweep covered 13 families, ordered by *static `gov` call-site count*. That proxy ignores loops and per-call cost variance, and it failed: the sweep averaged **88.1 s CPU/test**, while the full suite averages **154.6**. A sample of the supposedly heaviest third came in at 57% of the whole-suite mean, which is impossible if the ordering were sound. **The falsifying evidence was already in my hands: my own clean `brownfield` measurement is 587.7 s of CPU for a single test — 6.7× the sweep's per-test mean — and `brownfield` sat at position 23 and was never reached.** One measured test should have overturned the ordering.

**Error 3, the one worth carrying into V8.3 — the two estimates were not independent, so their agreement was worthless.** I presented "calibrated two independent ways, which agree" as validation. They were not independent: both rest on `cpu/wall` measured from the *same* biased sample (`brownfield` plus the sweep). Two estimates sharing a common biased input will agree with each other and both be wrong, and their agreement carries no information. **A cross-check is only evidence when the inputs are genuinely disjoint** — and the check that would have been disjoint, a direct measurement of the whole suite, is the one I argued was unnecessary.

#### Error 4, found later and second-order: `W` is not schedule-invariant either

The whole model rests on "total CPU work is a property of the tree, not of the schedule". **On an SMT machine that is not exactly true.** The kernel accounts *thread-seconds*, not work: two hyperthread siblings on one physical core each accrue CPU time at wall-clock rate while together delivering only ~1.2–1.3× one thread's throughput. So the same work measured at `P = 12.95` yields **more** CPU-seconds than measured at `P = 4.3`. `W = 38,971 s` is therefore partly an artefact of how parallel that particular run was.

What it does and does not affect:
- **The retraction is unaffected**, which is the comparison that mattered. The clean run (`P = 12.95`) and P2-AR-0075 (`P ≈ 12.2–13.1`) ran at essentially the same parallelism, so the same SMT inflation is present in both and it cancels.
- **The single-threaded derivation carries more uncertainty than §1 implies**, because it compares across very different parallelism: `W` at `P ≈ 4.3` would be somewhat *lower* than 38,971, so the true single-threaded wall is somewhat *below* 9,063 s. That conclusion does not depend on the model alone — P2-AR-0069 directly recorded 8,035 s for 229 tests (8,842 s scaled to 252), i.e. 2.3–2.5 h. **The ~2.5 h finding stands on a record, not only on arithmetic.**
- **It is the same mistake in miniature**: I took a quantity to be invariant because it was invariant in the idealisation, and did not check the assumption against the hardware. That is Error 3 again, one level down.

#### The consequence I was not asked to correct, but which follows

**The "7×" speedup for avoiding `--test-threads=1` is really ~3×.** It came from comparing 35.09 s/test (single-threaded, 229-test tree) against 4.92 s/test (the "serialised band", 189–225-test trees) — **a comparison across trees whose per-test cost differs by more than a factor of two**, which §3.1 has just shown is invalid. The like-for-like figure, on one tree, from the measured `W`: single-threaded is capped at `P ≈ 4.3` by `clamp(2, 4)`, default threads measured `P = 12.95`, so **3.0×**. The category error and its direction are unaffected and are now confirmed directly; only the magnitude was inflated.

**And the "serialised band" itself does not survive scrutiny.** Take P2-AR-0067: 225 tests in 1,213 s, labelled serialised. At today's 154.6 s CPU/test that tree would hold `W = 34,796 s`, requiring **`P = 28.7` cores on a 20-core machine — impossible.** For 1,213 s to be real at a realistic `P = 13`, the 225-test tree must have cost ≤ **70.1 s CPU/test, i.e. 2.2× cheaper per test than today's** — which in turn requires the 27 tests added since to average **859 s CPU each**, above `brownfield`'s 588 s, one of the heaviest tests in the suite. Possible, but implausible. **The likelier reading is that those four "serialised" figures are not full-suite runs, or are mis-recorded.** Stated as a hypothesis requiring verification, not a finding — but either way **they must not be used to set expectations for this tree**, which is what the retracted 20-minute target did.

### 3.2 Re-derived: the five concurrent suites, and why the conclusion got stronger

The original claim — that the five-concurrent-suite figures are physically impossible if the runs overlapped — was right, but it was derived from the wrong `W`, so it is re-derived here rather than left resting on a bad number. Better, it can be stated without needing `W` for those older trees at all, by inverting the question:

> Five suites finishing within the longest reported wall of 1,875 s have **1,875 × 20 = 37,500 core-seconds** between them. Each suite may therefore cost at most **7,500 s of CPU — 35.7 s CPU/test** at 210 tests.

The measured figure is **154.6 s CPU/test**. Those trees would have to have been **4.3× cheaper per test** than today's. With the original (2.39× too low) `W` the same argument gave a shortfall factor of 1.8; with the correct `W` it is **4.3**, so the conclusion is substantially stronger, and it was robust to a 2.4× calibration error in the first place. The likeliest benign explanation remains staggered starts, so that five suites were never simultaneously in flight; two of the five also reported spurious failures. **These figures cannot support a quantitative claim** — which is how both `V8_3_EVIDENCE_PACKAGE.md` and this diagnostic's brief already treat them.

### 3.3 An evidence-hygiene finding: at least one durable suite figure cannot be reproduced as recorded

**This is a finding against the orchestration's evidence hygiene, not a performance result.** It is recorded here because §3.1 turned it up and because it bears directly on what a formal verifier may rely on.

`P2-AR-0067.run.yaml:62` reads, verbatim:

> `orchestrator_checks: 'Reproduced serialised by the orchestrator on the untouched integrated tree 61e39b6: build 0 warnings; cargo test --lib 276/0; cargo test --test certification 225/0 (1213 s); gov …`

It is recorded as **a single full-suite run**, not a chunked one — of the Phase-2 run records only `P2-AR-0054` mentions chunking ("14 chunks at `e9a2f9c`"). At the measured 154.6 CPU-s/test, 225 tests hold **34,785 CPU-s**, which in 1,213 s requires **`P = 28.7`** on a machine whose hard ceiling is 20 logical CPUs and ~12 physical cores. **As recorded, it cannot have happened.**

Three candidate explanations, and **the record cannot distinguish them**:

1. **Mis-transcription** — the duration belongs to something else, or a digit is wrong.
2. **A partial or differently-scoped run** — a filtered subset, a chunk, or a reused earlier figure, recorded as if it were the whole suite.
3. **A genuinely cheaper tree** — possible only if the 225-test tree cost ≤70.1 CPU-s/test, i.e. 2.2× less than today's, which requires the 27 tests added since to average 859 CPU-s each — above `brownfield`'s 588 s, one of the heaviest tests in the suite. Implausible, not impossible.

The record carries **no thread count, no load average and no command line**, so it is unfalsifiable in precisely the way `V8_3_EVIDENCE_PACKAGE.md` §5.3 says evidence must not be. That is the finding: *the figure is not wrong so much as unusable*, and no amount of re-reading will fix it.

**Consequences, which are the actionable part:**

- **None of the four "serialised band" figures may be used as a baseline by anyone, including the formal verifier.** P2-AR-0067 is the one confirmed; P2-AR-0041, P2-AR-0054 and P2-AR-0064 sit in the same band and are suspect by the same arithmetic. They are the records that produced this report's own retracted 20-minute target.
- **The only usable full-suite baseline is the clean measurement of §1** — 252 tests, 3,010 s, with its load, thread count and CPU recorded.
- **This is the strongest possible argument for the V8.3 requirement that §5.3 already states.** A duration recorded without its concurrency conditions cannot be audited even in principle; here it took a CPU measurement taken for an unrelated purpose, months later, to notice that a durable record was arithmetically impossible. **Make thread count and load mandatory fields of any recorded test result.**
- **Do not spend machine time settling this** by checking out `61e39b6` and re-running — post-Phase-2 work at best, and the tree is no longer the one anyone cares about.

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

**The key scheduling fact, re-derived for 12 physical cores rather than 20 logical.** The clean run gives `W = 38,971 s` CPU in 3,010 s wall = **`P = 12.95`**. What that means depends entirely on the denominator, and the denominator was wrong:

| Denominator | Utilisation | Reading |
|---|---|---|
| 20 logical CPUs | 65% | *"a third of the machine is idle"* — the first version of this report. **Misleading.** |
| **12 physical cores (8P + 4E)** | **108%** | already drawing more scheduled threads than there are physical cores |

Since Linux places threads on idle physical cores before doubling up on siblings, an average of **12.95 runnable threads across 12 physical cores means essentially every physical core was busy**, with a little SMT doubling on top. **The machine was close to saturated, not a third idle.**

**So `38,971 ÷ 20 = 1,949 s (32.5 min)` is a bound that cannot be reached, and it should not be quoted as "the floor".** Reaching it would require all 20 logical CPUs to deliver a full core of throughput each, which SMT does not do: the second thread on a physical core typically adds ~20–30% on CPU-bound integer work, not 100%. Going from the measured state to all 20 logical CPUs busy means doubling up the 8 P-cores and gains only that SMT increment on them — with P-cores contributing the large majority of throughput, roughly **15–25% overall**. That puts the achievable floor at:

> **≈ 3,010 ÷ 1.15…1.25 = 2,400 – 2,600 s ≈ 40 – 43 min**

**NOT MEASURED — a model with stated assumptions** (SMT gain 1.2–1.3× on P-cores; P-cores ~70–75% of throughput; guest vCPUs mostly landing on distinct host physical cores). The vCPU→host mapping is not observable from inside the guest, so I cannot do better than a range from here. **The definitive experiment needs no modelling:** run the suite at `--test-threads` = 4, 8, 12, 16, 20 and plot wall against thread count; the knee is the achievable floor, measured directly. That is ~4 hours of machine time and is clearly post-Phase-2 work.

**The practical upshot is what matters, and it is the opposite of the first version's:** perfect scheduling buys roughly **7–10 minutes**, not 17.5. See R5.

*(Two corrections of record, both instructive. First, an earlier draft asserted the suite was "CPU-saturated" from 20 test threads × ~2 cores ≈ 40 cores of demand; that confused peak demand with achieved throughput and is contradicted by the measured 65%. Second — and this is the cautionary one — the draft that replaced it derived "`P ≈ 13.2`, about 66%", which is within 2% of the measured 12.95/65%. **It was right by luck**: `W` was 2.39× too low and the assumed wall (1,200 s) was 2.5× too low, and the two errors cancelled in the ratio. A derived quantity agreeing with reality does not validate the inputs it was derived from.)*

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

**Cost:** ~3.6–3.8 s on every `cargo build` / `cargo test` invocation, plus re-linking the 190 MB `gov` and 164 MB certification binaries. It is negligible against the 50-minute suite, but it is a floor on *every* targeted test run during iteration, which is exactly the loop the owner wants to make cheap. A side effect: because the binary is relinked every time, its `stat` identity changes, so the `runtime-digests.json` exe-SHA cache always misses (costing a further 0.106 s, §9).

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
**MEASURED, and corroborated INFERRED-FROM-RECORD.** The single largest consumer is `cargo test --test certification` run with `--test-threads=1`. This is now derived from the measured CPU rather than by scaling: `W = 38,971 s` and `gov`'s `clamp(2, 4)` worker cap hold a single-threaded run to `P ≈ 4.3`, giving **38,971 ÷ 4.3 = 9,063 s = 2.52 h**. The corroborating record is `P2-AR-0069.run.yaml:57` — **229 passed / 0 failed in 8,035 s (2.23 h), explicitly "single-threaded"**. *(The first version of this answer scaled 35.09 s/test across trees to reach 2.38 h; that cross-tree normalisation is invalid — §3.1 — though it happened to land near the right answer.)* Two caveats stated plainly: that round ran **two** full suites (a superseded pre-fix `228/1` plus the official `229/0`), so a round total could exceed 2.5 h on its own; and the required check set per round is four commands — `cargo build --release`, `gov contract verify`, `cargo test --lib`, `cargo test --test certification` — of which **only the certification suite has ever been timed in the records**. The other three are **NOT DETERMINED**; measuring them takes ~5 minutes on a quiet machine and is item (b) of §12.

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
**MEASURED (inspection) + MEASURED. It means one full suite at a time on the machine, not tests forced serial within a suite** — proven by the utilisation gap in §1(a): `--test-threads=1` caps the machine at `P ≈ 5` (`gov`'s `clamp(2, 4)`), whereas the clean run measured `P = 12.95`, so runs labelled "serialised" cannot have been single-threaded. Tests are **not** forced serial by anything: zero `#[serial]`, no `serial_test`, zero `env::set_var` in the suite, all env per-`Command`. In exactly one run (P2-AR-0069) it was *also* taken to mean `--test-threads=1`, which is where the 2.5 h comes from. A third setting, `--test-threads=4`, is hard-coded in `scripts/collect_evidence.sh:22`. Full detail §6.

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
- **Expected saving: ~3×, i.e. ~100 minutes per full run** (≈9,060 s single-threaded → 3,010 s measured). *Corrected from "~7×, ~2 hours": the 7× compared across trees of different per-test cost — see §3.1.* Still the largest zero-risk item, but note what it actually is: **a regression to avoid, not a speed-up available.** Current practice is already machine-exclusive default threads at 50 min; R1 prevents anyone dropping back to 2.5 h.
- **Basis:** MEASURED (the clean run, §1), plus MEASURED inspection §6. `gov`'s `clamp(2, 4)` caps a single-threaded run at `P ≈ 5` against the measured 12.95, which is the mechanism.
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

### R3 — Raise `opt-level` for the dev profile. **Do NOT do in Phase 2. Now the single most valuable measurement left, and the only lever that can move the milestone figure.**
- **Expected saving: NOT DETERMINED — but it is now the *only* candidate that can help.** I did not measure it; the sweep was stopped first. Still a candidate, not a finding.
- **Why it is now decisive rather than merely promising.** The clean run, read against the machine's **12 physical cores**, puts the achievable floor at **~40–43 min** (§5.2) against 50 min measured. Sharding, thread tuning and better packing all live inside that **7–10 minute** gap — and the 12-core correction shrank that gap from the 17.5 minutes an earlier draft claimed; impact selection and caching buy time only by *not running tests*. **Reducing `W` is the sole remaining way to move the number**, and `W` is **97% user-space CPU compiled at `opt-level = 0`** (§5.6). The repository already records `sha2` alone as **~20× slower** unoptimised — which is why `[profile.dev.package.sha2] opt-level = 3` exists — while `regex`, `jsonschema`, `serde_json`, `serde_yaml`, `curve25519-dalek` and all 99,655 lines of `gov-runtime` remain unoptimised. A 2× reduction in `W` would halve the work itself, taking a realistic run to ~25 min — more than double what perfect scheduling can deliver, and it is the only lever that does not stop at the hardware.
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
- **Rationale, re-derived for 12 physical cores (§5.2) — and the case against sharding is now much stronger than either earlier version.** The "35% idle" reading was an artefact of dividing by 20 logical CPUs. Against the **12 physical cores** the machine actually has, the measured `P = 12.95` is **108% — essentially every physical core busy**, with Linux already doubling slightly onto siblings. **There is very little genuine idle silicon to reclaim.** Perfect packing is worth ~7–10 minutes (50 min → ~40–43 min), not the 17.5 the earlier draft implied, and what remains is mostly SMT increment on already-busy P-cores.
- **So a shard would contend for hyperthreads rather than occupy idle cores** — it would take its throughput largely *from the other shards*, while still paying every isolation obligation in Q8, N× repeated per-process fixture setup, and an evidence-aggregation step that is itself a "reports success while failing" risk. The residue is also mostly long tail: a single 305 s test cannot be subdivided by any scheduler.
- **R3 is the better trade for the same engineering effort**: it attacks `W` itself, which is the only quantity that moves the floor.
- Revisit only if R3 is adopted and the resulting measured figure still misses the §11 target.

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

**All three are re-derived from the measured `W = 38,971 s` and 20 cores. The earlier targets (≤3 / ≤25 / ≤35 min) were built on the retracted calibration and are withdrawn.**

The governing arithmetic, and it is unforgiving:

> `W = 38,971 s` CPU · **20 logical CPUs on ~12 physical cores** · measured `P = 12.95`
> **Measured: 3,010 s = 50 min.**
> **Achievable floor: ~2,400–2,600 s ≈ 40–43 min** (modelled, §5.2 — `W ÷ 20 = 1,949 s / 32.5 min` is a bound that SMT cannot reach and is **not** quoted as the floor).
> **No scheduling change alone — not sharding, not thread tuning, not better packing — is worth more than about 7–10 minutes here.**

| Scenario | Target | Derivation |
|---|---|---|
| **Ordinary task/change validation** | **≤ 5 min** | At the measured 154.6 s CPU/test and `P ≈ 13`, a 10-test targeted family costs 1,546 ÷ 13 ≈ **119 s**; a 20-test family ≈ 240 s. Add the measured 3.6–3.8 s build tax (R2 removes it) and `cargo test --lib`. Family cost varies enormously (`srr` 21 tests vs `migration` 4 at 148.9 s/test), so this is a ceiling, not a typical. The binding constraint remains Q9's lesson, not speed: targeted runs **must** still be followed by one full suite before review — narrow lists already caused 30 cross-family failures. |
| **Milestone validation** | **≤ 55 min** | **MEASURED: 50 min** (3,010 s real, 2,966 s harness) machine-exclusive at default threads, 252 tests, exit 0. The 55 min target is that measurement plus headroom for continued growth. **This supersedes both the retracted 20–25 min target and the 2,742 s figure previously quoted** — see §3.1. The only thing R1 buys here is *avoiding a 3× regression* to ~2.5 h; it does not make 50 min faster, because 50 min already is the machine-exclusive default-threads figure. |
| **Full certification (G5/G6 gate)** | **≤ 65 min** | `cargo build --release` + `gov contract verify` + `cargo test --lib` (280 tests) + the suite. The suite contributes the measured 3,010 s; the other three remain **NOT DETERMINED** (never timed in any record) and are budgeted at ~600 s, still **the weakest number in this report**. Measuring them is §12(b), ~5 minutes. |

**This is what makes R3 decisive rather than merely attractive.** With an achievable scheduling floor of ~40–43 min (§5.2 — the machine has 12 physical cores, and `P = 12.95` already means essentially all of them are busy) and a workload that is **97% user-space CPU at `opt-level = 0`**, optimisation is now **the only lever that can move the milestone figure at all**. Every alternative — sharding, thread tuning, impact selection, caching — either cannot cross the floor or buys time by not running tests. If R3 delivered even 2×, `W` would fall to ~19,500 s and a realistic run to ~25 min — more than triple what perfect scheduling can buy. I am still deliberately **not** putting a number on it, because I have not measured it; §12(a) is now the highest-value measurement left in the brief by a clear margin.

---

## 12. What is still outstanding, and what it would take

**AWAITING CLEAN MEASUREMENT**, in priority order. Items (a) and (b) together need ~10 minutes of quiet machine.

- **(a) R3's saving — the highest-value gap.** `CARGO_PROFILE_DEV_OPT_LEVEL=2 cargo test --test certification brownfield::`, compared against the clean **318.457 s** baseline. ~5 min. Turns the report's leading recommendation from a candidate into a finding.
  **The measurement must report two things, not one.** Alongside the duration, it must state explicitly **whether any observable test outcome changed** — pass/fail per test, and ideally the asserted values — because the owner's constraint is that nothing be introduced for speed unless its safety is demonstrated. A build-profile change that provably alters no observable outcome is a different proposition from one that does, and only the former can be adopted without re-opening acceptance evidence. The prior expectation is that nothing changes (opt-level alone leaves `debug-assertions` and `overflow-checks` at their dev defaults, and the repository already carries `[profile.dev.package.sha2] opt-level = 3` with the recorded judgement that "optimising this one dependency in the dev profile changes no behaviour") — but **expectation is not demonstration**, and this is exactly the kind of assumption this orchestration has been burned by. If the saving is large, the honest next step is a full green suite under the new profile before anyone relies on it.
- **(b) The other three required checks (Q1, and the weakest number in §11.2).** Time `cargo build --release`, `cargo test --lib`, and `gov contract verify` individually. ~5 min.
- **(c) The remaining 25 families (Q2, Q3) — now also needed to repair the cost model, not just to fill gaps.** Re-run the full sweep clean; all 13 already-measured families must be re-measured too, since all are contaminated *and* the sample is now known to be unrepresentative (it averaged 88.1 s CPU/test against the suite's true 154.6). Budget ~50 min, not the ~25 min estimated before — the sweep's own per-family walls were built on the same understated cost. **Order families by measured CPU from the clean run, never again by static call-site count** (§3.1, Error 2).
- **(d) The `gov`-internal CPU split — the most valuable follow-up of all.** Where inside `gov` the 11,722 s of user CPU goes: hashing, JSON-Schema validation, regex, SQLite, ed25519. Needs `perf record` on one `gov` invocation, or a wrapper shim recording per-invocation `rusage` (the binary path is baked in at compile time via `env!("CARGO_BIN_EXE_gov")`, so a shim needs a build-time change). Without this, R3 is directionally justified but unquantified.
- **(e) Per-process fixture setup cost (Q8 item 3).** My estimator failed (median 6.8 s, range −33.7 to +209.1 s). Needs a timer around each `OnceLock::get_or_init`, or a purpose-built 2-test binary.
- **(f) The `cert_all` wrapper's actual `--test-threads` value (Q6).** Not in the repository; capture it from the agent harness that provides `run_check`.
- **A full 244-test suite run is *not* required.** P2-AR-0075's 2,742 s exists for this exact tree, and the §3 record analysis is stronger evidence for the headline than one more data point would be. Any full run should be cleared with the orchestrator first.

## 13. Things that surprised me

1. **The 2.5 hours is one undocumented flag.** P2-AR-0069 records no reason for `--test-threads=1`. A single defensive choice, made once and never questioned, tripled the cost and then became the premise of a performance investigation.
2. **"Serialised" meant the opposite of what it sounds like.** The orchestrator's "serialised" runs are the *fastest* in the entire record. The word was doing two jobs and one of them cost two hours per run.
3. **A correct, well-documented `--test-threads=1` requirement migrated to a corpus it does not apply to.** The held-out verifier harnesses genuinely need it. The certification suite is scrupulously per-`Command` — a deliberate design, with the reasoning written in the comments. Good engineering in one place became folklore in another.
4. **`cargo` never achieves a no-op build here, and nobody noticed**, because 3.7 s looks like a no-op. Cargo was saying `the file 'runtime/../.git/HEAD' is missing` the whole time, just not at default verbosity.
5. **One test takes 318 seconds.** I expected a long tail of many medium tests; instead 15.8% of tests hold 50% of the time. Test *count* is nearly uninformative — `srr` runs 21 tests in the time `migration` runs 1.2.
6. **Every plausible I/O hypothesis was wrong.** WSL2, tmpfs, the 37,808-entry `/tmp`, fixture copying, process spawn, exe hashing — all measured, all immaterial. System time is 1.5% of CPU. The answer was unoptimised user-space compute all along, and the repository already contained the clue in a comment about `sha2` being 20× slower.
7. **`178 GB` of build artefacts**, and 139 of 141 dependency units provably reusable — yet sharing them would make concurrent agent builds *worse*, not better.
8. **The third `RECONCILED` latch.** `6aa1cf8` fixed two process-global guards that should have been per-project. A third, structurally identical, is still there — and I found it while answering a performance question. (It turned out to be the better-behaved kind: it documents its own process scope, so it is a disclosed constraint rather than an oversight — §8.1.)
9. **I was wrong about the most-quoted figure in the package, in the direction that flattered my own model.** I called 2,742 s a 2.3× anomaly needing explanation and produced a confident mechanism for it. It was an ordinary run; the anomaly was in my calibration. What I had actually done was infer a quantity twice from a shared biased input, observe that the two results agreed, and call that validation — while arguing that the direct measurement which would have caught it was unnecessary. **The measurement I declined to take is the one that falsified me.**
10. **A published set of five durations is physically impossible**, and the correction made it *more* so — the shortfall factor went from 1.8× to 4.3× (§3.2). A conclusion that survives a 2.4× error in its own input was worth stating; those numbers had been sitting in the evidence package unreconciled.
11. **The "serialised band" I built the original headline on probably isn't what it says it is.** Reconciling it against the measured CPU requires those trees to have been 2.2× cheaper per test, implying the 27 tests added since average 859 s of CPU each — more than `brownfield`, one of the heaviest in the suite. Flagged as a hypothesis, not a finding (§3.1), but it means four durable records in `AGENT_RUNS/` deserve a second look.
12. **I divided by the wrong number for the entire diagnostic, and it was on the first line of §2.** I recorded "20 logical cores" from `nproc` in the opening minutes and used 20 as the denominator throughout — for utilisation, for the floor, for the sharding headroom. The machine has **12 physical cores**; `lscpu`'s "10 cores × 2 threads" is itself a WSL2 fabrication over an 8P+4E hybrid part. Both the number I used and the number the guest reports are wrong, in different ways. It inverted the R5 conclusion from "a third of the machine is idle" to "essentially every physical core is busy" — the same conclusion, reached for the opposite reason.
13. **A durable record in `AGENT_RUNS/` is arithmetically impossible**, and it took a CPU measurement gathered months later for an unrelated purpose to notice (§3.3). Not wrong so much as **unusable**: no thread count, no load, no command line, so it cannot be audited even in principle. It is also the record that produced this report's own retracted 20-minute target — a bad baseline propagating into a diagnostic meant to fix baselines.
14. **Total CPU was the most useful instrument in the diagnostic, and it indicted me as readily as anything else.** Because CPU work is schedule-invariant while wall time is not, `wait4` survived the contention that invalidated every wall-clock number, rejected three hypotheses at once via the 1.5–2.9% system-time ratio, and then — once someone measured it directly instead of inferring it — overturned my central reconciliation, my 7× headline, and a 66% utilisation figure that had been right only because two errors cancelled. The instrument was sound throughout; what failed was calibrating it from a sample I never checked against the one clean measurement I already held (`brownfield`, 587.7 s CPU for a single test, 6.7× my own sweep's mean).

---

*Prepared by P2-PERF-0001. Measurement and analysis only: no product source, test, policy or `framework/` file was modified. Raw instrumentation, logs and per-test data are committed alongside this report in `release/orchestration/phase-2/perf-diagnostic-evidence/` (`timed_run.py`, `sweep.py`, `analyse.py`, `M*-*.txt`, `sweep/fam-*.{meta.json,tests.tsv,timed.tsv}`, `sweep/loadavg.tsv`).*
