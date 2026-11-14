# Brief: independent auditor, W2-184 (DAEO-6f0s), FULL review round 1

You are a fresh, read-only independent auditor (Opus, effort high). You review ticket DAEO-6f0s (W2-184), profile
FULL: RUBRIC-2 at launch, at the head named below, against its KPI lines, the interface (at the end, word for word)
and the judgement rules (below, word for word). Write no file of any repository; run probes only in your session's
own `$TMPDIR` (copies, fixtures). Re-run no whole suite. Use your audit skill.

## What to review
- Tree (read-only): /home/usain/gov-os-worktrees/W2-184, branch w2/W2-184. **Head to probe: HEADPROBE.**
- The ticket's own change: `git -C /home/usain/gov-os-worktrees/W2-184 diff 1fd0066e1 HEADPROBE` (1fd0066e1 is the
  integration tip merged in; the diff holds only this ticket's files): `src/gov/launch/criticality.py` (new),
  `src/gov/launch/role.py`, `src/gov/launch/launcher.py`, `governance/project/criticality.yaml` (new),
  `tests/unit/launch/test_w2_184_*.py`, `tests/acceptance/W2-184/` (the independent test designer's 413 cases),
  `docs/changes/W2-184-CIT-E.md`.
- The ticket: /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-6f0s.md (KPI lines S1-S5 and F1; the
  non-goals). Sources: DEC-1167 (2), DEC-1126 (3), DEC-1120, DEC-1119, DEC-839, DEC-1010 in
  /home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md (read each by id).
- Evidence the lead has: `gov accept W2-184` 413/413 (see the lead's return); the full verification run's results.

## Known, and judged by the lead (judge them yourself too)
- `src/gov/launch/command.py` is outside the ticket's `allowed_paths`; `--reason`, `--trial` and `--owner-named` are
  keyword arguments of `launcher.launch` only, and the CLI wiring goes to the CTO as a package (interface 7.2). Judge
  whether anything else is missing, not this.
- Two lead amendments before this review, each with its own test-design batch and fix batch: 3.2a (a max after `--`
  equal to the resolved effort needs no `--reason`), and 1.4 replaced (with no `criticality.yaml`, a launch is as
  before W2-184; DEC-1167 (2)). The earlier 1.4 refused every engineer and test designer launch in a project with
  the kernel role files and no `criticality.yaml` (77 reds in W1-28, W1-32, W1-46, W1-50 and W2-60a). Judge whether
  the amended 1.4 opens a path where this repository (which has the file) launches off the table: that is in scope.
  Whether an adopted repository with no file should route by RUBRIC-2 is the lead's settled reading of DEC-1167 (2);
  name your view, classified as the rules say.

## What to probe (at least)
Each KPI line against the code and the cases: does the code do what the line and the interface say, and do the cases
fail when it does not? Particularly: the criticality matching (comment tail, either-way fnmatch, highest class, the
ticket's `class` never read); the table line parser against the real kernel role files; the floor and max/`--reason`;
a model after `--`; trials (every field); promotion (fail-open first, two failed reviews, the record's path, sorted
order, a lower model refused, a trial refused); a FULL ticket's review count (resumes, other tickets, other roles, the
`wbs_id` name, unreadable records), the probe's Opus max, the same setting twice and `--owner-named`; the record's nine
keys and their nulls; every refusal before the gate with no record left; the subagent model; `--plan` and lead
launches unchanged; any path where a launch starts on a model or effort the table does not give (fails open).

# Judgement rules (governance/project/briefs/JUDGEMENT.md, word for word)

JUDGEMENTTEXT

# Your record (your last message; the lead commits it as docs/probes/DAEO-6f0s/PR-DAEO-6f0s.md)
Return, as your last message, the record's body in Markdown (the lead adds the front matter):
1. A title line `# Probe of DAEO-6f0s (W2-184), round 1: judgement pass|fail`, then the head you probed (full hash),
   your session's role and model, and what you ran (commands, fixtures in `$TMPDIR`).
2. `## Findings`: each finding with an id (F1, F2, ...), the KPI line, what you saw (file:line, the probe and its
   output), and its two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`, and
   `Scope: in|out`.
3. `## Per KPI line`: S1, S2, S3, S4, S5, F1: pass or fail, one paragraph each.
4. The fenced verdict block, exactly in this form (JSON), one entry per KPI line:
```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "fail", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}]}]}
```
5. A last line: `judgement: pass` or `judgement: fail` (fail only when a finding is in scope, ordinary work yes, and
   fails open or loses work).
Then, after the record, the twelve fields, each a labelled line: task: / status: / work_completed: / files_changed: /
evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word)

