# AR-0021 evidence — independent compatibility & transaction review (C) of RoT-1 revision 7 (`d07d200`)

All instruments here are **original to AR-0021** unless the filename or header attributes them. The revision-7
installation-state predicate `c7lib.state_r7` is **encoded from the text** of `18` §9 (state table and precedence), §9.1
(closed entry sets, the `.gitattributes` member), §9.2 (root discovery and working-directory refusal) and §5.1 (honoured
journals, revision-7 identity and `done/` scan scope), `26` §2 (layout) and `20` §9 (record identity) at
`d07d200ac08a52c45071d33074e20cc62fbcc26e`. It does **not** import or copy reviewer C's `c6lib.state_r6`, the architect's
`crashmig7.state_r7`, or any pack instrument. Where the revision-7 text admits more than one reading, `state_r7` computes
**every** reading (field `by_reading`: `ABSENT/type` vs `ABSENT/path`, `LMI/narrow` vs `LMI/broad`) so a text ambiguity is
visible rather than resolved by the instrument.

The command registers (`register7.py`) are derived **twice** — from each real binary's `--help` recursion and from its own
`cli/src/main.rs` clap enums at its release commit (`git show`) — and cross-checked, without copying `register6.py`.

## Hygiene

Every child process runs under `env -i` with a constructed environment: `PATH`, `HOME`, `XDG_*` and `GOV_KERNEL_CACHE` in
scratch; **no other `GOV_*` variable unless a probe sets it explicitly as the object of the test** (the `P-ENV` matrix
rows). Git runs with `GIT_CONFIG_NOSYSTEM=1`, a scratch `GIT_CONFIG_GLOBAL`, `GIT_OPTIONAL_LOCKS=0`,
`core.hooksPath=/dev/null`. Whole-tree snapshots record **every** entry under the slot root (work tree,
`.governance-runtime/`, `.git/`, and for a worktree the base repository) by type, mode, size, SHA-256 and link count; each
matrix row records a before/after **whole-tree digest**, never a named path (forbidden assumption: a named-path digest does
not show that no write happened). No `rm -rf`/`rm -f` shell command was used; per-row scratch copies are removed with Python
`shutil.rmtree` inside the harnesses (scratch paths only). `__pycache__` is suppressed (`PYTHONDONTWRITEBYTECODE=1`).

The legacy binaries are the real `gov-4.1.{2,3,4,5}` copied read-only into scratch (SHA-256 in
`REVIEWED-CONTENT-DIGESTS.txt`). The pack text is read from a `git archive` of `d07d200` in scratch, so instruments that
resolve pack or canonical roots stay in scratch; legacy source is read with `git show` at `8ad06be`, `26ab5b6`, `47d8394`,
`da9c851` in the read-only review worktree.

## Evidence classes

