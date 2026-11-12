"""``gov session-watch stop-check waiter|idle``: the orchestrator's two Stop checks (DEC-1027, DEC-1110 (1)).

Claude Code runs a Stop hook when a session is about to end a turn. For the one registered orchestrator session, the
*waiter* check answers "block" while the inbox waiter is unarmed, and the *idle* check answers "block" while unblocked
work remains with nothing running. Each is a reminder, not a guard: it blocks at most once a turn, and an error ends the
turn and is named (DEC-1109 (3), DEC-936).

KPI map
-------
- S1 the waiter check: ``checks.waiter`` (the session: ``state.registered``; the stand-by note: ``state.standby_age``;
  the waiter's process: ``running.waiter_alive``).
- S2 the idle check: ``checks.idle``; the legitimate waits from the dispatcher's status: ``status``; "running": ``running``
  (agents, tasks, pid files; a pid past 3 hours is named as stale and not counted); the open items: ``items``.
- S3 once a turn: ``transcript.read`` (the turn's key and the ``IDLE-REASON`` line), ``checks.bounded`` and
  ``state.write_state`` (the state file, keyed by check), ``stop_hook_active``.
- S4 never a trap, never silent: ``command.run`` turns any exception into a ``systemMessage`` and a log line
  (``state.log``); the idle check ignores the stand-by note.
- S5 where the items come from is the project's configuration (``config``: ``governance/project/session-watch.yaml``),
  the default the dispatcher's ready list (``gov plan --ready``); nothing of any one project is named in this package.

Runtime folder ``.gov-runtime/session-watch/``: ``session.txt`` (read, never written), ``standby.txt``, ``state.json``,
``stop-check.log``. Overrides for tests (environment): ``GOV_SESSION_WATCH_PS`` (a JSON list of ``{pid, cmdline, start,
state, fds}``, the text itself or a file holding it, in place of /proc), ``GOV_SESSION_WATCH_NOW`` (epoch seconds),
``GOV_SESSION_WATCH_GOV`` (the program run for the plan), ``GOV_SESSION_WATCH_SUBAGENTS`` and ``GOV_SESSION_WATCH_TASKS``
(the folders of the session's background agents and tasks).
"""
