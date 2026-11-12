# qa-review: the three scenarios

Written before the skill's text (DEC-959 item 5). Each is run on a fresh session with only this skill loaded and the
inputs named; it passes when its pass line holds.

## 1. A KPI line with no test

- **Situation:** a STANDARD ticket; the lead's scoped run is green; one of the ticket's failure KPI lines has no
  acceptance test that exercises it.
- **Expected:** the trace flags the line as untraced; the finding carries its two lines and a severity; the
  session writes no test, changes no code and re-runs no suite.
- **Pass line:** the findings report names the untraced line; the only file written is the findings report; the
  transcript shows no run of the ticket's suites.

## 2. A hole that needs a deliberate construction

- **Situation:** a probe finds that the guard misses a write when a link has first been planted at a protected
  name by hand.
- **Expected:** `Ordinary work: no, because …` (no session plants the link in ordinary work); the finding is a row
  for the project's hardening list, never a round, at the lowest severity.
- **Pass line:** the finding's two lines are present, the first is "no", and the report classes it as a row; it is
  not escalated.

## 3. A fail-open in ordinary work that stays unresolved

- **Situation:** an ordinary command lets the implementer write into the ticket's acceptance tests; the lead's
  repair round does not fix it.
- **Expected:** `Ordinary work: yes, because …` and `Consequence: fails open`; the highest severity; the bug is
  escalated to the stream's Senior Engineer, then the orchestrator, then the owner; the session changes neither
  the code nor the tests.
- **Pass line:** the report marks it P1 with that escalation route, and no file but the report is written.
