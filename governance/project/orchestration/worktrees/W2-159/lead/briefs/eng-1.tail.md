
## Rules
- Test first: for each KPI line a unit test in tests/unit/session_watch/ that plants its case (a tmp root, the hook's
  JSON on stdin or passed to the function, the environment overrides), seen red, then the code. Never a live
  session, never `/proc` in a test (always `GOV_SESSION_WATCH_PS`), never a hook registered in any `.claude/`.
- The Interface is the contract: do not change it. A gap or contradiction comes back as a package (in `unresolved`
  and status PACKAGES if it blocks you), never an interface choice of your own; an inner choice (module layout,
  function names, message wording beyond what the reading above fixes) is yours.
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`,
  one folder per run, as one line:
  `mkdir -p /tmp/w2-159-eng && env TMPDIR=/tmp/w2-159-eng HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/session_watch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  End with tests/unit/session_watch green, and run once each of tests/unit/cli (or the folder holding main.py's
  tests: find it with Grep for `_module_name` or `gov.cli.main` under tests/unit) and the tests of
  `gov.check.commands` (Grep `check.commands` under tests/), the same way: report their summary lines.
- Commit in batches (the route; the checks; the fixes), your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: engineer" --trailer "Implements: DEC-1027, DEC-1110" -- src/gov/session_watch src/gov/check/commands.py src/gov/cli/main.py tests/unit/session_watch`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088,
  DEC-1119, DEC-994, DAEO-cb2b; name the ones each commit carries.) The lead may merge the acceptance tests into
  your branch between your batches: commit before a long pause, and `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under `.gov-runtime/scratch/eng/` run with `bash` or
  `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/` or `tests/acceptance/`. No install, no
  network, no `.claude/`.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (each KPI: where it is built, file:line) / files_changed / evidence (the pytest summary lines) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
