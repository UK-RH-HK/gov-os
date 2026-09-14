# 00 — Independent compatibility & transaction review (C) of RoT-1 revision 4

| | |
|---|---|
| Run | AR-0007, role `rot-reviewer-compat-transaction` |
| Reviewed | RoT-1 revision 4, commit `bca05a7e2c2791126fde1d3d812facdaa45b2e45` (`release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`) |
| Rejected prior | revision 3 `ca77a43`; consolidated review r3 `79a09a1` (synthesis adjudication governs) |
| Handoff | `HO-0007` |
| **Verdict** | **`BLOCKING_FINDINGS_PRESENT`** |

## Independence

This session authored no RoT-1 revision, no prior review, and did not read reviewer B's output, other branches or other
worktrees (`git branch -a`, `git log --all`, other scratch directories were not used). Under `release/orchestration/` I
read only `HO-0007`, `HO-0001` (§3–§4) and `AGENT_RUNS/README.md`. The architect's response matrix (`22`), `28`, P1r4,
P3r3 re-run, P4r4, LR2 and every pack evidence file were treated as **claims to test**, not findings. No scope deviation.

## Hygiene

All probes ran in scratch under `env -i` with `GOV_*` stripped from every child (only `GOV_KERNEL_CACHE` set, into
scratch); `HOME`, `XDG_*` into scratch; `GIT_CONFIG_NOSYSTEM=1`, `PYTHONDONTWRITEBYTECODE=1`. The canonical checkout and
the repository were never written. Whole-tree snapshots record **every** entry (work tree, `.governance-runtime/`,
`.git/`) by type, mode, size and SHA-256 — before/after digests of the entire tree, not named paths. Legacy binaries are
the real `gov-4.1.{2,3,4,5}` (SHA-256 in `evidence/registers.json` / `trees-build.json`). No forced deletes were used.

## Scope and method

Compatibility and transactions (Phase 1 protocol §5 C, HO-0007 §2–§4).

