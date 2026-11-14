
## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `@HEAD@`), how, each finding (id, the KPI line,
what and where with file and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
scope in|out), and, last, the fenced `verdict` block in this form:
```verdict
{"kpis": [{"kpi": "S6", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
covering S6, S7, S8, S9, S10, S11, S12, F4, F5 and F6, and S1 to S5 and F1 to F3 as `pass` only if you find nothing in
this change against them (they were reviewed before; this change does not touch their files). Your overall judgement:
`pass` or `fail`.

## The decisions it applies (from the register, by id)
- DEC-1180 (2): quoted above. DEC-1178 (5): "`approve q02 variant 0703aebf`: the writer's fix brief for hidden question
  q02 (`drafts/q02-writer-r2/EXAMIN-writer-q02-fix.md`); then the writer's round 2, the checker and `check_gold`
  (expect 20 of 20) by the owner's operator." (DEC-1180 (2) later: no checker run.) DEC-820: reads are open; only
  secrets, the held-out material's contents, the counterpart's work and the hidden half of an evaluation set are refused.
  Read any other id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.

## The ticket (read-only copy)
