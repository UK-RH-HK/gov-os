# Evidence — specialist A (AR-0009)

**Scratch only.**
- **Repository.** Read, never written, except this output directory.
- **Probes.** Ran under `env -i` in `…/scratchpad/ar-0009/`, with `HOME`, `XDG_*` (E0) and `GOV_KERNEL_CACHE` in scratch,
  `PYTHONDONTWRITEBYTECODE=1`, and no other `GOV_*` in any child.
- **Legacy binaries.** Used read-only; SHA-256 in `outputs/E0-baseline-LOG.txt`.
- **Committed outputs.** Absolute scratch paths are replaced by `<scratch>`, `<worktree>`, `<legacy-bin>`, `<evidence>` or
  `<scratchpad-path>`.

## Files

| File | Class | What it establishes | Key result |
|---|---|---|---|
| `E0-baseline-reproduction.sh` → `outputs/E0-baseline-LOG.txt`, `outputs/E0-baseline-summary.json` | executed / computed (unmodified committed scripts) | revision 4 identical at base; the retained instruments and the r3/r4 blocking probes reproduce, so each attack exists at base | selftest 56/56; checks exit 0 and 3; P4r4, VA4, P1r4, B model, B AF1–AF3, B surface, B first-binary, D-A02: `cmp` 0; r3 A01, lattice and removal identical after normalisation |
| `E1-selector-audit.py` → `outputs/E1-selector-audit.json` | design-encoded | SEL-1 over 61 decision rows (r1 6, r2 8, r3 9, r4 20, SAM 18) | every HIGH row flagged (18 rows, 14 findings); MEDIUM/LOW rows 10/10 flagged; sound mechanisms 0/12 flagged; SAM 0 unlabelled violations |
| `E2-tcb-capability-sets.py` → `outputs/E2-tcb-capability-sets.json` | computed (symbolic) | minimal capability sets for malicious bytes, source, named inputs and mirror, under revision 4, the literal CD4-1 closure (RID) and SAM | r4 {ba, pipeline} (= reviewer B); r4/RID {pipeline} for named inputs and {input_mirror} for a poisoned mirror, under stated readings; SAM: no row accepts with fewer than 2 keys except TA-12 (64 rows); reproductions submitted through the pipeline give {pipeline, 2 reproducer keys} |
| `gov_accept_reference.py` | prototype | the independent first-binary executor: typed fingerprint + measured bytes + statements; OpenSSL Ed25519; never executes the candidate; KS-7; installation predicate | used by E3 |
| `E3-first-binary-acceptance.py` → `outputs/E3-first-binary-acceptance.json` | executed (real Ed25519, deterministic toy lineage; legacy 4.1.5 for the Phase 4 register) | FB1, FB2, planted binary, Phase 4, ceremony order, 8 new attacks, 16 conformance vectors, 13 mutants; revision-4 paths (b) and (c) as controls | SAM refuses FB1a/b, FB2a/b, FB3; r4 path (b) `PASS` on FB1a and FB2a; path (c) `PASS` on the planted binary; 0 candidate executions; 16/16 vectors; 12/13 mutants plus 1 equivalent; two runs identical |
| `E4-release-scoped-registration.py` → `outputs/E4-release-scoped-registration.json` | executed (pack checker unmodified; real 4.1.5 consumption) | exact per-release registration vs revision 4 retention, open ranges, union and latest; B part P and D-A02 T1–T4; history rules; migrations; owner binding groups; additive members | revision 4 mixed exit 0 and secret indexed; SAM closed exit 3 and secret excluded; T1–T4 exit 3; retention 4.1.6 exit 0; only the closed rule meets 6/6; reversion and rewrite detected |

## Running

```sh
W=<worktree>; S=<fresh scratch dir>; LEG=<dir with gov-4.1.2 … gov-4.1.5>
EV=$W/release/root-of-trust/4.1.6-alternatives-r5/specialist-a/evidence
env -i PATH=/usr/bin:/bin HOME=$S/home AR9_SCRATCH=$S AR9_WORKTREE=$W AR9_LEGACY_BIN=$LEG bash $EV/E0-baseline-reproduction.sh
E="env -i PATH=/usr/bin:/bin HOME=$S/home PYTHONDONTWRITEBYTECODE=1"
$E python3 -B $EV/E1-selector-audit.py > E1.json
$E python3 -B $EV/E2-tcb-capability-sets.py > E2.json
$E GOV=$LEG/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/e3 python3 -B $EV/E3-first-binary-acceptance.py > E3.json      # needs python3-cryptography (signing) and openssl
$E REVIEW_REPO=$W GOV=$LEG/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/e4 python3 -B $EV/E4-release-scoped-registration.py > E4.json   # needs PyYAML
```

- **Directories.** Create `$S/e3` and `$S/e4` first.
- **Determinism.** E1, E2 and E3 are deterministic; E3 was run twice and compared equal with `cmp`.
- **E4.** Its checker exits and verdicts are deterministic; its consumption rows run the real binary.
