# 00 — Independent compatibility & transaction review (C) of RoT-1 revision 6

| | |
|---|---|
| Run | AR-0017, role `rot-reviewer-compat-transaction` |
| Reviewed | RoT-1 revision 6, commit `4106885dadebac55596067a2586cf4d3097fc025` (`release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`) |
| Rejected prior | revision 5 `cdb4e14`; consolidated review r5 `d1228cb` (synthesis adjudication governs over its panel) |
| Handoff | `HO-0017`; owner requirement `HO-0001` §3.4 |
| Branch / base | `phase1/rot1-r6-review-c` from `cd4526a` |
| Date | 2026-09-14 |
| **Role verdict** | **`NO_BLOCKING_FINDINGS`** (not the architecture verdict; the synthesis reviewer issues that) |

## Scope

Compatibility and transactions (Phase 1 protocol §5 C; `HO-0017` §2–§6): the real 4.1.2–4.1.5 binaries over their full
command registers on the revision-6 layout; the installation-state rules (`18` §9, §9.1, §9.2, the transaction-area
closure); layout durability through ordinary Git operations and tools; `gov-admit` admission and re-admission as
transactional state; rollback, recovery, snapshots, partial installs, crash recovery, concurrency, cross-machine behaviour,
path tricks and corrupted state; project-strength and gated-reduction obligations across remedies; prior-finding status;
held-out attacks; residuals.

## Independence

- **Authored before by this session:** nothing — no RoT-1 revision, specialist proposal, prior review, or the other panel
  review.
- **Orchestration files read:** `HO-0017`, `HO-0001` and `AGENT_RUNS/README.md` only.
- **Not read:** reviewer B's output, other branches (`git branch -a`/`git log --all` not used), other worktrees, other
  scratch directories, session or agent transcripts, task-output files.
- **Treated as claims:** the response matrix (`22`), LAY6, ADM6, UW6, ATTR6 and every pack evidence file.
- **Disclosures.**
  - The host context included the user's auto-memory index (one-line summaries of earlier Governance OS reviews). No memory
    file was opened; nothing here rests on it.
  - Twice the host saved a large tool output of mine to a file under `~/.claude/projects/…/tool-results/`. Those files were
    not opened; the sources were re-read from the worktree instead.
  - The coordinator sent a routing message mid-run (resume and finish). It changed no scope.
  - A scratch mirror of the repository was made with `git archive 4106885` so that reproduced instruments resolve canonical
    roots and sources in scratch. Legacy source was read with `git show` at `8ad06be`, `26ab5b6`, `47d8394`, `da9c851`
    (reachable from the branch).
  - One shell command containing `rm -rf` was denied by the permission system and did not run. Scratch copies are removed by
    Python `shutil.rmtree` inside `matrix6.py`/`gitops6.py` and the reproduced LAY6 `matrix5.py` (scratch paths only;
    `evidence/README.md`).
  - No helper sessions were used.

## Hygiene

All probes ran in scratch under `env -i`: `PATH`, `HOME`, `XDG_*`, `GOV_KERNEL_CACHE` in scratch; `GOV_*` set only where it
is the object of a test; Git with `GIT_CONFIG_NOSYSTEM=1`, scratch `GIT_CONFIG_GLOBAL`, `GIT_OPTIONAL_LOCKS=0`,
`core.hooksPath=/dev/null`. The canonical checkout and every other worktree were never written; the worktree held only this
output directory before commit (checked with `git status --ignored`). Legacy binaries were copied read-only; SHA-256 in
`evidence/REVIEWED-CONTENT-DIGESTS.txt` and `matrix6-summary.json`. Whole-tree digests, never named paths, decide "no write".

## Method

All instruments are original to AR-0017 (`evidence/`):
- **Registers** (`register6.py`): each binary's register from `--help` recursion and from its clap source, cross-checked
  (104/109/115/119 leaves; 0 leaf differences).
- **Revision-6 predicate** (`c6lib.state_r6`): `18` §9, §9.1 (with the `.gitattributes` member), §9.2 (with the transaction
  area) and §5.1, encoded from the text; overlapping rows reported together.
- **Trees** (`build6.py`): a real 4.1.5-built legacy project with a legacy update snapshot and two restricted
  classifications, migrated to the revision-6 layout with the 4.1.6 `framework/` kernel: R6, R6RES, R6CRASH (foreign crash
  transaction residue), R6V (nested legacy sub-project), L0.
