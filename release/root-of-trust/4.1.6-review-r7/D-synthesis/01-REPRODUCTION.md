# 01 — Reproduction (synthesis D, AR-0022)

HO-0022 §2.1: re-run every probe behind a HIGH or CRITICAL claim and every probe behind a claim that a prior HIGH is closed. This
review re-ran more than that minimum: every revision-7 instrument of the architect, the retained CSI checks, all of reviewer B's
probes, and reviewer C's revision-7 chain including the full `matrix7`.

## Method

- **Inputs.** A `git archive` of `d07d200` in scratch (the pack, `spec/`, `docs/`, `framework/`, `release/releases/`, `fixtures/`), with
  reviewer B's and C's directories copied from the review base (identical to `54be694` and `34633cc`). Real legacy binaries copied
  read-only.
- **Runs.** Unmodified copies of every probe and instrument, driven by `evidence/run/*.sh` (outputs to scratch only; the committed
  pack outputs stayed in place as inputs for dependants such as REGISTER-CHECK, which reads the committed `crashmig7.json`).
- **Comparison.** `evidence/run/compare_all.py` and `compare_matrix7.py`: byte-identical, or JSON leaves compared after normalising
  scratch paths; any differing verdict leaf is listed. Result files: `evidence/reproduction/REPRODUCTION-COMPARISON.json`,
  `MATRIX7-COMPARISON.json`.
- **Environment.** `evidence/README.md`.

## Results

### Architect (AR-0019), revision-7 instruments

| Instrument | Claim it supports | Result |
|---|---|---|
| CS7 (and `CS7-results.json.gz` uncompressed) | computed blocks and invariants; B-A01 and B-A03 controls | **byte-identical** |
| FA7 (two runs) | RV6-H1 closed as stated; shared vectors R1–R16 | **byte-identical** ×2 |
| CUR7 | RV6-H2 closed as stated; CUR-R1 window | **byte-identical** |
| ADM7 | RV6-M6 attack direction; OP-14 (b), OP-15 (a); decision rule; R-CLK-1 | **byte-identical** |
| ENV7 (real `rustc 1.98.1`) | RV6-H3 closed | **byte-identical** |
| BA11r7, BA12r7 | machine classes (§3.2); key subsets below threshold (§3.3) | **byte-identical** |
| PPR7, DA05r7, DA06r7 | RV6-M5 (model), RV6-L12, RV6-M1 | **byte-identical** |
| PROF7 | every exclusion under every declared mechanism | **byte-identical** (113/113 checks, 24/24 exclusions) |
| STATEMENTS-CHECK, REGISTER-CHECK, DA09r7 (578 fields, 0 uncovered), DA04r7 (15/15) | BC6-4 narrowed | **byte-identical** |

### Retained instruments

