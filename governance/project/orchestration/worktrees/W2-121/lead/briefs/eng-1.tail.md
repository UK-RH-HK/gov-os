
## Rules
- Unit tests in tests/unit/dispatch/, everything planted under tmp_path (a git project with an integration branch and
  worktrees, a tmp HOME with gate.json, GOV_RESOURCES_* variables, a planted /proc folder, a stub launch command and a
  stub notifier); never the real HOME, ~/.claude, ~/gov-os-worktrees, a real session or the real crontab. Cover every
  refusal S6 names (uncommitted claim, shut gate, no room for a peak, running ticket, unread return, malformed list
  line, hung command, crash after a launch).
- Nothing project-specific in `src/gov/dispatch/`: no `w2/integrate`, `w2/W2-`, `/home/usain`, `gov-os-worktrees`,
  `Dynamic-Agentic-Engineering-OS`, `.gov-runtime/scratch/orchestrator`, `DAEO-xxxx` or `W2-<n>` in code, comments or
  defaults (the test designer greps for them). Generic examples in docstrings use `<W2>`-style placeholders.
- Before you return, run your suite and the neighbours you import, whole-folder form:
  `env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  for tests/unit/dispatch, tests/unit/resources (if present) and tests/unit/cli (if present); report each summary line.
- Commit in small batches (the lead merges the tests between them; never edit while a merge is announced), your paths
  only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: engineer" --trailer "Implements: DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003" -- <your paths>`
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/;
  literal paths as write targets. Never touch .gov-runtime/scratch/lead/.
- In the module docstring of `src/gov/dispatch/__init__.py`: each KPI line, what implements it (function names), and the
  lead's readings you followed or departed from.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (pytest summary lines per suite; the line count of src/gov/dispatch/) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
