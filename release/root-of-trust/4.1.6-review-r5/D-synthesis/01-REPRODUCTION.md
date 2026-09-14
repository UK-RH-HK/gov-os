# D-synthesis 01 — Reproduction (review r5)

- **Log:** `evidence/reproduction/REPRODUCTION-LOG.json`.
- **Commands:** `evidence/reproduction/rerun_arch.sh`, adapted from reviewer B's; reviewer C's documented commands; and
  `repro_prior.sh`, run unmodified.

## Method and hygiene

- **Sources.** Every instrument ran from scratch, never from the worktree or the canonical checkout:
  - an export of `cdb4e14` (`git archive`);
  - a second, pristine export used for every comparison and for this review's probes;
  - copies of reviewer B's and C's evidence;
  - a scratch clone checked out at `59c1e5c`, which reviewer C's `register5.py` needs for `git show <release commit>:cli/src/main.rs`.
- **Child environment.** `env -i PATH=/usr/bin:/bin`. `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` point into scratch.
  `PYTHONDONTWRITEBYTECODE=1`; `python3 -B`. No other `GOV_*` variable.
  - Reviewer C's P-ENV rows set one `GOV_*` variable as the object under test, as C documents.
  - Reviewer B's A08 found the read-only rustup toolchain through its absolute fallback path; `HOME` stayed in scratch.
- **Legacy binaries.** Read-only; SHA-256 are in the log.
- **Writes into the export.** `FA5-first-admission.py` and `SRC5-source-identity.py` write their JSON into their own
  evidence directory, so they overwrote those two files inside the scratch export.
  - Comparisons use the committed blobs (`git show cdb4e14:…`) or the pristine export.
  - A `diff -r` against a fresh extract confirmed the pristine export was never modified.
- **Worktree.** Clean, including ignored files, before any output was added.

"Byte-identical" means equal to the committed file. "Identical after normalisation" means equal after scratch-path strings
and `elapsed` fields are removed. Where anything else differs, the difference is stated.

## 1. Architect's revision-5 instruments

| Instrument | Behind claim | Result |
|---|---|---|
| CSI `selftest` | BC4-3 closure; B "71 of 71" | **71 passed, 0 failed**; content identical (no differing leaf) |
| CSI `check` framework / 4.1.5 / 4.1.2 / 4.1.3 / 4.1.4 | exits 0/3/2/2/2 | **0 / 3 / 2 / 2 / 2**; identical except the `kernel_dir` path field |
| P1r4 on real 4.1.5 | BC-1 closure retained | **byte-identical** |
| P4r4 | retained trust-state rules | **byte-identical** |
| P4r5 conformance oracle | RV4-H1 closed as stated (VA5 rows); B's CLOSED claims | **byte-identical**: 65/65 revision-5 scenarios, 42/42 retained, 0 expected-`ACCEPTED` attack rows |
| DA03r5 | RV4-M7 closed for the 20 mutants | **byte-identical**: 20/20 normative rules, 17/17 revision-5 mutants |
| FA5 (two runs) | RV4-H2 closed as stated; B's RV5-B-H1 controls | **byte-identical to the committed blob** (`c0b951…`), both runs: 45/45 scenarios, 17/17 vectors, 26/27 mutants |
| REG5 on real 4.1.5 | RV4-H3 closed as stated | **byte-identical**: all 10 verdicts true |
| CS5 derivation calculator | RV4-H1 closed as stated; B's H1/H2/H3 baselines | **byte-identical**: 408 configurations, 21/21 self-checks, 1,752 invariant checks with 0 failures, 138,042 monotonicity checks with 0 violations |
| SRC5 | `30` §4.1 canonical digest; RV5-B-M4 | verdict leaves identical; **16 digest leaves differ from the committed output**; the function hashes `git archive --format=tar <tree>`, not the specified canonical content digest (confirms RV5-B-M4 (ii)) |

## 2. Review r4 and r3 probes against revision 5

| Probe | Result |
|---|---|
| review r4 B `RV4-B-M-reference-model`, `RV4-B-arch-functions` | byte-identical |
| review r4 B `RV4-B-surface-probes` | parts U and T unchanged; part P now exit 5 (the revision-4 retaining inventory is malformed under revision 5), as reviewer B reports |
| review r3 copies RV3-B-A01, RV3-B-CSI-injections, RV3-D-precedence-lattice, RV3-D-surface-forward-compat-and-removal | byte-identical to review r4's committed re-run outputs |
| review r4 D `RV4-D-A03`, `RV4-D-A03b` | byte-identical (9/20 on P4r4, as committed) |

The first scripted run of RV3-D-surface, RV4-D-A03 and RV4-D-A03b omitted their positional arguments and exited 1 before
doing anything. They were re-run with the arguments; the results above are from that run.

Not re-run by this review (not behind a HIGH or a closure claim; reviewer B re-ran them):
- `RV4-B-confinement-and-first-binary`;
- the RV3-B-A03/A14/A16 copy;
- the r2 P2 copy;
- `RV4-D-A02` (its retention form is superseded; REG5 covers it).

