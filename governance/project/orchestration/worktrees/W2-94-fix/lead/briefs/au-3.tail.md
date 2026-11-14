
## The decisions it applies (from the register, by id)
- DEC-1154: a change decided after a ticket's review gets a narrow independent check of that change; the ticket lands on
  it. DEC-1156 (7): own-branch path cases and decided-behaviour test revisions, the CTO routes them, a narrow check.
  DEC-1180 (4): a defect spotted is fixed in the same flow (S13). DEC-1010: how reviews converge. DEC-820: reads are open;
  only secrets, the held-out material's contents, the counterpart's work and the hidden half of an evaluation set are
  refused. Read any other id in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md` by grepping its id.

## Return (your final message, in full)
The twelve labelled fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons,
proposed_decisions, unresolved, recommended_next_action; sandbox and `ps` checks first), then **the probe record's
body** (no front matter; the lead adds it): what you probed (head `@HEAD@`), how, each of the three confirmations with
its evidence (the diff, the red-on-copy runs, the suite counts), each finding (id, the KPI line, what and where with file
and line, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, scope in|out), your overall
judgement (`pass` or `fail`), and, last, the fenced `verdict` block. It covers S12 and S13 (the revision touches their
checks), and the other lines (S1 to S11, F1 to F6) as `pass` only if you find nothing in this change against them (they
were reviewed before; this change does not touch their code). Its form:
```verdict
{"kpis": [{"kpi": "S13", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, ...]}
```
