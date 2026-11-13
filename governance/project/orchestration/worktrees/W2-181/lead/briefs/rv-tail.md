## Your record (your session's final message, in full; you write no file)
The twelve fields first, each a labelled line ("none" where nothing):
```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
Put step 0's result first in `evidence`, then the head at start and end, the `gov.__file__` line, your session id if you know it, your TMPDIR's measures, the read refusals counted.

Then the probe record body:
- `task: DAEO-ywb5` and `decisions:` (the ids your findings rest on); `probed_commit: <the full id of 499543a836d3>`.
- **Scope** and **Method** (what you planted and ran, how many times).
- **Probed and found sound**, per question above.
- **Findings**, each described as behaviour (what was done, what happened, what should have happened), never as code (DEC-136), each with `scope: in|out`, `Ordinary work: yes|no, because …`, `Consequence: fails open|loses work|other`, and what evidence would reverse it (DEC-1014). Name both ids where a superseded or PROPOSED rule is in use (DEC-1073).
- The classification on one line (counts of yes/fails open or loses work; yes/other; rows).
- At the end, the fenced block, one entry per KPI line, ids exactly `S1`, `F1`, `F2`, each finding listed under the line it concerns (a finding on no line goes under the nearest one, `scope: out`). Name your own findings `RV1`, `RV2` … so they are not confused with the KPI ids:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass|fail", "findings": [{"id": "RV1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}]}
```
Refused twice for the same call: stop and say so.
