# Evidence index (RoT-1 revision 5)

## Revision 5 evidence (`r5/`)

**Hygiene.** Every probe ran in `…/scratchpad/ar-0011/` under `env -i`; `GOV_*` removed from children; `HOME`, `XDG_*` and
`GOV_KERNEL_CACHE` in scratch; `PYTHONDONTWRITEBYTECODE=1`; legacy binaries read-only; no forced deletes. Absolute paths in
outputs are replaced by `<scratch>`, `<worktree>`, `<legacy-bin>`. Commands, SHA-256 digests and every comparison:
`r5/EVIDENCE-RUN-LOG-r5.json`, `r5/ST5-RUN-LOG.json`, `r5/FA5-RUN-LOG.json`. Revision-4 controls ran on a `git archive`
snapshot of the base commit `c8cdfac` in scratch.

| File | Kind | Establishes | Result |
|---|---|---|---|
| `r5/CS5-tcb-capability-sets.{py,json}` | reference (derivation calculator; FD-3) | minimal capability sets for five attack goals under every OP-2, OP-8, OP-9, OP-10 answer and four victim classes; controls for R-REP-2, R-REP-3, OP-9 (d) pass-through, CR4-B-07 option 2 | 408 configurations; 21/21 self-checks; 1,752 invariant checks, 0 failures; 138,042 monotonicity checks, 0 violations |
| `r5/P4r5-conformance-oracle.{py,json}` | reference (conformance oracle; loads `P4r4-trust-state-model.py` unmodified) | admission-predicate/1 running mode; E7 under registration; carried CR4-B rules; distinguishing scenarios for D-A03's mutants; VA4 rows and P4r4 binary scenarios re-expressed | 65/65; retained P4r4 42/42; 0 expected-`ACCEPTED` attack rows |
| `r5/DA03r5-oracle-regression-sensitivity.{py,json}` | reference (mutation) | review r4 D-A03 re-run against P4r5; new-rule mutants | D-A03 normative rules 20/20; revision-5 rules 17/17 |
| `r5/gov_admit_reference.py`, `r5/FA5-first-admission.{py,json}` | executed (real Ed25519 through OpenSSL; real 4.1.5 register) | bootstrap-mode admission, installation, admission records, genuine-binary rule; revision-4 paths (b), (c) as controls | 45/45 scenarios; 17/17 vectors; 26/27 mutants (1 equivalent under KS-7); deterministic |
| `r5/SRC5-source-identity.{py,json}` | executed (real Git) | canonical content digest versus `git archive` digests | 10/10 |
| `r5/REG5-release-scoped-registration.{py,json}` | executed (checker as amended; real 4.1.5 consumer) | part P, D-A02 T1–T4, ranges, rewrite, reversion, migration, consumption | 10/10 verdicts |
| `r5/CSI5-selftest.json`, `r5/CSI5-CSI-check-*.json` | executed (checker) | self-test and payload checks against the revision-5 checker | 71/71 (56 revision-4 cases identical); exits 0/3/2/2/2 with equal counts |
| `r5/ST5-*` | executed (reviewer C's trees and harness copies, attributed; real 4.1.2–4.1.5) | `18` §9.1–§9.2 predicate; subdirectory matrix; `subdir_escape`; D-A01 re-run; `.gitignore` surgery | P5-1…P5-3 hold, 0 counterexamples over 6,292 invocations |
| `r5/P3r3-rerun-r5-summary.json` | executed (harness unchanged) | root-anchored legacy containment | 2,085 jobs; equal to committed |

## Revision 4 evidence (history; retained instruments re-run in revision 5)


**Scope and hygiene.**
- **Scratch only.** Every probe ran in a scratch directory given by the operator. The repository, the canonical checkout
  and the review directories were never written.
- **Environment.** `GOV_*` variables are removed from child environments, and `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` point
  into scratch.
- **Status.** The probes are architecture instruments, not the Governance OS implementation.
- **Placeholders.** Absolute paths in committed outputs are replaced by `<repo>`, `<scratch>`, `<scratchpad>` and
  `<legacy-bin>`.
- **Run log.** Commands, times, exit codes and output digests are in `EVIDENCE-RUN-LOG.json`.

**How expectations are set.** Architect evidence is never an expected result for the implementation. The models and
checkers are conformance oracles; their value is in the mutants and distinguishing scenarios (`../12-ACCEPTANCE-TEST-PLAN.md`
§8).

## Revision 4 evidence

| File | Kind | What it establishes | Result |
|---|---|---|---|
| `CSI-check-framework.json`, `CSI-check-release-4.1.5.json`, `CSI-check-release-4.1.5-lock-operations-removed.json`, `CSI-check-legacy-4.1.{2,3,4}.json` | coverage checker (`../constitutional-surface/csi_check.py check`, revision-4 inventory) | E7 over whole payloads: classification, presence, YAML profile, registration, exact precedence, migration whitelist | framework: 113 files, exit 0. 4.1.5: exit 3 (historical `set_lock_field` migrations). 4.1.5 with lock operations removed: exit 0. 4.1.2: exit 2 (1 unclassified, 62 missing, 65 violations). 4.1.3: exit 2 (15 missing, 65 violations). 4.1.4: exit 2 (6 missing, 64 violations, 44 precedence differences). |
| `CSI-selftest.json` | checker self-test | HO-0001 §3.1 list plus revision-4 cases: each mode moved to `immutable` (S26–S30), removals (S31–S40), YAML profile (S41–S43), CR-07 (S44), reordering (S45), migrations (S46–S49), owner domain (S50–S52), reductions (S53–S54), `exception_relaxable` (S55) | **56 of 56** as expected |
| `P1r4-project-strength-and-absence.{py,json,stderr}` | reference (revision-4 library) + executed consumption on the real **4.1.5** binary | BC-1. **A:** order soundness, the RV3-D-A01 pairs, R01–R09 removals, TPS reductions. **B:** each attack consumed as revision-3 and revision-4 effective kernels, with harm assertions (authority, indexing and retrieval, gate). **C:** strength vector over effective policy; release-signed migrations (RV3-B-A18). **D:** composition (the directed join). | 0 unsound of 343; revision 3 loses strengthening in 9/9, revision 4 keeps it in 9/9, reference = binary 9/9; harms flip where observable; vector reports 9/9 revision-3 losses and 0 revision-4; migrations M1–M4, M6, M7 refused before any write, M5 gated, M8 control; composition verdicts true; 12 consumers initialised |
| `P4r4-trust-state-model.{py,json,stderr}` | reference model, independent of P4r3 | BC-2 and related rules: inclusion anchors, pin validity and integrity, currency proofs, witness purpose, clock, lift, playbooks, rotation, whitelist, `verify-artifact`, trust gates; a conformance oracle with 9 single-rule mutants | **54 of 54** hold; **9 of 9** mutants detected; matrix 132 rows (77 refused, 42 stated core, 13 (d) residual, 0 unstated, 0 `current`) |
| `VA4-verify-artifact-source-scenarios.{py,json,stderr}` | reference (P4r4 rule functions loaded by path) | BC-3: RV3-B-A08, the REJECTED variant, RV3-D-A03, custodial pre-checks, OP-2 options, and minimum capability sets | **16 of 16** as expected; 12 refused; route S, route S under OP-4 "no" and route B documented as minimum sets |
| `P3r3-rerun-r4-summary.json` | executed, harness unchanged, real **4.1.2–4.1.5** | R2-H4 not regressed | 2085 jobs; `summary`, `property_L3`, `chain_summary`, `job_count` equal to the committed `P3r3-pre-rot-register-matrix.json` |
| `LR2-installation-state-and-strength-reference.{py,json}`, `LR2-spec.json` | reference over real trees | RV3-M6/C-1 bounds and RV3-L7: the installation state machine and the strength vector on the 24 trees left by the legacy probes | trees with legacy entries: `PARTIAL(occupation)` or `LEGACY`; intact and clone trees `COMPLETE`; fresh clone after the untracking idiom: revision 3 `PARTIAL`, revision 4 `COMPLETE`; `PROJECT_STRENGTH_WEAKENED` on A05a (3) and A05c (9) |

## Review r3 probes re-run against revision 4

| File | Probe (origin, attribution) | Result |
|---|---|---|
| `rerun-RV3-B-A01-precedence-immutable.json` | review r3 B `RV3-B-A01-precedence-immutable.py`, run unmodified against this worktree | `passes_E7_reference_checker: false` |
| `rerun-RV3-B-A03-A14-A16-probes.json` | review r3 B `RV3-B-A03-A14-A16-probes.py` | A03: the 4.1.5 child writes both pin files as the invoking uid, mode 0644, which the revision-4 predicate ignores. A14: exit 2 for all 10 leaves. A16: exit 3. |
| `rerun-RV3-B-CSI-injections.json` | review r3 B `RV3-B-CSI-injections.py` | I01–I06 exit 2; I07 exit 3; I08 exit 3 (from the base payload's historical lock operations); I09 exit 2 |
| `rerun-RV3-D-precedence-lattice.json` | review r3 D `RV3-D-precedence-lattice.py` | 36 pairs, no unsound pair; TPS `immutable` registrations are computed reductions and remove no strengthening |
| `rerun-RV3-D-surface-forward-compat-and-removal.json` | review r3 D `RV3-D-surface-forward-compat-and-removal.py`, unmodified | R01–R09 exit 2; F01/F05/F06/F07/F09 exit 3 because the fixture does not register precedence exactly |
| `RV3-D-A09-A10-rerun-r4-release-consistent.{py,json}` | copy of the D probe with precedence mirrored into the kernel fixture | F01/F05/F06/F07/F09 exit 0; F02/F12 exit 2; F03/F04/F08/F10/F11 exit 3; R01–R09 exit 2 |
| `rerun-P1r3-against-r4-lib.json` | revision-3 architect `P1r3-floor-coverage.py` against the revision-4 library | harm verdicts (a)–(e) true |
| `rerun-RV3-C-build_base.json`, `rerun-RV3-C-destructive.json`, `rerun-RV3-C-occ_removal.json`, `rerun-RV3-C-full_removal_and_merge.json`, `rerun-RV3-C-durability.json` | review r3 C scripts, copied to scratch with only `REPO` set | destructive: 84 runs, 0 writes, property holds. Removal: legacy outcome reproduced, `governance/trust` unchanged, RoT-1 `PARTIAL(occupation)`. Merge: `framework.lock~legacy`. Durability as review r3. |
| `rerun-RV3-D-legacy-git-restore.json` | review r3 D `RV3-D-legacy-git-restore.py` on the revision-3 layout | A05/A06 legacy outcome; A07 idiom lists the occupation; fresh clone lacks it |
| `RV3-D-A05-A07-rerun-r4-layout.{py,json}` | copy of the D probe on the revision-4 layout (ignore-rule delta; the A07 commit tolerates "nothing to commit") | A05/A06 legacy outcome (documented LR-2); A07 idiom lists nothing; occupation present in a fresh clone |

**Not re-run unmodified:**
- review r3 B's `RV3-B-M-reference-model.py`, which encodes revision-3 rules;
- review r3 D's `RV3-D-oracle-anchor-artifact.py`, which loads P4r3.

Their constructions are P4r4 scenarios (`../22-REVIEW-RESPONSE-MATRIX.md` §1.1).

## Running (from this directory)

```sh
export SCRATCH=<fresh scratch dir>
E="env -i PATH=/usr/bin:/bin HOME=$SCRATCH/home PYTHONDONTWRITEBYTECODE=1"
$E GOV_REVIEW_SCRATCH=$SCRATCH/p1r4 GOV=<legacy-bin>/gov-4.1.5 python3 P1r4-project-strength-and-absence.py > P1r4-project-strength-and-absence.json
$E python3 P4r4-trust-state-model.py > P4r4-trust-state-model.json
$E python3 VA4-verify-artifact-source-scenarios.py > VA4-verify-artifact-source-scenarios.json
P3_REPO=<repo> P3_LEGACY_BIN=<legacy-bin> $E python3 P3r3-pre-rot-register-matrix.py $SCRATCH/p3 --workers 12 > $SCRATCH/P3r3-full.json
$E python3 LR2-installation-state-and-strength-reference.py <spec with real tree paths> $SCRATCH > LR2-installation-state-and-strength-reference.json
$E python3 RV3-D-A05-A07-rerun-r4-layout.py $SCRATCH/git-r4 <L3 layout with the revision-4 ignore rule> <legacy-bin>/gov-4.1.5 > RV3-D-A05-A07-rerun-r4-layout.json
REVIEW_REPO=<repo> $E python3 RV3-D-A09-A10-rerun-r4-release-consistent.py $SCRATCH/fc4 > RV3-D-A09-A10-rerun-r4-release-consistent.json
$E python3 ../constitutional-surface/csi_check.py check --json <kernel dir> > CSI-check-<name>.json
$E python3 ../constitutional-surface/csi_check.py selftest --scratch $SCRATCH/csi > CSI-selftest.json
```

- P3r3 takes under a minute with 12 workers on 20 cores; P1r4 about a minute; the others seconds.
- The legacy binaries' SHA-256 digests are in `P3r3-rerun-r4-summary.json` and `EVIDENCE-RUN-LOG.json`.
- `LR2-spec.json` shows tree paths with the `<scratch>` placeholder; to re-run it, substitute the real scratch trees
  produced by reviewer C's and synthesis D's probes.

**Attribution.**
- **P1r4:** reuses reviewer B's `RV3-B-A01` consumer set-up and harm tests, and the materialisation method of the
  revision-3 `P1r3`.
- **P4r4:** takes scenario shapes from review r2 `P4`, revision-3 `P4r3`, reviewer B's reference model, and synthesis D's
  oracle probe.
- **Copies:** the `RV3-D-*` copies are attributed in their docstrings.
- **Rules:** the rules are revision 4. The review directories were not edited.

## Earlier evidence (history)

| File | Revision | Status |
|---|---|---|
| `P3r3-pre-rot-register-matrix.{py,json,stderr}` | 3 | The harness is unchanged and was re-run (`P3r3-rerun-r4-summary.json`); the committed output remains the reference for equality. |
| `P1r3-floor-coverage.{py,json,stderr}` | 3 | Superseded by P1r4 for the project layer. Re-run against the revision-4 library (`rerun-P1r3-against-r4-lib.json`). |
| `P4r3-trust-state-model.{py,json,stderr}` | 3 | **Superseded by P4r4.** It passes under both anchor semantics (RV3-D-A11) and contains a hash-cyclic `A_valid` construction (RV3-M8). It is not a conformance target. |
| `G1-git-occupation-behaviour.{sh,txt}` | 3 | Still valid for pull, checkout and clone behaviour. The untracking idiom is covered by `RV3-D-A05-A07-rerun-r4-layout.json`. |
| `ESCALATION_PROBES.md`, `probe.sh`, `regen.py`, `probe-output.txt` | 1 | escalation probes E1–E5 against 4.1.5; still the reproduction target for RT-72 (ii) |
| `F1-format-boundary-probe.{py,json}` | 2 | **Superseded (R2-L3).** Supports no claim. |
