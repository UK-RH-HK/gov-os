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
