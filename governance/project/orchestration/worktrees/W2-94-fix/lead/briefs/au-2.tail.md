

## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `ff6ba10be89a`), how, each finding (id, the KPI line,
what and where with file and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`,
scope in|out), your judgement on question 5's path case, and, last, the fenced `verdict` block in this form:
```verdict
{"kpis": [{"kpi": "S13", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
covering S13, S11 and S12 (the epilog fix and the S11/F6 case revision touch them), and the other lines (S1 to S10, F1
to F6) as `pass` only if you find nothing in this change against them (they were reviewed before; this change does not
touch their code). Your overall judgement: `pass` or `fail`.

## The decisions it applies (from the register, by id)
- DEC-1180 (4): quoted above. DEC-1180 (2): the launch script gains a one-question fix flow (reviewed at fac8d2026).
  DEC-1156 (7): a narrow independent check of a change made after a ticket's review. DEC-136: tests written from
  described behaviour. DEC-820: reads are open; only secrets, the held-out material's contents, the counterpart's work
  and the hidden half of an evaluation set are refused. Read any other id in
  `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.
