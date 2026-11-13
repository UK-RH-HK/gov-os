
## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line ("none" where nothing): task / status (DONE or PACKAGES) /
work_completed / files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions /
unresolved / recommended_next_action. Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive). Then the probe record body: what you probed and found sound, each finding described as behaviour
(what was done, what happened, what should have; never as code), each with its two lines (`Ordinary work: yes|no,
because …` and `Consequence: fails open|loses work|other`), its scope (in|out) and what would reverse it, the
classification of the findings on one line, and this fenced block, one entry per KPI line (S1, S2, S3, S4, S5, F1, F2,
F3, F4):
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "F1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Name new findings FR-6, FR-7, ... (round 1 used FR-1 to FR-5; the KPI table uses F1-F4); say for each of FR-1 to FR-5 whether it holds at this head.
