# Orchestration: the nightly sheriff

A reference file of the orchestration skill, one level below `SKILL.md`. It states the method; the guard decides
(CAP-24.b). A project's own values stand as `<placeholders>` (DEC-539).

## The nightly

- The full suite runs once a day, on the head of `<integration branch>`, and nowhere else: a plain run, no close
  and no report-only gate (DEC-953 item 3, DEC-968 item 1). It holds no other work.
- Its results go to `<the project's nightly folder>` and into the morning report.

## A red

1. **Re-run the red alone.** A case that passes alone is a flaky candidate, named in the morning report; a case
   that fails alone is a red.
2. **Bisect to the change.** Trace the red over that day's merges to the merge, and the change, that caused it.
3. **Fix small, or send a P1.** A small, clear fix (a typo, a broken name, a one-line slip) is made on the spot,
   through `<the project's small-fix route>`, and reported in the morning. Anything else is a P1 package to the owner
   with a recommendation: a new ticket and its priority, or a fix folded into a current ticket (DEC-953 item 3,
   DEC-968 item 3).
4. The red holds no other work while it is investigated, and nothing goes on a list to wait: no new known red.

## Never

- Retry a case until it passes, or weaken a check, to make the nightly green (DEC-768 item 4, DEC-780).
- Run the full suite anywhere else to check a fix: the fix's own scoped run, then the next nightly, show it.
