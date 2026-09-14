# 01 — Reproduction (review r4 synthesis D, AR-0008)

HO-0008 §2 (1): re-run every probe behind a HIGH or CRITICAL claim and behind every claim that a prior HIGH is `CLOSED`.

## Method

- **Identity.** At base `9349d8c`: `git diff bca05a7 HEAD` empty for the pack, D-0008 and ARCH-0002; `git diff 152e68e HEAD`
  empty for B's directory; `git diff c6b8ba9 HEAD` empty for C's directory; `git diff da9c851 HEAD` empty for `runtime/`,
  `cli/`, `framework/`, `migrations/`, `capabilities/`, `Cargo.*`, `release/releases/`.
- **Environment.** `env -i PATH=/usr/bin:/bin HOME=<scratch>/home XDG_*=<scratch> PYTHONDONTWRITEBYTECODE=1
  GOV_KERNEL_CACHE=<scratch>/kcache REVIEW_REPO=<worktree>`; C's scripts add `GIT_CONFIG_NOSYSTEM=1` and
  `AR7_WT=<worktree>`, `AR7_LEGACY_BIN=<legacy-bin>` (C's documented overrides; its library strips `GOV_*` from children).
- **Scripts.** `evidence/probes/repro_ab.sh` (architect and B) and `evidence/probes/repro_c.sh` (C), run unmodified
  against the committed scripts. B's surface and confinement probes first failed because their `GOV_REVIEW_SCRATCH`
  directories did not exist; they were re-run with the directories created, with no other change.
- **Comparison.** `cmp` against the committed JSON where outputs are deterministic; normalised comparison (scratch path
  strings only) where outputs embed paths; aggregate comparison for C's 7.5 MB matrix (row count, per layout × position
  write counts, rows writing `governance/trust/**`, state counts, writing commands).
- **Binaries** (read-only): `gov-4.1.2` `dc924fb3…`, `gov-4.1.3` `baba4e40…`, `gov-4.1.4` `85f34cce…`, `gov-4.1.5`
  `9169d7a8…` (full digests in `evidence/REPRODUCTION-LOG.json`).

## Results

| # | Probe (owner) | Behind | Result | Reproduced |
|---|---|---|---|---|
| R01 | CSI `selftest` (architect) | BC-1 closure | 56 passed, 0 failed | yes |
| R02 | CSI `check` framework, 4.1.5, 4.1.2, 4.1.3, 4.1.4 (architect) | exits 0/3/2/2/2 | 0/3/2/2/2 | yes |
| R03 | `P4r4-trust-state-model.py` (architect) | BC-2 closure; RV3-M1/M3/M4/M8 | `cmp` 0 | yes |
| R04 | `VA4-verify-artifact-source-scenarios.py` (architect) | BC-3 closure; route B row | `cmp` 0 | yes |
| R05 | `P1r4-project-strength-and-absence.py`, real 4.1.5 (architect) | BC-1 closure; RV3-M5 | `cmp` 0 | yes |
| R06 | `RV4-B-M-reference-model.py` (B) | RV4-B-H1, H2, M2, M3, L2–L4; matrix; review-r3 constructions 18/18 | `cmp` 0 | yes |
| R07 | `RV4-B-arch-functions.py` (B) | RV4-B-H1 (AF1, AF2), RV4-B-H2 (AF3) | `cmp` 0 | yes |
| R08 | `RV4-B-surface-probes.py`, real 4.1.5 (B) | RV4-B-H3 (P), L1 (U), A10 (T) | `cmp` 0 | yes |
| R09 | `RV4-B-confinement-and-first-binary.py`, real 4.1.5 (B) | RV4-B-H2 part B, M1 part A | `cmp` 0 | yes |
| R10 | B's `r3-probe-copies/RV3-B-A01-precedence-immutable.py`, real 4.1.5 | RV3-H1 `CLOSED` (exit 3) | identical | yes |
| R11 | B's `RV3-B-A03-A14-A16-probes.py`, real 4.1.5 | RV3-M2 narrowed; L2, L3 | identical except one scratch path string | yes |
| R12 | B's `RV3-B-CSI-injections.py` | default deny | identical | yes |
| R13 | B's `r2rerun-P2-gate-record-forgery.py`, real 4.1.4/4.1.5 | repository records as requests (legacy behaviour) | identical except the scratch path | yes |
| R14 | B's `RV3-D-precedence-lattice.py` | order sound both directions | identical | yes |
| R15 | B's `RV3-D-surface-forward-compat-and-removal.py` | removals refused; forward compatibility | identical | yes |
| R16 | C `build_trees.py` (real 4.1.5 base project; R4, R4RES, R4APP) | base trees | exit 0 | yes |
| R17 | C `subdir_escape.py`, real 4.1.5 | **RV4-C-H1** | identical JSON | yes |
| R18 | C `durability.py`, real Git | RV4-C-M1; durability | identical JSON | yes |
| R19 | C `legacy_regain.py`, real 4.1.5 and Git | LR-2 bound | identical JSON | yes |
| R20 | C `matrix.py`, real 4.1.2–4.1.5 (10,618 invocations, 168 chains, 16 workers) | **RV4-C-H1**; `--root` property; R2-H4 | 10,618 rows; every aggregate identical (below) | yes |

### R20 aggregates (reproduced = committed)

| Layout / position | rows | rows writing the work tree |
|---|---:|---:|
| R4 `P-ROOT` | 966 | 0 |
| R4RES `P-ROOT` | 966 | 0 |
| R4APP `P-ROOT` | 572 | 0 |
| R4 `P-CWD:product` | 1,572 | 168 |
| R4 `P-CWD:spec`, `governance/overlay`, `governance/views`, `governance/trust`, `governance/trust/state`, `governance/framework.lock` | 572 each | 28 each |
| R4 `P-CWD:.`, `P-CWD:.governance-runtime` | 1,572; 572 | 0 |
| L0 control | 966 | 245 |

Rows writing under `governance/trust/**`: 56. Installation states: R4 `COMPLETE` 8,114; R4RES 966; R4APP 572; L0 `LEGACY`
966. Writing commands: `init` variants, `adopt baseline`, `migrate baseline`, and on L0 the ordinary mutating commands.

## Not re-run, and why

| Probe | Reason |
|---|---|
| Architect's P3r3 (2,085 jobs) and LR2 | The claims they support (the `--root` property; state machine on review-r3 trees) are independently reproduced by C's matrix (R20) and by D-A01's use of the LR2 functions. |
| Architect's re-runs of review-r3 C and D legacy probes | superseded by C's independent probes (R17–R20) on the revision-4 layout |
