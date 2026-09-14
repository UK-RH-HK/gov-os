# 05 — Pre-RoT command-register matrix (executed, independent)

## Registers (derived independently from each binary's own `--help`)

`evidence/register.py` walks each binary's `--help` tree (independent of the architect's P3r3 parser). Leaf-command
counts (SHA-256 in `evidence/registers.json`):

| Binary | SHA-256 (first 16) | Leaf commands | Groups |
|---|---|---|---|
| gov-4.1.2 | `dc924fb3293b3fda` | 104 | 20 |
| gov-4.1.3 | `baba4e403dc23fe9` | 109 | 21 |
| gov-4.1.4 | `85f34cce2b43877f` | 115 | 23 |
| gov-4.1.5 | `9169d7a8be41324a` | 119 | 23 |

## Base project and layout

A real legacy project built by the real 4.1.5 binary: `init --source 4.1.4` → gated update to 4.1.5 (legacy update
snapshot at `.governance-runtime/update/4.1.5/`) → a `restricted` classification added to
`governance/project/DATA_SENSITIVITY.yaml` **after** the update, plus realistic prior state (task, gate, CIT, handoff,
lesson packet, registered plugin, tool descriptor, memory index, adapters). Three intact revision-4 layout variants were
built (`evidence/build_trees.py`, `26` §2 / `08` §2):

- **R4** — the migrated layout (legacy update snapshot quarantined; a completed `trust-tx/done/<TX>` and a `snapshots/`
  present; `.gitignore` = replace-form rule);
- **R4RES** — a second machine that pulled the migration commit: legacy update snapshot still at
  `.governance-runtime/update/4.1.5/`, no RoT-1 transaction area;
- **R4APP** — as R4 but the `.gitignore` retains the legacy `.governance-runtime/` line (append);
- **L0** — the legacy project unchanged (positive control).

## Executed matrix

Each of the four real binaries × its own register, on a **fresh copy** of a tree, with whole-tree before/after maps
(work tree, `.governance-runtime/`, `.git/` — every entry by type/mode/size/digest), Git state, child `HOME`, the overlay
classification, and the `18` §9 installation state. **10,618 executed invocations + 168 stateful chains** across three
positions:

- **P-ROOT** — `--root <project>` (all four layouts);
- **P-CWD:<sub>** — no `--root`, working directory `<sub>` ∈ {`.`, `product`, `spec`, `governance/overlay`,
  `governance/views`, `governance/trust`, `governance/trust/state`, `governance/framework.lock`, `.governance-runtime`}
  (R4);
- **P-ENV** — no `--root`, cwd `.` or `product/`, with `GOV_KERNEL_SOURCE`, `GOV_CANONICAL_ROOT`, `GOV_PLUGINS_DIR`,
  `GOV_ROLE`, and all combined (R4).

## Totals

| Layout / position class | rows | work-tree writes | Git writes | state ≠ `COMPLETE` |
|---|---:|---:|---:|---:|
| R4 / **P-ROOT** (`--root`) | 966 | **0** | 0 | 0 |
| R4RES / **P-ROOT** | 966 | **0** | 0 | 0 |
| R4APP / **P-ROOT** | 572 | **0** | 0 | 0 |
| R4 / P-CWD content subdir (`product`, `spec`) | 4,288 | 196 | 0 | 0 |
| R4 / P-CWD inside governance tree | 2,860 | 140 | 0 | 0 |
| **L0 control** (legacy project) | 966 | **245** | 0 | — |

- **P-ROOT property (independently reproduced):** on all three intact-layout variants, no pre-RoT binary 4.1.2–4.1.5
  writes a byte to the work tree or Git, and no run removes the restricted classification. 2,504 invocations, 0 writes.
  Corroborates P3r3.
- **Env-var runs:** 2,000; the 140 that wrote are the same `init`/`adopt baseline`/`migrate baseline` class — environment
  variables open no new hole.
- **L0 control sanity:** 245 of 966 legacy invocations mutate the tree on an ordinary legacy project, confirming the
  argument synthesis reaches mutating code paths.

## The only writing commands

Across all 336 RoT-1-layout write rows, the commands that ever wrote are exactly **`init`, `adopt baseline`,
`migrate baseline`** — the three that root at `current_dir()` and skip `require_installed()`. Every other command in
every register returns `NOT_INSTALLED` / `IO_ERROR` and writes nothing, because `find_root()` + the occupation contains
them.

- Content-subdir invocations (`product/`, `spec/`) create a nested legacy install **outside** the PPS.
- **`governance/trust/` and `governance/trust/state/` invocations write inside `governance/trust/**` (56 invocations),
  and the outer RoT-1 state stays `COMPLETE`** → **RV4-C-H1** (`01-FINDINGS.md`).

## Chains

168 stateful chains (adoption A0–A11, init→use, init --force→use, update→gate→approve→rollback, a CIT whose manifest
targets `governance/trust/**` and the overlay, plugins/tools, recover/reinstall), at P-ROOT and from five subdirectories.
36 RoT-1 chains wrote — all the same subtree `init`/`adopt` class; those rooted in `governance/trust` wrote inside the
PPS with the outer state `COMPLETE`. No chain step retrieved the restricted marker. (`evidence/matrix-chains.json`.)

## Cross-check against the architect's P3r3 (claim under test)

P3r3 reports 695 invocations + 40 chains, 0 changes on the intact layout, with each binary's register from its own
`--help`. Reviewing the harness (`../../4.1.6/evidence/P3r3-pre-rot-register-matrix.py`) and re-deriving the registers
independently, the base construction, layout, whole-tree digests and control are sound and match my construction **for
the `--root` case**. P3r3's single coverage gap is decisive: **every P3r3 invocation carries `--root <project root>`**
(the harness always passes `--root c`), so subdirectory invocation of the `current_dir()`-rooted commands — the RV4-C-H1
class — is not exercised by P3r3, and the pack's LP-1 property statement (“every invocation derived from its own
register”) is true only under that implicit `--root`.

## Environment

Linux 6.6 (WSL2), ext4. The RoT-1 install/transaction machinery is architecture-only; cross-device / RENAME_EXCHANGE and
concurrent/crash behaviour were reasoned from `18`/`20`, not executed (`04` C-2, `02` A08–A10).
