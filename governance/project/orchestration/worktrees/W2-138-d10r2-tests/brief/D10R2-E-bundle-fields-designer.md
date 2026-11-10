Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-138-d10r2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 run 1's red groups E and H (8 cases): search results that differ from the pinned form (DAEO-rmhj, W2-138)

You are a fresh **independent test designer**, launched under W2-138's ticket (`.tickets/DAEO-rmhj.md`), which most
likely changed what these cases pin. D-10 (DEC-1122 (3)) needs each one traced and fixed before run 2.

## The reds (integrate's head `c9742b08910a`; each red alone too)
- E: `tests/acceptance/W2-131/test_w2_131_unchanged.py` (2): `fields that changed beside the register items' ids: ['continuation']`;
  `tests/acceptance/W2-135/test_w2_135_unchanged.py` (4): `almanac-batched, page 1: the bundle's 'continuation' changed`.
- H: `tests/acceptance/W1-21/test_w1_21_command.py` (1): `assert {'batches': [...]} == {'batches': [...]}` (a structure differs);
  `tests/acceptance/W2-04/test_w2_04_batches.py::test_a_lookup_failure_is_named_in_dropped_by_its_kind` (1):
  `a damaged index is not named in dropped by its kind: [{'id': 'supplementary', 'reason': 'the lexical index is unreadable'}]`.
Candidates since the cases were written: W2-138 `dcda27011` (11-07: the store's commit and folder in every search
result; CONTINUATION_INVALID), W2-32 S11 `9446d3225` (11-05: the pool order carried in the continuation token).

## The task
1. For each red, find the commit that changed the behaviour and read what that ticket decided (its ticket file,
   its acceptance tests, the register entry it cites).
2. If the change is the decided behaviour, revise the case to the new form without lowering what it checks (e.g. the
   `unchanged` cases still prove nothing but the register ids changed, with the token's new content accounted for).
   If the product broke what a KPI requires, change nothing for that case and report it as a product red (the CTO
   gives it to an engineer).
3. Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=<your tree>/src`:
   `python3 -m pytest tests/acceptance/W2-131 tests/acceptance/W2-135 tests/acceptance/W1-21/test_w1_21_command.py tests/acceptance/W2-04/test_w2_04_batches.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
   Report counts before and after; a case needing a GPU or real model is named, not forced.
4. One line in each changed suite's README.

## Where you work
- Worktree `/home/usain/gov-os-worktrees/W2-138-d10r2-tests`, branch `w2/W2-138-d10r2-tests` (from integrate at
  `c9742b08910a`). Write only `tests/acceptance/W2-131/**`, `W2-135/**`, `W1-21/**`, `W2-04/**`.

## Rules
- `EMG-common.md` holds. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No installs, never the full suite.
- Commit on your branch only, with `--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1122"
  --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: <the commit and decision that changed the form>"
  --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"`. Never merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short: per red its cause commit, test or product, the change, counts.
