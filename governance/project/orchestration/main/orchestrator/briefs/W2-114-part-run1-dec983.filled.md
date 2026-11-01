You are the ticket lead for ticket `DAEO-4eux` (`W2-114`, "W1-28's whole-tree copy check reads code, not message text"), profile LITE, a test-revision ticket under the owner's named decision (DEC-906, given in DEC-982). You work only in the worktree `/home/usain/gov-os-worktrees/W2-114` on branch `w2/W2-114`. Keep it tight: it is small and runs alongside the critical chain.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `b716d349b077`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-4eux.md`) and its WBS row in `docs/plan/WAVE_2_WBS.md`;
- DEC-982, DEC-977, DEC-385, DEC-906 and DEC-892 in `docs/DECISION_REGISTER.md`;
- `governance/project/orchestration/packages/P1-NEW-TICKETS-2026-10-31.md`, T2;
- W1-28's suite: `tests/acceptance/W1-28/test_w1_28_fixture_copies.py` and its `README.md`;
- what refused the batch of six on 2026-10-31: W2-108's scope test before its fix (`git show 789513df655c:tests/acceptance/W2-108/test_w2_108_scope.py`; its skip message named the repository root and the words "git worktree") and its fix (`git show 6c8afc7f`).

## Why you start now

W1-28's check reads the text of skip, fail and assertion messages as if it were code. On 2026-10-31 that refused a batch close for a test that copies nothing (DEC-977), at a cost of about 3 hours of batch run and a resume. The next message that names the root will do it again.

## The decisions for this run

- **One worker: a fresh independent test designer** (sandboxed through `gov launch`, `--effort high`), working in this worktree, as W2-90 (also LITE) ran. It is the ticket's only writer, so no tests worktree is needed (one writer per worktree). There is no engineer and no code change. You do not edit the tests yourself.
- **What the test designer does:**
  - the check ignores the arguments of `pytest.skip`, `pytest.fail` and assertion messages (string literals and f-strings in those positions), and looks for whole-tree routes only in argument lists and in `subprocess`, `os.system` and copy calls (for example `shutil.copytree`, a `cp -r` argument list, `git worktree add`, `git clone` of the repository);
  - **planted true copies are still found:** in a temporary folder, planted test files with a `cp -r` of the root, a `shutil.copytree` of the root, a `git worktree add` and a `git clone` of the repository, each inside a test function, and each is reported by the revised check as today; and a planted file whose skip message names the root and "git worktree" is not reported;
  - the README says what the check reads and why message text is left out, with `Rewrite-Reason: DEC-982`;
  - lowering nothing (MR-3, DEC-906): no route the check finds today is lost; no case removed or skipped.
- **Then, yourself:** W1-28's file alone to its end, and the planted cases; then the scoped set once (DEC-968): every suite goes through `verify_lock.sh`, which takes a heavy-job slot (DEC-983; no load wait). Any red the change did not cause is named for the CTO.
- **No review** (LITE).
- **Files kept clear:** only W1-28's two files. Nothing under `src/`, nothing of the critical chain (`src/gov/retrieval/**`, the path map).
- **If a step is held for more than 90 minutes:** write your checkpoint and return PACKAGES.

## This run's order

1. The test designer's batch (sandbox check first; its return checked for the twelve fields).
2. W1-28's file alone; the planted cases; the scoped run.
3. Return DONE (the branch ready to merge) or PACKAGES.

**Estimate:** about 40 lines of test; about 1.5 to 2 hours.
