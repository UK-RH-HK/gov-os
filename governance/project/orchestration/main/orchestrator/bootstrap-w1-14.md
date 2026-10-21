
## W1-14 residuals (proposal-to-ticket bridge, 2026-10-05)

Recorded at W1-14's close, from the ticket lead's summary. None is a defect of the ticket; each names who should
settle it where that is known.

- **Nothing calls `gov.tasks.bridge.derive` yet**, and `gov.tasks` does not export it (that file is outside the
  ticket's paths). W1-35's planning skill calls it.
- **Nothing teaches authors the task block** (DEC-355). W1-12's `tasks.md` template as delivered is refused. For
  W1-35 or a template change, together with the specification frontmatter (DEC-350).
- **Re-run edges** (DEC-356). A `- [x]` task gets an open ticket; a task edited after derivation never updates its
  ticket, and cycle detection then uses the ticket's `deps`; a removed task's ticket stays, unreported; indented
  sub-task lines are ignored. A hand-written ticket with the same `specification` and `task` is taken as that
  task's ticket.
- **The acceptance-path rule** calls two private names of the guard (`gov.guard.decide._match_pattern` and
  `_is_under_acceptance`), so a rename there breaks the bridge. A glob that reaches the acceptance tests without
  naming the folder (`**/*.py`) is not refused by the bridge; the guard still denies the write.
- **`role` is not checked against the roster**: an unknown role is derived and counts as an implementer for the
  acceptance-path rule. A dependency on an existing ticket accepts any file in `.tickets/`, closed or unreadable.
- **Failures part-way.** If `gov.tasks.create` fails after the ticket script wrote a file, that file is not cleaned
  up; a description that starts with `-` triggers it. Two runs at once on one change can each create a ticket per
  task. The ticket id prefix comes from the project folder name, so a name outside letters and digits gives ids the
  ticket schema rejects (W1-09's `create`).
- **Codes beyond the tests:** `TASKS_NOT_FOUND` and `TICKET_FAILED`.
- **Size and process.** 180 lines against 120. The lead had the engineer build before the five packages were
  decided; they were then decided as built (DEC-355, DEC-356). Workers ran unsandboxed (interim, DEC-183).
