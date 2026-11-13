# Brief rev-1: independent auditor for DAEO-fd0p (W2-160), STANDARD review round 1, class C2

You are the independent auditor (a fresh, read-only session) for ticket DAEO-fd0p (W2-160: `gov wait <exit-file>
[<max-s>]`, a bounded wait on a job's exit file with liveness by its pid file alone, and `gov session-watch
helper-watch`, an inbox item when a helper of the registered session or a launched worker dies or goes silent). Audit
the branch head **eb6d0cc07643** of `w2/W2-160` in /home/usain/gov-os-worktrees/W2-160 against the ticket's KPI lines
(S1-S4, F1-F4) and its Interface: I1 and I2 in the ticket's last section ("P-W2-160-1 decided ..."), which the owner
accepted word for word (DEC-1153 (2)).

You change nothing in the repository: no edit, no commit, no merge. Your verdict is your return.

## What to read
| what | path |
|---|---|
| the ticket (KPI lines; the Interface I1 and I2 at its end) | /home/usain/gov-os-worktrees/W2-160/.tickets/DAEO-fd0p.md (if it lacks the section "P-W2-160-1 decided", read /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-fd0p.md; the context packet below also carries it) |
| the change | `git -C /home/usain/gov-os-worktrees/W2-160 diff 9c507d513..eb6d0cc07643` (src/gov/wait/{__init__,command,liveness}.py, src/gov/session_watch/helper_watch.py, src/gov/session_watch/command.py, src/gov/check/commands.py, tests/unit/wait/, tests/unit/session_watch/test_w2_160_helper_watch.py, docs/changes/W2-160-evidence.md) |
| the independent acceptance suite (66 cases, all green at this head) | tests/acceptance/W2-160/ (README.md maps KPI lines to cases) |
| W2-159's code the helper watch reuses and the command it extends | src/gov/session_watch/ (config.py `pid_globs`, state.py, command.py's `stop-check`); its tests tests/acceptance/W2-159/, tests/unit/session_watch/ |
| the references the ticket ports (the CTO's scratch tools; where they differ from I1/I2, I1/I2 rule) | /home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/ref/wait_for.sh, helper_watch.py |
| the CLI's command contract (CLASS, ACT_PATHS, CHILD_EXIT_CODE) | src/gov/cli/main.py |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1119, DEC-1109, DEC-1153 |

Search with Read, Grep and Glob; search again once in different words if the first does not answer (DEC-1065).

## Known to the lead (judge them; do not re-report them as new)
- `tests/unit/session_watch/test_route.py:19` (W2-159's) asserts `ACT_PATHS == (".gov-runtime/session-watch/**",)`;
  the decided Interface adds `.gov-runtime/dispatch/inbox/**`, so it is red here. The file is outside the ticket's
  paths; the lead has returned it to the CTO as a package (a one-line change to the two-path tuple).
- `tests/acceptance/W2-159/test_f4_scope.py` checks the branch against W2-159's own allowed_paths, so it is red on any
  later ticket's branch.
- The engineer's risks: the state file is written in place (no temp file, for S4's spy), and a corrupt file reads as
  empty (items could be re-sent once); an empty exit file counts as not yet written; the `**` default of `pid_globs`
  does not enter hidden folders; a pid above 2^22 counts as no pid.

## What to probe (at least these; add your own)
1. Each KPI line and failure line against the code, not only against the tests: where a test is weaker than its line,
   probe the line directly. F4: `git diff --name-only <merge-base of HEAD and w2/integrate>..eb6d0cc07643` against the
   ticket's allowed_paths (tests/acceptance/W2-160/ is the test designer's).
2. `gov wait`: the bound (124 within `<max-s>` plus one poll), 125 within one poll of the pid's death, a zombie as gone,
   the 570 cap and its stderr line, `<max-s>` 0, negative, fractional or `x`, an exit file of `abc`, blank, `-1`, `256`,
   with a trailing newline; no argparse `invalid choice` text; the tail (`GOV_WAIT_LOG`, `.log`/`.json`/`.txt` order,
   the JSON result's fields, `.summary`). A pid file holding a pid reused by an unrelated live process: say what the
   wait does and whether I1 settles it.
3. The helper watch, every condition of I2: `api-error` (only from the last assistant/user/system entry), `stalled`
   (not finished, no entry for `--stale-min`), `worker gone`, `worker ended with an error` (non-zero code, `is_error`,
   `api_error_status`); once each across passes and across a restart; the exit file's mtime rule (at or after the start
   less `--every`); the window (`--window-h`) for transcripts and pid files; no session file means no helpers; the
   helpers folder from `GOV_SESSION_WATCH_SUBAGENTS` else the `~/.claude/projects/<mangled root>/<session>/subagents/`
   form; the items' names (`x`-open, `-<n>`), and each item naming the helper's id or the worker's log and its last line.
4. F2 and S4: plant canary text in every place a message's text can sit (`message.content` as a string and as blocks,
   a tool_use's `input`, a tool_result, `apiError` or `error` objects carrying a message, a worker `.json`'s `result`
   and error fields) and show it never reaches an item, the state file, the log or stdout; the `<synthetic>` exception
   only. No process-name match anywhere in src/gov/wait/ or helper_watch.py. A filesystem spy over a pass, a loop and a
   configuration error: only the inbox items, `helper-watch-state.json` and `helper-watch.log` are written.
5. The loop: `--max` reached gives one `HELPER_WATCH ended after <s> s; <n> item(s) written; re-arm it` and exit 0;
   whether `--every`/`--max` sleep real time under `GOV_SESSION_WATCH_NOW`; a W2-159 configuration error is exit 1,
   named.
6. `gov session-watch stop-check` is unchanged in behaviour (its `check` is now optional in the parser): run
   W2-159's acceptance and unit suites and say what else, if anything, changed for it; and whether `helper-watch`
   accepts a stray `waiter`/`idle` or `stop-check` accepts helper-watch options silently.
7. Robustness: the state file under a crash or concurrent passes (two watchers at once), an unreadable transcript or
   meta file, a non-JSON line, a pid file holding no number, an exit file that appears between the liveness check and
   the exit check (a race reported as gone?).

Your probes are read-only on the repository and run by Bash in your own TMPDIR (DEC-1144 (7)): make
`/home/usain/gov-os-worktrees/W2-160/.gov-runtime/scratch/rev-tmp` (or use the sandbox's TMPDIR if that is refused)
and plant everything there; scripts longer than one line go there too. Start stand-in processes yourself and stop them
by the pid you hold, never by name. Any pytest goes through the heavy-slot gate:
`TMPDIR=<your tmp> bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<an empty folder in your tmp> PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-160/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
A heavy-slot or resource refusal is a wait. Never a live session, never a hook registered anywhere, never the real
`~/.claude` (point `GOV_SESSION_WATCH_SUBAGENTS` and `HOME` at your tmp). Refused twice for the same call by the
guard, the sandbox or a hook: stop and say so; never reach the same effect by another form (DEC-1142 (9)).

The ticket's context packet (`gov context DAEO-fd0p --role independent-auditor --budget 12000`) follows.

----

