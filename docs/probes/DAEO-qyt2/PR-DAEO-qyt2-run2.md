---
type: probe
task: DAEO-qyt2
reviewer_session: "independent-auditor au-2 c7b46c46-39ec-4af6-bbba-275764ba1552 (the narrow independent check of run 2's test revision only, DEC-1156 (7); launched read-only by W2-185's lead through gov launch, Opus high, class C2, 2026-11-14); not an author of the change"
implementer_session: "independent-test-designer td-3 0298f2b5-6127-4da2-b447-a810a9ee8e3e (2ad99213c672, 8ee2c6dc422e, 6cb684972cdf, 00b56d2f2a43, 80841a0c66b0, 1689ecce8726, 86a7e7480d95, e54b383f882b); merges 0c7e4d68f106 (w2/integrate) and 16bddf807824 (the tests) by the lead"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 16bddf80782449573cedd7373544533d79d2a326
---

# Probe record: W2-185 (DAEO-qyt2), the narrow independent check of run 2's revision, on 16bddf807824

task: DAEO-qyt2
decisions_applied: DEC-1167, DEC-971, DEC-1156, DEC-801, DEC-808, DEC-1010

## Scope

The CTO's P-W2-185-REDS-1 (a) under DEC-1156 (7) widened the ticket by the eight test files holding the 18
decided-behaviour reds named by round 1's record (`PR-DAEO-qyt2.md`, lines 41-57). A fresh independent test designer
(td-3) revised them to DEC-1167 (4), one commit per file, each with `Rewrite-Reason: DEC-1167 (4), DEC-1156 (7) (W2-185
run 2)`. This check judged only that revision, `git diff 0c7e4d68f..16bddf807` (8 files), on four points: each revised
case keeps its point; plants; the five `PreCompact` cases outside the 18; scope and trailers. The code under `src/` and
`template/` is unchanged since round 1's PASS at 1180e4ec5 except w2/integrate's own files (the reviewer's check). The
reviewer's verdict block below is the reviewer's, copied as returned. The lead writes no verdict over it.

## The reviewer's result, in short (its full return: the lead's `log/au-2.result.md`)

- **Point 1, each case keeps its point: pass.** No id lost, no case deleted, no skip, xfail, flaky or rerun mark; 16 cases
  added. Entries are picked by program (`own_programs`/`program_of`, `_runs`, `_program`), never by place. Old points
  still fail when broken (guard limit 30; guard path broken). The new cases pin DEC-1167 (4): the old whole-event lift put
  back in `portability.py` turns 14 cases red. The loose `HOOKS_EVENT_DIFFERS` or `HOOKS_MATCHER_DIFFERS` acceptance leaves
  no face unpinned (the engineer's unit case pins the exact code).
- **Point 2, plants: pass.** (a) No `context_watch.py` entry in the template: 10 red (W2-59 seven lines, W2-106 pair,
  W1-38 context-watch cases). (b) A non-exempt third `postToolUse` entry: W2-05 over-repository, program_env and the W2-106
  pair red. (c) The template's watch with matcher `Bash|Edit`: 5 red. (d) The whole-event lift mutant: 14 red.
- **Point 3, the five PreCompact cases: pass.** Red on 0c7e4d68f from W2-176's read-first line (13fd1dd34, in the claim
  base), not this ticket; the case still requires exit 0 and the program's own `systemMessage`.
- **Point 4, scope and trailers: pass.** Exactly the eight widened files, one per commit; trailers in one final paragraph;
  `Implements:` ids from `sources:` only.
- Counts: unplanted, the eight files with `--optin lifted,breadth` and no `-k`: 194 cases, all green (192 under the
  default `-k`, which hides the two `*_carries_the_time_limit` cases; the test designer ran those apart: 2 passed).

## Findings

Classification: three findings, all out of scope, none fails open or loses work. No round proposed.

**R1 (out of scope).** `_json` in `tests/acceptance/W1-38/w1_38_hooks_support.py` reads the last JSON line for every
event, not only PreCompact; it would be better scoped to the PreCompact branch.
- Ordinary work: yes, because an honest agent could add a text line before a hook's JSON, as W2-176 did for PreCompact.
- Consequence: other (the guard's stdout is parsed strictly as JSON elsewhere: W1-08, `test_live_hook.py`, W2-106).

**R2 (out of scope).** 2ad99213c's `Rewrite-Reason` names only DEC-1167 (4) for its PreCompact hunk, whose cause is
W2-176; the commit body names W2-176.
- Ordinary work: yes, because a mixed-cause commit under one trailer is an ordinary slip.
- Consequence: other (only the record is affected).

**R3 (out of scope).** W2-59's `imports_only_the_standard_library` allows the kernel's own modules without following what
they import; right today, a future top-level import chain into `gov` would skip the `pin-gov-` check.
- Ordinary work: no, because it needs a new kernel-module chain that does not exist.
- Consequence: other.

The lead's triage: R1, R2 and R3 accepted as rows for the Wave 3 hardening list; none blocks (DEC-1010 item 1).

## Verdict (the reviewer's, as returned)

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": [{"id": "R2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": []}, {"kpi": "S3", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "F1", "verdict": "pass", "findings": []}]}
```
