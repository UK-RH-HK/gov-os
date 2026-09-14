# Evidence — review r7 B (trust and security, AR-0020)

Everything was run in scratch under `<scratchpad>/ar-0020/`, never in the canonical checkout or another worktree.

## Environment and hygiene

- Child processes ran with `env -i`: `PATH=/usr/bin:/bin`, `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` pointed into scratch,
  `PYTHONDONTWRITEBYTECODE=1`, and no `GOV_*` variables.
- Toolchain: Python 3.12.3 with PyYAML, `cryptography` and `jsonschema`; OpenSSL 3.0.13; `rustc 1.98.1` (used by ENV7 only).
- Legacy binaries were read-only; their sha256 values match `rerun/architect-runner-log.tsv`.
- No helper sessions were used. No transcript or task-output file was read.

Paths in the committed files are normalised to `<scratch>`, `<rerun>`, `<worktree>`, `<home>` and `<scratchpad>`.

## Files

| Path | What it is |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | sha256 of every reviewed file: the pack, D-0007, D-0008, ARCH-0002, `docs/DECISIONS.md` and review r6 at `d07d200…`, plus the owner requirements, HO-0020, HO-0001 and `AGENT_RUNS/README.md` at the review base `7e50c6e`. The pack, `spec/` and `docs/` are unchanged between the two commits. |
| `probes/RV7-B-A01-revocation-omission.py` → `outputs/RV7-B-A01.json` | **executed**; architect's reference executor, unmodified: RV7-B-H1, RV7-B-L3 |
| `probes/RV7-B-A01m-executor-mutant.py` → `outputs/RV7-B-A01m.json` | **executed**; a scratch copy of the executor with one mutation (apply every held revocation statement): the executor change alone does not close H1 |
| `probes/RV7-B-A02-c3-currency-stale-state.py` → `outputs/RV7-B-A02.json` | **executed** (part E: `gov_run`, `accept`) and **computed** (part C: BA11r7 source re-evaluated with one assumption replaced): RV7-B-H2 |
| `probes/RV7-B-CS7-extensions.py` → `outputs/RV7-B-CS7.json` | **computed**; the architect's CS7, unmodified and wrapped. The control reproduces the committed CP-REVOKED and CP-FC-ROOT blocks. Extensions A01-VA, A01-VB, A02, A02-FIX, A03: RV7-B-H1, H2, M1 |
| `probes/RV7-B-A04-A05-provenance-labels-and-schema-shapes.py` → `outputs/RV7-B-A04-A05.json` | **executed**; reference executor unmodified, plus jsonschema Draft 2020-12 over `trust-root.schema.json`: RV7-B-L1, RV7-B-L2 |
| `outputs/RV7-B-A08-PROF7-mutation-sensitivity.json` | **executed**; architect's PROF7, unmodified, on a scratch copy of the export with two schema mutations. EX-01 and EX-04 fail; everything else holds. The instrument is load-bearing for those mechanisms. |
| `probes/RV7-B-A09-exclusion-schema-sweep.py` → `outputs/RV7-B-A09.json` | **executed**; sweep of the 28 certified schemas. Excluded-mode identifiers appear only in descriptions, except `framework-lock-3.0.0` `verdict_at_install.freshness`, which is the freshness verdict axis of `24` §4.1, not a witness mode. No external `$ref`. The one object without `additionalProperties: false` is `trust-policy.surface`, validated by the CSI schema. |
| `rerun/run_r7_evidence.adapted.sh` | the architect's `evidence/r7/run/run_r7_evidence.sh` with placeholders filled in and the reviewer-C chain removed (compatibility scope) |
| `rerun/architect-runner-log.tsv` | per instrument: id, exit code, seconds, output sha256 |
| `rerun/dependent-rerun-log.tsv` | REGISTER-CHECK, DA09r7, DA04r7 and EXAMPLES re-run after the cascade (see below) |
| `rerun/COMPARISON.json` | re-run outputs against the committed outputs: byte-identical, or differing JSON leaves (`probes/compare_rerun.py`) |

## Re-run results (68 comparisons)

| Status | Count | Items |
|---|---|---|
| byte-identical | 53 | every revision-7 instrument (CS7 and `CS7-results.json.gz`, FA7 twice, CUR7, ADM7, ENV7, BA11r7, BA12r7, PPR7, DA05r7, DA06r7, STATEMENTS-CHECK, PROF7, REGISTER-CHECK, DA09r7, DA04r7); most retained revision-6 and revision-5 instruments (CSI self-test, P4r6, CS6, DA03r6, FA6, CON6, SRC6, UW6, ATTR6, ENV6, P4r5, DA03r5, FA5, REG5, P1r4, CS5); the review r6 and r5 probe re-runs apart from the rows below |
| differing, run-dependent leaves only | 8 | CSI checks ×5 (`kernel_dir`); ADM6 (unlocked mutant race counts); RV5-B-A05 (time-dependent archive digests); RV5-B-A08 (compiler-dependent image digest) |
| differing, stale committed output | 2 | `r7/retained/DA07r6…on-revision-7-plan.json` (RT-201 row; `plan_rt_rows` 199→202); `r7/r6-probes/RV6-B-A03.json` (S2 `sets_checked` 7→11). No verdict leaf differs (RV7-B-L5). |
| not runnable | 5 | RV6-B-A01 and RV6-D-A08, RV6-D-A09 (withdrawn `first-contact-manifest` schema); RV6-B-A02 (withdrawn manifest v1 field); RV6-D-A05 (withdrawn `21` §17). This matches the architect's `NOT-RUNNABLE.json`; their CP-1 re-expressions (FA7, CUR7, ENV7, DA05r7, DA09r7) were re-run byte-identical. |

**Cascade.** The committed runner's `crashmig7` needs reviewer C's built trees (`c6lib` and `trees2/`) that the runner does not
create. Its empty output made REGISTER-CHECK crash, which made DA09r7 differ and DA04r7 crash. EXAMPLES failed because the runner
copies `examples/rev7` away from `../../schemas`.

- `crashmig7` was not re-run: it is compatibility scope.
- REGISTER-CHECK was re-run with the committed `LAY7/crashmig7.json` as its input (disclosed). REGISTER-CHECK, DA09r7 and DA04r7
  then reproduced the digests in the architect's `EVIDENCE-RUN-LOG-r7.json` byte for byte.
- `make_rev7.py`, run in place, reproduced the logged digest.
