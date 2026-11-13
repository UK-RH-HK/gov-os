

----

## Return (your last message; nothing else is read)
First a fenced verdict block, exactly:
```verdict
ticket: DAEO-fd0p
head: eb6d0cc07643
round: 1
verdict: PASS | FAIL
blocking: <n>
```
PASS only when no finding is blocking (a KPI or failure line not met, an Interface item I1/I2 contradicted, a wait that
outlives its bound or waits on a gone job, a process matched by name, a message's text copied out, a condition written
twice, a write outside the three named files, or `stop-check` changed in behaviour). Then each finding: id (R1-<n>),
severity (blocking / non-blocking), in scope or not, the KPI line or Interface item, file:line, what you did to show
it (the probe's command and its output, short), and the behaviour that would be right (described, not a patch). Then
the probes you ran with their results, and your judgement on each of the lead's known items above. Then the twelve
fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed / evidence / tests
/ discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action, and `guard_refusals:`
(none, or each: time | form | the hook's reason | true or false-positive).
