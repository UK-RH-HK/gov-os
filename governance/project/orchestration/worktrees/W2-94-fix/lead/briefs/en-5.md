# W2-94: the W2-149 counts-schema pin takes S13's optional root key `fix`, the engineer's brief (DAEO-g87r)

You are a fresh engineer (class C3) under **W2-94** (`DAEO-g87r`; the ticket is read-only:
`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-g87r.md`, KPI lines S12 and S13 and the ticket body's
"Path case 2026-11-14 18:05" paragraph). Worktree `/home/usain/gov-os-worktrees/W2-94-fix`, branch `w2/W2-94-fix`
(head `820f5d3ab`). The ticket's context bundle (built by `gov context DAEO-g87r --role engineer`) is
`/home/usain/gov-os-worktrees/W2-94-fix/.gov-runtime/scratch/lead/briefs/ctx-en-5.md`; read its `ticket_text`.

## The one revision (the CTO's path case P-W2-94-S13-1 (a), DEC-1156 (7))
You change **one file only**: `tests/unit/orchestration/test_w2_149_indep_launch.py`, and in it **one thing only**:
in `test_counts_schema_closes_every_object_and_string` (about lines 1088-1116), the hard-coded `optional` map gains an
entry for the whole schema's root, `id(whole): {"fix"}`, in the file's own form (beside the two entries already there).
Nothing else in that file changes (no other line, comment, case or import), and no other file changes: not the schema,
not `indep_launch.py`, not any acceptance test, wall or brief.

Why: S13 added an optional root property `fix` to
`governance/project/orchestration/tools/indep-schemas/indep-counts.schema.json`; the case requires every root property
to be required unless the `optional` map names it, so it is red now.

## The failing output (your input)
```
FAILED tests/unit/orchestration/test_w2_149_indep_launch.py::test_counts_schema_closes_every_object_and_string
```

## Must be green after your change (run each)
- `tests/unit/orchestration/test_w2_149_indep_launch.py` (whole file; the target case now green)
- `tests/unit/orchestration/test_w2_173_indep_launch.py`, `tests/unit/orchestration/test_w2_178_indep_launch.py`,
  `tests/unit/orchestration/test_w2_94_fix_flow_unit.py`
- `tests/acceptance/W2-94/` and `tests/acceptance/W2-149/` (whole folders)

## Pytest, every run (a resource gate's refusal is a wait, not a refusal)
`env HOME=<an empty folder under your $TMPDIR> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-94-fix/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit" --tb=line`
If the slot tool cannot run in your sandbox, run the same pytest without it and say so. Use your sandbox's own `$TMPDIR`
for every temporary file, never a new folder under `.gov-runtime/scratch/`.

## Walls
- Never open, list, grep or print anything under `/home/usain/gov-os-eval/`, `/home/usain/gov-os-runs/`, any folder named
  `hidden` outside a test's `tmp_path`, any `fixtures/evaluation/examin/visible` or `hidden` folder, EXAMIN's real
  repository or the owner's copy.
- No model, network or installs. One simple command per Bash call; longer things in a script file under `$TMPDIR`. No
  merge. No `gov retrieve` or `gov context`: search with Read and Grep, and search again once in different words.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit
Every trailer in ONE final paragraph (no blank line between them):
`git commit -m "W2-94 (DAEO-g87r): the W2-149 counts-schema pin's optional map takes S13's root key fix (P-W2-94-S13-1 (a))" --trailer "Task: DAEO-g87r" --trailer "Role: engineer" --trailer "Implements: DEC-1180" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/unit/orchestration/test_w2_149_indep_launch.py`

## Return (your final message, in full)
The twelve labelled fields, each one line or "none": task, status, work_completed, files_changed, evidence (each suite's
pass/fail counts, `git diff --stat` of your commit, and the commit hash), tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action.
