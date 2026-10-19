# W2-49 (DAEO-ha8z) — lead checkpoint, 2026-10-17 (run 2, the apply round)

## RESUME HERE

**State:** DONE, held for the close order (DEC-737). The apply round of DEC-741 is done and verified green. Nothing is merged into `w2/integrate`; the ticket is not closed.

- Worktree `/home/usain/gov-os-worktrees/W2-49`, branch `w2/W2-49`, cut from `w2/integrate` at `a02e3485`; `w2/integrate` merged in at `1b43c73c` (approved paths, DEC-741).
- Branch head: the lead's hold checkpoint commit after `b9e4917e` (see `git log --oneline -8`).

## What the resume lead does (after W2-01 AND W2-51 have closed)

1. Merge `w2/integrate` into `w2/W2-49` with a merge commit carrying `Task: DAEO-ha8z` and `Role: orchestrator` (final trailer block). A conflict on the Contract files or the capability records goes to the orchestrator (Contract text: the owner's).
2. A fresh independent test designer writes the tests of KPI success line 3 ("the plan validator's two-way check covers the moved parts") and the failure line ("a Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator") against W2-51's (DAEO-egsy) Wave 2 plan validator (DEC-744); the README already names them as pending W2-51. Check them red/green as the validator stands.
3. One full `PYTHONPATH=/home/usain/gov-os-worktrees/W2-49/src python3 -m gov.cli.main rebuild --json` (never `--no-embeddings`), in the background with an exit file, no worker running.
4. Every suite again (`tests/acceptance/<suite>` one by one, `tests/unit`), in the background; resume-able runner at `.gov-runtime/scratch/lead/run2-suites.sh` (point its OUT folder at a new name). The full run takes > 2 h on this machine: the Bash background limit (2 h) stopped run 2's first pass at W1-41; the runner skips suites with an exit file.
5. Never run `docs/plan/tools/validate_s1.py` (DEC-738).
6. Then the hold again / DONE to the orchestrator, who merges and closes.

**If the owner overturns the K (2) reading:** revert `7f935156` (a new commit) AND drop `tests/acceptance/W2-49/test_w2_49_capability_records.py` (designer's commit, `Rewrite-Reason:` naming the owner's decision). Nothing else imports it.

## Commits on this branch in run 2 (after `1b43c73c`)

| Commit | Role | What | Trailers |
|---|---|---|---|
| `6456e155` | independent-test-designer | 53 tests added (`test_w2_49_owner_answers.py` 45, `test_w2_49_capability_records.py` 8 = K (2) only), support readers, README (validator lines pending W2-51). No existing test rewritten. | Task, Role, Implements: DEC-722, Co-Authored-By |
| `9921c80f` | orchestrator (lead) | `CP-DAEO-ha8z-0009` after the red check | Task, Implements: DEC-722, Role |
| `90c4d20a` | product-spec | Contract v4.2 in `contract.yaml` and `CONTRACT_v4.md`; status ACCEPTED in both (W2-L343) | Task, Role, Implements: DEC-722, CAP-43.b, CAP-44.f, CAP-44.h, CAP-45.a, Co-Authored-By |
| `5a6a12f5` | product-spec | the version line in all 273 capability records (273 files, 1 line each) — K (1) | Task, Role, Implements: DEC-722, DEC-614, Co-Authored-By |
| `7f935156` | product-spec | the 8 CIT-P §8 records (CAP-43.b, CAP-44.f, CAP-44.h rewritten; CAP-43.d, CAP-44.k, CAP-44.l new; CAP-43/CAP-44 Covers) — K (2), the orchestrator's reading, own commit | Task, Role, Implements: DEC-722, DEC-614, CAP-43.b, CAP-44.f, CAP-44.h, Co-Authored-By |
| `b9e4917e` | product-spec | `docs/changes/W2-49-CIT-E.md` (APPLIED); CIT-P frontmatter ACCEPTED + §13 "The owner's answers (DEC-741)" naming W2-52 | Task, Role, Implements: DEC-722, CAP-33, Co-Authored-By |
| (next) | orchestrator (lead) | the hold's `gov checkpoint` record | Task, Implements: DEC-722, Role |

## The named read (C (i)) — made

- `docs/source/originals/GOVERNANCE_OS_ADOPTION_MIGRATION_AND_INDEPENDENT_AUDIT_PROTOCOL_v3.0.md` ("# 20. Final adoption verdict", lines 591–613) and `docs/source/originals/GOVERNANCE_OS_RELEASE_DISTRIBUTION_ADOPTION_AND_UPSTREAM_LEARNING_PROTOCOL_v1.2.md` ("# 18. Adoption acceptance", lines 625–644), each by exact name from `docs/SOURCES.md` lines 149–150, read once via `git show bb6ec3a8…:docs/source/<path>` after printing heading lines only. CAP-44.h lists the ten numbered (1)–(10): (3) W2; nine W3, five with a named lite part.

## Verification (run 2, at `b9e4917e`)

- `gov.__file__` = `/home/usain/gov-os-worktrees/W2-49/src/gov/__init__.py`; full rebuild exit 0 (`invalid: []`; lexical, semantic, codeintel recreated).
- `tests/acceptance/W2-49`: 129 passed. All 50 acceptance suites: 11481 passed, 30 skipped, 3 failed = W1-42's two named exceptions (RETR-X-02, the governance share; DEC-713/714) + W1-46 `test_the_sandbox_accepts_a_connection_to_a_starting_host_of_the_research_allowlist[static.crates.io]` (curl 56, network) which passed alone (file: 36 passed). Latency cases of W1-02 and W1-05 passed in the full run. `tests/unit`: 2100 passed, 1 skipped.
- Logs: `.gov-runtime/scratch/lead/log/run2-*`, suites under `log/run2-suites/`.

## Open (for the orchestrator / owner)

- K (2) awaits the owner's confirmation; CAP-45.a's record is stale (4.1 item text, 4.2 version line) — package.
- The eight `SOURCE_MAP.csv` rows (outside the paths) — not decided.
- KPI line 3 and the failure line: pending W2-51.
- W2-I017: carried, J (i), at W2-30's close (orchestrator). W2-L343: done in `90c4d20a`.
- DEC-741 and DEC-744 not yet in this worktree's register (owner's staged batch).
- Temporary folder left: `.gov-runtime/scratch/ps-run2/` (the apply worker's two throwaway scripts; its `rm -r` was refused; untracked; outside the lead's write area).

## Loop count

Held by the lead; converged.
