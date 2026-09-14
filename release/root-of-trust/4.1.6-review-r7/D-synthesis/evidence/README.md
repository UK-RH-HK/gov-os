# Evidence — synthesis reviewer D (AR-0022)

Everything was run in scratch under `<scratchpad>/ar-0022/`, never in the canonical checkout or another worktree.

## Environment and hygiene

- The inputs were exported with `git archive d07d200` into scratch; reviewer B's and C's directories were copied from the review
  base (identical to `54be694` and `34633cc`: `git diff --quiet`). Legacy binaries were copied read-only (sha256 in
  `REVIEWED-CONTENT-DIGESTS.txt`).
- Child processes ran under `env -i` with `PATH=/usr/bin:/bin`, `HOME`, `TMPDIR`, `XDG_*` and `GOV_KERNEL_CACHE` in scratch,
  `PYTHONDONTWRITEBYTECODE=1`, Git with `GIT_CONFIG_NOSYSTEM=1`, and no `GOV_*` variable except where reviewer C's matrix sets one
  as the object of a test (its P-ENV rows). ENV7 and RV7-D-A02 use the real `rustc 1.98.1` from the account toolchain
  (`RUSTUP_HOME`, `CARGO_HOME` passed explicitly).
- Toolchain: Python 3.12.3 with PyYAML, `cryptography` 41.0.7 and `jsonschema` 4.10.3; OpenSSL 3.0.13; Git 2.43.0; `rustc 1.98.1`;
  `cc` 13.3.0.
- No helper sessions were used. No transcript, task-output file or harness tool-result file was read.
- Paths in committed files are normalised to `<scratch>`, `<worktree>` and `<home>`.

## Files

| Path | What it is |
|---|---|
| `REVIEWED-CONTENT-DIGESTS.txt` | sha256 of every reviewed Git blob: the pack, D-0007, D-0008, ARCH-0002 and `docs/DECISIONS.md` at `d07d200`; reviewer B at `54be694`; reviewer C at `34633cc`; the orchestration files read at `1d4d9f3` (HO-0022, HO-0001, `AGENT_RUNS/README.md`, both owner records and their indexes); the review r6 consolidated files read at `ab6b1f8`; the four legacy binaries |
| `run/run_arch.sh` | re-run of the architect's revision-7 instruments and the retained CSI checks (adapted from `evidence/r7/run/run_r7_evidence.sh`; outputs to scratch, never into the pack) |
| `run/run_B.sh` | re-run of reviewer B's six probes, unmodified copies |
| `run/run_C.sh`, `run/run_matrix7.sh` | re-run of reviewer C's revision-7 chain (`register7`, `build7`, `struct7`, `gitops7`, `txn7`, then `matrix7` with 16 workers), unmodified copies; `cur7x`, `adm7x`, `design7`, `ident7` were run directly (`reproduction/reviewer-C-direct-log.tsv`) |
| `run/run_matrix7_ptxn.sh` | the P-TXN positions of `matrix7` re-run alone over resolved paths (see Disclosures) |
| `run/run_D_bg.sh` | the two long held-out probes (A02, A06) |
| `run/compare_all.py`, `run/cmpjson.py`, `run/compare_matrix7.py` | the comparison of every re-run output with the committed output (`AR0022_SCRATCH` names the scratch root) |
| `reproduction/*.tsv` | per-run exit code, seconds and output sha256 |
| `reproduction/REPRODUCTION-COMPARISON.json` | the comparison result (byte-identical, run-dependent leaves, or differing verdict leaves) |
| `reproduction/MATRIX7-COMPARISON.json` | the composed `matrix7` re-run (full run without P-TXN, plus the P-TXN run) against the committed summary |
| `reproduction/matrix7-summary.full-run.json`, `reproduction/matrix7-summary.p-txn-run.json` | this review's two `matrix7` summaries |
| `probes/RV7-D-A01-omission-class-extension.py` → `outputs/RV7-D-A01.json` | **E**, reference executor unmodified: admitter revocation and security-relevant registration omitted by daily Trust States (RV7-H1) |
| `probes/RV7-D-A02-cross-axis-reproduction.py` → `outputs/RV7-D-A02.json` | **E** reference executor; **E** real `rustc 1.98.1` builds in four combinations; **C** CS7 unmodified and wrapped (RV7-M3) |
| `probes/RV7-D-A03-toolchain-two-distributions.py` → `outputs/RV7-D-A03.json` | **E**, reference executor unmodified; code, schema and label facts (RV7-M2) |
| `probes/RV7-D-A04-design-extractions.py` → `outputs/RV7-D-A04.json` | **D**, mechanical line extraction and absence checks at `d07d200`; decision-record state (RV7-M4, RV7-L10, RV7-I3, A10, and support for H1, H2, M3) |
| `probes/RV7-D-A05-clock-reset-replay.py` → `outputs/RV7-D-A05.json` | **E** on the retained P4r4 model, unmodified (RV7-L9) |
| `probes/RV7-D-A06-vector-mutation-sensitivity.py` → `outputs/RV7-D-A06.json` | **E**, 22 code-level mutants of a scratch copy of the executor, each against FA7, CUR7, ADM7 and PROF7 unmodified (RV7-M10) |
| `probes/RV7-D-A07-forward-compat-capability-and-artifact-flow.py` → `outputs/RV7-D-A07.json` | **E**, the pack's CSI checker and deriver on scratch kernels (RV7-L11) |

## Probe environment variables

| Probe | Variables |
|---|---|
| A01, A03, A05 | `PACK` (the exported `release/root-of-trust/4.1.6`), `A01_SCRATCH` / `A03_SCRATCH` |
| A02 | `PACK`, `A02_SCRATCH`, `RUSTC`, `RUSTUP_HOME`, `CARGO_HOME` |
| A04, A06, A07 | positional: the export root (and a scratch directory for A06, A07) |

## Disclosures

- **`matrix7` P-TXN positions.** `txn7.py` writes its JSON with the scratch prefix scrubbed to `<ar21>`; the first full `matrix7`
  run read that file and every P-TXN row (25 trees × 524 invocations = 13,100 rows) recorded `HARNESS_ERROR`
  (`FileNotFoundError`), while every other position ran. The P-TXN positions were re-run alone (`--only P-TXN`) with `<ar21>`
  resolved to the scratch root (`run/run_matrix7_ptxn.sh`); `run/compare_matrix7.py` composes the two runs and compares them with
  the committed summary (`reproduction/MATRIX7-COMPARISON.json`). The probes themselves were not modified.

- The first A07 run failed in its K4 part (the deriver expects `../tools/registry/TOOLS.yaml` beside the kernel) and A02's first run
  compared set renderings without canonical atom order; both probes were corrected and re-run from fresh scratch directories. The
  committed outputs are the corrected runs; no verdict of K1–K3 or of A02 parts E and R changed.
- The A04 absence checks were first run with a case-insensitive `CI` pattern that matched inside words; the pattern was made
  word-bounded and case-sensitive before the committed run.
