# W2-159 (DAEO-6lid): the lead's interface proposal, for P-W2-159-2 (DEC-1052)

The ticket's Interface names the command, stdin and the hook's answer form, but not where the configuration lives, the
runtime files' names, the waiter's default or the open-items reader. Proposed, to be accepted as a whole or amended:

1. Command: `gov session-watch stop-check waiter|idle [--root <dir>]` (route: P-W2-159-1). The module declares
   `CHILD_EXIT_CODE = True`, prints at most one JSON object on stdout in the Stop hook's form
   (`{"decision":"block","reason":...}` or `{"systemMessage":...}`) and returns 0, always, so no envelope is printed.
   A configuration error (`load_config` raising before `run`) is out of its reach: named as a residual.
2. Configuration: `governance/project/session-watch.yaml`, the mapping under `session_watch:` (the dispatcher's
   precedent, `dispatch.yaml` / `dispatch:`). Keys, all optional:
   - `waiter_commands`: list of strings, each matched as a substring of a process's command line. Unset or empty:
     the waiter check says nothing (nothing to arm); S1's planted project sets it.
   - `waiter_arm`: the command the block's reason names to arm it; default the first of `waiter_commands`.
   - `standby_max_age_h`: default 2.
   - `pid_globs`: globs relative to the root; default `.gov-runtime/**/*.pid`.
   - `items`: `{source: dispatcher}` (default) or `{source: file, path: <relative>, reader: <name>}`. The dispatcher
     source runs `gov plan --root <root> --ready <tmp>` and takes batch 1 as unblocked, less the tickets the
     dispatcher's status shows running. Readers: `lines` (built in: one item per non-`#` line, `<id> <state words>`;
     state `WAIT owner...` is owner-waiting, `WAIT ...` other wait, `DONE|CLOSED` closed, anything else unblocked)
     and `module.path:function` (returns a list of `{id, title, state}`, state one of open, owner, job, closed).
3. Runtime folder `.gov-runtime/session-watch/`: `session.txt` (the registered orchestrator session id; this ticket
   reads it, never writes it: writing it is the session-start hook's install, an owner's ACT), `standby.txt` (the
   stand-by note; its age is its mtime), `state.json` (the once-a-turn state, shared by both checks, keyed by check),
   `stop-check.log` (one tab-separated line per decision, with the IDLE-REASON line when one ended the turn).
4. Dispatcher status: `.gov-runtime/dispatch/status.json` (W2-121's schema), used when at most 5 minutes old by
   mtime: gate shut = `gate.open` false or `gate.disk.open` false; machine full = `outcome` "refused" (exit code 3);
   running = `running`, `running_jobs`, `pending_starts` non-empty.
5. Running (S2): the session's background agents and tasks as the reference reads them (Claude Code's own paths,
   derived from `transcript_path` and `session_id`, overridable for tests by env), and pid files under `pid_globs`
   (alive, started under 3 h ago, no `<name>.exit`); past 3 h named as stale and not counted.
6. Test overrides (env, the reference's precedent): `GOV_SESSION_WATCH_PS` (a JSON list of {pid, cmdline, start,
   state, fds} in place of /proc), `GOV_SESSION_WATCH_NOW` (epoch seconds), `GOV_SESSION_WATCH_GOV` (the `gov`
   program run for the plan).
