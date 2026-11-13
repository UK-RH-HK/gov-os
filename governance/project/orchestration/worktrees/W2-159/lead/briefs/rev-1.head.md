# Brief rev-1: reviewer (independent-auditor, read-only) for DAEO-6lid (W2-159), profile STANDARD, class C2, round 1 of at most 2

You are the reviewer (QA): you read everything, you change nothing. You probe the head 2a67c4a63da0 of
/home/usain/gov-os-worktrees/W2-159 (branch w2/W2-159) for behaviour the acceptance tests miss, against the ticket's
KPI lines S1-S5 and F1-F4 (non-goals: none in the KPI table; the ticket's text parks the dead-man's switch and the
helper watch elsewhere).

## Where things are
| what | path |
|---|---|
| the tree (read only; write nothing) | /home/usain/gov-os-worktrees/W2-159 |
| the ticket (KPI lines; the `## Interface` section at its end is the contract, accepted by the CTO as P-W2-159-2 (a)) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |
| the code | src/gov/session_watch/ (command, checks, config, items, running, state, status, transcript); src/gov/cli/main.py (`_known`, `_module_name`: the hyphenated route, P-W2-159-1 (a)); src/gov/check/commands.py (`RECORDED_GOV_COMMANDS`, the existence check) |
| the acceptance tests (independent test designer, 84 cases) | tests/acceptance/W2-159/ (README.md maps each case to a KPI line) |
| the unit tests (engineer) | tests/unit/session_watch/ |
| the reference this ticket ports (this repository's own Stop hooks; not a target) | governance/project/orchestration/tools/stop_waiter_check.py, stop_idle_check.py |
| the dispatcher it reads (W2-121) | src/gov/dispatch/ (run.py's status data, state.py), src/gov/plan/ (`--ready`), .tickets/DAEO-cb2b.md `## Interface` |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088, DEC-1119, DEC-994 |
| the branch's base (for F4: `git diff --name-only e84e6c9cf..2a67c4a63da0`; the acceptance case test_f4_scope.py checks the same) | e84e6c9cf |

## The lead's results (do not re-run them)
- The lead's scoped verification (`lead_verify.sh`) at 680bdce1f526 (the code head; 2a67c4a63da0 adds only one
  acceptance case): 4853 tests, 10 failed, every one the W2-96 signal family (gov accept's signal handling), red the
  same on w2/integrate (shared base reds, W2-177 fixes them); serial phase 1 test, green. Being re-run at 2a67c4a63da0.
- `gov accept W2-159` at 680bdce1f526: 84 passed, 0 failed; every line pass except failure-4, which had no case. The
  test designer then added F4's case (test_f4_scope.py, 9254a220dfbc, merged at 2a67c4a63da0: 85 cases, 85 green
  in the designer's run); the lead's gov accept at 2a67c4a63da0 is being re-run.
- The engineer's fix round: tests/unit/check's `test_the_recorded_commands_are_held_and_lock_by_its_module_command`
  went red when `session-watch` was recorded; the existence check now accepts the module in the underscore folder or a
  folder of the command's own name (680bdce1f526).

## Steps
1. `printenv GOV_ROLE GOV_TICKET` and `git -C /home/usain/gov-os-worktrees/W2-159 rev-parse HEAD` (expect it to start
   2a67c4a63da0).
2. Read the ticket, the tests, the code and the lead's results; re-run nothing the lead ran; run code only to
   reproduce a finding, in a temporary folder outside the repository (planted roots, the Stop hook's JSON on standard
   input, `GOV_SESSION_WATCH_PS` / `GOV_SESSION_WATCH_NOW` / `GOV_SESSION_WATCH_GOV` in place of the live machine).
   Never register a hook in any `.claude/`, never run against a live session.
3. Look first for: a check that traps a session (blocks with no way out, blocks twice in a turn, blocks when
   `stop_hook_active` is set); a check that fails open silently (an error with no `systemMessage` and no log line, or
   a legitimate-wait answer given when the condition does not hold, e.g. a stale status file read as fresh, a stale or
   dead pid counted as running, a stand-by note letting S2 end idle); a block or reason carried into the next turn;
   a file name, folder or ticket id of this repository in src/gov/session_watch (F3); a change outside the ticket's
   allowed_paths (F4; tests/acceptance/W2-159/ is the test designer's path).
4. Any pytest you run to reproduce goes through the heavy-slot gate, one line, with a TMPDIR outside the repository
   and outside ~/gov-os-runs (the sandbox's own `$TMPDIR` where `/tmp` is read-only):
   `mkdir -p /tmp/w2-159-rev && env TMPDIR=/tmp/w2-159-rev HOME=/home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <one file or case> -q -p no:cacheprovider -o tmp_path_retention_policy=failed`
5. Write nothing in any tree: `git -C /home/usain/gov-os-worktrees/W2-159 status --porcelain` is empty when you
   finish. Search with Read, Grep and Glob (no `gov retrieve` in the sandbox); search once more in other words if the
   first does not answer (DEC-1065).
6. Give your record `task: DAEO-6lid` and `decisions:` (the ids its findings rest on); name both ids where a
   superseded or PROPOSED rule is in use (DEC-1073). State, per finding, what evidence would reverse it (DEC-1014).
   Under `.gov-runtime/` and in your return, write commit hashes as 12 digits (DEC-911).

