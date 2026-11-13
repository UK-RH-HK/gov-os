
## What to do
- B1: a unit case first (red), then the fix; the existing cases stay green. Keep the 900 s slack a named constant.
- B2: a unit case first (red: the two records interleaved, deterministic, no sleeps), then the fix (e.g. re-read the
  state file and merge this check's record just before writing, under a short file lock or an atomic replace; or any
  inner choice that keeps one shared `state.json` keyed by check, as the Interface says). An error in that step is
  still S4's: the turn ends, named in `systemMessage` and the log.
- No name, path, folder or ticket id of this repository in src/gov/session_watch (S5, F3), comments included.
- Then run tests/unit/session_watch, then tests/acceptance/W2-159 (read and run it; never edit it), each green.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside ~/gov-os-runs
  (the sandbox's own `$TMPDIR`: `/tmp` is read-only there), `PYTHONUSERBASE=/home/usain/.local`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`, one folder per run, as one line, run in the background
  with its output to a file (the gate may queue for a while: all slots can be taken), e.g.:
  `env HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/session_watch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- One commit (or one per behaviour), your paths only (`git add` a new file first):
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: engineer" --trailer "Implements: DEC-1110, DEC-1109" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/session_watch tests/unit/session_watch`
  The lead may merge acceptance tests into your branch between your commits: commit before a long pause, and
  `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under the sandbox's `$TMPDIR`. Use literal paths. Never touch
  `.gov-runtime/scratch/lead/` or `tests/acceptance/`. No install, no network, no `.claude/`, never a live session or
  a hook registered anywhere. Search with Read, Grep and Glob; search once more in other words if the first does not
  answer (DEC-1065).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (each behaviour: file:line) / files_changed / evidence (each run's pytest summary line) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context packet (gov context at 08:40 UTC; the ticket text is unchanged since; today's call answers CONTEXT_OVER_CEILING)
