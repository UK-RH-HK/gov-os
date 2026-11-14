# W2-94 — one README map cell `gov accept` cannot read, the independent test designer's brief (DAEO-g87r)

You are a fresh independent test designer (class C2) under **W2-94** (`DAEO-g87r`; the ticket, read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`). Your folder `tests/acceptance/W2-94/` (391 cases,
all green) is merged into the ticket branch. `gov accept W2-94` refuses before running anything:

```
gov accept: ACCEPT_MAP_UNREADABLE: ticket DAEO-g87r: the README of tests/acceptance/W2-94/ has a map cell listing a KPI line it cannot read (README line 36: "S5 (W2-61's close record names KPI 6 as moved to W2-94)")
```

The map's KPI cells are read by `line_names` in `src/gov/accept/runner.py` (read its docstring, lines 72-98): every
line name in a cell's prose is read or refused, and `KPI 6` (W2-61's line, not this ticket's) is a line name it cannot
read. Every other row of the map reads (rows 30-35: success-1, success-4, failure-3, success-4, success-4, failure-1).

## The task
1. Re-word only the KPI cell of README row 36 so that it reads as this ticket's S5 (`success-5`) and names no other
   line: replace "KPI 6" by words that are not a line name (step 2 tells you whether the words read). Change nothing
   else in the folder.
2. Check the whole map reads, with this one-off check run from the tree (it prints each row's lines or UNLISTED):
   `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-tests/src python3 -c "import sys; from gov.accept.runner import parse_map; print(parse_map(open('tests/acceptance/W2-94/README.md', encoding='utf-8').read()).keys())"`
   It must print the five names success-1, success-4, success-5, failure-1, failure-3 (no error).
3. Re-run the folder once:
   `env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-94 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=short`
   (if the slot tool cannot run in your sandbox, run the same pytest without it and say so; a resource gate's refusal is
   a wait).

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-94-tests`, branch `w2/W2-94-tests`, at `83beeb8f6311` (your earlier commit).
  Write only `tests/acceptance/W2-94/README.md`.
- Walls: never open `~/gov-os-eval/`, `~/gov-os-runs/`, any `hidden` folder or any `fixtures/evaluation/examin/` folder of
  another tree. No GPU, model, network or installs. One simple command per Bash call. No merge inside the sandbox.
  Refused twice for the same call: stop and say so; never work around a refusal. No `gov retrieve` or `gov context`.
- **Commit** on `w2/W2-94-tests`, only the README, with
  `--trailer "Task: DAEO-g87r" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-957, DEC-954" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (task, status,
  work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved,
  recommended_next_action; sandbox and `ps` checks first), the check's printed names, the folder's counts, the commit and
  `TESTS-READY <hash12>`.