| Instrument | Result |
|---|---|
| CSI self-test | **byte-identical** (78/78) |
| CSI checks: framework, 4.1.5, 4.1.2, 4.1.3, 4.1.4 | equal except the run-dependent `kernel_dir` leaf; exits 0, 3, 2, 2, 2 |
| DA07r6 on the revision-7 plan; RV6-B-A03 (B's RV7-B-L5 staleness claim) | differ from the committed files in exactly the leaves B names (`plan_rt_rows` 202 vs 199 and the RT-201 row; `sets_checked` 11 vs 7 ×2); no verdict leaf |

### Reviewer B (AR-0020)

| Probe | Behind | Result |
|---|---|---|
| RV7-B-A01 | **RV7-B-H1**; L3 | **byte-identical** |
| RV7-B-A01m | **RV7-B-H1** (executor fix insufficient) | **byte-identical** |
| RV7-B-A02 | **RV7-B-H2** | **byte-identical** |
| RV7-B-CS7 | H1, H2 (computed); **M1** | **byte-identical** |
| RV7-B-A04-A05 | L1, L2 | **byte-identical** |
| RV7-B-A09 | exclusion schema sweep | **byte-identical** |
| RV7-B-A08 (PROF7 on a schema copy with `freshness-witness` and `channel_quorum` added) | exclusion checks load-bearing | **reproduced**: exactly EX-01 and EX-04 fail; 111/113 checks, 22/24 exclusions |

### Reviewer C (AR-0021)

| Probe | Behind | Result |
|---|---|---|
| cur7x | **RV7-C-H1** | **byte-identical** |
| adm7x | M1, L2, L3 | equal except the X5 race counts (4,220 decode errors over 20,183 reads in this run; 0 below-floor reads, as committed) |
| design7 | design findings; decision-record state | **byte-identical** |
| ident7 | M2 | equal except inode values; `every_candidate_contradicts_the_text` true; in this run inode reuse also made I2 call a different repository re-cloned at the same path "same" (one more contradiction) |
| registers7 | registers (104/109/115/119 leaves) | **byte-identical** |
| build7 | the revision-7 trees | every tree state under every reading and every base fact equal; commit ids, `project_trust_id` and entry counts (2 fewer Git entries per tree) differ, run-dependent |
| struct7 | structural tampering | **byte-identical** |
| gitops7 | layout durability (45 operations) | state, kernel-tamper flag, classifications and occupation tracking **equal for every operation** |
| txn7 | M3, M4, M5, L1, A23 | `summary`, `first_install_honouring`, `rollforward_model`, `uninstall`, `absent_with_legacy_named_content` equal; rows differ only in `intervening_note` (stash commit ids, 44 rows); `shared_record` unlocked lost updates 400 vs 397 (race) |
| **matrix7** | **R2-H4 CLOSED as a class**; LP-1r | see below |

### `matrix7`

Reviewer C's independent revision-7 pre-RoT matrix (real 4.1.2–4.1.5 binaries, full registers, 16 workers) was re-run unmodified.

- **Full run** (1,703 s): 118,732 rows, 117,256 active, per-binary counts and binary sha256 equal to the committed summary. Every
  P-TXN row (13,100) recorded `HARNESS_ERROR`: `txn7.py` writes its JSON with the scratch prefix scrubbed to `<ar21>`, so the tree
  paths did not resolve. Every other position ran.
- **P-TXN run** (239 s): the P-TXN positions alone (`--only P-TXN`), with `<ar21>` resolved to the scratch root; 13,100 rows,
  0 harness errors.
- **Composition** (`evidence/run/compare_matrix7.py` → `evidence/reproduction/MATRIX7-COMPARISON.json`): the full run's non-P-TXN
  positions plus the P-TXN run.

| Quantity | This review (composed) | Committed (C) |
|---|---|---|
| Position aggregates (rows, per-state counts, writing rows) | 196 positions, **all equal** | — |
| Active rows | 117,256 | 117,256 |
| **R2-H4**: a `governance/trust/**` or occupation change left `COMPLETE` under any reading without `KERNEL_TAMPERED` | **0 violations** (both runs) | 0 |
| **LP-1r**: root-anchored invocations write no project byte | 3,572 rows, **0 violations** | 3,572, 0 |
| A write moved a non-`COMPLETE` tree to `COMPLETE` (any reading) | **0** | 0 |
| A write produced `ABSENT` (any reading) | **0** | 0 |
| Writing rows on RoT-1 trees | 9,376 + 8,347 = 17,723 | 17,723 |
| Reading-divergence rows | 1,572 + 2,040 = 3,612 | 3,612 |
| Home writes | 70 + 64 = 134 | 134 |
| Harness-error rows | 13,101 − 13,100 (scrubbed paths) = 1 | 1 |
| Classification absent on a `COMPLETE`/`ABSENT` tree | 1,048, **all** on the deliberately degraded `SMUDGE_FILTER_OVERLAY` tree | 1,048 |
| Writes under the account-store path | 30, **all** P-ENV rows that point a cache variable into the store | 30 |
| Transaction-area writes | 296 (140 inside the honoured open transaction, installed state unchanged) | 296 |

**Result: reproduced.** R2-H4 is closed as a class on the revision-7 layout. Note on reviewer C's text (not the pack):
`05-PRE-ROT-MATRIX.md` quotes 28 classification-absent rows and 24 account-store-path rows; its committed summary, like this
re-run, gives 1,048 and 30. The characterisation (all on the degraded smudge-filter tree; all P-ENV cache redirections) holds.

## Deviations and disclosures

- The first A07 run and the first A02 comparison were corrected and re-run (`evidence/README.md`); the `matrix7` P-TXN positions
  were re-run as described above.
- Reviewer C's `matrix6` (review r6) was not re-run by this review; C and the architect both report it reproduced on the revision-7
  export, and `matrix7`, which this review reproduced, is C's broader primary evidence.
- Reviewer B's `run_r7_evidence.adapted.sh` was not used; this review ran the instruments with its own runner (`run_arch.sh`).