- **Independent registers.** Each legacy binary's full command register was derived from its own `--help` recursion
  (`evidence/register.py`, independent of the architect's P3r3 parser): 4.1.2 = 104 leaf commands, 4.1.3 = 109, 4.1.4 =
  115, 4.1.5 = 119.
- **Independent pre-RoT matrix.** A real legacy project was built by the real 4.1.5 binary (init 4.1.4 → gated update to
  4.1.5 → a `restricted` classification added **after** the update, plus realistic prior state: task, gate, CIT, handoff,
  lesson packet, registered plugin, tool descriptor, memory index, adapters), then the revision-4 layout (`26` §2 / `08`
  §2) built from it and committed as a migration commit. **10,618 executed invocations + 168 stateful chains** were run
  across three intact-layout variants (R4; R4RES with the legacy update snapshot still present; R4APP whose `.gitignore`
  retains the legacy line) and a legacy control (L0), in three invocation positions: `--root <project>`, from each of nine
  subdirectories with **no** `--root`, and with environment variables a user might set (`GOV_KERNEL_SOURCE`,
  `GOV_CANONICAL_ROOT`, `GOV_PLUGINS_DIR`, `GOV_ROLE`, …).
- **Layout durability** (`evidence/durability.py`): fresh clone, shallow clone, `git archive`, `git clean -fdx`,
  stash/pop, cone and non-cone sparse checkout, checkout across the migration commit, `git worktree add`, the untracking
  idiom, `git revert`, case-collision enumeration.
- **Legacy regain / path tricks** (`evidence/legacy_regain.py`): occupation removal, `git checkout`/`git restore` of
  pre-migration paths, a legacy CIT targeting `governance/trust/**`, symlink substitution of an occupation entry, and a
  nested legacy project.
- **Transaction state machine** (`18`, `20`): reviewed as a design (the RoT-1 install/transaction machinery is
  architecture-only, unimplemented); the legacy-binary boundary and the `18` §9 installation-state machine were exercised
  with the real binaries and a faithful re-encoding of `18` §9.

## Summary of results

- **The rooted property holds and is independently reproduced.** For every invocation carrying `--root <project root>`,
  on all three intact-layout variants (2,504 rows), **no pre-RoT binary writes a byte to the work tree or Git**, and a
  RoT-1 process afterwards is `COMPLETE`. This corroborates P3r3.

- **BLOCKING — RV4-C-H1 (HIGH). The occupation defence is escaped by subdirectory invocation.** `gov init`,
  `gov adopt baseline` and `gov migrate baseline` root at `current_dir()` (not `find_root()`; cli/src/main.rs) and do not
  call `require_installed()`. Run from **any subdirectory** of an intact revision-4 project with no `--root`, they install
  a fresh legacy governance project rooted at that subdirectory — a path the occupation does not cover. When the
  subdirectory is inside the trust tree (`governance/trust/` or `governance/trust/state/`), the pre-RoT write lands
  **inside the Protected Path Set `governance/trust/**`** (56 executed invocations), and the RoT-1 installation-state
  machine (`18` §9) still reports **`COMPLETE`**. This is a silent, persistent, undetected pre-RoT write into the trust
  PPS that a RoT-1 binary later treats as valid, on a fully intact layout, via ordinary commands. It contradicts VU-10
  (“writes under the PPS happen only inside the install transaction”) and HO-0001 §3.4 (trust paths protected as a class).
  **R2-H4 is therefore not closed as a class:** P3r3 and the pack's LP-1 only ever ran invocations with `--root <project
  root>`, so subtree invocation was untested.

- **RV4-C-M1 (MEDIUM, carried). RV3-L7 reopens under a real migrated `.gitignore`.** The revision-4 fix depends on the
  migrated project's `.gitignore` containing only the *replace-form* rule (`/.governance-runtime/*` +
  `!/.governance-runtime/migration`). A real legacy project's `.gitignore` already contains `.governance-runtime/`
  (written by legacy `init.rs`), and no pack rule specifies that the install transaction **removes** that pre-existing
  line. If it is retained (the non-destructive default — append), `git ls-files -ci --exclude-standard` lists
  `.governance-runtime/migration` and the “untrack ignored files” idiom drops the occupation from every later clone →
  `PARTIAL(occupation)`. Directly reproduced with real Git (`evidence/durability.json` R4 vs R4APP). Fail-closed, hence
  carriable, but the architect's “ADDRESSED — executed” closure of RV3-L7 rests on a hand-built tree
  (`RV3-D-A05-A07-rerun-r4-layout.json`) that does not exercise the retained-line case.

- **LR-2 / RV3-M6 reproduces exactly as documented.** Occupation removal, `git checkout <pre> -- governance` and
  `git restore --source <pre> -- governance` each let the real 4.1.5 binary regain a `verified: true` legacy install that
  retrieves post-migration-classified material, and a legacy CIT then rewrites `governance/trust/**`. In every case a
  RoT-1 binary fails closed (`PARTIAL(occupation)` or `LEGACY`). The revision-4 bound (`26` §8) is stated correctly and
  holds (`evidence/legacy_regain.json`).

## Prior-finding status (HO-0007 §3)

| Prior finding | Status | Basis |
|---|---|---|
| **R2-H4** pre-RoT binaries damage RoT-1 projects | **NOT CLOSED as a class (NARROWED)** | Closed for `--root` invocation (2,504 rows, 0 writes). **Open for subtree invocation** of `init`/`adopt baseline`/`migrate baseline`, which write the PPS with RoT-1 `COMPLETE` → **RV4-C-H1** (`evidence/subdir_escape.json`, `matrix-rows.jsonl`). |
| RV3-M6 occupation not robust to removal / Git restore | **OPEN as residual, bound correctly** | Reachable legacy outcome reproduced on the revision-4 layout; RoT-1 fails closed on all resulting trees (`legacy_regain.json` A/B/C/E). LR-2 (`26` §8) states it correctly. Carried. |
| RV3-L7 untracking idiom drops the occupation | **NARROWED, not CLOSED** | Closed only when the migrated `.gitignore` holds the replace-form rule alone; reopens when the legacy `.governance-runtime/` line is retained → **RV4-C-M1** (`durability.json`). |
| C-1 (LR-2 restated with harm assertions) | **Addressed as documented** | `26` §8 states the reachable outcome and the RoT-1 bound; reproduced (`legacy_regain.json`). |
| C-2 (cross-device tx refusal, unanchored `PARTIAL` repairable) | **Carried — spec only** | `18` §3, `20` §8. Not executable (RoT-1 tx unimplemented). |
| C-3 (doctor names stray merge/partial-removal artefacts) | **Carried — spec only** | `18` §9 D033. My E-case leaves a stray `governance/kernel/KERNEL_MANIFEST.json`; detection is spec-only. |
| C-4 (occupation type by `st_mode`, not name) | **Carried — spec only; model consistent** | The `18` §9 model flags a symlinked occupation entry as wrong-type → `PARTIAL` (`legacy_regain.json` F). |
| C-5 (full-register RT-50 on a genuine install) | **Carried — spec only** | My matrix is the independent analogue on a hand-built layout; a genuine-install run needs the implementation. **RT-50 must add subdirectory invocations (RV4-C-H1).** |
| RV3-M2 (transaction part): pins/records/journals writable by the governed account; `gov`-run repository commands | **Carried — spec only** | Confinement (VU-14, `24` §3.5) and “journal honoured only if VTS-registered” (`18` §5.1) are stated but unimplemented; not executable. |
| RV3-M9 (transaction part): acceptance plan cannot detect the classes | **Partly addressed; a gap remains** | `12` adds RT-50b, RT-81, RT-99, RT-122–127. **No RT exercises subdirectory invocation of `init`/`adopt baseline`/`migrate baseline`** (RV4-C-H1); the plan still cannot detect that class. |

**Verdict: `BLOCKING_FINDINGS_PRESENT`** — one HIGH (RV4-C-H1). This is a role verdict, not the architecture verdict;
the synthesis reviewer issues that. Findings detail in `01-FINDINGS.md`; held-out register in `02-HELDOUT-ATTACKS.md`;
residuals in `03-RESIDUALS.md`; carried requirements in `04-CARRIED-REQUIREMENTS.md`; executed matrix in
`05-PRE-ROT-MATRIX.md`.
