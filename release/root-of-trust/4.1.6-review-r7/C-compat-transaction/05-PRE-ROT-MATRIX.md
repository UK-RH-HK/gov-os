# 05 — Pre-RoT command-register matrix (executed, independent) on the revision-7 layout

## Registers, derived twice and cross-checked — `register7.py`

Each legacy binary's full command register is derived independently from its own `--help` recursion **and** from its own
`cli/src/main.rs` clap enums at the release commit (`git show`), and cross-checked, without copying `register6.py`.

| Binary | Commit | SHA-256 (prefix) | Leaves (help) | Leaves (source) | Options (help) | Leaves only in help / only in source |
|---|---|---|---:|---:|---:|---|
| gov-4.1.2 | `8ad06be` | `dc924fb3…` | 104 | 104 | 118 | [] / [] |
| gov-4.1.3 | `26ab5b6` | `baba4e40…` | 109 | 109 | 129 | [] / [] |
| gov-4.1.4 | `47d8394` | `85f34cce…` | 115 | 115 | 133 | [] / [] |
| gov-4.1.5 | `da9c851` | `9169d7a8…` | 119 | 119 | 134 | [] / [] |

Leaf and help-option counts equal review r6 C's independently derived register exactly; the help/source option deltas are
the three known source-only options (`release build --version`, `tools install --role`, `tools resolve --role`, not printed
by clap's leaf help). The `current_dir()`-rooted, non-`require_installed` families are exactly `init`, `adopt baseline` and
`migrate baseline` in all four versions (source lines quoted in `registers7.json`). Environment variables each version's
source reads (`git grep` over `runtime/src`, `cli/src`): `GOV_CANONICAL_ROOT`, `GOV_DISABLE_PLUGINS`, `GOV_KERNEL_CACHE`
(4.1.3+), `GOV_KERNEL_SOURCE`, `GOV_PLUGINS_DIR`, `GOV_ROLE`, `GOV_SESSION`, `GOV_TRACE_ID`.

## Base project and revision-7 layout — `build7.py`

A real legacy project built by the real 4.1.5 binary (`init --source 4.1.4` → gated `update --apply` to 4.1.5 leaving the
legacy update snapshot at `.governance-runtime/update/4.1.5/` → **two** `restricted` classifications → task, gate, CIT,
handoff, lesson packet, plugin, tool descriptor, adapters, memory index), migrated to the revision-7 layout as the pack
specifies it (`26` §2, §7; `08` §2–§3; `18` §5.1, §8, §9.1; `20` §3, §9), plus the local per-project record the revision-7
transaction rules read (`20` §9: `project_trust_id`, a repository identity from the common-directory `(st_dev, st_ino)`, the
paths, `done_tx`, `open_tx`). The installed kernel is the `framework/` tree at `d07d200` (no `KERNEL_MANIFEST.json`).

| Tree | Content | `18` §9 state (`state_r7`, every reading) |
|---|---|---|
| **L0** | legacy project (control) | `LEGACY` (kernel_tampered) |
| **R7** | migrated machine; `trust-tx/LOCK`, a registered `done/<TX>/journal.json`, a RoT-1 snapshot | `COMPLETE` |
| **R7RES** | second machine on the same commit; legacy update snapshot present; no transaction area | `COMPLETE` (a text ambiguity: `LMI/broad` reads it as `LAYOUT_MIGRATION_INCOMPLETE` because the legacy update snapshot is a legacy-named residue — see the reading note) |
| **R7CRASH** | R7 plus an **unregistered** crash transaction `trust-tx/<TX2>/{journal (swapped), trust.next, trust.prev, overlay.prev}` | `COMPLETE`, crash journal `FOREIGN_TRANSACTION_ARTEFACT` (inert) |
| **R7OPEN** | R7 plus an **honoured open** transaction (the record lists the TX) at phase `swapped` | `IN_TRANSACTION` |
| **R7V** | R7 plus a committed legacy 4.1.5 sub-project at `vendor/legacypkg` | `COMPLETE`, `NESTED_LEGACY_PROJECT` reported |
| **R7WT** | a `git worktree` of a clone of R7 (shared common directory) | `COMPLETE` |

**Reading note.** `state_r7` reports the state under all four readings of the two revision-7 text ambiguities (`ABSENT/type`
vs `ABSENT/path`; `LMI/narrow` vs `LMI/broad`). R7RES diverges: under `LMI/broad` (legacy-named residue = a
`LAYOUT_MIGRATION_INCOMPLETE` signal) it reads `LAYOUT_MIGRATION_INCOMPLETE`; under `LMI/narrow` it reads `COMPLETE`. A
legacy **update snapshot** is a legitimate second-machine artefact (not an interrupted migration), so `LMI/narrow` is the
intended reading; the pack should state that `LAYOUT_MIGRATION_INCOMPLETE` keys on a layout-migration **journal/marker**, not
on any legacy-named directory (carried under CR7-C-3). No reading makes R7RES `COMPLETE`-with-a-write or loses a
classification.

## Executed matrix — `matrix7.py`, predicate encoded independently from the text (`c7lib.state_r7`)

Each row: a fresh copy of a tree (for a worktree, the base repository and the worktree); whole-tree before/after maps of
**every** entry under the slot (work tree, `.governance-runtime/`, `.git/`) plus Git plumbing, child `HOME` and kernel
cache; the before/after whole-tree digest; `state_r7` before and after under **every reading**; the `18` §6.1
`KERNEL_TAMPERED` check against the release content set (never the unsigned lock); the overlay classifications; and, for the
honoured open transaction, the journal digest. The register is **every leaf** of each binary with every optional option and
positional as a separate variant, plus 25 stateful combinations (including `update --apply` and `kernel reinstall` sourced
from the installed RoT-1 kernel and from the quarantined snapshot, `init --force`, adopt/migrate batches and rollbacks, CIT,
recover).

| Position class | Trees | Note |
|---|---|---|
| **P-ROOT** `--root` (full register on R7; base + combos on R7RES, R7CRASH, R7OPEN, R7V, R7WT, L0) | all | LP-1r: root-anchored invocations write no project byte |
| **P-CWD** no `--root`, 30 working directories incl. inside `governance/trust/**`, the occupation, the transaction area, `done/`, the legacy quarantine, snapshots, `.git` (full register) | R7 | every `governance/trust/**` or occupation write leaves a not-`COMPLETE` state under every reading |
| **P-OPEN** no `--root`, inside an honoured open transaction's `trust.next`, `trust.prev`, `trust.prev/kernel`, `overlay.prev` | R7OPEN | legacy writes into the staged tree do not become `governance/trust`; the honoured journal is unchanged |
| **P-WT** no `--root`, inside a `git worktree` | R7WT | legacy writes stay within the worktree |
| **P-ENV** no `--root`, env-var sets incl. a kernel cache and source pointed **into the account store** and at the **installed kernel** | R7 | env vars open no new hole |
| **P-VEND** no `--root`, in/above a committed legacy sub-project | R7V | every legacy write stays inside `vendor/`; the sub-project is reported |
| **P-GIT** `--root` and `product` on the 45 `gitops7` trees | 45 trees | 0 non-`COMPLETE` tree elevated to `COMPLETE` |
| **P-TXN** `--root` on the post-recovery / crash-prefix / uninstall trees `txn7` produced | txn7 trees | half-migrated and recovered trees never `COMPLETE` without the steps |

**Totals (this review's independent revision-7 matrix, `matrix7-summary.json`).** **118,732 rows** (117,256 active, 1,476
skipped where a cwd is absent in a sparse/degraded tree; 1 harness-error row — a legacy `adopt map` that recurses the kernel
path, caught and recorded, not dropped), ≈ 2,074 s at 16 workers. Per binary: 4.1.2 27,749; 4.1.3 29,322; 4.1.4 30,417;
4.1.5 31,244. Per position class: P-ROOT 4,096; P-CWD 28,560; P-OPEN 2,620; P-WT 2,096; P-ENV 17,292; P-VEND 3,808; P-GIT
47,160; P-TXN 13,100. Writing rows on RoT-1 trees: 17,723. Binary SHA-256 recorded in the summary.

| Property (every reading) | Result |
|---|---|
| **LP-1r** — root-anchored invocations write no project byte | 3,572 rows, **0 violations** |
| **R2-H4** — a `governance/trust/**` or occupation change left `COMPLETE` (any reading) without `KERNEL_TAMPERED` | **0 violations** (independently recomputed over the writing rows: 0) |
| A write moved a non-`COMPLETE` tree to `COMPLETE` (any reading) | **0** |
| A write produced `ABSENT` (any reading) | **0** |
| Classification absent on a `COMPLETE`/`ABSENT` tree | 28 rows, **all** on the deliberately-degraded `SMUDGE_FILTER_OVERLAY` input tree; **0** on any intact R7-family tree (a legacy invocation never loses a classification on an intact layout) |
| Writes under the account-store path | 24 rows, **all** P-ENV where the user points `GOV_KERNEL_CACHE`/`XDG_CACHE_HOME` at the store: a legacy `init` writes kernel-**cache** blobs (`.local/state/…/kernels/…`), never the named trust files RoT-1 reads (`high-water.json`, `anchors.json`, …); inert, and `GOV_*` cannot add trust (D-0008 rule 15). Observation only — the account store must tolerate foreign files in its directory (carried) |
| Transaction-area writes into an **honoured open** transaction (P-OPEN) | 140 rows change the transaction-area digest while the machine stays `IN_TRANSACTION`; the **installed** state (`governance/trust`) is unchanged. `gov recover` re-authenticates the exchange-back target (`20` §5), so a legacy write into `trust.next`/`trust.prev` is caught at recover time — inert, guard is spec-only (C-2 / foreign-journal class) |

The **reading-divergence** rows (3,612) are exactly the two documented text ambiguities: a legacy update snapshot /
legacy-named residue reads `LAYOUT_MIGRATION_INCOMPLETE` under `LMI/broad` but `COMPLETE`/`PARTIAL` under `LMI/narrow`, and
a fully-removed legacy layout reads `ABSENT` under `ABSENT/type` but `PARTIAL` under `ABSENT/path`. None of these divergences
produces a `COMPLETE`-with-a-write or a classification loss; they are carried under CR7-C-3 (state that
`LAYOUT_MIGRATION_INCOMPLETE` and `ABSENT` key on a migration journal/marker and occupation **type**, not on any
legacy-named directory).

## Decisive properties

| Property | Result |
|---|---|
| **LP-1r** — root-anchored invocations on the RoT-1 trees write no project byte | see matrix7 summary; matrix6 (reproduced) 2,492 rows, **0 violations** |
| **R2-H4 class** — no invocation that changed a byte under `governance/trust/**` or an occupation entry is left `COMPLETE` (under **any** reading) without `KERNEL_TAMPERED` | matrix6 (reproduced) **0 violations** over 62,036 rows; matrix7 (this review, revision-7 predicate, more positions) — see summary |
| **Elevation** — a write moved a non-`COMPLETE` tree to `COMPLETE` under any reading | matrix6 (reproduced) **0**; matrix7 — see summary |
| **Transaction-area writes / honoured-journal mutation** | inert; the honoured open-transaction journal digest is unchanged by legacy writes (P-OPEN) |
| **Classification loss on a `COMPLETE` tree** | matrix6 (reproduced) **0** (16 losses are on pre-migration `LEGACY` trees, the documented LR-2 outcome) |

## Reproduction cross-check (the architect's and prior review's claims, tested)

`matrix6.py` (review r6 C, unmodified, 12 workers) was re-run against the `d07d200` export: **62,036 rows** (61,520
active, 516 skipped), and **every** property, per-position aggregate and writing-command count is **equal** to (a) the
committed review-r6 C summary and (b) **both** of the architect's revision-7 `matrix6` tree sets
(`evidence/r7/C/matrix6-summary.earlier-trees.json` and `matrix6-summary.rebuilt-trees.json`): **R2-H4 0 violations**;
LP-1r 2,492 rows, 0 project writes; Git-op elevation into `COMPLETE` 0; classification-lost 16; transaction-area 96. The
review r6 C `register6`, `struct6`, `attrprec6`, `admtx6` and `crashmig6` were re-run **byte-identical** to their committed
outputs; `gitops6` equal apart from the scratch prefix. So both the architect's "reviewer C `matrix6` re-run" claim and the
review r6 C legacy-containment result are confirmed on the revision-7 pack.

`matrix7` is broader than `matrix6` (independent register derivation; the revision-7 predicate with every reading; the
honoured-open-transaction, worktree and account-store-env positions; `update`/`reinstall` sourced from the installed kernel
and the quarantine) and is this review's primary independent evidence for R2-H4 on the revision-7 layout.
