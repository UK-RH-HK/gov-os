# Brief rev-2: reviewer (independent-auditor, read-only) for DAEO-6lid (W2-159), profile STANDARD, class C2, round 2 of 2 (the last; DEC-1010)

You are the reviewer (QA): you read everything, you change nothing. You probe the head da85fe5bcd88 of
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
| the branch's base (for F4: `git diff --name-only e84e6c9cf..da85fe5bcd88`; the acceptance case test_f4_scope.py checks the same) | e84e6c9cf |

## Round 1 and the fix (read this first)
A fresh reviewer probed 2a67c4a63da0 in round 1 (session b586cef3): **fail**. Its findings and the lead's triage
(DEC-1010; READY is computed from your verdict block, not from round 1's):
- FR-1 (S2): a pid file left by a worker that ended without its exit file, its number reused by an unrelated newer
  process, counted as running work, so an idle turn ended. In scope, ordinary work, fails open: **blocking; fixed**
  (B1 below).
- FR-2 (S3): the two checks, run side by side on one Stop, overwrote each other's once-a-turn record, so a later stop
  in the same turn got a second waiter block. In scope, ordinary work, other: **rides along; fixed** (B2 below).
- FR-3 (S2): other standing watchers (not the configured waiter) count as running work, bounded at 3 h and named.
  Out of scope (a watcher list is a new setting; the helper watch is another ticket): a row.
- FR-4 (S2): with the default dispatcher source, every ticket in the plan's batch 1 is unblocked, in-progress ones
  too. Out of scope (S5 fixes the ready list as the default), other: a row.
- FR-5 (S1): the waiter is matched machine-wide by command-line text. Out of scope (S1's wording and the reference):
  a row.
The fix (the behaviours, as given to the test designer and the engineer):
**B1 (S2; FR-1, blocking: in scope, ordinary work, fails open): a reused pid is not running work.**
- Done: a project holds a leftover pid file (under the pid globs, no `<name>.exit` beside it) written two days ago
  (its mtime); the number in it now belongs to an unrelated live process that started 10 minutes ago. One unblocked
  item is listed; nothing else runs.
- Happened: the idle check let the turn end, saying something of the orchestrator's is running (that pid).
- Should happen: a block naming the item. S2 counts "a pid file whose process is alive": the process the file named
  is gone; a process that started after the file was written is not it. The lead's reading [lead]: a pid file's
  process counts only when it started no later than 15 minutes (900 s, a slack for clock steps) after the file's
  mtime; one that started later is not counted and not named as running (as a dead pid is not). A process that
  started before the file was written, or within the 15 minutes after, still counts (the existing cases stay green).
  The project-specific exceptions of the reference (named launcher scripts) are not ported: the code names nothing of
  this repository (S5, F3).

**B2 (S3; FR-2, rides along: in scope, ordinary work, consequence other; DEC-802): the two checks keep each other's
once-a-turn record.**
- Done: both checks are installed; Claude Code runs a Stop event's hooks side by side. On one Stop the waiter is
  unarmed and an item is unblocked, so both block. The idle check reads the shared state file at its start and writes
  it after `gov plan` returns; the waiter check wrote its record in between.
- Happened: the idle check's write dropped the waiter's record; a later stop in the same turn, without
  `stop_hook_active`, got a second waiter block.
- Should happen: S3's "never twice for the same turn" holds whatever the order: after both checks end, the state file
  holds both checks' records for the turn, and a third waiter call in the same turn (no `stop_hook_active`) says
  nothing. (The Interface keeps one `state.json` shared by both checks, keyed by check.)

Commits since round 1: 29b7a2c335fb (test designer: 9 acceptance cases for B1 and B2, merged at da85fe5bcd88; 94
cases) and d25c7f171 (engineer: running.py's start slack, state.py's `record()` merging under a lock, checks.py;
unit cases). Probe the fix first (`git diff 2a67c4a63da0 da85fe5bcd88`), then whatever round 1 left; never a third
round: what you find now is the last word, and anything that still blocks goes to the owner once, with options.

## The lead's results (do not re-run them)
- The lead's scoped verification (`lead_verify.sh`) and `gov accept W2-159` at da85fe5bcd88: being run as you start;
  the lead reports them with your record. At 680bdce1f526 lead_verify had 4853 tests, 10 failed, every one the W2-96
  signal family (shared base reds, red the same on w2/integrate); at 2a67c4a63da0 gov accept passed 85 of 85, every
  line.
- The engineer's own runs at d25c7f171: tests/unit/session_watch red before the fix (5 failed), then
  tests/unit/session_watch with tests/acceptance/W2-159 (85 then) 138 passed. The test designer's run at
  29b7a2c335fb (without the fix): 5 failed (exactly the B1 and B2 cases), 89 passed.

## Steps
1. `printenv GOV_ROLE GOV_TICKET` and `git -C /home/usain/gov-os-worktrees/W2-159 rev-parse HEAD` (expect it to start
   da85fe5bcd88).
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

