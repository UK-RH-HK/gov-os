
## What to do
1. B1, in test_s2_idle.py (or a new file): a pid file written 2 days ago whose pid is now a live process started
   10 minutes ago, one unblocked item, nothing else running: a block naming the item, and the pid not named as
   running. A control at the slack's edge if you can plant it cleanly (a process started 10 minutes after the file
   was written still counts as running). The README row S2 (and F1 if it is a legitimate-wait case) lists them.
2. B2, in test_s3_once_a_turn.py (or a new file): the two checks' records interleaved on one Stop, deterministic, no
   sleeps and no timing race: e.g. the idle check's `GOV_SESSION_WATCH_GOV` plan stub, while it runs, runs the waiter
   check for the same session and turn (both block), then prints the plan; afterwards the state file holds both
   checks' records, and a third waiter call in the same turn without `stop_hook_active` says nothing. The README row S3
   (and F1: "a turn blocked twice") lists it.
3. Test the interface only (the command, stdin and stdout, the configuration, the runtime files, the log); never import
   `gov.session_watch`. Update the counts line.
4. Run the new cases (red on B1 and B2 for the behaviour, not for an error in the test), then the whole folder (every
   other case green); `--collect-only` lists every case.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside ~/gov-os-runs
  (the sandbox's own `$TMPDIR`: `/tmp` is read-only there), `PYTHONUSERBASE=/home/usain/.local`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as one line, run in the background with its output to a
  file (the gate may queue for a while: all slots can be taken), e.g.:
  `env HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-159 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- One commit, your path only (`git add` a new file first):
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1110, DEC-1109" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-159`
  `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under the sandbox's `$TMPDIR`. Use literal paths. Never touch
  `.gov-runtime/scratch/lead/`, `src/` or any other test folder. No install, no network, no `.claude/`, never a live
  session or a hook registered anywhere. Search with Read, Grep and Glob; search once more in other words if the first
  does not answer (DEC-1065).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (the cases per behaviour) / files_changed / evidence (the red lines of B1 and B2, the whole folder's
summary line, the `--collect-only` count) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).

## The ticket's context packet (gov context at 08:40 UTC; the ticket text is unchanged since; today's call answers CONTEXT_OVER_CEILING)
