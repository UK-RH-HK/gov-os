# 00 — Independent compatibility & transaction review (C) of RoT-1 revision 5

| | |
|---|---|
| Run | AR-0013, role `rot-reviewer-compat-transaction` |
| Reviewed | RoT-1 revision 5, commit `cdb4e14009bba60bea9b805563c1b60e84f30b4b` (`release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md`) |
| Rejected prior | revision 4 `bca05a7`; consolidated review r4 `97a5545` (synthesis adjudication governs over its panel) |
| Handoff | `HO-0013`; owner requirement `HO-0001` §3.4 |
| **Verdict** | **`NO_BLOCKING_FINDINGS`** |

## Independence

This session authored no RoT-1 revision, no specialist proposal, no prior review, and did not read reviewer B's output,
the other panel review, other branches, other worktrees or other scratch directories (`git branch -a`, `git log --all`,
sibling scratch dirs were not used). Under `release/orchestration/` I read only `HO-0013`, `HO-0001` and
`AGENT_RUNS/README.md`. The architect's response matrix (`22`), `28`, the ST5 subdirectory matrix, the P3r3 re-run, FA5,
REG5, CS5 and every pack evidence file were treated as **claims to test**, not findings. No scope deviation.

## Hygiene

All probes ran in scratch under `env -i` with `GOV_*` stripped from every child (`GOV_KERNEL_CACHE` pointed into
scratch; `GOV_*` env-var probes set the variable under test explicitly as the object of the test). `HOME`, `XDG_*` into
scratch; `GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0`, `PYTHONDONTWRITEBYTECODE=1`, `core.hooksPath=/dev/null`. The
canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS` and every other worktree were never written. Whole-tree
snapshots record **every** entry (work tree, `.governance-runtime/`, `.git/`, the child `HOME`, the kernel cache) by
type, mode, size and SHA-256, partitioned so no write is hidden by a named-path choice; each matrix row records a
before/after tree digest of the entire tree, never a named path. Legacy binaries are the real
`gov-4.1.{2,3,4,5}` (SHA-256 in `evidence/REVIEWED-CONTENT-DIGESTS.txt`), used read-only. No forced deletes.

## Method

Compatibility and transactions (Phase 1 protocol §5 C; `HO-0013` §2–§6). All instruments are original to AR-0013; the
installation-state predicate `c5lib.state_r5` is **encoded from the text of `18` §9, §9.1 and §9.2 at `cdb4e14`** and does
not import the architect's `ST5-installation-state-r5.py` or review r4 C's `c4lib.installation_state`. The `18` §6.1
`KERNEL_TAMPERED` check compares the installed kernel tree against the release content set (`RCS(D)`) computed by the
builder from the signed kernel, not from the unsigned lock.

- **Independent registers** (`register5.py`): each legacy binary's full command register derived two ways — from its own
  `--help` recursion **and** from its own source (`cli/src/main.rs` clap enums at `8ad06be`/`26ab5b6`/`47d8394`/`da9c851`)
  — and cross-checked: 4.1.2 = 104 leaf commands, 4.1.3 = 109, 4.1.4 = 115, 4.1.5 = 119; `in_help_not_source` and
  `in_source_not_help` empty for all four; paths and option counts equal to review r4 C's independently-derived register.
- **Revision-5 trees** (`build5.py`): a real legacy project built by the real 4.1.5 binary (init 4.1.4 → gated update to
  4.1.5, legacy update snapshot retained → **two** `restricted` classifications added **after** the update → task, gate,
  CIT, handoff, lesson packet, plugin, tool descriptor, adapters, memory index), migrated to the revision-5 layout
  (`26` §2, `08` §2–§3: lock 3.0.0 records the release content set `kernel.files` and the registration digest;
  `registration.dsse.json` in the trust entry set; `26` §8 `.gitignore` surgery; `26` §7 quarantine). Trees: **R5**
  (surgery), **R5RES** (second machine, legacy update snapshot present, no transaction area), **R5NOSURG** (rules
  appended, legacy line kept — negative control for RV4-M6), **R5V** (a committed legacy 4.1.5 sub-project at
  `vendor/legacypkg`), **L0** (control).
- **Independent pre-RoT matrix** (`matrix5.py`): every mutating command family (`init`, `adopt baseline`,
  `migrate baseline` and their combos) plus a 21-command control sample of non-mutating commands, from each real
  4.1.2–4.1.5 binary, run against fresh copies of the trees in positions `--root` (LP-1r), no-`--root` from 24 working
  directories including inside the PPS and the transaction area (P-CWD), inside/above a nested legacy sub-project
  (P-VEND), with six user-environment-variable sets × three directories (P-ENV), and on 18 trees produced by ordinary Git
  operations × two positions (P-GIT). **30,165 executed rows** (285 skipped for absent cwd) + **1,335** `--root` rows;
  before/after whole-tree digests and `18` §9/§9.1 state before and after each row.
- **Layout durability** (`gitops5.py`, real Git 2.43): fresh/shallow/partial clone, `git archive`, `git clean -fdx`,
  stash `-u`, cone and non-cone sparse checkout, checkout-across-migration, `git worktree add`, checkout of the
  pre-migration commit, `git restore --source <pre> -- governance`, the untracking idiom on R5 and R5NOSURG, a user
  `core.excludesFile` carrying `.governance-runtime/`, `.git/info/exclude` carrying it, and `core.autocrlf=true` /
  `* text=auto`+`core.eol=crlf` Windows checkouts.
- **Transaction & admission state** (`admit_tx.py`): crash between install-from-buffer and record-write; gov-admit re-run
  on a provisioned machine; rollback to a previously admitted binary; concurrent admissions — against the pack's own
  reference executor `evidence/r5/gov_admit_reference.py`, testing its transactional properties.
- **Reproduction** of the prior decisive probes against revision 5 as written (`repro_prior.sh`): review r4 C
  `subdir_escape`, `durability`, `legacy_regain`; review r4 D `RV4-D-A01`; the architect's ST5 subdir-escape, gitignore
  surgery, subdir matrix, D-A01 re-run; P3r3; and review r4 C's 10,618-invocation matrix.

## Reproduction of prior decisive probes (`evidence/reproduction/REPRODUCTION.json`)

| Probe (owner) | Behind | Reproduced on revision 5 |
|---|---|---|
| review r4 C `subdir_escape`, `durability`, `legacy_regain` | RV4-C-H1/M1, LR-2 | **byte-identical** |
| architect ST5 `subdir-escape`, `gitignore-surgery`, `D-A01-rerun`, `subdir-matrix-writing-rows` | RV4-M1/M6 closure | **byte-identical** |
| architect ST5 `subdir-matrix-summary` | RV4-M1 closure | identical except `elapsed_seconds` |
| review r4 D `RV4-D-A01` | RV4-M1 re-rating | identical on every substantive field (states, `KERNEL_TAMPERED`, strength); differs only in run-specific record ids (`CKPT-…`, `D-0001`) the legacy binary generates |
| architect P3r3 (2,085 jobs) | LP-1r | `summary`, `property_L3`, `chain_summary`, `job_count` equal to committed |
| review r4 C matrix (10,618 invocations, 168 chains) | RV4-C-H1, `--root` property, R2-H4 | 10,618 rows; writes-by-layout×position, states, 56 trust rows and writing commands all equal to committed |

## Summary of results

- **LP-1r holds and is independently reproduced.** Across 1,335 `--root` invocations on R5, R5RES, R5NOSURG and R5V,
  **no pre-RoT binary writes a byte to the work tree, `.governance-runtime/` or `.git`**; the classifications survive.
  The 4.1.2–4.1.5 registers reproduce review r4 C's aggregates byte-for-byte.
- **R2-H4 is CLOSED as a class, confirmed independently.** Across the whole 30,165-row matrix, **0 rows** in which a
  pre-RoT invocation changed a byte under `governance/trust/**` or an occupation entry and the revision-5 installation
  state was left `COMPLETE` (with no `KERNEL_TAMPERED`). The revision-5 closed-entry-set predicate (`18` §9.1) turns every
  such write into `PARTIAL(foreign_trust_entry | kernel_content_mismatch | occupation | nested_legacy_install)`; a
  nested-root legacy CIT that edits the installed kernel is `KERNEL_TAMPERED`. Environment variables (`GOV_KERNEL_SOURCE`,
  `GOV_CANONICAL_ROOT`, `GOV_PLUGINS_DIR`, `GOV_ROLE`, …) open no new hole: all 144 env-var rows that wrote the PPS are
  `PARTIAL`. RV4-M1's subdirectory escape is closed.
- **RV4-M6 (.gitignore) holds against the project `.gitignore`.** The `26` §8 surgery is idempotent; R5 → clone
  `COMPLETE` with the idiom listing nothing; R5NOSURG (legacy line kept) → clone `PARTIAL(occupation)` (fail closed).
- **No blocking finding.** Every gap found is either fail-closed (the RoT-1 binary refuses: `PARTIAL`/`LEGACY`/
  `KERNEL_TAMPERED`) or inert (litter that no trust decision consumes and that doctor reports). Details in
  `01-FINDINGS.md`. Five carried/low items, none needing a trust-relationship change:
  - **RV5-C-M1** — no `.gitattributes` ships; a `core.autocrlf=true` or `* text=auto`+`core.eol=crlf` (Windows) clone
    line-ending-converts the kernel bytes, so the machine is `KERNEL_TAMPERED`/`PARTIAL` and the project is unusable
    there (fail closed).
  - **RV5-C-M2** — the `26` §8 surgery reaches only the project `.gitignore`; a user `core.excludesFile` or
    `.git/info/exclude` carrying `.governance-runtime/` re-drops the migration occupation under the untracking idiom, so
    later clones are `PARTIAL(occupation)` (fail closed).
  - **RV5-C-L1** — `26` §4's LP-1s prose ("every write under `governance/**` other than the overlay files leaves a state
    that is not `COMPLETE`") overclaims: subtree `adopt baseline`/`migrate baseline` write `governance/spec/…` and
    `governance/views/spec/…` litter and the state stays `COMPLETE` (16 rows; inert, not read as trust).
  - **RV5-C-L2** — `18` §9.2's cwd-refusal set and `18` §9.1's closed-entry-set omit the transaction area
    `.governance-runtime/trust-tx/**`, though `18` §8 lists it in the PPS; a legacy `init` from inside it leaves
    `COMPLETE` with a reported (`NESTED_LEGACY_PROJECT`, D039) nested install; `gov recover`'s VTS-registration gate
    (`18` §5.1) makes it inert.
  - **RV5-C-L3** — gov-admit's "first admission" is not defined operationally; the reference discards the monotonic
    verifier trust store (clock high-water, anchors, per-project records) on any run where the store exists, and
    R-ADM-7's "record beside the binary" contradicts the reference's in-store placement (transactional-state clarity).

## Prior-finding status (`HO-0013` §3)

| Prior finding | Status | Basis |
|---|---|---|
| **R2-H4** pre-RoT binaries damage RoT-1 projects | **CLOSED as a class** | 30,165-row independent matrix: 0 rows leave `COMPLETE` after a `governance/trust/**` or occupation change without `KERNEL_TAMPERED`; LP-1r 1,335 rows 0 writes; `18` §9.1 closed entry sets. HO-0001 §3.4 property holds. |
| **RV4-M1** subdirectory escape / nested installs / `COMPLETE` examines no foreign entry | **CLOSED** for `governance/trust/**` and the occupation (§9.1 + §9.2); **NARROWED** residual → RV5-C-L2 (the transaction area is not in the closure) | matrix5 `R2-H4` and `nested_marker` properties; ST5 reproduced |
| **RV4-M6** retained `.gitignore` line / untracking idiom | **CLOSED** against the project `.gitignore`; **NARROWED** → RV5-C-M2 (global excludes / `.git/info/exclude`) | `gitops.json` UNTRACK_R5 vs UNTRACK_NOSURG vs GLOBALEXCL/INFOEXCL |
| **C-2** cross-device tx refusal; unanchored `PARTIAL` repairable | **Carried — spec only** (`18` §3, `20` §8; RoT-1 tx unimplemented) | design |
| **C-3** doctor names stray merge/partial-removal artefacts | **Carried — spec only**; scope must add `governance/spec` and the transaction area (RV5-C-L1/L2) | `18` §9 D033/D039 |
| **C-4** occupation type by `st_mode`, not name | **Carried — spec only; model consistent** (`18` §3, §9.1 preamble, symlink refusal) | design |
| **C-5** full-register RT-50 on a genuine install | **Carried — spec only**; my matrix is the independent analogue on a built layout | `12` RT-50, RT-144 |
| **C-6** doctor names nested lock / sparse | **Carried — spec only**; SPARSE_CONE/NONCONE → `PARTIAL(occupation)` reproduced | `gitops.json` |
| **RV4-M2** (transaction part): confinement deny→allow; journals honoured only if VTS-registered | **Carried — spec only**; the VTS-registration gate (`18` §5.1) is what makes RV5-C-L2 inert | design |
| **RV4-M5** (transaction part): computed weakening needs a recorded vector; fresh clone | **Carried — spec only** (`19` §9 item 5 added: requirements from pre-transaction inputs) | design |

**Verdict: `NO_BLOCKING_FINDINGS`** — a role verdict, not the architecture verdict; the synthesis reviewer issues that.
Findings in `01-FINDINGS.md`; held-out register `RV5-C-A01…A13` in `02-HELDOUT-ATTACKS.md`; residuals in
`03-RESIDUALS.md`; carried requirements in `04-CARRIED-REQUIREMENTS.md`; executed matrix in `05-PRE-ROT-MATRIX.md`.
