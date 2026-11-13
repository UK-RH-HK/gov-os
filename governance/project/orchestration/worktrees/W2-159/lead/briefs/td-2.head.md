# Brief td-2: independent test designer for DAEO-6lid (W2-159), batch 2 (F4 only), profile STANDARD, class C2

You wrote, as td-1, this ticket's acceptance tests (tests/acceptance/W2-159/, 84 cases, all green on the built code).
One KPI line has no case: F4. `gov accept W2-159` reads a line with no case as **fail**
(`{"kpi": "failure-4", "outcome": "fail", "passed": 0, "failed": 0}`), so the close cannot pass. Add one case for F4
and map it in the README. Change nothing else.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159-tests |
| branch | w2/W2-159-tests (from w2/W2-159 at 680bdce1f526) |
| your path | tests/acceptance/W2-159/** |
| the ticket (F4's line; `allowed_paths` in its front matter) | /home/usain/gov-os-worktrees/W2-159-tests/.tickets/DAEO-6lid.md |
| a precedent of the same line, already accepted (read it; write your own) | /home/usain/gov-os-worktrees/W2-159-tests/tests/acceptance/W2-157/test_w2_157_nothing_else.py, `allowed_paths` and `test_f4_the_branch_changes_only_the_tickets_allowed_paths` |
| how `gov accept` maps a case to a line | the README table's first column (src/gov/accept/runner.py `line_names`); today the F4 row says "not a test" |

## The line
F4: "Any change outside the paths above. Verify: `git diff --name-only` of the ticket's branch against its base lists
only paths matched by the ticket's allowed_paths." The base is the merge base of `HEAD` and `w2/integrate`; the
acceptance tests' own folder (tests/acceptance/W2-159/) is the test designer's path and is not a change outside the
ticket. Read `allowed_paths` from the ticket file (comments after a path are not part of it); a missing
`w2/integrate`, a failing git call or an empty `allowed_paths` fails the case naming the gap (it never passes or skips).
Run git with a clean environment (no global or system config, HOME a tmp folder), as the precedent does.

## What to do
1. A new file tests/acceptance/W2-159/test_f4_scope.py with the one case (plus helpers); the support module may be
   reused, not changed beyond what the case needs.
2. The README: the F4 row lists the new case (in the form the other rows use, e.g.
   `test_f4_scope.py::test_f4_<name>`), the counts line updated (85 in all), and "F4 is the lead's" removed where it
   is said.
3. Run the new file, then the whole folder; both green here (the branch is clean today: the diff against the base
   lists only src/gov/session_watch/**, src/gov/check/commands.py, src/gov/cli/main.py, tests/unit/session_watch/**
   and tests/acceptance/W2-159/**). Then show it can fail: in a throwaway clone or worktree of your own under the
   TMPDIR below (never in /home/usain/gov-os-worktrees/W2-159 or W2-159-tests), commit a change to a path outside
   `allowed_paths` and run the case there against that tree: red, naming the path. Remove the throwaway tree and
   say in `evidence` what you ran and what it printed.
4. `--collect-only` of the folder lists 85.

## Rules
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as
  one line:
  `mkdir -p /tmp/w2-159-td && env TMPDIR=/tmp/w2-159-td HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-159 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- One commit, your path only:
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1110" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-159`
  (`git add` the new file first.) `git status --short` empty when you return.
- One-line commands only; a longer script goes in a file under /tmp/w2-159-td/ run with `bash` or `python3`. Use
  literal paths. Never touch `.gov-runtime/scratch/lead/`, `src/` or any other test folder. No install, no network,
  no `.claude/`, never a live session or a hook registered anywhere. Search with Read, Grep and Glob; search once more
  in other words if the first does not answer (DEC-1065).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the green runs' summary lines, the throwaway red run's line, the
`--collect-only` count) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).

## The ticket's context packet (gov context at 08:40 UTC; the ticket text is unchanged since; today's call answers CONTEXT_OVER_CEILING)