## 3. Reviewer B's probes (every probe behind a HIGH)

| Probe | Behind | Result |
|---|---|---|
| RV5-B-A01 first-admission channel (real Ed25519) | **RV5-B-H1**, M1 (A03), L1 (ORD) | **byte-identical** |
| RV5-B-A04 calculator extensions | **RV5-B-H1** (L), **H2** (I), **H3** (P), M1 (R), L5 (C) | **byte-identical** |
| RV5-B-A05 source identity | M4 | every verdict identical; three time-dependent archive digests differ (by design, as B states) |
| RV5-B-A08 build image (real rustc 1.98.1, gcc) | **RV5-B-H2** | every verdict identical (26 boolean and short fields); binary digests differ because they depend on the local compiler |
| RV5-B-A09 floor class kernels (real 4.1.5) | **RV5-B-H3**, M2 | **byte-identical** |
| RV5-B-A12 machine classes | §3.2, L3, M3 | **byte-identical**: 296 rows, 0 `current` |

## 4. Reviewer C's probes, and C's reproduction of prior probes

| Probe | Behind | Result |
|---|---|---|
| `register5` (four real binaries; `--help` and source) | the registers | **byte-identical** (104/109/115/119 leaves) |
| `build5` | trees | exit 0 |
| `gitops5` (real Git 2.43) | RV5-C-M1, M2; durability | identical except 18 scratch tree-path strings |
| `matrix5 --focus` (four real binaries) | **R2-H4 `CLOSED as a class`**; RV4-M1 closure; C-L1, C-L2 | 30,165 rows (285 skipped); summary identical except `elapsed_seconds`; LP-1r 1,335 rows 0 violations; R2-H4 property 0 violations; LP-1s 16 counterexamples; transaction-area writes 96, all `COMPLETE`; classifications lost 0; Git-operation trees written into `COMPLETE` 0 |
| `admit_tx` (reference executor) | RV5-C-L3 | A08, A09, A10 identical; A11 (eight racing threads) differs in the number of stray move-aside directories and one `FileNotFoundError`: nondeterministic, as the race is |
| `repro_prior.sh` → review r4 C `subdir_escape`, `durability`, `legacy_regain` | RV4-M1, RV4-M6, LR-2 | **byte-identical** |
| `repro_prior.sh` → review r4 D `RV4-D-A01` | RV4-M1 re-rating | **byte-identical** |
| `repro_prior.sh` → architect ST5 `subdir-escape`, `gitignore-surgery`, `subdir-matrix-writing-rows` | RV4-M1, RV4-M6 closure | **byte-identical** |
| `repro_prior.sh` → architect ST5 `subdir-matrix-summary` | RV4-M1 closure | identical except `elapsed_seconds` |
| `repro_prior.sh` → architect ST5 `D-A01-rerun` | RV4-M1 closure | every state key and every other case equal. In case N2, the nested-root legacy CIT wrote a run-dependent set of legacy files (this run: `adapter-manifest.json`, `tool-registry.json`; committed: `D-0001.yaml`, `CKPT-00001.yaml`). `KERNEL_TAMPERED` true in both. |
| `repro_prior.sh` → architect P3r3 (2,085 jobs) | LP-1r | `summary`, `property_L3`, `chain_summary`, `job_count` equal |
| `repro_prior.sh` → review r4 C matrix (10,618 invocations, 168 chains) | `--root` property; R2-H4 | 10,618 rows; writes by layout × position × variant, states, trust rows (56) and writing commands all equal |

## 5. This review's probes

| Probe | Evidence class | Second run |
|---|---|---|
| RV5-D-A01 registered content not first-hand | computed (P4r5) + executed (checker, real 4.1.5) | byte-identical |
| RV5-D-A03 user-writable install anchoring | computed (reference `gov_run`, P4r4) | byte-identical |
| RV5-D-A04 conformance-vector gaps | executed (reference executor, 44 Ed25519 verifications) + computed (P4r5) | byte-identical |
| RV5-D-A05 forward compatibility | executed (checker) | byte-identical |
| RV5-D-A07 plan regression detection | computed (CS5 module, plan and register text) | byte-identical |

**Harness correction, recorded for transparency.** The first RV5-D-A04 run built its running-mode rows R1/R2 with a Trust
State listing the revoked digest but without the revocation statement that P4r5's `negative_set` reads, so the oracle
returned `ACCEPTED`. P4r5's own `AP-A8_candidate_revoked` builds both, so the probe was corrected to do the same (oracle
then `BINARY_REVOKED`). The bootstrap reference rows were unaffected: that executor reads the Trust State's `revocations`
directly. The committed output is from the corrected probe.

Similarly, the first RV5-D-A07 verdict for RV5-H1 matched any register row containing "evaluator". It was narrowed to rows
naming lineage selection or channel quorum, of which there are none.
