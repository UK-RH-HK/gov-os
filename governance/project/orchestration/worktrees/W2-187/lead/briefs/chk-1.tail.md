
## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed (none) /
evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then:
- what you probed and found sound, each with its probe;
- each finding as a described behaviour with file and line, `Ordinary work: yes|no, because …`,
  `Consequence: fails open|loses work|other`, and scope in or out;
- the verdict, `pass` or `fail`;
- **the fenced `verdict` block LAST**, one entry per KPI line it touches (at least success-3, success-6, success-7,
  success-11, success-12, failure-7):
  ```verdict
  {"kpis": [{"kpi": "success-3", "verdict": "pass", "findings": []}, ...]}
  ```
Then `guard_refusals:`. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
reach the same effect by another form (DEC-1142 (9)).

## The lead's results at 89d291eac
