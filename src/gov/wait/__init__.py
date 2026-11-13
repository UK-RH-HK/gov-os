"""``gov wait <exit-file> [<max-s>]``: a bounded wait on a job's exit file (DEC-1079, DEC-1052), the liveness by pid alone.

KPI map
-------
- S1 the bounded wait: ``command.run`` polls until the exit file is non-empty or ``<max-s>`` passes (default and ceiling
  570, a larger value capped and said so on stderr), then prints the log tail (``command._tail``) and the job's code;
  RUNNING is exit 124.
- S2 liveness by pid: ``<base>.pid`` beside the exit file is asked of ``liveness.gone`` alone (a signal 0 and the
  process state), so a job gone without its exit file is exit 125 within one poll and a second process of the same name
  keeps nothing alive; an exit file holding no number, a missing argument or a bad ``<max-s>`` is exit 2.
- F1 a wait never outlives its bound or waits for a gone process: the sleep is cut to the time left, and a gone pid is
  seen at the next poll.

Test hooks (environment): ``GOV_WAIT_EVERY`` (poll period in seconds, 5), ``GOV_WAIT_LINES`` (tail lines, 30),
``GOV_WAIT_LOG`` (the log to tail). ``liveness`` is shared with ``gov session-watch helper-watch``.
"""
