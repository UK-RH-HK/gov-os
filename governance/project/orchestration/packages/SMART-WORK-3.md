# SMART-WORK-3 — how reviews converge, in the Gov OS (DEC-1010 item 2, DEC-1003)

**For the owner: KPI proposals**, each applied when its ticket next runs. Also the day's other tool practices
(DEC-1003's same-day mapping), at the end.

## The deterministic parts
- **W2-115 (the smart close), new line:** `'READY is computed, not declared: each reviewer''s probe record carries a structured verdict per KPI line (pass or fail, each finding''s scope in or out, ordinary work yes or no, consequence fails open, loses work or other); the close refuses only on a finding that is in scope, reachable in ordinary work and fails open or loses work; a malformed or incomplete verdict refuses (fail closed); a verdict written by the ticket''s lead over a reviewer''s is refused [DEC-1010 item 1]'`
- **W2-117 (`gov queue`), new line:** `'A ticket''s review rounds are counted from its probe records; a candidate with a blocking finding after two rounds is refused with "to the owner, once, with options", never queued for a third round [DEC-1010 item 1]'`
- **W2-121 (`gov dispatch`), new line:** `'The dispatcher never starts a third review round for a ticket (its review rounds counted from its probe records); such a ticket goes to the inbox as an owner item [DEC-1010 item 1]'`

## The guidance parts
- **W2-33 (the roles), new line:** `'The QA engineer''s role file makes it the moderator: it triages every finding against the ticket''s own scope and KPIs; a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round; it returns the structured verdict per KPI; at most two review rounds per ticket [DEC-1010 item 1]'`
- **W2-11 (round 2: the qa-review skill and the reviewer''s brief template), new line:** `'The reviewer''s brief template requires the structured verdict block per KPI (scope, ordinary work, consequence per finding) and states the two questions word for word; the qa-review skill states the moderator''s triage, the blocking rule and the two-round cap, with one scenario each [DEC-1010 item 1]'`

## The day's other tool practices (DEC-1003)
- `tools/verdict.py` (READY from a verdict block) -> the W2-115 line above.
- `tools/inbox_wait.sh` and the dispatcher's inbox (a read-only wake; the return-seen race removed, DEC-1009) -> W2-121's inbox line already covers it; **W2-118 amended:** `'where a dispatcher runs, gov watch only reads its inbox and never marks a return seen [DEC-1009]'`.
- `interim_watch.sh` skips commits already on the integration branch -> **W2-118 new line:** `'a commit brought into a lead''s branch by a merge from the integration branch never wakes the caller [DEC-1003]'`.
- The dispatcher's peak admission, CPU judged as busy cores, and every heavy step in a slot -> W2-121's lines (DEC-1008) and **W2-20 amended (S2):** `'the gate judges real CPU use (busy cores over the last minute) as well as the load, and shows both [DEC-1010 item 7]'`.

## Recommendation
Apply all, confidence high (each line is a decision already in force here). W2-11's and W2-33's lines when they next
run (W2-11's round 2, W2-33's run 1); W2-115, W2-117, W2-118, W2-121 and W2-20 when they start.
