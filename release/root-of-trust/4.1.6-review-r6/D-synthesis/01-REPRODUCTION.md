# 01 — Reproduction (review r6 synthesis D, AR-0018)

HO-0018 §2 item 1 requires this review to re-run every probe behind a HIGH or CRITICAL claim, and every probe behind a claim that a
prior HIGH is `CLOSED`. This review re-ran more than that minimum.

## Method

- **Exports.** Scratch `git archive` exports of the base `b9bed32`; the pack at that base is identical to `4106885` (checked).
  Legacy binaries were copied read-only. Hygiene and tools: `evidence/README.md`.
- **What was re-run.** Every instrument ran unmodified from scratch copies:
  - the architect's revision-6 instruments and the retained revision-5 instruments;
  - all seven of reviewer B's probes;
  - reviewer C's probe chain;
  - review r5's decisive probes.
- **Comparison.** Byte comparison first, then leaf comparison after scratch-path normalisation (`evidence/probes/compare_arch.py`;
  the C and r5 comparisons use the same method). Outputs: `evidence/reproduction/`.

## 1. Architect instruments (claims behind RV5-H1/H2/H3 "as stated CLOSED", retained closures)

| Instrument | Behind | Result |
|---|---|---|
| CS6 JSON and `CS6-results.json.gz` (uncompressed) | BC5-4; the generated statements; RV5-H* minima | **byte-identical** |
| P4r6 | running-mode closures; RV5-M1, M9, L3, L6, L9 | **byte-identical** |
| DA03r6 | mutation sensitivity | **byte-identical** |
| FA6, two runs | RV5-H1 as stated closed; RV5-L1, L2, L6, M9 | **byte-identical**, both runs |
| CON6 | RV5-H3 closed at the registration; RV5-M2 | **byte-identical** |
| ENV6 (real toolchain) | RV5-H2 as stated closed | **byte-identical** |
| SRC6 | RV5-M4 | **byte-identical** |
| UW6, ATTR6, DA07r6 | RV5-M8; RV5-M6; plan detection of review r5 defects | **byte-identical** |
| ADM6 | RV5-M3, RV5-C-A11 | identical except the unlocked mutant's race errors (reported, not asserted by the architect) |
| REGISTER-CHECK, STATEMENTS-CHECK | BC5-4 | **byte-identical** (PASS) |
| CSI6 self-test | §3.1, §4 | **byte-identical** (78/78) |
| CSI6 checks: framework, 4.1.5, 4.1.2, 4.1.3, 4.1.4 | §3.1 | identical except the `kernel_dir` path; exits 0/3/2/2/2 |
| CS5, P4r5, DA03r5, REG5, P1r4 (retained) | CD5-0 retained closures | **byte-identical** |
| FA5 (retained; JSON written in the export) | BC4-2 retained | equal in every leaf (formatting only) |

## 2. Reviewer B probes (behind RV6-B-H1, H2, H3; M1, M2; L1; the holding A11 and A12)

| Probe | Behind | Result |
|---|---|---|
| RV6-B-A01 (parts P, R, S, I, C) | **H1, H2** | **byte-identical** |
| RV6-B-A02 (executed, real `rustc 1.98.1`; computed) | **H3** | **byte-identical** (same machine; digests compiler-dependent) |
| RV6-B-A03 | M2 | **byte-identical** |
| RV6-B-A04 | M1 | **byte-identical** |
| RV6-B-A10 | L1; §3.1, §4 | **byte-identical** |
| RV6-B-A11 | §3.2 holds for running machines | **byte-identical** |
| RV6-B-A12 | §3.3 key subsets | **byte-identical** |

## 3. Reviewer C probes (behind R2-H4 `CLOSED as a class`; RV6-C-M2, M5; L1, L3, L4)

All ran on trees this review rebuilt with C's unmodified `build6.py` from a real 4.1.5 project.

| Probe | Behind | Result |
|---|---|---|
| `register6.py` | registers derived twice | every per-version count and cross-check field equal (104/109/115/119 leaves; 0 help-only, 0 source-only); every leaf path equal. Only the ordering of the option-difference detail lists differs (196 leaves). |
| `build6.py` | revision-6 trees | rebuilt: R6, R6RES, R6CRASH, R6V `COMPLETE`; L0 `LEGACY`. The first launch failed on two scratch inputs C's run had prepared (a lesson fixture and a copy of `framework/`); they were provided from the export, the failed trees were moved aside, and the chain was re-run. |
| `gitops6.py` | RV5-M6 closed; RV6-C-M1, L1 | **byte-identical** |
| `struct6.py`, `attrprec6.py` | closed entry sets; attribute precedence | **byte-identical** |
| `admtx6.py` | RV5-M3 model; RV6-C-L3 | **byte-identical** |
| `crashmig6.py` | **RV6-C-M2** | **byte-identical** (post-recovery `ABSENT` at A-05, A-06; `COMPLETE` at A-11, B-11; legacy serves the restricted marker on 13 prefixes; no legacy command reaches `COMPLETE`) |
| `matrix6.py` (14 workers, 1,115 s) | **R2-H4 CLOSED as a class** | summary equal in every row count, property and per-position aggregate. 62,036 rows (61,520 executed, 516 skipped); R2-H4 property 0 violations; LP-1r 2,492 rows, 0 project writes; Git operations writing into `COMPLETE` 0; transaction-area rows left `COMPLETE` 96 (reported). Differing leaves: binary digests recorded by this run, `elapsed_seconds`, and C's re-summarise flag. |

**Not re-run.**
- C's `ptid-duplication` fact has no script. That a clone, worktree or archive carries the same `project_trust_id` follows from
  `08` §3 (the lock is tracked).
- The architect's LAY6 chain was re-run by reviewer C and is not relied on here: C's independent `matrix6` stands behind R2-H4.

## 4. Review r5 decisive probes (behind "prior HIGH CLOSED" claims)

| Probe | Result against review r5's committed output |
|---|---|
| RV5-B-A01, A04, A09, A12; RV5-D-A01, A04, A05 | **byte-identical** (they load retained revision-5 instruments or checker modes revision 6 did not change) |
| RV5-B-A05 | verdicts identical; 3 time-dependent archive digests differ |
| RV5-B-A08 | verdicts identical; 1 compiler-dependent image digest differs |
| RV5-D-A03 | differs only where revision 6 restated the pack text (`31` GB-4′, RT-138); **byte-identical** to reviewer B's revision-6 re-run |
| RV5-D-A07 | differs only where revision 6 added plan rows (20 leaves) |

The revision-6 answers to these probes are the architect's instruments above: FA6, ENV6, CON6, UW6, DA07r6.

## 5. Deviations and corrections, disclosed

| Item | What happened | Effect |
|---|---|---|
| Reviewer C chain, first launch | `build6.py` stopped on missing scratch inputs; the later steps failed on the missing trees | inputs provided; failed outputs moved to a side directory; full chain re-run (§3) |
| RV6-D-A03, first run | its data-only inventory row listed two digests and was refused `REGISTRATION_NOT_SINGLE_VALUED` (exit 5) | probe error; corrected to one registered digest; the first output is kept as `outputs/RV6-D-A03.first-run-probe-error.json` |
| RV6-D-A06, first run | read the results archive with the wrong structure and crashed | corrected; no output was used |
| RV6-D-A02, A05, A09, A10, first runs | lexical checks matched unrelated text: RT-170's "revoked"; "designated machines" and "packaging" in `21`; "author" inside "authority"; a sentence split that missed "This covers" | patterns tightened before the reported runs; the reported outputs are those runs; no executed or computed verdict of these attacks changed |