- **Pre-RoT matrix** (`matrix6.py`): full registers of 4.1.2–4.1.5 with every option variant plus 23 stateful combinations,
  `--root` on four RoT-1 trees and the control, no `--root` from 23 working directories at every depth (inside
  `governance/trust/**`, the occupation directory, `trust-tx`, `trust-tx/done`), 7 environment-variable sets, a nested
  legacy sub-project, and 22 Git-operation trees: **62,036 rows** (`05`).
- **Layout durability** (`gitops6.py`, `attrprec6.py`, `struct6.py`): clone, shallow, partial, sparse, archive, clean, stash,
  worktree, checkout and restore across the migration, the untracking idiom under every ignore source, the `.gitattributes`
  member against every attribute source, case-insensitive clone, structural tampering.
- **Transactions** (`admtx6.py`, `crashmig6.py`, design reading): the pack's revision-6 reference executor for crash,
  re-admission, rollback, concurrency and record placement; a crash after every step of the first-install layout migration
  with real legacy binaries on each recovered tree; the record, store and re-record rules of `17`–`20`, `24`, `26`, `31`,
  `34`.

## Reproduction of prior decisive probes and architect evidence (claims)

Re-run unmodified from the scratch mirror (`evidence/reproduction/`).

| Probe (owner) | Behind | Result on revision 6 |
|---|---|---|
| LAY6 `matrix5.py --focus --workers 16` (architect; review r5 C harness) | R2-H4 not regressed; LP-1r; LP-1s restated | **reproduced**: 30,735 rows, 285 skipped; every property, per-position aggregate and writing-command count equal to the committed LAY6 summary (R2-H4 0; LP-1r 1,335/0; LP-1s as stated in revision 5 16; transaction-area rows 96) |
| LAY6 `gitops5.py` | RV5-M6, RV5-M7 | **reproduced**: every row's state and reasons equal. Its `INFOATTR` row does not exercise the stated condition (`01` RV6-C-L5) |
| LAY6 `build5.py` | revision-6 layout | **reproduced**: R5, R5RES, R5NOSURG, R5V `COMPLETE` |
| LAY6 `props6.py` | LP-1s restated | counterexamples 0, equal; row counts differ with the input file (committed run included the L0 control) (`01` RV6-C-L5) |
| review r5 C `register5.py` (LAY6 copy) | registers | help side equal (104/109/115/119); source side empty in the history-less mirror (environmental); re-derived by `register6.py` |
| review r5 C `admit_tx.py` (r5 reference) | RV5-C-A08…A11 | equal except the nondeterministic unlocked A11 race |
| ADM6 (architect) | RV5-M3, RV5-C-A11 | verdicts equal; output equal except the nondeterministic unlocked-mutant race |
| UW6 (architect) | RV5-M8 restatement | **byte-identical** |
| review r5 D `RV5-D-A03` | RV5-M8 | behaviour verdicts unchanged; its pack-text checks now find no "C0–C2" claim in `31` GB-4′ or RT-138 (the revision-5 overclaim is gone) |
| review r5 C RV5-C-A01…A13 | R2-H4, RV5-C-M1/M2/L1/L2/L3 | re-asked on the revision-6 layout as RV6-C-A01…A14 with AR-0017's instruments (`02`) |

## Prior-finding status (`HO-0017` §3.1)

| Finding | Status | Basis |
|---|---|---|
| **R2-H4** pre-RoT binaries damage RoT-1 projects | **CLOSED as a class** (confirmed) | matrix6: 592 trust/occupation-writing rows, 0 left `COMPLETE` without `KERNEL_TAMPERED`; LP-1r 2,492 rows, 0 project writes; 0 Git-op trees written into `COMPLETE`; LAY6 reproduced; struct6: every trust/occupation/member tamper fails closed |
| **RV5-M3** re-admission discards the machine trust store; record placement | **CLOSED** at model level (R-ADM-7′, R-ADM-8′, R-ADM-13; carried to implementation CR6-C-5). The store's location and owner are newly found inconsistent → RV6-C-M5 | admtx6 T2, T4, T5, T9; ADM6 reproduced |
| **RV5-M6** no `.gitattributes` | **CLOSED as a class**; residual `.git/info/attributes` override fails closed → RV6-C-L1 | gitops6 `AUTOCRLF`, `TEXTAUTO_EOLCRLF`, `TEXTEOL_CRLF` `COMPLETE` with no CRLF on disk; attrprec6; `INFOATTR` `PARTIAL`, `KERNEL_TAMPERED` |
| **RV5-M7** out-of-project ignore sources | **NARROWED**: condition stated and source named; behaviour unchanged (fail closed) → RV6-C-M1 | gitops6 `GLOBALEXCL`, `INFOEXCL` `PARTIAL(occupation)` with `check-ignore` source |
| **RV5-L7** LP-1s and rule (12) overclaim | **NARROWED**: restated to trust/occupation (0 counterexamples); a third litter location unnamed → RV6-C-L4 | matrix6 LP-1s restated 0; 8 `governance/overlay/spec` rows `COMPLETE` |
| **RV5-L8** transaction area outside §9.1/§9.2; rule (10) | **CLOSED** in specification (§9.2 and rule (10) include it; litter reported and inert; refusal carried RT-175) | `discover_r6` refuses at `trust-tx` and `trust-tx/done`; 96 matrix rows reported |
| **C-2** cross-device transaction area | **OPEN** (carried; specified, not executable before implementation) | `18` §3; RT-123 |
| **C-3** doctor names stray artefacts | **OPEN** (carried; scope extended by RV6-C-L4 and RV6-C-M2) | `18` §9; RT-124 |
| **C-4** type by `st_mode`, not name | **NARROWED**: holds in the state model (struct6); the use-time `st_nlink` guard is specification only | struct6; VU-12 |
| **C-5** full-register RT-50 on a genuine install | **OPEN** (carried; needs the implementation; matrix6 is the independent analogue) | `12` RT-50, RT-144 |
| **C-6** doctor names nested lock / sparse roots | **NARROWED**: sparse → `PARTIAL(occupation)` executed; doctor naming specification only | gitops6 `SPARSE_CONE`, `SPARSE_NONCONE` |

