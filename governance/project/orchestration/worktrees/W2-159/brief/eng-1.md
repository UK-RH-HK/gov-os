Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-159/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

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
## The interface (the ticket's `## Interface` section, accepted as a whole by the CTO, P-W2-159-2 (a); the lead's reading of the KPI lines where marked [lead])

Read the ticket's `## Interface` section first: it is the contract, and neither you nor your counterpart changes it.
A gap or a contradiction you find comes back to the lead as a package (question, options with cost, recommendation),
never a choice of your own on an interface point. What follows restates it and adds the lead's reading where the
KPI lines leave a point open, so the test designer and the engineer build to the same thing.

1. Command: `gov session-watch stop-check waiter|idle [--root <dir>]`; standard input is the Stop hook's JSON
   (`session_id`, `transcript_path`, `stop_hook_active`, ...). It prints at most one JSON object on standard output,
   either `{"decision": "block", "reason": "..."}` or `{"systemMessage": "..."}`, or nothing; it exits 0 always and
   prints no envelope (the module declares `CHILD_EXIT_CODE = True`). The hyphenated command maps to the folder
   `src/gov/session_watch/` (P-W2-159-1 (a): `src/gov/cli/main.py`'s `_known` and `_module_name`, and
   `src/gov/check/commands.py`'s existence check, map `session-watch` to `session_watch`).
2. Configuration: `<root>/governance/project/session-watch.yaml`, mapping under `session_watch:`; every key optional:
   `waiter_commands` (list of substrings of a process's command line; unset or empty: the waiter check says
   nothing), `waiter_arm` (default the first of `waiter_commands`), `standby_max_age_h` (default 2), `pid_globs`
   (relative to the root; default `.gov-runtime/**/*.pid`), `items` (`{source: dispatcher}` default, or
   `{source: file, path: <relative>, reader: lines | <module.path:function>}`).
   - Reader `lines`: one item per non-`#` non-empty line, `<id> <state words>`; state `WAIT owner...` is
     owner-waiting, `WAIT ...` another wait, `DONE` or `CLOSED` closed, anything else unblocked.
   - Reader `module.path:function`: called as `function(path)` [lead: with the item file's absolute path], returns a
     list of `{id, title, state}`, state one of `open`, `owner`, `job`, `closed`.
   - Source `dispatcher`: runs `<gov> plan --root <root> --ready <tmp file>` and takes batch 1 (the lines under
     `# batch 1`, form `<name> <ticket id> <brief> <log>`) as unblocked, less the tickets `status.json`'s `running`
     shows. [lead] An item's id is the ticket id (the second column); its title the first column.
3. Runtime folder `<root>/.gov-runtime/session-watch/`: `session.txt` (the registered orchestrator session id; read,
   never written), `standby.txt` (the stand-by note; its age is its mtime), `state.json` (the once-a-turn state,
   shared by both checks, keyed by check: `{"waiter": {...}, "idle": {...}}`), `stop-check.log` (one tab-separated
   line per decision, the check's name in it, and the IDLE-REASON line's text when one ended the turn).
4. Dispatcher status `<root>/.gov-runtime/dispatch/status.json` (W2-121's schema), used only when at most 5 minutes
   old by mtime (an older one is not used): gate shut = `gate.open` false or `gate.disk.open` false; machine full =
   `outcome` "refused"; running = `running`, `running_jobs` or `pending_starts` non-empty.
5. Running (S2): the session's background agents and tasks as the reference reads them, and pid files under
   `pid_globs` (the process alive, started under 3 h ago, no `<name>.exit` beside the `<name>.pid`); one past 3 h is
   named as stale and not counted.
6. Test overrides (environment): `GOV_SESSION_WATCH_PS` (a JSON list of `{pid, cmdline, start, state, fds}` in place
   of /proc; `start` epoch seconds, `state` a /proc state letter, `Z` or `X` not alive), `GOV_SESSION_WATCH_NOW`
   (epoch seconds, the check's "now" for every age: stand-by note, status file, pid start), `GOV_SESSION_WATCH_GOV`
   (the `gov` program run for the plan). [lead, the Interface's item 5 "overridable for tests by env", named after the
   reference's precedent:] `GOV_SESSION_WATCH_SUBAGENTS` (the folder of the session's background agents' files) and
   `GOV_SESSION_WATCH_TASKS` (the folder of its background tasks' output files).

The lead's reading of the KPI lines (for both of you):
- [lead] Which session: both checks act only for the registered session (`session_id` equal to `session.txt`'s
  stripped text). Another session's id, no `session.txt`, or a `session.txt` that cannot be read: the check prints
  nothing (S1's "says nothing").
- [lead] A turn (S3): the reference's definition (`stop_idle_check.py`, docstring item 1 and `turn_and_reason`): the
  transcript (`transcript_path`, JSON lines) read back from its end to the last `user` entry that starts a turn (not
  a tool result and not `isMeta`, or any user entry carrying `turnOrigin` or `wakeupSource`); its `uuid` (else its
  `timestamp`) is the turn's key. The `IDLE-REASON: <why>` line is searched in the `assistant` entries' text items
  after that entry (and in the hook input's `last_assistant_message` if present). Only entry types, keys and those
  text items are read.
- [lead] Once a turn (S3): the state file records, per check, the session and the turn it blocked. A check never
  blocks when `stop_hook_active` is true, nor when the state shows it already blocked this session's same turn; a new
  turn key blocks again. A missing `state.json` is an empty state.
- [lead] Errors (S4) for the registered session: a `state.json` that exists but cannot be read or parsed is an
  error. On an error the check prints `{"systemMessage": "..."}` naming the error (no `decision`), and writes a line
  naming it in `stop-check.log`; the turn ends. This holds for both checks.
- [lead] S1's other cases (the waiter running, a stand-by note younger than its limit, another session, a session
  file that cannot be read): no block (no `decision` key in the output).
- [lead] The waiter's block reason names the inbox waiter and the `waiter_arm` command (the configured string, as it
  is).
- [lead] The idle check ignores the stand-by note (S4). A let-through for a legitimate wait (the gate shut, the
  machine full, every remaining item waiting on the owner, a running job) prints `{"systemMessage": "..."}` naming
  which wait and writes it in the log; a stale pid file (past 3 h) is named there too. An IDLE-REASON let-through
  prints a `systemMessage` with the stated reason and logs it. The idle block's reason names each unblocked item by
  its id.
- [lead] Order in the idle check: registered session; IDLE-REASON (ends the turn, logged); the bound
  (`stop_hook_active` or already blocked this turn: through); running (through, named); a legitimate wait from the
  dispatcher's status (through, named); the items: none unblocked (through, naming the waits, e.g. "every remaining
  item waits on the owner", with counts of owner, job and other waits); unblocked items: block, naming them.
- No name, path, folder or ticket id of this repository in `src/gov/session_watch/` (S5, F3): no `cto-`, no
  `DECIDED-NOT-DONE`, no `inbox_wait`, no `W2-`/`DAEO-` id, no `/home/...`, no `orchestrator/tools`.

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
