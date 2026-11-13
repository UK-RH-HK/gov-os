```
verdict: FAIL
head: f39289d3a379
findings: 6
- R2-1 | blocking | S4, F1 | src/gov/close/select.py:546 (used at :759, command.py:1816) | With no green base on HEAD's line, a red is judged against the parent of the ticket's oldest trailered commit. Planted P1: an untrailered first commit breaks W2-bb's widget test, then trailered work: the close exits 0, the ticket closes, the red is recorded caused:false with repair ticket p1-6prz. It should refuse RED_CAUSED. Ordinary work: yes, because a newly adopted project (close: scoped is the default) has no green record until its first green nightly or full close, and a forgotten trailer is an honest slip. Consequence: fails open. It follows PK-3 (a)'s written fallback, so it is a decision.
- R2-2 | major | F1, S4 | src/gov/close/select.py:546 | F-2 is worse this round: work landed on the main line between the green base and the ticket's fork is now judged as the ticket's. Planted P2: another ticket's landed commit breaks the widget test, then this ticket's trailered work: refused RED_CAUSED ("the head without the change: green"). Before this round it closed with a repair ticket. Ordinary work: yes, because any red landed since the newest green record counts, and here the green base is stale (PK-5). Consequence: other (fails closed). It follows DEC-988 item 3.
- R2-3 | minor | S6, F3 | src/gov/close/batch.py:624 | The rest is run on the batch's selection, computed on the whole build, minus the targets the rest lacks. A test that exists only without the culprit (one the culprit renamed or deleted) is never added, so another candidate's change reaching it lands without it run. Reasoned from the code, not planted. Before this round the rest's run refused (RUN_INCOMPLETE) whenever the culprit also added a file. Ordinary work: no, because it needs the culprit to rewrite or remove the one test covering another candidate's change, in a way that masks that change. Consequence: fails open. Smallest fix: the rest's selection is the union of the landed candidates' scoped selections on the rest's build.
- R2-4 | minor | S6, F3 | src/gov/close/batch.py:607, :626 | Two new guards are load-bearing but untested. M3 (a timeout with the candidate alone counts as confirmation): A is blamed, B lands. M4 (an empty target list allowed): B lands after a run of 0 tests. Both mutants pass all 14 unit batch tests, and no acceptance case plants either. The real code is right (B1: RUN_INCOMPLETE, B3: BATCH_UNEXPLAINED). Ordinary work: no. Consequence: other.
- R2-5 | minor | S9 | docs/research/W2-115-smart-close.md:43 | The script's docstring says to run it as `PYTHONPATH=... python3 -I s9.py`, but -I ignores PYTHONPATH, so `gov` cannot be imported (ModuleNotFoundError). The re-run paragraph's command, without -I, reproduces the table exactly. Ordinary work: no. Consequence: other.
- R2-6 | minor | S7 | src/gov/close/command.py:1846 | A refused scoped close writes no close record; the reds and their reasons are only in the refusal envelope on standard output, which is not kept. Scope: out (S7's record holds "the commit closed", and a refusal closes none). Ordinary work: yes. Consequence: other. Reversed by: an owner ruling that "each close" includes a refused one.
```

```verdict
{"kpis": [
{"kpi": "S1", "verdict": "pass", "findings": []},
{"kpi": "S2", "verdict": "pass", "findings": []},
{"kpi": "S3", "verdict": "pass", "findings": []},
{"kpi": "S4", "verdict": "fail", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S5", "verdict": "pass", "findings": []},
{"kpi": "S6", "verdict": "pass", "findings": [{"id": "R2-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R2-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S7", "verdict": "pass", "findings": [{"id": "R2-6", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "S8", "verdict": "pass", "findings": []},
{"kpi": "S9", "verdict": "pass", "findings": [{"id": "R2-5", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S10", "verdict": "pass", "findings": []},
{"kpi": "S11", "verdict": "pass", "findings": []},
{"kpi": "S12", "verdict": "pass", "findings": [{"id": "S12-deferred", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "S13", "verdict": "pass", "findings": []},
{"kpi": "F1", "verdict": "fail", "findings": [{"id": "R2-1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "R2-2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
{"kpi": "F2", "verdict": "pass", "findings": []},
{"kpi": "F3", "verdict": "pass", "findings": [{"id": "R2-3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "R2-4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
{"kpi": "F4", "verdict": "pass", "findings": []}
]}
```