## HO-0001 §3.4 (legacy-binary damage containment)

**SATISFIED as a class**, with carried conditions. No pre-RoT binary, in any executed position, environment or Git-operation
tree, silently mutates the kernel, trust, lock, occupation or `.gitattributes` member into a state a RoT-1 binary treats as
valid. The conditions are the LR-2 trigger list (RV6-C-M2), the per-record detection bound (RV6-C-M3) and the overlay-litter
naming (RV6-C-L4).

## Summary of results

- **Legacy containment holds on the revision-6 layout** (62,036 independent rows; LAY6 reproduced).
- **The `.gitattributes` member closes RV5-M6 as a class** under every in-tree attribute source; only `.git/info/attributes`
  overrides it, and that fails closed.
- **Admission records** behave as revision 6 states on the reference executor (store kept on re-admission, rollback keeps the
  record, serialised admissions, records outside the store ignored).
- **Transaction-state gaps (MEDIUM, carried):**
  - **RV6-C-M2**: the first-install layout migration and the exchange-to-journal window are outside the journal phase model.
    Executed: the documented recovery leaves half-migrated trees `LEGACY`, `PARTIAL` or `ABSENT` (and `ABSENT` permits `init`
    over the classified overlay); state rows overlap; legacy `init --force` then serves restricted material. Never `COMPLETE`.
  - **RV6-C-M3**: the per-project record identity (path vs `project_trust_id`) is defeated by worktree, move, second clone,
    fork or template copy.
  - **RV6-C-M4**: contradictory re-record rules at commit allow one reading in which a remedy or update clears a strength
    report or a pending gate.
  - **RV6-C-M5**: the admission store and the account Verifier Trust Store are specified incompatibly.
  - **RV6-C-M1**: out-of-project ignore sources (RV5-M7) remain, fail closed.
- **LOW:** RV6-C-L1…L6 (`01`).
- **Held-out:** RV6-C-A01…A19 (`02`); 0 blocking.
- **Residuals:** none NOT ACCEPTED; conditions in `03`.

**Verdict: `NO_BLOCKING_FINDINGS`.** No CRITICAL or HIGH. Every MEDIUM is carried as a bound, testable requirement that
changes no trust relationship (`04` CR6-C-1…12). RV6-C-M2 is stated with its escalation condition: if an implementation's
`init` on `ABSENT` ignores or overwrites an existing `governance/overlay`, the outcome is a silent persistent classification
loss (HIGH), which CR6-C-7 forbids.

## Output files

| File | Content |
|---|---|
| `00-REPORT.md` | this report |
| `01-FINDINGS.md` | RV6-C-M1…M5, RV6-C-L1…L6: statement, evidence class, failure scenario, severity, correction direction |
| `02-HELDOUT-ATTACKS.md` | RV6-C-A01…A19 |
| `03-RESIDUALS.md` | residual criteria and determinations |
| `04-CARRIED-REQUIREMENTS.md` | CR6-C-1…12 and C-2…C-6 with acceptance tests |
| `05-PRE-ROT-MATRIX.md` | registers, trees, the 62,036-row matrix, properties, durability |
| `evidence/` | probes, outputs, reproduction, `REVIEWED-CONTENT-DIGESTS.txt`, README |
