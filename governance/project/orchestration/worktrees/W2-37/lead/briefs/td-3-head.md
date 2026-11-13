You are a fresh independent test designer (MR-3). Ticket: DAEO-6n5k (W2-37, "gov impact"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-37-tests` on branch `w2/W2-37-tests`. The suite `tests/acceptance/W2-37/` exists and the implementation is committed; the second independent review found behaviours the suite does not hold (owner's DEC-812: fixed in this resume, a test-design batch first, DEC-136). You add one batch of new acceptance cases holding each behaviour below, red against the current code where the code does not yet hold it, and the README updated to map them. You change no existing case's assertions.

## Standing rules
- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-6n5k`); `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-37-tests`, `w2/W2-37-tests`); `git rev-parse HEAD` (expect prefix `64ccbd0cc`). If anything differs, stop and say so.
- DEC-732: every test run uses this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src` per command. Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src python3 -c "import gov; print(gov.__file__)"` in your return.
- **Every pytest runs through the heavy slot**, with a TMPDIR outside the repository and outside ~/gov-os-runs:
  `env TMPDIR=/tmp/gov-os-w237-td PYTHONUSERBASE=/home/usain/.local PATH=/home/usain/.local/bin:/home/usain/.nvm/versions/node/v22.23.3/bin:/usr/local/bin:/usr/bin:/bin PYTHONPATH=/home/usain/gov-os-worktrees/W2-37-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-37 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfs`
  (make the TMPDIR first with `mkdir -p /tmp/gov-os-w237-td`). A "all slots taken; waiting" line is a wait, not a refusal. Never `-x`.
- Run everything in the foreground. Return only after your commit exists. No checkout of another commit, reset, clean, stash, amend, rebase, merge, push or tag. Stage by exact path, never `git add -A`/`.`.
- Write files with the Write and Edit tools and literal absolute paths; anything longer than one line of shell goes in a script under `/home/usain/gov-os-worktrees/W2-37-tests/.gov-runtime/scratch/`. No here-documents.
- Never run `gov rebuild`, `gov close`, `gov adopt`, `gov pause`, `gov retrieve` or `gov context`. Search with Read and Grep; search again once in different words if the first does not answer.
- Never read `.claude/settings*.json`, anything under `~/.claude/`, the held-out file under `governance/project/`, the evaluation sets' root, or any hidden or memory-verdict folder. No glob/search/listing over `governance/project/`.
- Cases that build a code index are marked `local_only` (as the suite does); inside the sandbox the code graph's `/tmp/gov-cbm-<uid>` may be read-only: then they error at setup; say which they are, the lead runs them outside.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so. Never work around a refusal.

## What you read
- The ticket's KPI lines (in the context below; note DEC-1083 lifted the CIT-P/CIT-E lines; the query remains, and DEC-812 still asks these fixes).
- The suite and README `tests/acceptance/W2-37/` (fixtures, `w2_37_support.py`, readings R1 to R11). Build on its fixtures and helpers. Public interfaces only: the `gov impact` command line and its JSON output (`graphs`, `complete`, `gaps`, `change`, `affected`, `radius`, `--out`, `--compare`, `matches`, `differences`), `gov.store.load`. Never read `src/gov/impact/` to learn what a test should expect.

## The behaviours to hold (DEC-812 (1) and (2); each a success and a failure, no combinatorial expansion)
1. **A (compare against the proposal as committed).** A CIT-P (listing DEC-002 among its affected decisions) was committed and the store loaded; a CIT-E without DEC-002 gives `matches: false`. Then DEC-002 is removed from the CIT-P file in the working tree, not committed: `--compare` must not report `matches: true` with no differences. Accept either: the comparison uses the proposal as the store/HEAD holds it (so DEC-002 is still a difference), or it refuses / reports not matching while the CIT-P file differs from HEAD, naming the file.
2. **B (a register's first uncommitted entry).** The decision register named by the repository's path map has no entries at HEAD; the store is loaded; a first entry (e.g. DEC-090 with `**Supersedes:** DEC-001`) is added to it and not committed. `graphs.record` must not read `ok`: it reads `stale` (naming the register's path). Include the variant where the register sits in a non-governance namespace of the path map, where the report must not read `complete: true` while missing DEC-090 (`local_only` if a current code graph is needed for `complete` to matter; keep a variant that holds `graphs.record` alone without the code tool). The already-right case (the register holds one entry at HEAD, a further uncommitted entry reads `stale`) stays as a success guard.
3. **C (an incomplete proposal's match carries its incompleteness).** A CIT-P written with `complete: false` (and gaps) and a CIT-E with the same lists: the compare result carries the proposal's `complete: false` and its gaps (it may still say `matches: true`).
4. **E (refusals name their real cause).** `--compare` naming a CIT-P file that does not exist is refused naming that the file is missing (not "lists nothing under affected"). `--out ""` and `--out <an existing folder>` are refused naming the real cause (an empty path; a folder), not "a file is there already". Each still exits 1 with no traceback and writes nothing.
5. **F4 (`--out`'s stem against existing ids).** `--out` whose file stem is an id that already exists in the store (e.g. `CITP-001.md` when CITP-001 is a stored record, written to a new path) is refused naming the clash, and writes nothing.

## What you write
- Only inside `tests/acceptance/W2-37/`: one new file `test_w2_37_resume_findings.py` (helpers in it or added to the support module without changing existing helpers' behaviour), and a README section for this batch mapping each behaviour to its tests, its expected red reason, and which are `local_only`. Deterministic, no network, temporary repositories only.
- Red first: run the suite to its end. The new cases fail for the stated reason where the code lacks the behaviour; every existing case keeps its result (the three known reds stay red: the depth source and the two skill-routing cases).

## Commit
    git commit -m "W2-37: acceptance tests for the second review's findings A, B, C, E and F4 (red)" --trailer "Task: DAEO-6n5k" --trailer "Role: independent-test-designer" --trailer "Implements: CAP-33.b, DEC-167" --trailer "Rewrite-Reason: test design batch for the second review's findings A, B, C, E and F4 (DEC-812, DEC-136); no existing case changed" -- tests/acceptance/W2-37
Then show `git log -1 --format='%H%n%B'` and `git status --short`.

## Return (your last message; the twelve fields as labelled lines, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
In `tests:` give each new case with its result (red, green or error at setup) and reason, and the full suite's counts. Then `guard_refusals:` (none, or each refusal's command form and reason).

## The ticket's context (gov context, built by the lead outside the sandbox)
