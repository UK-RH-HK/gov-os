# 05 — Pre-RoT command-register matrix (executed, independent)

## Registers (derived twice, independently, and cross-checked) — `register6.py`

Each legacy binary's full command register is derived from its own `--help` recursion **and** from its own source
(`cli/src/main.rs` clap enums at the release commit, `git show`), and cross-checked.

| Binary | Commit | Leaf commands (help) | Leaf commands (source) | Options (help) | Options (source) | Leaves only in help / only in source |
|---|---|---:|---:|---:|---:|---|
| gov-4.1.2 | `8ad06be` | 104 | 104 | 118 | 121 | [] / [] |
| gov-4.1.3 | `26ab5b6` | 109 | 109 | 129 | 132 | [] / [] |
| gov-4.1.4 | `47d8394` | 115 | 115 | 133 | 136 | [] / [] |
| gov-4.1.5 | `da9c851` | 119 | 119 | 134 | 137 | [] / [] |

The three source-only options per version are `tools install --role`, `tools resolve --role` and `release build --version`:
present in the clap enums, not printed by clap's leaf help for these leaves (the matrix uses the help-derived options plus
required positionals and options). The `current_dir()`-rooted, non-`require_installed` families are exactly `init`,
`adopt baseline` and `migrate baseline` in all four versions (`cli/src/main.rs` `Cmd::Init` and `Cmd::Adopt | Cmd::Migrate`
use `cli.root.unwrap_or(current_dir())`); every other command resolves the root with `find_root` (walks up while
`governance/framework.lock` **exists**, so the revision-6 occupation directory anchors it at the RoT-1 project root) and then
`require_installed` (`NOT_INSTALLED`, because `governance/kernel/KERNEL_MANIFEST.json` cannot exist when `governance/kernel`
is a file). Environment variables read by the legacy sources (derived per version by `git grep`): `GOV_CANONICAL_ROOT`,
`GOV_DISABLE_PLUGINS`, `GOV_KERNEL_CACHE` (4.1.3+), `GOV_KERNEL_SOURCE`, `GOV_PLUGINS_DIR`, `GOV_ROLE`, `GOV_SESSION`,
`GOV_TRACE_ID`. Help leaf and option counts equal review r5 C's independently derived register.

## Base project and revision-6 layout — `build6.py`

A real legacy project built by the real 4.1.5 binary: `init --source 4.1.4` → gated `update --apply` to 4.1.5 (legacy
update snapshot at `.governance-runtime/update/4.1.5/`: `framework.lock`, `generated`, `kernel`, `project`,
`snapshot.json`) → **two** `restricted` classifications added after the update → task, gate, CIT (simulated, approved),
handoff, lesson packet, registered plugin, tool descriptor, adapters, memory index. Migrated to the revision-6 layout as the
pack specifies it (`08` §2–§3, `26` §2 and §7, `18` §5.1/§8/§9.1): the installed kernel is the 4.1.6 `framework/` tree at
`4106885` (no `KERNEL_MANIFEST.json`); lock 3.0.0 with the release content set (`kernel.files`), `registration_digest` and a
random `project_trust_id`; `registration.dsse.json`; **`governance/trust/.gitattributes` = `* -text\n`**; occupation entries;
`.gitignore` surgery (`/.governance-runtime/*`, `!/.governance-runtime/migration`); quarantine of the legacy update snapshot.

| Tree | Content | `18` §9 state (`state_r6`) |
|---|---|---|
| **R6** | migrated machine; `trust-tx/LOCK`, `trust-tx/done/<TX>/journal.json`, a RoT-1 snapshot `snapshots/<CI>/` | `COMPLETE` (reports the `done/` journal as `FOREIGN_TRANSACTION_ARTEFACT`, `01` RV6-C-L2) |
| **R6RES** | second machine on the same commit; legacy update snapshot at `.governance-runtime/update/4.1.5/`; no transaction area | `COMPLETE` |
| **R6CRASH** | R6 plus crash residue of an interrupted RoT-1 update: `trust-tx/<TX2>/{journal (swapped), trust.next/, trust.prev/, overlay.prev/}` (not VTS-registered) | `COMPLETE`, crash journal `FOREIGN` (inert) |
| **R6V** | R6 plus a committed legacy 4.1.5 sub-project at `vendor/legacypkg` | `COMPLETE`, `NESTED_LEGACY_PROJECT` reported |
| **L0** | the legacy project (control) | `LEGACY` |

