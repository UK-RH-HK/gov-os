
----

## Return (your last message; nothing else is read)
First a fenced verdict block, exactly:
```verdict
ticket: DAEO-p8tv
head: f706a77f5b7e
round: 1
verdict: PASS | FAIL
blocking: <n>
```
PASS only when no finding is blocking (a KPI or failure line not met, an Interface item contradicted, a fault that
loses data, measures a set twice, leaks a question or gold path, or opens the sets root). Then each finding: id
(R1-<n>), severity (blocking / non-blocking), the KPI line or Interface item, file:line, what you did to show it (the
probe's command and its output, short), and the behaviour that would be right (described, not a patch). Then the
probes you ran with their results, and your judgement on each engineer reading (faithful / changes behaviour / gap).
Then the twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action, and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
