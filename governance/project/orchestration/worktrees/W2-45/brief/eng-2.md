# Brief: engineer, DAEO-neam (W2-45), run 2 (batch 2: S1, the decision checker's speed)

You are a fresh engineer. Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2, in `/home/usain/gov-os-worktrees/W2-45`
on branch `w2/W2-45`. Batch 1 (commit `3ed6f53118d1`) implemented the ticket's `## Interface` items 1, 2, 4 to 7 in
`src/gov/check/runner.py`. The lead has merged the acceptance tests (`tests/acceptance/W2-45/`, merge `1b2c0f687`):
31 of 32 cases pass; the two S1 cases are red. Your one job: make S1 green by making the decision checker fast,
without changing what it finds (Interface item 3). You never change the Interface, the runner's result shape, or any
test under `tests/acceptance/`.

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-neam`), `printenv TMPDIR` (the sandbox's temp
  folder: call it T below and write it out literally in every command), and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-45`, `w2/W2-45`).
- Everything in the foreground; return only after your commit exists. No `git checkout` of another commit, `reset`,
  `clean`, amend, rebase, merge, push or tag.
- **Allowed paths (write only these):** `src/gov/decisions/checker.py` (speed only: the same findings on every input),
  `src/gov/check/runner.py`, `tests/unit/check/**`. Never write `tests/acceptance/`.
- **Scratch:** `/tmp` is read-only and the Write tool is refused under `.gov-runtime/scratch/` for you (batch 1).
  Put every scratch script and file under T, `mkdir -p T/w2-45-eng` first; write scripts there with the Write tool at
  the literal path and run them with `python3 <file>` / `bash <file>`.
- **Code under test (DEC-732):** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src` per command; quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src python3 -c "import gov; print(gov.__file__)"`.
- **Every pytest goes through the heavy-job slot**, TMPDIR outside the repository and outside `~/gov-os-runs` (T is),
  `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, e.g.:
  `env TMPDIR=T/w2-45-eng PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-45/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-45/test_s1_decision_checker_scale.py -q -s -p no:cacheprovider -o tmp_path_retention_policy=failed`
  (one command, no `&&`, no pipe). A whole-folder run adds `-m "not local_only" -k "not real and not green_here and
  not time_limit"` and `HOME=/home/usain/gov-os-worktrees/W2-45/.gov-runtime/scratch/empty-home`. Never `--basetemp`.
- **Reads (DEC-820):** open, except secrets and keys, the held-out qualification material's contents (never under
  `governance/project/`), the hidden half of any evaluation set. The acceptance tests are now in your tree: read them.
- **Search (DEC-1065):** no `gov retrieve`, no `gov context`; Read and Grep, search again once in other words. Grep the
  register only by id. No search from the repository root, `governance/project/` or `.claude/`.
- **Command forms:** no shell variable as a write target, no here-document, no backticks, no `bash -c '…'`, no long
  inline `python3 -c`, no compound `&&` / pipe chains around pytest.
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another command, form or file
  (DEC-1142 (9)); return it as a package.
- Never copy the repository. Install nothing. No subagents that write. Never ask the owner. Hashes: 12 digits.

## The failing output (the lead's run at merge `1b2c0f687`)

```
FAILED tests/acceptance/W2-45/test_s1_decision_checker_scale.py::test_s1_decision_checker_runs_within_the_gov_check_budget_on_200_decisions_and_20000_commits
FAILED tests/acceptance/W2-45/test_s1_decision_checker_scale.py::test_s1_the_decision_checker_answered_and_did_not_fail
core-authority: {"status":"RED","findings":[{"code":"CHECK_TIMED_OUT","time_limit_s":60,...}],"elapsed_s":60.079,"time_limit_s":60}
assert ('CHECK_FAILED' not in ['CHECK_TIMED_OUT'] and 'CHECK_TIMED_OUT' not in ['CHECK_TIMED_OUT'])
```

The planted repository is `w2_45_support.repo_with_decisions` (200 ACTIVE decisions under `docs/adr/`, each set by an
owner's commit, 20,000 commits, every second later commit revising a decision). The lead's reading, for you to check:
`_approved` in `src/gov/decisions/checker.py` walks the ancestry from `HEAD` one commit at a time for each ACTIVE
decision until the commit that set it (`_held` per commit, a `cat-file` read of `commit:path` and its parent), so the
cost is about decisions x commits. One way, if your measurement agrees: learn once, in one git pass (e.g. one
`git log --raw -z --no-renames --format=...` or `git rev-list --parents` plus `git diff-tree --stdin`), which commits
change which Markdown paths, and let a single-parent commit that leaves `path` unchanged continue its parent without
reading anything. Merges, moves, removed files and every rule in the module's docstring must give the same answer.

## The work

1. Profile S1 (the acceptance case above with `-s`, and a profile script under T). Record the before figure.
2. Make `src/gov/decisions/checker.py` fast enough that core-authority's `elapsed_s` on that repository is well
   under 60 (aim < 20 s on this loaded machine), with the same findings. If the runner adds cost (core-authority runs
   `python3 -m gov.check.authority`, see `src/gov/check/authority.py`, which is not yours), say so.
3. Prove "same findings": the existing suites green, through the slot: `tests/unit/decisions`, `tests/unit/check`,
   `tests/unit/gitenv`, `tests/acceptance/W1-26`, `tests/acceptance/W2-150`, `tests/acceptance/W2-01`,
   `tests/acceptance/W1-21`, and all of `tests/acceptance/W2-45`. Add unit tests in `tests/unit/check/`
   (`test_w2_45_*.py`) only if they show the speed path keeps an answer the suites do not cover (a single-parent commit
   that does not touch the file; a move; a merge).
4. Do not touch `tests/acceptance/W2-95/` even though one of its cases (`test_w2_95_other_checks_results_do_not_change_with_core_pathmap`)
   is red at this head: that is the lead's package to the CTO (the case compares whole entries and `elapsed_s` is a
   wall time). Do not move or drop `elapsed_s` to make it pass.

## Commit

    git commit -m "W2-45: <subject>" --trailer "Task: DAEO-neam" --trailer "Role: engineer" --trailer "Implements: DEC-729" -- <your paths>

(`git add` a new file first.)

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: (DONE | PACKAGES | ESCALATION ...) / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include: the sandbox check first in `evidence`; commits (12 digits) with trailers; before/after `elapsed_s` of
core-authority on the S1 repository; each suite's counts; the `gov.__file__` line; read refusals; scratch figures
(`du -sh`, `du -s --inodes` of T/w2-45-eng, removed at the end); any package.