`tracked_but_ignored` on R6 is `[]`; the only tracked runtime path is `.governance-runtime/migration`; the surgery is
idempotent.

## Executed matrix — `matrix6.py`, state predicate encoded independently from the text (`c6lib.state_r6`)

Each row: a fresh copy of a tree; whole-tree before/after maps of **every** entry under the project root (work tree,
`.governance-runtime/`, `.git/`) plus Git plumbing (HEAD, refs, `status --porcelain`, stash), child `HOME` and kernel cache;
the before/after whole-tree digest; the `18` §9/§9.1 state before and after; the `18` §6.1 `KERNEL_TAMPERED` check against
`RCS(D)` (the builder's release content set, never the unsigned lock); nested-marker reports; the overlay classifications.
The register is **every leaf** of each binary with every optional option and positional as a separate variant ("full"),
plus 23 stateful combinations (update apply/rollback, `init --force`, `kernel reinstall`, `adopt`/`migrate migrate` and
rollback batch 0, CIT execute/rollback, decide, tools install `--execute`, plugins register, capabilities invoke, recover,
rebuild-memory, verify product, adapters generate, checkpoint create).

| Position class | Trees | Rows | Rows writing the project | `state_after` | Note |
|---|---|---:|---:|---|---|
| **P-ROOT** `--root` (full register on R6; base + combos on R6RES, R6CRASH, R6V) | R6, R6RES, R6CRASH, R6V | 2,492 | **0** | all `COMPLETE` | **LP-1r: 0 project writes** (work tree, runtime, `.git`); top codes `NOT_INSTALLED` 1,553, `ADOPTION_NOT_STARTED` 552 |
| P-ROOT `--root` control | L0 | 516 | 505 | `LEGACY` | the argument synthesis reaches mutating code paths on an ordinary legacy project |
| **P-CWD** no `--root`, 23 working directories incl. `governance/trust`, `governance/trust/{kernel,kernel/policies,state,root,lineage,profiles}`, `governance/framework.lock`, `.governance-runtime/trust-tx`, `.governance-runtime/trust-tx/done` (full register) | R6 | 21,712 | 1,056 | 21,208 `COMPLETE`, 504 `PARTIAL` | 336 rows wrote `governance/trust/**` — **all `PARTIAL`**; 48 wrote the occupation — **all `PARTIAL`**; 96 wrote the transaction area — `COMPLETE`, all reported (inert; RoT-1 refuses the cwd, `18` §9.2); 16 `governance/spec`/`governance/views/spec` litter — `COMPLETE` (inert, restated in revision 6); 8 `governance/overlay/spec` litter — `COMPLETE` (**`01` RV6-C-L4**) |
| **P-ENV** no `--root`, 7 env-var sets (`KSRC`, `CANON`, `PLUGDIR`, `ROLESESS`+`GOV_DISABLE_PLUGINS`, `CACHE_IN_PROJECT`, `TRACE`, `ALL`) × `.`, `product`, `governance/trust` | R6 | 10,836 | 339 | 10,668 `COMPLETE`, 168 `PARTIAL` | env vars open no new hole: the 168 rows writing `governance/trust/**` are **all `PARTIAL`** |
| **P-VEND** no `--root`, in/above a committed legacy sub-project (full register) | R6V | 3,776 | 2,781 | all `COMPLETE` | every legacy write stays **inside** `vendor/` (0 rows write outside it); the sub-project is reported (LR-3) |
| **P-GIT** `--root` and `product` on 22 Git-operation trees (`gitops6`) | 22 trees | 22,188 | 2,492 | 14,448 `COMPLETE`, 5,676 `PARTIAL`, 2,064 `LEGACY` | **0** rows turn a non-`COMPLETE` tree into `COMPLETE`; the 336 writes on `COMPLETE` trees are all `@product` nested installs or `product/spec` litter (224 reported nested installs), **0** trust/occupation writes; 40 occupation writes on already non-`COMPLETE` trees |

**Totals: 62,036 rows** (61,520 executed; 516 skipped because `product/` is absent in the cone-sparse tree); 0 timeouts.
Per binary: 4.1.2 14,332; 4.1.3 15,216; 4.1.4 15,780; 4.1.5 16,192. Binary SHA-256 recorded in the summary.
Elapsed ≈ 1,040 s at 18 workers. The summary was recomputed from the complete rows file after the first dump failed on a
tuple-keyed dictionary (`matrix6.py --resummarise`; no invocation was re-run).

## Decisive properties (`matrix6-summary.json`)

| Property | Result |
|---|---|
| **LP-1r** — root-anchored invocations on the four RoT-1 trees write no project byte | 2,492 rows, **0 violations** |
| **R2-H4 class** — no invocation that changed a byte under `governance/trust/**` or an occupation entry is left `COMPLETE` without `KERNEL_TAMPERED` | **0 violations**; 592 trust/occupation-writing rows: 568 `PARTIAL`, 24 `LEGACY`; 120 `KERNEL_TAMPERED` |
| LP-1s as restated in revision 6 (`26` §4) | **0 counterexamples** |
| LP-1s as stated in revision 5 (every write under `governance/**` other than overlay content) | 16 counterexamples (`governance/spec`, `governance/views/spec`), unchanged from review r5 |
| Transaction-area writes left `COMPLETE` | 96 (cwd `trust-tx` 48, `trust-tx/done` 48), all reported, inert |
| Overlay-directory litter left `COMPLETE` | 8 (`governance/overlay/spec/audits/GOVERNANCE-ADOPTION/00-BASELINE.yaml`, cwd `governance/overlay`, `adopt`/`migrate baseline`), classifications intact → `01` RV6-C-L4 |
| Classifications lost on a `COMPLETE` RoT-1 tree | **0**. 16 rows lose them on `CHECKOUT_PRE`/`RESTORE_PRE_GOV` trees that are `LEGACY` before and after (legacy `init --force` on a Git-restored pre-migration tree: the documented LR-2 outcome) |
| Git-op tree written from non-`COMPLETE` into `COMPLETE` | **0** |
| New legacy markers not reported | 44, all the **root** legacy layout re-created on `LEGACY` Git-restored trees (not nested; `LEGACY` before and after) |
| Writes to the child `HOME` | 32, all `tools health` on trees holding an installed legacy project (L0, `vendor/legacypkg`, Git-restored trees) |

## Layout durability (`gitops6.json`, real Git 2.43.0)

| Operation | State | Fail direction |
|---|---|---|
| fresh / shallow / partial clone, `git archive`, `clean -fdx`, `stash -u`/pop, `worktree add`, checkout across the migration and back, untracking idiom with the surgery, `core.ignorecase=true` clone | `COMPLETE` | — |
| `core.autocrlf=true` (persisted), project `* text=auto`+`core.eol=crlf`, project `* text eol=crlf` | `COMPLETE`, no CRLF in the kernel | member protects |
| `.git/info/attributes` `* text` + `autocrlf` | `PARTIAL(kernel_content_mismatch, foreign_trust_entry(.gitattributes_content))`, `KERNEL_TAMPERED` | fail closed → CR6-C-1 |
| `.git/info/attributes` `* text` without a conversion source | `COMPLETE` | — |
| cone `sparse-checkout set governance`, non-cone sparse excluding occupation roots | `PARTIAL(occupation)` | fail closed (C-6) |
| checkout of the pre-migration commit, `git restore --source <pre> -- governance` | `LEGACY`, `KERNEL_TAMPERED` | read-only (LR-1/LR-2) |
| untracking idiom with a retained legacy directory-ignore line, user `core.excludesFile`, `.git/info/exclude` carrying `.governance-runtime/` | `PARTIAL(occupation)`; `check-ignore` names the source | fail closed → CR6-C-2 |

**Harness note.** A first `gitops6` pass passed `core.autocrlf`/`core.eol` as command-level `git -c` on `git clone`, which is
not written to the new repository, so its later checkout did not convert. It was corrected to persist the configuration
into the cloned repository (`git config`) before the converting checkout, and an isolated control confirmed that
`.git/info/attributes` then introduces CRLF. Only the corrected pass is reported and fed the matrix.

## Cross-check against the architect's evidence (claims under test)

See `00-REPORT.md` §Reproduction for the re-runs of LAY6, ADM6, UW6, RV5-D-A03 and review r5 C's `admit_tx` against
revision 6. AR-0017's independent matrix is broader than LAY6 (full register on the root and every working directory, not
only the mutating families; `trust-tx/done` and `trust/profiles` positions; `R6CRASH` crash residue; the revision-6
`INFOATTR`, `INFOATTR_NOCONV` and `TEXTEOL_CRLF` Git trees) and agrees with LAY6 on every shared property: R2-H4 0, LP-1r 0,
LP-1s restated 0, LP-1s as stated in revision 5 16, transaction-area rows 96, Git-op elevation into `COMPLETE` 0.
