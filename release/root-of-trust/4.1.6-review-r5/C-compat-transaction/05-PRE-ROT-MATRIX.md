# 05 — Pre-RoT command-register matrix (executed, independent)

## Registers (derived twice, independently, and cross-checked)

`register5.py` derives each legacy binary's full command register both from its own `--help` recursion **and** from its
own source (`cli/src/main.rs` clap enums at the release commit), and cross-checks them. SHA-256 in
`evidence/REVIEWED-CONTENT-DIGESTS.txt`.

| Binary | Commit | Leaf commands (help) | Leaf commands (source) | `in_help_not_source` | `in_source_not_help` |
|---|---|---:|---:|---|---|
| gov-4.1.2 | `8ad06be` | 104 | 104 | [] | [] |
| gov-4.1.3 | `26ab5b6` | 109 | 109 | [] | [] |
| gov-4.1.4 | `47d8394` | 115 | 115 | [] | [] |
| gov-4.1.5 | `da9c851` | 119 | 119 | [] | [] |

Paths and option counts equal review r4 C's independently-derived register (`registers.json`): 4.1.2 118 options, 4.1.3
129, 4.1.4 133, 4.1.5 134. The two `current_dir()`-rooted, non-`require_installed` families are exactly `init`
(all forms), `adopt baseline` and `migrate baseline` (`cli/src/main.rs` lines 729, 747 at `da9c851`; unchanged across
`8ad06be`/`26ab5b6`/`47d8394`).

## Base project and revision-5 layout (`build5.py`)

A real legacy project built by the real 4.1.5 binary: `init --source 4.1.4` → gated update to 4.1.5 (legacy update
snapshot at `.governance-runtime/update/4.1.5/`) → **two** `restricted` classifications added **after** the update
(`product/restricted-plan.md`, `product/customers/**`) → realistic prior state (task, gate, CIT, handoff, lesson packet,
registered plugin, tool descriptor, memory index, adapters). Migrated to the revision-5 layout (`26` §2, `08` §2–§3:
lock 3.0.0 records the release content set `kernel.files` and the registration digest; `registration.dsse.json` joins the
trust entry set; `26` §8 `.gitignore` surgery; `26` §7 quarantine). Trees: **R5** (surgery, transaction area present),
**R5RES** (second machine; legacy update snapshot present; no transaction area), **R5NOSURG** (rules appended, legacy line
kept — negative control), **R5V** (committed legacy 4.1.5 sub-project at `vendor/legacypkg`), **L0** (legacy control). All
four RoT-1 trees are `COMPLETE` under `18` §9.1; L0 is `LEGACY`; R5V additionally reports `NESTED_LEGACY_PROJECT`.

## Executed matrix (`matrix5.py`), the `18` §9.1 state predicate encoded independently from the text

Each row: fresh copy of a tree; whole-tree before/after maps (work tree, `.governance-runtime/`, `.git` files and
plumbing, child `HOME`, kernel cache — every entry by type/mode/size/digest); before/after tree digest; the `18` §9/§9.1
installation state before and after; the `18` §6.1 `KERNEL_TAMPERED` check against `RCS(D)`; the overlay classifications.
The register is the mutating families (`init`/`adopt baseline`/`migrate baseline` + combos) plus a 21-command control
sample of non-mutating commands; the full-register no-write property is corroborated separately by the reproduced review
r4 C matrix (10,618 invocations, byte-identical aggregates) and P3r3 (2,085 jobs, identical).

