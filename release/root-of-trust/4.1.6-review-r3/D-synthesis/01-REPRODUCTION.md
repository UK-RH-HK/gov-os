# 01 — Reproduction of the panel's decisive probes (AR-0004)

HO-0004 §2.1 requires re-running every probe behind a HIGH or CRITICAL claim and every probe behind a claim that a prior
HIGH is `CLOSED`. This review re-ran those and every other executable probe the panel and the architect committed.

## Method

- **Where.**
  - Scratch root: `ar-0004/repro/`.
  - The worktree was only read. `git status --porcelain --ignored` was empty after every run.
- **Environment.**
  - `env -i PATH=/usr/bin:/bin`, so no `GOV_*` variable reached any child.
  - `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` pointed into scratch, either by this review or by the probe itself.
  - `PYTHONDONTWRITEBYTECODE=1`.
- **Binaries.** The legacy binaries were used read-only.

  | Binary | SHA-256 |
  |---|---|
  | 4.1.2 | `dc924fb3…74a767b7` |
  | 4.1.3 | `baba4e40…b7d0fd89` |
  | 4.1.4 | `85f34cce…5b67f` |
  | 4.1.5 | `9169d7a8…1de915` |

  Full digests: `evidence/REPRODUCTION-LOG.json`.
- **Scripts.** B's and the architect's scripts ran unmodified from this worktree.
  - `REVIEW_REPO` and `P3_REPO` were set to this worktree.
  - `GOV_REVIEW_SCRATCH` and the P3r3 scratch argument pointed into scratch.
- **C's scripts.** They hard-code reviewer C's worktree in `lib.py` (`REPO`). They were copied to scratch, and only that constant was set to this worktree.
  - `build_base.py` refuses an existing scratch directory. The first attempt therefore failed before any probe ran, and the chain was re-run in a fresh directory.
- **Comparison.**
  - Byte comparison where outputs are deterministic.
  - Otherwise, JSON equality after replacing scratch paths, 16-hex tree digests and 40-hex commit ids with placeholders.

## Results

| # | Probe | Owner | Behind claim | Command (abbreviated) | Result |
|---|---|---|---|---|---|
| 1 | P4r3 trust-state model | architect | pack closures R2-M2…M6; B's `CLOSED` R2-M4, R2-M6 | `python3 4.1.6/evidence/P4r3-trust-state-model.py` | **reproduced**, byte-identical (34/34 agree) |
| 2 | P1r3 floor coverage, real 4.1.5 | architect | R2-H1 narrowing (harm flips) | `GOV=gov-4.1.5 python3 4.1.6/evidence/P1r3-floor-coverage.py` | **reproduced**, byte-identical |
| 3 | P3r3 pre-RoT register matrix, real 4.1.2–4.1.5 | architect | R2-H4 closure (LP-1); R2-L3 `CLOSED` | `P3r3-pre-rot-register-matrix.py <scratch> --workers 8` (88 s) | **reproduced**: `summary`, `property_L3` (695 invocations, 40 chains, 0 violations), `chain_summary`, `job_count` 2085 equal. The only difference is the committed file's compacted `registers` entries (3 keys vs 2 per binary). |
| 4 | CSI checker `check` and `selftest` | architect | R2-H1 default deny | `csi_check.py check framework/`, 4.1.5, 4.1.2, 4.1.3, 4.1.4; `selftest` | **reproduced**: exits 0, 0, 2, 3, 3; self-test 26 passed, 0 failed |
| 5 | RV3-B-M reference model | B | **RV3-B-H2**, **RV3-B-H3** (A08), M1, M3, M4, L1 | `python3 B/evidence/RV3-B-M-reference-model.py` | **reproduced**, byte-identical (132-row matrix: R7 C2 policy root in 90 rows, C3 in 86) |
| 6 | r2 P4 under revision-2 rules | B (copy of r2) | r2 B1–B6 `agrees: false` under revision 2 | `python3 B/evidence/r2rerun-P4-trust-state-model.py` | **reproduced**, byte-identical |
| 7 | RV3-B-A01 precedence to `immutable` | B | **RV3-B-H1** | `GOV=gov-4.1.5 python3 B/evidence/RV3-B-A01-precedence-immutable.py` | **reproduced**, 0 differences. Checker exit 0. On 4.1.5: resume `AUTHORITY_DENIED` → ok; confidential file excluded → indexed and retrievable; R1 gate `AUTHORITY_DENIED` → ok. Overlay identical. |
| 8 | RV3-B-A03/A14/A16 | B | M2, L2, L3 | `python3 B/evidence/RV3-B-A03-A14-A16-probes.py` | **reproduced**, 0 differences |
| 9 | RV3-B CSI injections I01–I09 | B | default deny; M5 (I08) | `python3 B/evidence/RV3-B-CSI-injections.py` | **reproduced**, 0 differences |
| 10 | r2 P2 gate-record forgery, real 4.1.5 | B (copy of r2) | R2-M1 on the unchanged implementation | `python3 B/evidence/r2rerun-P2-gate-record-forgery.py` | **reproduced**: control `applied: false`; forged record `applied: true` |
| 11 | C destructive register (84 invocations × 4 real binaries) | C | R2-H4 `NARROWED` (LP-1) | `build_base.py`; `run_destructive.py` | **reproduced**, 0 differences (0 writes, 0 classification lost) |
| 12 | C partial occupation removal | C | C-1 (A04) | `occ_removal.py` | **reproduced**, 0 differences |
| 13 | C full removal and dir/file merge | C | C-1 (A05); A03 | `full_removal_and_merge.py` | **reproduced**, 0 differences (legacy `init --force` ok, `verified: true`, restricted retrievable, `governance/trust` unchanged) |
| 14 | C durability | C | A02, A06, A09 | `durability.py` | **reproduced**, 0 differences |

**Not re-executable** (no RoT-1 binary exists): spec-only mechanisms VU-11, VU-12, the union trust record, foreign
journals, terminal confirmation, the strength vector and the consumer register. B, C and the architect label them spec-only; this review
agrees.

**Architect G1** (Git occupation behaviour) was not re-run. C's durability probe (row 14) and this review's D-A05 and
D-A07 exercise the same Git behaviour with real commands.

## Identity of the reviewed content

`evidence/REVIEWED-CONTENT-DIGESTS.txt` lists 188 files with SHA-256 and Git blob ids, at this review's base and at their origin commits:
- the pack, D-0007, D-0008, ARCH-0002 and `docs/DECISIONS.md` at `ca77a43`;
- B at `7d8c73a`;
- C at `9e013c1`;
- review r2 at `e5a6b8a`;
- the handoffs and README at base.

Every blob is identical to its origin commit. The implementation paths (`runtime`, `cli`, `framework`, `migrations`, `capabilities`, `Cargo.*`, `release/releases`) are unchanged since `da9c851`.
