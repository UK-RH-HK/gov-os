"""``gov plan``: the dependency map from each ticket's writes, needs and waits, and the launch batches it proposes
(W2-136, DEC-1088, DEPENDENCY-MAP-1).

Read-only, deterministic and a proposal: the orchestrator approves the batches into the ready list (DEC-1007 (2)),
and ``gov launch``'s check (``gov.launch.plan_check``) is the only other caller. No close, landing, claim, readiness
or hook module imports this package (DEC-1052).

- ``tickets``: the ticket store's fields the plan reads;
- ``overlap``: whether two path patterns can name one path, under the guard's own matcher;
- ``derive``: the waits, the findings and the batches;
- ``render``: the text lines, the ``--json`` result and the ``--ready`` list;
- ``command``: the command line.
"""
