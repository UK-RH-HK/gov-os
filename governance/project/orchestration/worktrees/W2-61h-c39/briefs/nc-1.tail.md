
## Return (your last message; nothing else is read)
Your probe record's body, ready for the lead to commit under `docs/probes/DAEO-h2k3/` (the lead adds the front matter):
1. A line `reviewer_session: <your session id if you know it, else "unknown">`.
2. What you probed and found sound, as short bullets (commands and counts, no hidden content).
3. Each finding with its id, scope (in|out), and the two lines `Ordinary work: yes|no, because …` and
   `Consequence: fails open|loses work|other`.
4. `Judgement: pass|fail`.
5. Last, the fenced verdict block, one entry per KPI line you judged (S1 and S3 at least):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": []}, {"kpi": "S3", "verdict": "pass|fail", "findings": [{"id": "N1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
