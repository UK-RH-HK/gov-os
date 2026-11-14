

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing):
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then each finding as: id, KPI line, what, where (file:line), how found (the command), `Ordinary work: yes|no, because ...`,
`Consequence: fails open|loses work|other`, scope in|out.
Then the fenced verdict block, one entry per line S1-S11, F1, F2:

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```

Also state your session id if you know it, and the head you probed.

## The ticket's context packet (gov context DAEO-03ub --role independent-auditor)

