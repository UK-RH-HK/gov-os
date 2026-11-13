# Brief eng-1: engineer for DAEO-6lid (W2-159), profile STANDARD, class C2

You implement ticket DAEO-6lid (W2-159): `gov session-watch stop-check waiter|idle`, the orchestrator's two Stop
checks in the product (a turn does not end with the inbox waiter unarmed, nor idle while unblocked work remains;
each a reminder blocking at most once a turn). An independent test designer writes the acceptance tests
(tests/acceptance/W2-159/) in parallel; you never read them (the guard refuses the counterpart's work). Write your own
unit tests as you go (test first).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-159 |
| branch | w2/W2-159 |
| allowed paths | src/gov/session_watch/**, src/gov/check/commands.py, src/gov/cli/main.py, tests/unit/session_watch/** |
| ticket (read it first: KPI lines S1-S5 and F1-F4, the Interface section at its end) | /home/usain/gov-os-worktrees/W2-159/.tickets/DAEO-6lid.md |
| the command convention (module, `run()`, `CHILD_EXIT_CODE`, the reserved 0/1/2) | src/gov/cli/main.py (docstring) and an example: src/gov/dispatch/command.py, src/gov/plan/command.py |
| the route for the hyphenated name (P-W2-159-1 (a)) | src/gov/cli/main.py `_known` (line ~109) and `_module_name` (line ~117); src/gov/check/commands.py (`RECORDED_GOV_COMMANDS` and the existence check in `check`) |
| the dispatcher (W2-121): status.json's fields, the state folder, the ready list | src/gov/dispatch/run.py (the `data` dict), src/gov/dispatch/state.py (`FOLDER`), src/gov/plan/render.py `ready_text`, the ticket DAEO-cb2b's `## Interface` (.tickets/DAEO-cb2b.md) |
| the configuration loader's precedent (a yaml mapping under one key) | src/gov/dispatch/config.py |
| the reference (this repository's own two Stop hooks: read for the behaviours, the turn reading, /proc reading, the background agents' and tasks' paths; never a target, never copy its project-specific names) | governance/project/orchestration/tools/stop_waiter_check.py, stop_idle_check.py (in your tree; the same as the main tree's at 08:40 UTC 11-12, ACT-IDLE-GUARD-1. ACT-IDLE-GUARD-2, packaged and not yet applied, changes only how it names this repository's merged branches as launchable: not in this ticket's Interface) |
| the sources (read by id in docs/DECISION_REGISTER.md; grep the register only by id) | DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088, DEC-1119, DEC-994 |

Search with Read, Grep and Glob; search once more in other words if the first does not answer (DEC-1065).

## What to build
- `src/gov/session_watch/` (`__init__.py` with the KPI map in its docstring, `command.py`, and a few modules, e.g.
  config, state and log, waiter, idle, items, running); `HELP`, `CLASS = "act"` with `ACT_PATHS` the runtime folder
  (it writes `state.json` and `stop-check.log`), `CHILD_EXIT_CODE = True`, `run` returning 0 after printing at most
  one JSON object. Wrap each check so any exception becomes S4's `systemMessage` and log line; never a traceback,
  never a non-zero exit.
- `src/gov/cli/main.py`: `_known` lists a folder `session_watch` with a `command.py` as `session-watch`, and
  `_module_name("session-watch")` finds `gov.session_watch.command` (a hyphen in the name maps to an underscore in
  the folder; about 4 lines; a name already without a hyphen is unchanged). One unit test in
  tests/unit/session_watch/ for the mapping.
- `src/gov/check/commands.py`: record `session-watch` in `RECORDED_GOV_COMMANDS` (a comment line naming W2-159 and
  DEC-1110, as the others do), and its existence check maps the hyphen to the folder the same way.
- Size: the ticket estimates about 330 lines; keep it plain, standard library plus `yaml` as the repository uses it;
  `gov plan` through subprocess with a timeout (10 s) for the dispatcher source; a failing or timing-out plan is an
  error (S4), named.
- No name, path, folder or ticket id of this repository in `src/gov/session_watch/` (S5, F3): the reference's
  `cto-session.txt`, `DECIDED-NOT-DONE`, `inbox_wait*.sh`, `/home/...`, `W2-`/`DAEO-` ids, `orchestrator/tools`
  all stay out, including in docstrings and comments (cite decisions by DEC id only).