| Position class | rows | project writes | `state_after` | note |
|---|---:|---:|---|---|
| **P-ROOT** `--root` on R5/R5RES/R5NOSURG/R5V | 1,335 | **0** | all `COMPLETE` | **LP-1r: 0 project writes** (work tree, runtime, `.git`); classifications survive |
| P-ROOT `--root` on **L0** control | 480 | 474 | `LEGACY` | legacy binaries mutate an ordinary legacy project — the argument synthesis reaches mutating code paths |
| **P-CWD** no-`--root`, 24 working dirs incl. inside the PPS (R5) | 11,040 | 1,056 | 10,544 `COMPLETE`, 496 `PARTIAL` | 288 rows wrote `governance/trust/**` — **all 288 `PARTIAL`**; 48 wrote the occupation — all `PARTIAL`; 96 wrote the transaction area — `COMPLETE` reported (RV5-C-L2); 96 wrote `governance/spec`/`governance/views` litter (RV5-C-L1) |
| **P-ENV** six user-env-var sets × 3 dirs (R5) | 5,130 | 291 | 4,986 `COMPLETE`, 144 `PARTIAL` | env vars open no new hole: the 144 rows writing `governance/trust/**` are **all `PARTIAL`**; only `init`/`adopt`/`migrate` write |
| **P-VEND** in/above a committed legacy sub-project (R5V) | 1,920 | 1,470 | all `COMPLETE` | every legacy command operates **inside** `vendor/legacypkg`; the outer `governance/trust` is untouched; the sub-project is reported `NESTED_LEGACY_PROJECT` (contained, LR-3) |
| **P-GIT** 18 Git-op trees × {root, product} | 9,975 | 1,492 | 5,130 `COMPLETE`, 3,705 `PARTIAL`, 1,140 `LEGACY` | writes are `@product` nested installs or on already-non-`COMPLETE` trees; **0** rows write a non-`COMPLETE` tree into `COMPLETE`; **0** `governance/trust` writes leave `COMPLETE` |

**Totals: 30,165 executed rows** (285 skipped for an absent cwd) + **1,335 `--root` rows**. Binaries read-only, SHA-256
recorded.

## Decisive properties (`matrix5-summary.json`)

| Property | Result |
|---|---|
| **LP-1r** — `--root` invocations on the four RoT-1 trees write no project byte | 1,335 rows, **0 violations** |
| **R2-H4 class** — no invocation that changed a byte under `governance/trust/**` or an occupation entry is left `COMPLETE` without `KERNEL_TAMPERED` | **0 violations** across 30,165 rows |
| Classifications lost on a RoT-1 layout | **0 rows** |
| Git-op tree written from non-`COMPLETE` into `COMPLETE` by a legacy binary | **0 rows** |
| Every nested legacy marker reported (`PARTIAL` under `governance/`, else `NESTED_LEGACY_PROJECT`) | 3,549 rows, all reported |
| `governance/trust`/occupation-writing rows left `COMPLETE` (RV4-M1 class) | **0** |
| Transaction-area writes left `COMPLETE` (RV5-C-L2) | 96 (reported, inert — recover VTS-registration gate) |
| `governance/spec`/`governance/views` litter left `COMPLETE` (RV5-C-L1) | 16 (inert — not read as trust) |

## Layout durability (`gitops.json`, real Git 2.43)

| Operation | State | Fail direction |
|---|---|---|
| fresh / shallow / partial clone, `git archive`, `clean -fdx`, `stash -u`, `worktree add`, checkout-across-migration-and-back, project-`.gitignore` untracking idiom (surgery) | `COMPLETE` | — |
| cone `sparse-checkout set governance`, non-cone sparse dropping occupation | `PARTIAL(occupation)` | fail closed |
| checkout pre-migration commit, `git restore --source <pre> -- governance` | `LEGACY` | read-only |
| `core.autocrlf=true`, `* text=auto`+`core.eol=crlf` | `PARTIAL(kernel_content_mismatch)`, `KERNEL_TAMPERED` | fail closed → **RV5-C-M1** |
| untracking idiom with legacy line kept (R5NOSURG), user `core.excludesFile`, `.git/info/exclude` carrying `.governance-runtime/` | `PARTIAL(occupation)` | fail closed → **RV5-C-M2** |

## Cross-check against the architect's evidence (claims under test)

- **P3r3** (2,085 jobs) re-run against revision 5: `summary`, `property_L3`, `chain_summary`, `job_count` equal to the
  committed output. The `--root`-only coverage note of review r4 C still applies, but revision 5 closes the subdirectory
  class independently of P3r3 (matrix5 R2-H4 property).
- **ST5 subdirectory matrix** (6,292 invocations) and **ST5 D-A01 re-run** reproduced byte-identical (summary differs only
  in `elapsed_seconds`); my independent `state_r5` predicate agrees with ST5's on every row class.
- **Review r4 C matrix** (10,618 invocations, 168 chains): rows, writes-by-layout×position, states, 56 trust rows and
  writing commands all equal to the committed output.
