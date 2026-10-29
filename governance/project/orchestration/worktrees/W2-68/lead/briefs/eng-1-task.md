You are a fresh engineer (brief A2 of the Wave 2 prompt). Ticket: DAEO-2gc7 (W2-68), "Batched closes, reuse on the same code, and two fingerprints", profile FULL. You work in this worktree only: `/home/usain/gov-os-worktrees/W2-68`, branch `w2/W2-68`.

First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-2gc7`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-68` and `w2/W2-68`). If anything differs, stop and say so.

## What you read

- The ticket file `.tickets/DAEO-2gc7.md` (its KPI lines, success and failure; its `allowed_paths` and the limits on each), its card in `docs/plan/WAVE_2_WBS.md` §2, and the decisions DEC-883, DEC-889 items 2 and 4, DEC-890, DEC-880, DEC-899 in `docs/DECISION_REGISTER.md`.
- **The design note `docs/research/W2-68-batched-close.md`: it is the design you build.** Its sections 11 ("Settled points") and 12 ("Corrections") hold over the sections before them. Where you find the design cannot be built as written inside the allowed paths, do not invent another design: return it as a decision package, and build what is not blocked.
- The code you touch and the code it calls, and anything else in the repository you need (DEC-820).
- **Never read the acceptance tests' code** (DEC-820 (c)): nothing under `tests/acceptance/W2-68/`, by any tool. You may run them and read their results (names, pass or fail, failure messages).

## Your task: <BATCH>

## How you work

- Write only inside the ticket's `allowed_paths`, within the limit each one carries: `src/gov/close/batch.py` and `src/gov/close/fingerprint.py` (new); `src/gov/close/command.py` for the calls and the record's lines only; `src/gov/close/repo.py` for the store-freshness check only; `src/gov/store/**` for the fingerprints a rebuild records and the incremental record load only; builder tests in `tests/unit/close/test_batch*`, `tests/unit/close/test_fingerprint*`, `tests/unit/store/test_fingerprint*`; and the design note. Never `tests/acceptance/**`, never another file (`select.py`, `evidence.py`, `nightly.py`, `src/gov/rebuild/**`, `src/gov/retrieval/**` are not yours: call them, never change them). If the design needs a change outside these paths, return a package.
- **Fail closed everywhere** (the ticket's failure KPIs): a fingerprint that cannot be computed means a fresh run (no reuse, no incremental load, no fingerprint equality); a run that failed, was cut short or lacks its JUnit XML is never reused; a store on another code fingerprint is stale. Never make a gate decision fail open.
- Proportion rule (DEC-135): no code for edge cases beyond the KPIs and the design. Match the surrounding code's style (docstrings, naming, comment density, `GovError` codes and messages).
- Builder tests go in the ticket's unit-test paths, as regression evidence only. No `conftest.py` anywhere (DEC-919).
- Run, before you commit: your builder tests; `tests/unit/close` and `tests/unit/store`; the acceptance suite `tests/acceptance/W2-68` (read only its results); and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` (quote its last line: no collection error). Every run with `TMPDIR=/tmp/gov-os-lead-W2-68`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-68/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, to its end. Report which acceptance cases pass and which still fail, with their failure lines; failing cases that belong to a later batch are expected.
- Commit your work (code and builder tests) in one or more commits, each by path: `git commit -m "<subject>" --trailer "Task: DAEO-2gc7" --trailer "Role: engineer" --trailer "Implements: DEC-883, DEC-889, DEC-890" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>`. Commit before any long run.
- **Your scratch share:** 6 GB and 300,000 files and folders. **Time:** about 90 minutes; if the batch does not fit, commit what is done and green, and say what is left.
- Your return also gives: your commits, the lines added and removed (`git diff --stat` of your commits), and each acceptance case's state.

