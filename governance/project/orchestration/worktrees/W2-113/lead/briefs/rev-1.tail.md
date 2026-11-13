

----

## Return (your last message; nothing else is read)
First a fenced verdict block, exactly:
```verdict
ticket: DAEO-g29a
head: 6542b7ec525b
round: 1
verdict: PASS | FAIL
blocking: <n>
```
PASS only when no finding is blocking (a KPI or failure line not met, an Interface item I1/I2/I3 contradicted, a
session other than the CTO's asked or let through, the CTO refused in a freshly adopted product, a refusal that opens,
or words that claim a key was set when none was). Then each finding: id (R1-<n>), severity (blocking / non-blocking),
in scope or not, the KPI line or Interface item, file:line, what you did to show it (the probe's command and its
output, short), whether it happens in ordinary work (yes/no, because ...), and the behaviour that would be right
(described, not a patch). Then the probes you ran with their results (counts), and your judgement on each of the
lead's known items above. Then the twelve fields, each a labelled line ("none" where nothing): task / status /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action, and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
