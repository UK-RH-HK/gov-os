"""``gov dispatch``: one pass a minute keeps the machine full and the work moving without any agent session (part a: the
generic core, ``tick`` and ``status``; DEC-1007, DEC-1008).

Nothing here names a project's branches, paths or tickets: they come from ``governance/project/dispatch.yaml``
(``config.py``), the state is ``<root>/.gov-runtime/dispatch/`` (``state.py``).

The files: ``config`` (the configuration), ``state`` (the state folder, the lock, the ready list), ``shell`` (every
external command, limited by ``command_timeout_s``), ``procs`` (the running sessions, from the processes), ``readiness``
(an entry's checks), ``peaks`` (history, peaks, room), ``returns`` (the inbox items and escalations), ``status`` (the
status files), ``run`` (the pass) and ``command`` (``gov dispatch``).

KPI lines and what implements them
----------------------------------

- **S1** (one pass, the lock, OFF, ``status``; the host's installed entry is the CTO's act at the last close, not here):
  ``run.tick`` (the OFF file, then ``state.State.lock``, an ``flock`` released when the process ends, so no stale lock;
  held: exit 4 and nothing written), ``command.run`` (``tick``, and ``status`` through ``status.read``).
- **S2** (at most one start a pass, the list's order, each skipped entry named): ``readiness.reason`` (malformed, already
  started, claim committed on the integration branch and in the worktree, worktree clean, brief complete, ticket not
  running, no unread return, in that order), ``run._pass`` (then the machine's checks: gate, disk, ``max_leads``,
  stagger, room), ``run._start`` (the log name into ``started.txt`` before ``run.spawn``, detached).
- **S3** (peaks, not the moment): ``peaks.compute`` and ``peaks.refresh`` (``peaks.json``, at least daily), ``peaks.ahead``
  and ``peaks.room`` (the admission); the memory floor and working size are read from the resource gate's ``gate.json``
  (``gov.resources.config``), and the gate and the disk from ``gov.resources.gate`` (``read``, ``check_disk``).
- **S4** (every finished session one item, once; a start that never ran; an unread item escalated): ``returns.finished``,
  ``returns.never_ran``, ``returns.escalate``.
- **S5** (the status every pass; a failed pass says so at the top): ``status.write``, ``status.render``, ``status.failed``;
  ``run.tick`` writes ``PASS FAILED <time>: <reason>`` and ``"ok": false`` for any exception or configuration error.
  The running sessions are counted from the processes only: ``procs.find`` and ``procs.lead_marker``.
- **S6** (nothing project-specific; a planted test for each refusal): the code; ``tests/unit/dispatch/``.
- **S7** (no third review round): ``readiness._review``: a brief with a ``run: review`` line and two or more
  ``<worktree>/<probes_dir>/<ticket id>/*.md`` records is not started and becomes one ``status: owner`` item, once.
- **S8** (no watcher to re-arm): every wake is an inbox item a pass writes; the package starts no watcher process.
- **S9** (commits and paths resolved against git): ``returns.parse``, ``returns.commit_ids``, ``returns.file_paths``,
  ``returns.unresolved``; the item's ``unresolved:`` line.
- **S10** (the ready list may be ``gov plan --ready``'s): ``state.read_ready`` reads its four-field lines and ``#``
  comments; only what is on the list is ever started.
- **F1** (the start half): no session for an off-list, not-ready, running entry or one without room; the lead count is
  taken from the processes (``procs.find``), never from ``started.txt`` or the logs.

The lead's readings, followed
-----------------------------

The interface (the keys of ``dispatch.yaml``, the forms of the history, ``peaks.json``, the inbox items and the exit
codes) is as the lead's brief reads it. Departures and additions, named:

- Exit 1 (the pass failed) and 2 (a usage or configuration error) are the command line's reserved codes, which
  ``EXIT_CODES`` may not declare: the module is ``CHILD_EXIT_CODE`` and ends with them itself, printing its own output
  (the envelope under ``--json``), as ``gov plan`` does. Exit 3 and 4 are declared.
- ``max_leads`` and the stagger hold a start with exit 0 (named in the status): exit 3 is the gate, the disk and the
  forecast only.
- A start recorded in ``started.txt`` within ``never_ran_after_s`` with no process, no ``.exit`` yet, is counted as
  running for its ticket, for ``max_leads`` and as holding nothing against its peak (it is on its way).
- The CPU peaks ahead are each running job's whole kind peak (the busy cores already hold what it uses now, so this is
  the cautious side), as the brief's formula reads.
- ``peaks.json`` is also refreshed when the history file is newer than it.
- A program that timed out is not run again in the same pass, so a hung one costs one timeout. A timeout in an entry's
  check is that entry's named reason; in the notifier it is a ``problems`` line of the status. A launch that cannot be
  spawned leaves ``<log name>.exit`` holding 127 (it becomes a return) and fails the pass (exit 1).
- An escalation is recorded in ``escalated.txt`` only when the notifier exits 0 (F-2). A notifier that fails, times out
  or cannot be started leaves it due: retried no sooner than ``notify_retry_s`` (default 600) after the last attempt, and
  named in the status's ``problems`` in every pass until it is sent or the item is read; a timeout ends that pass's
  escalations (the rest are named as not sent, not recorded). A failed notifier never fails the pass.
- ``notifier_command`` is required at load (F-3): a missing one is exit 2 naming the key, nothing started.
- An inbox item is written once, ever (F-1): ``items-written.txt`` outlives the item, so one deleted from ``inbox/`` or
  ``inbox/read/`` is never written again (nor its escalation raised again). An item a pass finds in either folder that
  the record does not hold (a state from before it) is recorded as written then (``state.State.record_seen``).
- A ``files_changed`` path resolves only when git knows it (in HEAD, in the history, or existing and ignored): an
  untracked, not-ignored or only staged path is unresolved (F-4). When git cannot answer, the item says ``unchecked:
  could not be checked (<the failure>): <names>``, never ``unresolved:`` (F-6).
- The OFF file: the pass writes only the status, which says OFF. The launch runs in the ticket's worktree.
- The items are named ``<log name>.return.txt``, ``<log name>.never-ran.txt`` and ``<log name>.owner.txt``; a line of
  ``started.txt`` is ``<log name> <time> <W2> <ticket id>``.
- ``gov.resources.gate.read`` clears registry entries of ended sessions as it reads (the gate's own behaviour); the
  dispatcher writes nothing of the registry.
"""
