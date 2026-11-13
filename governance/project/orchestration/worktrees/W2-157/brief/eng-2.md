Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-2: engineer for DAEO-ozyt (W2-157), profile STANDARD, class C2: one red to fix

You are a fresh engineer for ticket DAEO-ozyt (W2-157: the GPU backstop, `gov resources --backstop <pgid>...`). The
code is built (commits 8939fcff5515 and c5b0ee91dd12 on w2/W2-157); the acceptance run is 108 passed, 1 failed. You
fix that one red in the code, and nothing else. You never read or change `tests/acceptance/` (an independent test
designer's); the failing output below is all you get of it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157 |
| branch | w2/W2-157 |
| your allowed paths | src/gov/resources/backstop.py, src/gov/resources/command.py, src/gov/resources/config.py, tests/unit/resources/test_w2_157*, docs/changes/W2-157-evidence.md |
| the ticket (KPI S4: "a group already ended is skipped and named") | /home/usain/gov-os-worktrees/W2-157/.tickets/DAEO-ozyt.md |
| the Interface (L1: each value a decimal integer above 1, else exit 2; L5: an ended group is skipped and named) | docs/changes/W2-157-evidence.md (the readings L1-L9 as applied) |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The failing output (the whole of it)
```
FAILED tests/acceptance/W2-157/test_w2_157_groups.py::test_s4_a_number_no_group_can_have_is_skipped_not_refused

Outcome(code=1, envelope=None, out='', err=...)
E       AssertionError: the command printed no JSON envelope
E       exit: 1
E       stderr: Traceback (most recent call last):
E         File "/home/usain/gov-os-worktrees/W2-157/src/gov/cli/main.py", line 249, in main
E           outcome = command.handler(root, args, config)
E         File "/home/usain/gov-os-worktrees/W2-157/src/gov/resources/command.py", line 80, in run
E           return watch(args.backstop, root)
E         File "/home/usain/gov-os-worktrees/W2-157/src/gov/resources/backstop.py", line 159, in watch
E           skipped = [g for g in named if not _live(g)]
E         File "/home/usain/gov-os-worktrees/W2-157/src/gov/resources/backstop.py", line 55, in _live
E           os.killpg(group, 0)
E       OverflowError: signed integer is greater than maximum
```
The case's name says the expected outcome: a decimal integer above 1 that no process group can have (beyond what
`os.killpg` accepts) is skipped and named as an ended group, as L5 says, not a crash and not a refusal. Check every
other place the backstop signals a group (`os.killpg(g, SIGSTOP)` on a trip, the per-poll check) for the same fault.

## Safety
Your unit tests plant their own process groups only (children started with `start_new_session=True`) and stand-ins
under `tmp_path`; never signal a process you did not start; never run `--backstop` against a real group, the real GPU
or the real HOME's gate.json.

## Rules
- A unit test first in `tests/unit/resources/test_w2_157_backstop.py` that fails on the present code, then the fix.
- Keep W2-20's tests green: run `tests/unit/resources` and `tests/acceptance/W2-20` before the commit, in the form
  `env HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src python3 -m pytest <folder> -q -p no:cacheprovider
  -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
- Add one line to `docs/changes/W2-157-evidence.md` naming the fix and its unit test.
- Anything longer than one line goes in a script file under `$TMPDIR` (the sandbox denies writes to the tree's
  `.gov-runtime/scratch/`; the last engineer was refused there), run with `bash <file>`. No merge, no push, no edit outside your
  paths. A refused call is reported, never worked around.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- <paths>`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/unit/resources and tests/acceptance/W2-20)
/ tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
