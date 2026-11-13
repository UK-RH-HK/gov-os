# Brief eng-2: engineer for DAEO-6lid (W2-159), fix round 1, profile STANDARD, class C2

One red, from the lead's verification of w2/W2-159 at 268a2fadc181. Make it green inside your paths. Change nothing
else.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159 |
| branch | w2/W2-159 |
| allowed paths | src/gov/session_watch/**, src/gov/check/commands.py, src/gov/cli/main.py, tests/unit/session_watch/** |
| ticket (the Interface section at its end; P-W2-159-1 (a)) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |

## The failing output
```
FAILED tests/unit/check/test_kernel_followup.py::test_the_recorded_commands_are_held_and_lock_by_its_module_command
AssertionError: assert ['session-watch', 'lock'] == ['lock']
  At index 0 diff: 'session-watch' != 'lock'
```
Green on w2/integrate's head (f7962d3661d1); red since this branch recorded `session-watch` in
`src/gov/check/commands.py`'s `RECORDED_GOV_COMMANDS` and mapped the existence check's folder to `session_watch`.
The test (read it: tests/unit/check/test_kernel_followup.py, about line 100) plants `src/gov/<command>/command.py`
for every name in `GOV_COMMANDS`, the hyphenated name as it is. The test file is outside the ticket's paths: do not
edit it. The lead's direction: the existence check in `check()` accepts a command's module in its underscore folder
(`session_watch`, what `gov` imports) or in a folder of the command's own name, as it is; keep the comment true.
Add one unit test in tests/unit/session_watch/ for the check: the underscore folder alone passes, no folder is a
finding. Then run that test file, tests/unit/session_watch, tests/unit/check and tests/acceptance/W2-159, each green.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs (the sandbox's own `$TMPDIR` if `/tmp/...` is not writable), `PYTHONUSERBASE=/home/usain/.local`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`, one folder per run, as one line, e.g.:
  `env HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/unit/check -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- You may read tests/acceptance/W2-159/ and run it now (the lead merged it); never edit it.
- One commit, your paths only (`git add` a new file first):
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: engineer" --trailer "Implements: DEC-1110" -- src/gov/check/commands.py tests/unit/session_watch`
- One-line commands only; literal paths. Never touch `.gov-runtime/scratch/lead/`. No install, no network, no
  `.claude/`. `git status --short` empty when you return.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (file:line) / files_changed / evidence (each run's pytest summary line) / tests / discoveries / risks /
lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