- **E** executed with the real 4.1.2–4.1.5 binaries and/or real Git 2.43.0.
- **M** the pack's own revision-7 reference executor `evidence/r7/gov_admit_reference_r7.py` exercised (architecture
  evidence, not the product; `gov`/`gov-admit`/the install transaction machinery are unimplemented). Where the reference
  has a single parameter for something the text leaves open (which account's store a first admission moves aside), the probe
  wraps that path function and says so; the reference's decision functions run unchanged.
- **D** design reading of the pack at `d07d200`; every quoted sentence is extracted mechanically (`design7.py`) and printed
  so it can be checked, and a pattern that does not match is reported `NOT_FOUND`.

## Original instruments (`probes/`)

| Probe | Output | Class | What it tests |
|---|---|---|---|
| `c7lib.py` | — | — | the revision-7 predicate library (`state_r7` with every reading; whole-tree maps; root discovery; honoured-journal logic) |
| `register7.py` | `registers7.json` | E/D | each binary's full command register, derived twice (help + source) and cross-checked; env vars each source reads; `current_dir()` root fallbacks |
| `build7.py` | `build7.json` (+ trees) | E | a real 4.1.5 legacy project migrated to the revision-7 layout, plus the local per-project record state the transaction rules read; trees L0, R7, R7RES, R7CRASH, R7OPEN, R7V, R7WT |
| `gitops7.py` | `gitops7.json` | E | layout durability over 45 ordinary Git/tool operations incl. new ones (bundle, zip archive, clean on the machine, worktree at the pre-migration commit, reset --hard, `rm -r --cached . && add .`, skip-worktree, working-tree-encoding from three attribute sources, export-ignore, a locally configured smudge filter, symlinks/fileMode off, cp without dot-entries, merge/cherry-pick/format-patch of a legacy branch, submodule) |
| `matrix7.py` | `matrix7-summary.json`, rows | E | the independent pre-RoT command-register matrix on the revision-7 layout, positions P-ROOT/P-CWD/P-OPEN (inside an honoured transaction)/P-WT (git worktree)/P-ENV (incl. a kernel cache and source pointed into the account store and the installed kernel)/P-VEND/P-GIT/P-TXN |
| `struct7.py` | `struct7.json` | E | structural tampering and journal-honouring: occupation/type swaps, symlinks, member deletion/alteration, kernel edits, hard links (VU-12), planted/tracked/identity-mismatched journals, a foreign layout-migration journal, an honoured layout phase |
| `txn7.py` | `txn7.json` | E | held-out transaction attacks: a crash between the phase write and the step; ordinary and legacy operations between the crash and `gov recover`; two literal recovery readings (L, S); the first-install honouring condition; ABSENT with classified legacy-named content; uninstall's result; a shared per-project record updated by two worktrees without a lock; crashmig7's roll-forward branch |
| `adm7x.py` | `adm7x.json` | M | admission-as-state held-out attacks against the reference executor: multi-account first admission; protected store lost / account store kept; two machines sharing one home; clock high-water from an ordinary wrong-ahead clock; non-atomic `floors.json` versus concurrent reads |
| `ident7.py` | `ident7.json` | E | RV7-C-A05: every concrete identity a conforming implementation could record for "the Git common-directory identity ... never committed" (`20` §9), across worktree, moved checkout (same and cross filesystem), bind mount, second clone, fork, template copy, tar copy, reinit, `--shared`, and a different repo re-cloned at the same path |
| `cur7x.py` | `cur7x.json` | M+D | RV7-C-A25: a Trust State from offline media older than 24 hours used, on an admitted machine, for the anchoring event and the currency proof of a running-mode C3 transition; against OWNER-DESIGN-REQUIREMENTS-0002 OT-1 |
| `design7.py` | `design7.json` | D | the exact pack sentences each design-class finding rests on (extracted, not paraphrased), and the decision-record state fields (D-0008/D-0007/ARCH-0002) |

## Reproduction (`reproduction/`) — the architect's and prior review's claims, tested

Unmodified scratch copies run against the `d07d200` export (or the review r6 worktree for `register6`), compared with the
committed outputs:

| Instrument | Owner | Result |
|---|---|---|
| `register6`, `struct6`, `attrprec6`, `admtx6`, `crashmig6` | review r6 C (AR-0017) | **byte-identical** to the committed review-r6 C outputs |
| `gitops6` | review r6 C | every row's state, reasons and kernel-tampered flag **equal** (paths differ only by scratch prefix) |
| `matrix6` (12 workers, full) | review r6 C, re-run by the architect | **62,036 rows** (61,520 active, 516 skipped); every property, per-position aggregate and writing-command count **equal** to the committed review-r6 C summary and to **both** of the architect's revision-7 `matrix6` tree sets: R2-H4 **0 violations**, LP-1r 2,492 rows **0 project writes**, Git-op elevation into `COMPLETE` **0**, classification-lost 16 (LR-2 pre-migration checkouts), transaction-area 96 |
| `crashmig7`, `ADM7`, `PPR7` | architect (AR-0019) | **byte-identical** (verdicts and whole output equal) |
| `RV6-D-A07`, `RV6-D-A10` | review r6 D | **byte-identical** to the architect's committed re-runs |
| `CUR7` | architect (AR-0019) | **byte-identical** (14/14 verdicts equal) |

`REVIEWED-CONTENT-DIGESTS.txt` — SHA-256 of every reviewed pack blob (`release/root-of-trust/4.1.6/**`, `D-0008`,
`ARCH-0002`, `D-0007`, `docs/DECISIONS.md`) as the git object at `d07d200`, the review-r6 consolidated files read, and the
four legacy binaries.
